#!/usr/bin/env python3
"""
Three-Player Nash Equilibrium Calculator

Supports games with asymmetric strategy spaces (e.g., 2x4x2).
Finds pure strategy Nash equilibria by checking best response conditions.
"""

import numpy as np
from typing import List, Tuple, Optional


class ThreePlayerGame:
    """
    A three-player normal form game.
    
    Attributes:
        payoffs: List of three numpy arrays, one for each player.
                 Shape is (n1, n2, n3) where ni is the number of strategies for player i.
    """
    
    def __init__(self, payoffs: List[np.ndarray]):
        """
        Initialize the game with payoff matrices.
        
        Args:
            payoffs: List of 3 numpy arrays [payoffs_p1, payoffs_p2, payoffs_p3]
                    Each array has shape (n1, n2, n3)
        """
        if len(payoffs) != 3:
            raise ValueError("Must provide exactly 3 payoff matrices")
        
        self.payoffs = [np.array(p) for p in payoffs]
        self.shape = self.payoffs[0].shape
        
        # Verify all payoff matrices have the same shape
        for i, p in enumerate(self.payoffs):
            if p.shape != self.shape:
                raise ValueError(f"Payoff matrix {i} has shape {p.shape}, expected {self.shape}")
        
        self.n_strategies = list(self.shape)
    
    def get_payoff(self, player: int, strategy_profile: Tuple[int, int, int]) -> float:
        """Get payoff for a player given a strategy profile."""
        return self.payoffs[player][strategy_profile]
    
    def is_best_response(self, player: int, strategy: int, 
                         other_strategies: Tuple[int, ...]) -> bool:
        """
        Check if a strategy is a best response for a player given others' strategies.
        
        Args:
            player: Player index (0, 1, or 2)
            strategy: The strategy to check
            other_strategies: Tuple of the other two players' strategies
        
        Returns:
            True if the strategy is a best response
        """
        # Build the full strategy profile for comparison
        if player == 0:
            current_payoff = self.payoffs[0][strategy, other_strategies[0], other_strategies[1]]
            # Check all alternative strategies for player 0
            for alt_strat in range(self.n_strategies[0]):
                alt_payoff = self.payoffs[0][alt_strat, other_strategies[0], other_strategies[1]]
                if alt_payoff > current_payoff:
                    return False
        elif player == 1:
            current_payoff = self.payoffs[1][other_strategies[0], strategy, other_strategies[1]]
            for alt_strat in range(self.n_strategies[1]):
                alt_payoff = self.payoffs[1][other_strategies[0], alt_strat, other_strategies[1]]
                if alt_payoff > current_payoff:
                    return False
        else:  # player == 2
            current_payoff = self.payoffs[2][other_strategies[0], other_strategies[1], strategy]
            for alt_strat in range(self.n_strategies[2]):
                alt_payoff = self.payoffs[2][other_strategies[0], other_strategies[1], alt_strat]
                if alt_payoff > current_payoff:
                    return False
        
        return True
    
    def is_nash_equilibrium(self, strategy_profile: Tuple[int, int, int]) -> bool:
        """
        Check if a strategy profile is a Nash equilibrium.
        
        A strategy profile is a Nash equilibrium if each player's strategy
        is a best response to the others' strategies.
        """
        s1, s2, s3 = strategy_profile
        
        # Check if Player 1's strategy is a best response
        if not self.is_best_response(0, s1, (s2, s3)):
            return False
        
        # Check if Player 2's strategy is a best response
        if not self.is_best_response(1, s2, (s1, s3)):
            return False
        
        # Check if Player 3's strategy is a best response
        if not self.is_best_response(2, s3, (s1, s2)):
            return False
        
        return True
    
    def find_pure_nash_equilibria(self) -> List[Tuple[int, int, int]]:
        """
        Find all pure strategy Nash equilibria.
        
        Returns:
            List of strategy profiles that are Nash equilibria
        """
        equilibria = []
        
        for s1 in range(self.n_strategies[0]):
            for s2 in range(self.n_strategies[1]):
                for s3 in range(self.n_strategies[2]):
                    if self.is_nash_equilibrium((s1, s2, s3)):
                        equilibria.append((s1, s2, s3))
        
        return equilibria
    
    def find_best_responses(self, player: int, 
                            other_strategies: Tuple[int, ...]) -> List[int]:
        """
        Find all best responses for a player given others' strategies.
        
        Returns:
            List of strategies that are best responses
        """
        best_payoff = float('-inf')
        best_responses = []
        
        for strat in range(self.n_strategies[player]):
            if player == 0:
                payoff = self.payoffs[0][strat, other_strategies[0], other_strategies[1]]
            elif player == 1:
                payoff = self.payoffs[1][other_strategies[0], strat, other_strategies[1]]
            else:
                payoff = self.payoffs[2][other_strategies[0], other_strategies[1], strat]
            
            if payoff > best_payoff:
                best_payoff = payoff
                best_responses = [strat]
            elif payoff == best_payoff:
                best_responses.append(strat)
        
        return best_responses
    
    def display_payoff_tables(self, 
                              p1_labels: Optional[List[str]] = None,
                              p2_labels: Optional[List[str]] = None,
                              p3_labels: Optional[List[str]] = None) -> str:
        """
        Generate a string representation of the payoff tables.
        """
        output = []
        
        p1_labels = p1_labels or [f"S{i}" for i in range(self.n_strategies[0])]
        p2_labels = p2_labels or [f"S{i}" for i in range(self.n_strategies[1])]
        p3_labels = p3_labels or [f"S{i}" for i in range(self.n_strategies[2])]
        
        for p3_idx in range(self.n_strategies[2]):
            output.append(f"\n{'='*80}")
            output.append(f"Player 3: {p3_labels[p3_idx]}")
            output.append("="*80)
            
            # Header
            header = f"{'P1/P2':<15}"
            for p2_idx in range(self.n_strategies[1]):
                header += f"{p2_labels[p2_idx]:<18}"
            output.append(header)
            output.append("-" * 80)
            
            # Rows
            for p1_idx in range(self.n_strategies[0]):
                row = f"{p1_labels[p1_idx]:<15}"
                for p2_idx in range(self.n_strategies[1]):
                    p1_pay = self.payoffs[0][p1_idx, p2_idx, p3_idx]
                    p2_pay = self.payoffs[1][p1_idx, p2_idx, p3_idx]
                    p3_pay = self.payoffs[2][p1_idx, p2_idx, p3_idx]
                    row += f"({p1_pay:>5.2f},{p2_pay:>5.2f},{p3_pay:>5.2f}) "
                output.append(row)
        
        return "\n".join(output)


if __name__ == "__main__":
    # Test with a simple 2x2x2 game
    p1 = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    p2 = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    p3 = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    
    game = ThreePlayerGame([p1, p2, p3])
    print("Game shape:", game.shape)
    print("Nash equilibria:", game.find_pure_nash_equilibria())
