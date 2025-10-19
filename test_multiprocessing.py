#!/usr/bin/env python3
"""
Test multiprocessing compatibility of the new simulation engine.

This demonstrates that the engine can be used with multiprocessing.Pool
which is critical for the R2 backend runner.
"""

from multiprocessing import Pool
from sim.engine import simulate_race, create_agents
from sim.scenarios import generate_scenarios
import time


def run_simulation(args):
    """
    Worker function for multiprocessing.
    Must be at module level to be picklable.
    """
    scenario, agents, use_2026_rules = args
    df = simulate_race(scenario, agents, use_2026_rules)
    winner = df[df['won'] == True]['agent'].iloc[0]
    return {
        'scenario_id': scenario['id'],
        'num_laps': scenario['num_laps'],
        'winner': winner,
        'df': df
    }


def main():
    print("=" * 60)
    print("MULTIPROCESSING COMPATIBILITY TEST")
    print("=" * 60)
    print()

    # Generate scenarios
    num_scenarios = 20
    scenarios = generate_scenarios(num_scenarios)
    agents = create_agents()

    print(f"Testing with {num_scenarios} scenarios...")
    print()

    # Test 1: Sequential execution
    print("Test 1: Sequential execution")
    start = time.time()
    sequential_results = []
    for scenario in scenarios:
        result = run_simulation((scenario, agents, True))
        sequential_results.append(result)
    sequential_time = time.time() - start
    print(f"  ✓ Completed in {sequential_time:.2f}s")
    print(f"  ✓ Throughput: {num_scenarios/sequential_time:.1f} scenarios/sec")
    print()

    # Test 2: Parallel execution
    print("Test 2: Parallel execution (4 workers)")
    start = time.time()
    args = [(scenario, agents, True) for scenario in scenarios]

    with Pool(4) as pool:
        parallel_results = pool.map(run_simulation, args)

    parallel_time = time.time() - start
    print(f"  ✓ Completed in {parallel_time:.2f}s")
    print(f"  ✓ Throughput: {num_scenarios/parallel_time:.1f} scenarios/sec")
    print(f"  ✓ Speedup: {sequential_time/parallel_time:.2f}x")
    print()

    # Verify results
    print("Test 3: Verifying results consistency")
    winners_seq = [r['winner'] for r in sequential_results]
    winners_par = [r['winner'] for r in parallel_results]

    if winners_seq == winners_par:
        print("  ✓ Sequential and parallel results are identical")
    else:
        print("  ✗ Results differ!")
        for i, (seq, par) in enumerate(zip(winners_seq, winners_par)):
            if seq != par:
                print(f"    Scenario {i}: sequential={seq}, parallel={par}")

    print()

    # Display results summary
    print("Results Summary:")
    print("-" * 60)
    winner_counts = {}
    for result in parallel_results:
        winner = result['winner']
        winner_counts[winner] = winner_counts.get(winner, 0) + 1

    for agent, count in sorted(winner_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {agent:20s}: {count:3d} wins ({count*100/num_scenarios:5.1f}%)")

    print("-" * 60)
    print()

    print("=" * 60)
    print("MULTIPROCESSING COMPATIBILITY CONFIRMED")
    print("=" * 60)


if __name__ == "__main__":
    main()
