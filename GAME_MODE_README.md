# Interactive Game Mode - Implementation Guide

## Overview

The interactive game mode allows players to race against 7 AI opponents on the real Bahrain International Circuit. During the race, the game pauses at critical decision points (rain, safety car, tire degradation, etc.) and uses Gemini AI to analyze 3 strategic alternatives, providing recommendations to the player.

---

## Architecture

### Backend Components

**Created:**
1. `api/game_sessions.py` - Game session management with thread-safe state tracking
2. `sim/game_loop.py` - Lap-by-lap race orchestrator with decision point detection
3. `api/game_types.py` - Pydantic models for WebSocket message validation
4. `api/main.py` - WebSocket endpoint `/ws/game/{session_id}` (added to existing API)

**Existing (Reused):**
- `sim/quick_sim.py` - Fast probabilistic simulator (~1000 sims/sec)
- `api/gemini_game_advisor.py` - Gemini-powered strategy analysis

### Frontend Components

**Created:**
1. `web/components/GameUI/DecisionModal.tsx` - Strategy selection modal (3 cards with Gemini analysis)
2. `web/components/GameUI/RaceHUD.tsx` - Real-time telemetry display (battery, tires, fuel)
3. `web/components/GameUI/GameController.tsx` - Main game controller with WebSocket management
4. `web/hooks/useWebSocket.ts` - WebSocket hook with auto-reconnection
5. `web/app/game/page.tsx` - Game mode route

**Enhanced:**
- `web/components/BentoBoxes/Box1_RaceTrack.tsx` - Now supports 8 cars with position badges and driver names

---

## Quick Start

### 1. Backend Setup

```bash
# Install dependencies (if not already installed)
pip install fastapi websockets python-dotenv google-generativeai pandas numpy

# Set Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Start backend server
cd /Users/prajit/Desktop/projects/Gand
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
# Install dependencies (if not already installed)
cd web
npm install framer-motion

# Start development server
npm run dev
```

### 3. Play the Game

1. Open browser: `http://localhost:3000/game`
2. Click **START RACE**
3. Watch cars race around Bahrain track
4. When decision point triggers:
   - 3 strategy cards appear
   - Gemini analyzes each strategy
   - 30-second countdown timer
   - Press `1`, `2`, or `3` (or click a card)
5. Race continues with your chosen strategy
6. Repeat 3-5 times per race
7. See final position at race end

---

## Decision Point Triggers

The game pauses for player decisions at these events:

| Event | Trigger Condition | Frequency |
|-------|------------------|-----------|
| **Rain Start** | Rain begins (scenario.rain_lap) | Once per race |
| **Safety Car** | Safety car deployed (scenario.safety_car_lap) | Once per race |
| **Battery Low** | Battery < 15% | Once |
| **Tire Critical** | Tire life < 25% | Once |
| **Strategic Checkpoint** | Every 12 laps | 3-4 times per race |

**Total decision points per race:** 3-5 (depending on scenario events)

---

## Message Protocol (WebSocket)

### Client → Server

**START_GAME:**
```json
{
  "type": "START_GAME",
  "player_name": "Player",
  "total_laps": 57,
  "rain_lap": 25,  // optional
  "safety_car_lap": 30  // optional
}
```

**SELECT_STRATEGY:**
```json
{
  "type": "SELECT_STRATEGY",
  "strategy_id": 0  // 0=Aggressive, 1=Balanced, 2=Conservative
}
```

### Server → Client

**RACE_STARTED:**
```json
{
  "type": "RACE_STARTED",
  "session_id": "abc123",
  "total_laps": 57,
  "player": { "position": 1, "battery_soc": 100, ... },
  "opponents": [ ... 7 opponents ... ]
}
```

**LAP_UPDATE:** (every 0.5 seconds)
```json
{
  "type": "LAP_UPDATE",
  "lap": 15,
  "player": { "position": 4, "battery_soc": 68.2, ... },
  "opponents": [ ... ],
  "is_raining": false,
  "safety_car_active": false
}
```

**DECISION_POINT:**
```json
{
  "type": "DECISION_POINT",
  "event_type": "RAIN_START",
  "lap": 25,
  "position": 4,
  "battery_soc": 65.0,
  "tire_life": 58.0,
  "fuel_remaining": 42.0,
  "recommended": [
    {
      "strategy_id": 0,
      "strategy_name": "Aggressive",
      "win_rate": 42.0,
      "rationale": "Deploy electric power now for speed advantage in rain...",
      "confidence": 0.85,
      "strategy_params": { ... }
    },
    { ... second recommendation ... }
  ],
  "avoid": {
    "strategy_id": 2,
    "strategy_name": "Conservative",
    "win_rate": 8.0,
    "rationale": "Too passive in rain conditions...",
    "risk": "Will lose 2-3 positions..."
  },
  "latency_ms": 1850,
  "used_fallback": false
}
```

