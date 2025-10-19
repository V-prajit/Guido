# DEV1 (SIM/PERF) - IMPLEMENTATION GUIDE

**Your Mission:** Build the core simulation engine for Strategy Gym 2026, an F1 energy management strategy discovery system.

## Tools Strategy

- **ChatGPT**: NumPy vectorization, performance optimization, micro-benchmarks
- **Claude Code**: Refactoring, implementing TODOs, adding tests, code structure

## Implementation Timeline (H0-H8)

### Progress Tracker
- ✅ **H0-H1**: Core Engine Skeleton - COMPLETED
- ⏳ **H1-H2**: Scenario Generation - NOT STARTED
- ⏳ **H2-H3**: Eight Agent Implementations - NOT STARTED
- ⏳ **H3-H4**: Performance Optimization - NOT STARTED
- ⏳ **H5-H6**: Adaptive AI Implementation - NOT STARTED
- ⏳ **H6-H7**: Precompute Lookup Table - NOT STARTED
- ⏳ **H7-H8**: Final Performance Tuning - NOT STARTED

---

## H0-H1: Core Engine Skeleton ✅ COMPLETED

**Goal:** Basic simulation that can run 1 race with 1 agent

**Status:** ✅ All tests passing. Can run 10-lap race with DummyAgent.

### Step 1: Read the Physics Spec
- Open `prompts/physics_spec.md` and understand the model
- This is a SIMPLIFIED model, not realistic physics
- Focus: lap time as function of deployment decisions

### Step 2: Create `sim/engine.py`

#### A) RaceState Dataclass
```python
from dataclasses import dataclass

@dataclass
class RaceState:
    lap: int              # Current lap (1-57)
    battery_soc: float    # State of charge (0-100%)
    position: int         # Current race position
    tire_age: int         # Laps on current tires
    boost_used: int       # How many boost uses remaining (0-2)
```

#### B) Agent Base Class
```python
class Agent:
    def __init__(self, name: str, params: dict):
        self.name = name
        self.params = params

    def decide(self, state: RaceState) -> dict:
        """
        Returns: {
            'deploy_straight': 0-100,
            'deploy_corner': 0-100,
            'harvest': 0-100,
            'use_boost': bool
        }
        """
        raise NotImplementedError
```

#### C) simulate_lap() Function
```python
def simulate_lap(state: RaceState, decision: dict, scenario: dict) -> tuple[RaceState, float]:
    """
    Takes: RaceState, decision dict, scenario dict
    Returns: (new_RaceState, lap_time_seconds)
    """
    # Start with base time
    base_time = 90.0
    lap_time = base_time

    # Subtract deployment bonus
    lap_time -= decision['deploy_straight'] * 0.003  # max -0.3s
    lap_time -= decision['deploy_corner'] * 0.002    # max -0.2s

    # Add harvesting penalty
    lap_time += decision['harvest'] * 0.0015  # max +0.15s

    # Add low battery penalty
    if state.battery_soc < 20:
        lap_time += (20 - state.battery_soc) * 0.02

    # Update battery SOC
    drain = (decision['deploy_straight'] * 0.02) + (decision['deploy_corner'] * 0.015)
    charge = decision['harvest'] * 0.025
    new_soc = max(0, min(100, state.battery_soc - drain + charge))

    # Create new state
    new_state = RaceState(
        lap=state.lap + 1,
        battery_soc=new_soc,
        position=state.position,
        tire_age=state.tire_age + 1,
        boost_used=state.boost_used + (1 if decision['use_boost'] else 0)
    )

    return new_state, lap_time
```

