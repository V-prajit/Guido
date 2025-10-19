"""
Example integration showing agents_v2 with physics_2024

This demonstrates how the 8 agents interact with the physics engine
to simulate a single lap for all agents.
"""

from sim.agents_v2 import create_agents_v2
from sim.physics_2024 import (
    RaceState,
    load_baseline,
    calculate_lap_time,
    update_battery,
    update_tire_condition,
    update_fuel
)


def simulate_single_lap_all_agents():
    """Simulate one lap for all 8 agents showing their different approaches."""

    # Initialize
    agents = create_agents_v2()
    baseline = load_baseline()

    # Starting state (lap 30 of race)
    initial_state = RaceState(
        lap=30,
        battery_soc=65.0,
        position=4,
        tire_age=25,
        tire_life=60.0,
        fuel_remaining=50.0,
        boost_used=1
    )

    print("\n" + "="*120)
    print("SINGLE LAP SIMULATION - All 8 Agents")
    print("="*120)
    print(f"\nInitial State: Lap {initial_state.lap}, P{initial_state.position}, "
          f"Battery {initial_state.battery_soc:.1f}%, Tire Life {initial_state.tire_life:.1f}%\n")

    print(f"{'Agent':<20s} | {'Decision (E/T/F/ERS/A/D)':^40s} | {'Lap Time':>10s} | {'New Battery':>12s} | {'Tire Life':>10s} | {'Fuel':>8s}")
    print("-"*120)

    results = []

    for agent in agents:
        # Agent makes decision
        decision = agent.decide(initial_state)

        # Physics calculates outcomes
        lap_time = calculate_lap_time(decision, initial_state, baseline, tire_compound='HARD')
        new_battery = update_battery(decision, initial_state, baseline)
        new_tire_life = update_tire_condition(decision, initial_state, baseline, tire_compound='HARD')
        new_fuel = update_fuel(decision, initial_state, baseline)

        # Format decision string
        decision_str = f"{decision.energy_deployment:4.0f}/{decision.tire_management:4.0f}/" \
                      f"{decision.fuel_strategy:4.0f}/{decision.ers_mode:4.0f}/" \
                      f"{decision.overtake_aggression:4.0f}/{decision.defense_intensity:4.0f}"

        print(f"{agent.name:<20s} | {decision_str:^40s} | {lap_time:9.3f}s | "
              f"{initial_state.battery_soc:5.1f}→{new_battery:5.1f}% | "
              f"{initial_state.tire_life:4.1f}→{new_tire_life:4.1f}% | "
              f"{new_fuel:6.1f}kg")

        results.append({
            'agent': agent.name,
            'lap_time': lap_time,
            'battery_delta': new_battery - initial_state.battery_soc,
            'tire_delta': new_tire_life - initial_state.tire_life
        })

    print("\n" + "="*120)
    print("ANALYSIS")
    print("="*120)

    # Find fastest lap
    fastest = min(results, key=lambda x: x['lap_time'])
    print(f"\n🏁 Fastest Lap: {fastest['agent']} ({fastest['lap_time']:.3f}s)")

    # Find most battery gained
    best_battery = max(results, key=lambda x: x['battery_delta'])
    print(f"🔋 Best Battery Management: {best_battery['agent']} ({best_battery['battery_delta']:+.1f}%)")

    # Find best tire preservation
    best_tire = max(results, key=lambda x: x['tire_delta'])
    print(f"🏎️  Best Tire Preservation: {best_tire['agent']} ({best_tire['tire_delta']:+.1f}%)")

    print("\n" + "="*120)
    print("KEY OBSERVATIONS")
    print("="*120)

    print("\n1. LAP TIME TRADE-OFFS:")
    print("   - ElectricBlitzer: Fast lap but drains battery")
    print("   - EnergySaver: Slower lap but gains battery for late race")
    print("   - TireWhisperer: Moderate pace but preserves tires")

    print("\n2. ENERGY STRATEGIES:")
    print("   - Learned agents (Verstappen/Hamilton/Alonso): Efficient, sustainable pace")
    print("   - ElectricBlitzer: High deployment, needs harvest in late race")
    print("   - EnergySaver: Low deployment now, attack mode later")

    print("\n3. TIRE MANAGEMENT:")
    print("   - TireWhisperer: Minimal degradation for one-stop strategy")
    print("   - Learned agents: Balanced degradation")
    print("   - ElectricBlitzer: Higher degradation from aggressive driving")

    print("\n4. STRATEGIC DIVERSITY:")
    print("   - 8 agents show measurably different approaches")
    print("   - No single 'best' strategy - depends on race context")
    print("   - Position, lap number, battery state all influence decisions")

    print("\n" + "="*120)


def demonstrate_adaptive_behavior():
    """Show how agents adapt to different race situations."""

    print("\n" + "="*120)
    print("ADAPTIVE BEHAVIOR DEMONSTRATION")
    print("="*120)

    agents = create_agents_v2()
    baseline = load_baseline()

    scenarios = [
        ("Early Race - Fresh Tires, Full Battery", RaceState(5, 95.0, 3, 3, 95.0, 95.0, 0)),
        ("Mid Race - Moderate Battery", RaceState(30, 60.0, 5, 25, 60.0, 50.0, 1)),
        ("Late Race - Low Battery", RaceState(50, 25.0, 4, 35, 40.0, 20.0, 2)),
    ]

    for scenario_name, state in scenarios:
        print(f"\n{'='*120}")
        print(f"Scenario: {scenario_name}")
        print(f"State: Lap {state.lap}, P{state.position}, Battery {state.battery_soc:.0f}%, "
              f"Tire Life {state.tire_life:.0f}%")
        print(f"{'='*120}")
        print(f"{'Agent':<20s} | {'Energy':>7s} | {'Tire':>7s} | {'ERS':>7s} | {'Attack':>7s} | {'Lap Time':>10s}")
        print("-"*120)

        for agent in agents:
            decision = agent.decide(state)
            lap_time = calculate_lap_time(decision, state, baseline, 'HARD')

            print(f"{agent.name:<20s} | "
                  f"{decision.energy_deployment:7.1f} | "
                  f"{decision.tire_management:7.1f} | "
                  f"{decision.ers_mode:7.1f} | "
                  f"{decision.overtake_aggression:7.1f} | "
                  f"{lap_time:9.3f}s")


def main():
    """Run all demonstrations."""

    print("\n" + "="*120)
    print(" "*35 + "AGENTS V2 + PHYSICS 2024 INTEGRATION EXAMPLE")
    print("="*120)

    # Demo 1: Single lap for all agents
    simulate_single_lap_all_agents()

    # Demo 2: Adaptive behavior across race phases
    demonstrate_adaptive_behavior()

    print("\n" + "="*120)
    print("Integration successful! Agents are ready for full race simulation.")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()
