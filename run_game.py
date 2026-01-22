#!/usr/bin/env python3
"""
Three-Player Geopolitical Game: Nash Equilibrium Calculator

Integrates:
- Opposition payoff model (Stage I additive + Stage II multiplicative)
- Regime payoff model (Survival-based with additive bonuses)
- Israel payoff model (Two-bank additive system)

Players:
- Player 1: Opposition (2 strategies: Escalate, Deescalate)
- Player 2: Regime (4 strategies: combinations of E/D against Israel and Opposition)
- Player 3: Israel (2 strategies: Escalate, Deescalate)

Usage:
    python run_game.py <csv_file>        # Run with custom probabilities
    python run_game.py --sample          # Generate sample CSV
    python run_game.py --pdf             # Use PDF example values
"""

import sys
import csv
import numpy as np
from typing import Dict, Tuple, List

from three_player_nash import ThreePlayerGame
from integrated_payoffs import (
    OppositionProbs, RegimeProbs, IsraelProbs,
    opposition_expected_payoff, regime_expected_payoff, israel_expected_payoff,
    load_probabilities_from_csv, compute_payoffs_from_probabilities,
    normalize_payoffs
)


# Strategy labels
P1_LABELS = ["Escalate", "Deescalate"]
P2_LABELS = [
    "Escalate vs Israel & Escalate vs Opposition",
    "Escalate vs Israel & Deescalate vs Opposition",
    "Deescalate vs Israel & Escalate vs Opposition",
    "Deescalate vs Israel & Deescalate vs Opposition"
]
P2_SHORT_LABELS = ["E-Isr & E-Opp", "E-Isr & D-Opp", "D-Isr & E-Opp", "D-Isr & D-Opp"]
P3_LABELS = ["Escalate", "Deescalate"]


def display_payoff_tables(payoffs_p1: np.ndarray, payoffs_p2: np.ndarray, 
                          payoffs_p3: np.ndarray, title: str = "GAME PAYOFF TABLES"):
    """Display game payoff tables in a readable format."""
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)
    
    for p3_idx in range(2):
        print(f"\n{'=' * 90}")
        print(f"ISRAEL: {P3_LABELS[p3_idx].upper()}")
        print("=" * 90)
        
        # Header
        print(f"\n{'Opposition':<15}", end="")
        for p2_idx in range(4):
            print(f"{P2_SHORT_LABELS[p2_idx]:<20}", end="")
        print()
        print("-" * 90)
        
        # Rows
        for p1_idx in range(2):
            print(f"{P1_LABELS[p1_idx]:<15}", end="")
            for p2_idx in range(4):
                p1_pay = payoffs_p1[p1_idx, p2_idx, p3_idx]
                p2_pay = payoffs_p2[p1_idx, p2_idx, p3_idx]
                p3_pay = payoffs_p3[p1_idx, p2_idx, p3_idx]
                print(f"({p1_pay:>5.2f},{p2_pay:>5.2f},{p3_pay:>5.2f})", end="  ")
            print()


def display_equilibria(equilibria: List[Tuple[int, int, int]], 
                       payoffs_p1: np.ndarray, payoffs_p2: np.ndarray, 
                       payoffs_p3: np.ndarray):
    """Display Nash equilibria with detailed information."""
    print("\n" + "=" * 90)
    print("PURE STRATEGY NASH EQUILIBRIA")
    print("=" * 90)
    
    if not equilibria:
        print("\nNo pure strategy Nash equilibria found.")
        print("\nThis suggests the game may only have mixed strategy equilibria,")
        print("which require probabilistic mixing over strategies.")
    else:
        print(f"\nFound {len(equilibria)} pure strategy Nash equilibrium/equilibria:\n")
        
        for i, eq in enumerate(equilibria, 1):
            print(f"{'─' * 70}")
            print(f"EQUILIBRIUM {i}")
            print(f"{'─' * 70}")
            print(f"  Player 1 (Opposition): {P1_LABELS[eq[0]]} (Strategy {eq[0]})")
            print(f"  Player 2 (Regime):     {P2_LABELS[eq[1]]} (Strategy {eq[1]})")
            print(f"  Player 3 (Israel):     {P3_LABELS[eq[2]]} (Strategy {eq[2]})")
            print(f"\n  Payoffs:")
            print(f"    Opposition: {payoffs_p1[eq]:.2f}")
            print(f"    Regime:     {payoffs_p2[eq]:.2f}")
            print(f"    Israel:     {payoffs_p3[eq]:.2f}")
            print()


