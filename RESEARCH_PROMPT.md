# F1 2026 Racing Simulator - Critical Issues & Architecture Research

## EXECUTIVE SUMMARY

We have a **real-time F1 racing game simulator** built with:
- **Backend**: FastAPI + WebSocket (Python, asyncio)
- **Frontend**: Next.js + React + Framer Motion (TypeScript)
- **Physics**: Custom 6-variable strategy system with real 2024 Bahrain GP calibration

**Current Critical Issues:**
1. ✅ **PARTIALLY FIXED** - After Gemini strategy selection, movement stops or behaves erratically
2. ❌ **CRITICAL** - Cars stay stuck at start area while lap counter keeps incrementing
3. ❌ **CRITICAL** - Player car (blue dot) randomly falls behind then suddenly jumps ahead
4. ✅ **FIXED** - Speed was hardcoded (now uses backend calculations)
5. ✅ **FIXED** - Strategy recommendations showing randomly (now only on decision points)
6. ✅ **ATTEMPTED** - lap_progress calculation changed to cycle 0→1 per lap

**What We Need:**
1. **Root cause analysis** of why cars don't move correctly around the track
2. **Fix** for lap_progress/cumulative_time synchronization
3. **Architecture review** of pause/resume mechanism
4. **Suggestions** for making demo more impressive for judges (visual clarity, performance metrics, etc.)

---

## SYSTEM ARCHITECTURE

### High-Level Flow

```
┌────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                       │
│  - BentoLayout.tsx: Main UI with race track + telemetry    │
│  - Box1_RaceTrack.tsx: SVG track with car animations       │
│  - useGameSession.ts: WebSocket state management           │
│  - useWebSocket.ts: WebSocket connection handler           │
└──────────────────┬─────────────────────────────────────────┘
                   │ WebSocket (ws://localhost:8000/ws/game/{id})
                   │ Messages: START_GAME, SELECT_STRATEGY, LAP_UPDATE
┌──────────────────▼─────────────────────────────────────────┐
│                  BACKEND (FastAPI)                          │
│  - api/main.py: WebSocket endpoint                          │
│  - api/game_sessions.py: GameState, PlayerState, OpponentState │
│  - sim/game_loop.py: GameLoopOrchestrator                   │
│  - api/gemini_game_advisor.py: AI recommendations           │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow (per lap)

```
1. run_race_loop() (api/main.py:437)
   └─> while not complete:
       ├─> orchestrator.advance_lap() (sim/game_loop.py:44)
       │   ├─> _simulate_player_lap() → calculates lap_time, updates cumulative_time
       │   ├─> _simulate_opponent_laps() → same for 7 AI opponents
       │   ├─> _update_race_positions() → sorts by cumulative_time
       │   └─> _update_visualization_metrics() → calculates speed, gap_to_leader, lap_progress
       │
       ├─> send LAP_UPDATE via WebSocket (includes player + opponents state)
       │
       ├─> check_for_decision_point() → rain, safety car, battery low, etc.
       │   └─> if triggered:
       │       ├─> get_decision_recommendations() → Gemini AI analysis
       │       ├─> send DECISION_POINT message
       │       ├─> pause_event.clear() → PAUSE RACE LOOP
       │       └─> await pause_event.wait() → WAIT FOR STRATEGY SELECTION
       │
       └─> await asyncio.sleep(0.1) → 10 updates/second