#### D) simulate_race() Function
```python
import pandas as pd

def simulate_race(scenario: dict, agents: list) -> pd.DataFrame:
    """
    Takes: scenario dict, list of Agents
    Returns: pandas DataFrame with columns [agent, lap, battery_soc, lap_time, final_position, won]
    """
    num_laps = scenario.get('num_laps', 57)
    results = []
    agent_times = {agent.name: 0.0 for agent in agents}

    # Initialize states for each agent
    states = {
        agent.name: RaceState(lap=1, battery_soc=100.0, position=i+1, tire_age=0, boost_used=0)
        for i, agent in enumerate(agents)
    }

    # Simulate each lap
    for lap in range(1, num_laps + 1):
        for agent in agents:
            state = states[agent.name]
            decision = agent.decide(state)
            new_state, lap_time = simulate_lap(state, decision, scenario)

            agent_times[agent.name] += lap_time
            states[agent.name] = new_state

            results.append({
                'agent': agent.name,
                'lap': lap,
                'battery_soc': new_state.battery_soc,
                'lap_time': lap_time,
                'cumulative_time': agent_times[agent.name],
                'final_position': 0,  # Will calculate after
                'won': 0
            })

    # Determine winner (lowest total time)
    winner = min(agent_times.items(), key=lambda x: x[1])[0]

    # Update positions and won flag
    df = pd.DataFrame(results)
    for agent_name in agent_times.keys():
        agent_mask = df['agent'] == agent_name
        df.loc[agent_mask, 'final_position'] = sorted(agent_times.values()).index(agent_times[agent_name]) + 1
        df.loc[agent_mask, 'won'] = 1 if agent_name == winner else 0

    return df
```

### Step 3: Test It Works

Create `test_engine.py`:
```python
from sim.engine import Agent, RaceState, simulate_race

class DummyAgent(Agent):
    def decide(self, state):
        return {
            'deploy_straight': 50,
            'deploy_corner': 50,
            'harvest': 50,
            'use_boost': False
        }

scenario = {'num_laps': 10}
agents = [DummyAgent("Test", {})]
df = simulate_race(scenario, agents)
print(df)
print(f"\nTotal time: {df['cumulative_time'].max():.2f}s")
```

**✅ Checkpoint H1:** Can run 1 race with 1 agent, get DataFrame output

**Completion Status:**
- ✅ `sim/engine.py` created with all components (245 lines)
- ✅ `test_engine.py` created with DummyAgent and validation checks
- ✅ Test passed: 4/4 validation checks
- ✅ Physics verified: lap time 89.825s, battery drain -0.5%/lap
- ✅ Ready for H1-H2: Scenario Generation

---

## H1-H2: Scenario Generation

**Goal:** Create 100 diverse scenarios

### Step 4: Create `sim/scenarios.py`

```python
import numpy as np

def generate_scenarios(num_scenarios: int) -> list[dict]:
    """
    Generate diverse race scenarios.

    Each scenario has:
    - id: int
    - num_laps: 50, 57, or 70
    - rain_lap: int or None (25% chance, lap 20-50)
    - safety_car_lap: int or None (33% chance, lap 15-40)
    - track_type: 'power' | 'technical' | 'balanced'
    - temperature: 20-35 degrees C
    """
    scenarios = []

    for i in range(num_scenarios):
        # Use deterministic seed for reproducibility
        np.random.seed(i)

        # Lap count distribution
        num_laps = np.random.choice([50, 57, 70])

        # Rain (25% chance between lap 20-50)
        rain_lap = None
        if np.random.random() < 0.25:
            rain_lap = np.random.randint(20, min(50, num_laps))

        # Safety car (33% chance between lap 15-40)
        safety_car_lap = None
        if np.random.random() < 0.33:
            safety_car_lap = np.random.randint(15, min(40, num_laps))

        # Track type
        track_type = np.random.choice(['power', 'technical', 'balanced'])

        # Temperature
        temperature = np.random.uniform(20.0, 35.0)

        scenarios.append({
            'id': i,
            'num_laps': num_laps,
            'rain_lap': rain_lap,
            'safety_car_lap': safety_car_lap,
            'track_type': track_type,
            'temperature': temperature
        })

    return scenarios
```

### Step 5: Update simulate_lap() to Handle Scenario Events

```python
def simulate_lap(state: RaceState, decision: dict, scenario: dict) -> tuple[RaceState, float]:
    # ... existing code ...

    # Add rain penalty if this is the rain lap
    if scenario.get('rain_lap') == state.lap:
        lap_time += 2.0

    # Safety car handling would bunch up cars (simplified: no effect on lap time for now)

    return new_state, lap_time
```

**✅ Checkpoint H2:** Can generate 100 scenarios, run them, get varied results

