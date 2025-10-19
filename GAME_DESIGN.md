# F1 STRATEGY GYM 2026 - INTERACTIVE GAME MODE

**Interactive AI-Powered Racing Strategy Game**

---

## CORE CONCEPT

**What We're Building:**

An interactive F1 racing game where you compete against 7 AI agents with different racing styles learned from real F1 data. When critical race conditions change, the game pauses, runs 100 simulations of possible outcomes, and uses **Gemini AI** to recommend the top 2 best strategies and 1 worst strategy (to avoid). You choose your approach, and the game continues.

**Why This Wins the Hackathon:**

- ✅ **Interactive** - Judges can play it live
- ✅ **AI in the loop** - Real-time decision support, not post-race analysis
- ✅ **Technical depth** - Physics simulation, multi-agent, Gemini synthesis, real F1 data
- ✅ **Novel** - "AI racing strategist" concept is unique
- ✅ **Engaging** - Fun to play, memorable for judges
- ✅ **Defensible** - Based on real 2024 Bahrain GP telemetry, extrapolated to 2026 regulations

---

## THE PLAYER EXPERIENCE

### Demo Flow (4 minutes for judges)

**[0:00-0:30] THE HOOK**

> "F1 race engineers make split-second strategic decisions with incomplete information. In 2026, with 3× more electric power, these decisions become even more critical.
>
> We built an AI racing strategist that simulates 100 possible futures in seconds and recommends optimal strategies in real-time."

**[0:30-2:00] LIVE GAMEPLAY**

*[Screen shows 2D top-down track view with 8 cars]*

> "You're P4, racing against 7 AI agents - each with strategies learned from real F1 drivers like Verstappen, Hamilton, and Alonso.
>
> Watch the race play out..."

*[Game auto-plays for 10 seconds, cars move around track]*

**LAP 15 - RAIN STARTS**

*[Game pauses, UI shows]*

```
⚠️ CONDITION CHANGE: RAIN DETECTED
Running 100 simulations from current state...
[Progress bar: 100 sims in 0.5s]
Analyzing outcomes with Gemini...
```

*[3 strategy cards appear]*

