# Physics Modules - Quick Start Guide

## Installation (Already Done)
✓ Modules located in `/Users/prajit/Desktop/projects/Gand/sim/`
✓ No additional dependencies required
✓ Uses existing baseline data

## 5-Minute Quick Start

### 1. Import the modules
```python
from sim.physics_2026 import (
    AgentDecision,
    RaceState,
    load_baseline,
    calculate_lap_time,
    update_battery
)
```

### 2. Load calibrated baseline
```python
baseline = load_baseline()
```

### 3. Create a decision (6 strategic variables)
```python
decision = AgentDecision(
    energy_deployment=75.0,  # 75% battery usage
    tire_management=60.0,    # Moderate tire push
    fuel_strategy=50.0,      # Balanced mixture
    ers_mode=70.0,          # Mostly deploy
    overtake_aggression=80.0,
    defense_intensity=70.0
)
```

### 4. Create a race state
```python
state = RaceState(
    lap=10,
    battery_soc=85.0,
    position=3,
    tire_age=10,
    tire_life=85.0,
    fuel_remaining=80.0,
    boost_used=0
)
```

### 5. Calculate lap time
```python
lap_time = calculate_lap_time(decision, state, baseline)
print(f"Lap time: {lap_time:.3f}s")
```

### 6. Update battery
```python
new_battery = update_battery(decision, state, baseline)
print(f"Battery: {state.battery_soc}% → {new_battery:.1f}%")
```

## Test & Validate

### Run full test suite
```bash
python test_physics.py
```

### Run usage examples
```bash
python example_physics_usage.py
```

### Run integration tests
```bash
python test_integration.py
```

## Key Differences: 2024 vs 2026

```python
# 2024 physics (120kW MGU-K)
lap_2024 = calculate_lap_time(decision, state, baseline, use_2026_rules=False)
bat_2024 = update_battery(decision, state, baseline, use_2026_rules=False)

# 2026 physics (350kW MGU-K - 3x power)
lap_2026 = calculate_lap_time(decision, state, baseline, use_2026_rules=True)
bat_2026 = update_battery(decision, state, baseline, use_2026_rules=True)

# Results:
# lap_2026 is ~2-3s faster (more electric power)
# bat_2026 drains ~3x faster (same battery capacity)
```

## Strategic Variables Explained

| Variable | Range | Effect |
|----------|-------|--------|
| **energy_deployment** | 0-100 | Higher = faster lap, more battery drain |
| **tire_management** | 0-100 | Higher = push harder, more tire wear |
| **fuel_strategy** | 0-40 | Lean mixture (slower, saves fuel) |
| **fuel_strategy** | 40-60 | Balanced (neutral) |
| **fuel_strategy** | 60-100 | Rich mixture (faster, burns fuel) |
| **ers_mode** | 0-100 | 0=harvest, 100=deploy |
| **overtake_aggression** | 0-100 | Higher = more likely to overtake |
| **defense_intensity** | 0-100 | Higher = harder to overtake |

## Common Patterns

### Aggressive Strategy (Early Race)
```python
AgentDecision(
    energy_deployment=95.0,   # Deploy almost all
    tire_management=85.0,     # Push hard
    fuel_strategy=70.0,       # Rich mixture
    ers_mode=90.0,            # Max deployment
    overtake_aggression=90.0,
    defense_intensity=50.0
)
```

### Conservative Strategy (Late Race, Low Battery)
```python
AgentDecision(
    energy_deployment=30.0,   # Conserve battery
    tire_management=40.0,     # Save tires
    fuel_strategy=35.0,       # Lean mixture
    ers_mode=20.0,            # Heavy harvest
    overtake_aggression=50.0,
    defense_intensity=80.0    # Defend position
)
```

### Balanced Strategy (Mid Race)
```python
AgentDecision(
    energy_deployment=60.0,
    tire_management=60.0,
    fuel_strategy=50.0,
    ers_mode=50.0,
    overtake_aggression=60.0,
    defense_intensity=60.0
)
```

## Complete Example (10 Laps)

```python
from sim.physics_2026 import *

baseline = load_baseline()
decision = AgentDecision(70, 60, 50, 70, 80, 70)
state = RaceState(1, 100.0, 1, 0, 100.0, 110.0, 0)

for lap in range(1, 11):
    # Calculate lap
    lap_time = calculate_lap_time(decision, state, baseline)
    new_battery = update_battery(decision, state, baseline)
    new_tire = update_tire_condition(decision, state, baseline)
    new_fuel = update_fuel(decision, state, baseline)
    
    print(f"Lap {lap}: {lap_time:.2f}s | Bat: {new_battery:.1f}% | Tire: {new_tire:.1f}%")
    
    # Update state
    state = RaceState(
        lap=lap + 1,
        battery_soc=new_battery,
        position=state.position,
        tire_age=state.tire_age + 1,
        tire_life=new_tire,
        fuel_remaining=new_fuel,
        boost_used=state.boost_used
    )
```

## Documentation

- **PHYSICS_README.md** - Complete reference guide
- **IMPLEMENTATION_SUMMARY.md** - Implementation details
- **test_physics.py** - Test suite (read for more examples)
- **example_physics_usage.py** - Real-world usage patterns

## Support

All functions have comprehensive docstrings:
```python
help(calculate_lap_time)
help(update_battery)
help(AgentDecision)
```

## Quick Troubleshooting

**Import Error?**
```python
# Make sure you're in the project directory
import sys
sys.path.insert(0, '/Users/prajit/Desktop/projects/Gand')
```

**Values out of range?**
- All strategic variables: 0-100
- Battery SOC: 0-100
- Tire life: 0-100
- Functions clamp to valid ranges

**Physics seem wrong?**
```bash
# Run validation
python test_physics.py
# Should show: ✓ ALL TESTS PASSED
```

---

**Ready to use!** Start with `example_physics_usage.py` to see real patterns.
