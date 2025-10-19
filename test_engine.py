"""
Test script for H0-H1 and H1-H2 checkpoints

H0-H1: Core Engine Skeleton - Basic simulation functionality
H1-H2: Scenario Generation - Diverse scenario generation and validation
"""

from sim.engine import Agent, RaceState, simulate_race
from sim.scenarios import generate_scenarios
from collections import Counter


class DummyAgent(Agent):
    """
    Simple test agent with balanced deployment strategy.

    Uses 50% deployment on straights and corners, 50% harvesting.
    Never uses boost.
    """

    def decide(self, state: RaceState):
        return {
            'deploy_straight': 50,
            'deploy_corner': 50,
            'harvest': 50,
            'use_boost': False
        }


def test_h0_h1():
    """Test H0-H1: Core Engine Skeleton"""
    print("=" * 60)
    print("H0-H1 Checkpoint Test: Core Engine Skeleton")
    print("=" * 60)

    # Create test scenario (10 lap race)
    scenario = {'num_laps': 10}

    # Create test agent
    agents = [DummyAgent("Test_Agent", {})]

    print("\nRunning 10-lap test race with DummyAgent...")
    print(f"Agent strategy: 50% deploy, 50% harvest\n")

    # Run simulation
    df = simulate_race(scenario, agents)

    # Display results
    print("Lap-by-Lap Results:")
    print("-" * 60)
    print(df[['lap', 'battery_soc', 'lap_time', 'cumulative_time']].to_string(index=False))

    # Summary statistics
    print("\n" + "=" * 60)
    print("Race Summary:")
    print("=" * 60)
    total_time = df['cumulative_time'].max()
    final_battery = df[df['lap'] == 10]['battery_soc'].values[0]
    avg_lap_time = df['lap_time'].mean()
    min_lap_time = df['lap_time'].min()
    max_lap_time = df['lap_time'].max()

    print(f"Total race time: {total_time:.2f}s")
    print(f"Final battery SOC: {final_battery:.1f}%")
    print(f"Average lap time: {avg_lap_time:.3f}s")
    print(f"Fastest lap: {min_lap_time:.3f}s")
    print(f"Slowest lap: {max_lap_time:.3f}s")

    # Validation checks
    print("\n" + "=" * 60)
    print("Validation Checks:")
    print("=" * 60)

    checks_passed = 0
    total_checks = 4

    # Check 1: Battery SOC within bounds
    if df['battery_soc'].min() >= 0 and df['battery_soc'].max() <= 100:
        print("✅ Battery SOC stays within [0, 100]")
        checks_passed += 1
    else:
        print("❌ Battery SOC out of bounds!")

    # Check 2: Lap times reasonable
    if 85 <= avg_lap_time <= 95:
        print("✅ Average lap time in reasonable range (85-95s)")
        checks_passed += 1
    else:
        print("❌ Average lap time outside expected range!")

    # Check 3: DataFrame has correct columns
    expected_cols = {'agent', 'lap', 'battery_soc', 'lap_time', 'cumulative_time', 'final_position', 'won'}
    if set(df.columns) == expected_cols:
        print("✅ DataFrame has all required columns")
        checks_passed += 1
    else:
        print("❌ DataFrame missing columns!")

    # Check 4: Correct number of rows
    if len(df) == 10:
        print("✅ Correct number of rows (10 laps)")
        checks_passed += 1
    else:
        print(f"❌ Expected 10 rows, got {len(df)}")

    # Final verdict
    print("\n" + "=" * 60)
    if checks_passed == total_checks:
        print(f"🎉 H0-H1 CHECKPOINT PASSED ({checks_passed}/{total_checks} checks)")
        print("Core engine skeleton is working correctly!")
    else:
        print(f"⚠️  CHECKPOINT INCOMPLETE ({checks_passed}/{total_checks} checks passed)")
        print("Review failed checks above.")
    print("=" * 60)

    return checks_passed == total_checks


