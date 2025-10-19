#!/usr/bin/env python3
"""
Test script to verify AI Discovery system components.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        from sim.engine import simulate_race
        print("✅ sim.engine imported")
    except ImportError as e:
        print(f"❌ Failed to import sim.engine: {e}")
        return False

    try:
        from sim.physics_2024 import RaceState, AgentDecision
        print("✅ sim.physics_2024 imported")
    except ImportError as e:
        print(f"❌ Failed to import sim.physics_2024: {e}")
        return False

    try:
        from sim.agents_v2 import AdaptiveAI, create_agents_v2
        print("✅ sim.agents_v2 imported")
    except ImportError as e:
        print(f"❌ Failed to import sim.agents_v2: {e}")
        return False

    try:
        from sim.scenarios import generate_scenarios
        print("✅ sim.scenarios imported")
    except ImportError as e:
        print(f"❌ Failed to import sim.scenarios: {e}")
        return False

    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported")
    except ImportError as e:
        print("❌ google-generativeai not installed")
        print("   Run: pip install google-generativeai")
        return False

    return True


def test_adaptive_ai():
    """Test that AdaptiveAI can load and use playbooks."""
    print("\nTesting AdaptiveAI...")

    from sim.agents_v2 import AdaptiveAI
    from sim.physics_2024 import RaceState

    # Create agent
    agent = AdaptiveAI()
    print(f"✅ Created AdaptiveAI agent: {agent.name}")

    # Test with sample state
    state = RaceState(
        lap=30,
        battery_soc=25.0,
        position=3,
        tire_age=15,
        tire_life=60.0,
        fuel_remaining=50.0,
        boost_used=1
    )

    # Get decision
    decision = agent.decide(state)
    print(f"✅ Agent made decision: energy={decision.energy_deployment:.1f}, "
          f"tire={decision.tire_management:.1f}")

    # Check if playbook exists
    if Path('data/playbook.json').exists():
        with open('data/playbook.json') as f:
            playbook = json.load(f)
        print(f"✅ Playbook loaded: {len(playbook.get('rules', []))} rules")
    else:
        print("⚠️ No playbook found at data/playbook.json")

    return True


def test_mini_simulation():
    """Run a mini simulation to verify everything works."""
    print("\nTesting mini simulation...")

    from sim.engine import simulate_race
    from sim.scenarios import generate_scenarios
    from sim.agents_v2 import VerstappenStyle, HamiltonStyle, AdaptiveAI

    # Generate 1 scenario
    scenarios = generate_scenarios(1)
    print(f"✅ Generated {len(scenarios)} scenario")

    # Create 3 agents
    agents = [VerstappenStyle(), HamiltonStyle(), AdaptiveAI()]
    print(f"✅ Created {len(agents)} agents")

    # Run simulation
    try:
        df = simulate_race(scenarios[0], agents, use_2026_rules=True)
        print(f"✅ Simulation completed: {len(df)} rows")

        # Check results
        final_laps = df.groupby('agent').tail(1)
        for _, row in final_laps.iterrows():
            print(f"   {row['agent']}: Position {row['final_position']}, "
                  f"Won: {row['won']}")

        return True
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False


def test_gemini_connection():
    """Test Gemini API connection if key is available."""
    print("\nTesting Gemini connection...")

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found in environment")
        print("   To set it up:")
        print("   1. Get key at: https://aistudio.google.com/apikey")
        print("   2. Create .env file with: GEMINI_API_KEY=your_key")
        return False

    if api_key == "your_key_here":
        print("⚠️ GEMINI_API_KEY is still placeholder value")
        return False

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Test with simple prompt
        response = model.generate_content("Reply with just: 'Connected'")
        print(f"✅ Gemini API connected: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("AI DISCOVERY SYSTEM - COMPONENT TEST")
    print("="*60)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test AdaptiveAI
    if not test_adaptive_ai():
        all_passed = False

    # Test mini simulation
    if not test_mini_simulation():
        all_passed = False

    # Test Gemini (optional)
    test_gemini_connection()  # Don't fail if no API key

    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL CORE TESTS PASSED")
        print("\nNext steps:")
        print("1. Set up Gemini API key in .env file")
        print("2. Run: python scripts/run_discovery_pipeline.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please fix the issues above before running discovery pipeline")
    print("="*60)


if __name__ == '__main__':
    main()