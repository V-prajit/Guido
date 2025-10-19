"""
Strategy Gym 2026 - Scenario Generation

This module generates diverse race scenarios for testing different energy
deployment strategies across varying conditions (track types, weather, race length).
"""

import numpy as np


def generate_scenarios(num_scenarios: int) -> list[dict]:
    """
    Generate diverse race scenarios with deterministic seeding.

    Each scenario represents a unique race configuration with varying:
    - Race length (50, 57, or 70 laps)
    - Weather conditions (25% chance of rain)
    - Safety car events (33% chance)
    - Track characteristics (power/technical/balanced)
    - Ambient temperature

    Uses deterministic seeding (based on scenario ID) to ensure reproducibility
    across runs. This is critical for validation and benchmarking.

    Args:
        num_scenarios: Number of scenarios to generate

    Returns:
        List of scenario dictionaries, each containing:
            - id: Sequential scenario identifier (0 to n-1)
            - num_laps: Race length (50, 57, or 70 laps)
            - rain_lap: Lap when rain starts (None if no rain), 25% probability
            - safety_car_lap: Lap when safety car deploys (None if none), 33% probability
            - track_type: Track characteristic ('power' | 'technical' | 'balanced')
            - temperature: Ambient temperature in Celsius (20.0-35.0)

    Example:
        >>> scenarios = generate_scenarios(3)
        >>> len(scenarios)
        3
        >>> all('num_laps' in s for s in scenarios)
        True
    """
    scenarios = []

    for i in range(num_scenarios):
        # Use deterministic seed for reproducibility
        # Each scenario gets its own seed based on ID
        np.random.seed(i)

        # Race length distribution
        # Common lengths: 50 (short), 57 (standard), 70 (long)
        num_laps = np.random.choice([50, 57, 70])

        # Rain event (25% chance between lap 20-50)
        # Rain adds 2.0s penalty per lap (handled in simulate_lap)
        rain_lap = None
        if np.random.random() < 0.25:
            # Ensure rain lap doesn't exceed race length
            max_rain_lap = min(50, num_laps)
            if max_rain_lap >= 20:
                rain_lap = int(np.random.randint(20, max_rain_lap + 1))

        # Safety car event (33% chance between lap 15-40)
        # Note: Current physics model doesn't apply SC penalty,
        # but infrastructure is ready for future implementation
        safety_car_lap = None
        if np.random.random() < 0.33:
            # Ensure safety car lap doesn't exceed race length
            max_sc_lap = min(40, num_laps)
            if max_sc_lap >= 15:
                safety_car_lap = int(np.random.randint(15, max_sc_lap + 1))

        # Track type affects optimal strategy
        # - 'power': Long straights favor straight line deployment
        # - 'technical': Many corners favor corner deployment
        # - 'balanced': Mix of both
        track_type = np.random.choice(['power', 'technical', 'balanced'])

        # Ambient temperature (20-35°C)
        # Future: Could affect battery efficiency, tire degradation
        temperature = float(np.random.uniform(20.0, 35.0))

        # Build scenario dictionary
        scenarios.append({
            'id': i,
            'num_laps': int(num_laps),
            'rain_lap': rain_lap,
            'safety_car_lap': safety_car_lap,
            'track_type': track_type,
            'temperature': temperature
        })

    return scenarios
