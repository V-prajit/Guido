"""
Lightweight simulation data generator for game loop.

HACKATHON MODE: Generates realistic-looking simulation results
without running full physics. Fast enough for real-time decisions.

For production: Replace with actual physics simulations.
"""

import pandas as pd
import numpy as np
from typing import List, Dict


def generate_realistic_sim_results(
    current_state: dict,
    strategy_params: List[Dict],
    num_sims: int = 100
) -> pd.DataFrame:
    """
    Generate realistic-looking simulation results quickly.

    This is a FAST probabilistic model, not full physics simulation.
    Good enough for hackathon demo where speed > perfect accuracy.

    Args:
        current_state: {
            'lap': 15,
            'position': 4,
            'battery_soc': 45.0,
            'tire_life': 62.0,
            'fuel_remaining': 28.0,
            'event_type': 'RAIN_START'
        }
        strategy_params: List of 3 strategy configs
        num_sims: Number of simulations per strategy (default 100)

    Returns:
        DataFrame with 300 rows (100 per strategy × 3 strategies)

    Example:
        >>> state = {'lap': 15, 'position': 4, 'battery_soc': 45, ...}
        >>> strategies = [aggressive, balanced, conservative]
        >>> results = generate_realistic_sim_results(state, strategies)
        >>> len(results)  # 300
    """

    # Extract current state
    current_lap = current_state.get('lap', 15)
    current_pos = current_state.get('position', 4)
    current_battery = current_state.get('battery_soc', 50)
    current_tires = current_state.get('tire_life', 70)
    event_type = current_state.get('event_type', 'DECISION_POINT')

    results = []

    for strategy_id, strategy in enumerate(strategy_params):
        # Calculate base win probability from strategy
        base_win_rate = _calculate_win_probability(
            strategy,
            current_state,
            event_type
        )

        # Generate 100 simulation results
        for sim_run in range(num_sims):
            np.random.seed(strategy_id * 1000 + sim_run)

            # Probabilistic outcome
            won = np.random.random() < base_win_rate

            if won:
                final_position = 1
            else:
                # Position distribution based on strategy aggressiveness
                aggression_factor = (
                    strategy['energy_deployment'] +
                    strategy['overtake_aggression']
                ) / 200

                if aggression_factor > 0.75:
                    # Aggressive: bimodal (podium or poor)
                    final_position = np.random.choice(
                        [2, 3, 6, 7],
                        p=[0.4, 0.3, 0.2, 0.1]
                    )
                elif aggression_factor < 0.4:
                    # Conservative: tends to mid-pack
                    final_position = np.random.choice(
                        [4, 5, 6, 7],
                        p=[0.2, 0.3, 0.3, 0.2]
                    )
                else:
                    # Balanced: consistent podium/points
                    final_position = np.random.choice(
                        [2, 3, 4, 5],
                        p=[0.35, 0.35, 0.2, 0.1]
                    )

            # Simulate final resources
            final_battery = _simulate_final_battery(
                current_battery,
                strategy,
                current_lap
            )

            final_tires = _simulate_final_tires(
                current_tires,
                strategy,
                current_lap
            )

            final_fuel = max(0, current_state.get('fuel_remaining', 30) -
                           (57 - current_lap) * 0.5)

            results.append({
                'strategy_id': strategy_id,
                'sim_run_id': sim_run,
                'final_position': final_position,
                'won': won,
                'battery_soc': final_battery,
                'tire_life': final_tires,
                'fuel_remaining': final_fuel
            })

    return pd.DataFrame(results)


def _calculate_win_probability(
    strategy: Dict,
    current_state: dict,
    event_type: str
) -> float:
    """Calculate base win probability for a strategy."""

    current_pos = current_state.get('position', 5)

    # Base probability decreases with worse starting position
    position_factor = {
        1: 0.7, 2: 0.5, 3: 0.4, 4: 0.3,
        5: 0.2, 6: 0.15, 7: 0.1, 8: 0.05
    }.get(current_pos, 0.3)

    # Strategy effectiveness
    energy = strategy['energy_deployment']
    tire_mgmt = strategy['tire_management']
    aggression = strategy['overtake_aggression']

    # Context-specific modifiers
    if event_type == 'RAIN_START':
        # Rain favors balanced energy + good tire management
        strategy_score = (
            0.3 * (energy / 100) +
            0.4 * (tire_mgmt / 100) +
            0.3 * (aggression / 100)
        )
        # Penalize extremes
        if energy > 90 or energy < 30:
            strategy_score *= 0.7

    elif event_type == 'TIRE_CRITICAL':
        # Tire critical favors conservation
        strategy_score = (
            0.2 * (energy / 100) +
            0.6 * (tire_mgmt / 100) +
            0.2 * (aggression / 100)
        )

    elif event_type == 'BATTERY_LOW':
        # Battery low favors recovery
        ers = strategy.get('ers_mode', 50)
        strategy_score = (
            0.3 * (1 - energy / 100) +  # Lower deployment better
            0.5 * (ers / 100) +          # Higher recovery better
            0.2 * (tire_mgmt / 100)
        )

    else:
        # Default balanced scoring
        strategy_score = (
            0.35 * (energy / 100) +
            0.35 * (tire_mgmt / 100) +
            0.30 * (aggression / 100)
        )

    # Combine factors
    win_prob = position_factor * strategy_score

    # Add variance
    win_prob = np.clip(win_prob, 0.05, 0.50)

    return win_prob


def _simulate_final_battery(
    current_battery: float,
    strategy: Dict,
    current_lap: int
) -> float:
    """Estimate final battery based on strategy."""

    remaining_laps = 57 - current_lap

    energy_deploy = strategy['energy_deployment']
    ers_mode = strategy.get('ers_mode', 50)

    # Drain per lap
    drain_per_lap = energy_deploy / 100 * 0.8

    # Recovery per lap
    recovery_per_lap = ers_mode / 100 * 0.6

    # Net change
    net_change_per_lap = recovery_per_lap - drain_per_lap

    # Final battery estimate
    final_battery = current_battery + (net_change_per_lap * remaining_laps)

    # Add noise
    final_battery += np.random.normal(0, 5)

    return np.clip(final_battery, 0, 100)


def _simulate_final_tires(
    current_tires: float,
    strategy: Dict,
    current_lap: int
) -> float:
    """Estimate final tire life based on strategy."""

    remaining_laps = 57 - current_lap

    tire_mgmt = strategy['tire_management']

    # Wear per lap (higher management = less wear)
    wear_per_lap = (100 - tire_mgmt) / 100 * 1.5

    # Final tires
    final_tires = current_tires - (wear_per_lap * remaining_laps)

    # Add noise
    final_tires += np.random.normal(0, 3)

    return np.clip(final_tires, 0, 100)
