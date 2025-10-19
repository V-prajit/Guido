#!/usr/bin/env python3
"""
Generate diverse simulation data for AI strategy discovery.

This script systematically explores the strategy space by creating agents
with varied strategic parameters and running them through simulations.
The goal is to generate comprehensive data for Gemini to discover patterns.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
import time
from dataclasses import dataclass
from itertools import product

from sim.engine import simulate_race
from sim.physics_2024 import RaceState, AgentDecision
from sim.scenarios import generate_scenarios
from sim.agents_v2 import AgentV2


@dataclass
class ExplorationAgent(AgentV2):
    """Agent with fixed strategic parameters for systematic exploration."""

    def __init__(self, name: str, strategy_params: Dict[str, float]):
        """
        Initialize with fixed strategy parameters.

        Args:
            name: Agent identifier
            strategy_params: Dict with 6 strategic variables (0-100 each)
        """
        self.name = name
        self.strategy_params = strategy_params
        self.profile = strategy_params.copy()

    def decide(self, state: RaceState) -> AgentDecision:
        """Make decision based on fixed strategy with slight state-based adjustments."""

        # Start with base strategy
        params = self.strategy_params.copy()

        # Add minimal state-based adjustments for realism
        # Low battery - reduce deployment, increase harvesting
        if state.battery_soc < 20:
            params['energy_deployment'] *= 0.5
            params['ers_mode'] *= 0.4

        # Late race with good battery - push harder
        if state.lap > 50 and state.battery_soc > 60:
            params['energy_deployment'] = min(100, params['energy_deployment'] * 1.2)
            params['ers_mode'] = min(100, params['ers_mode'] * 1.2)

        # Worn tires - reduce tire management aggression
        if state.tire_life < 30:
            params['tire_management'] *= 0.6

        return AgentDecision(
            energy_deployment=params['energy_deployment'],
            tire_management=params['tire_management'],
            fuel_strategy=params['fuel_strategy'],
            ers_mode=params['ers_mode'],
            overtake_aggression=params['overtake_aggression'],
            defense_intensity=params['defense_intensity']
        )


def generate_exploration_strategies(num_strategies: int = 50) -> List[Dict[str, float]]:
    """
    Generate diverse strategic parameter combinations.

    Returns list of strategy dictionaries with 6 variables each.
    """
    strategies = []

    # 1. Grid sampling for systematic coverage (first 27 strategies)
    grid_values = [20, 50, 80]  # Low, medium, high for each parameter
    grid_combos = list(product(grid_values, repeat=6))

    # Take first 27 grid combinations (3^3 = 27 for first 3 params varied, others fixed)
    for i, (energy, tire, fuel) in enumerate(product(grid_values, repeat=3)):
        if i >= min(27, num_strategies):
            break
        strategies.append({
            'energy_deployment': float(energy),
            'tire_management': float(tire),
            'fuel_strategy': float(fuel),
            'ers_mode': float(energy * 0.9),  # Correlate with energy
            'overtake_aggression': 50.0 + (energy - 50) * 0.3,  # Slight correlation
            'defense_intensity': 70.0 - (energy - 50) * 0.2  # Inverse correlation
        })

    # 2. Random sampling for exploration (remaining strategies)
    remaining = num_strategies - len(strategies)
    np.random.seed(42)

    for i in range(remaining):
        # Generate with some realistic correlations
        energy = np.random.uniform(15, 95)
        tire = np.random.uniform(20, 100)
        fuel = np.random.uniform(30, 80)

        # ERS mode tends to correlate with energy deployment
        ers = energy * (0.8 + np.random.uniform(-0.2, 0.3))
        ers = np.clip(ers, 10, 100)

        # Overtaking vs defense tend to be inversely related
        overtake = np.random.uniform(30, 100)
        defense = 130 - overtake + np.random.uniform(-20, 20)
        defense = np.clip(defense, 30, 100)

        strategies.append({
            'energy_deployment': float(energy),
            'tire_management': float(tire),
            'fuel_strategy': float(fuel),
            'ers_mode': float(ers),
            'overtake_aggression': float(overtake),
            'defense_intensity': float(defense)
        })

    return strategies


def run_discovery_simulations(num_scenarios: int = 200, num_strategies: int = 50) -> pd.DataFrame:
    """
    Run comprehensive simulations with diverse strategies.

    Args:
        num_scenarios: Number of race scenarios to generate
        num_strategies: Number of different strategy combinations to test

    Returns:
        DataFrame with all simulation results
    """

    print(f"Generating {num_strategies} diverse strategies...")
    strategies = generate_exploration_strategies(num_strategies)

    print(f"Generating {num_scenarios} race scenarios...")
    scenarios = generate_scenarios(num_scenarios)

    # Create agents from strategies
    agents = []
    for i, strategy in enumerate(strategies):
        agent = ExplorationAgent(f"Explorer_{i:03d}", strategy)
        agents.append(agent)

    # Add some baseline agents for comparison (first 3 from create_agents_v2)
    from sim.agents_v2 import VerstappenStyle, HamiltonStyle, AlonsoStyle
    agents.extend([VerstappenStyle(), HamiltonStyle(), AlonsoStyle()])

    total_races = len(scenarios)
    print(f"\nRunning {total_races} races with {len(agents)} agents...")
    print("This will generate ~{:,} race results".format(total_races * len(agents) * 57))  # 57 laps per race

    all_results = []
    start_time = time.time()

    for i, scenario in enumerate(scenarios):
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            eta = (total_races - i - 1) / rate
            print(f"  Progress: {i+1}/{total_races} scenarios "
                  f"({rate:.1f} scenarios/sec, ETA: {eta:.0f}s)")

        # Run race simulation (uses 2026 rules by default)
        df = simulate_race(scenario, agents, use_2026_rules=True)

        # Add scenario metadata
        df['scenario_id'] = scenario['id']
        df['scenario_type'] = scenario.get('track_type', 'balanced')
        rain_lap = scenario.get('rain_lap')
        df['scenario_rain'] = rain_lap is not None and rain_lap > 0

        # Add agent strategy metadata for explorers
        for agent in agents:
            if agent.name.startswith('Explorer_'):
                agent_df_mask = df['agent'] == agent.name
                for param, value in agent.strategy_params.items():
                    df.loc[agent_df_mask, f'strategy_{param}'] = value

        all_results.append(df)

    # Combine all results
    full_df = pd.concat(all_results, ignore_index=True)

    # Calculate summary statistics
    print("\n" + "="*60)
    print("DISCOVERY DATA GENERATION COMPLETE")
    print("="*60)

    # Performance analysis
    agent_performance = full_df.groupby('agent').agg({
        'won': 'sum',
        'final_position': 'mean',
        'lap_time': 'mean'
    }).round(2)

    # Find top performers
    top_agents = agent_performance.nlargest(10, 'won')
    print("\nTop 10 Agents by Wins:")
    print(top_agents)

    # Analyze strategy patterns of winners
    winner_df = full_df[full_df['won'] == True]
    if len(winner_df) > 0:
        print("\nWinning Strategy Averages:")
        strategy_cols = [col for col in winner_df.columns if col.startswith('strategy_')]
        if strategy_cols:
            winning_strategies = winner_df[strategy_cols].mean()
            for param in strategy_cols:
                clean_name = param.replace('strategy_', '')
                print(f"  {clean_name}: {winning_strategies[param]:.1f}")

    # Save results
    csv_path = 'data/discovery_runs.csv'
    full_df.to_csv(csv_path, index=False)
    print(f"\nSaved {len(full_df)} rows to {csv_path}")

    # Save summary for Gemini analysis
    summary = {
        'num_scenarios': num_scenarios,
        'num_strategies': num_strategies,
        'num_agents': len(agents),
        'total_rows': len(full_df),
        'generation_time': time.time() - start_time,
        'top_performers': top_agents.to_dict(),
        'winner_stats': {
            'total_races': len(scenarios),
            'unique_winners': full_df[full_df['won'] == True]['agent'].nunique()
        }
    }

    summary_path = 'data/discovery_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Saved summary to {summary_path}")

    return full_df


def main():
    """Run discovery data generation."""

    # Parse command line arguments
    num_scenarios = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    num_strategies = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    print("="*60)
    print("AI STRATEGY DISCOVERY - DATA GENERATION")
    print("="*60)
    print(f"Scenarios: {num_scenarios}")
    print(f"Strategy Variants: {num_strategies}")
    print()

    # Generate the data
    df = run_discovery_simulations(num_scenarios, num_strategies)

    print("\n✅ Discovery data generation complete!")
    print(f"   Use this data with api/gemini_discovery.py to discover patterns")


if __name__ == '__main__':
    main()