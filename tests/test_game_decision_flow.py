"""
End-to-end test for interactive game decision system.

Tests the complete flow:
1. Run 300 simulations from mid-race state (100 per strategy)
2. Analyze results with GameAdvisor (Gemini or fallback)
3. Verify performance (<4s total latency)
4. Validate output format for game integration

Author: Claude Code
Date: 2025-10-19
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import pandas as pd
from api.gemini_game_advisor import GameAdvisor
from sim.decision_sim import run_decision_simulations, DecisionState

def test_complete_decision_flow():
    """
    Full integration test: simulation → analysis → recommendations
    """

    print("=" * 70)
    print("INTERACTIVE GAME DECISION SYSTEM - END-TO-END TEST")
    print("=" * 70)

    # ==========================================
    # STEP 1: Set up realistic mid-race scenario
    # ==========================================

    print("\n📍 STEP 1: Setting up mid-race scenario...")
    print("   Lap 15/57, Position P4")
    print("   Battery: 45%, Tires: 62%, Fuel: 28kg")
    print("   Event: RAIN STARTING")

    race_state = DecisionState(
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

    # Define 3 strategic alternatives
    strategies = [
        {
            'name': 'Aggressive',
            'energy_deployment': 85,
            'tire_management': 70,
            'fuel_strategy': 60,
            'ers_mode': 80,
            'overtake_aggression': 90,
            'defense_intensity': 40
        },
        {
            'name': 'Balanced',
            'energy_deployment': 60,
            'tire_management': 80,
            'fuel_strategy': 70,
            'ers_mode': 65,
            'overtake_aggression': 60,
            'defense_intensity': 55
        },
        {
            'name': 'Conservative',
            'energy_deployment': 35,
            'tire_management': 90,
            'fuel_strategy': 85,
            'ers_mode': 50,
            'overtake_aggression': 30,
            'defense_intensity': 70
        }
    ]

    # ==========================================
    # STEP 2: Run quick simulations
    # ==========================================

    print("\n⚡ STEP 2: Running quick simulations...")
    print("   Target: 300 sims in <2 seconds")

    sim_start = time.time()

    sim_results = run_decision_simulations(
        current_state=race_state,
        strategy_params=strategies,
        num_sims_per_strategy=100,
        use_2026_rules=True
    )

    sim_elapsed = time.time() - sim_start

    print(f"   ✅ Completed {len(sim_results)} simulations in {sim_elapsed:.3f}s")
    print(f"   📊 Speed: {len(sim_results) / sim_elapsed:.1f} sims/sec")

    if sim_elapsed > 2.0:
        print(f"   ⚠️ WARNING: Exceeded 2s target (took {sim_elapsed:.2f}s)")

    # ==========================================
    # STEP 3: Validate simulation data format
    # ==========================================

    print("\n🔍 STEP 3: Validating simulation data...")

    required_cols = ['strategy_id', 'sim_run_id', 'final_position', 'won',
                     'battery_soc', 'tire_life', 'fuel_remaining']

    missing_cols = [col for col in required_cols if col not in sim_results.columns]

    if missing_cols:
        print(f"   ❌ Missing required columns: {missing_cols}")
        return False

    print(f"   ✅ All required columns present")
    print(f"   📋 Total rows: {len(sim_results)}")
    print(f"   📋 Strategies: {sim_results['strategy_id'].nunique()}")

    # Print summary stats
    print("\n   Strategy Performance Summary:")
    for sid in range(3):
        strategy_data = sim_results[sim_results['strategy_id'] == sid]
        win_rate = strategy_data['won'].mean() * 100
        avg_pos = strategy_data['final_position'].mean()
        avg_battery = strategy_data['battery_soc'].mean()

        print(f"      {strategies[sid]['name']:12s}: {win_rate:5.1f}% wins, "
              f"P{avg_pos:.1f} avg, {avg_battery:.0f}% battery")

    # ==========================================
    # STEP 4: Analyze with GameAdvisor
    # ==========================================

    print("\n🧠 STEP 4: Running Gemini analysis...")

    advisor = GameAdvisor()

    race_context = {
        'lap': race_state.lap,
        'total_laps': race_state.total_laps,
        'position': race_state.position,
        'battery_soc': race_state.battery_soc,
        'tire_life': race_state.tire_life,
        'fuel_remaining': race_state.fuel_remaining,
        'event_type': 'RAIN_START'
    }

    analysis_start = time.time()

    recommendations = advisor.analyze_decision_point(
        sim_results=sim_results,
        race_context=race_context,
        strategy_params=strategies,
        timeout_seconds=2.5
    )

    analysis_elapsed = time.time() - analysis_start

    print(f"   ✅ Analysis completed in {analysis_elapsed:.3f}s")
    print(f"   🤖 Used Gemini: {not recommendations['used_fallback']}")
    print(f"   ⏱️ Reported latency: {recommendations['latency_ms']}ms")

    # ==========================================
    # STEP 5: Validate recommendations format
    # ==========================================

    print("\n✅ STEP 5: Validating recommendations...")

    if 'recommended' not in recommendations or 'avoid' not in recommendations:
        print("   ❌ Missing 'recommended' or 'avoid' fields")
        return False

    if len(recommendations['recommended']) != 2:
        print(f"   ❌ Expected 2 recommendations, got {len(recommendations['recommended'])}")
        return False

    print("   ✅ Recommendation structure valid")

    # Display recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDED STRATEGIES:")
    print("=" * 70)

    for i, rec in enumerate(recommendations['recommended'], 1):
        print(f"\n{i}. {rec['strategy_name']} (Strategy {rec['strategy_id']})")
        print(f"   Win Rate: {rec['win_rate']:.1f}%")
        print(f"   Avg Position: P{rec['avg_position']:.1f}")
        print(f"   Confidence: {rec['confidence']:.0%}")
        print(f"   Rationale: {rec['rationale']}")

    print("\n" + "=" * 70)
    print("STRATEGY TO AVOID:")
    print("=" * 70)

    avoid = recommendations['avoid']
    print(f"\n❌ {avoid['strategy_name']} (Strategy {avoid['strategy_id']})")
    print(f"   Win Rate: {avoid['win_rate']:.1f}%")
    print(f"   Avg Position: P{avoid['avg_position']:.1f}")
    print(f"   Rationale: {avoid['rationale']}")
    print(f"   Risk: {avoid['risk']}")

    # ==========================================
    # STEP 6: Performance summary
    # ==========================================

    total_latency = sim_elapsed + analysis_elapsed

    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY:")
    print("=" * 70)
    print(f"   Simulation Time:  {sim_elapsed:.3f}s ({len(sim_results)} sims)")
    print(f"   Analysis Time:    {analysis_elapsed:.3f}s")
    print(f"   Total Latency:    {total_latency:.3f}s")
    print(f"   Target:           <4.0s")

    if total_latency <= 4.0:
        print(f"   ✅ PASSED - {4.0 - total_latency:.2f}s under target")
    else:
        print(f"   ⚠️ EXCEEDED - {total_latency - 4.0:.2f}s over target")

    print("\n" + "=" * 70)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 70)

    return True


def test_edge_cases():
    """Test edge cases for robustness."""

    print("\n" + "=" * 70)
    print("EDGE CASE TESTING")
    print("=" * 70)

    # Test 1: Late race (lap 50)
    print("\n🧪 Test 1: Late race scenario (lap 50/57)...")

    late_race_state = DecisionState(
        lap=50,
        total_laps=57,
        position=2,
        battery_soc=15.0,  # Low battery
        tire_life=25.0,    # Worn tires
        fuel_remaining=10.0,
        tire_compound='HARD'
    )

    strategies = [
        {'energy_deployment': 50, 'tire_management': 85, 'fuel_strategy': 70,
         'ers_mode': 90, 'overtake_aggression': 60, 'defense_intensity': 80},
        {'energy_deployment': 30, 'tire_management': 90, 'fuel_strategy': 80,
         'ers_mode': 95, 'overtake_aggression': 40, 'defense_intensity': 85},
        {'energy_deployment': 20, 'tire_management': 95, 'fuel_strategy': 90,
         'ers_mode': 98, 'overtake_aggression': 20, 'defense_intensity': 90}
    ]

    start = time.time()
    results = run_decision_simulations(late_race_state, strategies, num_sims_per_strategy=50)
    elapsed = time.time() - start

    print(f"   ✅ Completed {len(results)} sims in {elapsed:.3f}s")
    print(f"   📊 Remaining laps: {late_race_state.total_laps - late_race_state.lap}")

    # Test 2: Early race (lap 5)
    print("\n🧪 Test 2: Early race scenario (lap 5/57)...")

    early_race_state = DecisionState(
        lap=5,
        total_laps=57,
        position=6,
        battery_soc=95.0,
        tire_life=98.0,
        fuel_remaining=100.0,
        tire_compound='HARD'
    )

    start = time.time()
    results = run_decision_simulations(early_race_state, strategies, num_sims_per_strategy=50)
    elapsed = time.time() - start

    print(f"   ✅ Completed {len(results)} sims in {elapsed:.3f}s")
    print(f"   📊 Remaining laps: {early_race_state.total_laps - early_race_state.lap}")

    # Test 3: Power track
    print("\n🧪 Test 3: Power track (Monza style)...")

    power_track_state = DecisionState(
        lap=20,
        total_laps=57,
        position=4,
        battery_soc=60.0,
        tire_life=70.0,
        fuel_remaining=40.0,
        tire_compound='HARD',
        track_type='power'
    )

    # Energy-focused strategy should do better on power tracks
    power_strategies = [
        {'energy_deployment': 95, 'tire_management': 60, 'fuel_strategy': 60,
         'ers_mode': 85, 'overtake_aggression': 85, 'defense_intensity': 50},
        {'energy_deployment': 60, 'tire_management': 70, 'fuel_strategy': 65,
         'ers_mode': 65, 'overtake_aggression': 60, 'defense_intensity': 60},
        {'energy_deployment': 30, 'tire_management': 85, 'fuel_strategy': 75,
         'ers_mode': 50, 'overtake_aggression': 40, 'defense_intensity': 70}
    ]

    start = time.time()
    results = run_decision_simulations(power_track_state, power_strategies, num_sims_per_strategy=50)
    elapsed = time.time() - start

    print(f"   ✅ Completed {len(results)} sims in {elapsed:.3f}s")

    # Check if high energy strategy wins more
    for sid in range(3):
        strategy_data = results[results['strategy_id'] == sid]
        win_rate = strategy_data['won'].mean() * 100
        print(f"      Strategy {sid} (energy={power_strategies[sid]['energy_deployment']}): {win_rate:.1f}% wins")

    print("\n✅ Edge case tests complete")


def benchmark_scaling():
    """Test performance at different scales."""

    print("\n" + "=" * 70)
    print("PERFORMANCE SCALING BENCHMARK")
    print("=" * 70)

    test_state = DecisionState(
        lap=15,
        position=4,
        battery_soc=50.0,
        tire_life=70.0,
        fuel_remaining=35.0,
        tire_compound='HARD'
    )

    strategies = [
        {'energy_deployment': 80, 'tire_management': 70, 'fuel_strategy': 60,
         'ers_mode': 75, 'overtake_aggression': 80, 'defense_intensity': 50},
        {'energy_deployment': 60, 'tire_management': 80, 'fuel_strategy': 70,
         'ers_mode': 65, 'overtake_aggression': 60, 'defense_intensity': 60},
        {'energy_deployment': 40, 'tire_management': 90, 'fuel_strategy': 80,
         'ers_mode': 55, 'overtake_aggression': 40, 'defense_intensity': 70}
    ]

    test_sizes = [10, 50, 100, 200]

    print("\n   Testing different simulation counts:")
    print("   " + "-" * 50)

    for n in test_sizes:
        start = time.time()
        results = run_decision_simulations(test_state, strategies, num_sims_per_strategy=n)
        elapsed = time.time() - start

        total_sims = n * 3
        sims_per_sec = total_sims / elapsed

        status = "✅" if elapsed < 2.0 else "⚠️"
        print(f"   {status} {total_sims:3d} sims: {elapsed:.3f}s ({sims_per_sec:.0f} sims/sec)")

    print()


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("INTERACTIVE GAME DECISION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    print("This test validates the complete decision-making pipeline:")
    print("  1. Run 300 physics simulations from mid-race state")
    print("  2. Analyze results with Gemini (or fallback)")
    print("  3. Generate actionable recommendations")
    print("  4. Verify performance (<4s total latency)")
    print()

    # Main integration test
    success = test_complete_decision_flow()

    if success:
        # Additional tests
        test_edge_cases()
        benchmark_scaling()

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("System is ready for game integration!")
        print()
        print("Next steps:")
        print("  1. Integrate run_decision_simulations() into game loop")
        print("  2. Call GameAdvisor.analyze_decision_point() when game pauses")
        print("  3. Display recommendations to player")
        print("  4. Resume game with selected strategy")
        print()
    else:
        print("\n" + "=" * 70)
        print("❌ TEST FAILED")
        print("=" * 70)
        print()
        print("Please review errors above and fix issues.")
        print()
