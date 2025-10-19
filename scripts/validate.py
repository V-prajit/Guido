"""
Validation Script for Strategy Gym 2026 Adaptive AI

Tests that the Adaptive AI agent, when powered by the playbook,
can beat baseline strategies on unseen scenarios.

Success criteria: Adaptive wins > median of baseline agents (7 others)
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sim.scenarios import generate_scenarios
from sim.agents import create_agents, AdaptiveAI
from sim.engine import simulate_race


def load_playbook(playbook_path='data/playbook_test.json'):
    """
    Load playbook from JSON file with fallback.

    Args:
        playbook_path: Path to playbook JSON file

    Returns:
        Playbook dict, or empty dict if file not found
    """
    try:
        with open(playbook_path, 'r') as f:
            playbook = json.load(f)
            print(f"✅ Loaded playbook from {playbook_path}")
            print(f"   Contains {len(playbook.get('rules', []))} rules")
            return playbook
    except FileNotFoundError:
        print(f"⚠️  No playbook found at {playbook_path}")
        print("   Using empty playbook (will fall back to baseline)")
        return {'rules': []}
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parsing playbook: {e}")
        print("   Using empty playbook (will fall back to baseline)")
        return {'rules': []}


def run_validation(num_scenarios=20, seed=9999):
    """
    Run validation testing on unseen scenarios.

    Args:
        num_scenarios: Number of test scenarios (default 20)
        seed: Random seed for reproducibility (default 9999)

    Returns:
        Dictionary with validation results
    """
    print("=" * 70)
    print("ADAPTIVE AI VALIDATION")
    print("=" * 70)

    # Load playbook
    print("\nLoading playbook...")
    playbook = load_playbook()

    # Generate NEW scenarios (different seed from training)
    print(f"\nGenerating {num_scenarios} validation scenarios (seed={seed})...")
    np.random.seed(seed)
    scenarios = generate_scenarios(num_scenarios)
    print(f"✅ Generated {len(scenarios)} unseen scenarios")

    # Create baseline agents (first 7)
    base_agents = create_agents()[:-1]  # Exclude default AdaptiveAI

    # Create playbook-powered AdaptiveAI
    adaptive = AdaptiveAI("Adaptive_AI", {}, playbook)

    # Combine all agents
    agents = base_agents + [adaptive]

    print(f"\nTesting agents:")
    for i, agent in enumerate(agents):
        marker = "📘 PLAYBOOK" if agent.name == "Adaptive_AI" else "  "
        print(f"  {marker} {agent.name}")

    # Run validation races
    print(f"\nRunning {num_scenarios} races...")
    wins_by_agent = {agent.name: 0 for agent in agents}

    for i, scenario in enumerate(scenarios):
        if (i + 1) % 5 == 0:
            print(f"  Progress: {i + 1}/{num_scenarios} scenarios completed")

        df = simulate_race(scenario, agents)
        winner = df[df['won'] == 1]['agent'].iloc[0]
        wins_by_agent[winner] += 1

    # Calculate statistics
    adaptive_wins = wins_by_agent['Adaptive_AI']
    baseline_wins = [wins for name, wins in wins_by_agent.items() if name != 'Adaptive_AI']
    median_baseline = sorted(baseline_wins)[len(baseline_wins) // 2]
    max_baseline = max(baseline_wins)

    # Display results
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    print("\nWin Distribution:")
    print(f"{'Agent':<25} {'Wins':<8} {'Win Rate':<10} {'Status':<15}")
    print("-" * 70)

    # Sort by wins (descending)
    sorted_results = sorted(wins_by_agent.items(), key=lambda x: -x[1])

    for agent_name, wins in sorted_results:
        win_rate = (wins / num_scenarios) * 100
        if agent_name == 'Adaptive_AI':
            status = "📘 ADAPTIVE"
        else:
            status = ""
        print(f"{agent_name:<25} {wins:<8} {win_rate:<10.1f}% {status:<15}")

    # Statistical analysis
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS")
    print("=" * 70)

    print(f"\nAdaptive AI Performance:")
    print(f"  Wins: {adaptive_wins}/{num_scenarios} ({(adaptive_wins/num_scenarios)*100:.1f}%)")

    print(f"\nBaseline Agents Performance:")
    print(f"  Median wins: {median_baseline}/{num_scenarios} ({(median_baseline/num_scenarios)*100:.1f}%)")
    print(f"  Max wins: {max_baseline}/{num_scenarios} ({(max_baseline/num_scenarios)*100:.1f}%)")
    print(f"  Best baseline: {sorted_results[1][0] if sorted_results[0][0] == 'Adaptive_AI' else sorted_results[0][0]}")

    print(f"\nValidation Criteria:")
    print(f"  Target: Adaptive wins > median baseline")
    print(f"  Actual: {adaptive_wins} wins > {median_baseline} wins")

    passed = adaptive_wins > median_baseline

    if passed:
        margin = adaptive_wins - median_baseline
        print(f"  Margin: +{margin} wins")
        print(f"\n  ✅ VALIDATION PASSED")
    else:
        gap = median_baseline - adaptive_wins
        print(f"  Gap: -{gap} wins")
        print(f"\n  ❌ VALIDATION FAILED")

    print("=" * 70)

    # Display rule usage statistics
    if hasattr(adaptive, 'rule_usage') and adaptive.rule_usage:
        print("\nRULE USAGE STATISTICS")
        print("=" * 70)

        total_decisions = sum(adaptive.rule_usage.values())
        sorted_rules = sorted(adaptive.rule_usage.items(), key=lambda x: -x[1])

        for rule_name, count in sorted_rules:
            percentage = (count / total_decisions) * 100 if total_decisions > 0 else 0
            print(f'  {rule_name}: {count} times ({percentage:.1f}%)')

        print("=" * 70)

    # Return results
    results = {
        'num_scenarios': num_scenarios,
        'adaptive_wins': adaptive_wins,
        'adaptive_win_rate': round((adaptive_wins / num_scenarios) * 100, 1),
        'median_baseline_wins': median_baseline,
        'median_baseline_rate': round((median_baseline / num_scenarios) * 100, 1),
        'max_baseline_wins': max_baseline,
        'passed': passed,
        'playbook_loaded': len(playbook.get('rules', [])) > 0
    }

    # Add rule usage statistics to results
    if hasattr(adaptive, 'rule_usage') and adaptive.rule_usage:
        total_decisions = sum(adaptive.rule_usage.values())
        results['rule_usage'] = {
            'total_decisions': total_decisions,
            'rules': {
                rule_name: {
                    'count': count,
                    'percentage': round((count / total_decisions) * 100, 1) if total_decisions > 0 else 0
                }
                for rule_name, count in adaptive.rule_usage.items()
            }
        }

    return results


def main():
    """Run validation with command line arguments"""
    # Allow custom scenario count
    num_scenarios = 20
    if len(sys.argv) > 1:
        try:
            num_scenarios = int(sys.argv[1])
        except ValueError:
            print(f"Invalid scenario count, using default: {num_scenarios}")

    # Run validation
    results = run_validation(num_scenarios)

    # Save results
    os.makedirs('data', exist_ok=True)
    with open('data/validation.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: data/validation.json")

    # Return exit code
    sys.exit(0 if results['passed'] else 1)


if __name__ == "__main__":
    main()
