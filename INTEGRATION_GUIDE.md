# GAME LOOP ↔ GEMINI ADVISOR INTEGRATION GUIDE

**Quick Reference for Game Loop Developer**

---

## 🚀 Quick Start (Copy-Paste Ready)

```python
from api.gemini_game_advisor import GameAdvisor

# 1. Initialize ONCE at game start
advisor = GameAdvisor()

# 2. At decision point, call this:
recommendations = advisor.analyze_decision_point(
    sim_results=sim_df,
    race_context=context_dict,
    strategy_params=strategies_list,
    timeout_seconds=2.5
)

# 3. Display recommendations['recommended'] and recommendations['avoid'] to player
# 4. Get player choice (strategy_id 0, 1, or 2)
# 5. Apply chosen strategy and resume race
```

---

## 📥 INPUT: What Game Loop Must Provide

### 1. **sim_results** (pandas DataFrame)

300 rows total: 100 simulations × 3 strategies

**Required columns:**
- `strategy_id` (int): 0, 1, or 2
- `final_position` (int): Final race position (1-8)
- `won` (bool): True if won race, False otherwise

**Optional but recommended columns:**
- `battery_soc` (float): Final battery state (0-100)
- `sim_run_id` (int): Simulation number (0-99 per strategy)
- `tire_life` (float): Final tire life (0-100)
- `fuel_remaining` (float): Final fuel (kg)

**Example:**
```python
import pandas as pd

sim_df = pd.DataFrame({
    'strategy_id': [0,0,0,..., 1,1,1,..., 2,2,2,...],  # 300 rows
    'sim_run_id': [0,1,2,..., 0,1,2,..., 0,1,2,...],
    'final_position': [1, 2, 3, 4, ...],
    'won': [True, False, False, ...],
    'battery_soc': [15.2, 12.1, 8.5, ...],  # Final battery after race
})

# Strategy 0: rows 0-99
# Strategy 1: rows 100-199
# Strategy 2: rows 200-299
```

### 2. **race_context** (dict)

Current race state when decision point triggered.

**Required fields:**
```python
race_context = {
    'lap': 15,                    # Current lap number
    'total_laps': 57,            # Total race laps
    'position': 4,               # Current position (1-8)
    'battery_soc': 45.0,         # Current battery (0-100)
    'tire_life': 62.0,           # Current tire life (0-100)
    'fuel_remaining': 28.0,      # Current fuel (kg)
    'event_type': 'RAIN_START'   # Why game paused (see below)
}
```

**Valid event_type values:**
- `'RAIN_START'` - Rain just started
- `'SAFETY_CAR'` - Safety car deployed
- `'TIRE_CRITICAL'` - Tires below 25%
- `'BATTERY_LOW'` - Battery below 15%
- `'OVERTAKE_OPPORTUNITY'` - Rival within 1s
- `'PIT_DECISION'` - Pit window opening

### 3. **strategy_params** (list of 3 dicts)

The 3 strategic variations you tested in simulations.

**Each strategy has 6 variables (all 0-100):**

```python
strategy_params = [
    # Strategy 0: Aggressive
    {
        'energy_deployment': 85,      # High electric power usage
        'tire_management': 70,        # Push tires moderately
        'fuel_strategy': 60,          # Some fuel conservation
        'ers_mode': 80,               # High energy recovery
        'overtake_aggression': 90,    # Very aggressive overtakes
        'defense_intensity': 40       # Light defense
    },

    # Strategy 1: Balanced
    {
        'energy_deployment': 60,
        'tire_management': 80,
        'fuel_strategy': 70,
        'ers_mode': 65,
        'overtake_aggression': 60,
        'defense_intensity': 55
    },

    # Strategy 2: Conservative
    {
        'energy_deployment': 35,      # Minimal battery usage
        'tire_management': 90,        # Heavy tire preservation
        'fuel_strategy': 85,          # Max fuel conservation
        'ers_mode': 50,
        'overtake_aggression': 30,    # Avoid risky moves
        'defense_intensity': 70       # Strong defense
    }
]
```

**IMPORTANT:** Order matters! Strategy 0 must match `sim_results[strategy_id==0]`, etc.

---

## 📤 OUTPUT: What Gemini Returns

### Complete Response Object

