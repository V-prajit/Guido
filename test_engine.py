"""
Test script for H0-H1 checkpoint: Core Engine Skeleton

This script verifies that the basic simulation engine works correctly
by running a simple 10-lap race with a dummy agent.
"""

from sim.engine import Agent, RaceState, simulate_race


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


def main():
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


if __name__ == "__main__":
    main()
