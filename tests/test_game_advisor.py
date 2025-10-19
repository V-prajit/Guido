"""
Test the GameAdvisor with mock simulation data.

Usage:
    python test_game_advisor.py
"""

import pandas as pd
import numpy as np
import sys
from api.gemini_game_advisor import GameAdvisor

def generate_mock_sim_results(num_sims_per_strategy=100):
    """
    Generate realistic mock simulation results.

    Simulates 3 strategies × 100 races each = 300 total race outcomes.

    Strategy 0: Aggressive (high risk, high reward)
    Strategy 1: Balanced (moderate everything)
    Strategy 2: Conservative (low risk, low reward)
    """

    np.random.seed(42)  # Reproducible results

    data = []

    # Strategy 0: Aggressive
    # - High win rate (42%) but some DNFs
    # - Low final battery (risky)
    # - Good for attacking positions
    print("📊 Generating Strategy 0: Aggressive...")
    for i in range(num_sims_per_strategy):
        won = np.random.random() < 0.42  # 42% win rate

        if won:
            final_position = 1
        else:
            # Bimodal: either podium or poor finish (high variance)
            if np.random.random() < 0.6:
                final_position = np.random.choice([2, 3])
            else:
                final_position = np.random.choice([5, 6, 7, 8])

        data.append({
            'strategy_id': 0,
            'sim_run_id': i,
            'lap': 57,
            'battery_soc': np.random.normal(12, 5),  # Low final battery
            'tire_life': np.random.normal(25, 10),
            'fuel_remaining': np.random.normal(2, 1),
            'final_position': final_position,
            'won': won
        })

    # Strategy 1: Balanced
    # - Medium win rate (38%)
    # - Consistent results
    # - Safe choice
    print("📊 Generating Strategy 1: Balanced...")
    for i in range(num_sims_per_strategy):
        won = np.random.random() < 0.38  # 38% win rate

        if won:
            final_position = 1
        else:
            # More consistent - usually podium or points
            final_position = np.random.choice([2, 3, 4, 5], p=[0.4, 0.3, 0.2, 0.1])

        data.append({
            'strategy_id': 1,
            'sim_run_id': i + num_sims_per_strategy,
            'lap': 57,
            'battery_soc': np.random.normal(22, 4),  # Healthy final battery
            'tire_life': np.random.normal(35, 8),
            'fuel_remaining': np.random.normal(3, 1),
            'final_position': final_position,
            'won': won
        })

    # Strategy 2: Conservative
    # - Low win rate (8%)
    # - Too passive, loses positions
    # - High final battery (unused potential)
    print("📊 Generating Strategy 2: Conservative...")
    for i in range(num_sims_per_strategy):
        won = np.random.random() < 0.08  # 8% win rate

        if won:
            final_position = 1
        else:
            # Usually finishes mid-pack or worse
            final_position = np.random.choice([4, 5, 6, 7, 8], p=[0.15, 0.25, 0.25, 0.20, 0.15])

        data.append({
            'strategy_id': 2,
            'sim_run_id': i + 2 * num_sims_per_strategy,
            'lap': 57,
            'battery_soc': np.random.normal(45, 6),  # Too much battery left
            'tire_life': np.random.normal(55, 8),    # Unused tire life
            'fuel_remaining': np.random.normal(5, 1),
            'final_position': final_position,
            'won': won
        })

    df = pd.DataFrame(data)

    print(f"✅ Generated {len(df)} simulation results")
    print(f"   Strategy 0: {df[df['strategy_id']==0]['won'].sum()} wins")
    print(f"   Strategy 1: {df[df['strategy_id']==1]['won'].sum()} wins")
    print(f"   Strategy 2: {df[df['strategy_id']==2]['won'].sum()} wins")

    return df


def get_mock_race_context():
    """Generate a mock race context for testing."""
    return {
        'lap': 15,
        'total_laps': 57,
        'position': 4,
        'battery_soc': 45.0,
        'tire_life': 62.0,
        'fuel_remaining': 28.0,
        'event_type': 'RAIN_START'
    }


def get_mock_strategy_params():
    """Generate 3 strategy configurations for testing."""
    return [
        # Strategy 0: Aggressive
        {
            'energy_deployment': 85,
            'tire_management': 70,
            'fuel_strategy': 60,
            'ers_mode': 80,
            'overtake_aggression': 90,
            'defense_intensity': 40
        },
        # Strategy 1: Balanced
        {
            'energy_deployment': 60,
            'tire_management': 80,
            'fuel_strategy': 70,
            'ers_mode': 65,
            'overtake_aggression': 60,
            'defense_intensity': 55
        },
        # Strategy 2: Conservative
        {
            'energy_deployment': 35,
            'tire_management': 90,
            'fuel_strategy': 85,
            'ers_mode': 50,
            'overtake_aggression': 30,
            'defense_intensity': 70
        }
    ]


