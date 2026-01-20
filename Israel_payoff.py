#!/usr/bin/env python3
"""
FINAL VERSION — additive banks with corrected goal numbering.

STRUCTURE:

BANK 1 (additive):
  Bank1 = 100 * (0.30*P(G1) + 0.20*P(G2) + 0.50*P(G3))

BANK 2 (additive):
  Bank2 = 100 * (0.30*P(G4) + 0.70*P(G5))

FINAL PAYOFF:
  Final = 0.60 * Bank1 + 0.40 * Bank2

Properties:
- If G1=G2=G3=1 → Bank1 = 100
- If G4=G5=1 → Bank2 = 100
- Analytic expectation is exact (linearity of expectation)
- Monte Carlo used as sanity check
"""

from __future__ import annotations
from dataclasses import dataclass
import random
from typing import Optional, Dict, Any


def _clamp01(x: float, name: str) -> float:
    if not isinstance(x, (int, float)):
        raise TypeError(f"{name} must be a number in [0,1], got {type(x)}")
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise ValueError(f"{name} must be in [0,1], got {x}")
    return x


# -------------------------
# Constants
# -------------------------
BANK1_MAX = 100.0
BANK2_MAX = 100.0

# BANK 1 weights (sum to 1.0)
W_G1 = 0.30
W_G2 = 0.20
W_G3 = 0.50

# BANK 2 weights (sum to 1.0)
W_G4 = 0.30
W_G5 = 0.70

# Final payoff weights
W_BANK1_TO_FINAL = 0.60
W_BANK2_TO_FINAL = 0.40


@dataclass(frozen=True)
class EventProbs:
    """
    Probabilities (0..1) that each goal is achieved.
    """
    G1: float
    G2: float
    G3: float
    G4: float
    G5: float

    def validated(self) -> "EventProbs":
        return EventProbs(
            G1=_clamp01(self.G1, "G1"),
            G2=_clamp01(self.G2, "G2"),
            G3=_clamp01(self.G3, "G3"),
            G4=_clamp01(self.G4, "G4"),
            G5=_clamp01(self.G5, "G5"),
        )


# -------------------------
# Analytic expectations
# -------------------------
def bank1_expected(p: EventProbs) -> float:
    return BANK1_MAX * (W_G1 * p.G1 + W_G2 * p.G2 + W_G3 * p.G3)


def bank2_expected(p: EventProbs) -> float:
    return BANK2_MAX * (W_G4 * p.G4 + W_G5 * p.G5)


def expected_payoff_analytic(p: EventProbs) -> float:
    p = p.validated()
    b1 = bank1_expected(p)
    b2 = bank2_expected(p)
    return W_BANK1_TO_FINAL * b1 + W_BANK2_TO_FINAL * b2


# -------------------------
# Monte Carlo simulation
# -------------------------
def payoff_one_draw(p: EventProbs, rng: Optional[random.Random] = None) -> float:
    rng = rng or random.Random()
    p = p.validated()

    g1 = 1.0 if rng.random() < p.G1 else 0.0
    g2 = 1.0 if rng.random() < p.G2 else 0.0
    g3 = 1.0 if rng.random() < p.G3 else 0.0
    g4 = 1.0 if rng.random() < p.G4 else 0.0
    g5 = 1.0 if rng.random() < p.G5 else 0.0

    bank1 = BANK1_MAX * (W_G1 * g1 + W_G2 * g2 + W_G3 * g3)
    bank2 = BANK2_MAX * (W_G4 * g4 + W_G5 * g5)

    return W_BANK1_TO_FINAL * bank1 + W_BANK2_TO_FINAL * bank2


def expected_payoff_monte_carlo(
    p: EventProbs, n: int = 200_000, seed: int = 1
) -> float:
    rng = random.Random(seed)
    total = 0.0
    for _ in range(n):
        total += payoff_one_draw(p, rng)
    return total / n


# -------------------------
# Reporting helper
# -------------------------
def breakdown(p: EventProbs) -> Dict[str, Any]:
    p = p.validated()
    b1 = bank1_expected(p)
    b2 = bank2_expected(p)
    final = expected_payoff_analytic(p)

    return {
        "inputs": vars(p),
        "bank1_expected": b1,
        "bank2_expected": b2,
        "final_expected": final,
        "consistency_checks": {
            "bank1_full_if_all_ones": BANK1_MAX * (W_G1 + W_G2 + W_G3),
            "bank2_full_if_all_ones": BANK2_MAX * (W_G4 + W_G5),
            "final_full_if_banks_full":
                W_BANK1_TO_FINAL * BANK1_MAX + W_BANK2_TO_FINAL * BANK2_MAX,
        },
    }


if __name__ == "__main__":
    # Example probabilities (edit freely)
    probs = EventProbs(
        G1=0.30,
        G2=0.25,
        G3=0.20,
        G4=0.40,
        G5=0.35,
    )

    print("=== Analytic expected payoff ===")
    print(f"{expected_payoff_analytic(probs):.2f} / 100")

    print("\n=== Monte Carlo sanity check ===")
    print(f"{expected_payoff_monte_carlo(probs):.2f} / 100")

    print("\n=== Breakdown ===")
    for k, v in breakdown(probs).items():
        print(f"{k}: {v}")