"""
CUSTOM GAME WITH MORE STRATEGIES
Example: Each player has 3 strategies (3x3x3 game)
"""

import numpy as np
from three_player_nash import ThreePlayerGame

# =============================================================================
# FOR 3x3x3 GAME (3 strategies per player)
# =============================================================================

# Player 1's payoffs
# Format: payoffs_p1[P1_strategy, P2_strategy, P3_strategy]
payoffs_p1 = np.array([
    # When Player 1 plays Strategy 0:
    [
        [10, 8, 6],   # P2 plays 0, P3 plays 0/1/2
        [7, 9, 5],    # P2 plays 1, P3 plays 0/1/2
        [4, 6, 8]     # P2 plays 2, P3 plays 0/1/2
    ],
    # When Player 1 plays Strategy 1:
    [
        [9, 7, 5],    # P2 plays 0, P3 plays 0/1/2
        [11, 6, 8],   # P2 plays 1, P3 plays 0/1/2
        [3, 10, 7]    # P2 plays 2, P3 plays 0/1/2
    ],
    # When Player 1 plays Strategy 2:
    [
        [6, 5, 9],    # P2 plays 0, P3 plays 0/1/2
        [8, 10, 4],   # P2 plays 1, P3 plays 0/1/2
        [7, 3, 6]     # P2 plays 2, P3 plays 0/1/2
    ]
])

# Player 2's payoffs
payoffs_p2 = np.array([
    [
        [8, 9, 7],
        [10, 5, 6],
        [4, 8, 9]
    ],
    [
        [7, 6, 10],
        [9, 8, 4],
        [5, 7, 6]
    ],
    [
        [6, 8, 5],
        [7, 9, 10],
        [8, 4, 7]
    ]
])

# Player 3's payoffs
payoffs_p3 = np.array([
    [
        [7, 10, 8],
        [6, 5, 9],
        [8, 7, 4]
    ],
    [
        [9, 6, 7],
        [5, 8, 10],
        [7, 9, 5]
    ],
    [
        [8, 7, 6],
        [10, 4, 8],
        [6, 9, 7]
    ]
])

# Create and solve
game = ThreePlayerGame([payoffs_p1, payoffs_p2, payoffs_p3])

print("\n3x3x3 GAME ANALYSIS")
print("="*60)

game.display_game()
equilibria = game.find_pure_nash_equilibria()
game.display_pure_nash_equilibria(equilibria)

# =============================================================================
# TEMPLATE FOR DIFFERENT SIZED GAMES
# =============================================================================

print("\n\n" + "="*60)
print("HOW TO CREATE GAMES WITH DIFFERENT NUMBERS OF STRATEGIES")
print("="*60)
print("""
For a game where:
- Player 1 has n1 strategies (0, 1, ..., n1-1)
- Player 2 has n2 strategies (0, 1, ..., n2-1)
- Player 3 has n3 strategies (0, 1, ..., n3-1)

Create payoff matrices of shape (n1, n2, n3):

payoffs_p1 = np.zeros((n1, n2, n3))
payoffs_p2 = np.zeros((n1, n2, n3))
payoffs_p3 = np.zeros((n1, n2, n3))

Then fill in values:
payoffs_p1[i, j, k] = payoff for P1 when P1 plays i, P2 plays j, P3 plays k

Example for 2x3x2 game (P1 has 2, P2 has 3, P3 has 2 strategies):

payoffs_p1 = np.array([
    # When P1 plays strategy 0:
    [
        [val1, val2],   # P2 plays 0, P3 plays 0 or 1
        [val3, val4],   # P2 plays 1, P3 plays 0 or 1
        [val5, val6]    # P2 plays 2, P3 plays 0 or 1
    ],
    # When P1 plays strategy 1:
    [
        [val7, val8],   # P2 plays 0, P3 plays 0 or 1
        [val9, val10],  # P2 plays 1, P3 plays 0 or 1
        [val11, val12]  # P2 plays 2, P3 plays 0 or 1
    ]
])
""")