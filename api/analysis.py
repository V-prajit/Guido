import pandas as pd
import glob
import os

def get_latest_run() -> str:
    """Get path to latest CSV file"""
    csvs = glob.glob('runs/*.csv')
    if not csvs:
        raise FileNotFoundError("No run files found")
    return max(csvs, key=os.path.getctime)

def aggregate_results(csv_path: str) -> dict:
    """Aggregate simulation results.

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