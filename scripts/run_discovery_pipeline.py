#!/usr/bin/env python3
"""
Complete AI Strategy Discovery Pipeline.

This script runs the entire discovery process:
1. Generate diverse simulation data
2. Analyze patterns with Gemini
3. Create AI-discovered playbook
4. Validate against baselines
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import json
import time
from pathlib import Path
from dotenv import load_dotenv


def check_requirements():
    """Check if all requirements are met."""

    print("Checking requirements...")

    # Check for Gemini API key
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("\n⚠️ GEMINI_API_KEY not found!")
        print("\nTo set up your API key:")
        print("1. Get a free API key at: https://aistudio.google.com/apikey")
        print("2. Create a .env file in the project root with:")
        print("   GEMINI_API_KEY=your_actual_key_here")
        print("\nOr export it in your terminal:")
        print("   export GEMINI_API_KEY=your_actual_key_here")
        return False

    if api_key == "your_key_here":
        print("\n⚠️ GEMINI_API_KEY is still set to placeholder value!")
        print("Please replace 'your_key_here' with your actual API key.")
        return False

    print(f"✅ Gemini API key found: {api_key[:8]}...")

    # Check Python packages
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package installed")
    except ImportError:
        print("⚠️ Missing google-generativeai package")
        print("   Run: pip install google-generativeai")
        return False

    try:
        import pandas
        import numpy
        print("✅ Required packages installed")
    except ImportError:
        print("⚠️ Missing required packages")
        print("   Run: pip install -r requirements.txt")
        return False

    return True


def run_step(command: str, description: str) -> bool:
    """
    Run a pipeline step.

    Args:
        command: Shell command to execute
        description: Description of the step

    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}\n")

    result = subprocess.run(command, shell=True, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ Step failed: {description}")
        return False

    print(f"\n✅ Completed: {description}")
    return True


def main():
    """Run the complete discovery pipeline."""

    print("\n" + "="*70)
    print(" "*20 + "AI STRATEGY DISCOVERY PIPELINE")
    print("="*70)
    print("\nThis will:")
    print("1. Generate diverse strategy exploration data")
    print("2. Use Gemini AI to discover winning patterns")
    print("3. Create an AI-powered playbook")
    print("4. Validate discovered strategies")
    print("\n" + "="*70)

    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix issues above.")
        sys.exit(1)

    # Parse arguments
    num_training_scenarios = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    num_strategies = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    num_validation_scenarios = int(sys.argv[3]) if len(sys.argv) > 3 else 50

    print(f"\nConfiguration:")
    print(f"  Training Scenarios: {num_training_scenarios}")
    print(f"  Strategy Variants: {num_strategies}")
    print(f"  Validation Scenarios: {num_validation_scenarios}")

    start_time = time.time()

    # Step 1: Generate discovery data
    success = run_step(
        f"python scripts/generate_discovery_data.py {num_training_scenarios} {num_strategies}",
        "Step 1/4: Generating Discovery Data"
    )
    if not success:
        sys.exit(1)

    # Step 2: Run Gemini discovery
    success = run_step(
        "python api/gemini_discovery.py",
        "Step 2/4: AI Pattern Discovery with Gemini"
    )
    if not success:
        print("\n⚠️ Gemini discovery failed, but continuing with fallback rules...")

    # Step 3: Copy discovered playbook for AdaptiveAI
    if Path('data/playbook_discovered.json').exists():
        print(f"\n{'='*60}")
        print("📌 Step 3/4: Activating Discovered Playbook")
        print(f"{'='*60}")

        # Backup original playbook
        if Path('data/playbook.json').exists():
            subprocess.run("cp data/playbook.json data/playbook_original.json", shell=True)
            print("✅ Backed up original playbook to data/playbook_original.json")

        # Activate discovered playbook
        subprocess.run("cp data/playbook_discovered.json data/playbook.json", shell=True)
        print("✅ Activated discovered playbook")
    else:
        print("\n⚠️ No discovered playbook found, skipping activation")

    # Step 4: Validate discovered strategies
    success = run_step(
        f"python scripts/validate_discovery.py {num_validation_scenarios}",
        "Step 4/4: Validating Discovered Strategies"
    )

    # Final summary
    elapsed = time.time() - start_time
    print("\n" + "="*70)
    print(" "*20 + "PIPELINE COMPLETE")
    print("="*70)
    print(f"\n⏱️ Total time: {elapsed:.1f} seconds")

    # Load and display key results
    if Path('data/validation_discovery.json').exists():
        with open('data/validation_discovery.json') as f:
            validation = json.load(f)

        if 'agent_performance' in validation:
            perf = validation['agent_performance']
            if 'AdaptiveAI_Discovered' in perf.get('won', {}):
                discovered_wins = perf['won']['AdaptiveAI_Discovered']
                discovered_win_rate = perf['win_rate']['AdaptiveAI_Discovered']
                print(f"\n🏆 AI-Discovered Strategy Performance:")
                print(f"   Wins: {discovered_wins}/{num_validation_scenarios}")
                print(f"   Win Rate: {discovered_win_rate:.1f}%")

    # Display discovered rules
    if Path('data/playbook_discovered.json').exists():
        with open('data/playbook_discovered.json') as f:
            playbook = json.load(f)

        print(f"\n📋 Discovered {len(playbook['rules'])} Strategic Rules:")
        for i, rule in enumerate(playbook['rules'][:5], 1):  # Show top 5
            print(f"   {i}. {rule['rule']} (confidence: {rule['confidence']:.0%})")

    print("\n" + "="*70)
    print("✅ AI Strategy Discovery Pipeline Complete!")
    print("\nNext steps:")
    print("  • Review discovered rules: cat data/playbook_discovered.json | jq")
    print("  • Run full benchmark: python scripts/comprehensive_benchmark.py")
    print("  • Test API: python api/main.py (then visit http://localhost:8000/docs)")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()