---

## H2-H3: Eight Agent Implementations

**Goal:** Create 8 agents with DISTINCT behaviors

### Step 6: Create `sim/agents.py`

```python
from sim.engine import Agent, RaceState

class ElectricBlitz(Agent):
    """Deploys all battery early, fast start, struggles late"""
    def decide(self, state: RaceState):
        # Front-load: deploy more when battery is full
        battery_factor = state.battery_soc / 100.0
        return {
            'deploy_straight': 90 * battery_factor,
            'deploy_corner': 70 * battery_factor,
            'harvest': 30,
            'use_boost': state.lap < 10 and state.boost_used < 2
        }

class EnergySaver(Agent):
    """Conservative early, strong finish"""
    def decide(self, state: RaceState):
        # Assume 57 lap race for calculation
        race_progress = state.lap / 57.0
        return {
            'deploy_straight': 40 + (race_progress * 40),
            'deploy_corner': 40 + (race_progress * 30),
            'harvest': 70,
            'use_boost': state.lap > 50 and state.boost_used < 2
        }

class BalancedHybrid(Agent):
    """Steady throughout"""
    def decide(self, state: RaceState):
        return {
            'deploy_straight': 60,
            'deploy_corner': 50,
            'harvest': 50,
            'use_boost': False  # Never uses boost
        }

class CornerSpecialist(Agent):
    """Saves electric for corner exits"""
    def decide(self, state: RaceState):
        return {
            'deploy_straight': 30,
            'deploy_corner': 80,
            'harvest': 60,
            'use_boost': False
        }

class StraightDominator(Agent):
    """Max speed on straights"""
    def decide(self, state: RaceState):
        return {
            'deploy_straight': 85,
            'deploy_corner': 30,
            'harvest': 55,
            'use_boost': False
        }

class LateCharger(Agent):
    """Harvests heavily early, attacks late"""
    def decide(self, state: RaceState):
        if state.lap < 30:
            return {
                'deploy_straight': 30,
                'deploy_corner': 30,
                'harvest': 80,
                'use_boost': False
            }
        else:
            return {
                'deploy_straight': 90,
                'deploy_corner': 70,
                'harvest': 20,
                'use_boost': state.boost_used < 2
            }

class OvertakeHunter(Agent):
    """Saves battery for overtaking opportunities"""
    def decide(self, state: RaceState):
        # Simplified: just use position as proxy
        in_battle = state.position > 1 and state.position < 5
        boost_now = in_battle and state.boost_used < 2 and state.lap > 10

        deploy = 80 if in_battle else 50
        return {
            'deploy_straight': deploy,
            'deploy_corner': deploy,
            'harvest': 45,
            'use_boost': boost_now
        }

class AdaptiveAI(Agent):
    """Will read playbook later (H5-H6)"""
    def __init__(self, name: str, params: dict, playbook: dict = None):
        super().__init__(name, params)
        self.playbook = playbook or {'rules': []}

    def decide(self, state: RaceState):
        # For now, just balanced
        return {
            'deploy_straight': 60,
            'deploy_corner': 50,
            'harvest': 50,
            'use_boost': False
        }
```

### Step 7: Create create_agents() Helper

```python
def create_agents():
    """Factory function to create all 8 agents"""
    return [
        ElectricBlitz("Electric_Blitz", {}),
        EnergySaver("Energy_Saver", {}),
        BalancedHybrid("Balanced_Hybrid", {}),
        CornerSpecialist("Corner_Specialist", {}),
        StraightDominator("Straight_Dominator", {}),
        LateCharger("Late_Charger", {}),
        OvertakeHunter("Overtake_Hunter", {}),
        AdaptiveAI("Adaptive_AI", {})
    ]
```

### Step 8: Test Diversity

Run 10 scenarios with all 8 agents. Verify different agents win different scenarios.

```python
# Add to test_engine.py
from sim.scenarios import generate_scenarios
from sim.agents import create_agents

scenarios = generate_scenarios(10)
agents = create_agents()
wins = {agent.name: 0 for agent in agents}

for scenario in scenarios:
    df = simulate_race(scenario, agents)
    winner = df[df['won'] == 1]['agent'].iloc[0]
    wins[winner] += 1

print("Win distribution:")
for agent, count in sorted(wins.items(), key=lambda x: -x[1]):
    print(f"{agent}: {count}/10")
```

