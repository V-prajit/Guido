#!/usr/bin/env python3
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from sim.scenarios import generate_scenarios
from sim.agents import create_agents
from sim.engine import simulate_race
from api.gemini import synthesize_playbook

def generate_playbook(num_scenarios=100, seed=42):
    print("="*60)
    print("PLAYBOOK GENERATION")
    print("="*60)

    print(f"\nGenerating {num_scenarios} scenarios...")
    np.random.seed(seed)
    scenarios = generate_scenarios(num_scenarios)

    agents = create_agents()
    print(f"Running {num_scenarios} races with {len(agents)} agents...")

    all_results = []
    for i, scenario in enumerate(scenarios):
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{num_scenarios}")
        df = simulate_race(scenario, agents)
        all_results.append(df)

    full_df = pd.concat(all_results, ignore_index=True)

    agent_stats = {}
    for agent in agents:
        agent_df = full_df[full_df['agent'] == agent.name]
        wins = int(agent_df['won'].sum())
        avg_pos = float(agent_df.groupby('scenario_id')['position'].last().mean())
        agent_stats[agent.name] = {'wins': wins, 'avg_position': round(avg_pos, 2)}

    sorted_agents = sorted(agent_stats.items(), key=lambda x: -x[1]['wins'])
    for name, stats in sorted_agents:
        print(f"  {name}: {stats['wins']} wins")

    print(f"\nSynthesizing playbook...")
    playbook = synthesize_playbook(agent_stats, full_df)

    with open('data/playbook.json', 'w') as f:
        json.dump(playbook, f, indent=2)

    print(f"✅ Saved {len(playbook['rules'])} rules to data/playbook.json")
    return playbook

if __name__ == '__main__':
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    playbook = generate_playbook(num)
    print(f"\nModel: {playbook.get('model')}, Fallback: {playbook.get('fallback', False)}")
