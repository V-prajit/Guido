#!/usr/bin/env python3
"""
Validate AI-discovered strategies against baseline agents.

This script:
1. Loads the AI-generated playbook
2. Runs NEW scenarios (not in training data)
3. Compares AdaptiveAI (with discovered rules) vs baseline agents
4. Measures win rate, performance improvement, and rule utilization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

from sim.engine import simulate_race
from sim.scenarios import generate_scenarios
from sim.agents_v2 import (
    AdaptiveAI, VerstappenStyle, HamiltonStyle, AlonsoStyle,
    ElectricBlitzer, EnergySaver, TireWhisperer, Opportunist
)


def load_playbooks() -> Tuple[Dict, Dict]:
    """Load both original and discovered playbooks for comparison."""

    # Load original/baseline playbook
    original_path = Path('data/playbook.json')
    if original_path.exists():
        with open(original_path) as f:
            original_playbook = json.load(f)
    else:
        original_playbook = {"rules": []}

    # Load discovered playbook
    discovered_path = Path('data/playbook_discovered.json')
    if discovered_path.exists():
        with open(discovered_path) as f:
            discovered_playbook = json.load(f)
    else:
        print("⚠️ No discovered playbook found at data/playbook_discovered.json")
        print("   Using original playbook for both agents")
        discovered_playbook = original_playbook

    return original_playbook, discovered_playbook


class AdaptiveAIOriginal(AdaptiveAI):
    """AdaptiveAI using original/baseline playbook."""
    def __init__(self):
        super().__init__(playbook_path='data/playbook.json')
        self.name = "AdaptiveAI_Original"


class AdaptiveAIDiscovered(AdaptiveAI):
    """AdaptiveAI using discovered playbook."""
    def __init__(self):
        # First check if discovered playbook exists
        discovered_path = Path('data/playbook_discovered.json')
        if discovered_path.exists():
            super().__init__(playbook_path='data/playbook_discovered.json')
        else:
            # Fall back to original
            super().__init__(playbook_path='data/playbook.json')
        self.name = "AdaptiveAI_Discovered"
        self.rule_usage = {}  # Track which rules fire

    def decide(self, state):
        """Override to track rule usage."""
        # Get base decision
        decision = super().decide(state)

        # Track which rules matched (re-evaluate conditions)
        for i, rule in enumerate(self.playbook.get('rules', [])):
            condition = rule.get('condition', '')
            safe_vars = {
                'battery_soc': state.battery_soc,
                'lap': state.lap,
                'position': state.position,
                'tire_age': state.tire_age,
                'tire_life': state.tire_life,
                'fuel_remaining': state.fuel_remaining,
                'boost_used': state.boost_used
            }

            try:
                if eval(condition, {"__builtins__": {}}, safe_vars):
                    rule_name = rule.get('rule', f'Rule_{i}')
                    self.rule_usage[rule_name] = self.rule_usage.get(rule_name, 0) + 1
            except:
                pass

        return decision


def run_validation(num_scenarios: int = 50, verbose: bool = True) -> Dict:
    """
    Run validation races with unseen scenarios.

    Args:
        num_scenarios: Number of validation scenarios
        verbose: Print progress

    Returns:
        Dict with validation results
    """

    print("\n" + "="*60)
    print("AI STRATEGY DISCOVERY - VALIDATION")
    print("="*60)

    # Generate NEW scenarios (different seed from training)
    np.random.seed(9999)  # Different seed to ensure unseen data
    scenarios = generate_scenarios(num_scenarios)
    print(f"\nGenerated {num_scenarios} NEW validation scenarios")

    # Create agents for testing
    agents = [
        # Discovered strategy
        AdaptiveAIDiscovered(),
        # Original/baseline strategy
        AdaptiveAIOriginal(),
        # Champion-learned strategies (strong baselines)
        VerstappenStyle(),
        HamiltonStyle(),
        AlonsoStyle(),
        # Synthetic strategies
        ElectricBlitzer(),
        EnergySaver(),
        TireWhisperer(),
        Opportunist()
    ]

    print(f"Testing {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.name}")

    # Run validation races
    print(f"\nRunning {num_scenarios} validation races...")
    start_time = time.time()
    all_results = []

    for i, scenario in enumerate(scenarios):
        if verbose and (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            eta = (num_scenarios - i - 1) / rate
            print(f"  Progress: {i+1}/{num_scenarios} "
                  f"({rate:.1f} scenarios/sec, ETA: {eta:.0f}s)")

        # Run race (uses 2026 rules by default)
        df = simulate_race(scenario, agents, use_2026_rules=True)
        df['scenario_id'] = scenario['id']
        all_results.append(df)

    # Combine results
    full_df = pd.concat(all_results, ignore_index=True)
    elapsed = time.time() - start_time

    print(f"✅ Completed in {elapsed:.1f} seconds ({num_scenarios/elapsed:.1f} scenarios/sec)")

    # Analyze results
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)

    # Get final positions for each agent in each race
    final_results = full_df.groupby(['scenario_id', 'agent']).tail(1)

    # Calculate win rates and average positions
    agent_performance = final_results.groupby('agent').agg({
        'won': 'sum',
        'final_position': 'mean',
        'lap_time': 'mean'
    }).round(2)

    agent_performance['win_rate'] = (agent_performance['won'] / num_scenarios * 100).round(1)
    agent_performance = agent_performance.sort_values('win_rate', ascending=False)

    print("\n📊 Agent Performance:")
    print("-" * 50)
    print(f"{'Agent':<25} {'Wins':>6} {'Win%':>7} {'Avg Pos':>8}")
    print("-" * 50)

    for agent_name in agent_performance.index:
        stats = agent_performance.loc[agent_name]
        wins = int(stats['won'])
        win_rate = stats['win_rate']
        avg_pos = stats['final_position']

        # Highlight discovered AI
        marker = "⭐" if "Discovered" in agent_name else "  "
        print(f"{marker} {agent_name:<23} {wins:>4} {win_rate:>6.1f}% {avg_pos:>7.2f}")

    # Compare discovered vs original
    discovered_wins = agent_performance.loc['AdaptiveAI_Discovered', 'won'] if 'AdaptiveAI_Discovered' in agent_performance.index else 0
    original_wins = agent_performance.loc['AdaptiveAI_Original', 'won'] if 'AdaptiveAI_Original' in agent_performance.index else 0

    print("\n" + "="*60)
    print("💡 KEY METRICS")
    print("="*60)

    if 'AdaptiveAI_Discovered' in agent_performance.index:
        discovered_win_rate = agent_performance.loc['AdaptiveAI_Discovered', 'win_rate']
        discovered_avg_pos = agent_performance.loc['AdaptiveAI_Discovered', 'final_position']

        print(f"\nAI-Discovered Strategy Performance:")
        print(f"  Win Rate: {discovered_win_rate:.1f}%")
        print(f"  Average Position: {discovered_avg_pos:.2f}")

        if 'AdaptiveAI_Original' in agent_performance.index:
            original_win_rate = agent_performance.loc['AdaptiveAI_Original', 'win_rate']
            improvement = discovered_win_rate - original_win_rate
            print(f"\n  Improvement vs Original: {improvement:+.1f}% win rate")

        # Compare to champion baselines
        champion_agents = ['VerstappenStyle', 'HamiltonStyle', 'AlonsoStyle']
        champion_wins = agent_performance.loc[
            [a for a in champion_agents if a in agent_performance.index], 'win_rate'
        ].mean() if any(a in agent_performance.index for a in champion_agents) else 0

        print(f"  vs Champion Average: {discovered_win_rate - champion_wins:+.1f}% win rate")

        # Check if meets success criteria (>60% win rate)
        success = discovered_win_rate >= 60
        print(f"\n  ✅ Success Criteria Met (≥60% wins): {success}")

    # Track rule usage (if available)
    discovered_agent = next((a for a in agents if isinstance(a, AdaptiveAIDiscovered)), None)
    if discovered_agent and hasattr(discovered_agent, 'rule_usage'):
        if discovered_agent.rule_usage:
            print("\n📋 Rule Utilization (Discovered Playbook):")
            sorted_rules = sorted(discovered_agent.rule_usage.items(), key=lambda x: x[1], reverse=True)
            for rule_name, count in sorted_rules[:5]:
                print(f"  {rule_name}: {count:,} times")

    # Save validation results
    results = {
        'num_scenarios': num_scenarios,
        'elapsed_time': elapsed,
        'agent_performance': agent_performance.to_dict(),
        'discovered_wins': int(discovered_wins),
        'original_wins': int(original_wins),
        'validation_passed': discovered_wins > original_wins
    }

    output_path = 'data/validation_discovery.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Validation results saved to {output_path}")

    return results


def main():
    """Run validation with command line arguments."""

    num_scenarios = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    # Check if discovered playbook exists
    if not Path('data/playbook_discovered.json').exists():
        print("⚠️ No discovered playbook found!")
        print("Please run the discovery pipeline first:")
        print("  1. python scripts/generate_discovery_data.py")
        print("  2. python api/gemini_discovery.py")
        sys.exit(1)

    # Run validation
    results = run_validation(num_scenarios)

    # Final summary
    print("\n" + "="*60)
    if results['validation_passed']:
        print("🎉 VALIDATION SUCCESSFUL!")
        print("AI-discovered strategies outperform the baseline.")
    else:
        print("⚠️ VALIDATION NEEDS IMPROVEMENT")
        print("AI-discovered strategies did not outperform baseline.")
        print("Consider:")
        print("  - Generating more diverse training data")
        print("  - Tuning Gemini prompts for better pattern extraction")
        print("  - Adjusting confidence thresholds for rules")
    print("="*60)


if __name__ == '__main__':
    main()