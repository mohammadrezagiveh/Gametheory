"""
Three-Player Escalation Game (2x4x2)
Nash Equilibrium Calculator

Game Structure:
- Player 1: 2 strategies (Escalate, Deescalate)
- Player 2: 4 strategies (4 different combinations)
- Player 3: 2 strategies (Escalate, Deescalate)
"""

import numpy as np
from three_player_nash import ThreePlayerGame


def input_escalation_game():
    """
    Input game payoffs in the format shown in the PDF.
    
    The game has:
    - Player 1: 2 strategies (0=Escalate, 1=Deescalate)
    - Player 2: 4 strategies (0-3 for different combinations)
    - Player 3: 2 strategies (0=Escalate, 1=Deescalate)
    """
    print("="*80)
    print("THREE-PLAYER ESCALATION GAME - NASH EQUILIBRIUM CALCULATOR")
    print("="*80)
    print("\nGame Structure:")
    print("  Player 1: Strategy 0 = Escalate, Strategy 1 = Deescalate")
    print("  Player 2: 4 strategies (0, 1, 2, 3)")
    print("  Player 3: Strategy 0 = Escalate, Strategy 1 = Deescalate")
    print("\n" + "="*80)
    
    # Initialize payoff matrices: shape is (P1_strategies, P2_strategies, P3_strategies)
    payoffs_p1 = np.zeros((2, 4, 2))
    payoffs_p2 = np.zeros((2, 4, 2))
    payoffs_p3 = np.zeros((2, 4, 2))
    
    # Define strategy labels for clarity
    p1_labels = ["Escalate", "Deescalate"]
    p3_labels = ["Escalate", "Deescalate"]
    
    print("\nYou will enter payoffs for two tables:")
    print("  Table 1: When Player 3 Escalates")
    print("  Table 2: When Player 3 Deescalates")
    print("\nFor each cell, enter payoffs as: P1_payoff, P2_payoff, P3_payoff")
    print("="*80)
    
    # Input for each Player 3 strategy
    for p3_strat in range(2):
        print(f"\n{'='*80}")
        print(f"TABLE {p3_strat + 1}: WHEN PLAYER 3 PLAYS '{p3_labels[p3_strat].upper()}'")
        print("="*80)
        
        # Input for each combination of Player 1 and Player 2
        for p1_strat in range(2):
            print(f"\n--- When Player 1 plays '{p1_labels[p1_strat]}' ---")
            
            for p2_strat in range(4):
                print(f"\n  Player 2 Strategy {p2_strat}:")
                
                while True:
                    try:
                        payoffs_str = input(f"    Enter payoffs (P1, P2, P3): ")
                        payoffs = [float(x.strip()) for x in payoffs_str.split(',')]
                        
                        if len(payoffs) != 3:
                            print("    Error: Please enter exactly 3 payoffs separated by commas")
                            continue
                        
                        payoffs_p1[p1_strat, p2_strat, p3_strat] = payoffs[0]
                        payoffs_p2[p1_strat, p2_strat, p3_strat] = payoffs[1]
                        payoffs_p3[p1_strat, p2_strat, p3_strat] = payoffs[2]
                        break
                    except ValueError:
                        print("    Error: Please enter valid numbers")
    
    return payoffs_p1, payoffs_p2, payoffs_p3


