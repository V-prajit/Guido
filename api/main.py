from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from dotenv import load_dotenv
import time
import glob
import json

load_dotenv()

# Multiprocessing setup (macOS safe)
MP_CTX = mp.get_context("spawn")
MAX_WORKERS = int(os.getenv("MAX_WORKERS") or min(mp.cpu_count(), 8))
EXECUTOR = ProcessPoolExecutor(max_workers=MAX_WORKERS, mp_context=MP_CTX)

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
    await websocket.accept()

    game_state: GameState = None
    orchestrator: GameLoopOrchestrator = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get('type')

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
                    # Resume race
                    game_state.is_paused = False
                    game_state.current_decision_point = None

                    # Send confirmation
                    await websocket.send_json({
                        'type': 'STRATEGY_APPLIED',
                        'strategy_id': strategy_id
                    })

                    # Continue race
                    await run_race_loop(websocket, orchestrator, game_state)
                else:
                    await websocket.send_json({
                        'type': 'ERROR',
                        'message': 'Invalid strategy selection'
                    })

    except WebSocketDisconnect:
        # Cleanup session on disconnect
        if game_state:
            session_manager.delete_session(game_state.session_id)
    except Exception as e:
        await websocket.send_json({
            'type': 'ERROR',
            'message': 'Game error',
            'details': str(e)
        })


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
            # Pause game
            game_state.is_paused = True

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

            # Wait for player to select strategy
            # (race loop pauses here, client sends SELECT_STRATEGY)
            break

        # Pacing: Wait 500ms between laps for visualization
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)