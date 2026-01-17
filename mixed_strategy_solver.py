import numpy as np

def get_payoff_matrix():
    """Get payoff values from user input."""
    print("=" * 50)
    print("2x2 Game - Mixed Strategy Nash Equilibrium Solver")
    print("=" * 50)
    print("\nGame structure:")
    print("                Player 2")
    print("              Left    Right")
    print("Player 1  Top  (a,b)   (c,d)")
    print("        Bottom (e,f)   (g,h)")
    print("\nEnter payoffs as: Player1_payoff, Player2_payoff")
    print("-" * 50)
    
    # Get payoffs for each cell
    print("\nTop-Left cell (Player 1 plays Top, Player 2 plays Left):")
    tl = input("  Enter payoffs (e.g., 3,2): ").split(",")
    a11, b11 = float(tl[0].strip()), float(tl[1].strip())
    
    print("\nTop-Right cell (Player 1 plays Top, Player 2 plays Right):")
    tr = input("  Enter payoffs (e.g., 0,0): ").split(",")
    a12, b12 = float(tr[0].strip()), float(tr[1].strip())
    
    print("\nBottom-Left cell (Player 1 plays Bottom, Player 2 plays Left):")
    bl = input("  Enter payoffs (e.g., 0,0): ").split(",")
    a21, b21 = float(bl[0].strip()), float(bl[1].strip())
    
    print("\nBottom-Right cell (Player 1 plays Bottom, Player 2 plays Right):")
    br = input("  Enter payoffs (e.g., 2,3): ").split(",")
    a22, b22 = float(br[0].strip()), float(br[1].strip())
    
    # Payoff matrices
    P1 = np.array([[a11, a12], [a21, a22]])  # Player 1's payoffs
    P2 = np.array([[b11, b12], [b21, b22]])  # Player 2's payoffs
    
    return P1, P2

def find_pure_strategy_ne(P1, P2):
    """Find all pure strategy Nash Equilibria."""
    pure_ne = []
    strategies = [(0, 0, "Top", "Left"), (0, 1, "Top", "Right"),
                  (1, 0, "Bottom", "Left"), (1, 1, "Bottom", "Right")]
    
    for i, j, s1, s2 in strategies:
        # Check if (i,j) is a Nash Equilibrium
        # Player 1 has no profitable deviation (check column j)
        p1_best = P1[i, j] >= P1[1-i, j]
        # Player 2 has no profitable deviation (check row i)
        p2_best = P2[i, j] >= P2[i, 1-j]
        
        if p1_best and p2_best:
            pure_ne.append((i, j, s1, s2, P1[i,j], P2[i,j]))
    
    return pure_ne

def find_mixed_strategy_ne(P1, P2):
    """
    Find mixed strategy Nash Equilibrium.
    
    p = probability Player 1 plays Top
    q = probability Player 2 plays Left
    
    Player 2 makes Player 1 indifferent:
    q*P1[0,0] + (1-q)*P1[0,1] = q*P1[1,0] + (1-q)*P1[1,1]
    
    Player 1 makes Player 2 indifferent:
    p*P2[0,0] + (1-p)*P2[1,0] = p*P2[0,1] + (1-p)*P2[1,1]
    """
    # Solve for q (Player 2's mixing probability)
    # q = (P1[1,1] - P1[0,1]) / ((P1[0,0] - P1[0,1]) - (P1[1,0] - P1[1,1]))
    denom_q = (P1[0,0] - P1[0,1]) - (P1[1,0] - P1[1,1])
    numer_q = P1[1,1] - P1[0,1]
    
    # Solve for p (Player 1's mixing probability)
    # p = (P2[1,1] - P2[1,0]) / ((P2[0,0] - P2[1,0]) - (P2[0,1] - P2[1,1]))
    denom_p = (P2[0,0] - P2[1,0]) - (P2[0,1] - P2[1,1])
    numer_p = P2[1,1] - P2[1,0]
    
    result = {"exists": False, "p": None, "q": None, "reason": ""}
    
    # Check if mixed strategy NE exists
    if abs(denom_q) < 1e-10:
        result["reason"] = "Player 1 has a dominant strategy (no mixing needed)"
        return result
    
    if abs(denom_p) < 1e-10:
        result["reason"] = "Player 2 has a dominant strategy (no mixing needed)"
        return result
    
    q = numer_q / denom_q
    p = numer_p / denom_p
    
    # Check if probabilities are valid (between 0 and 1)
    if not (0 < p < 1) or not (0 < q < 1):
        result["reason"] = f"Mixed strategy probabilities outside (0,1): p={p:.4f}, q={q:.4f}"
        return result
    
    # Calculate expected payoffs
    exp_p1 = p * (q * P1[0,0] + (1-q) * P1[0,1]) + (1-p) * (q * P1[1,0] + (1-q) * P1[1,1])
    exp_p2 = p * (q * P2[0,0] + (1-q) * P2[0,1]) + (1-p) * (q * P2[1,0] + (1-q) * P2[1,1])
    
    result["exists"] = True
    result["p"] = p
    result["q"] = q
    result["exp_payoff_p1"] = exp_p1
    result["exp_payoff_p2"] = exp_p2
    
    return result