**RACE_COMPLETE:**
```json
{
  "type": "RACE_COMPLETE",
  "final_position": 3,
  "player": { ... },
  "opponents": [ ... ],
  "decision_count": 4,
  "race_summary": { ... }
}
```

---

## Performance Notes

### Current Configuration

**Simulation Engine:** `sim/quick_sim.py` (probabilistic)
- **Speed:** ~1000 simulations/second
- **Decision latency:** <2 seconds for 300 sims (100 per strategy × 3)
- **Accuracy:** Good approximation of race outcomes

**Gemini Analysis:** `api/gemini_game_advisor.py`
- **Latency:** <2.5 seconds
- **Total decision time:** ~4 seconds (acceptable with good UX)

### Performance Optimization Options

**Option 1: Switch to Realistic Physics** (if current performance is good)

```python
# In sim/game_loop.py, replace:
from sim.quick_sim import run_quick_sims_from_state

# With:
from sim.decision_sim import run_decision_simulations

# Pros: Uses real 2024-calibrated physics, more accurate
# Cons: ~100 sims/sec (slower, 3-6 second latency)
```

**Option 2: Reduce Simulation Count** (if latency is too high)

```python
# In sim/game_loop.py, line ~275:
sim_results = run_quick_sims_from_state(
    current_state,
    strategy_params,
    num_sims_per_strategy=50  # Reduce from 100 to 50
)

# Reduces total sims from 300 to 150 (~1 second latency)
```

**Option 3: Pre-cache Common Decision Points**

```python
# Cache frequent scenarios (rain, battery low, tire critical)
# Load pre-computed simulations on game start
# Instant recommendations for cached scenarios
```

### Benchmark Script

To test different configurations:

```bash
# Test quick_sim performance
python -c "
from sim.quick_sim import run_quick_sims_from_state, RaceState
from sim.decision_sim import generate_strategy_variations
import time

state = RaceState(lap=15, total_laps=57, position=4, battery_soc=45, tire_life=60, fuel_remaining=70)
strategies = generate_strategy_variations(state, 'RAIN_START')

start = time.time()
results = run_quick_sims_from_state(state, strategies, num_sims_per_strategy=100)
elapsed = time.time() - start

print(f'300 quick sims: {elapsed:.2f}s ({300/elapsed:.0f} sims/sec)')
"

# Test decision_sim performance (realistic physics)
python -c "
from sim.decision_sim import run_decision_simulations
import time

start = time.time()
results = run_decision_simulations(
    current_lap=15,
    current_position=4,
    current_battery_soc=45,
    current_tire_life=60,
    current_fuel=70,
    strategies=[
        {'energy_deployment': 85, 'tire_management': 70, ...},
        {'energy_deployment': 60, 'tire_management': 80, ...},
        {'energy_deployment': 35, 'tire_management': 90, ...}
    ],
    num_sims_per_strategy=100
)
elapsed = time.time() - start

print(f'300 realistic sims: {elapsed:.2f}s ({300/elapsed:.0f} sims/sec)')
"
```

**Performance Targets:**
- ✅ Quick sims: >500 sims/sec (< 1s for 300 sims)
- ⚠️ Realistic sims: >100 sims/sec (<3s for 300 sims)
- ✅ Total decision latency: <4s (with Gemini)

---

## UI Features

### Decision Modal

- **3 Strategy Cards:** Aggressive, Balanced, Conservative
- **Gemini Analysis:** Win rate %, rationale, confidence scores
- **30-Second Timer:** Auto-selects best strategy at 0s
- **Keyboard Shortcuts:** Press `1`, `2`, or `3` to select
- **Visual Feedback:** Green border for recommended, red for avoid
- **Parameter Display:** Shows all 6 strategy variables

### Race HUD

- **Current Lap:** X / 57
- **Position:** P1-P8 with large display
- **Battery Gauge:** Color-coded (green/yellow/red)
- **Tire Life Gauge:** With degradation warnings
- **Fuel Remaining:** Consumption tracking
- **Event Indicators:** Rain icon, safety car icon
- **Warnings:** Critical battery, tire wear, fuel low

### Race Track

- **8 Cars:** Player (blue) + 7 AI opponents (white)
- **Real Bahrain Circuit:** GeoJSON coordinates from 2024 GP
- **Position Badges:** P1, P2, etc. above each car
- **Driver Names:** Below each car
- **Smooth Animation:** 20 FPS with realistic cornering

---