**✅ Checkpoint H3:** 8 agents with distinct strategies, different winners across scenarios

---

## H3-H4: Performance Optimization

**Goal:** Get to 1000 simulations in <5 seconds

### Step 9: Vectorize Lap Simulation

**🤖 USE CHATGPT:**

Prompt:
```
I have this simulate_lap() function. Vectorize it using NumPy so I can simulate
all agents in parallel in one pass. Here's my current code:

[paste simulate_lap()]

The goal is to process all 8 agents simultaneously rather than in a loop.
```

### Step 10: Add Numba JIT Compilation

**🤖 USE CHATGPT:**

Prompt:
```
Add Numba @njit decorator to my lap time calculation function for 10x speedup.
Here's my code:

[paste lap time calculation section]
```

Example pattern:
```python
import numba

@numba.jit(nopython=True)
def calculate_lap_time(deploy_straight, deploy_corner, harvest, battery_soc):
    lap_time = 90.0
    lap_time -= deploy_straight * 0.003
    lap_time -= deploy_corner * 0.002
    lap_time += harvest * 0.0015
    if battery_soc < 20:
        lap_time += (20 - battery_soc) * 0.02
    return lap_time
```

### Step 11: Create Benchmark Script

Create `scripts/bench.py`:
```python
import time
from sim.scenarios import generate_scenarios
from sim.agents import create_agents
from sim.engine import simulate_race

scenarios = generate_scenarios(1000)
agents = create_agents()

start = time.time()
for scenario in scenarios:
    df = simulate_race(scenario, agents)
elapsed = time.time() - start

print(f"1000 scenarios in {elapsed:.2f}s")
print(f"Rate: {1000/elapsed:.1f} scenarios/sec")
print(f"Target: >200 scenarios/sec")
print(f"Status: {'✅ PASS' if 1000/elapsed > 200 else '❌ FAIL'}")
```

**TARGET:** >200 scenarios/sec (1000 in 5s)

**✅ Checkpoint H4:** `python scripts/bench.py` shows <5s for 1000 scenarios

---

## H5-H6: Adaptive AI Implementation

**Goal:** Make AdaptiveAI read playbook and follow rules

### Step 12: Update AdaptiveAI Class

```python
class AdaptiveAI(Agent):
    def __init__(self, name: str, params: dict, playbook: dict = None):
        super().__init__(name, params)
        self.playbook = playbook or {'rules': []}

    def decide(self, state: RaceState):
        # Check each rule
        for rule in self.playbook.get('rules', []):
            if self.matches_condition(rule['condition'], state):
                return rule['action']

        # Default: balanced
        return {
            'deploy_straight': 60,
            'deploy_corner': 50,
            'harvest': 50,
            'use_boost': False
        }

    def matches_condition(self, condition: str, state: RaceState) -> bool:
        """
        Evaluate condition string against state.
        Example condition: "battery_soc < 30 and lap > 40"
        """
        try:
            context = {
                'battery_soc': state.battery_soc,
                'lap': state.lap,
                'position': state.position,
                'tire_age': state.tire_age,
                'boost_used': state.boost_used
            }
            # Safe eval with restricted builtins
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            print(f"Condition eval failed: {condition}, error: {e}")
            return False
```

### Step 13: Create Validation Script

