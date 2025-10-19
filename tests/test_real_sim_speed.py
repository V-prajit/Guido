"""
Test REAL simulation speed for decision points.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from sim.decision_sim import DecisionState, run_decision_simulations, generate_strategy_variations

def test_simulation_speed():
    """Test how fast we can run 300 real simulations."""

    print("🏎️  Testing REAL simulation speed for decision points\n")

    # Current race state at decision point
    state = DecisionState(
        lap=15,
        total_laps=57,
        position=4,
        battery_soc=45.0,
        tire_life=62.0,
        fuel_remaining=28.0,
        tire_age=15,
        tire_compound='HARD',
        rain=True,
        track_type='balanced',
        temperature=25.0
    )

    # Generate 3 strategies
    strategies = generate_strategy_variations(state, 'RAIN_START')

    print("📊 Configuration:")
    print(f"   Current lap: {state.lap}/{state.total_laps}")
    print(f"   Remaining laps: {state.total_laps - state.lap}")
    print(f"   Simulations per strategy: 100")
    print(f"   Total simulations: 300\n")

    # Run simulations and measure time
    print("⏱️  Running simulations...")
    start_time = time.time()

    results = run_decision_simulations(
        current_state=state,
        strategy_params=strategies,
        num_sims_per_strategy=100,
        use_2026_rules=True
    )

    elapsed = time.time() - start_time

    print(f"✅ Complete in {elapsed:.2f}s\n")

    # Analyze results
    print("📈 Results Summary:")
    print(f"   Total rows: {len(results)}")
    print(f"   Columns: {len(results.columns)}")
    print(f"\n   Available metrics:")
    for col in sorted(results.columns):
        print(f"      - {col}")

    print(f"\n   Win distribution:")
    for sid in range(3):
        strat_data = results[results['strategy_id'] == sid]
        wins = strat_data['won'].sum()
        avg_pos = strat_data['final_position'].mean()
        avg_battery = strat_data['battery_soc'].mean()
        print(f"      Strategy {sid}: {wins} wins, avg P{avg_pos:.1f}, {avg_battery:.1f}% battery")

    # Performance metrics
    print(f"\n⚡ Performance:")
    print(f"   Simulations per second: {300/elapsed:.1f}")
    print(f"   Time per simulation: {elapsed*1000/300:.1f}ms")

    # Check if fast enough for real-time
    gemini_time = 1.5  # Estimated Gemini 2.5 Flash time
    total_decision_time = elapsed + gemini_time

    print(f"\n🎯 Total Decision Latency Estimate:")
    print(f"   Simulation: {elapsed:.2f}s")
    print(f"   Gemini 2.5 Flash: ~{gemini_time:.1f}s")
    print(f"   Total: ~{total_decision_time:.1f}s")

    if total_decision_time < 4:
        print(f"   ✅ Under 4s target!")
    else:
        print(f"   ⚠️  Above 4s target (but acceptable for demo)")

    return elapsed, results

if __name__ == '__main__':
    elapsed, results = test_simulation_speed()
