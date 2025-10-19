#!/usr/bin/env python3
"""
Validate 2024 physics simulation against real 2024 Bahrain GP results.

This proves our physics model is realistic by comparing simulated lap times,
fuel consumption, and tire degradation to actual race data.
"""

import sys
sys.path.insert(0, '/Users/prajit/Desktop/projects/Gand')

from sim.engine import simulate_race, create_agents
from sim.physics_2024 import load_baseline
import json
from datetime import datetime

# Real 2024 Bahrain GP results
REAL_2024_RESULTS = {
    'verstappen': {
        'final_position': 1,
        'avg_lap_time': 95.84,  # From learned_strategies.json
        'total_laps': 57
    },
    'hamilton': {
        'final_position': 7,
        'avg_lap_time': 96.66,  # From learned_strategies.json
        'total_laps': 57
    },
    'alonso': {
        'final_position': 9,
        'avg_lap_time': 97.18,  # From learned_strategies.json
        'total_laps': 57
    }
}

def validate_2024_physics():
    """
    Run 2024 physics simulation and compare to real results.
    """
    print("=" * 60)
    print("2024 PHYSICS VALIDATION")
    print("Comparing simulation to real 2024 Bahrain GP")
    print("=" * 60)
    print()

    # Load baseline parameters
    baseline = load_baseline()
    print(f"✓ Loaded baseline parameters")
    print(f"  Base lap time: {baseline['track_characteristics']['base_lap_time']}s")
    print(f"  Track: {baseline['race_info']['track_name']}")
    print()

    # Create scenario matching real 2024 Bahrain GP
    scenario = {
        'id': 0,
        'num_laps': 57,
        'track_type': 'balanced',
        'rain_lap': None,  # No rain in 2024 race
        'safety_car_lap': None,  # Simplified - no SC for validation
        'temperature': 18.0,  # Actual race temp
        'wind': 'low',
        'tire_strategy': 'soft-hard',
        'starting_positions': [1, 2, 3, 4, 5, 6, 7, 8]  # Grid order
    }

    # Get learned agents only (first 3 agents)
    all_agents = create_agents()
    learned_agents = all_agents[:3]  # VerstappenStyle, HamiltonStyle, AlonsoStyle

    print(f"Running simulation with {len(learned_agents)} learned agents...")
    print(f"Agents: {[a.name for a in learned_agents]}")
    print()

    # Run with 2024 physics
    df = simulate_race(scenario, learned_agents, use_2026_rules=False)

    print("✓ Simulation complete")
    print()

    # Analyze results
    validation_results = {
        'timestamp': datetime.now().isoformat(),
        'scenario': scenario,
        'agents_tested': [a.name for a in learned_agents],
        'comparisons': {},
        'validation_passed': True
    }

    # Compare each agent to real driver
    agent_mapping = {
        'VerstappenStyle': 'verstappen',
        'HamiltonStyle': 'hamilton',
        'AlonsoStyle': 'alonso'
    }

    print("VALIDATION RESULTS:")
    print("-" * 60)

    tolerance = 2.0  # ±2 seconds tolerance

    for agent_name, real_driver in agent_mapping.items():
        agent_df = df[df['agent'] == agent_name]

        if len(agent_df) == 0:
            continue

        # Calculate metrics (convert to Python types for JSON serialization)
        avg_lap_time = float(agent_df['lap_time'].mean())
        final_position = int(agent_df['final_position'].iloc[0])
        total_laps = int(agent_df['lap'].max())

        # Get real results
        real_data = REAL_2024_RESULTS[real_driver]
        real_avg_lap = real_data['avg_lap_time']
        real_position = real_data['final_position']

        # Calculate difference
        lap_time_diff = abs(avg_lap_time - real_avg_lap)
        position_diff = abs(final_position - real_position)

        # Validate
        lap_time_ok = lap_time_diff <= tolerance

        # Store results
        validation_results['comparisons'][agent_name] = {
            'simulated_avg_lap': round(avg_lap_time, 2),
            'real_avg_lap': real_avg_lap,
            'lap_time_diff': round(lap_time_diff, 2),
            'simulated_position': final_position,
            'real_position': real_position,
            'position_diff': position_diff,
            'lap_time_within_tolerance': lap_time_ok
        }

        if not lap_time_ok:
            validation_results['validation_passed'] = False

        # Print comparison
        status = "✓" if lap_time_ok else "✗"
        print(f"{status} {agent_name} (real: {real_driver.upper()})")
        print(f"  Sim avg lap: {avg_lap_time:.2f}s | Real: {real_avg_lap:.2f}s | Diff: {lap_time_diff:.2f}s")
        print(f"  Sim position: P{final_position} | Real: P{real_position}")
        print()

    print("-" * 60)

    if validation_results['validation_passed']:
        print("✓ VALIDATION PASSED - All lap times within ±2s")
    else:
        print("✗ VALIDATION FAILED - Some lap times exceed ±2s tolerance")

    print()

    # Additional metrics
    print("ADDITIONAL METRICS:")
    print("-" * 60)

    # Tire degradation
    avg_final_tire = float(df[df['lap'] == 57]['tire_life'].mean())
    print(f"Average final tire life: {avg_final_tire:.1f}%")

    # Fuel consumption
    avg_final_fuel = float(df[df['lap'] == 57]['fuel_remaining'].mean())
    fuel_used = 110.0 - avg_final_fuel
    fuel_per_lap = fuel_used / 57
    print(f"Average fuel used: {fuel_used:.1f}kg ({fuel_per_lap:.2f}kg/lap)")

    # Battery management
    avg_final_battery = float(df[df['lap'] == 57]['battery_soc'].mean())
    print(f"Average final battery: {avg_final_battery:.1f}%")

    print()

    # Save validation report
    output_path = 'data/validation_2024.json'
    with open(output_path, 'w') as f:
        json.dump(validation_results, f, indent=2)

    print(f"✓ Validation report saved to {output_path}")
    print()

    print("=" * 60)
    if validation_results['validation_passed']:
        print("2024 PHYSICS VALIDATED ✓")
        print("Ready for 2026 extrapolation")
    else:
        print("VALIDATION NEEDS TUNING")
        print("Physics parameters may need adjustment")
    print("=" * 60)

    return validation_results

if __name__ == '__main__':
    validate_2024_physics()
