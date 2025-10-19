#!/usr/bin/env python3
"""
Comprehensive End-to-End Benchmark and Validation Suite

Tests the complete realistic physics pipeline:
1. Scenario generation
2. 2026 physics simulation
3. Results aggregation
4. Playbook-powered recommendations
5. AdaptiveAI performance

Produces a demo-ready report showing:
- Performance metrics vs targets
- Physics realism validation
- Agent diversity and effectiveness
- 2024 vs 2026 comparison
"""

import sys
sys.path.insert(0, '/Users/prajit/Desktop/projects/Gand')

import time
import json
from datetime import datetime
from sim.engine import simulate_race, create_agents
from sim.scenarios import generate_scenarios
from api.analysis import aggregate_results
from api.recommend import get_recommendations_fast
import pandas as pd

def benchmark_full_pipeline(num_scenarios=100):
    """Run comprehensive benchmark of entire system."""

    print("=" * 70)
    print("COMPREHENSIVE BENCHMARK - REALISTIC PHYSICS SYSTEM")
    print("=" * 70)
    print()

    results = {
        'timestamp': datetime.now().isoformat(),
        'num_scenarios': num_scenarios,
        'targets': {
            'simulation_time': 15.0,  # seconds for 1000 scenarios
            'recommendation_latency_p95': 1.5,  # seconds
            'adaptive_win_rate': 60.0  # percent
        },
        'results': {}
    }

    # ========================================================================
    # PART 1: SCENARIO GENERATION
    # ========================================================================
    print("PART 1: SCENARIO GENERATION")
    print("-" * 70)

    start = time.time()
    scenarios = generate_scenarios(num_scenarios, seed=42)
    gen_time = time.time() - start

    results['results']['scenario_generation'] = {
        'time_seconds': round(gen_time, 3),
        'scenarios_per_sec': round(num_scenarios / gen_time, 1),
        'passed': gen_time < 1.0
    }

    print(f"✓ Generated {num_scenarios} scenarios in {gen_time:.3f}s")
    print(f"  ({num_scenarios/gen_time:.1f} scenarios/sec)")
    print()

    # ========================================================================
    # PART 2: SIMULATION PERFORMANCE (2026 PHYSICS)
    # ========================================================================
    print("PART 2: SIMULATION PERFORMANCE (2026 PHYSICS)")
    print("-" * 70)

    agents = create_agents()
    print(f"✓ Created {len(agents)} agents")
    print(f"  Agents: {[a.name for a in agents]}")
    print()

    # Run simulations
    all_dfs = []
    start = time.time()

    for i, scenario in enumerate(scenarios):
        df = simulate_race(scenario, agents, use_2026_rules=True)
        df['scenario_id'] = scenario['id']
        all_dfs.append(df)

        if (i + 1) % 20 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"  Progress: {i+1}/{num_scenarios} ({rate:.1f} scenarios/sec)")

    sim_time = time.time() - start
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Calculate performance metrics
    scenarios_per_sec = num_scenarios / sim_time
    time_for_1000 = 1000 / scenarios_per_sec

    results['results']['simulation'] = {
        'time_seconds': round(sim_time, 2),
        'scenarios_per_sec': round(scenarios_per_sec, 2),
        'extrapolated_1000_scenarios': round(time_for_1000, 2),
        'target_met': time_for_1000 < 15.0,
        'total_simulations': len(combined_df)
    }

    print()
    print(f"✓ Simulated {num_scenarios} races in {sim_time:.2f}s")
    print(f"  Performance: {scenarios_per_sec:.2f} scenarios/sec")
    print(f"  Extrapolated 1000 scenarios: {time_for_1000:.2f}s")
    status = "✓ MET" if time_for_1000 < 15.0 else "⚠ NEEDS OPTIMIZATION"
    print(f"  Target (<15s for 1000): {status}")
    print()

    # ========================================================================
    # PART 3: RESULTS ANALYSIS
    # ========================================================================
    print("PART 3: RESULTS ANALYSIS")
    print("-" * 70)

    # Save temporary CSV for analysis
    temp_csv = 'data/temp_benchmark_results.csv'
    combined_df.to_csv(temp_csv, index=False)

    start = time.time()
    stats = aggregate_results(temp_csv)
    analysis_time = time.time() - start

    results['results']['analysis'] = {
        'time_seconds': round(analysis_time, 3),
        'metrics_generated': len(stats),
        'passed': analysis_time < 1.0
    }

    print(f"✓ Analyzed results in {analysis_time:.3f}s")
    print(f"  Metrics generated: {len(stats)}")
    print()

    # Show win distribution
    wins = {agent: data['wins'] for agent, data in stats.items()}
    total_wins = sum(wins.values())

    print("Win Distribution:")
    for agent, win_count in sorted(wins.items(), key=lambda x: x[1], reverse=True):
        win_pct = (win_count / num_scenarios) * 100
        bar = "█" * int(win_pct / 2)
        print(f"  {agent:20s} | {win_count:3d} wins ({win_pct:5.1f}%) {bar}")
    print()

    # ========================================================================
    # PART 4: RECOMMENDATION PERFORMANCE
    # ========================================================================
    print("PART 4: RECOMMENDATION PERFORMANCE")
    print("-" * 70)

    # Test 100 recommendation queries
    test_queries = [
        {'lap': i, 'battery_soc': 50 + (i % 50), 'position': (i % 8) + 1,
         'tire_age': i % 30, 'tire_life': 100 - (i % 80), 'fuel_remaining': 100 - i}
        for i in range(100)
    ]

    latencies = []
    for query in test_queries:
        start = time.time()
        recs = get_recommendations_fast(query)
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)

    latencies.sort()
    p50 = latencies[49]
    p95 = latencies[94]
    p99 = latencies[98]
    avg = sum(latencies) / len(latencies)

    results['results']['recommendations'] = {
        'queries_tested': 100,
        'avg_latency_ms': round(avg, 2),
        'p50_latency_ms': round(p50, 2),
        'p95_latency_ms': round(p95, 2),
        'p99_latency_ms': round(p99, 2),
        'target_met_p95': p95 < 1500
    }

    print(f"✓ Tested 100 recommendation queries")
    print(f"  Average latency: {avg:.2f}ms")
    print(f"  P50: {p50:.2f}ms | P95: {p95:.2f}ms | P99: {p99:.2f}ms")
    status = "✓ MET" if p95 < 1500 else "⚠ NEEDS OPTIMIZATION"
    print(f"  Target (P95 <1500ms): {status}")
    print()

    # ========================================================================
    # PART 5: ADAPTIVEAI VALIDATION
    # ========================================================================
    print("PART 5: ADAPTIVEAI PERFORMANCE VALIDATION")
    print("-" * 70)

    # Get AdaptiveAI stats
    adaptive_wins = wins.get('AdaptiveAI', 0)
    adaptive_win_rate = (adaptive_wins / num_scenarios) * 100

    # Calculate baseline (median of other agents)
    other_wins = [w for agent, w in wins.items() if agent != 'AdaptiveAI']
    median_baseline = sorted(other_wins)[len(other_wins) // 2] if other_wins else 0
    baseline_rate = (median_baseline / num_scenarios) * 100

    results['results']['adaptive_ai'] = {
        'wins': adaptive_wins,
        'win_rate_pct': round(adaptive_win_rate, 1),
        'baseline_median': median_baseline,
        'baseline_rate_pct': round(baseline_rate, 1),
        'beats_baseline': adaptive_wins > median_baseline,
        'target_met': adaptive_win_rate > 60.0
    }

    print(f"AdaptiveAI Performance:")
    print(f"  Wins: {adaptive_wins}/{num_scenarios} ({adaptive_win_rate:.1f}%)")
    print(f"  Baseline (median): {median_baseline}/{num_scenarios} ({baseline_rate:.1f}%)")

    if adaptive_wins > median_baseline:
        print(f"  ✓ AdaptiveAI beats baseline by {adaptive_wins - median_baseline} wins")
    else:
        print(f"  ⚠ AdaptiveAI below baseline by {median_baseline - adaptive_wins} wins")

    status = "✓ MET" if adaptive_win_rate > 60.0 else "⚠ BELOW TARGET"
    print(f"  Target (>60% win rate): {status}")
    print()

    # ========================================================================
    # PART 6: 2024 VS 2026 COMPARISON
    # ========================================================================
    print("PART 6: 2024 vs 2026 PHYSICS COMPARISON")
    print("-" * 70)

    # Run same scenario with 2024 and 2026 physics
    test_scenario = scenarios[0]

    df_2024 = simulate_race(test_scenario, agents, use_2026_rules=False)
    df_2026 = simulate_race(test_scenario, agents, use_2026_rules=True)

    avg_lap_2024 = df_2024['lap_time'].mean()
    avg_lap_2026 = df_2026['lap_time'].mean()
    time_diff = avg_lap_2024 - avg_lap_2026

    results['results']['physics_comparison'] = {
        '2024_avg_lap_time': round(avg_lap_2024, 2),
        '2026_avg_lap_time': round(avg_lap_2026, 2),
        'time_difference_seconds': round(time_diff, 2),
        'pct_improvement': round((time_diff / avg_lap_2024) * 100, 1)
    }

    print(f"2024 Physics: {avg_lap_2024:.2f}s average lap")
    print(f"2026 Physics: {avg_lap_2026:.2f}s average lap")
    print(f"Improvement: {time_diff:.2f}s ({(time_diff/avg_lap_2024)*100:.1f}% faster)")
    print(f"  (Due to 3x electric power: 350kW vs 120kW)")
    print()

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print()

    all_passed = all([
        results['results']['simulation']['target_met'],
        results['results']['recommendations']['target_met_p95'],
        results['results']['adaptive_ai']['beats_baseline']
    ])

    print("Target Achievement:")
    print(f"  Simulation (<15s for 1000): {results['results']['simulation']['target_met'] and '✓ MET' or '⚠ MISSED'}")
    print(f"  Recommendations (P95 <1.5s): {results['results']['recommendations']['target_met_p95'] and '✓ MET' or '⚠ MISSED'}")
    print(f"  AdaptiveAI (beats baseline): {results['results']['adaptive_ai']['beats_baseline'] and '✓ MET' or '⚠ MISSED'}")
    print()

    if all_passed:
        print("🎉 ALL TARGETS MET - SYSTEM READY FOR DEMO")
    else:
        print("⚠  Some targets missed - consider optimization")
    print()

    # Save results
    output_path = 'data/comprehensive_benchmark.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Benchmark results saved to {output_path}")
    print("=" * 70)

    return results

if __name__ == '__main__':
    benchmark_full_pipeline(num_scenarios=100)
