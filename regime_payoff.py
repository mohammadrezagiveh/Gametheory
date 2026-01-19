#!/usr/bin/env python3
"""
Revised additive payoff model (out of 100) based on your latest clarification.

EVENTS (each has a probability in [0,1]):
- S: Survival
- M: Maintaining previous policies
- R: Regional dominance
- C: Credible internal power
- V: Not getting subjected to violence

PAYOFF LOGIC (diagram + your clarification):
1) If Survival happens (S=True):
   - Base payoff = 50
   - Additive bonuses (order does NOT matter):
       + 20 * M
       + 20 * R
       + 10 * C
   - V is ignored in this branch.

2) If Survival does NOT happen (S=False):
   - Base payoff = 0
   - Only V contributes:
       + 20 * V
   - M, R, C are ignored in this branch.

This code provides:
- expected_payoff_analytic: expected payoff given probabilities (main use)
- payoff_one_draw: one simulated payoff draw (for intuition / Monte Carlo)
- expected_payoff_monte_carlo: Monte Carlo estimate to sanity check analytic result
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, Any, Optional


# ---- Weights (points out of 100) ----
BASE_SURVIVE = 50.0
W_M = 20.0
W_R = 20.0
W_C = 10.0
W_V = 20.0


def _clamp01(x: float, name: str) -> float:
    if not isinstance(x, (int, float)):
        raise TypeError(f"{name} must be a number in [0,1], got {type(x)}")
    if x < 0.0 or x > 1.0:
        raise ValueError(f"{name} must be in [0,1], got {x}")
    return float(x)


@dataclass(frozen=True)
class EventProbs:
    """
    Probabilities for each event in [0,1].
    """
    S: float  # Survival
    M: float  # Maintaining previous policies
    R: float  # Regional dominance
    C: float  # Credible internal power
    V: float  # Not getting subjected to violence

    def validated(self) -> "EventProbs":
        return EventProbs(
            S=_clamp01(self.S, "S"),
            M=_clamp01(self.M, "M"),
            R=_clamp01(self.R, "R"),
            C=_clamp01(self.C, "C"),
            V=_clamp01(self.V, "V"),
        )


def expected_payoff_analytic(p: EventProbs, cap_100: bool = True) -> float:
    """
    Expected payoff out of 100, computed analytically.

    E[Payoff] = P(S) * (50 + 20*P(M) + 20*P(R) + 10*P(C))
                + (1-P(S)) * (20*P(V))

    NOTE:
    - This assumes independence / unconditional probabilities as provided.
    - If you later want conditional probabilities (e.g., M/R/C depend on survival),
      you can extend the formula accordingly.

    cap_100:
      If True, caps the expected payoff at 100 (usually unnecessary here because
      max in survive branch is 50+20+20+10=100).
    """
    p = p.validated()

    survive_branch = BASE_SURVIVE + W_M * p.M + W_R * p.R + W_C * p.C
    no_survive_branch = W_V * p.V

    expected = p.S * survive_branch + (1.0 - p.S) * no_survive_branch

    if cap_100:
        expected = min(100.0, max(0.0, expected))
    return expected


def payoff_one_draw(p: EventProbs, rng: Optional[random.Random] = None) -> float:
    """
    Generate ONE payoff realization (0..100) by sampling events as Bernoulli trials.
    This is useful if you want to simulate distributions.

    IMPORTANT:
    This samples each event independently using its probability.
    """
    p = p.validated()
    rng = rng or random.Random()

    S = rng.random() < p.S
    M = rng.random() < p.M
    R = rng.random() < p.R
    C = rng.random() < p.C
    V = rng.random() < p.V

    payoff = 0.0

    if S:
        payoff += BASE_SURVIVE
        payoff += W_M if M else 0.0
        payoff += W_R if R else 0.0
        payoff += W_C if C else 0.0
        # V ignored in survive branch
    else:
        payoff += W_V if V else 0.0
        # M/R/C ignored in no-survival branch

    return payoff


def expected_payoff_monte_carlo(
    p: EventProbs,
    n: int = 200_000,
    seed: int = 42,
) -> float:
    """
    Monte Carlo estimate of expected payoff out of 100.
    Sanity-check for the analytic expectation.
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
    Helpful breakdown of components for debugging / reporting.
    Returns a dict you can print or log.
    """
    p = p.validated()

    survive_branch = BASE_SURVIVE + W_M * p.M + W_R * p.R + W_C * p.C
    no_survive_branch = W_V * p.V
    expected = expected_payoff_analytic(p)

    return {
        "inputs": {"S": p.S, "M": p.M, "R": p.R, "C": p.C, "V": p.V},
        "branch_payoffs": {
            "payoff_if_survive_expected_given_probs": survive_branch,
            "payoff_if_not_survive_expected_given_probs": no_survive_branch,
        },
        "expected_payoff": expected,
        "max_payoff_if_survive": 100.0,
        "max_payoff_if_not_survive": W_V,
    }


if __name__ == "__main__":
    # --- Example usage (edit these probabilities) ---
    probs = EventProbs(
        S=0.70,  # Survival
        M=0.40,  # Maintaining previous policies
        R=0.30,  # Regional dominance
        C=0.50,  # Credible internal power
        V=0.60,  # Not getting subjected to violence
    )

    print("=== Analytic expected payoff ===")
    e = expected_payoff_analytic(probs)
    print(f"Expected payoff: {e:.2f} / 100")

    print("\n=== Monte Carlo sanity check ===")
    e_mc = expected_payoff_monte_carlo(probs, n=200_000, seed=1)
    print(f"Monte Carlo expected payoff: {e_mc:.2f} / 100")

    print("\n=== Breakdown ===")
    info = breakdown(probs)
    for k, v in info.items():
        print(f"{k}: {v}")