#!/usr/bin/env python3
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sim.scenarios import generate_scenarios
from sim.agents import create_agents, AdaptiveAI
from sim.engine import simulate_race

def run_ablation_study(playbook_path='data/playbook.json', num_scenarios=50):
    print(f"\n{'='*60}")
    print("ABLATION STUDY - Rule Importance")
    print(f"{'='*60}\n")

    with open(playbook_path, 'r') as f:
        playbook = json.load(f)

    print(f"Testing {len(playbook['rules'])} rules with {num_scenarios} scenarios\n")

    print("Baseline (all rules)...")
    baseline_wins = run_test(playbook, num_scenarios)
    print(f"  Wins: {baseline_wins}/{num_scenarios} ({baseline_wins*100/num_scenarios:.0f}%)\n")

    impacts = []
    for i, rule in enumerate(playbook['rules']):
        print(f"Without '{rule['rule']}'...")

        ablated = playbook.copy()
        ablated['rules'] = [r for j, r in enumerate(playbook['rules']) if j != i]

        wins = run_test(ablated, num_scenarios)
        delta = wins - baseline_wins

        impact_level = 'Critical' if abs(delta) > 5 else 'Moderate' if abs(delta) > 2 else 'Minor'
        impacts.append({
            'rule': rule['rule'],
            'wins': wins,
            'delta': delta,
            'level': impact_level
        })

        print(f"  Wins: {wins}/{num_scenarios} ({delta:+d}) [{impact_level}]\n")

    print(f"{'='*60}")
    print("IMPACT RANKING")
    print(f"{'='*60}\n")

    impacts.sort(key=lambda x: abs(x['delta']), reverse=True)

    for imp in impacts:
        symbol = '🔴' if imp['level'] == 'Critical' else '🟡' if imp['level'] == 'Moderate' else '🟢'
        print(f"{symbol} {imp['rule']}: {imp['delta']:+d} wins ({imp['level']})")

    with open('data/ablation_results.json', 'w') as f:
        json.dump(impacts, f, indent=2)

    print(f"\n✅ Saved to data/ablation_results.json\n")

def run_test(playbook, num_scenarios):
    np.random.seed(8888)
    scenarios = generate_scenarios(num_scenarios)

    base_agents = create_agents()[:-1]
    adaptive = AdaptiveAI("Adaptive_AI", {}, playbook)
    agents = base_agents + [adaptive]

    wins = 0
    for scenario in scenarios:
        df = simulate_race(scenario, agents)
        winner = df[df['won'] == 1]['agent'].iloc[0]
        if winner == 'Adaptive_AI':
            wins += 1

    return wins

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/playbook.json'
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    if not os.path.exists(path):
        print(f"❌ Playbook not found: {path}")
        sys.exit(1)

    run_ablation_study(path, num)
