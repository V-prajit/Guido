"""
Example: Using the 2024 and 2026 Physics Modules

This demonstrates how to use the physics modules to simulate realistic F1 races
with the 6 strategic control variables.
"""

from sim.physics_2024 import AgentDecision, RaceState, load_baseline
from sim.physics_2026 import calculate_lap_time, update_battery, update_tire_condition, update_fuel


def simulate_verstappen_2024_strategy():
    """
    Simulate Verstappen's 2024 Bahrain GP strategy.

    From learned_strategies.json:
    - energy_deployment: 29.5
    - tire_management: 100
    - fuel_strategy: 52.9
    - ers_mode: 35.4
    - overtake_aggression: 40
    - defense_intensity: 100
    """
    print("=" * 60)
    print("EXAMPLE 1: Verstappen's 2024 Bahrain GP Strategy")
    print("=" * 60)

    baseline = load_baseline()

    # Verstappen's actual strategy profile
    verstappen_decision = AgentDecision(
        energy_deployment=29.5,
        tire_management=100.0,  # Full push
        fuel_strategy=52.9,     # Slightly rich
        ers_mode=35.4,          # More harvest than deploy
        overtake_aggression=40.0,  # Conservative (started P1, didn't need to overtake)
        defense_intensity=100.0    # Maximum defense
    )

    # Lap 20 state (second stint on HARD tires)
    state = RaceState(
        lap=20,
        battery_soc=75.0,
        position=1,
        tire_age=3,  # Fresh HARD tires
        tire_life=95.0,
        fuel_remaining=70.0,
        boost_used=0
    )

    print(f"Lap {state.lap} (HARD tires, lap {state.tire_age})")
    print(f"Strategy: {verstappen_decision}")
    print()

    # Simulate with 2026 rules
    lap_time = calculate_lap_time(verstappen_decision, state, baseline, tire_compound='HARD')
    new_battery = update_battery(verstappen_decision, state, baseline)
    new_tire_life = update_tire_condition(verstappen_decision, state, baseline, tire_compound='HARD')
    new_fuel = update_fuel(verstappen_decision, state, baseline)

    print(f"Results:")
    print(f"  Lap time: {lap_time:.3f}s")
    print(f"  Battery: {state.battery_soc:.1f}% → {new_battery:.1f}%")
    print(f"  Tire life: {state.tire_life:.1f}% → {new_tire_life:.1f}%")
    print(f"  Fuel: {state.fuel_remaining:.1f}kg → {new_fuel:.1f}kg")
    print()

    # Simulate 10 laps
    print("Simulating 10 laps:")
    current_state = state
    for lap in range(10):
        lap_time = calculate_lap_time(verstappen_decision, current_state, baseline, tire_compound='HARD')
        new_battery = update_battery(verstappen_decision, current_state, baseline)
        new_tire_life = update_tire_condition(verstappen_decision, current_state, baseline, tire_compound='HARD')
        new_fuel = update_fuel(verstappen_decision, current_state, baseline)

        print(f"  Lap {current_state.lap}: {lap_time:.3f}s | Battery: {new_battery:.1f}% | Tire: {new_tire_life:.1f}% | Fuel: {new_fuel:.1f}kg")

        # Update state for next lap
        current_state = RaceState(
            lap=current_state.lap + 1,
            battery_soc=new_battery,
            position=1,
            tire_age=current_state.tire_age + 1,
            tire_life=new_tire_life,
            fuel_remaining=new_fuel,
            boost_used=0
        )

    print()


