# Physics Modules - Quick Reference

## Overview

Two calibrated physics modules for Strategy Gym 2026:
- **physics_2024.py**: Calibrated from 2024 Bahrain GP real data
- **physics_2026.py**: Extrapolated to 2026 regulations (3x electric power)

## Key Changes: 2024 → 2026

| Parameter | 2024 | 2026 | Change |
|-----------|------|------|--------|
| MGU-K Power | 120kW | 350kW | 2.92x (3x) |
| Battery Capacity | 4MJ | 4MJ | Unchanged |
| Energy Bonus | 0.012s/% | 0.036s/% | 3x stronger |
| Battery Drain | 0.02%/% | 0.06%/% | 3x faster |
| ICE/Electric Split | 80/20 | 50/50 | Balanced |

**Result**: More power available, but depletes 3x faster. Energy management becomes race-defining.

## Strategic Control Variables (6)

Each agent controls 6 variables per lap (all 0-100%):

```python
@dataclass
class AgentDecision:
    energy_deployment: float    # How much battery to use
    tire_management: float      # 0=conserve, 100=push hard
    fuel_strategy: float        # 0=lean, 50=balanced, 100=rich
    ers_mode: float            # 0=harvest, 50=auto, 100=deploy
    overtake_aggression: float  # Risk vs reward in attacks
    defense_intensity: float    # How hard to defend position
```

## Race State

```python
@dataclass
class RaceState:
    lap: int                    # Current lap (1-57)
    battery_soc: float         # Battery state (0-100%)
    position: int              # Race position
    tire_age: int              # Laps on current tires
    tire_life: float           # Tire condition (0-100%)
    fuel_remaining: float      # Fuel in kg
    boost_used: int            # Manual boosts used (0-2)
```

## Core Functions

### Load Baseline Data
```python
from sim.physics_2026 import load_baseline

baseline = load_baseline()
# Returns: 2024 Bahrain GP calibrated parameters
```

### Calculate Lap Time
```python
from sim.physics_2026 import calculate_lap_time

lap_time = calculate_lap_time(
    decision,           # AgentDecision
    state,             # RaceState
    baseline,          # From load_baseline()
    tire_compound='HARD',
    use_2026_rules=True  # False for 2024 physics
)
# Returns: lap time in seconds
```

### Update Battery
```python
from sim.physics_2026 import update_battery

new_soc = update_battery(
    decision,
    state,
    baseline,
    use_2026_rules=True  # False for 2024 physics
)
# Returns: new battery SOC (0-100%)
```

### Update Tire Condition
```python
from sim.physics_2026 import update_tire_condition

new_tire_life = update_tire_condition(
    decision,
    state,
    baseline,
    tire_compound='HARD'
)
# Returns: new tire life (0-100%)
```

### Update Fuel
```python
from sim.physics_2026 import update_fuel

new_fuel = update_fuel(decision, state, baseline)
# Returns: remaining fuel in kg
```

### Calculate Overtake Probability
```python
from sim.physics_2026 import calculate_overtake_probability

prob = calculate_overtake_probability(
    attacker_decision,
    defender_decision,
    gap=0.4,  # Time gap in seconds
    baseline
)
# Returns: probability (0.0-1.0)
```

## Physics Effects

### Lap Time Formula (2026)
```
base_time = tire_compound['base_time']  # 96.66s for HARD

+ tire_degradation
+ fuel_weight_penalty
+ fuel_strategy_effect
+ tire_push_penalty
+ low_battery_penalty
- energy_deployment_bonus (3x in 2026)
```

### Battery Dynamics (2026)
```
drain = energy_deployment * 0.06  # 3x faster than 2024
charge = (100 - ers_mode) * 0.015
new_soc = clamp(current_soc - drain + charge, 0, 100)
```

### Tire Degradation
```
base_wear = 1.5%

multiplier:
  tire_management > 70: 1.5x (pushing hard)
  tire_management < 40: 0.7x (conserving)
  else: 1.0x
```

### Fuel Consumption
```
fuel_strategy < 40:  1.5 kg/lap (lean)
fuel_strategy < 60:  1.8 kg/lap (balanced)
fuel_strategy >= 60: 2.2 kg/lap (rich)
```

## Example Usage

