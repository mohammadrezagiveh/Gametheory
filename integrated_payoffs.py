#!/usr/bin/env python3
"""
Integrated Three-Player Game: Opposition vs Regime vs Israel

This module integrates the payoff calculations for all three players:
- Player 1 (Opposition): Stage I additive + Stage II multiplicative degradation
- Player 2 (Regime): Survival-based with additive bonuses
- Player 3 (Israel): Two-bank additive system

The system reads probability parameters from a CSV file and computes
expected payoffs for each strategy combination.
"""

from __future__ import annotations
from dataclasses import dataclass
from itertools import product
import csv
import numpy as np
from typing import Dict, List, Tuple, Any, Optional


# =============================================================================
# OPPOSITION PAYOFF MODEL (Player 1)
# =============================================================================

# Stage I additive bank weights (points out of 100)
OPP_W_PR = 30.0   # Political Reform
OPP_W_CL = 30.0   # Civil Liberties
OPP_W_MI = 40.0   # Material Improvement

# Stage II degradation multipliers (apply when event is "No")
OPP_MULT_BI_NO = 0.30   # Border Integrity
OPP_MULT_IS_NO = 0.70   # Infrastructure Survival
OPP_MULT_MD_NO = 0.40   # Maintaining Deterrence
OPP_MULT_LOC_NO = 0.70  # Lack of Casualty


@dataclass(frozen=True)
class OppositionProbs:
    """Probabilities for Opposition goals (0..1)."""
    BI: float   # Border Integrity
    IS: float   # Infrastructure Survival
    MD: float   # Maintaining Deterrence
    LoC: float  # Lack of Casualty
    PR: float   # Political Reform
    CL: float   # Civil Liberties
    MI: float   # Material Improvement


def opposition_payoff_realization(
    BI: bool, IS: bool, MD: bool, LoC: bool,
    PR: bool, CL: bool, MI: bool
) -> float:
    """One realized payoff for Opposition given boolean outcomes."""
    # Stage I: build bank additively
    bank = 0.0
    if PR:
        bank += OPP_W_PR
    if CL:
        bank += OPP_W_CL
    if MI:
        bank += OPP_W_MI

    # Stage II: degrade bank when things go wrong
    if not BI:
        bank *= OPP_MULT_BI_NO
    if not IS:
        bank *= OPP_MULT_IS_NO
    if not MD:
        bank *= OPP_MULT_MD_NO
    if not LoC:
        bank *= OPP_MULT_LOC_NO

    return bank


def opposition_expected_payoff(p: OppositionProbs) -> float:
    """
    Exact expected payoff for Opposition via full enumeration of all 128 states.
    Assumes independence across events.
    """
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

        expected += state_prob * opposition_payoff_realization(BI, IS, MD, LoC, PR, CL, MI)

    return expected


# =============================================================================
# REGIME PAYOFF MODEL (Player 2)
# =============================================================================

# Weights for Regime payoff
REG_BASE_SURVIVE = 50.0
REG_W_M = 20.0  # Maintaining previous policies
REG_W_R = 20.0  # Regional dominance
REG_W_C = 10.0  # Credible internal power
REG_W_V = 20.0  # Not getting subjected to violence


@dataclass(frozen=True)
class RegimeProbs:
    """Probabilities for Regime goals (0..1)."""
    S: float  # Survival
    M: float  # Maintaining previous policies
    R: float  # Regional dominance
    C: float  # Credible internal power
    V: float  # Not getting subjected to violence


def regime_expected_payoff(p: RegimeProbs) -> float:
    """
    Expected payoff for Regime.
    
    If Survival (S=True): Base 50 + bonuses from M, R, C
    If No Survival (S=False): Only V contributes (20 points)
    """
    survive_branch = REG_BASE_SURVIVE + REG_W_M * p.M + REG_W_R * p.R + REG_W_C * p.C
    no_survive_branch = REG_W_V * p.V

    expected = p.S * survive_branch + (1.0 - p.S) * no_survive_branch
    return min(100.0, max(0.0, expected))


# =============================================================================
# ISRAEL PAYOFF MODEL (Player 3)
# =============================================================================

# Bank 1 weights (sum to 1.0)
ISR_W_G1 = 0.30
ISR_W_G2 = 0.20
ISR_W_G3 = 0.50

# Bank 2 weights (sum to 1.0)
ISR_W_G4 = 0.30
ISR_W_G5 = 0.70

# Final payoff weights
ISR_W_BANK1 = 0.60
ISR_W_BANK2 = 0.40

ISR_BANK_MAX = 100.0