def input_from_pdf_format():
    """
    Input game using the exact format from the PDF.
    Organized as two tables (one for each Player 3 strategy).
    """
    print("="*80)
    print("ESCALATION GAME - PDF FORMAT INPUT")
    print("="*80)
    print("\nEnter values from the two tables in your PDF.")
    print("Format: P1_payoff, P2_payoff, P3_payoff")
    print("="*80)
    
    # Initialize
    payoffs_p1 = np.zeros((2, 4, 2))
    payoffs_p2 = np.zeros((2, 4, 2))
    payoffs_p3 = np.zeros((2, 4, 2))
    
    p2_strategy_names = [
        "Escalate against P3 and Escalate against P1",
        "Escalate against P3 and Deescalate against P1",
        "Deescalate against P3 and Escalate against P1",
        "Deescalate against P3 and Deescalate against P1"
    ]
    
    # Table 1: Player 3 Escalates
    print("\n" + "="*80)
    print("TABLE 1: PLAYER 3 ESCALATES")
    print("="*80)
    
    for p1_idx, p1_name in enumerate(["Player 1 Escalates", "Player 1 Deescalates"]):
        print(f"\n{p1_name}:")
        for p2_idx in range(4):
            print(f"  {p2_strategy_names[p2_idx]}:")
            payoffs_str = input(f"    Payoffs: ")
            payoffs = [float(x.strip()) for x in payoffs_str.split(',')]
            payoffs_p1[p1_idx, p2_idx, 0] = payoffs[0]
            payoffs_p2[p1_idx, p2_idx, 0] = payoffs[1]
            payoffs_p3[p1_idx, p2_idx, 0] = payoffs[2]
    
    # Table 2: Player 3 Deescalates
    print("\n" + "="*80)
    print("TABLE 2: PLAYER 3 DEESCALATES")
    print("="*80)
    
    for p1_idx, p1_name in enumerate(["Player 1 Escalates", "Player 1 Deescalates"]):
        print(f"\n{p1_name}:")
        for p2_idx in range(4):
            print(f"  {p2_strategy_names[p2_idx]}:")
            payoffs_str = input(f"    Payoffs: ")
            payoffs = [float(x.strip()) for x in payoffs_str.split(',')]
            payoffs_p1[p1_idx, p2_idx, 1] = payoffs[0]
            payoffs_p2[p1_idx, p2_idx, 1] = payoffs[1]
            payoffs_p3[p1_idx, p2_idx, 1] = payoffs[2]
    
    return payoffs_p1, payoffs_p2, payoffs_p3


def use_pdf_example():
    """
    Use the exact values from the PDF example.
    """
    print("="*80)
    print("USING VALUES FROM PDF EXAMPLE")
    print("="*80)
    
    # Initialize matrices (shape: P1_strategies=2, P2_strategies=4, P3_strategies=2)
    payoffs_p1 = np.zeros((2, 4, 2))
    payoffs_p2 = np.zeros((2, 4, 2))
    payoffs_p3 = np.zeros((2, 4, 2))
    
    # TABLE 1: Player 3 Escalates (p3_strategy = 0)
    # Player 1 Escalates (p1_strategy = 0)
    payoffs_p1[0, 0, 0], payoffs_p2[0, 0, 0], payoffs_p3[0, 0, 0] = 1, 2, 6
    payoffs_p1[0, 1, 0], payoffs_p2[0, 1, 0], payoffs_p3[0, 1, 0] = 4, 1, 3
    payoffs_p1[0, 2, 0], payoffs_p2[0, 2, 0], payoffs_p3[0, 2, 0] = -1, 1.5, 7
    payoffs_p1[0, 3, 0], payoffs_p2[0, 3, 0], payoffs_p3[0, 3, 0] = 1.5, 0, 10
    
    # Player 1 Deescalates (p1_strategy = 1)
    payoffs_p1[1, 0, 0], payoffs_p2[1, 0, 0], payoffs_p3[1, 0, 0] = 0, 7, 4
    payoffs_p1[1, 1, 0], payoffs_p2[1, 1, 0], payoffs_p3[1, 1, 0] = 5, 5, 3.5
    payoffs_p1[1, 2, 0], payoffs_p2[1, 2, 0], payoffs_p3[1, 2, 0] = -2, 2.5, 6
    payoffs_p1[1, 3, 0], payoffs_p2[1, 3, 0], payoffs_p3[1, 3, 0] = 3.5, 4, 8
    
    # TABLE 2: Player 3 Deescalates (p3_strategy = 1)
    # Player 1 Escalates (p1_strategy = 0)
    payoffs_p1[0, 0, 1], payoffs_p2[0, 0, 1], payoffs_p3[0, 0, 1] = 1.5, 8, 3.5
    payoffs_p1[0, 1, 1], payoffs_p2[0, 1, 1], payoffs_p3[0, 1, 1] = 10, 5, 2
    payoffs_p1[0, 2, 1], payoffs_p2[0, 2, 1], payoffs_p3[0, 2, 1] = 1, 5, 5
    payoffs_p1[0, 3, 1], payoffs_p2[0, 3, 1], payoffs_p3[0, 3, 1] = 8, 4, 5
    
    # Player 1 Deescalates (p1_strategy = 1)
    payoffs_p1[1, 0, 1], payoffs_p2[1, 0, 1], payoffs_p3[1, 0, 1] = 1, 10, 1
    payoffs_p1[1, 1, 1], payoffs_p2[1, 1, 1], payoffs_p3[1, 1, 1] = 7, 5, 0
    payoffs_p1[1, 2, 1], payoffs_p2[1, 2, 1], payoffs_p3[1, 2, 1] = 0, 6, 3
    payoffs_p1[1, 3, 1], payoffs_p2[1, 3, 1], payoffs_p3[1, 3, 1] = 6, 5, 4
    
    return payoffs_p1, payoffs_p2, payoffs_p3


