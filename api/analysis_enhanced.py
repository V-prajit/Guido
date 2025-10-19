"""
Enhanced analysis module that integrates with Gemini AI discovery.

This module provides:
1. Standard result aggregation (original functionality)
2. Integration with Gemini discovery pipeline
3. Real-time playbook generation from simulation data
"""

import pandas as pd
import glob
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_latest_run() -> str:
    """Get path to latest CSV file"""
    csvs = glob.glob('runs/*.csv')
    if not csvs:
        raise FileNotFoundError("No run files found")
    return max(csvs, key=os.path.getctime)


def aggregate_results(csv_path: str) -> dict:
    """
    Aggregate simulation results.

    Returns stats like:
    {
        "agent_name": {
            "wins": int,
            "avg_position": float,
            "avg_battery": float,
            "avg_tire_life": float,
            "avg_fuel_remaining": float,
            "win_rate": float,
            "avg_energy_deployment": float,
            "avg_tire_management": float,
            "avg_fuel_strategy": float,
            "avg_ers_mode": float,
            "avg_overtake_aggression": float,
            "avg_defense_intensity": float
        }
    }
    """
    df = pd.read_csv(csv_path)

    # Get final state for each race
    final_states = df.groupby(['scenario_id', 'agent']).tail(1)

    # Calculate stats per agent
    stats = {}
    total_scenarios = final_states['scenario_id'].nunique()

    for agent in final_states['agent'].unique():
        agent_data = final_states[final_states['agent'] == agent]

        # Get all laps for this agent for decision variable averages
        agent_all_laps = df[df['agent'] == agent]

        stats[agent] = {
            # Race results
            "wins": int(agent_data['won'].sum()),
            "avg_position": float(agent_data['final_position'].mean()),
            "win_rate": float(agent_data['won'].sum() / total_scenarios * 100),
            "total_races": len(agent_data),

            # Performance metrics
            "avg_lap_time": float(agent_data['lap_time'].mean()),

            # Final state resources (from last lap only)
            "avg_final_battery": float(agent_data['battery_soc'].mean()),
            "avg_final_tire_life": float(agent_data['tire_life'].mean()),
            "avg_final_fuel": float(agent_data['fuel_remaining'].mean()),

            # Strategy decision averages (across all laps)
            "avg_energy_deployment": float(agent_all_laps['energy_deployment'].mean()),
            "avg_tire_management": float(agent_all_laps['tire_management'].mean()),
            "avg_fuel_strategy": float(agent_all_laps['fuel_strategy'].mean()),
            "avg_ers_mode": float(agent_all_laps['ers_mode'].mean()),
            "avg_overtake_aggression": float(agent_all_laps['overtake_aggression'].mean()),
            "avg_defense_intensity": float(agent_all_laps['defense_intensity'].mean())
        }

    return stats


def analyze_with_gemini(csv_path: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
    """
    Analyze simulation results using Gemini AI discovery.

    Args:
        csv_path: Path to CSV file (defaults to latest run)
        use_cache: Whether to use cached playbook if recent

    Returns:
        Dict with analysis results and generated playbook
    """
    # Get CSV path
    if csv_path is None:
        csv_path = get_latest_run()

    # Check if we should use cached playbook
    playbook_path = Path('data/playbook_discovered.json')
    if use_cache and playbook_path.exists():
        # Check if playbook is recent (< 1 hour old)
        import time
        age_seconds = time.time() - playbook_path.stat().st_mtime
        if age_seconds < 3600:  # 1 hour
            print(f"Using cached playbook (age: {age_seconds/60:.1f} minutes)")
            with open(playbook_path) as f:
                playbook = json.load(f)

            # Still calculate stats
            stats = aggregate_results(csv_path)

            return {
                "stats": stats,
                "playbook": playbook,
                "playbook_preview": {
                    "num_rules": len(playbook.get("rules", [])),
                    "generation_method": playbook.get("generation_method", "unknown"),
                    "cached": True
                },
                "csv_analyzed": csv_path
            }

    # Run Gemini discovery
    try:
        print("Running Gemini AI discovery on simulation data...")

        # Import here to avoid circular dependencies
        from api.gemini_discovery import StrategyDiscoverer

        # Check for API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️ GEMINI_API_KEY not found, using fallback rules")
            # Fall back to simple aggregation
            from api.gemini import synthesize_playbook
            stats = aggregate_results(csv_path)
            df = pd.read_csv(csv_path)
            playbook = synthesize_playbook(stats, df)
        else:
            # Use real Gemini discovery
            discoverer = StrategyDiscoverer(api_key)

            # Load data
            df = pd.read_csv(csv_path)

            # Analyze and generate playbook
            analysis = discoverer.analyze_simulation_data(df)
            playbook_data = discoverer.synthesize_playbook(analysis)

            # Enhance with metadata
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
                "generation_method": "gemini_discovery" if not playbook_data.get("fallback") else "fallback",
                "source_data": {
                    "csv_path": csv_path,
                    "num_scenarios": df['scenario_id'].nunique(),
                    "num_agents": df['agent'].nunique()
                }
            }

            # Save discovered playbook
            with open(playbook_path, 'w') as f:
                json.dump(playbook, f, indent=2)
            print(f"✅ Saved discovered playbook to {playbook_path}")

            # Also update main playbook for AdaptiveAI
            main_playbook_path = Path('data/playbook.json')
            with open(main_playbook_path, 'w') as f:
                json.dump(playbook, f, indent=2)
            print(f"✅ Updated main playbook for AdaptiveAI")

            # Calculate stats
            stats = aggregate_results(csv_path)

    except Exception as e:
        print(f"⚠️ Gemini discovery failed: {e}")
        print("Falling back to standard analysis...")

        # Fall back to simple aggregation
        from api.gemini import synthesize_playbook
        stats = aggregate_results(csv_path)
        df = pd.read_csv(csv_path)
        playbook = synthesize_playbook(stats, df)

    return {
        "stats": stats,
        "playbook": playbook,
        "playbook_preview": {
            "num_rules": len(playbook.get("rules", [])),
            "generation_method": playbook.get("generation_method", "fallback"),
            "cached": False
        },
        "csv_analyzed": csv_path
    }


def get_playbook_metrics(playbook: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key metrics from a playbook.

    Args:
        playbook: Playbook dict

    Returns:
        Dict with playbook metrics
    """
    rules = playbook.get("rules", [])

    if not rules:
        return {
            "num_rules": 0,
            "avg_confidence": 0,
            "avg_uplift": 0,
            "coverage_situations": []
        }

    # Calculate averages
    confidences = [r.get("confidence", 0) for r in rules]
    uplifts = [r.get("uplift_win_pct", 0) for r in rules]

    # Extract situation coverage
    situations = []
    for rule in rules:
        condition = rule.get("condition", "")
        if "battery_soc < 30" in condition:
            situations.append("low_battery")
        if "lap < 15" in condition:
            situations.append("early_race")
        if "lap > 45" in condition or "lap > 50" in condition:
            situations.append("late_race")
        if "tire_life < " in condition:
            situations.append("degraded_tires")
        if "position" in condition:
            situations.append("position_based")

    return {
        "num_rules": len(rules),
        "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
        "avg_uplift": sum(uplifts) / len(uplifts) if uplifts else 0,
        "coverage_situations": list(set(situations)),
        "generation_method": playbook.get("generation_method", "unknown")
    }