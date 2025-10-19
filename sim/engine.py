import pandas as pd
import numpy as np
import random

def simulate_race(scenario: dict, agents: list) -> pd.DataFrame:
    """Simulate a race scenario with given agents"""
    
    # Set random seed for reproducible results
    np.random.seed(scenario.get('seed', 42))
    random.seed(scenario.get('seed', 42))
    
    num_agents = len(agents)
    laps = scenario.get('laps', 60)
    
    # Initialize race data
    data = []
    
    # Simulate race positions and performance
    base_lap_time = 90.0  # Base lap time in seconds
    weather_factor = 1.1 if scenario.get('weather') == 'wet' else 1.0
    
    for i, agent in enumerate(agents):
        agent_name = agent if isinstance(agent, str) else agent.name
        
        # Agent-specific performance characteristics
        if 'Conservative' in agent_name:
            speed_factor = 0.98
            consistency = 0.95
            battery_efficiency = 1.1
        elif 'Aggressive' in agent_name:
            speed_factor = 1.02
            consistency = 0.85
            battery_efficiency = 0.9
        elif 'Balanced' in agent_name:
            speed_factor = 1.0
            consistency = 0.9
            battery_efficiency = 1.0
        else:
            speed_factor = np.random.uniform(0.95, 1.05)
            consistency = np.random.uniform(0.8, 0.95)
            battery_efficiency = np.random.uniform(0.9, 1.1)
        
        # Calculate race performance
        avg_lap_time = base_lap_time * weather_factor * speed_factor
        lap_time_variation = avg_lap_time * (1 - consistency) * 0.1
        
        # Final lap time with some randomness
        final_lap_time = avg_lap_time + np.random.uniform(-lap_time_variation, lap_time_variation)
        
        # Battery simulation
        base_battery_consumption = 100 / laps  # Base consumption per lap
        actual_consumption = base_battery_consumption / battery_efficiency
        final_battery = max(5, 100 - (actual_consumption * laps) + np.random.uniform(-10, 10))
        
        # Position calculation (faster lap times = better positions)
        position_score = final_lap_time + np.random.uniform(0, 2)
        
        data.append({
            'agent': agent_name,
            'final_position': 0,  # Will be calculated after sorting
            'battery_soc': final_battery,
            'lap_time': final_lap_time,
            'won': 0,  # Will be set for winner
            'position_score': position_score,
            'laps_completed': laps,
            'avg_speed': 300 / (final_lap_time / 60),  # km/h approximation
            'consistency_rating': consistency,
            'strategy_effectiveness': np.random.uniform(0.6, 1.0)
        })
    
    # Convert to DataFrame and calculate positions
    df = pd.DataFrame(data)
    
    # Sort by position score (lower is better) and assign positions
    df = df.sort_values('position_score').reset_index(drop=True)
    df['final_position'] = range(1, len(df) + 1)
    
    # Mark winner
    df.loc[0, 'won'] = 1
    
    # Remove helper column
    df = df.drop('position_score', axis=1)
    
    return df