def analyze_best_responses(game: ThreePlayerGame, 
                           payoffs_p1: np.ndarray, payoffs_p2: np.ndarray,
                           payoffs_p3: np.ndarray):
    """Analyze and display best response structure."""
    print("\n" + "=" * 90)
    print("BEST RESPONSE ANALYSIS")
    print("=" * 90)
    
    print("\nFor each player, showing best responses given others' strategies:\n")
    
    # Player 1 (Opposition) best responses
    print("OPPOSITION best responses:")
    for p2 in range(4):
        for p3 in range(2):
            br = game.find_best_responses(0, (p2, p3))
            br_labels = [P1_LABELS[b] for b in br]
            print(f"  vs Regime={P2_SHORT_LABELS[p2]}, Israel={P3_LABELS[p3]}: {br_labels}")
    
    print("\nREGIME best responses:")
    for p1 in range(2):
        for p3 in range(2):
            br = game.find_best_responses(1, (p1, p3))
            br_labels = [P2_SHORT_LABELS[b] for b in br]
            print(f"  vs Opposition={P1_LABELS[p1]}, Israel={P3_LABELS[p3]}: {br_labels}")
    
    print("\nISRAEL best responses:")
    for p1 in range(2):
        for p2 in range(4):
            br = game.find_best_responses(2, (p1, p2))
            br_labels = [P3_LABELS[b] for b in br]
            print(f"  vs Opposition={P1_LABELS[p1]}, Regime={P2_SHORT_LABELS[p2]}: {br_labels}")


def create_game_probability_csv(filepath: str, probabilities: Dict):
    """Create a CSV with all strategy combinations and probability parameters."""
    header = [
        'p1_strat', 'p1_label', 'p2_strat', 'p2_label', 'p3_strat', 'p3_label',
        'opp_BI', 'opp_IS', 'opp_MD', 'opp_LoC', 'opp_PR', 'opp_CL', 'opp_MI',
        'reg_S', 'reg_M', 'reg_R', 'reg_C', 'reg_V',
        'isr_G1', 'isr_G2', 'isr_G3', 'isr_G4', 'isr_G5',
        'computed_opp_payoff', 'computed_reg_payoff', 'computed_isr_payoff'
    ]
    
    rows = []
    for (p1, p2, p3), probs in sorted(probabilities.items()):
        opp_probs = OppositionProbs(**probs['opposition'])
        reg_probs = RegimeProbs(**probs['regime'])
        isr_probs = IsraelProbs(**probs['israel'])
        
        row = {
            'p1_strat': p1, 'p1_label': P1_LABELS[p1],
            'p2_strat': p2, 'p2_label': P2_SHORT_LABELS[p2],
            'p3_strat': p3, 'p3_label': P3_LABELS[p3],
            **{f'opp_{k}': v for k, v in probs['opposition'].items()},
            **{f'reg_{k}': v for k, v in probs['regime'].items()},
            **{f'isr_{k}': v for k, v in probs['israel'].items()},
            'computed_opp_payoff': f"{opposition_expected_payoff(opp_probs):.2f}",
            'computed_reg_payoff': f"{regime_expected_payoff(reg_probs):.2f}",
            'computed_isr_payoff': f"{israel_expected_payoff(isr_probs):.2f}",
        }
        rows.append(row)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    
    return filepath


def run_game_from_csv(csv_path: str, scale: float = 10.0, verbose: bool = True):
    """
    Run the complete game analysis from a CSV file.
    
    Args:
        csv_path: Path to CSV with probability parameters
        scale: Scale for payoff normalization (default 10.0 for 0-10 scale)
        verbose: Whether to print detailed analysis
    
    Returns:
        Tuple of (game, equilibria, payoffs)
    """
    print("\n" + "=" * 90)
    print("THREE-PLAYER GEOPOLITICAL GAME ANALYZER")
    print("=" * 90)
    print(f"\nLoading probabilities from: {csv_path}")
    
    # Load and compute payoffs
    probabilities = load_probabilities_from_csv(csv_path)
    payoffs_p1, payoffs_p2, payoffs_p3 = compute_payoffs_from_probabilities(probabilities)
    
    # Normalize to desired scale
    if scale != 100.0:
        payoffs_p1, payoffs_p2, payoffs_p3 = normalize_payoffs(
            payoffs_p1, payoffs_p2, payoffs_p3, scale=scale
        )
    
    # Display payoff tables
    if verbose:
        display_payoff_tables(payoffs_p1, payoffs_p2, payoffs_p3,
                             title=f"GAME PAYOFF TABLES (0-{scale:.0f} scale)")
    
    # Create game and find equilibria
    game = ThreePlayerGame([payoffs_p1, payoffs_p2, payoffs_p3])
    equilibria = game.find_pure_nash_equilibria()
    
    # Display equilibria
    display_equilibria(equilibria, payoffs_p1, payoffs_p2, payoffs_p3)
    
    # Best response analysis
    if verbose:
        analyze_best_responses(game, payoffs_p1, payoffs_p2, payoffs_p3)
    
    return game, equilibria, (payoffs_p1, payoffs_p2, payoffs_p3)


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("THREE-PLAYER GEOPOLITICAL GAME - NASH EQUILIBRIUM CALCULATOR")
    print("=" * 70)
    
    csv_path = input("\nEnter the path to your CSV file: ").strip()
    
    if not csv_path:
        print("Error: No file path provided.")
        return
    
    run_game_from_csv(csv_path)


if __name__ == "__main__":
    main()