```

### Key Timing Parameters

- **Base Lap Time**: 90 seconds (realistic F1)
- **LAP_TIME_MULTIPLIER**: 5.0 (demo speed: 90s / 5.0 = 18s per lap)
- **Update Frequency**: 0.1s sleep = 10 Hz = ~180 updates per lap
- **Frontend Interpolation**: 60 fps requestAnimationFrame between backend updates

---

## CRITICAL CODE SECTIONS

### 1. lap_progress Calculation (sim/game_loop.py:233-265)

**THIS IS THE MOST LIKELY CULPRIT**

```python
def _update_visualization_metrics(self, current_lap: int):
    """
    Calculate speed, gap_to_leader, and lap_progress for smooth visualization.

    Speed: Derived from lap_time (faster lap = higher speed)
    Gap to leader: Time difference from leader's cumulative time
    Lap progress: Position within current lap (0-1 per lap for smooth track animation)
    """
    # Find the race leader (lowest cumulative time)
    all_racers = [self.game_state.player] + self.game_state.opponents
    leader_time = min(racer.cumulative_time for racer in all_racers)

    # Update player metrics
    player = self.game_state.player
    player.speed = self._calculate_speed(player.lap_time)
    player.gap_to_leader = player.cumulative_time - leader_time

    # Progress WITHIN current lap (cycles 0→1 each lap for smooth track animation)
    # This shows position around the circuit, resetting each lap
    expected_lap_time = self.base_lap_time / self.lap_time_multiplier  # 90 / 5.0 = 18s
    lap_start_time = (current_lap - 1) * expected_lap_time
    elapsed_in_current_lap = player.cumulative_time - lap_start_time
    player.lap_progress = min(1.0, max(0.0, elapsed_in_current_lap / expected_lap_time))

    # Update opponent metrics
    for opponent in self.game_state.opponents:
        opponent.speed = self._calculate_speed(opponent.last_lap_time)
        opponent.gap_to_leader = opponent.cumulative_time - leader_time

        # Same calculation - progress within current lap
        elapsed_in_current_lap_opp = opponent.cumulative_time - lap_start_time
        opponent.lap_progress = min(1.0, max(0.0, elapsed_in_current_lap_opp / expected_lap_time))
```

**PROBLEM HYPOTHESIS:**
- `expected_lap_time` is constant (18s), but actual `lap_time` varies per car (different strategies)
- `lap_start_time = (current_lap - 1) * 18` assumes all cars complete laps at exactly 18s
- Reality: Cars have different cumulative_time values (some faster/slower)
- **Result**: `elapsed_in_current_lap` can be negative or > expected_lap_time
- **Visual symptom**: Cars stuck at start (0.0) or finish (1.0), or jumping erratically

### 2. Lap Time Calculation (sim/game_loop.py:91-141)

```python
def _simulate_player_lap(self) -> Dict:
    """Simulate one lap for player"""
    player = self.game_state.player

    # Get current strategy parameters
    energy = player.energy_deployment
    tire_mgmt = player.tire_management
    fuel_strat = player.fuel_strategy
    ers = player.ers_mode

    # Battery dynamics
    battery_drain = (energy / 100) * 0.8
    battery_gain = (ers / 100) * 0.6
    player.battery_soc = max(0, min(100, player.battery_soc - battery_drain + battery_gain))

    # Tire degradation
    tire_wear = (100 - tire_mgmt) / 100 * 1.5
    player.tire_life = max(0, player.tire_life - tire_wear)

    # Fuel consumption
    fuel_burn = (100 - fuel_strat) / 100 * 0.5
    player.fuel_remaining = max(0, player.fuel_remaining - fuel_burn)

    # Lap time calculation (base: 90s)
    lap_time = 90.0
    lap_time -= (energy / 100) * 0.3  # Energy gives speed
    lap_time += (100 - tire_mgmt) / 100 * 0.2  # Poor tire mgmt slows down
    if player.battery_soc < 20:
        lap_time += (20 - player.battery_soc) * 0.02  # Battery penalty
    if self.game_state.is_raining:
        lap_time += 2.0  # Rain penalty
    if self.game_state.safety_car_active:
        lap_time += 30.0  # Safety car neutralizes pace

    # Add some randomness
    lap_time += np.random.uniform(-0.5, 0.5)

    # Apply LAP_TIME_MULTIPLIER for demo speed (e.g., 90s / 5.0 = 18s)
    lap_time = lap_time / self.lap_time_multiplier

    player.lap_time = lap_time
    player.cumulative_time += lap_time  # CRITICAL: This is the "ground truth" for position

    return {...}
```

**OBSERVED BEHAVIOR:**
- Player lap time: 17.5s - 18.5s (varies by strategy)
- Opponents: Similar range but each different
- **cumulative_time** is the authoritative source of truth
- **lap_progress** tries to visualize this but calculation is flawed

### 3. Pause/Resume Mechanism (api/main.py:437-524)

```python
async def run_race_loop(websocket: WebSocket, orchestrator: GameLoopOrchestrator, game_state: GameState):
    """
    Run the race lap-by-lap, pausing for decision points.
    """
    while not game_state.is_complete and not game_state.is_paused:
        # Advance one lap
        lap_result = orchestrator.advance_lap()

        # Send lap update to client
        await websocket.send_json({
            'type': 'LAP_UPDATE',
            'lap': lap_result['lap'],
            'player': lap_result.get('player'),
            'opponents': lap_result.get('opponents', []),
            ...
        })

        # Check for decision points
        decision_check = orchestrator.check_for_decision_point()

        if decision_check.get('triggered'):
            # Get recommendations from GameAdvisor
            recommendations = await orchestrator.get_decision_recommendations(...)

            # Send decision point to client
            await websocket.send_json({
                'type': 'DECISION_POINT',
                ...
            })

            # Pause race loop and wait for player to select strategy
            game_state.pause_event.clear()  # Pause
            await game_state.pause_event.wait()  # Wait for SELECT_STRATEGY
            # Strategy selected! Loop continues seamlessly

        # Pacing: Wait 100ms between updates for smooth visualization
        await asyncio.sleep(0.1)