## Testing

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to WebSocket
- [ ] Click "START RACE" initiates game
- [ ] Cars animate smoothly around track
- [ ] Decision point triggers (rain/battery/checkpoint)
- [ ] Decision modal shows 3 strategies
- [ ] Gemini recommendations appear correctly
- [ ] Keyboard shortcuts (1/2/3) work
- [ ] Race resumes after strategy selection
- [ ] Multiple decision points work
- [ ] Race completes and shows final position
- [ ] "RACE AGAIN" button restarts game

### Automated Testing

```bash
# Test game advisor integration
cd /Users/prajit/Desktop/projects/Gand
python tests/test_game_decision_flow.py

# Expected output:
# ✅ Decision flow completed in <4000ms
# ✅ Got 2 recommended strategies
# ✅ Got 1 avoid strategy
# ✅ All strategies have valid parameters
```

---

## Troubleshooting

### WebSocket Connection Failed

**Problem:** Frontend shows "DISCONNECTED"

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check WebSocket endpoint: `wscat -c ws://localhost:8000/ws/game/test`
3. Check CORS settings in `api/main.py`

### Decision Modal Never Appears

**Problem:** Game runs but no decision points trigger

**Solution:**
1. Check `sim/game_loop.py` line ~234 (`check_for_decision_point`)
2. Verify events are configured: rain_lap, safety_car_lap not null
3. Add debug logging: `print(f"Checking decision: lap={lap}, battery={battery}")`

### Gemini Recommendations Slow

**Problem:** Decision latency > 5 seconds

**Solution:**
1. Check Gemini API key is set: `echo $GEMINI_API_KEY`
2. Reduce timeout in `sim/game_loop.py`: `timeout_seconds=1.5` (uses fallback faster)
3. Check network latency to Gemini API

### Cars Not Moving on Track

**Problem:** Track shows but cars are static

**Solution:**
1. Check lap updates are being received in browser console
2. Verify `opponents` array has lap_progress values (0-1)
3. Check `Box1_RaceTrack.tsx` animation interval (line ~193)

---

## Next Steps / Enhancements

### Completed ✅
- ✅ Backend game loop with WebSocket
- ✅ Decision point detection (5 trigger types)
- ✅ Gemini integration for strategy analysis
- ✅ Frontend UI (track, HUD, decision modal)
- ✅ 8-car visualization with real Bahrain circuit
- ✅ Keyboard shortcuts and auto-selection
- ✅ Race completion and restart flow

### Future Enhancements 🚀

1. **Multiplayer Mode**
   - Multiple players racing together
   - Shared decision points or individual strategies
   - Leaderboard and race replay

2. **More Tracks**
   - Monaco, Silverstone, Monza circuits
   - Track selection UI
   - Track-specific strategies

3. **Career Mode**
   - Championship progression
   - Unlock faster AI opponents
   - Strategy playbook persistence

4. **Advanced Telemetry**
   - Sector times with color coding
   - Throttle/brake/DRS indicators
   - Live lap time comparison

5. **Pit Stop Strategy**
   - Manual pit stop decisions
   - Tire compound selection
   - Fuel load optimization

6. **Replay System**
   - Save race replays
   - Playback controls
   - Decision history review

---

## File Structure

```
/Users/prajit/Desktop/projects/Gand/

Backend:
├── api/
│   ├── main.py              [MODIFIED] Added WebSocket endpoint
│   ├── game_sessions.py     [NEW] Session management
│   └── game_types.py        [NEW] Message type definitions
├── sim/
│   ├── game_loop.py         [NEW] Race orchestrator
│   ├── quick_sim.py         [EXISTS] Fast simulator
│   └── decision_sim.py      [EXISTS] Realistic simulator

Frontend:
├── web/
│   ├── components/
│   │   ├── BentoBoxes/
│   │   │   └── Box1_RaceTrack.tsx    [MODIFIED] 8-car support
│   │   └── GameUI/
│   │       ├── DecisionModal.tsx     [NEW] Strategy selection
│   │       ├── RaceHUD.tsx           [NEW] Telemetry display
│   │       └── GameController.tsx    [NEW] Main controller
│   ├── hooks/
│   │   └── useWebSocket.ts           [NEW] WebSocket hook
│   └── app/
│       └── game/
│           └── page.tsx              [NEW] Game route
```

---

## Credits

- **Real Bahrain Circuit Data:** GeoJSON from 2024 Bahrain GP
- **AI Opponents:** Learned from Verstappen, Hamilton, Alonso telemetry (2024)
- **Strategy Analysis:** Powered by Google Gemini 1.5 Flash
- **Physics Engine:** Calibrated from FastF1 2024 Bahrain data

---

## Support

For issues or questions:
1. Check console logs (browser & backend)
2. Review WebSocket messages in Network tab
3. Test individual components in isolation
4. Run automated tests: `python tests/test_game_decision_flow.py`