def compare_aggressive_vs_conservative():
    """
    Compare aggressive vs conservative energy strategies in 2026.
    """
    print("=" * 60)
    print("EXAMPLE 2: Aggressive vs Conservative Energy Strategy (2026)")
    print("=" * 60)

    baseline = load_baseline()

    # Aggressive: Deploy all battery early
    aggressive = AgentDecision(
        energy_deployment=100.0,  # Max deployment
        tire_management=50.0,
        fuel_strategy=50.0,
        ers_mode=80.0,  # Mostly deploy, little harvest
        overtake_aggression=80.0,
        defense_intensity=60.0
    )

    # Conservative: Save battery, harvest more
    conservative = AgentDecision(
        energy_deployment=30.0,  # Low deployment
        tire_management=50.0,
        fuel_strategy=50.0,
        ers_mode=20.0,  # Heavy harvest
        overtake_aggression=50.0,
        defense_intensity=60.0
    )

    state = RaceState(
        lap=10,
        battery_soc=80.0,
        position=3,
        tire_age=10,
        tire_life=85.0,
        fuel_remaining=80.0,
        boost_used=0
    )

    # Simulate both strategies
    agg_time = calculate_lap_time(aggressive, state, baseline)
    agg_battery = update_battery(aggressive, state, baseline)

    con_time = calculate_lap_time(conservative, state, baseline)
    con_battery = update_battery(conservative, state, baseline)

    print("Aggressive Strategy (100% deployment):")
    print(f"  Lap time: {agg_time:.3f}s")
    print(f"  Battery: {state.battery_soc:.1f}% → {agg_battery:.1f}% (drain: {state.battery_soc - agg_battery:.1f}%)")
    print()

    print("Conservative Strategy (30% deployment):")
    print(f"  Lap time: {con_time:.3f}s")
    print(f"  Battery: {state.battery_soc:.1f}% → {con_battery:.1f}% (gain: {con_battery - state.battery_soc:.1f}%)")
    print()

    print(f"Time difference: {con_time - agg_time:.3f}s (aggressive is faster)")
    print(f"Battery difference: {(state.battery_soc - agg_battery) - (con_battery - state.battery_soc):.1f}% swing")
    print()

    print("Strategic insight:")
    print("  - Aggressive: Fast early laps, but depletes battery quickly")
    print("  - Conservative: Slower laps, but maintains/builds battery charge")
    print("  - 2026 amplifies this trade-off due to 3x electric power")
    print()


def demonstrate_strategic_complexity():
    """
    Show how multiple variables interact to create complex strategic choices.
    """
    print("=" * 60)
    print("EXAMPLE 3: Strategic Complexity - Multiple Variables")
    print("=" * 60)

    baseline = load_baseline()

    # Scenario 1: Overtaking attempt (low battery, need speed)
    print("SCENARIO 1: Overtaking Attempt")
    print("Situation: P4, chasing P3, gap 0.8s, low battery (35%)")
    print()

    overtake_state = RaceState(
        lap=40,
        battery_soc=35.0,  # Low battery!
        position=4,
        tire_age=15,
        tire_life=60.0,
        fuel_remaining=35.0,
        boost_used=1
    )

    # Option A: Deploy remaining battery for overtake
    deploy_all = AgentDecision(
        energy_deployment=90.0,  # Risk it
        tire_management=85.0,    # Push hard
        fuel_strategy=70.0,      # Rich mixture
        ers_mode=90.0,           # Deploy
        overtake_aggression=95.0,  # Go for it!
        defense_intensity=40.0
    )

    # Option B: Conserve for late race
    conserve = AgentDecision(
        energy_deployment=20.0,
        tire_management=40.0,
        fuel_strategy=30.0,  # Lean
        ers_mode=10.0,       # Harvest
        overtake_aggression=30.0,
        defense_intensity=40.0
    )

    deploy_time = calculate_lap_time(deploy_all, overtake_state, baseline)
    deploy_battery = update_battery(deploy_all, overtake_state, baseline)

    conserve_time = calculate_lap_time(conserve, overtake_state, baseline)
    conserve_battery = update_battery(conserve, overtake_state, baseline)

    print("Option A - Deploy All:")
    print(f"  Lap time: {deploy_time:.3f}s (chase down P3)")
    print(f"  Battery after: {deploy_battery:.1f}% (CRITICAL!)")
    print(f"  Risk: May not finish race with power")
    print()

    print("Option B - Conserve:")
    print(f"  Lap time: {conserve_time:.3f}s (lose 0.8s to P3)")
    print(f"  Battery after: {conserve_battery:.1f}% (recovering)")
    print(f"  Benefit: Can attack in final laps")
    print()

    print(f"Trade-off: {conserve_time - deploy_time:.3f}s slower, but {conserve_battery - deploy_battery:.1f}% more battery")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("PHYSICS MODULE USAGE EXAMPLES")
    print("=" * 60)
    print()

    # Example 1: Real driver strategy
    simulate_verstappen_2024_strategy()

    # Example 2: Compare strategies
    compare_aggressive_vs_conservative()

    # Example 3: Complex strategic decisions
    demonstrate_strategic_complexity()

    print("=" * 60)
    print("These examples demonstrate:")
    print("  1. All 6 strategic variables have real impact")
    print("  2. 2026 regulations amplify energy management trade-offs")
    print("  3. Complex multi-variable decisions create emergent strategy")
    print("  4. Physics are realistic but fast (optimized for 1000+ sims)")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