@dataclass(frozen=True)
class IsraelProbs:
    """Probabilities for Israel goals (0..1)."""
    G1: float  # Goal 1
    G2: float  # Goal 2
    G3: float  # Goal 3
    G4: float  # Goal 4
    G5: float  # Goal 5


def israel_expected_payoff(p: IsraelProbs) -> float:
    """
    Expected payoff for Israel using two-bank additive system.
    
    Bank1 = 100 * (0.30*G1 + 0.20*G2 + 0.50*G3)
    Bank2 = 100 * (0.30*G4 + 0.70*G5)
    Final = 0.60 * Bank1 + 0.40 * Bank2
    """
    bank1 = ISR_BANK_MAX * (ISR_W_G1 * p.G1 + ISR_W_G2 * p.G2 + ISR_W_G3 * p.G3)
    bank2 = ISR_BANK_MAX * (ISR_W_G4 * p.G4 + ISR_W_G5 * p.G5)
    return ISR_W_BANK1 * bank1 + ISR_W_BANK2 * bank2


# =============================================================================
# CSV LOADING AND GAME CONSTRUCTION
# =============================================================================

def load_probabilities_from_csv(filepath: str) -> Dict[Tuple[int, int, int], Dict[str, Dict[str, float]]]:
    """
    Load probability parameters from CSV file.
    
    Expected CSV format:
    p1_strat,p2_strat,p3_strat,opp_BI,opp_IS,opp_MD,opp_LoC,opp_PR,opp_CL,opp_MI,reg_S,reg_M,reg_R,reg_C,reg_V,isr_G1,isr_G2,isr_G3,isr_G4,isr_G5
    
    Returns:
        Dictionary mapping (p1_strat, p2_strat, p3_strat) to player probability dicts
    """
    probabilities = {}
    
    with open(filepath, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row['p1_strat']), int(row['p2_strat']), int(row['p3_strat']))
            
            probabilities[key] = {
                'opposition': {
                    'BI': float(row['opp_BI']),
                    'IS': float(row['opp_IS']),
                    'MD': float(row['opp_MD']),
                    'LoC': float(row['opp_LoC']),
                    'PR': float(row['opp_PR']),
                    'CL': float(row['opp_CL']),
                    'MI': float(row['opp_MI']),
                },
                'regime': {
                    'S': float(row['reg_S']),
                    'M': float(row['reg_M']),
                    'R': float(row['reg_R']),
                    'C': float(row['reg_C']),
                    'V': float(row['reg_V']),
                },
                'israel': {
                    'G1': float(row['isr_G1']),
                    'G2': float(row['isr_G2']),
                    'G3': float(row['isr_G3']),
                    'G4': float(row['isr_G4']),
                    'G5': float(row['isr_G5']),
                }
            }
    
    return probabilities


def compute_payoffs_from_probabilities(
    probabilities: Dict[Tuple[int, int, int], Dict[str, Dict[str, float]]]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute payoff matrices from probability parameters.
    
    Returns:
        Tuple of (opposition_payoffs, regime_payoffs, israel_payoffs)
        Each array has shape (2, 4, 2) for the 2x4x2 game
    """
    # Initialize payoff matrices
    payoffs_p1 = np.zeros((2, 4, 2))  # Opposition
    payoffs_p2 = np.zeros((2, 4, 2))  # Regime
    payoffs_p3 = np.zeros((2, 4, 2))  # Israel
    
    for (p1, p2, p3), probs in probabilities.items():
        # Opposition payoff
        opp_probs = OppositionProbs(**probs['opposition'])
        payoffs_p1[p1, p2, p3] = opposition_expected_payoff(opp_probs)
        
        # Regime payoff
        reg_probs = RegimeProbs(**probs['regime'])
        payoffs_p2[p1, p2, p3] = regime_expected_payoff(reg_probs)
        
        # Israel payoff
        isr_probs = IsraelProbs(**probs['israel'])
        payoffs_p3[p1, p2, p3] = israel_expected_payoff(isr_probs)
    
    return payoffs_p1, payoffs_p2, payoffs_p3


def normalize_payoffs(payoffs_p1: np.ndarray, payoffs_p2: np.ndarray, 
                      payoffs_p3: np.ndarray, scale: float = 10.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalize payoffs to a common scale (e.g., 0-10) for easier comparison.
    
    Args:
        payoffs_p1, payoffs_p2, payoffs_p3: Raw payoff matrices (0-100 scale)
        scale: Target maximum value
    
    Returns:
        Normalized payoff matrices
    """
    return (
        payoffs_p1 * scale / 100.0,
        payoffs_p2 * scale / 100.0,
        payoffs_p3 * scale / 100.0
    )


# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def display_payoff_matrices(payoffs_p1: np.ndarray, payoffs_p2: np.ndarray, 
                            payoffs_p3: np.ndarray, player_names: Tuple[str, str, str] = None):
    """
    Display payoff matrices for all three players in a readable format.
    
    Args:
        payoffs_p1, payoffs_p2, payoffs_p3: Payoff arrays of shape (2, 4, 2)
        player_names: Optional tuple of player names (default: Opposition, Regime, Israel)
    """
    if player_names is None:
        player_names = ("Opposition", "Regime", "Israel")
    
    p1_name, p2_name, p3_name = player_names
    
    print("\n" + "=" * 80)
    print("PAYOFF MATRICES")
    print("=" * 80)
    
    # For each combination of P1 and P3 strategies
    for p1_strat in range(2):
        for p3_strat in range(2):
            print(f"\n{p1_name} Strategy {p1_strat}, {p3_name} Strategy {p3_strat}")
            print("-" * 80)
            
            # Header
            print(f"{'Regime Strat':<15} {'Opposition':<15} {'Regime':<15} {'Israel':<15}")
            print("-" * 80)
            
            # Display each regime strategy
            for p2_strat in range(4):
                opp_payoff = payoffs_p1[p1_strat, p2_strat, p3_strat]
                reg_payoff = payoffs_p2[p1_strat, p2_strat, p3_strat]
                isr_payoff = payoffs_p3[p1_strat, p2_strat, p3_strat]
                
                print(f"{p2_strat:<15} {opp_payoff:<15.2f} {reg_payoff:<15.2f} {isr_payoff:<15.2f}")