```python
{
    # ===== TOP 2 RECOMMENDED STRATEGIES =====
    'recommended': [
        {
            'strategy_id': 1,                    # Which strategy (0, 1, or 2)
            'strategy_name': 'Balanced',         # Human-readable name
            'win_rate': 39.0,                    # Win percentage (0-100)
            'avg_position': 2.3,                 # Average final position
            'rationale': 'Strategy B offers the highest win rate (39%) and best average finishing position (P2.3) in the rain. The balanced approach to energy deployment and tire management maximizes opportunities without excessive risk, maintaining a reasonable final battery level.',
            'confidence': 0.85,                  # Confidence score (0-1)
            'strategy_params': {                 # Full strategy config
                'energy_deployment': 60,
                'tire_management': 80,
                'fuel_strategy': 70,
                'ers_mode': 65,
                'overtake_aggression': 60,
                'defense_intensity': 55
            }
        },
        {
            'strategy_id': 0,                    # Second best
            'strategy_name': 'Aggressive',
            'win_rate': 37.0,
            'avg_position': 3.0,
            'rationale': 'Strategy A is a strong alternative with a 37% win rate, leveraging aggressive energy deployment in the rain. While it risks lower final battery (11.8%), the increased overtake aggression could be beneficial in the initial wet laps.',
            'confidence': 0.78,
            'strategy_params': {
                'energy_deployment': 85,
                'tire_management': 70,
                'fuel_strategy': 60,
                'ers_mode': 80,
                'overtake_aggression': 90,
                'defense_intensity': 40
            }
        }
    ],

    # ===== WORST STRATEGY TO AVOID =====
    'avoid': {
        'strategy_id': 2,                        # Which strategy to avoid
        'strategy_name': 'Conservative',
        'win_rate': 12.0,                        # Poor win rate
        'avg_position': 5.3,                     # Poor finishing position
        'rationale': "Strategy C's conservative approach yields a significantly lower win rate (12%) and a poor average finishing position (P5.3). The lack of aggression in the rain will likely result in lost positions and missed opportunities to capitalize on the changing conditions.",
        'risk': 'Drops to P7+ in 60% of simulations',  # Specific warning
        'strategy_params': {
            'energy_deployment': 35,
            'tire_management': 90,
            'fuel_strategy': 85,
            'ers_mode': 50,
            'overtake_aggression': 30,
            'defense_intensity': 70
        }
    },

    # ===== METADATA =====
    'latency_ms': 5245,                          # How long analysis took
    'used_fallback': False,                      # True if Gemini failed
    'gemini_available': True,                    # True if Gemini API working
    'timestamp': '2025-10-19T08:07:22.296311Z'  # When analysis ran
}
```

---

## 🎮 Complete Game Loop Integration Example

