"""
Performance Report Generator for Strategy Gym 2026

Generates a JSON performance report for demo presentation.
Measures and logs key performance metrics to data/perf.json.
"""

import time
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim.scenarios import generate_scenarios
from sim.agents import create_agents
from sim.engine import simulate_race


def generate_performance_report(num_scenarios: int = 1000):
    """
    Generate comprehensive performance report.

    Args:
        num_scenarios: Number of scenarios to benchmark (default 1000)

    Returns:
        Dictionary with performance metrics
    """
    print("=" * 70)
    print("GENERATING PERFORMANCE REPORT")
    print("=" * 70)

    # Generate scenarios
    print(f"\nGenerating {num_scenarios} scenarios...")
    scenarios = generate_scenarios(num_scenarios)
    agents = create_agents()

    print(f"Running {num_scenarios} simulations with {len(agents)} agents...")
    print("Please wait...\n")

    # Measure performance
    start_time = time.time()

    for scenario in scenarios:
        df = simulate_race(scenario, agents)

    elapsed_time = time.time() - start_time

    # Calculate metrics
    perf_data = {
        "num_scenarios": num_scenarios,
        "num_agents": len(agents),
        "total_time_sec": round(elapsed_time, 2),
        "scenarios_per_sec": round(num_scenarios / elapsed_time, 1),
        "avg_scenario_time_ms": round((elapsed_time / num_scenarios) * 1000, 2),
        "target_met": elapsed_time < 5.0,
        "total_races": num_scenarios * len(agents)
    }

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save to JSON
    output_path = 'data/perf.json'
    with open(output_path, 'w') as f:
        json.dump(perf_data, f, indent=2)

    # Display report
    print("=" * 70)
    print("PERFORMANCE REPORT")
    print("=" * 70)
    print(json.dumps(perf_data, indent=2))
    print("=" * 70)
    print(f"\nReport saved to: {output_path}")
    print(f"Status: {'✅ PASS' if perf_data['target_met'] else '❌ FAIL'}")
    print("=" * 70)

    return perf_data


def main():
    """Run performance report generation"""
    # Allow custom scenario count via command line
    num_scenarios = 1000
    if len(sys.argv) > 1:
        try:
            num_scenarios = int(sys.argv[1])
        except ValueError:
            print(f"Invalid scenario count, using default: {num_scenarios}")

    # Generate report
    results = generate_performance_report(num_scenarios)

    # Return exit code based on target
    sys.exit(0 if results['target_met'] else 1)


if __name__ == "__main__":
    main()
