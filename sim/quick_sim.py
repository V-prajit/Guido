"""
Quick simulation runner for game loop decision points.

Runs fast simulations from current race state to finish line.
Used by GameAdvisor to test strategic alternatives.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class RaceState:
    """Current race state at decision point."""
    lap: int
    total_laps: int
    position: int
    battery_soc: float
    tire_life: float
    fuel_remaining: float
    gap_ahead: float = 0.0  # seconds
    gap_behind: float = 0.0
    rain: bool = False
    safety_car: bool = False


def run_quick_sims_from_state(
    current_state: RaceState,
    strategy_params: List[Dict],
    num_sims_per_strategy: int = 100
) -> pd.DataFrame:
    """
    Run quick simulations from current race state to finish.

    Args:
        current_state: Current race state (lap, position, battery, etc.)
        strategy_params: List of 3 strategy configurations to test
        num_sims_per_strategy: Number of simulations per strategy (default 100)

    Returns:
        DataFrame with simulation results (300 rows = 100 × 3 strategies)

        Columns:
            - strategy_id (int): 0, 1, or 2
            - sim_run_id (int): 0-99
            - final_position (int): Final race position
            - won (bool): True if won race
            - battery_soc (float): Final battery level
            - tire_life (float): Final tire life
            - fuel_remaining (float): Final fuel

    Example:
        >>> state = RaceState(lap=15, total_laps=57, position=4, battery_soc=45.0, ...)
        >>> strategies = [aggressive, balanced, conservative]
        >>> results = run_quick_sims_from_state(state, strategies, num_sims=100)
        >>> print(len(results))  # 300
    """

    results = []

    for strategy_id, params in enumerate(strategy_params):
        for sim_run in range(num_sims_per_strategy):
            # Run single simulation from current state to finish
            result = _simulate_single_race_from_state(
                current_state,
                params,
                sim_run
            )

            results.append({
                'strategy_id': strategy_id,
                'sim_run_id': sim_run,
                'final_position': result['position'],
                'won': result['position'] == 1,
                'battery_soc': result['battery_soc'],
                'tire_life': result['tire_life'],
                'fuel_remaining': result['fuel_remaining']
            })

    return pd.DataFrame(results)


def _simulate_single_race_from_state(
    state: RaceState,
    strategy: Dict,
    seed: int
) -> Dict:
    """
    Simulate one race from current state to finish.

    This is a SIMPLIFIED simulation for speed.
    Uses probabilistic model based on strategy parameters.
    """

    np.random.seed(seed)

    # Remaining laps to simulate
    remaining_laps = state.total_laps - state.lap

    # Starting resources
    battery = state.battery_soc
    tires = state.tire_life
    fuel = state.fuel_remaining
    position = state.position

    # Strategy parameters (0-100 each)
    energy_deploy = strategy['energy_deployment']
    tire_mgmt = strategy['tire_management']
    fuel_strat = strategy['fuel_strategy']
    ers_mode = strategy['ers_mode']
    overtake_agg = strategy['overtake_aggression']
    defense_int = strategy['defense_intensity']

    # Simulate lap-by-lap
    for lap in range(remaining_laps):
        # Battery dynamics
        battery_drain = (energy_deploy / 100) * 0.8  # Drain per lap
        battery_gain = (ers_mode / 100) * 0.6        # Recovery per lap
        battery = max(0, min(100, battery - battery_drain + battery_gain))

        # Tire degradation
        tire_wear = (100 - tire_mgmt) / 100 * 1.5  # Higher management = less wear
        tires = max(0, tires - tire_wear)

        # Fuel consumption
        fuel_burn = (100 - fuel_strat) / 100 * 0.5  # Higher strategy = less burn
        fuel = max(0, fuel - fuel_burn)

        # Position changes (probabilistic)
        # Higher deployment + aggression = more overtakes
        # Lower defense = more vulnerable to overtakes

        overtake_chance = (energy_deploy + overtake_agg) / 200 * 0.15
        defend_chance = defense_int / 100 * 0.12

        # Rain increases position volatility
        if state.rain:
            overtake_chance *= 1.5
            defend_chance *= 0.8

        # Try to gain positions
        if position > 1 and np.random.random() < overtake_chance:
            position -= 1  # Gain position

        # Risk losing positions
        if position < 8 and np.random.random() < (0.1 - defend_chance):
            position += 1  # Lose position

        # Penalty for depleted resources
        if battery < 5:
            # Critical battery - lose positions
            if np.random.random() < 0.3:
                position = min(8, position + 1)

        if tires < 10:
            # Critical tires - lose positions
            if np.random.random() < 0.4:
                position = min(8, position + 1)

    # Final position influenced by strategy effectiveness
    # Balanced strategies get small boost
    if 40 <= energy_deploy <= 70 and 60 <= tire_mgmt <= 85:
        # Balanced approach - slight advantage
        if np.random.random() < 0.2:
            position = max(1, position - 1)

    # Aggressive strategies - high variance
    if energy_deploy > 80 and overtake_agg > 80:
        # High risk, high reward
        if np.random.random() < 0.25:
            position = max(1, position - 2)  # Big gain
        elif np.random.random() < 0.15:
            position = min(8, position + 2)  # Big loss

    # Conservative strategies - tend to lose positions
    if energy_deploy < 40 and overtake_agg < 40:
        # Too passive
        if np.random.random() < 0.4:
            position = min(8, position + 1)

    return {
        'position': int(position),
        'battery_soc': float(battery),
        'tire_life': float(tires),
        'fuel_remaining': float(fuel)
    }


# ==========================================
# STRATEGY VARIATION GENERATOR
# ==========================================

def generate_strategy_variations(
    current_state: RaceState,
    event_type: str
) -> List[Dict]:
    """
    Generate 3 strategic alternatives based on event type.

    Args:
        current_state: Current race state
        event_type: 'RAIN_START', 'SAFETY_CAR', 'TIRE_CRITICAL', etc.

    Returns:
        List of 3 strategy dicts: [aggressive, balanced, conservative]

    Example:
        >>> state = RaceState(lap=15, battery_soc=45, ...)
        >>> strategies = generate_strategy_variations(state, 'RAIN_START')
        >>> len(strategies)  # 3
    """

    if event_type == 'RAIN_START':
        return [
            # Aggressive: Deploy heavily in rain
            {
                'energy_deployment': 85,
                'tire_management': 70,
                'fuel_strategy': 60,
                'ers_mode': 80,
                'overtake_aggression': 90,
                'defense_intensity': 40
            },
            # Balanced: Moderate approach
            {
                'energy_deployment': 60,
                'tire_management': 80,
                'fuel_strategy': 70,
                'ers_mode': 65,
                'overtake_aggression': 60,
                'defense_intensity': 55
            },
            # Conservative: Preserve in rain
            {
                'energy_deployment': 35,
                'tire_management': 90,
                'fuel_strategy': 85,
                'ers_mode': 50,
                'overtake_aggression': 30,
                'defense_intensity': 70
            }
        ]

    elif event_type == 'TIRE_CRITICAL':
        return [
            # Aggressive: Push on worn tires
            {
                'energy_deployment': 90,
                'tire_management': 40,
                'fuel_strategy': 60,
                'ers_mode': 85,
                'overtake_aggression': 85,
                'defense_intensity': 35
            },
            # Balanced: Careful management
            {
                'energy_deployment': 60,
                'tire_management': 70,
                'fuel_strategy': 65,
                'ers_mode': 65,
                'overtake_aggression': 55,
                'defense_intensity': 60
            },
            # Conservative: Max preservation
            {
                'energy_deployment': 30,
                'tire_management': 95,
                'fuel_strategy': 80,
                'ers_mode': 50,
                'overtake_aggression': 25,
                'defense_intensity': 75
            }
        ]

    elif event_type == 'BATTERY_LOW':
        return [
            # Aggressive: Risk it, keep deploying
            {
                'energy_deployment': 70,
                'tire_management': 75,
                'fuel_strategy': 65,
                'ers_mode': 95,  # Max recovery
                'overtake_aggression': 60,
                'defense_intensity': 50
            },
            # Balanced: Moderate recovery
            {
                'energy_deployment': 45,
                'tire_management': 80,
                'fuel_strategy': 70,
                'ers_mode': 85,
                'overtake_aggression': 45,
                'defense_intensity': 60
            },
            # Conservative: Heavy harvesting
            {
                'energy_deployment': 20,
                'tire_management': 85,
                'fuel_strategy': 80,
                'ers_mode': 95,
                'overtake_aggression': 25,
                'defense_intensity': 70
            }
        ]

    elif event_type == 'SAFETY_CAR':
        return [
            # Aggressive: Attack on restart
            {
                'energy_deployment': 90,
                'tire_management': 65,
                'fuel_strategy': 55,
                'ers_mode': 80,
                'overtake_aggression': 95,
                'defense_intensity': 30
            },
            # Balanced: Maintain on restart
            {
                'energy_deployment': 65,
                'tire_management': 75,
                'fuel_strategy': 65,
                'ers_mode': 70,
                'overtake_aggression': 65,
                'defense_intensity': 55
            },
            # Conservative: Defend on restart
            {
                'energy_deployment': 40,
                'tire_management': 85,
                'fuel_strategy': 80,
                'ers_mode': 60,
                'overtake_aggression': 35,
                'defense_intensity': 80
            }
        ]

    else:
        # Default: General alternatives
        return [
            {
                'energy_deployment': 80,
                'tire_management': 70,
                'fuel_strategy': 60,
                'ers_mode': 80,
                'overtake_aggression': 85,
                'defense_intensity': 45
            },
            {
                'energy_deployment': 60,
                'tire_management': 80,
                'fuel_strategy': 70,
                'ers_mode': 65,
                'overtake_aggression': 60,
                'defense_intensity': 55
            },
            {
                'energy_deployment': 35,
                'tire_management': 90,
                'fuel_strategy': 85,
                'ers_mode': 50,
                'overtake_aggression': 30,
                'defense_intensity': 70
            }
        ]


# ==========================================
# DECISION POINT DETECTOR
# ==========================================

def check_decision_point(
    current_state: RaceState,
    handled_events: set
) -> str:
    """
    Check if game should pause for player decision.

    Args:
        current_state: Current race state
        handled_events: Set of already-handled event types

    Returns:
        Event type string if decision needed, None otherwise

    Example:
        >>> state = RaceState(lap=15, battery_soc=45, rain=True, ...)
        >>> handled = set()
        >>> event = check_decision_point(state, handled)
        >>> print(event)  # 'RAIN_START'
    """

    # Rain just started
    if current_state.rain and 'RAIN_START' not in handled_events:
        return 'RAIN_START'

    # Safety car deployed
    if current_state.safety_car and 'SAFETY_CAR' not in handled_events:
        return 'SAFETY_CAR'

    # Battery critically low
    if current_state.battery_soc < 15 and 'BATTERY_LOW' not in handled_events:
        return 'BATTERY_LOW'

    # Tires degraded
    if current_state.tire_life < 25 and 'TIRE_CRITICAL' not in handled_events:
        return 'TIRE_CRITICAL'

    # Rival close behind (attack opportunity)
    if current_state.gap_ahead < 1.0 and current_state.gap_ahead > 0 and 'OVERTAKE_OPPORTUNITY' not in handled_events:
        return 'OVERTAKE_OPPORTUNITY'

    # No decision needed
    return None
