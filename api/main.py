from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dotenv import load_dotenv
import time
import glob
import json

load_dotenv()

# Multiprocessing setup (macOS safe)
MP_CTX = mp.get_context("spawn")
MAX_WORKERS = int(os.getenv("MAX_WORKERS") or min(mp.cpu_count(), 8))
EXECUTOR = ProcessPoolExecutor(max_workers=MAX_WORKERS, mp_context=MP_CTX)

# Thread pool for I/O-bound tasks
THREAD_EXECUTOR = ThreadPoolExecutor(max_workers=4)

app = FastAPI(title="Strategy Gym 2026")

# CORS configuration
cors_allow_all = os.getenv("CORS_ALLOW_ALL", "true").lower() == "true"
if cors_allow_all:
    origins = ["*"]
else:
    origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared error model
class ApiError(BaseModel):
    code: int
    message: str
    detail: str | None = None

# Request/Response models
class RunRequest(BaseModel):
    num_scenarios: int = 100
    num_agents: int = 8
    repeats: int = 1

class RunResponse(BaseModel):
    run_id: str
    scenarios_completed: int
    csv_path: str
    elapsed_sec: float

class AnalyzeResponse(BaseModel):
    stats: dict
    playbook_preview: dict

class RecommendRequest(BaseModel):
    lap: int
    battery_soc: float
    position: int
    rain: bool = False
    tire_age: int = 0
    tire_life: float = 100.0
    fuel_remaining: float = 100.0
    boost_used: int = 0

class RecommendResponse(BaseModel):
    recommendations: list
    latency_ms: float
    timestamp: float
    seed: int
    conditions_evaluated: list

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("runs", exist_ok=True)

