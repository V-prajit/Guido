# Quick Reference: 6-Variable System

## For Developers Working with the API

This guide helps you understand the new 6-variable decision system and how to use the updated API.

---

## Decision Variables (Old vs New)

### Old System (3 variables)
```python
{
    "deploy_straight": 0-100,  # Electric power on straights
    "deploy_corner": 0-100,    # Electric power on corners
    "harvest": 0-100           # Energy recovery
}
```

### New System (6 variables)
```python
{
    "energy_deployment": 0-100,      # Overall electric power usage
    "tire_management": 0-100,        # Tire wear vs speed tradeoff
    "fuel_strategy": 0-100,          # Fuel mixture (lean to rich)
    "ers_mode": 0-100,               # ERS harvest vs deploy balance
    "overtake_aggression": 0-100,    # Overtaking risk/reward
    "defense_intensity": 0-100       # Defensive driving intensity
}
```

---

## DataFrame Columns (New Engine)

When you read CSV files from `/runs/*.csv`, expect these **15 columns**:

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `agent` | str | - | Agent name (VerstappenStyle, HamiltonStyle, etc.) |
| `lap` | int | 1-57 | Current lap number |
| `battery_soc` | float | 0-100 | Battery state of charge (%) |
| `tire_life` | float | 0-100 | Tire condition (%) |
| `fuel_remaining` | float | 0-110 | Fuel in kg |
| `lap_time` | float | 85-105 | Lap time in seconds |
| `cumulative_time` | float | >0 | Total race time so far |
| `final_position` | int | 1-8 | Final race position |
| `won` | bool | True/False | Did this agent win? |
| `energy_deployment` | float | 0-100 | Energy decision this lap |
| `tire_management` | float | 0-100 | Tire decision this lap |
| `fuel_strategy` | float | 0-100 | Fuel decision this lap |
| `ers_mode` | float | 0-100 | ERS decision this lap |
| `overtake_aggression` | float | 0-100 | Overtake decision this lap |
| `defense_intensity` | float | 0-100 | Defense decision this lap |

---

## API Usage Examples

### 1. Run Simulation

```python
from api.runner import run_simulations

run_id, csv_path, elapsed = run_simulations(
    num_scenarios=100,
    num_repeats=1,
    max_workers=4
)

print(f"Completed in {elapsed:.2f}s")
print(f"Results: {csv_path}")
```

**Output:**
```
runs/20251019_051133_7e66eb.csv  # 15 columns × (100 scenarios × 8 agents × 57 laps)
```

---

### 2. Aggregate Results

```python
from api.analysis import aggregate_results

stats = aggregate_results('runs/20251019_051133_7e66eb.csv')

# Access agent statistics
agent_stats = stats['AdaptiveAI']
print(f"Win rate: {agent_stats['win_rate']:.1f}%")
print(f"Avg energy: {agent_stats['avg_energy_deployment']:.1f}")
print(f"Avg tire mgmt: {agent_stats['avg_tire_management']:.1f}")
```

**Available Metrics per Agent:**
- `wins` - Number of race wins
- `win_rate` - Win percentage
- `avg_position` - Average finishing position
- `avg_lap_time` - Average lap time
- `avg_final_battery` - Average battery at race end
- `avg_final_tire_life` - Average tire life at race end
- `avg_final_fuel` - Average fuel at race end
- `avg_energy_deployment` - Average energy deployment (all laps)
- `avg_tire_management` - Average tire management (all laps)
- `avg_fuel_strategy` - Average fuel strategy (all laps)
- `avg_ers_mode` - Average ERS mode (all laps)
- `avg_overtake_aggression` - Average overtake aggression (all laps)
- `avg_defense_intensity` - Average defense intensity (all laps)

---

### 3. Get Recommendations

```python
from api.recommend import get_recommendations_fast

state = {
    'lap': 30,
    'battery_soc': 45,
    'position': 3,
    'tire_age': 25,
    'tire_life': 60,
    'fuel_remaining': 50,
    'boost_used': 1,
    'rain': False
}

recommendations, conditions, seed = get_recommendations_fast(state)

for rec in recommendations:
    print(f"Rule: {rec['rule']}")
    print(f"Confidence: {rec['confidence']:.2%}")
    print(f"Action: {rec['action']}")
    print(f"Rationale: {rec['rationale']}")
```

**Output:**
```python
{
    'rule': 'Tire Preservation (Mid-Race)',
    'action': {
        'energy_deployment': 60,
        'tire_management': 35,
        'fuel_strategy': 45,
        'ers_mode': 55,
        'overtake_aggression': 50,
        'defense_intensity': 70
    },
    'confidence': 0.80,
    'rationale': 'Mid-race with degraded tires - conserve tire life while maintaining competitive pace'
}
```

---

## Playbook Schema v2.0

The playbook is stored in `data/playbook.json`:

```json
{
  "schema_version": "2.0",
  "variables": [
    "energy_deployment",
    "tire_management",
    "fuel_strategy",
    "ers_mode",
    "overtake_aggression",
    "defense_intensity"
  ],
  "rules": [
    {
      "rule": "Low Battery Conservation (Late Race)",
      "condition": "battery_soc < 30 and lap > 40",
      "action": {
        "energy_deployment": 20,
        "tire_management": 65,
        "fuel_strategy": 50,
        "ers_mode": 10,
        "overtake_aggression": 40,
        "defense_intensity": 80
      },
      "confidence": 0.90,
      "uplift_win_pct": 22.5,
      "rationale": "..."
    }
  ]
}
```