```python
from api.gemini_game_advisor import GameAdvisor
import pandas as pd

class RaceGame:
    def __init__(self):
        # Initialize Gemini advisor ONCE at game start
        self.advisor = GameAdvisor()
        self.current_lap = 0
        self.player_state = {...}

    def run_race(self):
        """Main game loop"""

        while self.current_lap < 57:
            # Advance race simulation
            self.current_lap += 1
            self.update_race_state()

            # Check if critical event occurred
            event_type = self.check_decision_point()

            if event_type:
                # PAUSE GAME - Decision needed!
                self.handle_decision_point(event_type)

    def check_decision_point(self):
        """Check if game should pause for player decision"""

        # Rain just started
        if self.conditions['rain'] and not self.handled_rain:
            return 'RAIN_START'

        # Safety car deployed
        if self.conditions['safety_car'] and not self.handled_sc:
            return 'SAFETY_CAR'

        # Battery critically low
        if self.player_state['battery_soc'] < 15:
            return 'BATTERY_LOW'

        # Tires degraded
        if self.player_state['tire_life'] < 25:
            return 'TIRE_CRITICAL'

        # No decision needed
        return None

    def handle_decision_point(self, event_type):
        """Pause game, get Gemini recommendations, wait for player choice"""

        print(f"⚠️ DECISION POINT: {event_type}")

        # STEP 1: Generate 3 strategy variations
        strategies = self.generate_strategy_variations(event_type)
        # Returns: [aggressive_params, balanced_params, conservative_params]

        # STEP 2: Run 100 quick sims per strategy (300 total)
        print("Running 300 simulations...")
        sim_results = self.run_quick_simulations(strategies, num_sims=100)
        # Returns: DataFrame with 300 rows

        # STEP 3: Get current race context
        race_context = {
            'lap': self.current_lap,
            'total_laps': 57,
            'position': self.player_state['position'],
            'battery_soc': self.player_state['battery_soc'],
            'tire_life': self.player_state['tire_life'],
            'fuel_remaining': self.player_state['fuel_remaining'],
            'event_type': event_type
        }

        # STEP 4: Call Gemini advisor
        print("Analyzing with Gemini...")
        recommendations = self.advisor.analyze_decision_point(
            sim_results=sim_results,
            race_context=race_context,
            strategy_params=strategies,
            timeout_seconds=2.5
        )

        print(f"Analysis complete in {recommendations['latency_ms']}ms")

        # STEP 5: Display to player (send to frontend)
        self.display_recommendations_to_player(recommendations)

        # STEP 6: Wait for player choice
        chosen_strategy_id = self.wait_for_player_input()
        # Player clicks Strategy A/B/C → returns 0, 1, or 2

        # STEP 7: Apply chosen strategy
        chosen_params = strategies[chosen_strategy_id]
        self.apply_strategy(chosen_params)

        # STEP 8: Mark decision as handled
        if event_type == 'RAIN_START':
            self.handled_rain = True

        # STEP 9: Resume race
        print(f"Resuming race with Strategy {chr(65+chosen_strategy_id)}...")

    def generate_strategy_variations(self, event_type):
        """Generate 3 strategic alternatives based on event"""

        # You can customize based on event type
        if event_type == 'RAIN_START':
            # Rain strategies: more aggressive deployment
            return [
                {'energy_deployment': 85, 'tire_management': 70, 'fuel_strategy': 60,
                 'ers_mode': 80, 'overtake_aggression': 90, 'defense_intensity': 40},
                {'energy_deployment': 60, 'tire_management': 80, 'fuel_strategy': 70,
                 'ers_mode': 65, 'overtake_aggression': 60, 'defense_intensity': 55},
                {'energy_deployment': 35, 'tire_management': 90, 'fuel_strategy': 85,
                 'ers_mode': 50, 'overtake_aggression': 30, 'defense_intensity': 70},
            ]

        elif event_type == 'TIRE_CRITICAL':
            # Tire strategies: focus on tire management
            return [
                {'energy_deployment': 90, 'tire_management': 40, ...},  # Push on worn tires
                {'energy_deployment': 60, 'tire_management': 70, ...},  # Balanced
                {'energy_deployment': 30, 'tire_management': 95, ...},  # Max conservation
            ]

        # etc...

    def run_quick_simulations(self, strategies, num_sims=100):
        """Run fast simulations from current state"""

        results = []

        for strategy_id, strategy_params in enumerate(strategies):
            for sim_run in range(num_sims):
                # Run simulation from current state to race end
                result = self.simulate_race_from_current_state(strategy_params)

                results.append({
                    'strategy_id': strategy_id,
                    'sim_run_id': sim_run,
                    'final_position': result['position'],
                    'won': result['position'] == 1,
                    'battery_soc': result['final_battery'],
                    'tire_life': result['final_tires'],
                    'fuel_remaining': result['final_fuel']
                })

        return pd.DataFrame(results)

    def display_recommendations_to_player(self, recommendations):
        """Send to frontend for display"""

        # Extract data for UI
        top1 = recommendations['recommended'][0]
        top2 = recommendations['recommended'][1]
        avoid = recommendations['avoid']

        # Send to frontend (WebSocket, REST API, etc.)
        self.send_to_frontend({
            'type': 'DECISION_POINT',
            'strategies': [
                {
                    'id': 0,
                    'name': top1['strategy_name'],
                    'win_rate': top1['win_rate'],
                    'rationale': top1['rationale'],
                    'badge': 'RECOMMENDED #1',
                    'color': 'green'
                },
                {
                    'id': 1,
                    'name': top2['strategy_name'],
                    'win_rate': top2['win_rate'],
                    'rationale': top2['rationale'],
                    'badge': 'RECOMMENDED #2',
                    'color': 'blue'
                },
                {
                    'id': 2,
                    'name': avoid['strategy_name'],
                    'win_rate': avoid['win_rate'],
                    'rationale': avoid['rationale'],
                    'badge': 'AVOID',
                    'color': 'red',
                    'risk': avoid['risk']
                }
            ]
        })
```

---

## 🎨 Frontend Display Format

Send this to your frontend developer:

