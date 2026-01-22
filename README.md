# Three-Player Geopolitical Game: Nash Equilibrium Calculator

An integrated game theory analysis system for modeling strategic interactions between three players: **Opposition**, **Regime**, and **Israel**.

## Overview

This system combines three distinct payoff calculation models into a unified Nash equilibrium calculator:

| Player | Model | Key Parameters |
|--------|-------|----------------|
| **Opposition** | Stage I additive + Stage II multiplicative degradation | BI, IS, MD, LoC, PR, CL, MI |
| **Regime** | Survival-based with additive bonuses | S, M, R, C, V |
| **Israel** | Two-bank additive system | G1, G2, G3, G4, G5 |

## Game Structure

- **Player 1 (Opposition)**: 2 strategies
  - `0`: Escalate against the regime
  - `1`: Deescalate (pursue civil means, reform over revolution)

- **Player 2 (Regime)**: 4 strategies (combinations)
  - `0`: Escalate vs Israel & Escalate vs Opposition
  - `1`: Escalate vs Israel & Deescalate vs Opposition
  - `2`: Deescalate vs Israel & Escalate vs Opposition
  - `3`: Deescalate vs Israel & Deescalate vs Opposition

- **Player 3 (Israel)**: 2 strategies
  - `0`: Escalate (attack infrastructure, destabilize)
  - `1`: Deescalate

## Files

| File | Description |
|------|-------------|
| `run_game.py` | Main entry point - runs complete analysis |
| `integrated_payoffs.py` | Payoff calculation for all three players |
| `three_player_nash.py` | Nash equilibrium finding algorithms |
| `game_probabilities.csv` | Sample CSV with probability parameters |

## Usage

### Run with PDF Example Values
```bash
python run_game.py --pdf
```

### Run with Custom Probabilities (from CSV)
```bash
python run_game.py game_probabilities.csv
```

### Generate Sample CSV Template
```bash
python run_game.py --sample
```

## CSV Format

The CSV file defines probability parameters for each of the 16 strategy combinations:

```csv
p1_strat,p2_strat,p3_strat,opp_BI,opp_IS,...,isr_G4,isr_G5
0,0,0,0.30,0.40,...,0.55,0.60
...
```

### Opposition Parameters (7 probabilities)
| Parameter | Description | Stage |
|-----------|-------------|-------|
| `opp_BI` | Border Integrity maintained | II (degradation) |
| `opp_IS` | Infrastructure Survival | II (degradation) |
| `opp_MD` | Maintaining Deterrence | II (degradation) |
| `opp_LoC` | Lack of Casualty | II (degradation) |
| `opp_PR` | Political Reform achieved | I (additive) |
| `opp_CL` | Civil Liberties achieved | I (additive) |
| `opp_MI` | Material Improvement | I (additive) |

**Formula**: Build bank additively (30×PR + 30×CL + 40×MI), then apply multiplicative degradation for each failed Stage II goal.

### Regime Parameters (5 probabilities)
| Parameter | Description |
|-----------|-------------|
| `reg_S` | Survival |
| `reg_M` | Maintaining previous policies |
| `reg_R` | Regional dominance |
| `reg_C` | Credible internal power |
| `reg_V` | Not subjected to violence |

**Formula**: If S=True: 50 + 20×M + 20×R + 10×C. If S=False: 20×V only.

### Israel Parameters (5 probabilities)
| Parameter | Description | Bank |
|-----------|-------------|------|
| `isr_G1` | Goal 1 | Bank 1 (30% weight) |
| `isr_G2` | Goal 2 | Bank 1 (20% weight) |
| `isr_G3` | Goal 3 | Bank 1 (50% weight) |
| `isr_G4` | Goal 4 | Bank 2 (30% weight) |
| `isr_G5` | Goal 5 | Bank 2 (70% weight) |

**Formula**: Bank1 = 100×(0.3×G1 + 0.2×G2 + 0.5×G3), Bank2 = 100×(0.3×G4 + 0.7×G5), Final = 0.6×Bank1 + 0.4×Bank2

## Output

The system provides:

1. **Payoff Tables**: Clear display of all 16 strategy combinations with (Opposition, Regime, Israel) payoffs

2. **Nash Equilibria**: Pure strategy equilibria where no player can improve by unilateral deviation

3. **Best Response Analysis**: Shows optimal responses for each player given all possible opponent strategy combinations

## Example Output

```
EQUILIBRIUM 1
──────────────────────────────────────────────────────────────────────
  Player 1 (Opposition): Deescalate (Strategy 1)
  Player 2 (Regime):     Escalate vs Israel & Escalate vs Opposition
  Player 3 (Israel):     Escalate (Strategy 0)

  Payoffs:
    Opposition: 2.00
    Regime:     7.00
    Israel:     4.00
```

## Extending the Model

To modify payoff weights, edit the constants in `integrated_payoffs.py`:

```python
# Opposition Stage I weights
OPP_W_PR = 30.0  # Political Reform contribution
OPP_W_CL = 30.0  # Civil Liberties contribution
OPP_W_MI = 40.0  # Material Improvement contribution

# Opposition Stage II degradation multipliers
OPP_MULT_BI_NO = 0.30  # Multiplier when Border Integrity fails
...
```

## Dependencies

- Python 3.7+
- NumPy

Install with:
```bash
pip install numpy
```