def display_results(P1, P2, pure_ne, mixed_ne):
    """Display the results nicely."""
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    # Display the game matrix
    print("\nPayoff Matrix (Player 1, Player 2):")
    print("-" * 35)
    print(f"              {'Left':^12} {'Right':^12}")
    print(f"    Top       ({P1[0,0]:>4.1f},{P2[0,0]:>4.1f})   ({P1[0,1]:>4.1f},{P2[0,1]:>4.1f})")
    print(f"    Bottom    ({P1[1,0]:>4.1f},{P2[1,0]:>4.1f})   ({P1[1,1]:>4.1f},{P2[1,1]:>4.1f})")
    
    # Pure Strategy NE
    print("\n" + "-" * 50)
    print("PURE STRATEGY NASH EQUILIBRIA:")
    if pure_ne:
        for i, j, s1, s2, pay1, pay2 in pure_ne:
            print(f"  • ({s1}, {s2}) with payoffs ({pay1:.2f}, {pay2:.2f})")
    else:
        print("  None found")
    
    # Mixed Strategy NE
    print("\n" + "-" * 50)
    print("MIXED STRATEGY NASH EQUILIBRIUM:")
    if mixed_ne["exists"]:
        p, q = mixed_ne["p"], mixed_ne["q"]
        print(f"\n  Player 1's strategy:")
        print(f"    P(Top) = {p:.4f}")
        print(f"    P(Bottom) = {1-p:.4f}")
        print(f"\n  Player 2's strategy:")
        print(f"    P(Left) = {q:.4f}")
        print(f"    P(Right) = {1-q:.4f}")
        print(f"\n  Expected Payoffs at equilibrium:")
        print(f"    Player 1: {mixed_ne['exp_payoff_p1']:.4f}")
        print(f"    Player 2: {mixed_ne['exp_payoff_p2']:.4f}")
    else:
        print(f"  No interior mixed strategy NE: {mixed_ne['reason']}")
    
    print("\n" + "=" * 50)

def solve_example(P1, P2, name=""):
    """Solve and display for a given payoff matrix."""
    if name:
        print(f"\n{'='*50}")
        print(f"Example: {name}")
        print(f"{'='*50}")
    pure_ne = find_pure_strategy_ne(P1, P2)
    mixed_ne = find_mixed_strategy_ne(P1, P2)
    display_results(P1, P2, pure_ne, mixed_ne)

def main():
    print("\nChoose an option:")
    print("1. Enter custom payoffs")
    print("2. Run classic examples")
    
    choice = input("\nYour choice (1 or 2): ").strip()
    
    if choice == "1":
        P1, P2 = get_payoff_matrix()
        pure_ne = find_pure_strategy_ne(P1, P2)
        mixed_ne = find_mixed_strategy_ne(P1, P2)
        display_results(P1, P2, pure_ne, mixed_ne)
    else:
        # Matching Pennies
        P1 = np.array([[1, -1], [-1, 1]])
        P2 = np.array([[-1, 1], [1, -1]])
        solve_example(P1, P2, "Matching Pennies")
        
        # Battle of the Sexes
        P1 = np.array([[3, 0], [0, 2]])
        P2 = np.array([[2, 0], [0, 3]])
        solve_example(P1, P2, "Battle of the Sexes")
        
        # Prisoner's Dilemma
        P1 = np.array([[-1, -3], [0, -2]])
        P2 = np.array([[-1, 0], [-3, -2]])
        solve_example(P1, P2, "Prisoner's Dilemma")
        
        # Hawk-Dove Game
        P1 = np.array([[-2, 4], [0, 2]])
        P2 = np.array([[-2, 0], [4, 2]])
        solve_example(P1, P2, "Hawk-Dove (Chicken)")

if __name__ == "__main__":
    main()