```

**ISSUES ENCOUNTERED:**
1. ❌ **Original**: Used `break` → race loop exited completely, never resumed
2. ✅ **Fixed**: Use asyncio.Event pause/resume → works, but might have timing issues
3. ❓ **Concern**: Does cumulative_time continue advancing during pause? No, it doesn't (lap only advances when advance_lap() is called)

### 4. Frontend Interpolation (web/components/BentoBoxes/Box1_RaceTrack.tsx:210-266)

```typescript
// 60fps interpolation loop using requestAnimationFrame
useEffect(() => {
  const animate = () => {
    const now = Date.now();
    const timeSinceUpdate = now - lastUpdateTimeRef.current;

    // Calculate interpolation factor (0 to 1) based on expected update interval
    const t = Math.min(timeSinceUpdate / updateIntervalRef.current, 1.0);

    // Interpolate between previous and current states
    const interpolated = currentCarsRef.current.map((currentCar, index) => {
      const previousCar = previousCarsRef.current[index] || currentCar;

      // Smooth interpolation of lap progress
      let interpolatedProgress = previousCar.lapProgress + (currentCar.lapProgress - previousCar.lapProgress) * t;

      // Handle lap wrap-around (1.0 → 0.0)
      if (Math.abs(currentCar.lapProgress - previousCar.lapProgress) > 0.5) {
        // Likely a lap completion
        if (currentCar.lapProgress < previousCar.lapProgress) {
          interpolatedProgress = previousCar.lapProgress + (1.0 + currentCar.lapProgress - previousCar.lapProgress) * t;
          if (interpolatedProgress >= 1.0) interpolatedProgress -= 1.0;
        }
      }

      // Interpolate speed
      const interpolatedSpeed = Math.round(
        previousCar.speed + (currentCar.speed - previousCar.speed) * t
      );

      return {
        ...currentCar,
        lapProgress: interpolatedProgress,
        speed: interpolatedSpeed,
      };
    });

    setInterpolatedCars(interpolated);
    animationFrameRef.current = requestAnimationFrame(animate);
  };

  animationFrameRef.current = requestAnimationFrame(animate);

  return () => {
    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };
}, []); // Only set up once
```

**FRONTEND LOGIC:**
- Receives lap_progress from backend every ~100ms (10 Hz)
- Interpolates to 60 fps for smooth animation
- Handles lap wrap-around (1.0 → 0.0) specially
- **Problem**: If backend sends bad lap_progress, frontend can't fix it

---

## SYMPTOM ANALYSIS

### Symptom 1: Cars Stuck at Start Area
**What we see:**
- Lap counter: 15/57, 16/57, 17/57... (incrementing correctly)
- Car positions: All clustered at 0-5% of track (start area)
- lap_progress values: 0.0 - 0.05 (not cycling to 1.0)

**Debug logs would show:**
```
[LAP 15] Player: pos=3, lap_progress=0.0234, cumulative=270.5s
[LAP 16] Player: pos=3, lap_progress=0.0289, cumulative=288.2s
[LAP 17] Player: pos=3, lap_progress=0.0312, cumulative=306.1s
```

**Hypothesis:**
- `expected_lap_time = 18s` (constant)
- `lap_start_time = (17 - 1) * 18 = 288s`
- `elapsed_in_current_lap = 306.1 - 288 = 18.1s`
- `lap_progress = 18.1 / 18 = 1.005 → clamped to 1.0`
- **BUT** if calculation is wrong, it might be:
- `lap_start_time = 0` (always?) → `306.1 / 18 = 17.0 → clamped to 1.0`
- **OR** cumulative_time is not advancing properly

### Symptom 2: Player Car Jumping Around
**What we see:**
- Player car (blue) at 0.2 lap_progress
- Suddenly jumps to 0.8 lap_progress
- Then back to 0.1

**Hypothesis:**
- lap_progress calculation uses `current_lap` from orchestrator
- But `current_lap` might increment before cumulative_time is updated?
- **OR** pause/resume causes timing desync
- **OR** strategy selection changes lap_time but lap_progress calculation doesn't account for it

---

## PREVIOUS FIX ATTEMPTS

### Attempt 1: Fixed Speed Calculation ✅
**Problem**: Frontend recalculated speed with hardcoded formula
**Fix**: Use backend-calculated speed from lap_time
**Result**: Speed now reflects actual performance (200-350 km/h)

### Attempt 2: Fixed lap_progress to Cycle Per Lap ✅ (but broken?)
**Problem**: lap_progress was total race progress (0→1 over 57 laps)
**Fix**: Calculate progress within current lap
**Result**: Cars should cycle 0→1 each lap, but they don't (stuck at start)

### Attempt 3: Fixed Pause/Resume with asyncio.Event ✅
**Problem**: `break` statement exited race loop completely
**Fix**: Use pause_event.clear() / pause_event.wait() / pause_event.set()
**Result**: Loop continues after strategy selection, but movement still broken

### Attempt 4: Hide Strategy Recs Until Decision Point ✅
**Problem**: Strategy cards always visible
**Fix**: `{decisionPoint && <div>...</div>}`
**Result**: UI now clean, only shows during rain/safety car/critical events

---

## WHAT WE NEED FROM YOU

### 1. Root Cause Analysis
**Please analyze the lap_progress calculation and identify:**
- Why cars stay at start area when lap counter advances
- Why player car jumps around randomly
- Is the formula in `_update_visualization_metrics()` correct?
- Should we use a different approach (e.g., based on cumulative_time ratios)?

### 2. Proposed Fix
**Provide corrected code for:**
- `_update_visualization_metrics()` in sim/game_loop.py
- Any related changes needed in frontend or WebSocket message structure

### 3. Architecture Review
**Answer these questions:**
- Is the pause/resume mechanism sound? (asyncio.Event)
- Should cumulative_time be paused during decision points?
- Is 0.1s update interval too fast/slow?
- Should frontend interpolation work differently?

### 4. Demo Enhancement Suggestions
**Help us make this more impressive for judges:**
- What visual indicators would make strategy differences more obvious?
- How to show AI discovery in action?
- Performance metrics to highlight (latency, accuracy, etc.)?
- Any "wow factor" features we should add?

---

## FULL CODE LISTINGS

### sim/game_loop.py (Lines 233-280 - CRITICAL SECTION)
```python
def _update_visualization_metrics(self, current_lap: int):
    """
    Calculate speed, gap_to_leader, and lap_progress for smooth visualization.

    Speed: Derived from lap_time (faster lap = higher speed)
    Gap to leader: Time difference from leader's cumulative time
    Lap progress: Position within current lap (0-1 per lap for smooth track animation)
    """
    # Find the race leader (lowest cumulative time)
    all_racers = [self.game_state.player] + self.game_state.opponents
    leader_time = min(racer.cumulative_time for racer in all_racers)

    # Update player metrics
    player = self.game_state.player
    player.speed = self._calculate_speed(player.lap_time)
    player.gap_to_leader = player.cumulative_time - leader_time

    # Progress WITHIN current lap (cycles 0→1 each lap for smooth track animation)
    # This shows position around the circuit, resetting each lap
    expected_lap_time = self.base_lap_time / self.lap_time_multiplier
    lap_start_time = (current_lap - 1) * expected_lap_time
    elapsed_in_current_lap = player.cumulative_time - lap_start_time
    player.lap_progress = min(1.0, max(0.0, elapsed_in_current_lap / expected_lap_time))

    # Update opponent metrics
    for opponent in self.game_state.opponents:
        opponent.speed = self._calculate_speed(opponent.last_lap_time)
        opponent.gap_to_leader = opponent.cumulative_time - leader_time

        # Same calculation - progress within current lap
        elapsed_in_current_lap_opp = opponent.cumulative_time - lap_start_time
        opponent.lap_progress = min(1.0, max(0.0, elapsed_in_current_lap_opp / expected_lap_time))

