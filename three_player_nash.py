import numpy as np
from scipy.optimize import minimize, LinearConstraint
import itertools
from typing import List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class ThreePlayerGame:
    """
    A class to represent and analyze 3-player normal form games.
    
    Each player has a set of strategies, and payoffs are defined for each 
    combination of strategies.
    """
    
    def __init__(self, payoff_matrices: List[np.ndarray]):
        """
        Initialize the game with payoff matrices.
        
        Parameters:
        -----------
        payoff_matrices : List[np.ndarray]
            List of 3 numpy arrays, one for each player.
            Each matrix should have shape (n1, n2, n3) where ni is the number
            of strategies for player i.
            payoff_matrices[i][s1, s2, s3] gives player i's payoff when
            player 1 plays strategy s1, player 2 plays s2, player 3 plays s3.
        """
        if len(payoff_matrices) != 3:
            raise ValueError("Must provide exactly 3 payoff matrices")
        
        self.payoffs = payoff_matrices
        self.shape = payoff_matrices[0].shape
        
        # Verify all matrices have the same shape
        for i, matrix in enumerate(payoff_matrices):
            if matrix.shape != self.shape:
                raise ValueError(f"All payoff matrices must have the same shape. "
                               f"Matrix {i} has shape {matrix.shape}, expected {self.shape}")
        
        self.n_strategies = self.shape  # (n1, n2, n3)
        
    def get_payoff(self, strategies: Tuple[int, int, int], player: int) -> float:
        """Get payoff for a player given pure strategy profile."""
        return self.payoffs[player][strategies]
    
    def expected_payoff(self, mixed_strategies: List[np.ndarray], player: int) -> float:
        """
        Calculate expected payoff for a player given mixed strategy profile.
        
        Parameters:
        -----------
        mixed_strategies : List[np.ndarray]
            List of 3 probability distributions (one per player)
        player : int
            Player index (0, 1, or 2)
        """
        payoff = 0.0
        for s1 in range(self.n_strategies[0]):
            for s2 in range(self.n_strategies[1]):
                for s3 in range(self.n_strategies[2]):
                    prob = (mixed_strategies[0][s1] * 
                           mixed_strategies[1][s2] * 
                           mixed_strategies[2][s3])
                    payoff += prob * self.payoffs[player][s1, s2, s3]
        return payoff
    
    def best_response_pure(self, other_strategies: Tuple[int, int], 
                          player: int) -> Tuple[int, float]:
        """
        Find best pure strategy response for a player given others' strategies.
        
        Parameters:
        -----------
        other_strategies : Tuple[int, int]
            Strategies of the other two players
        player : int
            Player index (0, 1, or 2)
        
        Returns:
        --------
        Tuple[int, float] : (best_strategy, payoff)
        """
        best_strategy = 0
        best_payoff = float('-inf')
        
        for strategy in range(self.n_strategies[player]):
            # Construct full strategy profile
            if player == 0:
                full_strategy = (strategy, other_strategies[0], other_strategies[1])
            elif player == 1:
                full_strategy = (other_strategies[0], strategy, other_strategies[1])
            else:
                full_strategy = (other_strategies[0], other_strategies[1], strategy)
            
            payoff = self.get_payoff(full_strategy, player)
            
            if payoff > best_payoff:
                best_payoff = payoff
                best_strategy = strategy
        
        return best_strategy, best_payoff
    
    def is_pure_nash(self, strategies: Tuple[int, int, int]) -> bool:
        """Check if a pure strategy profile is a Nash equilibrium."""
        # For each player, check if their strategy is a best response
        for player in range(3):
            # Get other players' strategies
            if player == 0:
                others = (strategies[1], strategies[2])
            elif player == 1:
                others = (strategies[0], strategies[2])
            else:
                others = (strategies[0], strategies[1])
            
            best_strat, _ = self.best_response_pure(others, player)
            
            if best_strat != strategies[player]:
                return False
        
        return True
    
    def find_pure_nash_equilibria(self) -> List[Tuple[int, int, int]]:
        """Find all pure strategy Nash equilibria."""
        equilibria = []
        
        # Check all possible strategy combinations
        for s1 in range(self.n_strategies[0]):
            for s2 in range(self.n_strategies[1]):
                for s3 in range(self.n_strategies[2]):
                    strategies = (s1, s2, s3)
                    if self.is_pure_nash(strategies):
                        equilibria.append(strategies)
        
        return equilibria
    
    def expected_payoff_given_others(self, own_mixed: np.ndarray, 
                                     other_mixed: List[np.ndarray], 
                                     player: int) -> float:
        """
        Calculate expected payoff for player given their mixed strategy 
        and others' mixed strategies.
        """
        full_mixed = other_mixed.copy()
        full_mixed.insert(player, own_mixed)
        return self.expected_payoff(full_mixed, player)
    
    def find_mixed_nash_support_enumeration(self, max_support_size: int = None) -> List[Tuple]:
        """
        Find mixed strategy Nash equilibria using support enumeration.
        
        This method tries different support sets (subsets of strategies that 
        are played with positive probability).
        """
        if max_support_size is None:
            max_support_size = min(self.n_strategies)
        
        equilibria = []
        
        # Try different support sizes
        for support_sizes in itertools.product(
            range(1, min(max_support_size, self.n_strategies[0]) + 1),
            range(1, min(max_support_size, self.n_strategies[1]) + 1),
            range(1, min(max_support_size, self.n_strategies[2]) + 1)
        ):
            # Try different support combinations
            for supports in itertools.product(
                itertools.combinations(range(self.n_strategies[0]), support_sizes[0]),
                itertools.combinations(range(self.n_strategies[1]), support_sizes[1]),
                itertools.combinations(range(self.n_strategies[2]), support_sizes[2])
            ):
                eq = self._solve_for_support(supports)
                if eq is not None:
                    equilibria.append(eq)
        
        return equilibria
    
    def _solve_for_support(self, supports: Tuple) -> Optional[Tuple]:
        """
        Attempt to find equilibrium with given support.
        Returns None if no valid equilibrium exists for this support.
        """
        try:
            # Create initial guess
            mixed_strategies = []
            for player in range(3):
                strategy = np.zeros(self.n_strategies[player])
                support = supports[player]
                strategy[list(support)] = 1.0 / len(support)
                mixed_strategies.append(strategy)
            
            # Use optimization to refine
            result = self._optimize_mixed_nash(mixed_strategies, supports)
            
            if result is not None:
                # Verify it's actually an equilibrium
                if self._verify_mixed_nash(result, tolerance=1e-4):
                    return tuple(result)
            
            return None
        except:
            return None
    
    def _optimize_mixed_nash(self, initial_strategies: List[np.ndarray], 
                            supports: Tuple) -> Optional[List[np.ndarray]]:
        """Optimize to find exact probabilities for given support."""
        # This is a simplified version - a full implementation would solve
        # the indifference conditions exactly
        return initial_strategies
    
    def _verify_mixed_nash(self, mixed_strategies: List[np.ndarray], 
                          tolerance: float = 1e-6) -> bool:
        """
        Verify if mixed strategies form a Nash equilibrium.
        
        For each player and each strategy in their support, check if the
        expected payoff is the same (indifference condition).
        """
        for player in range(3):
            # Get strategies in support
            support = np.where(mixed_strategies[player] > tolerance)[0]
            
            if len(support) == 0:
                return False
            
            # Calculate expected payoffs for each pure strategy
            payoffs = []
            other_players = [i for i in range(3) if i != player]
            other_mixed = [mixed_strategies[i] for i in other_players]
            
            for strategy in range(self.n_strategies[player]):
                pure_strat = np.zeros(self.n_strategies[player])
                pure_strat[strategy] = 1.0
                payoff = self.expected_payoff_given_others(pure_strat, other_mixed, player)
                payoffs.append(payoff)
            
            # Check indifference for support
            support_payoffs = [payoffs[s] for s in support]
            if len(support_payoffs) > 1:
                if max(support_payoffs) - min(support_payoffs) > tolerance:
                    return False
            
            # Check that strategies outside support have lower or equal payoff
            non_support = [s for s in range(self.n_strategies[player]) if s not in support]
            max_support_payoff = max(support_payoffs)
            for s in non_support:
                if payoffs[s] > max_support_payoff + tolerance:
                    return False
        
        return True
    
    def display_game(self):
        """Display the game payoff matrices."""
        print("=" * 60)
        print("THREE-PLAYER GAME")
        print("=" * 60)
        print(f"\nNumber of strategies: Player 1: {self.n_strategies[0]}, "
              f"Player 2: {self.n_strategies[1]}, Player 3: {self.n_strategies[2]}")
        
        for player in range(3):
            print(f"\n--- Player {player + 1} Payoffs ---")
            for s3 in range(self.n_strategies[2]):
                print(f"\nWhen Player 3 plays Strategy {s3}:")
                print("          ", end="")
                for s2 in range(self.n_strategies[2]):
                    print(f"P2-S{s2}    ", end="")
                print()
                
                for s1 in range(self.n_strategies[0]):
                    print(f"P1-S{s1}:    ", end="")
                    for s2 in range(self.n_strategies[1]):
                        payoff = self.payoffs[player][s1, s2, s3]
                        print(f"{payoff:6.2f}  ", end="")
                    print()
    
    def display_pure_nash_equilibria(self, equilibria: List[Tuple]):
        """Display pure strategy Nash equilibria."""
        print("\n" + "=" * 60)
        print("PURE STRATEGY NASH EQUILIBRIA")
        print("=" * 60)
        
        if not equilibria:
            print("\nNo pure strategy Nash equilibria found.")
            return
        
        print(f"\nFound {len(equilibria)} pure strategy Nash equilibrium/equilibria:\n")
        
        for i, eq in enumerate(equilibria, 1):
            print(f"Equilibrium {i}:")
            print(f"  Player 1: Strategy {eq[0]}")
            print(f"  Player 2: Strategy {eq[1]}")
            print(f"  Player 3: Strategy {eq[2]}")
            print(f"  Payoffs: (P1: {self.payoffs[0][eq]:.2f}, "
                  f"P2: {self.payoffs[1][eq]:.2f}, "
                  f"P3: {self.payoffs[2][eq]:.2f})")
            print()
    
    def display_mixed_nash_equilibria(self, equilibria: List[Tuple]):
        """Display mixed strategy Nash equilibria."""
        print("\n" + "=" * 60)
        print("MIXED STRATEGY NASH EQUILIBRIA")
        print("=" * 60)
        
        if not equilibria:
            print("\nNo mixed strategy Nash equilibria found.")
            print("(Note: Finding all mixed equilibria in 3-player games is computationally intensive)")
            return
        
        print(f"\nFound {len(equilibria)} mixed strategy equilibrium/equilibria:\n")
        
        for i, eq in enumerate(equilibria, 1):
            print(f"Equilibrium {i}:")
            for player in range(3):
                print(f"  Player {player + 1}:")
                for strategy, prob in enumerate(eq[player]):
                    if prob > 1e-6:
                        print(f"    Strategy {strategy}: {prob:.4f}")
            
            # Calculate expected payoffs
            expected = [self.expected_payoff(eq, p) for p in range(3)]
            print(f"  Expected Payoffs: (P1: {expected[0]:.4f}, "
                  f"P2: {expected[1]:.4f}, P3: {expected[2]:.4f})")
            print()