```javascript
// What they'll receive from backend
{
  "type": "DECISION_POINT",
  "strategies": [
    {
      "id": 0,
      "name": "Balanced",
      "win_rate": 39.0,
      "avg_position": 2.3,
      "rationale": "Strategy B offers the highest win rate...",
      "badge": "RECOMMENDED #1",
      "color": "green",
      "confidence": 0.85
    },
    {
      "id": 1,
      "name": "Aggressive",
      "win_rate": 37.0,
      "avg_position": 3.0,
      "rationale": "Strategy A is a strong alternative...",
      "badge": "RECOMMENDED #2",
      "color": "blue",
      "confidence": 0.78
    },
    {
      "id": 2,
      "name": "Conservative",
      "win_rate": 12.0,
      "avg_position": 5.3,
      "rationale": "Strategy C's conservative approach...",
      "badge": "AVOID",
      "color": "red",
      "risk": "Drops to P7+ in 60% of simulations"
    }
  ]
}

// Player clicks a card → send back:
{
  "chosen_strategy_id": 1  // 0, 1, or 2
}
```

---

## ⚠️ Error Handling

### If Gemini API Fails

The advisor **automatically falls back** to simple heuristics:

```python
recommendations = advisor.analyze_decision_point(...)

if recommendations['used_fallback']:
    print("⚠️ Using fallback recommendations (Gemini unavailable)")
    # Recommendations still valid, just simpler rationales
else:
    print("✅ Using Gemini-powered recommendations")
```

Fallback rationales look like:
> "Highest win rate (39.0%) across 100 simulations. Average finishing position: P2.3."

Still usable, just less contextual than Gemini's analysis.

### Validation

All responses are **validated before returning**:
- ✅ Always has 2 recommendations + 1 avoid
- ✅ All required fields present
- ✅ strategy_id values are valid (0, 1, or 2)
- ✅ Confidence scores between 0-1

**You don't need to validate** - it's guaranteed correct.

---

## 📊 Performance Expectations

| Metric | Target | Typical | Notes |
|--------|--------|---------|-------|
| **Gemini Analysis** | <2.5s | 2-5s | Can vary with API load |
| **Fallback** | <100ms | <10ms | Instant if Gemini fails |
| **Total Latency** | <4s | 2-6s | Including sim aggregation |

**Optimization tip:** If too slow, reduce `timeout_seconds` to 2.0 or use faster model:
```python
# In api/gemini_game_advisor.py line 50:
'gemini-1.5-flash'  # Instead of gemini-2.0-flash-exp
```

---

## 🧪 Test Before Integration

```bash
# Test with mock data (no game loop needed)
python test_game_advisor.py

# Should output:
# ✅ GameAdvisor initialized with Gemini
# ✅ Analysis Complete!
# ✅ Test COMPLETED SUCCESSFULLY!
```

This proves Gemini integration works before you connect it to game loop.

---

## 🚨 Common Issues & Fixes

### Issue: "GenerativeModel() got unexpected keyword argument 'system_instruction'"

**Fix:** Upgrade google-generativeai
```bash
pip install --upgrade google-generativeai
```

### Issue: "Gemini initialization failed: API key not found"

**Fix:** Set environment variable
```bash
export GEMINI_API_KEY=your_actual_api_key_here
```

Or create `.env` file:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### Issue: Latency >10s

**Fix:** Reduce timeout or use faster model
```python
recommendations = advisor.analyze_decision_point(
    ...,
    timeout_seconds=2.0  # Reduce from 2.5s
)
```

---

## 📞 Need Help?

If you get stuck:

1. **Check test works:** `python test_game_advisor.py`
2. **Check environment:** `echo $GEMINI_API_KEY`
3. **Check version:** `pip show google-generativeai`
4. **Read the code:** `api/gemini_game_advisor.py` has detailed docstrings

---

## ✅ Integration Checklist

- [ ] Import GameAdvisor: `from api.gemini_game_advisor import GameAdvisor`
- [ ] Initialize once: `advisor = GameAdvisor()`
- [ ] Detect decision points: Rain, safety car, tire critical, etc.
- [ ] Generate 3 strategy variations
- [ ] Run 100 quick sims per strategy (300 total)
- [ ] Build race_context dict with current state
- [ ] Call `advisor.analyze_decision_point(...)`
- [ ] Display `recommendations['recommended']` and `recommendations['avoid']`
- [ ] Get player choice (strategy_id 0, 1, or 2)
- [ ] Apply chosen strategy and resume race

**Estimated integration time: 2-4 hours**

---

**You're ready to integrate! The Gemini advisor is production-ready and tested.** 🚀