def _calculate_speed(self, lap_time: float) -> float:
    """
    Convert lap_time to approximate speed in km/h for visualization.

    Faster laps = higher speed.
    Base: 90s lap = 300 km/h
    Every second faster/slower = ~10 km/h change
    """
    base_speed = 300.0  # km/h at 90s lap
    speed_delta = (90.0 - lap_time) * 10.0  # Each second difference = 10 km/h
    speed = base_speed + speed_delta

    # Clamp to realistic F1 speeds (200-350 km/h)
    return max(200.0, min(350.0, speed))
```

### api/main.py (Lines 437-524 - Race Loop)
```python
async def run_race_loop(websocket: WebSocket, orchestrator: GameLoopOrchestrator, game_state: GameState):
    """
    Run the race lap-by-lap, pausing for decision points.
    """
    while not game_state.is_complete and not game_state.is_paused:
        # Advance one lap
        lap_result = orchestrator.advance_lap()

        # Update session
        session_manager.update_session(game_state.session_id, game_state)

        # Send lap update to client (includes speed, gap_to_leader, lap_progress from game_loop)
        await websocket.send_json({
            'type': 'LAP_UPDATE',
            'lap': lap_result['lap'],
            'player': lap_result.get('player'),  # Now includes: speed, gap_to_leader, all telemetry
            'opponents': lap_result.get('opponents', []),  # Now includes: speed, gap_to_leader, lap_progress
            'is_raining': lap_result.get('is_raining', False),
            'safety_car_active': lap_result.get('safety_car_active', False),
            'server_timestamp': time.time()  # For frontend interpolation sync
        })

        # Check if race is complete
        if lap_result.get('race_complete'):
            await websocket.send_json({
                'type': 'RACE_COMPLETE',
                'final_position': lap_result['final_position'],
                'player': asdict(game_state.player),
                'opponents': [asdict(opp) for opp in game_state.opponents],
                'decision_count': len(game_state.decision_history),
                'race_summary': {
                    'total_laps': game_state.total_laps,
                    'decisions_made': len(game_state.decision_history)
                }
            })
            break

        # Check for decision points
        decision_check = orchestrator.check_for_decision_point()

        if decision_check.get('triggered'):
            # Get recommendations from GameAdvisor
            event_type = decision_check['event_type']
            current_state = decision_check['state']

            # Run quick sims + Gemini analysis
            recommendations = await orchestrator.get_decision_recommendations(
                event_type=event_type,
                current_state=current_state
            )

            # Send decision point to client
            await websocket.send_json({
                'type': 'DECISION_POINT',
                'event_type': event_type,
                'lap': current_state.lap,
                'position': current_state.position,
                'battery_soc': current_state.battery_soc,
                'tire_life': current_state.tire_life,
                'fuel_remaining': current_state.fuel_remaining,
                'recommended': recommendations['recommended'],
                'avoid': recommendations.get('avoid'),
                'latency_ms': recommendations.get('latency_ms', 0),
                'used_fallback': recommendations.get('used_fallback', False)
            })

            # Store decision point
            game_state.current_decision_point = {
                'event_type': event_type,
                'recommendations': recommendations
            }

            # Pause race loop and wait for player to select strategy
            # Clear the event (pauses the loop)
            game_state.pause_event.clear()

            # Wait for SELECT_STRATEGY to set the event (non-blocking)
            # Loop will pause here until strategy is selected
            await game_state.pause_event.wait()

            # Strategy selected! Loop continues seamlessly

        # Pacing: Wait 100ms between updates for smooth visualization
        await asyncio.sleep(0.1)