def display_payoff_summary(payoffs_p1: np.ndarray, payoffs_p2: np.ndarray, 
                          payoffs_p3: np.ndarray):
    """Display summary statistics for each player's payoffs."""
    print("\n" + "=" * 80)
    print("PAYOFF SUMMARY STATISTICS")
    print("=" * 80)
    
    players = [
        ("Opposition", payoffs_p1),
        ("Regime", payoffs_p2),
        ("Israel", payoffs_p3)
    ]
    
    for name, payoffs in players:
        print(f"\n{name}:")
        print(f"  Min:    {np.min(payoffs):.2f}")
        print(f"  Max:    {np.max(payoffs):.2f}")
        print(f"  Mean:   {np.mean(payoffs):.2f}")
        print(f"  Median: {np.median(payoffs):.2f}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to load CSV and compute payoffs."""
    print("Three-Player Game Payoff Calculator")
    print("=" * 50)
    
    # Prompt for CSV file path
    csv_path = input("\nEnter the path to your CSV file: ").strip()
    
    # Remove quotes if user included them
    csv_path = csv_path.strip('"').strip("'")
    
    try:
        # Load probabilities from CSV
        print(f"\nLoading probabilities from: {csv_path}")
        probabilities = load_probabilities_from_csv(csv_path)
        print(f"Successfully loaded {len(probabilities)} strategy combinations")
        
        # Compute payoffs
        print("\nComputing expected payoffs...")
        payoffs_p1, payoffs_p2, payoffs_p3 = compute_payoffs_from_probabilities(probabilities)
        
        # Optional: normalize payoffs
        normalize = input("\nNormalize payoffs to 0-10 scale? (y/n): ").strip().lower()
        if normalize == 'y':
            payoffs_p1, payoffs_p2, payoffs_p3 = normalize_payoffs(payoffs_p1, payoffs_p2, payoffs_p3)
            print("Payoffs normalized to 0-10 scale")
        
        print("\nPayoff computation complete!")
        print(f"Opposition payoffs shape: {payoffs_p1.shape}")
        print(f"Regime payoffs shape: {payoffs_p2.shape}")
        print(f"Israel payoffs shape: {payoffs_p3.shape}")
        
        # Display the payoff matrices
        display_payoff_matrices(payoffs_p1, payoffs_p2, payoffs_p3)
        
        # Display summary statistics
        display_payoff_summary(payoffs_p1, payoffs_p2, payoffs_p3)
        
        return payoffs_p1, payoffs_p2, payoffs_p3
        
    except FileNotFoundError:
        print(f"\nError: File '{csv_path}' not found.")
        print("Please check the path and try again.")
        return None, None, None
    except KeyError as e:
        print(f"\nError: Missing required column in CSV: {e}")
        print("Please ensure your CSV has all required columns.")
        return None, None, None
    except Exception as e:
        print(f"\nError loading or processing CSV: {e}")
        return None, None, None


if __name__ == "__main__":
    main()