@app.post("/run", response_model=RunResponse)
async def run_simulation(req: RunRequest):
    """Non-blocking simulation runner"""
    from api.runner import run_simulations
    
    loop = asyncio.get_running_loop()
    try:
        run_id, csv_path, elapsed = await loop.run_in_executor(
            EXECUTOR, run_simulations, req.num_scenarios, req.repeats, MAX_WORKERS
        )
        return RunResponse(
            run_id=run_id, 
            scenarios_completed=req.num_scenarios, 
            csv_path=csv_path, 
            elapsed_sec=elapsed
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"code": 500, "message": "Simulation failed", "detail": str(e)}
        )

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_runs():
    """Analyze latest run and generate playbook"""
    from api.analysis import get_latest_run, aggregate_results
    from api.gemini import synthesize_playbook
    import pandas as pd
    
    try:
        # Get latest CSV
        csv_path = get_latest_run()
        
        # Aggregate stats
        stats = aggregate_results(csv_path)
        
        # Call Gemini synthesis
        df = pd.read_csv(csv_path)
        playbook = synthesize_playbook(stats, df)
        
        # Cache playbook with atomic write
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(playbook, tmp, indent=2)
            os.replace(tmp.name, 'data/playbook.json')
        
        return AnalyzeResponse(
            stats=stats,
            playbook_preview={"num_rules": len(playbook.get('rules', []))}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No run files found. Run simulation first.")
    except Exception as e:
        # Return last cached playbook if analysis fails
        if os.path.exists('data/playbook.json'):
            with open('data/playbook.json', 'r') as f:
                playbook = json.load(f)
            return AnalyzeResponse(
                stats={},
                playbook_preview={"cached": True, "num_rules": len(playbook.get('rules', []))}
            )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/playbook")
async def get_playbook():
    """Return cached playbook"""
    if not os.path.exists('data/playbook.json'):
        raise HTTPException(status_code=404, detail="No playbook generated yet")
    
    with open('data/playbook.json', 'r') as f:
        return json.load(f)

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    """Fast recommendation with transparency"""
    from api.recommend import get_recommendations_fast
    
    start = time.time()
    
    state = {
        'lap': req.lap,
        'battery_soc': req.battery_soc,
        'position': req.position,
        'rain': req.rain,
        'tire_age': req.tire_age,
        'tire_life': req.tire_life,
        'fuel_remaining': req.fuel_remaining,
        'boost_used': req.boost_used
    }
    
    recommendations, conditions_evaluated, seed = get_recommendations_fast(state)
    elapsed_ms = (time.time() - start) * 1000
    
    return RecommendResponse(
        recommendations=recommendations,
        latency_ms=elapsed_ms,
        timestamp=time.time(),
        seed=seed,
        conditions_evaluated=conditions_evaluated
    )

@app.post("/validate")
async def run_validation():
    """Run validation scenarios with adaptive AI"""
    import numpy as np
    from sim.scenarios import generate_scenarios
    from sim.agents import create_agents, AdaptiveAI
    from sim.engine import simulate_race
    
    # Load playbook
    if not os.path.exists('data/playbook.json'):
        raise HTTPException(status_code=400, detail="No playbook to validate")
    
    with open('data/playbook.json', 'r') as f:
        playbook = json.load(f)
    
    # Generate NEW scenarios
    np.random.seed(9999)
    scenarios = generate_scenarios(20)
    
    # Create agents with adaptive
    base_agents = create_agents()[:-1]
    adaptive = AdaptiveAI("Adaptive_AI", {}, playbook)
    agents = base_agents + [adaptive]
    
    # Run validation
    wins_by_agent = {a if isinstance(a, str) else a.name: 0 for a in agents}
    
    for scenario in scenarios:
        df = simulate_race(scenario, agents)
        winner = df[df['won'] == 1]['agent'].iloc[0]
        wins_by_agent[winner] += 1
    
    adaptive_wins = wins_by_agent['Adaptive_AI']
    baseline_wins = [w for a, w in wins_by_agent.items() if a != 'Adaptive_AI']
    median_baseline = sorted(baseline_wins)[len(baseline_wins)//2] if baseline_wins else 0
    
    return {
        "validation_scenarios": 20,
        "wins_by_agent": wins_by_agent,
        "adaptive_wins": adaptive_wins,
        "adaptive_win_rate": adaptive_wins / 20 * 100,
        "median_baseline": median_baseline,
        "median_baseline_rate": median_baseline / 20 * 100,
        "passed": adaptive_wins > median_baseline
    }

@app.get("/perf")
async def get_performance():
    """Get system performance metrics"""
    from api.perf import get_performance_metrics
    return get_performance_metrics()

@app.post("/benchmark")
async def run_benchmark_endpoint(num_scenarios: int = 1000):
    """Run performance benchmark with safety limits"""
    max_scenarios = int(os.getenv("MAX_BENCHMARK_SCENARIOS", 5000))
    if num_scenarios > max_scenarios:
        raise HTTPException(
            status_code=400,
            detail={
                "code": 400,
                "message": "Too many scenarios requested",
                "detail": f"Maximum allowed: {max_scenarios}"
            }
        )
    
    from api.perf import run_benchmark
    return run_benchmark(num_scenarios)

@app.get("/logs")
async def get_logs(offset: int = 0, limit: int = 50):
    """List run logs with pagination"""
    log_files = sorted(glob.glob("runs/*.json"), reverse=True)
    total = len(log_files)
    
    items = []
    for log_file in log_files[offset:offset+limit]:
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
                items.append({
                    "log_id": data["run_id"],
                    "run_id": data["run_id"],
                    "created_utc": data["created_utc"],
                    "scenarios": data["scenarios"],
                    "duration_sec": data["duration_sec"],
                    "verdict": data.get("verdict"),
                    "probability": data.get("probability")
                })
        except (json.JSONDecodeError, KeyError):
            continue
    
    return {"total": total, "items": items}

@app.get("/logs/{log_id}")
async def get_log_detail(log_id: str):
    """Get detailed log for specific run"""
    log_path = f"runs/{log_id}.json"
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log not found")
    
    with open(log_path, 'r') as f:
        return json.load(f)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "playbook_exists": os.path.exists('data/playbook.json'),
        "latest_run": max(glob.glob('runs/*.csv'), default=None),
        "num_runs": len(glob.glob('runs/*.csv')),
        "max_workers": MAX_WORKERS
    }


# ==========================================
# GAME MODE - WEBSOCKET ENDPOINT
# ==========================================

from fastapi import WebSocket, WebSocketDisconnect
from api.game_sessions import session_manager, GameState
from sim.game_loop import GameLoopOrchestrator
from dataclasses import asdict


def generate_heuristic_recommendations(current_state, event_type: str) -> dict:
    """
    Generate instant heuristic recommendations without running simulations.
    Used as fallback when pre-computation isn't ready (NEVER block the game!)
    """
    # Rain: Aggressive = risky, Balanced = safe, Conservative = very safe
    strategies = [
        {
            'strategy_id': 0,
            'strategy_name': 'Aggressive',
            'win_rate': 25.0,
            'rationale': 'High risk in rain. Push hard with electric power but tires will wear fast.',
            'confidence': 0.6,
            'strategy_params': {
                'energy_deployment': 85,
                'tire_management': 50,
                'fuel_strategy': 55,
                'ers_mode': 80,
                'overtake_aggression': 85,
                'defense_intensity': 60
            }
        },
        {
            'strategy_id': 1,
            'strategy_name': 'Balanced',
            'win_rate': 45.0,
            'rationale': 'Moderate pace with careful tire management. Best overall approach in rain.',
            'confidence': 0.8,
            'strategy_params': {
                'energy_deployment': 60,
                'tire_management': 75,
                'fuel_strategy': 70,
                'ers_mode': 65,
                'overtake_aggression': 55,
                'defense_intensity': 65
            }
        },
        {
            'strategy_id': 2,
            'strategy_name': 'Conservative',
            'win_rate': 15.0,
            'rationale': 'Very safe but slow. Risk dropping positions to faster cars.',
            'confidence': 0.7,
            'strategy_params': {
                'energy_deployment': 35,
                'tire_management': 90,
                'fuel_strategy': 85,
                'ers_mode': 50,
                'overtake_aggression': 30,
                'defense_intensity': 70
            }
        }
    ]

    return {
        'recommended': [strategies[1], strategies[0]],  # Balanced, then Aggressive
        'avoid': strategies[2],  # Conservative
        'latency_ms': 0,
        'used_fallback': True
    }


def calculate_realistic_speed(
    lap_progress: float,
    energy_deployment: float,
    tire_management: float,
    battery_soc: float
) -> float:
    """
    Calculate realistic F1 speed based on ACCURATE Bahrain International Circuit layout.

    Bahrain GP Track (5.412 km, 15 turns, clockwise):
    - Main straight (bottom): 0-12% - DRS zone, top speed
    - Turn 1 braking: 12-18% - Heavy braking into first corner
    - Turns 2-4: 18-28% - Right-side technical complex
    - Turns 5-8: 28-40% - Top section, medium-speed
    - Turns 9-10: 40-55% - Middle flowing section
    - Back straight: 55-68% - Top area, second DRS candidate
    - Turns 11-13: 68-82% - Left descent
    - Turns 14-15: 82-92% - Final corner complex
    - Acceleration: 92-100% - Power onto main straight

    Args:
        lap_progress: Position in lap (0-1)
        energy_deployment: Strategy param (0-100)
        tire_management: Strategy param (0-100)
        battery_soc: Battery level (0-100)

    Returns:
        Speed in km/h (100-340 range for realistic braking)
    """
    # SECTOR 1: Start/Finish Straight + Turn 1-4 Complex (0-33%)
    if lap_progress < 0.12:
        # MAIN STRAIGHT (bottom of track map) - Where "You" P1 starts
        # DRS active, maximum acceleration: 280 → 330 km/h
        progress = lap_progress / 0.12
        base_speed = 280 + (progress * 50)

    elif lap_progress < 0.18:
        # TURN 1: HEAVY BRAKING ZONE (end of main straight)
        # Dramatic slowdown for tight first corner: 330 → 100 km/h
        progress = (lap_progress - 0.12) / 0.06
        base_speed = 330 - (progress * 230)

    elif lap_progress < 0.25:
        # STRAIGHT AFTER TURN 1: Diagonal straight up-right (toward Piastri/Norris)
        # FAST acceleration out of Turn 1 exit: 100 → 280 km/h
        progress = (lap_progress - 0.18) / 0.07
        base_speed = 100 + (progress * 180)

    elif lap_progress < 0.35:
        # TECHNICAL SECTION: Hamilton/Alonso area corners (middle-right of map)
        # Medium-speed technical: 260 → 280 km/h
        progress = (lap_progress - 0.25) / 0.10
        base_speed = 260 + (progress * 20)

    # SECTOR 2: Middle to Top Section (35-66%)
    elif lap_progress < 0.43:
        # TURNS 5-8: Top-right back section
        # Medium-speed acceleration: 280 → 305 km/h
        progress = (lap_progress - 0.35) / 0.08
        base_speed = 280 + (progress * 25)

    elif lap_progress < 0.58:
        # TURNS 9-10: Middle technical flowing section
        # Maintaining momentum: 290 → 300 km/h
        progress = (lap_progress - 0.43) / 0.15
        base_speed = 290 + (progress * 10)

    # SECTOR 3: Final Section Back to Start/Finish (58-100%)
    elif lap_progress < 0.70:
        # BACK STRAIGHT: Top section (Piastri/Norris area on map)
        # Second DRS zone, good acceleration: 300 → 320 km/h
        progress = (lap_progress - 0.58) / 0.12
        base_speed = 300 + (progress * 20)

    elif lap_progress < 0.83:
        # TURNS 11-13: Left-side descent (Perez area on map)
        # Downhill technical section: 275 → 285 km/h
        progress = (lap_progress - 0.70) / 0.13
        base_speed = 275 + (progress * 10)

    elif lap_progress < 0.92:
        # TURNS 14-15: Final corner complex
        # Slow-speed corners before final straight: 270 → 280 km/h
        progress = (lap_progress - 0.83) / 0.09
        base_speed = 270 + (progress * 10)

    else:
        # FINAL ACCELERATION: Onto main straight (92-100%)
        # Power on for next lap: 280 → 330 km/h
        progress = (lap_progress - 0.92) / 0.08
        base_speed = 280 + (progress * 50)

    # Apply per-car strategy modifiers
    # Straights benefit from energy deployment, corners from tire management
    is_straight = (lap_progress < 0.12 or              # Main straight
                   (0.18 < lap_progress < 0.25) or      # Straight after Turn 1
                   (0.58 < lap_progress < 0.70) or      # Back straight (top)
                   lap_progress > 0.92)                 # Acceleration zone

    if is_straight:
        # STRAIGHTS: Energy deployment matters (electric power boost)
        # High energy = faster acceleration and top speed
        straight_bonus = (energy_deployment - 60) / 100 * 15  # ±15 km/h
        base_speed += straight_bonus
    else:
        # CORNERS: Tire management matters (mechanical grip)
        # High tire mgmt = better cornering speed
        corner_bonus = (tire_management - 70) / 100 * 10  # ±10 km/h
        base_speed += corner_bonus

    # Battery penalty (low battery → power limited on acceleration)
    if battery_soc < 20:
        battery_penalty = (20 - battery_soc) * 1.0  # 1 km/h per % below 20
        base_speed -= battery_penalty

    # Clamp to realistic F1 speeds (100-340 km/h range)
    # Allows for realistic heavy braking at Turn 1
    return max(100.0, min(340.0, base_speed))


def get_opponent_strategy_params(agent_type: str) -> tuple:
    """
    Get energy_deployment and tire_management for AI opponents.

    Returns:
        (energy_deployment, tire_management) tuple
    """
    strategies = {
        'VerstappenStyle': (70, 80),     # Balanced aggression
        'HamiltonStyle': (60, 90),       # Tire conservation
        'AlonsoStyle': (55, 85),         # Strategic defense
        'AggressiveAttacker': (85, 60),  # All-out attack
        'TireWhisperer': (50, 95),       # Maximum tire care
        'EnergyMaximizer': (90, 70),     # Energy aggressive
        'BalancedRacer': (60, 75)        # Standard approach
    }
    return strategies.get(agent_type, (60, 70))  # Default fallback


@app.websocket("/ws/game/{session_id}")
async def game_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for interactive game mode.

    Client sends:
    - START_GAME: Initialize new race
    - SELECT_STRATEGY: Choose strategy during decision point

    Server sends:
    - RACE_STARTED: Race initialized
    - LAP_UPDATE: Lap-by-lap race state
    - DECISION_POINT: Pause for player decision with recommendations
    - RACE_COMPLETE: Race finished
    """
    import traceback

    print(f"✓ WebSocket connection attempt: {session_id}")
    await websocket.accept()
    print(f"✓ WebSocket accepted: {session_id}")

    game_state: GameState = None
    orchestrator: GameLoopOrchestrator = None

    try:
        while True:
            print(f"[{session_id}] Waiting for message...")
            # Receive message from client
            try:
                data = await websocket.receive_json()
                print(f"[{session_id}] ✓ Got message: {data}")
            except Exception as e:
                print(f"[{session_id}] ❌ Failed to receive JSON: {e}")
                traceback.print_exc()
                break

            message_type = data.get('type')
            print(f"[{session_id}] Message type: {message_type}")

            # ==========================================
            # START GAME
            # ==========================================
            if message_type == 'START_GAME':
                # Create new game session
                player_name = data.get('player_name', 'Player')
                total_laps = data.get('total_laps', 57)
                rain_lap = data.get('rain_lap')
                safety_car_lap = data.get('safety_car_lap')

                # Use provided session_id or create new one
                new_session_id = session_manager.create_session(
                    player_name=player_name,
                    total_laps=total_laps,
                    rain_lap=rain_lap,
                    safety_car_lap=safety_car_lap
                )

                # Get game state
                game_state = session_manager.get_session(new_session_id)

                # Initialize pause_event for race control
                game_state.pause_event = asyncio.Event()
                game_state.pause_event.set()  # Initially not paused

                orchestrator = GameLoopOrchestrator(game_state)

                # Send RACE_STARTED message
                await websocket.send_json({
                    'type': 'RACE_STARTED',
                    'session_id': new_session_id,
                    'total_laps': total_laps,
                    'player': asdict(game_state.player),
                    'opponents': [asdict(opp) for opp in game_state.opponents]
                })

                # Start auto-advancing laps
                await run_race_loop(websocket, orchestrator, game_state)

            # ==========================================
            # SELECT STRATEGY
            # ==========================================
            elif message_type == 'SELECT_STRATEGY':
                if not orchestrator:
                    await websocket.send_json({
                        'type': 'ERROR',
                        'message': 'No active game session'
                    })
                    continue

                strategy_id = data.get('strategy_id', 0)

                # Apply chosen strategy
                success = orchestrator.apply_strategy_choice(strategy_id)

                if success:
                    # Clear decision point
                    game_state.current_decision_point = None

                    # Send confirmation
                    await websocket.send_json({
                        'type': 'STRATEGY_APPLIED',
                        'strategy_id': strategy_id
                    })

                    # Resume race loop by setting the pause_event
                    # This will unblock the await pause_event.wait() in run_race_loop
                    game_state.pause_event.set()
                else:
                    await websocket.send_json({
                        'type': 'ERROR',
                        'message': 'Invalid strategy selection'
                    })

    except WebSocketDisconnect:
        # Cleanup session on disconnect
        print(f"✓ Client disconnected: {session_id}")
        if game_state:
            session_manager.delete_session(game_state.session_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        traceback.print_exc()
        try:
            await websocket.send_json({
                'type': 'ERROR',
                'message': 'Game error',
                'details': str(e)
            })
        except:
            pass


async def run_race_loop(websocket: WebSocket, orchestrator: GameLoopOrchestrator, game_state: GameState):
    """
    Run the race lap-by-lap with fixed timing, pausing for decision points.

    Uses a lap timer to gate advance_lap() calls to maintain correct timing
    (e.g., 18s per lap with LAP_TIME_MULTIPLIER=5.0), while sending updates
    at 10 Hz for smooth visualization.

    CRITICAL FIX: Advances cumulative_time incrementally every 100ms for smooth
    car movement, while keeping lap-based physics every 18s for accuracy.
    """
    # Calculate expected lap time in demo units (e.g., 90s / 5.0 = 18s)
    LAP_TIME_DEMO = 90.0 / orchestrator.lap_time_multiplier

    # Timing accumulators
    lap_accum = 0.0       # Accumulates time for next lap advancement
    update_accum = 0.0    # Accumulates time for next state broadcast
    last = time.perf_counter()  # Monotonic clock (immune to system clock changes)
    UPDATE_INTERVAL = 0.1  # 10 Hz update rate

    # CRITICAL FIX: Track baseline cumulative times for smooth interpolation
    # These store the authoritative cumulative_time from the last advance_lap() call
    cumulative_baselines = {}
    all_racers = [game_state.player] + game_state.opponents
    for racer in all_racers:
        racer_id = id(racer)  # Use object ID as unique key
        cumulative_baselines[racer_id] = racer.cumulative_time

    # Ensure race starts in running state
    game_state.pause_event.set()

    # CRITICAL FIX: Advance to lap 1 immediately to kickstart the race
    # Without this, race stays at lap 0 forever waiting for first lap_accum >= 18s
    if game_state.current_lap == 0:
        orchestrator.advance_lap()
        session_manager.update_session(game_state.session_id, game_state)
        # Update baselines after first lap advancement
        for racer in all_racers:
            cumulative_baselines[id(racer)] = racer.cumulative_time

    while not game_state.is_complete and not game_state.is_paused:
        # Measure real elapsed time using monotonic clock
        now = time.perf_counter()
        dt = now - last
        last = now

        # Pause handling: freeze simulation time when paused
        if not game_state.pause_event.is_set():
            await asyncio.sleep(0.02)  # Small sleep while paused
            continue

        # Accumulate time
        lap_accum += dt
        update_accum += dt

        # ==========================================
        # SMOOTH VISUALIZATION: Update lap_progress AND speed
        # Each racer advances from their baseline + elapsed lap time
        # ==========================================
        all_racers = [game_state.player] + game_state.opponents
        for racer in all_racers:
            racer_id = id(racer)
            baseline = cumulative_baselines.get(racer_id, racer.cumulative_time)

            # Per-car speed multiplier (faster cars move faster in visualization)
            # Use last lap time to estimate current pace
            if hasattr(racer, 'lap_time') and racer.lap_time > 0:
                expected_lap_time = racer.lap_time
            elif hasattr(racer, 'last_lap_time') and racer.last_lap_time > 0:
                expected_lap_time = racer.last_lap_time
            else:
                expected_lap_time = LAP_TIME_DEMO

            # Speed factor: how fast this car is relative to demo lap time
            # Faster cars (lower lap_time) get speed_factor > 1.0
            speed_factor = LAP_TIME_DEMO / max(0.1, expected_lap_time)

            # Estimate current cumulative time (baseline + scaled elapsed time)
            estimated_cumulative = baseline + (lap_accum * speed_factor)

            # Calculate lap_progress from estimated cumulative time
            # This gives smooth per-car movement based on individual pace
            car_fractional_laps = estimated_cumulative / LAP_TIME_DEMO
            racer.lap_progress = min(0.999, float(car_fractional_laps - int(car_fractional_laps)))

            # ==========================================
            # DYNAMIC SPEED CALCULATION (every 100ms)
            # Uses lap_progress + strategy to show realistic F1 speed variation
            # ==========================================
            if hasattr(racer, 'energy_deployment'):
                # Player: use actual strategy params
                racer.speed = calculate_realistic_speed(
                    lap_progress=racer.lap_progress,
                    energy_deployment=racer.energy_deployment,
                    tire_management=racer.tire_management,
                    battery_soc=racer.battery_soc
                )
            else:
                # Opponent: use agent-specific strategy defaults
                energy, tire_mgmt = get_opponent_strategy_params(racer.agent_type)
                racer.speed = calculate_realistic_speed(
                    lap_progress=racer.lap_progress,
                    energy_deployment=energy,
                    tire_management=tire_mgmt,
                    battery_soc=racer.battery_soc
                )

        # Only advance lap when enough time has passed (~18s)
        if lap_accum >= LAP_TIME_DEMO:
            lap_result = orchestrator.advance_lap()
            lap_accum = 0.0  # Reset lap timer

            # Update cumulative time baselines with NEW authoritative values
            for racer in all_racers:
                cumulative_baselines[id(racer)] = racer.cumulative_time

            # Update session
            session_manager.update_session(game_state.session_id, game_state)

            # DEMO OPTIMIZATION: Pre-compute rain decision on lap 2 for instant lap 3 display
            if game_state.current_lap == 2 and not orchestrator.pre_compute_started:
                print("[DEMO] Lap 2 complete - triggering pre-computation for rain decision")
                orchestrator.pre_compute_started = True
                # Run pre-computation in SEPARATE THREAD (truly non-blocking)
                loop = asyncio.get_event_loop()
                loop.run_in_executor(THREAD_EXECUTOR, orchestrator.pre_compute_rain_decision)

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

        # Send state updates at 10 Hz (independent of lap advancement)
        if update_accum >= UPDATE_INTERVAL:
            update_accum = 0.0

            # Send lap update to client (includes speed, gap_to_leader, lap_progress from game_loop)
            await websocket.send_json({
                'type': 'LAP_UPDATE',
                'lap': game_state.current_lap,
                'player': asdict(game_state.player),
                'opponents': [asdict(opp) for opp in game_state.opponents],
                'is_raining': game_state.is_raining,
                'safety_car_active': game_state.safety_car_active,
                'server_timestamp': now  # For frontend interpolation sync
            })

            # Debug logging (once per second)
            if int(now) != int(last + dt):  # New second boundary
                print(f"[RACE] Lap {game_state.current_lap}/{game_state.total_laps}, "
                      f"lap_accum={lap_accum:.2f}s, "
                      f"player cumulative={game_state.player.cumulative_time:.2f}s, "
                      f"pos=P{game_state.player.position}")

        # Check for decision points
        decision_check = orchestrator.check_for_decision_point()

        if decision_check.get('triggered'):
            # Get recommendations from GameAdvisor
            event_type = decision_check['event_type']
            current_state = decision_check['state']

            # DEMO OPTIMIZATION: Use pre-computed decision for rain on lap 3
            if event_type == 'RAIN_START' and orchestrator.pre_computed_decision is not None:
                print("[DEMO] ✓ Using pre-computed rain decision (instant response!)")
                recommendations = orchestrator.pre_computed_decision
                recommendations['latency_ms'] = recommendations.get('latency_ms', 0)
                recommendations['pre_computed'] = True
            else:
                # CRITICAL FIX: Use instant heuristic fallback (NEVER block the game!)
                print(f"[DEMO] Pre-computation not ready, using instant heuristic fallback for {event_type}")
                recommendations = generate_heuristic_recommendations(current_state, event_type)
                recommendations['pre_computed'] = False
                print(f"[DEMO] ✓ Instant fallback recommendations generated (0ms latency)")

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
            game_state.pause_event.clear()
            print(f"[RACE_LOOP] Paused race, waiting for player to select strategy...")

            # Wait for SELECT_STRATEGY to set the event (with 5 min timeout)
            try:
                await asyncio.wait_for(game_state.pause_event.wait(), timeout=300.0)
                print(f"[RACE_LOOP] ✓ Player selected strategy, resuming race...")
            except asyncio.TimeoutError:
                # Timeout - auto-select balanced strategy
                print(f"[RACE_LOOP] ⚠️ Decision timeout (5min) - auto-selecting balanced strategy")
                orchestrator.apply_strategy_choice(1)  # Auto-select balanced (strategy_id=1)
                game_state.pause_event.set()

            # Reset monotonic clock baseline after pause to prevent dt spike
            last = time.perf_counter()

        # Cooperative yield to event loop
        await asyncio.sleep(0.002)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)