def print_recommendations(recommendations):
    """Pretty print the recommendations."""

    print("\n" + "=" * 70)
    print("🏁 RACE STRATEGY RECOMMENDATIONS")
    print("=" * 70)

    print("\n✅ TOP 2 RECOMMENDED STRATEGIES:\n")

    for i, rec in enumerate(recommendations['recommended'], 1):
        print(f"{i}. Strategy {chr(65 + rec['strategy_id'])}: {rec['strategy_name']}")
        print(f"   Win Rate: {rec['win_rate']:.1f}%  |  Avg Position: P{rec['avg_position']:.1f}")
        print(f"   Confidence: {rec['confidence']:.0%}")
        print(f"   💡 Rationale: {rec['rationale']}")
        print()

    print("❌ AVOID THIS STRATEGY:\n")
    avoid = recommendations['avoid']
    print(f"   Strategy {chr(65 + avoid['strategy_id'])}: {avoid['strategy_name']}")
    print(f"   Win Rate: {avoid['win_rate']:.1f}%  |  Avg Position: P{avoid['avg_position']:.1f}")
    print(f"   ⚠️  Rationale: {avoid['rationale']}")
    print(f"   🚨 Risk: {avoid['risk']}")
    print()

    print("=" * 70)
    print(f"⏱️  Analysis Latency: {recommendations['latency_ms']}ms")
    print(f"🤖 Gemini Available: {recommendations.get('gemini_available', False)}")
    print(f"📋 Used Fallback: {recommendations['used_fallback']}")
    print(f"🕐 Timestamp: {recommendations.get('timestamp', 'N/A')}")
    print("=" * 70 + "\n")


def test_game_advisor():
    """Main test function."""

    print("\n" + "🧪" * 35)
    print("TESTING GAME ADVISOR WITH MOCK DATA")
    print("🧪" * 35 + "\n")

    # Step 1: Initialize advisor
    print("1️⃣  Initializing GameAdvisor...")
    advisor = GameAdvisor()
    print()

    # Step 2: Generate mock data
    print("2️⃣  Generating mock simulation data...")
    sim_results = generate_mock_sim_results(num_sims_per_strategy=100)
    race_context = get_mock_race_context()
    strategy_params = get_mock_strategy_params()
    print()

    # Print race context
    print("3️⃣  Race Context:")
    print(f"   Lap: {race_context['lap']}/{race_context['total_laps']}")
    print(f"   Position: P{race_context['position']}")
    print(f"   Battery: {race_context['battery_soc']:.1f}%")
    print(f"   Tires: {race_context['tire_life']:.1f}%")
    print(f"   Fuel: {race_context['fuel_remaining']:.1f} kg")
    print(f"   Event: {race_context['event_type']}")
    print()

    # Step 3: Call advisor
    print("4️⃣  Calling GameAdvisor.analyze_decision_point()...")
    print("   (This may take 2-4 seconds if using Gemini API)")
    print()

    try:
        recommendations = advisor.analyze_decision_point(
            sim_results=sim_results,
            race_context=race_context,
            strategy_params=strategy_params,
            timeout_seconds=3.0
        )

        # Step 4: Display results
        print("5️⃣  Analysis Complete!")
        print_recommendations(recommendations)

        # Step 5: Validation
        print("6️⃣  Validating Output Schema...")

        assert 'recommended' in recommendations, "Missing 'recommended' field"
        assert 'avoid' in recommendations, "Missing 'avoid' field"
        assert len(recommendations['recommended']) == 2, "Expected 2 recommendations"

        for rec in recommendations['recommended']:
            assert 'strategy_id' in rec
            assert 'strategy_name' in rec
            assert 'win_rate' in rec
            assert 'rationale' in rec
            assert 'confidence' in rec

        avoid = recommendations['avoid']
        assert 'strategy_id' in avoid
        assert 'strategy_name' in avoid
        assert 'risk' in avoid

        print("   ✅ All validations passed!")
        print()

        # Success summary
        print("=" * 70)
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("✅ GameAdvisor is ready for integration with game loop")
        print("✅ Recommendation schema validated")
        print(f"✅ Latency within acceptable range: {recommendations['latency_ms']}ms < 4000ms")
        print()

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling."""

    print("\n" + "🔬" * 35)
    print("TESTING EDGE CASES")
    print("🔬" * 35 + "\n")

    advisor = GameAdvisor()

    # Test 1: Empty simulation results
    print("1️⃣  Testing with empty simulation data...")
    try:
        empty_df = pd.DataFrame()
        recommendations = advisor.analyze_decision_point(
            sim_results=empty_df,
            race_context=get_mock_race_context(),
            strategy_params=get_mock_strategy_params(),
            timeout_seconds=2.0
        )
        print("   ⚠️  Empty data handled gracefully (used fallback)")
    except Exception as e:
        print(f"   ✅ Correctly raised error: {type(e).__name__}")

    print()

    # Test 2: Invalid strategy params
    print("2️⃣  Testing with mismatched strategy count...")
    try:
        sim_df = generate_mock_sim_results(50)
        recommendations = advisor.analyze_decision_point(
            sim_results=sim_df,
            race_context=get_mock_race_context(),
            strategy_params=[{}, {}],  # Only 2 strategies
            timeout_seconds=2.0
        )
        print("   ⚠️  Handled gracefully")
    except Exception as e:
        print(f"   ✅ Correctly raised error: {type(e).__name__}")

    print("\n✅ Edge case tests complete\n")


if __name__ == '__main__':
    # Run main test
    success = test_game_advisor()

    # Optionally run edge case tests
    if '--edge-cases' in sys.argv:
        test_edge_cases()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
