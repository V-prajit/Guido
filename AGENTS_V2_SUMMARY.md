# Agents V2 - 6-Variable Strategic System

## Overview

Successfully implemented 8 agents using the new 6-variable decision system. All agents use `AgentDecision` with:
- `energy_deployment` (0-100)
- `tire_management` (0-100)
- `fuel_strategy` (0-100)
- `ers_mode` (0-100)
- `overtake_aggression` (0-100)
- `defense_intensity` (0-100)

---

## Agent Profiles

### 1. VerstappenStyle (Learned Agent)
**Based on:** Max Verstappen's 2024 Bahrain GP victory

**Base Profile:**
```
Energy Deployment:      29.5  (conservative, efficient)
Tire Management:       100.0  (aggressive push/conserve cycles)
Fuel Strategy:          52.9  (balanced)
ERS Mode:               35.4  (harvest-focused)
Overtake Aggression:    40.0  (cautious - started P1)
Defense Intensity:     100.0  (relentless position defense)
```

**Characteristics:**
- Conservative energy management for race-long efficiency
- Dynamic tire management based on stint phase
- Excellent defensive positioning
- Focus on track position over risky overtakes

**Adaptive Behaviors:**
- Low battery (< 30%) → harvest more, reduce deployment
- Late race high battery (lap 45+, >70%) → deploy more
- Worn tires (< 40% life) → conserve tires

---

### 2. HamiltonStyle (Learned Agent)
**Based on:** Lewis Hamilton's 2024 Bahrain GP (P7, 8 overtakes)

**Base Profile:**
```
Energy Deployment:      27.5  (most efficient of leaders)
Tire Management:       100.0  (aggressive)
Fuel Strategy:          51.9  (balanced)
ERS Mode:               30.9  (harvest-focused)
Overtake Aggression:   100.0  (race craft specialist)
Defense Intensity:      96.4  (strong defender)
```

**Characteristics:**
- Energy efficiency expert
- Aggressive in overtaking situations
- Strong defensive abilities
- Long stint capability

**Adaptive Behaviors:**
- Behind (position > 5) → increase aggression, deploy more
- Low battery (< 25%) → heavy harvest mode
- Long stints (tire age > 25) → preserve tires

---

### 3. AlonsoStyle (Learned Agent)
**Based on:** Fernando Alonso's 2024 Bahrain GP (P9, 10 overtakes)

**Base Profile:**
```
Energy Deployment:      25.7  (most conservative energy)
Tire Management:       100.0  (aggressive)
Fuel Strategy:          53.8  (balanced)
ERS Mode:               30.5  (harvest-focused)
Overtake Aggression:   100.0  (midfield specialist)
Defense Intensity:      85.7  (strong)
```

**Characteristics:**
- Master of energy management
- Midfield specialist - aggressive in battles
- Tire whisperer - can extend stints
- Opportunistic overtaker

**Adaptive Behaviors:**
- High battery (> 80%) → deploy opportunistically
- Low battery (< 30%) → heavy harvest mode
- Midfield position (P5-P10) → extra aggressive
- Worn tires (< 50% life) → preserve aggressively

---

### 4. ElectricBlitzer (Synthetic Agent)
**Strategy:** Deploy everything early, attack hard, blitz the start

**Base Profile:**
```
Energy Deployment:      95.0  (maximum early deployment)
Tire Management:        90.0  (push hard)
Fuel Strategy:          85.0  (rich mixture)
ERS Mode:               95.0  (deploy heavy)
Overtake Aggression:    95.0  (very aggressive)
Defense Intensity:      60.0  (medium)
```

**Characteristics:**
- Aggressive early-race strategy
- Aims to build insurmountable gap early
- Weakens in final laps
- High-risk, high-reward approach

**Adaptive Behaviors:**
- Early race (laps 1-20): 100% deployment
- Mid race (laps 21-40): 70% deployment
- Late race (laps 41+): 40% deployment (battery depleted)
- Critical battery (< 15%) → emergency harvest mode

---

### 5. EnergySaver (Synthetic Agent)
**Strategy:** Conserve early, attack late (reverse ElectricBlitzer)

**Base Profile:**
```
Energy Deployment:      30.0  (early race base)
Tire Management:        60.0  (moderate)
Fuel Strategy:          40.0  (lean)
ERS Mode:               30.0  (harvest heavy early)
Overtake Aggression:    50.0  (base)
Defense Intensity:      70.0  (solid defense)
```

**Characteristics:**
- Conservative early, aggressive late
- Heavy harvesting in opening laps
- Strong finish with full battery
- Patience-based strategy

**Adaptive Behaviors:**
- Early race (laps 1-20): 30% energy, heavy harvest
- Mid race (laps 21-40): 60% energy (×2 multiplier)
- Late race (laps 41+): 90% energy (×3 multiplier)
- Low battery safeguard: cap deployment if SOC < 30%

---

### 6. TireWhisperer (Synthetic Agent)
**Strategy:** Minimal tire wear, one-stop specialist

**Base Profile:**
```
Energy Deployment:      60.0  (moderate)
Tire Management:        35.0  (very gentle)
Fuel Strategy:          50.0  (balanced)
ERS Mode:               50.0  (balanced)
Overtake Aggression:    50.0  (balanced)
Defense Intensity:      65.0  (moderate)
```

**Characteristics:**
- Tire preservation specialist
- Sacrifices pace for tire life
- Aims for longest possible stints
- Consistency over speed

**Adaptive Behaviors:**
- Old tires (age > 20): 70% tire management multiplier
- Degraded tires (life < 50%): 60% multiplier
- Fresh tires (age < 5, life > 90%): 130% multiplier (can push)
- Adapts preservation intensity to tire condition