def test_h1_h2():
    """Test H1-H2: Scenario Generation"""
    print("\n\n" + "=" * 60)
    print("H1-H2 Checkpoint Test: Scenario Generation")
    print("=" * 60)

    # Generate 100 scenarios
    print("\nGenerating 100 diverse scenarios...")
    scenarios = generate_scenarios(100)
    print(f"✅ Generated {len(scenarios)} scenarios")

    # Analyze scenario diversity
    print("\n" + "=" * 60)
    print("Scenario Diversity Analysis:")
    print("=" * 60)

    # Lap count distribution
    lap_counts = Counter(s['num_laps'] for s in scenarios)
    print("\nLap Count Distribution:")
    for laps, count in sorted(lap_counts.items()):
        print(f"  {laps} laps: {count}/100 ({count}%)")

    # Track type distribution
    track_types = Counter(s['track_type'] for s in scenarios)
    print("\nTrack Type Distribution:")
    for track, count in sorted(track_types.items()):
        print(f"  {track}: {count}/100 ({count}%)")

    # Rain events
    rain_count = sum(1 for s in scenarios if s['rain_lap'] is not None)
    print(f"\nRain Events: {rain_count}/100 ({rain_count}%)")
    print(f"  Expected ~25%, Got {rain_count}%")

    # Safety car events
    sc_count = sum(1 for s in scenarios if s['safety_car_lap'] is not None)
    print(f"\nSafety Car Events: {sc_count}/100 ({sc_count}%)")
    print(f"  Expected ~33%, Got {sc_count}%")

    # Temperature range
    temps = [s['temperature'] for s in scenarios]
    print(f"\nTemperature Range: {min(temps):.1f}°C - {max(temps):.1f}°C")
    print(f"  Expected: 20.0°C - 35.0°C")

    # Test rain penalty with a specific scenario
    print("\n" + "=" * 60)
    print("Testing Rain Penalty:")
    print("=" * 60)

    # Create a scenario with known rain lap
    rain_scenario = {
        'num_laps': 10,
        'rain_lap': 5,
        'safety_car_lap': None,
        'track_type': 'balanced',
        'temperature': 25.0
    }

    print("\nRunning 10-lap race with rain on lap 5...")
    agent = DummyAgent("Rain_Test", {})
    df = simulate_race(rain_scenario, [agent])

    # Check lap times before and after rain
    lap_4_time = df[df['lap'] == 4]['lap_time'].values[0]
    lap_5_time = df[df['lap'] == 5]['lap_time'].values[0]
    lap_6_time = df[df['lap'] == 6]['lap_time'].values[0]

    print(f"Lap 4 (before rain): {lap_4_time:.3f}s")
    print(f"Lap 5 (rain lap):    {lap_5_time:.3f}s")
    print(f"Lap 6 (after rain):  {lap_6_time:.3f}s")

    rain_penalty = lap_5_time - lap_4_time
    print(f"\nRain penalty: {rain_penalty:.3f}s")
    print(f"Expected: ~2.0s (may vary slightly due to battery changes)")

    # Run multiple scenarios to verify variety
    print("\n" + "=" * 60)
    print("Running Sample Scenarios:")
    print("=" * 60)

    print("\nRunning 10 diverse scenarios with DummyAgent...")
    sample_scenarios = scenarios[:10]
    results = []

    for scenario in sample_scenarios:
        df = simulate_race(scenario, [DummyAgent("Test", {})])
        total_time = df['cumulative_time'].max()
        final_battery = df[df['lap'] == df['lap'].max()]['battery_soc'].values[0]
        results.append({
            'id': scenario['id'],
            'laps': scenario['num_laps'],
            'rain': scenario['rain_lap'] is not None,
            'time': total_time,
            'battery': final_battery
        })

    print("\nResults:")
    print(f"{'ID':<4} {'Laps':<6} {'Rain':<6} {'Time':<10} {'Battery':<8}")
    print("-" * 40)
    for r in results:
        rain_str = f"L{sample_scenarios[r['id']]['rain_lap']}" if r['rain'] else "No"
        print(f"{r['id']:<4} {r['laps']:<6} {rain_str:<6} {r['time']:<10.2f} {r['battery']:<8.1f}%")

    # Validation checks
    print("\n" + "=" * 60)
    print("Validation Checks:")
    print("=" * 60)

    checks_passed = 0
    total_checks = 6

    # Check 1: Correct number of scenarios
    if len(scenarios) == 100:
        print("✅ Generated exactly 100 scenarios")
        checks_passed += 1
    else:
        print(f"❌ Expected 100 scenarios, got {len(scenarios)}")

    # Check 2: All lap counts are valid
    if all(s['num_laps'] in [50, 57, 70] for s in scenarios):
        print("✅ All lap counts are valid (50, 57, or 70)")
        checks_passed += 1
    else:
        print("❌ Invalid lap counts found")

    # Check 3: Rain probability roughly 25% (allow 15-35% range for randomness)
    if 15 <= rain_count <= 35:
        print("✅ Rain probability in expected range (~25%)")
        checks_passed += 1
    else:
        print(f"❌ Rain probability outside expected range: {rain_count}%")

    # Check 4: Safety car probability roughly 33% (allow 23-43% range)
    if 23 <= sc_count <= 43:
        print("✅ Safety car probability in expected range (~33%)")
        checks_passed += 1
    else:
        print(f"❌ Safety car probability outside expected range: {sc_count}%")

    # Check 5: Temperature range is correct
    if 20.0 <= min(temps) and max(temps) <= 35.0:
        print("✅ Temperature range correct (20-35°C)")
        checks_passed += 1
    else:
        print("❌ Temperature range incorrect")

    # Check 6: Rain penalty is approximately 2.0s (allow 1.8-2.2s for battery variance)
    if 1.8 <= rain_penalty <= 2.2:
        print("✅ Rain penalty approximately 2.0s")
        checks_passed += 1
    else:
        print(f"❌ Rain penalty outside expected range: {rain_penalty:.3f}s")

    # Final verdict
    print("\n" + "=" * 60)
    if checks_passed == total_checks:
        print(f"🎉 H1-H2 CHECKPOINT PASSED ({checks_passed}/{total_checks} checks)")
        print("Scenario generation is working correctly!")
        print("Ready to proceed to H2-H3: Eight Agent Implementations")
    else:
        print(f"⚠️  CHECKPOINT INCOMPLETE ({checks_passed}/{total_checks} checks passed)")
        print("Review failed checks above.")
    print("=" * 60)

    return checks_passed == total_checks


def main():
    """Run all checkpoint tests"""
    h0_h1_passed = test_h0_h1()
    h1_h2_passed = test_h1_h2()

    # Overall summary
    print("\n\n" + "=" * 60)
    print("OVERALL TEST SUMMARY")
    print("=" * 60)
    print(f"H0-H1 (Core Engine):      {'✅ PASSED' if h0_h1_passed else '❌ FAILED'}")
    print(f"H1-H2 (Scenario Gen):     {'✅ PASSED' if h1_h2_passed else '❌ FAILED'}")
    print("=" * 60)

    if h0_h1_passed and h1_h2_passed:
        print("🎉 ALL CHECKPOINTS PASSED!")
        print("Ready to proceed to H2-H3: Eight Agent Implementations")
    else:
        print("⚠️  Some checkpoints failed. Review above for details.")
    print("=" * 60)


if __name__ == "__main__":
    main()