def example_prisoners_dilemma_3player():
    """
    Example: 3-player Prisoner's Dilemma
    Each player can Cooperate (0) or Defect (1)
    """
    print("\n" + "="*60)
    print("EXAMPLE: 3-PLAYER PRISONER'S DILEMMA")
    print("="*60)
    print("\nEach player can Cooperate (Strategy 0) or Defect (Strategy 1)")
    print("Cooperating gives benefits to others but costs the cooperator.")
    
    # Payoffs when all cooperate: (3, 3, 3)
    # Each defector gains 1, each cooperator loses 1
    
    # Player 1 payoffs
    p1 = np.array([
        [[3, 2], [2, 1]],  # When P1 cooperates
        [[4, 3], [3, 2]]   # When P1 defects
    ])
    
    # Player 2 payoffs
    p2 = np.array([
        [[3, 2], [4, 3]],  # When P2 cooperates
        [[2, 1], [3, 2]]   # When P2 defects
    ])
    
    # Player 3 payoffs
    p3 = np.array([
        [[3, 4], [2, 3]],  # When P3 cooperates
        [[2, 3], [1, 2]]   # When P3 defects
    ])
    
    game = ThreePlayerGame([p1, p2, p3])
    game.display_game()
    
    # Find equilibria
    pure_eq = game.find_pure_nash_equilibria()
    game.display_pure_nash_equilibria(pure_eq)
    
    return game


