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
            "win_rate": float
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
        
        stats[agent] = {
            "wins": int(agent_data['won'].sum()),
            "avg_position": float(agent_data['final_position'].mean()),
            "avg_battery": float(agent_data['battery_soc'].mean()),
            "win_rate": float(agent_data['won'].sum() / total_scenarios * 100),
            "avg_lap_time": float(agent_data['lap_time'].mean()),
            "total_races": len(agent_data)
        }
    
    return stats