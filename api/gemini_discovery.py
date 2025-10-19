#!/usr/bin/env python3
"""
AI-Powered Strategy Discovery using Google Gemini.

This module implements genuine AI strategy discovery by:
1. Analyzing simulation data to find winning patterns
2. Using Gemini to synthesize patterns into actionable rules
3. Generating playbooks with confidence scores and performance metrics
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import re


class StrategyDiscoverer:
    """
    Discovers optimal F1 strategies using Gemini AI to analyze simulation data.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API connection.

        Args:
            api_key: Gemini API key (or will load from environment)
        """
        # Load environment variables
        load_dotenv()

        # Get API key
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "⚠️ GEMINI_API_KEY required. Please provide your Google AI Studio API key.\n"
                "Get one at: https://aistudio.google.com/apikey\n"
                "Then either:\n"
                "1. Set GEMINI_API_KEY in .env file, or\n"
                "2. Pass api_key parameter to StrategyDiscoverer()"
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        print(f"✅ Gemini API configured (key: {self.api_key[:8]}...)")

    def analyze_simulation_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze simulation results to extract patterns for Gemini.

        Args:
            df: DataFrame with simulation results

        Returns:
            Dict with performance groups and patterns
        """
        print("Analyzing simulation data...")

        # Get race-level results (final lap of each agent in each scenario)
        final_laps = df.groupby(['scenario_id', 'agent']).tail(1)

        # Calculate agent performance metrics
        agent_stats = final_laps.groupby('agent').agg({
            'won': 'sum',
            'final_position': 'mean',
            'lap_time': 'mean',
            'energy_deployment': 'mean',
            'tire_management': 'mean',
            'fuel_strategy': 'mean',
            'ers_mode': 'mean',
            'overtake_aggression': 'mean',
            'defense_intensity': 'mean'
        }).round(2)

        # Identify top performers (top 25%)
        num_agents = len(agent_stats)
        top_cutoff = int(num_agents * 0.25)
        bottom_cutoff = int(num_agents * 0.75)

        agent_stats['win_rate'] = agent_stats['won'] / final_laps['scenario_id'].nunique()
        agent_stats = agent_stats.sort_values('win_rate', ascending=False)

        top_agents = agent_stats.head(top_cutoff)
        bottom_agents = agent_stats.tail(num_agents - bottom_cutoff)
        middle_agents = agent_stats.iloc[top_cutoff:bottom_cutoff]

        # Analyze situational patterns
        patterns = {}

        # 1. Low battery situations (battery < 30 in late race)
        low_battery_df = df[(df['battery_soc'] < 30) & (df['lap'] > 40)]
        if len(low_battery_df) > 0:
            winners_mask = low_battery_df['agent'].isin(top_agents.index)
            patterns['low_battery_late_race'] = {
                'winner_strategy': low_battery_df[winners_mask][
                    ['energy_deployment', 'ers_mode', 'tire_management']
                ].mean().to_dict(),
                'loser_strategy': low_battery_df[~winners_mask][
                    ['energy_deployment', 'ers_mode', 'tire_management']
                ].mean().to_dict(),
                'sample_size': len(low_battery_df)
            }

        # 2. Early race aggression (lap < 15)
        early_race_df = df[df['lap'] < 15]
        if len(early_race_df) > 0:
            winners_mask = early_race_df['agent'].isin(top_agents.index)
            patterns['early_race'] = {
                'winner_strategy': early_race_df[winners_mask][
                    ['energy_deployment', 'overtake_aggression', 'tire_management']
                ].mean().to_dict(),
                'loser_strategy': early_race_df[~winners_mask][
                    ['energy_deployment', 'overtake_aggression', 'tire_management']
                ].mean().to_dict(),
                'sample_size': len(early_race_df)
            }

        # 3. Tire degradation (tire_life < 40)
        degraded_tires_df = df[df['tire_life'] < 40]
        if len(degraded_tires_df) > 0:
            winners_mask = degraded_tires_df['agent'].isin(top_agents.index)
            patterns['degraded_tires'] = {
                'winner_strategy': degraded_tires_df[winners_mask][
                    ['tire_management', 'energy_deployment', 'overtake_aggression']
                ].mean().to_dict(),
                'loser_strategy': degraded_tires_df[~winners_mask][
                    ['tire_management', 'energy_deployment', 'overtake_aggression']
                ].mean().to_dict(),
                'sample_size': len(degraded_tires_df)
            }

        # Build analysis summary for Gemini
        analysis = {
            'simulation_metadata': {
                'num_scenarios': df['scenario_id'].nunique(),
                'num_agents': df['agent'].nunique(),
                'total_laps': len(df),
                'physics_version': '2026_extrapolated'
            },
            'performance_groups': {
                'top_25_percent': {
                    'agents': top_agents.index.tolist(),
                    'avg_win_rate': float(top_agents['win_rate'].mean()),
                    'avg_position': float(top_agents['final_position'].mean()),
                    'strategy_profile': {
                        'energy_deployment': float(top_agents['energy_deployment'].mean()),
                        'tire_management': float(top_agents['tire_management'].mean()),
                        'fuel_strategy': float(top_agents['fuel_strategy'].mean()),
                        'ers_mode': float(top_agents['ers_mode'].mean()),
                        'overtake_aggression': float(top_agents['overtake_aggression'].mean()),
                        'defense_intensity': float(top_agents['defense_intensity'].mean())
                    }
                },
                'bottom_25_percent': {
                    'agents': bottom_agents.index.tolist(),
                    'avg_win_rate': float(bottom_agents['win_rate'].mean()),
                    'avg_position': float(bottom_agents['final_position'].mean()),
                    'strategy_profile': {
                        'energy_deployment': float(bottom_agents['energy_deployment'].mean()),
                        'tire_management': float(bottom_agents['tire_management'].mean()),
                        'fuel_strategy': float(bottom_agents['fuel_strategy'].mean()),
                        'ers_mode': float(bottom_agents['ers_mode'].mean()),
                        'overtake_aggression': float(bottom_agents['overtake_aggression'].mean()),
                        'defense_intensity': float(bottom_agents['defense_intensity'].mean())
                    }
                }
            },
            'situational_patterns': patterns
        }

        return analysis

    def synthesize_playbook(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to synthesize patterns into actionable playbook rules.

        Args:
            analysis: Analysis dict from analyze_simulation_data

        Returns:
            Playbook dict with rules, confidence scores, and rationales
        """
        print("Calling Gemini API for pattern synthesis...")

        # Construct prompt for Gemini
        prompt = f"""You are an F1 strategy expert analyzing simulation data from 2026 regulations.
The 2026 F1 cars have 3x more electric power (350kW vs 120kW), creating a 50/50 ICE/Electric split.

I have simulation data comparing winning vs losing strategies. Please analyze the patterns and generate
specific, actionable strategic rules.

SIMULATION DATA:
{json.dumps(analysis, indent=2)}

Based on this data, generate 5-7 strategic rules for optimal performance. Each rule should:
1. Have a clear condition (when to apply it)
2. Specify exact action values for the 6 strategic variables
3. Include a confidence score (0.0-1.0) based on data support
4. Provide a brief rationale explaining why it works

IMPORTANT: Generate rules that reflect the actual patterns in the data, not generic F1 wisdom.
Focus on situations where winners significantly outperform losers.

Return ONLY a valid JSON object (no markdown backticks) in this exact format:
{{
  "rules": [
    {{
      "rule": "Short descriptive name",
      "condition": "battery_soc < 30 and lap > 40",
      "action": {{
        "energy_deployment": 25,
        "tire_management": 60,
        "fuel_strategy": 45,
        "ers_mode": 15,
        "overtake_aggression": 40,
        "defense_intensity": 80
      }},
      "confidence": 0.85,
      "uplift_win_pct": 15.2,
      "rationale": "Brief explanation of why this works based on the data"
    }}
  ]
}}

Make sure:
- Conditions use only these variables: battery_soc, lap, position, tire_life, tire_age, fuel_remaining
- All action values are between 0-100
- Confidence reflects the sample size and performance difference
- Uplift is realistic (typically 5-30%)
"""

        # Make API call with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                raw_response = response.text

                # Extract JSON from response (handle markdown wrappers)
                json_match = re.search(r'(\{[\s\S]*\})', raw_response)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to clean common wrapper patterns
                    json_str = raw_response.replace('```json', '').replace('```', '').strip()

                # Parse JSON
                playbook_data = json.loads(json_str)

                # Validate structure
                if 'rules' not in playbook_data:
                    raise ValueError("Response missing 'rules' key")

                print(f"✅ Gemini generated {len(playbook_data['rules'])} rules")
                return playbook_data

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print("⚠️ Gemini API failed, using fallback rules")
                    return self._generate_fallback_playbook(analysis)

    def _generate_fallback_playbook(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback playbook if Gemini API fails.
        Uses simple data-driven heuristics.
        """
        print("Generating fallback playbook from data patterns...")

        top_profile = analysis['performance_groups']['top_25_percent']['strategy_profile']
        bottom_profile = analysis['performance_groups']['bottom_25_percent']['strategy_profile']

        rules = []

        # Rule 1: Low battery conservation (if we have that pattern)
        if 'low_battery_late_race' in analysis['situational_patterns']:
            pattern = analysis['situational_patterns']['low_battery_late_race']
            if pattern['sample_size'] > 10:
                rules.append({
                    "rule": "Low Battery Conservation",
                    "condition": "battery_soc < 30 and lap > 40",
                    "action": {
                        "energy_deployment": max(15, pattern['winner_strategy'].get('energy_deployment', 20)),
                        "tire_management": 60,
                        "fuel_strategy": 45,
                        "ers_mode": max(10, pattern['winner_strategy'].get('ers_mode', 15)),
                        "overtake_aggression": 40,
                        "defense_intensity": 85
                    },
                    "confidence": min(0.75, pattern['sample_size'] / 100),
                    "uplift_win_pct": 15.0,
                    "rationale": "Data shows winners conserve energy aggressively when battery is low"
                })

        # Rule 2: Early race based on top performers
        rules.append({
            "rule": "Early Race Aggression",
            "condition": "lap < 15 and battery_soc > 70",
            "action": {
                "energy_deployment": min(90, top_profile['energy_deployment'] * 1.3),
                "tire_management": top_profile['tire_management'],
                "fuel_strategy": top_profile['fuel_strategy'],
                "ers_mode": min(85, top_profile['ers_mode'] * 1.4),
                "overtake_aggression": min(90, top_profile['overtake_aggression'] * 1.2),
                "defense_intensity": top_profile['defense_intensity']
            },
            "confidence": 0.70,
            "uplift_win_pct": 12.0,
            "rationale": "Top performers deploy more energy early when battery is full"
        })

        # Rule 3: General winning strategy
        rules.append({
            "rule": "Balanced Performance",
            "condition": "lap > 15 and lap < 45",
            "action": top_profile,
            "confidence": 0.65,
            "uplift_win_pct": 8.0,
            "rationale": "Average strategy of top 25% performers"
        })

        return {"rules": rules, "fallback": True}

    def generate_complete_playbook(self, csv_path: str = 'data/discovery_runs.csv') -> Dict[str, Any]:
        """
        Complete pipeline: Load data → Analyze → Synthesize → Generate playbook.

        Args:
            csv_path: Path to simulation results CSV

        Returns:
            Complete playbook dict ready for AdaptiveAI
        """
        print("\n" + "="*60)
        print("AI STRATEGY DISCOVERY PIPELINE")
        print("="*60)

        # Load simulation data
        print(f"\nLoading simulation data from {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df):,} rows, {df['scenario_id'].nunique()} scenarios, {df['agent'].nunique()} agents")

        # Analyze patterns
        print("\nAnalyzing performance patterns...")
        analysis = self.analyze_simulation_data(df)

        # Calculate some stats for display
        top_win_rate = analysis['performance_groups']['top_25_percent']['avg_win_rate']
        bottom_win_rate = analysis['performance_groups']['bottom_25_percent']['avg_win_rate']
        print(f"Top 25% agents win rate: {top_win_rate:.1%}")
        print(f"Bottom 25% agents win rate: {bottom_win_rate:.1%}")

        # Synthesize playbook using Gemini
        print("\nSynthesizing strategic patterns with Gemini...")
        playbook_data = self.synthesize_playbook(analysis)

        # Enhance playbook with metadata
        playbook = {
            "rules": playbook_data.get("rules", []),
            "generated_at": pd.Timestamp.now().isoformat(),
            "num_simulations": df['scenario_id'].nunique(),
            "schema_version": "2.0",
            "variables": [
                "energy_deployment",
                "tire_management",
                "fuel_strategy",
                "ers_mode",
                "overtake_aggression",
                "defense_intensity"
            ],
            "generation_method": "gemini_discovery" if not playbook_data.get("fallback") else "fallback_heuristics",
            "source_data": {
                "csv_path": csv_path,
                "num_scenarios": df['scenario_id'].nunique(),
                "num_agents": df['agent'].nunique(),
                "total_rows": len(df)
            }
        }

        # Save playbook
        output_path = 'data/playbook_discovered.json'
        with open(output_path, 'w') as f:
            json.dump(playbook, f, indent=2)

        print(f"\n✅ Playbook saved to {output_path}")
        print(f"   Generated {len(playbook['rules'])} rules using {playbook['generation_method']}")

        # Display rule summary
        print("\nDiscovered Rules:")
        for i, rule in enumerate(playbook['rules'], 1):
            print(f"  {i}. {rule['rule']} (confidence: {rule['confidence']:.0%}, "
                  f"uplift: +{rule.get('uplift_win_pct', 0):.1f}%)")

        return playbook


def main():
    """Main entry point for strategy discovery."""
    import sys

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️ GEMINI_API_KEY not found in environment!")
        print("Please either:")
        print("1. Create a .env file with: GEMINI_API_KEY=your_key_here")
        print("2. Export it: export GEMINI_API_KEY=your_key_here")
        print("\nGet your API key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    # Initialize discoverer
    try:
        discoverer = StrategyDiscoverer()
    except ValueError as e:
        print(e)
        sys.exit(1)

    # Check if discovery data exists
    csv_path = 'data/discovery_runs.csv'
    if not Path(csv_path).exists():
        print(f"\n⚠️ Discovery data not found at {csv_path}")
        print("Please run: python scripts/generate_discovery_data.py")
        sys.exit(1)

    # Generate playbook
    playbook = discoverer.generate_complete_playbook(csv_path)

    print("\n" + "="*60)
    print("✅ AI STRATEGY DISCOVERY COMPLETE")
    print("="*60)
    print(f"Next steps:")
    print(f"1. Copy playbook: cp data/playbook_discovered.json data/playbook.json")
    print(f"2. Validate: python scripts/validate_discovery.py")
    print(f"3. Benchmark: python scripts/comprehensive_benchmark.py")


if __name__ == '__main__':
    main()