Create `scripts/validate.py`:
```python
import json
import numpy as np
from sim.scenarios import generate_scenarios
from sim.agents import create_agents, AdaptiveAI
from sim.engine import simulate_race

# Load playbook (will be generated by R4 later)
try:
    with open('data/playbook.json', 'r') as f:
        playbook = json.load(f)
except FileNotFoundError:
    print("⚠️  No playbook found, using empty playbook")
    playbook = {'rules': []}

# Generate NEW scenarios (different seed)
np.random.seed(9999)
scenarios = generate_scenarios(20)

# Replace last agent with playbook-powered adaptive
base_agents = create_agents()[:-1]
adaptive = AdaptiveAI("Adaptive_AI", {}, playbook)
agents = base_agents + [adaptive]

# Run validation
wins_by_agent = {a.name: 0 for a in agents}

for scenario in scenarios:
    df = simulate_race(scenario, agents)
    winner = df[df['won'] == 1]['agent'].iloc[0]
    wins_by_agent[winner] += 1

print("=== VALIDATION RESULTS ===")
for agent, wins in sorted(wins_by_agent.items(), key=lambda x: -x[1]):
    print(f"{agent}: {wins}/20 ({wins/20*100:.1f}%)")

adaptive_wins = wins_by_agent['Adaptive_AI']
baseline_wins = [w for a, w in wins_by_agent.items() if a != 'Adaptive_AI']
median_baseline = sorted(baseline_wins)[len(baseline_wins)//2]

print(f"\nAdaptive: {adaptive_wins/20*100:.1f}%")
print(f"Median baseline: {median_baseline/20*100:.1f}%")
print(f"Status: {'✅ PASS' if adaptive_wins > median_baseline else '❌ FAIL'}")
```

**✅ Checkpoint H6:** Adaptive AI wins ≥60% on validation (once playbook exists)

---

## H6-H7: Precompute Lookup Table (Optional)

**Goal:** Create fast lookup for common states

### Step 14: Create Lookup Table

Create `scripts/precompute_lookup.py`:
```python
import json
from sim.agents import AdaptiveAI
from sim.engine import RaceState

# Load playbook
try:
    with open('data/playbook.json', 'r') as f:
        playbook = json.load(f)
except FileNotFoundError:
    print("No playbook found, skipping")
    exit(0)

adaptive = AdaptiveAI("lookup", {}, playbook)
lookup = {}

# Grid search common states
for lap in [10, 20, 30, 40, 50]:
    for battery in [20, 40, 60, 80]:
        for position in [1, 3, 5, 10]:
            state = RaceState(
                lap=lap,
                battery_soc=battery,
                position=position,
                tire_age=lap,
                boost_used=0
            )
            decision = adaptive.decide(state)
            lookup[f"{lap}_{battery}_{position}"] = decision

# Save
with open('data/lookup.json', 'w') as f:
    json.dump(lookup, f, indent=2)

print(f"✅ Precomputed {len(lookup)} state mappings")
```

**✅ Checkpoint H7:** Lookup table generated for fast recommendations

---

## H7-H8: Final Performance Tuning

**Goal:** Profile and optimize remaining bottlenecks

### Step 15: Profile and Optimize

**🤖 USE CHATGPT:**

Prompt:
```
Profile my simulate_race() function and identify the top 3 performance bottlenecks.
Here's my code:

[paste simulate_race()]

Give me 3 specific optimizations with code snippets.
```

### Step 16: Create Performance Report

Create `scripts/perf_report.py`:
```python
import time
import json
from sim.scenarios import generate_scenarios
from sim.agents import create_agents
from sim.engine import simulate_race

scenarios = generate_scenarios(1000)
agents = create_agents()

# Measure
start = time.time()
for scenario in scenarios:
    df = simulate_race(scenario, agents)
elapsed = time.time() - start

perf_data = {
    "num_scenarios": 1000,
    "num_agents": 8,
    "total_time_sec": round(elapsed, 2),
    "scenarios_per_sec": round(1000 / elapsed, 1),
    "avg_scenario_time_ms": round((elapsed / 1000) * 1000, 2),
    "target_met": elapsed < 5.0
}

# Create data directory if needed
import os
os.makedirs('data', exist_ok=True)

with open('data/perf.json', 'w') as f:
    json.dump(perf_data, f, indent=2)

print("=== PERFORMANCE REPORT ===")
print(json.dumps(perf_data, indent=2))
print(f"\nStatus: {'✅ PASS' if perf_data['target_met'] else '❌ FAIL'}")
```

**✅ Checkpoint H8:** Performance metrics logged, ready for demo

---

## Testing Checklist

Run these before declaring H8 complete:

