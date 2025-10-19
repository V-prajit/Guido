"""
Performance Benchmark for Strategy Gym 2026

Measures simulation throughput by running 1000 scenarios with 8 agents.
Target: >200 scenarios/sec (1000 scenarios in <5 seconds)

This script provides real performance metrics without any hardcoded values.
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim.scenarios import generate_scenarios
from sim.agents import create_agents
from sim.engine import simulate_race


def run_benchmark(num_scenarios: int = 1000):
    """
    Run performance benchmark.

    Args:
        num_scenarios: Number of scenarios to run (default 1000)

    Returns:
        Dictionary with performance metrics
    """
    print("=" * 70)
    print("STRATEGY GYM 2026 - PERFORMANCE BENCHMARK")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Scenarios: {num_scenarios}")
    print(f"  Agents per scenario: 8")
    print(f"  Target: >200 scenarios/sec (1000 in <5.0s)")

    # Generate scenarios
    print(f"\nGenerating {num_scenarios} scenarios...")
    scenarios = generate_scenarios(num_scenarios)
    print(f"✅ Generated {len(scenarios)} scenarios")

    # Create agents
    agents = create_agents()
    print(f"✅ Created {len(agents)} agents")

    # Run benchmark
    print(f"\nRunning benchmark...")
    print("(This will take a moment, please wait...)")

    start_time = time.time()

    for i, scenario in enumerate(scenarios):
        # Run simulation
        df = simulate_race(scenario, agents)

        # Progress indicator every 100 scenarios
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            current_rate = (i + 1) / elapsed
            print(f"  Progress: {i + 1}/{num_scenarios} scenarios ({current_rate:.1f} scenarios/sec)")

    total_elapsed = time.time() - start_time

    # Calculate metrics
    scenarios_per_sec = num_scenarios / total_elapsed
    avg_scenario_time_ms = (total_elapsed / num_scenarios) * 1000
    target_met = scenarios_per_sec > 200

    # Display results
    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    print(f"\nPerformance Metrics:")
    print(f"  Total time: {total_elapsed:.2f} seconds")
    print(f"  Scenarios/sec: {scenarios_per_sec:.1f}")
    print(f"  Avg time per scenario: {avg_scenario_time_ms:.2f} ms")
    print(f"  Total races simulated: {num_scenarios * len(agents)}")

    print(f"\nTarget Analysis:")
    print(f"  Target: >200 scenarios/sec")
    print(f"  Actual: {scenarios_per_sec:.1f} scenarios/sec")

    if target_met:
        print(f"  Status: ✅ TARGET MET")
        speedup = scenarios_per_sec / 200
        print(f"  Speedup vs target: {speedup:.2f}x")
    else:
        print(f"  Status: ❌ TARGET NOT MET")
        gap = 200 - scenarios_per_sec
        speedup_needed = 200 / scenarios_per_sec
        print(f"  Gap: {gap:.1f} scenarios/sec too slow")
        print(f"  Speedup needed: {speedup_needed:.2f}x")

    print("\n" + "=" * 70)

    return {
        'num_scenarios': num_scenarios,
        'num_agents': len(agents),
        'total_time_sec': total_elapsed,
        'scenarios_per_sec': scenarios_per_sec,
        'avg_scenario_time_ms': avg_scenario_time_ms,
        'target_met': target_met
    }


def main():
    """Run benchmark with command line arguments"""
    # Allow custom scenario count via command line
    num_scenarios = 1000
    if len(sys.argv) > 1:
        try:
            num_scenarios = int(sys.argv[1])
            print(f"Custom scenario count: {num_scenarios}")
        except ValueError:
            print(f"Invalid scenario count, using default: {num_scenarios}")

    # Run benchmark
    results = run_benchmark(num_scenarios)

    # Return exit code based on target
    sys.exit(0 if results['target_met'] else 1)


if __name__ == "__main__":
    main()
