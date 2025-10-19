import psutil
import time
from multiprocessing import cpu_count

def get_performance_metrics():
    """Get current system performance metrics"""
    return {
        "cpu_count": cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_gb": psutil.virtual_memory().available / (1024**3),
        "disk_usage_percent": psutil.disk_usage('.').percent,
        "timestamp": time.time()
    }

def run_benchmark(num_scenarios: int = 1000):
    """Run performance benchmark"""
    from api.runner import run_simulations
    import os
    
    max_workers = int(os.getenv("MAX_WORKERS") or min(cpu_count(), 8))
    
    start = time.time()
    run_id, csv_path, elapsed = run_simulations(num_scenarios, num_repeats=1, max_workers=max_workers)
    
    return {
        "num_scenarios": num_scenarios,
        "elapsed_sec": elapsed,
        "scenarios_per_sec": num_scenarios / elapsed if elapsed > 0 else 0,
        "avg_scenario_ms": (elapsed / num_scenarios) * 1000 if num_scenarios > 0 else 0,
        "run_id": run_id,
        "max_workers": max_workers,
        "timestamp": time.time()
    }