```bash
# Test 1: Single race
python -c "from sim.engine import *; from sim.agents import *; print(simulate_race({'num_laps': 10}, create_agents()))"

# Test 2: Benchmark
python scripts/bench.py
# Expected: <5s for 1000 scenarios

# Test 3: Validation (after playbook exists)
python scripts/validate.py
# Expected: Adaptive >60% win rate

# Test 4: Performance report
python scripts/perf_report.py
# Expected: Creates data/perf.json with metrics
```

All should work without errors.

---

## Files You Will Create

- [x] `sim/__init__.py` (empty, for module) ✅ H0-H1
- [x] `sim/engine.py` (RaceState, Agent, simulate_lap, simulate_race) ✅ H0-H1
- [ ] `sim/agents.py` (8 agent classes + create_agents)
- [ ] `sim/scenarios.py` (generate_scenarios)
- [ ] `scripts/bench.py` (performance benchmark)
- [ ] `scripts/validate.py` (validation runner)
- [ ] `scripts/precompute_lookup.py` (optional optimization)
- [ ] `scripts/perf_report.py` (metrics logger)
- [x] `test_engine.py` (unit test) ✅ H0-H1

---

## Success Criteria (by H8)

- ✅ 8 agents with distinct behaviors
- ✅ 1000 sims in <5 seconds
- ✅ Adaptive AI that reads playbook
- ✅ Validation showing Adaptive ≥60% wins (once playbook exists)
- ✅ All scripts working
- ✅ Performance metrics logged

---

## Critical Formulas Reference

### Lap Time Calculation
```python
base_time = 90.0
lap_time = base_time
lap_time -= deploy_straight * 0.003  # max -0.3s
lap_time -= deploy_corner * 0.002    # max -0.2s
lap_time += harvest * 0.0015         # max +0.15s penalty
if battery_soc < 20:
    lap_time += (20 - battery_soc) * 0.02
if rain:
    lap_time += 2.0
```

### Battery Dynamics
```python
drain = (deploy_straight * 0.02) + (deploy_corner * 0.015)
charge = harvest * 0.025
new_soc = clamp(current_soc - drain + charge, 0, 100)
```

---

## When to Use Which Tool

### Use ChatGPT For:
- "How do I vectorize this NumPy code?"
- "Add Numba JIT to this function"
- "What's the bottleneck in this code?"
- "Give me 3 performance optimizations"

### Use Claude Code For:
- Implementing full files with TODOs
- Refactoring code structure
- Adding docstrings and type hints
- Writing unit tests
- Debugging integration issues

---

## Integration Notes

### For R2 (Backend)
Your `simulate_race()` function MUST:
- Be a pure function (no side effects)
- Return a pandas DataFrame
- Be picklable for multiprocessing
- Include columns: agent, lap, battery_soc, lap_time, final_position, won

### For R4 (AI/Insights)
Your `AdaptiveAI` agent will consume playbook JSON with:
- `rules`: List of rule objects
- Each rule has: `condition` (Python expression), `action` (decision dict)
- Conditions evaluated with restricted eval() for security

---

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run single test
python test_engine.py

# Benchmark performance
python scripts/bench.py

# Validate adaptive AI (needs playbook)
python scripts/validate.py

# Generate performance report
python scripts/perf_report.py

# Create directories
mkdir -p sim scripts data
```

---

## Common Pitfalls to Avoid

1. **Don't make physics too complex** - Keep it simple for speed
2. **Don't forget to clamp battery SOC** - Must stay in [0, 100]
3. **Don't use global state** - Everything must be picklable
4. **Don't optimize prematurely** - Get it working first (H0-H3), then optimize (H3-H8)
5. **Don't forget deterministic seeds** - Use `np.random.seed(i)` in scenario generation

---

## Performance Targets Summary

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Simulation Speed | >200 scenarios/sec | `python scripts/bench.py` |
| Total Time (1000 scenarios) | <5 seconds | `python scripts/bench.py` |
| Adaptive Win Rate | >60% | `python scripts/validate.py` |
| Agent Diversity | Different winners per scenario | Visual inspection of results |

---

**END OF IMPLEMENTATION GUIDE**

Refer to `CLAUDE.md` for project context and `PROJECT.md` for full system architecture.