def display_game_tables(payoffs_p1, payoffs_p2, payoffs_p3):
    """Display the game in the PDF table format."""
    print("\n" + "="*80)
    print("GAME PAYOFF TABLES")
    print("="*80)
    
    p1_labels = ["Escalate", "Deescalate"]
    p3_labels = ["Escalate", "Deescalate"]
    p2_labels = [
        "E-P3 & E-P1",
        "E-P3 & D-P1",
        "D-P3 & E-P1",
        "D-P3 & D-P1"
    ]
    
    for p3_idx in range(2):
        print(f"\n{'='*80}")
        print(f"PLAYER 3: {p3_labels[p3_idx].upper()}")
        print("="*80)
        
        # Header
        print(f"\n{'Player 1':<15}", end="")
        for p2_idx in range(4):
            print(f"{p2_labels[p2_idx]:<18}", end="")
        print()
        print("-" * 80)
        
        # Rows
        for p1_idx in range(2):
            print(f"{p1_labels[p1_idx]:<15}", end="")
            for p2_idx in range(4):
                p1_pay = payoffs_p1[p1_idx, p2_idx, p3_idx]
                p2_pay = payoffs_p2[p1_idx, p2_idx, p3_idx]
                p3_pay = payoffs_p3[p1_idx, p2_idx, p3_idx]
                print(f"({p1_pay:>4.1f},{p2_pay:>4.1f},{p3_pay:>4.1f})", end="  ")
            print()


def analyze_game(payoffs_p1, payoffs_p2, payoffs_p3):
    """Analyze the game and find Nash equilibria."""
    
    # Display the game
    display_game_tables(payoffs_p1, payoffs_p2, payoffs_p3)
    
    # Create game object
    game = ThreePlayerGame([payoffs_p1, payoffs_p2, payoffs_p3])
    
    # Find pure strategy Nash equilibria
    print("\n" + "="*80)
    print("SEARCHING FOR NASH EQUILIBRIA...")
    print("="*80)
    
    equilibria = game.find_pure_nash_equilibria()
    
    # Display results
    print("\n" + "="*80)
    print("PURE STRATEGY NASH EQUILIBRIA")
    print("="*80)
    
    if not equilibria:
        print("\nNo pure strategy Nash equilibria found.")
    else:
        print(f"\nFound {len(equilibria)} pure strategy Nash equilibrium/equilibria:\n")
        
        p1_labels = ["Escalate", "Deescalate"]
        p3_labels = ["Escalate", "Deescalate"]
        p2_labels = [
            "Escalate against P3 and Escalate against P1",
            "Escalate against P3 and Deescalate against P1",
            "Deescalate against P3 and Escalate against P1",
            "Deescalate against P3 and Deescalate against P1"
        ]
        
        for i, eq in enumerate(equilibria, 1):
            print(f"Equilibrium {i}:")
            print(f"  Player 1: {p1_labels[eq[0]]} (Strategy {eq[0]})")
            print(f"  Player 2: {p2_labels[eq[1]]} (Strategy {eq[1]})")
            print(f"  Player 3: {p3_labels[eq[2]]} (Strategy {eq[2]})")
            print(f"  Payoffs: (P1: {payoffs_p1[eq]:.2f}, "
                  f"P2: {payoffs_p2[eq]:.2f}, "
                  f"P3: {payoffs_p3[eq]:.2f})")
            print()
    
    return game, equilibria


def main():
    """Main function to run the escalation game analyzer."""
    
    print("\n" + "="*80)
    print("THREE-PLAYER ESCALATION GAME ANALYZER")
    print("="*80)
    print("\nChoose an option:")
    print("  1. Use PDF example values")
    print("  2. Enter custom values (simple format)")
    print("  3. Enter custom values (PDF table format)")
    
    choice = input("\nYour choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        payoffs_p1, payoffs_p2, payoffs_p3 = use_pdf_example()
    elif choice == "2":
        payoffs_p1, payoffs_p2, payoffs_p3 = input_escalation_game()
    elif choice == "3":
        payoffs_p1, payoffs_p2, payoffs_p3 = input_from_pdf_format()
    else:
        print("Invalid choice. Using PDF example.")
        payoffs_p1, payoffs_p2, payoffs_p3 = use_pdf_example()
    
    # Analyze the game
    game, equilibria = analyze_game(payoffs_p1, payoffs_p2, payoffs_p3)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()