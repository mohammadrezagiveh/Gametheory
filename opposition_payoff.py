#!/usr/bin/env python3
"""
Updated payoff model with a Stage-I "payoff bank" (additive) and Stage-II multiplicative
degradation when things go wrong — PLUS Monte Carlo sanity check.

========================
YOUR NEW LOGIC (as I read the diagram)
========================

STAGE I: Build a "payoff bank" additively (0..100)
- Political Reform (PR)      -> if Yes, add 30 to the bank
- Civil Liberties (CL)       -> if Yes, add 30 to the bank
- Material Improvement (MI)  -> if Yes, add 40 to the bank

So:
    bank = 30*PR + 30*CL + 40*MI
If all three are true, bank = 100 ("full").

STAGE II: Degrade (multiply) whatever is in the bank when an event goes wrong
Applied sequentially:
- Border Integrity (BI)
    if BI = No  -> bank *= 0.30
- Infrastructure Survival (IS)
    if IS = No  -> bank *= 0.70
- Maintaining Deterrence (MD)
    if MD = No  -> bank *= 0.40
- Lack of Casualty (LoC)
    if LoC = No -> bank *= 0.70

Final Payoff = bank after multipliers.

NOTES:
- This is a clean “add then degrade” structure.
- Analytic expectation below is computed EXACTLY by enumerating all 2^7 = 128 states,
  assuming independence across events.
- Monte Carlo sim should converge to the analytic value as n increases.
"""

from __future__ import annotations
from dataclasses import dataclass
from itertools import product
import random
from typing import Optional, Dict, Any


# -------------------------
# Stage I additive bank weights (points out of 100)
# -------------------------
W_PR = 30.0
W_CL = 30.0
W_MI = 40.0

# -------------------------
# Stage II degradation multipliers (apply when event is "No")
# -------------------------
MULT_BI_NO = 0.30
MULT_IS_NO = 0.70
MULT_MD_NO = 0.40
MULT_LOC_NO = 0.70


def _clamp01(x: float, name: str) -> float:
    if not isinstance(x, (int, float)):
        raise TypeError(f"{name} must be a number in [0,1], got {type(x)}")
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise ValueError(f"{name} must be in [0,1], got {x}")
    return x


@dataclass(frozen=True)
class EventProbs:
    """
    Probabilities (0..1) that each event is YES/True.
    """
    # Stage II (degradation gates)
    BI: float   # Border Integrity
    IS: float   # Infrastructure Survival
    MD: float   # Maintaining Deterrence
    LoC: float  # Lack of Casualty

    # Stage I (bank builders)
    PR: float   # Political Reform
    CL: float   # Civil Liberties
    MI: float   # Material Improvement

    def validated(self) -> "EventProbs":
        return EventProbs(
            BI=_clamp01(self.BI, "BI"),
            IS=_clamp01(self.IS, "IS"),
            MD=_clamp01(self.MD, "MD"),
            LoC=_clamp01(self.LoC, "LoC"),
            PR=_clamp01(self.PR, "PR"),
            CL=_clamp01(self.CL, "CL"),
            MI=_clamp01(self.MI, "MI"),
        )


def payoff_from_realization(
    BI: bool, IS: bool, MD: bool, LoC: bool,
    PR: bool, CL: bool, MI: bool
) -> float:
    """
    One realized payoff (0..100) given a boolean realization of events.
    """
    # ---- Stage I: build the bank additively ----
    bank = 0.0
    if PR:
        bank += W_PR
    if CL:
        bank += W_CL
    if MI:
        bank += W_MI

    # ---- Stage II: degrade bank when things go wrong ----
    if not BI:
        bank *= MULT_BI_NO
    if not IS:
        bank *= MULT_IS_NO
    if not MD:
        bank *= MULT_MD_NO
    if not LoC:
        bank *= MULT_LOC_NO

    return bank


def payoff_one_draw(p: EventProbs, rng: Optional[random.Random] = None) -> float:
    """
    One Monte Carlo draw (independence assumption): sample each event, compute payoff.
    """
    p = p.validated()
    rng = rng or random.Random()

    BI = rng.random() < p.BI
    IS = rng.random() < p.IS
    MD = rng.random() < p.MD
    LoC = rng.random() < p.LoC
    PR = rng.random() < p.PR
    CL = rng.random() < p.CL
    MI = rng.random() < p.MI

    return payoff_from_realization(BI, IS, MD, LoC, PR, CL, MI)