```

### web/hooks/useGameSession.ts (Debug Logging)
```typescript
case "LAP_UPDATE": {
  setCurrentLap(data.lap ?? 0);
  setPlayerState(data.player);
  setOpponents(data.opponents || []);
  setIsRaining(Boolean(data.is_raining));
  setSafetyCarActive(Boolean(data.safety_car_active));

  // Debug logging for car positions
  console.log(`[LAP ${data.lap}] Player: pos=${data.player?.position}, lap_progress=${data.player?.lap_progress?.toFixed(4)}, speed=${Math.round(data.player?.speed || 0)} km/h, cumulative=${data.player?.cumulative_time?.toFixed(2)}s`);
  data.opponents?.slice(0, 3).forEach((opp: OpponentState) => {
    console.log(`[LAP ${data.lap}] ${opp.name}: pos=${opp.position}, lap_progress=${opp.lap_progress?.toFixed(4)}, speed=${Math.round(opp.speed || 0)} km/h, cumulative=${opp.cumulative_time?.toFixed(2)}s`);
  });

  break;
}
```

---

## EXPECTED BEHAVIOR

**What should happen:**
1. Race starts → all cars at lap_progress = 0.0
2. After 1.8s (18s / 10 updates) → lap_progress = 0.1
3. After 9s → lap_progress = 0.5 (halfway around track)
4. After 18s → lap_progress = 1.0 → RESET to 0.0 (lap 2 starts)
5. Cars spread out based on cumulative_time (faster cars ahead)
6. Player car (blue) clearly visible, distinct from white opponents
7. Decision point triggers → modal appears → race continues in background
8. Strategy selected → modal closes → race continues smoothly
9. After 57 laps → race complete

**What actually happens:**
1. Race starts → all cars at lap_progress = 0.0 ✅
2. After 1.8s → lap_progress = 0.02 ❌ (should be 0.1)
3. Lap counter increments → cars stay at ~0.03 ❌
4. Player car jumps between 0.1 and 0.8 randomly ❌
5. Decision point → modal appears ✅
6. Strategy selected → cars stop moving completely ❌

---

## QUESTIONS FOR STRONGER LLMS

### Technical Questions
1. **Is the lap_progress formula fundamentally flawed?** Should we use a ratio-based approach instead?
   ```python
   # Current approach (broken?)
   lap_start_time = (current_lap - 1) * expected_lap_time
   elapsed = cumulative_time - lap_start_time
   lap_progress = elapsed / expected_lap_time

   # Alternative approach?
   total_expected = current_lap * expected_lap_time
   lap_progress = (cumulative_time / total_expected) % 1.0  # Modulo for cycling
   ```

2. **Should each car have its own lap counter** based on cumulative_time instead of shared current_lap?
   ```python
   # Current: All cars use same current_lap (from orchestrator)
   # Alternative: Each car tracks own lap
   car.current_lap = int(car.cumulative_time / expected_lap_time) + 1
   lap_progress = (car.cumulative_time % expected_lap_time) / expected_lap_time
   ```

3. **Is asyncio.sleep(0.1) causing timing drift?** Should we use absolute time tracking instead?

4. **Should we send server_timestamp and have frontend compensate for network latency?**

### Demo Enhancement Questions
1. **Visual clarity**: How to make strategy differences more obvious?
   - Color-code cars by strategy (aggressive=red, conservative=blue)?
   - Show "energy deployment" heatmap on track?
   - Animated trails behind cars showing speed?

2. **AI discovery**: How to showcase Gemini's analysis?
   - Show "confidence bars" on strategy cards?
   - Display "simulations run" counter during decision?
   - Highlight which rule from playbook was used?

3. **Performance metrics**: What numbers impress judges?
   - "300 simulations in 0.8s"?
   - "Sub-2s AI recommendations"?
   - "10 Hz real-time telemetry streaming"?

4. **Wow factor**: Any killer features we should add quickly?
   - Replay mode with speed control?
   - Side-by-side comparison of strategy outcomes?
   - Live strategy effectiveness chart?

---

## CONSTRAINTS & CONTEXT

- **Time pressure**: This is for a hackathon demo (need fix ASAP)
- **Tech stack locked**: Python backend, Next.js frontend, can't change fundamentally
- **Performance**: Must maintain 10 Hz updates (0.1s sleep)
- **Accuracy**: Physics calibrated from real 2024 Bahrain GP data (important for credibility)
- **Demo length**: ~4 minutes, need to show full race compressed to ~2 minutes

---

## SUCCESS CRITERIA

**Must have:**
1. Cars move smoothly around track (lap_progress cycles 0→1 each lap)
2. Player car (blue) clearly visible and moves correctly
3. Positions update based on cumulative_time (faster cars ahead)
4. Decision points pause for input, then resume seamlessly
5. Full 57-lap race completes in ~17 minutes (18s/lap × 57)

**Nice to have:**
1. Visual indicators of strategy differences
2. Performance metrics displayed prominently
3. AI discovery process visible to judges
4. Replay/analysis features

---

## YOUR MISSION

Please provide:
1. **Root cause diagnosis** with explanation
2. **Complete corrected code** for affected functions
3. **Step-by-step testing plan** to verify fix
4. **Enhancement suggestions** for demo impact
5. **Risk assessment** of proposed changes

**Format:**
- Be specific (line numbers, variable names)
- Explain WHY the bug exists
- Provide runnable code snippets
- Suggest validation tests

Thank you! 🏎️💨
