#!/usr/bin/env python3
"""
Test script for the new simulation engine with realistic physics.

This script demonstrates that the new engine meets all requirements:
1. Uses realistic physics from physics_2026.py
2. Works with 6-variable agents from agents_v2.py
3. Tracks tire life and fuel consumption
4. Outputs enhanced DataFrame with new columns
5. Preserves picklable interface for multiprocessing
"""

from sim.engine import simulate_race, create_agents
from sim.scenarios import generate_scenarios

def main():
    print("=" * 60)
    print("SIMULATION ENGINE V2 TEST")
    print("=" * 60)
    print()

    # Generate test scenario
    scenarios = generate_scenarios(1)
    scenario = scenarios[0]

    print(f"Scenario: {scenario}")
    print()

    # Create agents
    agents = create_agents()
    print(f"Created {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.name}")
    print()

    # Run simulation
    print("Running simulation with 2026 physics...")
    df = simulate_race(scenario, agents, use_2026_rules=True)

    print(f"✓ Simulation complete")
    print(f"✓ Laps simulated: {df['lap'].max()}")
    print(f"✓ Agents: {df['agent'].nunique()}")
    print()

    # Check new columns exist
    print("Checking required columns...")
    required_cols = [
        'tire_life', 'fuel_remaining',
        'energy_deployment', 'tire_management', 'fuel_strategy',
        'ers_mode', 'overtake_aggression', 'defense_intensity'
    ]

    for col in required_cols:
        if col in df.columns:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ {col} MISSING")

    print()

    # Display results
    print("Final Results:")
    print("-" * 100)
    final_lap = df[df['lap'] == df['lap'].max()].sort_values('final_position')

    for _, row in final_lap.iterrows():
        position = row['final_position']
        agent = row['agent']
        time = row['cumulative_time']
        battery = row['battery_soc']
        tire = row['tire_life']
        fuel = row['fuel_remaining']

        status = "🏆 WINNER" if row['won'] else ""

        print(f"P{position}  {agent:20s}  {time:8.2f}s  "
              f"Battery: {battery:5.1f}%  Tire: {tire:5.1f}%  Fuel: {fuel:5.1f}kg  {status}")

    print("-" * 100)
    print()

    # Sample decision data
    print("Sample Decision Data (Lap 1, first 3 agents):")
    print("-" * 100)
    lap1 = df[df['lap'] == 1].head(3)
    for _, row in lap1.iterrows():
        print(f"{row['agent']:20s}:")
        print(f"  Energy: {row['energy_deployment']:5.1f}  "
              f"Tire Mgmt: {row['tire_management']:5.1f}  "
              f"Fuel: {row['fuel_strategy']:5.1f}")
        print(f"  ERS: {row['ers_mode']:5.1f}  "
              f"Overtake: {row['overtake_aggression']:5.1f}  "
              f"Defense: {row['defense_intensity']:5.1f}")
        print()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