def expected_payoff_analytic(p: EventProbs) -> float:
    """
    Exact expected payoff via full enumeration of all 128 states (assumes independence).
    """
    p = p.validated()
    probs_yes = {
        "BI": p.BI, "IS": p.IS, "MD": p.MD, "LoC": p.LoC,
        "PR": p.PR, "CL": p.CL, "MI": p.MI,
    }

    expected = 0.0
    for BI, IS, MD, LoC, PR, CL, MI in product([False, True], repeat=7):
        state_prob = 1.0
        state_prob *= probs_yes["BI"] if BI else (1.0 - probs_yes["BI"])
        state_prob *= probs_yes["IS"] if IS else (1.0 - probs_yes["IS"])
        state_prob *= probs_yes["MD"] if MD else (1.0 - probs_yes["MD"])
        state_prob *= probs_yes["LoC"] if LoC else (1.0 - probs_yes["LoC"])
        state_prob *= probs_yes["PR"] if PR else (1.0 - probs_yes["PR"])
        state_prob *= probs_yes["CL"] if CL else (1.0 - probs_yes["CL"])
        state_prob *= probs_yes["MI"] if MI else (1.0 - probs_yes["MI"])

        expected += state_prob * payoff_from_realization(BI, IS, MD, LoC, PR, CL, MI)

    return expected


def expected_payoff_monte_carlo(p: EventProbs, n: int = 200_000, seed: int = 1) -> float:
    """
    Monte Carlo estimate of expected payoff (sanity check).
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    rng = random.Random(seed)
    total = 0.0
    for _ in range(n):
        total += payoff_one_draw(p, rng=rng)
    return total / n


def breakdown(p: EventProbs) -> Dict[str, Any]:
    """
    Useful reporting: min/max and expectation.
    """
    p = p.validated()

    max_bank = W_PR + W_CL + W_MI  # 100
    min_bank = 0.0

    # Worst-case: full bank then all degradations trigger
    worst_nonzero = max_bank * MULT_BI_NO * MULT_IS_NO * MULT_MD_NO * MULT_LOC_NO

    return {
        "inputs": {
            "BI": p.BI, "IS": p.IS, "MD": p.MD, "LoC": p.LoC,
            "PR": p.PR, "CL": p.CL, "MI": p.MI
        },
        "bank_range": {"min": min_bank, "max": max_bank},
        "worst_case_if_bank_full_and_all_fail": worst_nonzero,
        "expected_payoff_analytic": expected_payoff_analytic(p),
        "notes": [
            "Stage I is additive: bank = 30*PR + 30*CL + 40*MI (in points).",
            "Stage II degrades bank multiplicatively when BI/IS/MD/LoC are No.",
            "Analytic expectation is exact under independence; MC should converge with large n.",
        ],
    }


if __name__ == "__main__":
    # ---- Example probabilities (edit these) ----
    probs = EventProbs(
        # Stage II
        BI=0.85,   # P(Border Integrity = Yes)
        IS=0.70,   # P(Infrastructure Survival = Yes)
        MD=0.65,   # P(Maintaining Deterrence = Yes)
        LoC=0.60,  # P(Lack of Casualty = Yes)

        # Stage I
        PR=0.30,   # P(Political Reform = Yes)
        CL=0.40,   # P(Civil Liberties = Yes)
        MI=0.50,   # P(Material Improvement = Yes)
    )

    print("=== Analytic expected payoff (exact enumeration) ===")
    e = expected_payoff_analytic(probs)
    print(f"Expected payoff: {e:.2f} / 100")

    print("\n=== Monte Carlo sanity check ===")
    e_mc = expected_payoff_monte_carlo(probs, n=200_000, seed=1)
    print(f"Monte Carlo expected payoff: {e_mc:.2f} / 100")

    print("\n=== Breakdown ===")
    info = breakdown(probs)
    for k, v in info.items():
        print(f"{k}: {v}")