def example_coordination_game():
    """
    Example: 3-player Coordination Game
    Players benefit from coordinating on the same strategy
    """
    print("\n" + "="*60)
    print("EXAMPLE: 3-PLAYER COORDINATION GAME")
    print("="*60)
    print("\nPlayers benefit when they all choose the same option (0 or 1)")
    
    # High payoff when all coordinate
    # Player 1 payoffs
    p1 = np.array([
        [[5, 0], [0, 0]],  # When P1 chooses 0
        [[0, 0], [0, 5]]   # When P1 chooses 1
    ])
    
    # Player 2 payoffs (symmetric)
    p2 = np.array([
        [[5, 0], [0, 0]],
        [[0, 0], [0, 5]]
    ])
    
    # Player 3 payoffs (symmetric)
    p3 = np.array([
        [[5, 0], [0, 0]],
        [[0, 0], [0, 5]]
    ])
    
    game = ThreePlayerGame([p1, p2, p3])
    game.display_game()
    
    pure_eq = game.find_pure_nash_equilibria()
    game.display_pure_nash_equilibria(pure_eq)
    
    return game


def custom_game_input():
    """Interactive function to input a custom 3-player game."""
    print("\n" + "="*60)
    print("CUSTOM 3-PLAYER GAME INPUT")
    print("="*60)
    
    # Get number of strategies for each player
    print("\nEnter the number of strategies for each player:")
    n1 = int(input("Player 1: "))
    n2 = int(input("Player 2: "))
    n3 = int(input("Player 3: "))
    
    print(f"\nYou will need to enter payoffs for each of the {n1*n2*n3} strategy combinations.")
    print("For each combination, enter payoffs for all 3 players separated by commas.")
    
    # Initialize payoff matrices
    p1 = np.zeros((n1, n2, n3))
    p2 = np.zeros((n1, n2, n3))
    p3 = np.zeros((n1, n2, n3))
    
    # Get payoffs
    for s1 in range(n1):
        for s2 in range(n2):
            for s3 in range(n3):
                print(f"\nPlayer 1: Strategy {s1}, Player 2: Strategy {s2}, Player 3: Strategy {s3}")
                payoffs_str = input("Enter payoffs (P1, P2, P3): ")
                payoffs = [float(x.strip()) for x in payoffs_str.split(',')]
                
                p1[s1, s2, s3] = payoffs[0]
                p2[s1, s2, s3] = payoffs[1]
                p3[s1, s2, s3] = payoffs[2]
    
    game = ThreePlayerGame([p1, p2, p3])
    return game


if __name__ == "__main__":
    print("3-PLAYER GAME THEORY NASH EQUILIBRIUM CALCULATOR")
    print("=" * 60)
    
    # Example 1: Prisoner's Dilemma
    game1 = example_prisoners_dilemma_3player()
    
    # Example 2: Coordination Game
    game2 = example_coordination_game()
    
    print("\n" + "="*60)
    print("READY FOR CUSTOM GAMES")
    print("="*60)
    print("\nTo use this code with your own game:")
    print("1. Create payoff matrices for each player")
    print("2. Initialize: game = ThreePlayerGame([p1_payoffs, p2_payoffs, p3_payoffs])")
    print("3. Find equilibria: pure_eq = game.find_pure_nash_equilibria()")
    print("4. Display: game.display_pure_nash_equilibria(pure_eq)")
    print("\nOr use the custom_game_input() function for interactive input.")