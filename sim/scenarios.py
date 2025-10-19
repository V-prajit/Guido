"""
Strategy Gym 2026 - Scenario Generation

This module generates realistic race scenarios based on 2024 Bahrain Grand Prix
characteristics for testing different energy deployment strategies across varying
conditions (track types, weather, tire strategies).
"""

import numpy as np
import json
import os
from pathlib import Path


def generate_scenarios(num_scenarios: int, seed: int = None) -> list[dict]:
    """
    Generate realistic F1 race scenarios based on 2024 Bahrain GP characteristics.

    Each scenario represents a unique race configuration with varying:
    - Race length (57 laps for Bahrain GP)
    - Weather conditions (10% chance of rain - rare in desert climate)
    - Safety car events (33% chance)
    - Track characteristics (power/technical/balanced)
    - Realistic temperature range (17.6-18.9°C - night race)
    - Wind conditions (low/medium/high)
    - Tire strategies based on 2024 race data
    - Randomized starting grid positions

    Uses deterministic seeding (based on scenario ID or provided seed) to ensure
    reproducibility across runs. This is critical for validation and benchmarking.

    Args:
        num_scenarios: Number of scenarios to generate
        seed: Optional random seed for reproducibility. If None, uses scenario ID
              as seed for deterministic generation.

    Returns:
        List of scenario dictionaries, each containing:
            - id: Sequential scenario identifier (0 to n-1)
            - num_laps: Race length (57 laps for Bahrain)
            - rain_lap: Lap when rain starts (None if no rain), 10% probability
            - safety_car_lap: Lap when safety car deploys (None if none), 33% probability
            - track_type: Track characteristic ('power' | 'technical' | 'balanced')
            - temperature: Ambient temperature in Celsius (17.6-18.9°C)
            - wind: Wind conditions ('low' | 'medium' | 'high')
            - tire_strategy: Tire compound strategy ('soft-hard' | 'medium-hard' | 'soft-soft')
            - starting_positions: Randomized starting grid [1-8]

    Example:
        >>> scenarios = generate_scenarios(3, seed=42)
        >>> len(scenarios)
        3
        >>> all('num_laps' in s for s in scenarios)
        True
        >>> scenarios[0]['num_laps']
        57
    """
    # Load real baseline parameters from 2024 Bahrain GP
    baseline = _load_baseline_data()

    scenarios = []

    for i in range(num_scenarios):
        # Use deterministic seed for reproducibility
        # If seed is provided, use it with scenario ID; otherwise just use scenario ID
        if seed is not None:
            np.random.seed(seed + i)
        else:
            np.random.seed(i)

        scenario = _generate_single_scenario(i, baseline)
        scenarios.append(scenario)

    return scenarios


def _load_baseline_data() -> dict:
    """
    Load baseline parameters from 2024 Bahrain GP data.

    Returns:
        Dictionary with baseline race parameters. Falls back to hardcoded
        values if data file is not found.
    """
    try:
        # Try to load from data directory
        data_path = Path(__file__).parent.parent / 'data' / 'baseline_2024.json'
        with open(data_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to hardcoded Bahrain GP values
        return {
            'race_info': {
                'num_laps': 57,
                'track_name': 'Bahrain International Circuit'
            },
            'track_characteristics': {
                'temperature_range': [17.6, 18.9],
                'base_lap_time': 96.8
            },
            'tire_compounds': {
                'SOFT': {'base_time': 98.4, 'deg_rate': 0.01},
                'HARD': {'base_time': 96.66, 'deg_rate': 0.022}
            }
        }


def _generate_single_scenario(scenario_id: int, baseline: dict) -> dict:
    """
    Generate one realistic scenario based on Bahrain GP characteristics.

    Args:
        scenario_id: Unique identifier for this scenario
        baseline: Baseline parameters from 2024 race data

    Returns:
        Dictionary containing scenario configuration
    """
    # Base race parameters from Bahrain GP
    num_laps = baseline.get('race_info', {}).get('num_laps', 57)

    # Track type affects optimal strategy
    # Bahrain is a power track (long straights), but we vary for diversity
    # - 'power': Long straights favor straight line deployment (60% probability for Bahrain)
    # - 'technical': Many corners favor corner deployment (20%)
    # - 'balanced': Mix of both (20%)
    track_type = np.random.choice(
        ['power', 'technical', 'balanced'],
        p=[0.60, 0.20, 0.20]
    )

    # Temperature range for strategic diversity
    # For discovery/training: use wide range (15-35°C) to test hot/cold strategies
    # For Bahrain-specific validation: [17.6, 18.9°C] from 2024 data
    # Default to wide range for strategy exploration
    temp_range = [15, 35]  # Wide range creates hot/cold strategic diversity
    temperature = float(np.random.uniform(temp_range[0], temp_range[1]))

    # Wind conditions affect straight-line speed and overtaking
    wind = np.random.choice(['low', 'medium', 'high'], p=[0.50, 0.35, 0.15])

    # Rain event (10% chance - Bahrain is desert climate, rain is very rare)
    # When it does occur, it's typically in later stages of race
    rain_lap = None
    if np.random.random() < 0.10:
        # Ensure rain lap doesn't exceed race length
        max_rain_lap = min(50, num_laps - 5)
        if max_rain_lap >= 20:
            rain_lap = int(np.random.randint(20, max_rain_lap + 1))

    # Safety car event (33% chance between lap 15-40)
    # Probability based on historical F1 statistics
    safety_car_lap = None
    if np.random.random() < 0.33:
        # Ensure safety car lap doesn't exceed race length
        max_sc_lap = min(40, num_laps - 10)
        if max_sc_lap >= 15:
            safety_car_lap = int(np.random.randint(15, max_sc_lap + 1))

    # Tire strategies based on 2024 Bahrain GP data
    # Most teams ran soft-hard single stop (70%)
    # Conservative teams ran medium-hard (25%)
    # Risky two-stop with soft-soft was rare (5%)
    tire_strategy = np.random.choice(
        ['soft-hard', 'medium-hard', 'soft-soft'],
        p=[0.70, 0.25, 0.05]
    )

    # Starting grid positions (randomized for each scenario)
    # Simulates different qualifying outcomes
    starting_positions = list(range(1, 9))  # 8 agents
    np.random.shuffle(starting_positions)

    # Build scenario dictionary
    return {
        'id': scenario_id,
        'num_laps': int(num_laps),
        'track_type': track_type,
        'rain_lap': rain_lap,
        'safety_car_lap': safety_car_lap,
        'temperature': round(temperature, 1),
        'wind': wind,
        'tire_strategy': tire_strategy,
        'starting_positions': starting_positions
    }
