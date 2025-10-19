#!/usr/bin/env python3
"""
Full Scale Test - 1000 Scenarios

Validates that the system can actually handle 1000 scenarios
and confirms the performance extrapolation is accurate.
"""

import sys
sys.path.insert(0, '/Users/prajit/Desktop/projects/Gand')

import time
from sim.engine import simulate_race, create_agents
from sim.scenarios import generate_scenarios
import pandas as pd

def full_scale_test():
    """Run 1000 scenarios to validate performance."""

    print("=" * 70)
    print("FULL SCALE TEST - 1000 SCENARIOS")
    print("=" * 70)
    print()

    # Generate scenarios
    print("Generating 1000 scenarios...")
    start = time.time()
    scenarios = generate_scenarios(1000, seed=123)
    gen_time = time.time() - start
    print(f"✓ Generated in {gen_time:.3f}s")
    print()

    # Create agents
    print("Creating 8 agents...")
    agents = create_agents()
    print(f"✓ Agents: {[a.name for a in agents]}")
    print()

    # Run simulations
    print("Running 1000 simulations (2026 physics)...")
    print("This may take 5-10 seconds...")
    print()

    all_dfs = []
    start = time.time()

    for i, scenario in enumerate(scenarios):
        df = simulate_race(scenario, agents, use_2026_rules=True)
        df['scenario_id'] = scenario['id']
        all_dfs.append(df)

        # Progress updates
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            remaining = (1000 - (i + 1)) / rate
            print(f"  Progress: {i+1}/1000 ({rate:.1f} scenarios/sec, {remaining:.1f}s remaining)")

    sim_time = time.time() - start
    combined_df = pd.concat(all_dfs, ignore_index=True)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    # Performance metrics
    scenarios_per_sec = 1000 / sim_time
    total_laps = len(combined_df)

    print(f"Total Time: {sim_time:.2f}s")
    print(f"Performance: {scenarios_per_sec:.2f} scenarios/sec")
    print(f"Total Laps Simulated: {total_laps:,}")
    print()

    # Win distribution
    final_states = combined_df.groupby(['scenario_id', 'agent']).tail(1)
    wins = {}
    for agent in final_states['agent'].unique():
        agent_data = final_states[final_states['agent'] == agent]
        wins[agent] = int(agent_data['won'].sum())

    print("Win Distribution (1000 races):")
    for agent, win_count in sorted(wins.items(), key=lambda x: x[1], reverse=True):
        win_pct = (win_count / 1000) * 100
        bar = "█" * int(win_pct / 2)
        print(f"  {agent:20s} | {win_count:4d} wins ({win_pct:5.1f}%) {bar}")
    print()

    # Target check
    target = 15.0
    if sim_time < target:
        print(f"✓ TARGET MET: {sim_time:.2f}s < {target}s")
    else:
        print(f"⚠ TARGET MISSED: {sim_time:.2f}s > {target}s")
    print()

    # Save results
    output_csv = 'data/full_scale_1000_scenarios.csv'
    combined_df.to_csv(output_csv, index=False)
    print(f"✓ Results saved to {output_csv}")
    print("=" * 70)

    return {
        'sim_time': sim_time,
        'scenarios_per_sec': scenarios_per_sec,
        'total_laps': total_laps,
        'wins': wins,
        'target_met': sim_time < target
    }

if __name__ == '__main__':
    full_scale_test()