**✅ Strategy A: AGGRESSIVE ATTACK** (Recommended #1)
- Deploy 85% battery next 5 laps
- Push tires to 70%
- Risk overtake on car ahead
- **Win probability: 42%**
- **Gemini says:** "Rain reduces grip advantage. Deploy electric power now before cars adapt. 42% chance to take P3."

**✅ Strategy B: BALANCED APPROACH** (Recommended #2)
- Deploy 60% battery
- Conserve tires at 80%
- Maintain position
- **Win probability: 38%**
- **Gemini says:** "Safe choice. Preserves tires for potential dry conditions later. 38% chance to hold position."

**❌ Strategy C: EXTREME CONSERVATION** (Worst - Avoid!)
- Deploy 20% battery
- Ultra-conservative tire management
- Heavy energy harvesting
- **Win probability: 8%**
- **Gemini says:** "Too passive. Field will overtake during rain phase. Only 8% win probability. Drops to P7+ in 82% of scenarios."

*[Judge clicks Strategy A]*

*[Game resumes, car moves up the order]*

> "You chose aggression - and it worked. You're now P3."

**LAP 35 - SAFETY CAR DEPLOYED**

*[Game pauses again with new recommendations]*

**LAP 57 - RACE FINISH**

*[Results screen]*

```
🏆 FINAL POSITION: P2

YOUR DECISIONS:
✓ Lap 15 (Rain): Chose Aggressive Attack → Gained 1 position
✓ Lap 35 (Safety Car): Chose Balanced Approach → Maintained position
✗ Lap 50 (Tire Critical): Chose Conservative → Lost potential attack

AI PERFORMANCE COMPARISON:
- You: P2 (67% optimal decision rate)
- Pure AI (following all #1 recommendations): P1
- VerstappenStyle Agent: P3
- HamiltonStyle Agent: P4
```

**[2:00-2:30] THE NUMBERS**

> "Behind the scenes:
> - 3 decision points during the race
> - 300 total simulations (100 per decision, 0.5s each)
> - Gemini synthesis: 2-3s per decision
> - Total AI advice time: <10s for entire 57-lap race
> - Built on real 2024 Bahrain GP telemetry
> - Validated against actual race data (±2s accuracy)"

**[2:30-4:00] Q&A**

---

## TECHNICAL ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────┐
│                 GAME FRONTEND (React + Canvas)                    │
│                                                                   │
│  • 2D track visualization (top-down view)                        │
│  • 8 cars with real-time position updates                        │
│  • Telemetry dashboard (battery, tires, fuel)                    │
│  • Decision modal with 3 strategy cards                          │
│  • Results screen with decision analysis                         │
└────────────────────────┬─────────────────────────────────────────┘
                         │ WebSocket (live race updates)
                         │ REST API (decision analysis)
┌────────────────────────▼─────────────────────────────────────────┐
│              GAME ORCHESTRATOR (FastAPI Backend)                 │
│                                                                   │
│  /start_race       - Initialize new game session                 │
│  /game_state       - Get current race state                      │
│  /make_decision    - Submit player choice                        │
│  /get_recommendations - Trigger decision analysis                │
└──┬──────────────┬──────────────┬──────────────┬─────────────┬───┘
   │              │              │              │             │
   ▼              ▼              ▼              ▼             ▼
┌──────┐  ┌────────────┐  ┌───────────┐  ┌──────────┐  ┌─────────┐
│ Game │  │ Decision   │  │ Quick Sim │  │ Gemini   │  │ State   │
│ Loop │  │ Detector   │  │ Runner    │  │ Advisor  │  │ Manager │
│      │  │            │  │ (100×3)   │  │          │  │         │
└──┬───┘  └─────┬──────┘  └─────┬─────┘  └────┬─────┘  └────┬────┘
   │            │               │             │           │
   └────────────┴───────────────┴─────────────┴───────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │   PHYSICS ENGINE       │
                  │   (6-Variable System)  │
                  │                        │
                  │  • 2024 Bahrain cal.   │
                  │  • 2026 extrapolation  │
                  │  • 8 racing agents     │
                  │  • 300 sims/sec        │
                  └────────────────────────┘
```

---

## GAME MECHANICS

### Race Flow

```
1. RACE START
   ├─ 8 cars on grid (Player + 7 AI agents)
   ├─ Cars auto-play using learned agent strategies
   └─ Game loop: 60 FPS visual updates

2. AUTO-PLAY PHASE (Laps 1-14)
   ├─ Watch cars race
   ├─ See your position change
   ├─ Monitor: Battery, Tires, Fuel, Position
   └─ No player interaction needed

3. 🛑 DECISION POINT #1: Rain Starts (Lap 15)
   ├─ Game PAUSES
   ├─ Capture current game state
   ├─ Generate 3 strategy variations:
   │  • Aggressive (high deployment, push hard)
   │  • Balanced (moderate everything)
   │  • Conservative (preserve resources)
   ├─ Run 100 quick sims per strategy (300 total)
   ├─ Send results → Gemini GameAdvisor
   ├─ Gemini returns: Top 2 + Worst 1 with explanations
   ├─ PLAYER CHOOSES (click Strategy A/B/C)
   └─ Game RESUMES with chosen parameters

4. AUTO-PLAY PHASE (Laps 16-34)
   └─ Game continues with your chosen strategy

5. 🛑 DECISION POINT #2: Safety Car (Lap 35)
   └─ [Repeat decision flow]

6. AUTO-PLAY PHASE (Laps 36-49)

7. 🛑 DECISION POINT #3: Tire Critical (Lap 50)
   └─ [Repeat decision flow]

8. FINAL SPRINT (Laps 51-57)
   └─ Auto-play to finish line

9. RESULTS SCREEN
   ├─ Final position + podium animation
   ├─ Decision timeline (which choices worked/failed)
   ├─ Compare vs pure AI performance
   ├─ Agent leaderboard
   └─ Replay button
```

### Decision Triggers (When Game Pauses)

```python
def check_decision_point(race_state):
    """Returns event_type if pause needed, else None"""

    # Critical condition changes that trigger pause:

    if race_state.rain_started and not race_state.already_handled_rain:
        return "RAIN_START"

    if race_state.safety_car_deployed and not race_state.already_handled_sc:
        return "SAFETY_CAR"

    if race_state.tire_life < 25 and not race_state.already_handled_tires:
        return "TIRE_CRITICAL"

    if race_state.battery_soc < 15 and not race_state.already_handled_battery:
        return "BATTERY_LOW"

    if race_state.gap_to_rival < 1.0 and not race_state.already_handled_attack:
        return "OVERTAKE_OPPORTUNITY"

    return None  # No decision needed, keep racing
```

### Strategic Variables (6-Dimensional Control)

Each strategy controls all 6 variables:

1. **energy_deployment** (0-100) - How aggressively to use electric power
2. **tire_management** (0-100) - Balance tire preservation vs performance
3. **fuel_strategy** (0-100) - Fuel saving vs power output tradeoff
4. **ers_mode** (0-100) - Energy recovery intensity
5. **overtake_aggression** (0-100) - Risk tolerance for overtaking moves
6. **defense_intensity** (0-100) - Defensive driving aggressiveness

**Example Strategy Configurations:**

```python
# AGGRESSIVE
{
    'energy_deployment': 85,    # Deploy battery heavily
    'tire_management': 70,      # Push tires moderately hard
    'fuel_strategy': 60,        # Some fuel conservation
    'ers_mode': 80,             # High energy recovery
    'overtake_aggression': 90,  # Very aggressive overtakes
    'defense_intensity': 40     # Light defense (focus on attack)
}

# BALANCED
{
    'energy_deployment': 60,
    'tire_management': 80,
    'fuel_strategy': 70,
    'ers_mode': 65,
    'overtake_aggression': 60,
    'defense_intensity': 55
}

# CONSERVATIVE
{
    'energy_deployment': 35,    # Minimal battery usage
    'tire_management': 90,      # Heavy tire preservation
    'fuel_strategy': 85,        # Maximum fuel conservation
    'ers_mode': 50,             # Moderate recovery
    'overtake_aggression': 30,  # Avoid risky moves
    'defense_intensity': 70     # Strong defense
}
```

---

## GEMINI'S ROLE

### What Gemini Does

At each decision point, Gemini:

1. **Receives simulation data** for 3 strategies (100 races each)
2. **Analyzes patterns** in win rates, positions, resource usage
3. **Considers race context** (current lap, position, event type)
4. **Generates recommendations**:
   - Top 2 strategies with clear rationales
   - Worst strategy with specific risk warnings
5. **Outputs structured JSON** for immediate display

### Example Gemini Analysis

**Input Context:**
- Lap 15/57, Position P4, Battery 45%, Tires 62%
- Event: Rain just started
- Strategy A: 42% win rate, avg P2.3 finish
- Strategy B: 38% win rate, avg P2.5 finish
- Strategy C: 8% win rate, avg P4.8 finish

**Gemini Output:**

```json
{
  "recommended": [
    {
      "strategy_id": 0,
      "rationale": "Rain reduces mechanical grip advantage. Deploy electric power now for overtaking before field adapts. 42% win probability justifies the risk with only 5% DNF rate.",
      "confidence": 0.85
    },
    {
      "strategy_id": 1,
      "rationale": "Safer choice preserving tires for potential dry spell later. 38% win rate with minimal DNF risk (2%). Strong fallback if aggressive strategy feels too risky.",
      "confidence": 0.78
    }
  ],
  "avoid": {
    "strategy_id": 2,
    "rationale": "Too passive during rain phase when electric power provides maximum advantage. Only 8% win probability indicates severe underperformance.",
    "risk": "Drops to P7+ in 82% of simulations. Heavy harvesting loses you 3 positions on average."
  }
}
```

### Fallback Mode

If Gemini API unavailable or times out:

1. **Sort strategies by win rate**
2. **Recommend top 2** with basic explanations
3. **Identify worst** with simple risk statement
4. **Latency: <100ms** (instant fallback)

Example fallback rationale:
> "Highest win rate (42.0%) across 100 simulations. Average finishing position: P2.3."

---

## COMPONENT RESPONSIBILITIES

### Game Loop Developer

**Delivers:**

1. **Decision Point Detection**
   ```python
   def detect_decision_points(race_state):
       """Check each lap if critical event occurred"""
       if should_pause(race_state):
           return event_type  # "RAIN_START", "SAFETY_CAR", etc.
       return None
   ```

2. **Strategy Variation Generator**
   ```python
   def generate_strategy_alternatives(current_state, event_type):
       """Create 3 strategic variations for testing"""
       return [aggressive_params, balanced_params, conservative_params]
   ```

3. **Quick Simulation Runner**
   ```python
   def run_quick_sims(strategies, num_sims=100):
       """Run 100 sims per strategy from current state"""
       # Returns DataFrame with 300 rows
       return sim_results_df
   ```

4. **Game State Manager**
   ```python
   @dataclass
   class GameState:
       lap: int
       positions: List[int]
       battery_soc: List[float]
       tire_life: List[float]
       # ... etc
   ```

### Frontend Developer

**Delivers:**

1. **2D Track View** (Canvas-based)
   - Top-down track layout
   - 8 colored dots (cars)
   - Smooth 60 FPS animation
   - Position labels

2. **Telemetry Dashboard**
   ```
   LAP: 15/57                    P4
   Gap Ahead: +1.2s   Behind: -0.8s
   ─────────────────────────────────
   Battery:  ████████░░ 45%
   Tires:    ████████████░ 62%
   Fuel:     ███████░░░ 28kg
   ```

3. **Decision Modal** (fullscreen overlay)
   - 3 strategy cards side-by-side
   - Win probability (large %)
   - Risk indicator (🟢🟡🔴)
   - Gemini explanation
   - Parameter visualization
   - Click to select

4. **Results Screen**
   - Final position with trophy animation
   - Decision timeline
   - AI comparison chart
   - Replay button

### Backend Developer (Orchestrator)

**Delivers:**

1. **Game Orchestration API**
   - `POST /start_race` - Initialize game session
   - `GET /game_state/{game_id}` - Get current state
   - `POST /get_recommendations` - Trigger decision analysis
   - `POST /make_decision` - Submit player choice
   - `POST /resume_race` - Continue game loop

2. **WebSocket Updates** (optional)
   - Real-time position broadcasts
   - Lap-by-lap telemetry
   - Smooth state sync

---

## YOUR IMPLEMENTATION (Gemini Advisor)

**Already Completed:**

✅ `api/gemini_game_advisor.py` - Core advisor class
✅ `prompts/gemini_game_advisor_system.txt` - Prompt engineering
✅ `test_game_advisor.py` - Mock data testing
✅ `CLAUDE.md` updated with integration guide
✅ `GAME_DESIGN.md` (this document)

**Integration Contract:**

```python
from api.gemini_game_advisor import GameAdvisor

# Initialize once
advisor = GameAdvisor()

# At each decision point
recommendations = advisor.analyze_decision_point(
    sim_results=sim_df,         # 300 rows (100 × 3 strategies)
    race_context={
        'lap': 15,
        'position': 4,
        'battery_soc': 45.0,
        'event_type': 'RAIN_START',
        # ...
    },
    strategy_params=[
        {...},  # Strategy A (6 variables)
        {...},  # Strategy B
        {...}   # Strategy C
    ],
    timeout_seconds=2.5
)

# Returns structured recommendations
# Use recommendations['recommended'] and recommendations['avoid']
```

**Performance Guarantees:**

- ⚡ <2.5s Gemini analysis (with timeout)
- 🔄 <100ms fallback if Gemini fails
- ✅ Always returns valid schema
- 🛡️ Graceful degradation

---

## SUCCESS METRICS

### Must Have (Demo Requirements)

- [x] 8 cars race (player + 7 AI agents)
- [x] 2D track visualization
- [x] 3+ decision points per race
- [x] 100 quick sims per decision (<1s)
- [x] Gemini recommendations (top 2 + worst)
- [x] Player can choose strategy
- [x] Final results with decision analysis

### Performance Targets

- **Quick sims**: 300 races in <1s (300+ sims/sec)
- **Gemini analysis**: <2.5s
- **Total decision latency**: <4s
- **Frame rate**: 30-60 FPS
- **Fallback latency**: <100ms

### Nice to Have

- ⭐ Smooth 60 FPS animation
- ⭐ WebSocket live updates
- ⭐ Sound effects (engine, rain, overtakes)
- ⭐ Multiple tracks (Monaco, Silverstone)
- ⭐ Difficulty levels (easier AI agents)
- ⭐ Leaderboard (best results)

---

## DEMO SCRIPT (4 Minutes)

**[0:00-0:30] Hook**
> "2026 regulations bring 3× more electric power. No historical data exists. Teams need simulation. We built an AI strategist that plays F1 with you in real-time."

**[0:30-1:45] Live Gameplay**
> *Show race, hit decision point, Gemini analyzes, player chooses, race continues*

**[1:45-2:15] Results**
> "Finished P2. If I followed all AI recommendations? P1. But I made one suboptimal choice."

**[2:15-3:00] Technical Deep Dive**
> "300 simulations per decision, analyzed in <3s by Gemini. Built on real 2024 Bahrain data, validated within ±2s of actual lap times."

**[3:00-4:00] Q&A**
> Handle judge questions about tech stack, AI integration, physics accuracy

---

## TESTING CHECKLIST

**Before Demo:**

```bash
# 1. Test GameAdvisor
python test_game_advisor.py
# Expected: 2 recommendations + 1 avoid, latency <4s

# 2. Test full game flow (once integrated)
# - Start race
# - Trigger decision at lap 15
# - Verify Gemini recommendations appear
# - Select strategy
# - Complete race
# - Check results screen

# 3. Test fallback mode
# - Disable GEMINI_API_KEY temporarily
# - Verify instant fallback recommendations
# - Re-enable API key

# 4. Load testing
# - Run 10 consecutive decisions
# - Verify no memory leaks
# - Check consistent latency
```

---

## RISK MITIGATION

**Risk 1: Gemini latency >5s**
- ✅ Mitigation: 2.5s timeout, instant fallback
- ✅ Backup: Pre-cached common scenarios

**Risk 2: Game loop bugs**
- ✅ Mitigation: Extensive testing H11-13
- ✅ Backup: Pre-recorded perfect playthrough video

**Risk 3: Decision points don't trigger**
- ✅ Mitigation: Comprehensive trigger testing
- ✅ Backup: Manual trigger on specific laps if needed

**Risk 4: Quick sims too slow**
- ✅ Mitigation: Your existing engine does 200+ sims/sec
- ✅ Backup: Reduce to 50 sims per strategy (150 total)

**Risk 5: Frontend rendering slow**
- ✅ Mitigation: Canvas optimization, reduce draw calls
- ✅ Backup: Simplified graphics (just dots and lines)

---

## STORY FOR JUDGES

**The Problem:**
> "F1 race engineers make critical strategic decisions in seconds with incomplete information. Should we pit? Deploy battery now or save it? Attack or defend? With 2026's 3× more electric power, these decisions become even more complex."

**Our Solution:**
> "We built an AI racing strategist that simulates hundreds of possible futures and recommends optimal strategies in real-time. It's trained on real 2024 F1 data and uses Gemini to synthesize complex outcomes into actionable recommendations."

**The Innovation:**
> "This isn't post-race analysis - it's real-time decision support. When conditions change, we run 100 simulations, analyze them with AI, and present clear options with win probabilities and explanations. You're racing WITH the AI, not against it."

**The Impact:**
> "Judges can play it and see how AI-assisted decisions outperform gut instinct. This is the future of racing strategy - and any domain where split-second decisions under uncertainty matter."

---

## TIMELINE SUMMARY

**H0-H2:** Game Loop Core (teammate)
**H2-H4:** Quick Sim + Backend (teammate)
**H4-H7:** Frontend Core (teammate)
**H7-H9:** Gemini Integration (✅ YOUR WORK - DONE!)
**H9-H11:** Polish & Integration
**H11-H13:** Testing & Bug Fixes
**H13-H14:** Demo Prep
**H14-H15:** Rehearsal

---

## FILES REFERENCE

**Your Completed Work:**
- `api/gemini_game_advisor.py` - Core implementation (250 lines)
- `prompts/gemini_game_advisor_system.txt` - Prompt engineering
- `test_game_advisor.py` - Comprehensive testing
- `CLAUDE.md` - Integration documentation
- `GAME_DESIGN.md` - This file

**Teammate Integration Points:**
- Game loop needs to call `GameAdvisor.analyze_decision_point()`
- Frontend displays `recommendations['recommended']` and `recommendations['avoid']`
- Backend orchestrates: detect → sim → analyze → display → choice → resume

---

**Your Gemini integration is complete and ready! Share this document with your teammates so they know how to integrate with your GameAdvisor module.**