---

### 7. Opportunist (Synthetic Agent)
**Strategy:** Position-aware adaptive strategy

**Base Profile:**
```
Energy Deployment:      70.0  (base)
Tire Management:        65.0  (base)
Fuel Strategy:          55.0  (slightly rich)
ERS Mode:               60.0  (balanced)
Overtake Aggression:    50.0  (varies by position)
Defense Intensity:      50.0  (varies by position)
```

**Characteristics:**
- Adapts to race position dynamically
- Attacks when behind, defends when ahead
- Strategic flexibility
- Context-aware decision making

**Adaptive Behaviors:**
- **Leading (P1-P3):** Attack=40, Defend=90, Energy=60, Tire=55
- **Midfield (P4-P6):** Attack=70, Defend=65, Energy=75, Tire=65
- **Trailing (P7+):** Attack=95, Defend=50, Energy=85, Tire=75
- Low battery safeguard: reduce energy if SOC < 30%

---

### 8. AdaptiveAI (Playbook-Powered Agent)
**Strategy:** Reads Gemini-generated playbook and follows discovered rules

**Base Profile:**
```
Energy Deployment:      70.0  (balanced)
Tire Management:        65.0  (balanced)
Fuel Strategy:          55.0  (balanced)
ERS Mode:               60.0  (balanced)
Overtake Aggression:    70.0  (balanced)
Defense Intensity:      70.0  (balanced)
```

**Characteristics:**
- Playbook-powered AI
- Evaluates rules dynamically each lap
- Safe eval() with restricted context
- Graceful fallback to balanced strategy

**Implementation:**
- Loads `data/playbook.json` at initialization
- Evaluates rule conditions with safe eval()
- Applies matching rule actions
- Security: restricted eval context (no `__builtins__`)
- Available variables: `battery_soc`, `lap`, `position`, `tire_age`, `tire_life`, `fuel_remaining`, `boost_used`

**Example Playbook Rule:**
```json
{
  "rule": "Low Battery Conservation",
  "condition": "battery_soc < 30 and lap > 40",
  "action": {
    "energy_deployment": 30,
    "ers_mode": 20,
    "tire_management": 50
  },
  "confidence": 0.85
}
```

---

## Test Results

### Decision Variance (Mid-race: Lap 10, P3, 80% battery)
```
Agent                | Energy |   Tire |   Fuel |    ERS | Attack | Defend
--------------------------------------------------------------------------------
VerstappenStyle      |   28.6 |   97.9 |   56.4 |   32.5 |   43.6 |   97.6
HamiltonStyle        |   24.2 |   98.5 |   49.0 |   31.0 |   95.5 |   94.7
AlonsoStyle          |   30.5 |  100.0 |   54.9 |   33.6 |  100.0 |   84.6
ElectricBlitzer      |   96.6 |   93.7 |   83.1 |   98.1 |   98.4 |   59.2
EnergySaver          |   29.7 |   63.0 |   37.2 |   28.0 |   38.0 |   68.8
TireWhisperer        |   56.6 |   38.9 |   52.2 |   47.3 |   49.6 |   67.4
Opportunist          |   56.7 |   59.9 |   55.4 |   57.0 |   43.0 |   87.5
AdaptiveAI           |   68.9 |   63.6 |   56.3 |   55.9 |   71.9 |   65.3
```

### Strategy Diversity Metrics
- **Energy deployment variance:** 394.7 (highly diverse)
- **Tire management variance:** 465.6 (highly diverse)
- **Target variance:** >100 (PASSED)

### State Responsiveness Tests
✓ **ElectricBlitzer:** Early race (90.5) → Late race (39.7) energy deployment
✓ **EnergySaver:** Early race (29.4) → Late race (89.2) energy deployment
✓ **Opportunist:** Leading (Attack=37.2, Defend=93.8) vs Trailing (Attack=99.7, Defend=46.2)
✓ **TireWhisperer:** Fresh tires (47.9) → Worn tires (18.2) tire management

---

## Usage

```python
from sim.agents_v2 import create_agents_v2
from sim.physics_2024 import RaceState

# Create all agents
agents = create_agents_v2()

# Simulate a lap decision
state = RaceState(
    lap=30,
    battery_soc=60.0,
    position=5,
    tire_age=20,
    tire_life=65.0,
    fuel_remaining=70.0,
    boost_used=1
)

for agent in agents:
    decision = agent.decide(state)
    print(f"{agent.name}: Energy={decision.energy_deployment:.1f}")
```

---

## Integration Points

### With Physics Engine (`sim/physics_2024.py`)
- Uses `AgentDecision` dataclass
- Uses `RaceState` dataclass
- Compatible with `calculate_lap_time()`, `update_battery()`, `update_tire_condition()`, `update_fuel()`

### With Playbook System (`data/playbook.json`)
- AdaptiveAI reads playbook at initialization
- Evaluates conditions using safe eval()
- Applies actions dynamically
- Gracefully handles missing/invalid playbook

### With Simulation Engine (Future Integration)
- Factory function `create_agents_v2()` provides all agents
- Each agent's `decide()` method takes `RaceState`, returns `AgentDecision`
- Agents maintain no mutable state (stateless decisions)
- Compatible with multiprocessing (picklable)

---

## Success Criteria

✅ All 8 agents implemented
✅ Each uses 6-variable AgentDecision
✅ Learned agents load from learned_strategies.json
✅ Synthetic agents have unique, measurable strategies
✅ AdaptiveAI reads playbook
✅ Factory function creates all agents
✅ No errors when tested
✅ Strategy variance > 100 (highly diverse)
✅ State responsiveness verified

**Status:** ✅ COMPLETE - Ready for simulation integration