```python
from sim.physics_2026 import (
    AgentDecision,
    RaceState,
    load_baseline,
    calculate_lap_time,
    update_battery
)

# Load calibrated physics
baseline = load_baseline()

# Define strategy
decision = AgentDecision(
    energy_deployment=75.0,  # 75% battery use
    tire_management=60.0,    # Moderate push
    fuel_strategy=50.0,      # Balanced
    ers_mode=70.0,          # Mostly deploy
    overtake_aggression=80.0,
    defense_intensity=70.0
)

# Current state
state = RaceState(
    lap=10,
    battery_soc=85.0,
    position=3,
    tire_age=10,
    tire_life=85.0,
    fuel_remaining=80.0,
    boost_used=0
)

# Simulate one lap
lap_time = calculate_lap_time(decision, state, baseline)
new_battery = update_battery(decision, state, baseline)

print(f"Lap time: {lap_time:.3f}s")
print(f"Battery: {state.battery_soc}% → {new_battery:.1f}%")
```

## Strategic Insights from Physics

### Energy Management (2026)
- 100% deployment = 3.6s/lap faster
- But drains battery at 6%/lap
- Creates critical trade-off: speed vs sustainability

### Tire Strategy
- Pushing hard (>70% management) = 1.5x wear
- Conserving (<40% management) = 0.7x wear
- Balance needed for multi-stint races

### Fuel Strategy
- Lean: Saves fuel but +0.3s/lap penalty
- Rich: Burns fuel but -0.2s/lap bonus
- Critical in close battles

### Overtaking
- Gap < 0.3s: 60% base chance
- Gap > 1.0s: 5% base chance
- Aggression/defense modifiers: ±30%

## Performance

All functions optimized for speed:
- Pure Python calculations
- NumPy-compatible (can vectorize)
- No I/O in hot path (baseline loaded once)
- Target: 1000+ race simulations in <5 seconds

## Validation

Run test suite:
```bash
python test_physics.py
```

Expected output:
- ✓ 2024 physics working
- ✓ 2026 showing 3x electric power effect
- ✓ All 6 variables impact lap times
- ✓ Battery drains 3-4x faster in 2026

## Data Sources

Calibrated from:
- **data/baseline_2024.json**: Real 2024 Bahrain GP physics
- **data/learned_strategies.json**: Verstappen/Hamilton/Alonso profiles

Parameters include:
- SOFT tire: 98.4s base, 0.01 deg_rate
- HARD tire: 96.66s base, 0.022 deg_rate
- Fuel effect: 0.026s per kg
- ERS deployment: 4MJ max per lap

## Files

- **/Users/prajit/Desktop/projects/Gand/sim/physics_2024.py** - 2024 calibrated physics
- **/Users/prajit/Desktop/projects/Gand/sim/physics_2026.py** - 2026 extrapolated physics
- **/Users/prajit/Desktop/projects/Gand/test_physics.py** - Comprehensive test suite
- **/Users/prajit/Desktop/projects/Gand/example_physics_usage.py** - Usage examples
- **/Users/prajit/Desktop/projects/Gand/data/baseline_2024.json** - Calibration data
- **/Users/prajit/Desktop/projects/Gand/data/learned_strategies.json** - Real driver profiles

## Integration with Simulation Engine

These physics modules can be integrated with the existing simulation engine:

```python
# In sim/engine.py, replace simplified physics with realistic physics
from sim.physics_2026 import calculate_lap_time, update_battery, AgentDecision

def simulate_lap(state, decision_dict, scenario):
    # Convert dict to AgentDecision
    decision = AgentDecision(
        energy_deployment=decision_dict.get('deploy_straight', 0),
        tire_management=decision_dict.get('deploy_corner', 0),
        fuel_strategy=50.0,  # From agent strategy
        ers_mode=decision_dict.get('harvest', 0),
        overtake_aggression=50.0,
        defense_intensity=50.0
    )

    # Use realistic physics
    lap_time = calculate_lap_time(decision, state, baseline)
    new_soc = update_battery(decision, state, baseline)

    # ... rest of simulation
```

## Next Steps

To integrate with Strategy Gym 2026:
1. Update agent strategies to use 6 control variables
2. Modify sim/engine.py to use realistic physics
3. Update scenarios to include tire compound selection
4. Add tire pit stop logic
5. Integrate overtake probability into race simulation

---

Generated: 2025-10-18
Based on: 2024 Bahrain GP data
2026 Regulations: FIA Technical Regulations 2026 (MGU-K power increase)
