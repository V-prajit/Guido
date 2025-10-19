#!/usr/bin/env python3
"""
Test API Integration with New 6-Variable System

This script verifies that all API integration components work correctly
with the new realistic physics engine and 6-variable agent decision system.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sim.engine import simulate_race
from sim.agents_v2 import create_agents_v2
from sim.scenarios import generate_scenarios
from api.analysis import aggregate_results
from api.recommend import get_recommendations_fast
import pandas as pd
import json

def test_simulation():
    """Test 1: Run simulation with new engine"""
    print("\n=== Test 1: Simulation Engine ===")

    scenarios = generate_scenarios(3, seed=42)
    agents = create_agents_v2()
    df = simulate_race(scenarios[0], agents, use_2026_rules=True)

    print(f"✓ Simulation ran successfully")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Column names: {list(df.columns)}")

    # Verify expected columns
    expected_cols = [
        'agent', 'lap', 'battery_soc', 'tire_life', 'fuel_remaining',
        'lap_time', 'cumulative_time', 'final_position', 'won',
        'energy_deployment', 'tire_management', 'fuel_strategy',
        'ers_mode', 'overtake_aggression', 'defense_intensity'
    ]

    missing_cols = set(expected_cols) - set(df.columns)
    if missing_cols:
        print(f"✗ Missing columns: {missing_cols}")
        return False

    print(f"✓ All expected columns present")

    # Check data types and ranges
    assert df['battery_soc'].between(0, 100).all(), "Battery SOC out of range"
    assert df['tire_life'].between(0, 100).all(), "Tire life out of range"
    assert df['fuel_remaining'].between(0, 120).all(), "Fuel out of range"
    assert df['energy_deployment'].between(0, 100).all(), "Energy deployment out of range"
    assert df['tire_management'].between(0, 100).all(), "Tire management out of range"

    print(f"✓ Data types and ranges valid")

    return df

def test_aggregation(df):
    """Test 2: Aggregation with new metrics"""
    print("\n=== Test 2: Results Aggregation ===")

    # Add scenario_id for aggregation
    df['scenario_id'] = 0

    # Save to temp CSV
    temp_csv = '/tmp/test_integration.csv'
    df.to_csv(temp_csv, index=False)

    stats = aggregate_results(temp_csv)

    print(f"✓ Aggregation works")
    print(f"  Agents analyzed: {len(stats)}")

    # Check one agent's stats
    first_agent = list(stats.keys())[0]
    agent_stats = stats[first_agent]

    print(f"\n  Sample agent '{first_agent}':")
    print(f"    Wins: {agent_stats['wins']}")
    print(f"    Win rate: {agent_stats['win_rate']:.1f}%")
    print(f"    Avg position: {agent_stats['avg_position']:.2f}")

    # Verify new metrics exist
    new_metrics = [
        'avg_final_battery', 'avg_final_tire_life', 'avg_final_fuel',
        'avg_energy_deployment', 'avg_tire_management', 'avg_fuel_strategy',
        'avg_ers_mode', 'avg_overtake_aggression', 'avg_defense_intensity'
    ]

    for metric in new_metrics:
        if metric not in agent_stats:
            print(f"✗ Missing metric: {metric}")
            return False
        print(f"    {metric}: {agent_stats[metric]:.2f}")

    print(f"\n✓ All new metrics present and valid")

    os.remove(temp_csv)
    return True

def test_recommendations():
    """Test 3: Recommendations with 6 variables"""
    print("\n=== Test 3: Recommendations Engine ===")

    # Test different scenarios
    test_queries = [
        {
            'name': 'Early race, full battery',
            'state': {
                'lap': 10,
                'battery_soc': 85,
                'position': 5,
                'tire_age': 10,
                'tire_life': 90,
                'fuel_remaining': 100
            }
        },
        {
            'name': 'Low battery late race',
            'state': {
                'lap': 50,
                'battery_soc': 25,
                'position': 3,
                'tire_age': 40,
                'tire_life': 45,
                'fuel_remaining': 30
            }
        },
        {
            'name': 'Leader final laps',
            'state': {
                'lap': 55,
                'battery_soc': 60,
                'position': 1,
                'tire_age': 35,
                'tire_life': 55,
                'fuel_remaining': 15
            }
        }
    ]

    for query in test_queries:
        print(f"\n  Testing: {query['name']}")
        recommendations, conditions, seed = get_recommendations_fast(query['state'])

        if not recommendations:
            print(f"    ✗ No recommendations returned")
            return False

        print(f"    ✓ {len(recommendations)} recommendation(s)")

        for rec in recommendations:
            print(f"      Rule: {rec['rule']}")
            print(f"      Confidence: {rec['confidence']:.2f}")

            # Verify 6 variables in action
            action = rec['action']
            expected_vars = [
                'energy_deployment', 'tire_management', 'fuel_strategy',
                'ers_mode', 'overtake_aggression', 'defense_intensity'
            ]

            missing_vars = set(expected_vars) - set(action.keys())
            if missing_vars:
                print(f"      ✗ Missing action variables: {missing_vars}")
                return False

            print(f"      Action: ED={action['energy_deployment']}, TM={action['tire_management']}, " +
                  f"FS={action['fuel_strategy']}, ERS={action['ers_mode']}, " +
                  f"OA={action['overtake_aggression']}, DI={action['defense_intensity']}")

    print(f"\n✓ Recommendations engine working with 6 variables")
    return True

def test_playbook_schema():
    """Test 4: Playbook schema validation"""
    print("\n=== Test 4: Playbook Schema ===")

    with open('data/playbook.json', 'r') as f:
        playbook = json.load(f)

    print(f"✓ Playbook loaded")
    print(f"  Rules: {len(playbook['rules'])}")
    print(f"  Schema version: {playbook.get('schema_version', 'N/A')}")

    # Verify variables list
    if 'variables' in playbook:
        print(f"  Variables: {', '.join(playbook['variables'])}")
        expected_vars = [
            'energy_deployment', 'tire_management', 'fuel_strategy',
            'ers_mode', 'overtake_aggression', 'defense_intensity'
        ]
        if set(playbook['variables']) != set(expected_vars):
            print(f"✗ Variables mismatch")
            return False

    # Verify each rule has 6 variables
    for i, rule in enumerate(playbook['rules']):
        action = rule['action']
        if len(action) != 6:
            print(f"✗ Rule {i} has {len(action)} variables, expected 6")
            return False

    print(f"✓ All rules have 6-variable actions")
    return True

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("API Integration Test Suite")
    print("Testing new 6-variable system with realistic physics")
    print("=" * 60)

    try:
        # Test 1: Simulation
        df = test_simulation()
        if df is None:
            print("\n✗ Simulation test failed")
            return False

        # Test 2: Aggregation
        if not test_aggregation(df):
            print("\n✗ Aggregation test failed")
            return False

        # Test 3: Recommendations
        if not test_recommendations():
            print("\n✗ Recommendations test failed")
            return False

        # Test 4: Playbook schema
        if not test_playbook_schema():
            print("\n✗ Playbook schema test failed")
            return False

        print("\n" + "=" * 60)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        print("\nAPI integration layer is ready for:")
        print("  - New realistic physics engine")
        print("  - 6-variable agent decision system")
        print("  - Enhanced DataFrame output (15 columns)")
        print("  - Updated playbook schema v2.0")
        print("  - Resource management metrics (tire, fuel, battery)")

        return True

    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
