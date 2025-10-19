import multiprocessing as mp
import pandas as pd
import uuid
import time
import tempfile
import os
import json
from datetime import datetime
from typing import Tuple

def run_single_scenario(args: Tuple) -> pd.DataFrame:
    """Top-level worker function for multiprocessing"""
    scenario_id, scenario, agents = args
    from sim.engine import simulate_race
    df = simulate_race(scenario, agents)
    df['scenario_id'] = scenario_id
    return df

def run_simulations(num_scenarios: int, num_repeats: int, max_workers: int) -> Tuple[str, str, float]:
    """Run simulations with spawn-safe multiprocessing"""
    from sim.scenarios import generate_scenarios
    from sim.agents import create_agents
    
    start_time = time.time()
    scenarios = generate_scenarios(num_scenarios)
    agents = create_agents()
    
    tasks = [(f"S{i:04d}_{r}", scenarios[i], agents)
             for i in range(num_scenarios)
             for r in range(num_repeats)]
    
    # Use spawn context for macOS safety
    mp_ctx = mp.get_context("spawn")
    with mp_ctx.Pool(processes=max_workers) as pool:
        results = pool.map(run_single_scenario, tasks)
    
    df = pd.concat(results, ignore_index=True)
    
    # Atomic write with UTC timestamp
    run_id = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    # Write CSV atomically
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        csv_path = f"runs/{run_id}.csv"
        os.replace(tmp.name, csv_path)
    
    elapsed = time.time() - start_time
    
    # Write run summary atomically
    summary = {
        "run_id": run_id,
        "created_utc": datetime.utcnow().isoformat(),
        "scenarios": num_scenarios,
        "repeats": num_repeats,
        "duration_sec": elapsed,
        "csv_path": csv_path,
        "scenarios_per_sec": num_scenarios / elapsed if elapsed > 0 else 0
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(summary, tmp, indent=2)
        summary_path = f"runs/{run_id}.json"
        os.replace(tmp.name, summary_path)
    
    print(f"✓ Completed {num_scenarios} scenarios in {elapsed:.2f}s")
    print(f"  Rate: {num_scenarios/elapsed:.1f} scenarios/sec")
    print(f"  Saved to: {csv_path}")
    
    return run_id, csv_path, elapsed