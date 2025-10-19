import random
import numpy as np

def generate_scenarios(n: int) -> list:
    """Generate n racing scenarios with realistic parameters"""
    scenarios = []
    
    tracks = ['monaco', 'silverstone', 'spa', 'monza', 'suzuka', 'interlagos']
    weather_conditions = ['dry', 'wet', 'mixed', 'overcast']
    
    for i in range(n):
        scenario = {
            'track_id': random.choice(tracks),
            'weather': random.choice(weather_conditions),
            'temperature': random.randint(15, 35),
            'humidity': random.randint(40, 90),
            'wind_speed': random.randint(0, 25),
            'track_grip': random.uniform(0.7, 1.0),
            'safety_car_probability': random.uniform(0.1, 0.3),
            'seed': random.randint(1000, 9999),
            'laps': random.randint(50, 70),
            'pit_window_start': random.randint(15, 25),
            'pit_window_end': random.randint(35, 45)
        }
        scenarios.append(scenario)
    
    return scenarios