---

## FastAPI Endpoints

### POST /run
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"num_scenarios": 100, "num_agents": 8, "repeats": 1}'
```

**Response:**
```json
{
  "run_id": "20251019_051133_7e66eb",
  "scenarios_completed": 100,
  "csv_path": "runs/20251019_051133_7e66eb.csv",
  "elapsed_sec": 8.2
}
```

---

### POST /analyze
```bash
curl -X POST http://localhost:8000/analyze
```

**Response:**
```json
{
  "stats": {
    "AdaptiveAI": {
      "wins": 65,
      "win_rate": 65.0,
      "avg_energy_deployment": 67.6,
      "avg_tire_management": 64.0,
      ...
    }
  },
  "playbook_preview": {
    "num_rules": 6
  }
}
```

---

### GET /playbook
```bash
curl http://localhost:8000/playbook
```

**Response:** Complete playbook JSON with schema v2.0

---

### POST /recommend
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "lap": 30,
    "battery_soc": 45,
    "position": 3,
    "tire_life": 60,
    "fuel_remaining": 50
  }'
```

**Response:**
```json
{
  "recommendations": [
    {
      "rule": "Tire Preservation (Mid-Race)",
      "action": {
        "energy_deployment": 60,
        "tire_management": 35,
        "fuel_strategy": 45,
        "ers_mode": 55,
        "overtake_aggression": 50,
        "defense_intensity": 70
      },
      "confidence": 0.80,
      "rationale": "..."
    }
  ],
  "latency_ms": 0.3,
  "timestamp": 1729315893.123,
  "seed": 1234
}
```

---

## Test Scripts

### Run All Tests
```bash
# Integration test
python scripts/test_api_integration.py

# Multiprocessing test
python scripts/test_multiprocessing.py

# Complete flow validation
python scripts/validate_complete_flow.py
```

---

## Common Patterns

### Pattern 1: Run and Analyze
```python
from api.runner import run_simulations
from api.analysis import aggregate_results

# Run
run_id, csv_path, elapsed = run_simulations(100, 1, 4)

# Analyze
stats = aggregate_results(csv_path)

# Find winner
winner = max(stats.items(), key=lambda x: x[1]['win_rate'])
print(f"Top performer: {winner[0]} with {winner[1]['win_rate']:.1f}% win rate")
```

### Pattern 2: Get Real-time Advice
```python
from api.recommend import get_recommendations_fast

# During race simulation
for lap in range(1, 58):
    state = get_current_state(lap)  # Your function
    recommendations, _, _ = get_recommendations_fast(state)

    if recommendations:
        action = recommendations[0]['action']
        # Apply action to agent
        apply_strategy(action)
```

### Pattern 3: Load and Analyze Historical Data
```python
import pandas as pd

# Load any run
df = pd.read_csv('runs/20251019_051133_7e66eb.csv')

# Filter for specific agent
adaptive = df[df['agent'] == 'AdaptiveAI']

# Analyze decision patterns
print(f"Avg energy deployment: {adaptive['energy_deployment'].mean():.1f}")
print(f"Avg tire management: {adaptive['tire_management'].mean():.1f}")

# Compare early vs late race
early = adaptive[adaptive['lap'] < 20]
late = adaptive[adaptive['lap'] > 40]

print(f"Early race energy: {early['energy_deployment'].mean():.1f}")
print(f"Late race energy: {late['energy_deployment'].mean():.1f}")
```

---

## Debugging Tips

### Check DataFrame Schema
```python
import pandas as pd
df = pd.read_csv('runs/latest.csv')
print(df.columns.tolist())  # Should have 15 columns
print(df.dtypes)
```

### Verify Playbook
```python
import json
with open('data/playbook.json', 'r') as f:
    playbook = json.load(f)
print(f"Schema version: {playbook.get('schema_version')}")
print(f"Variables: {playbook.get('variables')}")
print(f"Rules: {len(playbook['rules'])}")
```

### Test Recommendation Latency
```python
import time
from api.recommend import get_recommendations_fast

state = {'lap': 30, 'battery_soc': 50, 'position': 3, 'tire_life': 60, 'fuel_remaining': 50}

start = time.time()
recommendations, _, _ = get_recommendations_fast(state)
latency = (time.time() - start) * 1000

print(f"Latency: {latency:.2f}ms")  # Should be <50ms
```

---

## Migration from Old System

If you have old code using 3 variables:

**Old:**
```python
action = {
    'deploy_straight': 80,
    'deploy_corner': 50,
    'harvest': 60
}
```

**New:**
```python
action = {
    'energy_deployment': 70,      # Combines deploy_straight + deploy_corner
    'tire_management': 65,         # New: tire preservation
    'fuel_strategy': 55,           # New: fuel mixture
    'ers_mode': 60,                # Replaces harvest
    'overtake_aggression': 70,     # New: overtaking strategy
    'defense_intensity': 70        # New: defensive strategy
}
```

---

## Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Simulation (1 scenario, 8 agents) | <100ms | ~60ms |
| Aggregation (1000 scenarios) | <1s | ~200ms |
| Recommendation | <1.5s | <1ms |
| CSV write (1000 scenarios) | <500ms | ~100ms |

---

## Support

For issues or questions:
1. Check test scripts in `/scripts/`
2. Review `/Users/prajit/Desktop/projects/Gand/API_INTEGRATION_UPDATE.md`
3. Verify playbook schema in `/data/playbook.json`
4. Check CSV output columns (should be 15)
