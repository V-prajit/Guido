"""
Strategy Gym 2026 - 2024 Calibrated Physics Module

This module implements realistic F1 physics calibrated from 2024 Bahrain GP data.
It provides the foundation for 2026 extrapolation with 6 strategic control variables.

Physics calibrated from:
- 2024 Bahrain GP (57 laps)
- Real tire degradation rates (SOFT: 0.01, HARD: 0.022)
- Real fuel consumption (1.8 kg/lap base)
- Real lap times (95-98s range)
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any


@dataclass
class AgentDecision:
    """
    6 strategic variables controlled by each agent per lap.

    These represent the key decisions drivers make during a race:
    - Energy management (when to deploy battery)
    - Tire preservation (how hard to push)
    - Fuel strategy (lean vs rich mixture)
    - ERS mode (harvest vs deploy)
    - Overtaking aggression (risk vs reward)
    - Defensive intensity (when ahead)
    """
    energy_deployment: float    # 0-100% - How much battery to use this lap
    tire_management: float      # 0-100% - 0=push hard, 100=conserve tires
    fuel_strategy: float        # 0-100% - 0=lean, 50=balanced, 100=rich
    ers_mode: float            # 0-100% - 0=harvest, 50=auto, 100=deploy
    overtake_aggression: float  # 0-100% - How hard to attack when behind
    defense_intensity: float    # 0-100% - How hard to defend when ahead


@dataclass
class RaceState:
    """
    Current state of the race for an agent.

    Represents all information an agent needs to make strategic decisions.
    """
    lap: int                    # Current lap (1-57)
    battery_soc: float         # Battery state of charge (0-100%)
    position: int              # Current race position
    tire_age: int              # Laps on current tires
    tire_life: float           # Tire condition (0-100%)
    fuel_remaining: float      # Fuel in kg
    boost_used: int            # Manual boosts used (0-2)


def load_baseline() -> Dict[str, Any]:
    """
    Load 2024 Bahrain GP baseline physics parameters.

    Returns:
        dict: Physics parameters including:
            - tire_compounds: SOFT and HARD tire characteristics
            - fuel_effect: Fuel weight penalty and consumption
            - ers_deployment: Energy deployment characteristics
            - track_characteristics: Base lap time and conditions
            - race_info: Track name, date, lap count

    Example:
        >>> baseline = load_baseline()
        >>> print(baseline['track_characteristics']['base_lap_time'])
        96.8
    """
    baseline_path = Path(__file__).parent.parent / 'data' / 'baseline_2024.json'
    with open(baseline_path, 'r') as f:
        return json.load(f)


def calculate_lap_time(
    decision: AgentDecision,
    state: RaceState,
    baseline: Dict[str, Any],
    tire_compound: str = 'HARD'
) -> float:
    """
    Calculate realistic lap time based on 2024 Bahrain GP physics.

    Physics model:
    - Base time from tire compound (SOFT: 98.4s, HARD: 96.66s)
    - Tire degradation increases lap time over stint
    - Fuel weight penalty: heavier = slower
    - Energy deployment bonus: more deployment = faster
    - Fuel strategy effect: lean/balanced/rich trade-offs
    - Battery low penalty: SOC < 20% causes significant slowdown

    Args:
        decision: Agent's strategic decisions for this lap
        state: Current race state
        baseline: Physics parameters from baseline_2024.json
        tire_compound: 'SOFT' or 'HARD' (default: 'HARD')

    Returns:
        float: Lap time in seconds

    Example:
        >>> decision = AgentDecision(75, 60, 50, 70, 80, 70)
        >>> state = RaceState(10, 85.0, 3, 10, 85.0, 80.0, 0)
        >>> baseline = load_baseline()
        >>> lap_time = calculate_lap_time(decision, state, baseline)
        >>> print(f"{lap_time:.2f}s")
    """
    # Start with tire compound base time
    tire_data = baseline['tire_compounds'][tire_compound]
    base_time = tire_data['base_time']
    deg_rate = tire_data['deg_rate']

    lap_time = base_time

    # 1. Tire degradation effect
    # Higher tire_management = less degradation accumulation
    # Lower tire_management = more degradation penalty
    degradation_factor = 2.0 - (decision.tire_management / 100.0)
    tire_degradation_penalty = state.tire_age * deg_rate * degradation_factor
    lap_time += tire_degradation_penalty

    # Extra penalty if tire_life is very low
    if state.tire_life < 30:
        lap_time += (30 - state.tire_life) * 0.05

    # 2. Fuel weight effect
    # NOTE: Base lap time already accounts for average fuel load (55kg mid-race)
    # Only apply penalty/benefit for deviation from average
    avg_fuel = 55.0
    fuel_effect = baseline['fuel_effect']['penalty_per_kg']
    lap_time += (state.fuel_remaining - avg_fuel) * fuel_effect

    # 3. Energy deployment bonus
    # More deployment = faster lap (calibrated to 2024 MGU-K: 120kW)
    # At 30% deployment: ~0.9s faster (typical for efficient drivers)
    # At 100% deployment: ~3.0s faster (maximum attack mode)
    energy_bonus = decision.energy_deployment * 0.03
    lap_time -= energy_bonus

    # 4. Fuel strategy effect
    # Lean (0-40): Slower but saves fuel (+0.3s penalty)
    # Balanced (40-60): No penalty
    # Rich (60-100): Faster but burns fuel (-0.2s bonus)
    if decision.fuel_strategy < 40:
        lap_time += 0.3  # Lean mixture penalty
    elif decision.fuel_strategy > 60:
        lap_time -= 0.2  # Rich mixture bonus

    # 5. Tire push penalty
    # Pushing hard (tire_management < 20) causes extra wear and slight time loss
    if decision.tire_management < 20:
        lap_time += 0.15

    # 6. Battery low penalty
    # Critical penalty when battery is low (< 20%)
    if state.battery_soc < 20:
        lap_time += (20 - state.battery_soc) * 0.02

    return lap_time


def update_tire_condition(
    decision: AgentDecision,
    state: RaceState,
    baseline: Dict[str, Any],
    tire_compound: str = 'HARD'
) -> float:
    """
    Update tire condition based on management strategy.

    Tire degradation model:
    - SOFT: 2.0% per lap base, HARD: 1.5% per lap base
    - Modified by tire_management (higher = more care):
        - High management (>70): Conserve tires (×0.7)
        - Low management (<40): Push hard (×1.5)
        - Balanced (40-70): Normal degradation (×1.0)

    Args:
        decision: Agent's strategic decisions
        state: Current race state
        baseline: Physics parameters
        tire_compound: 'SOFT' or 'HARD'

    Returns:
        float: New tire life percentage (0-100)

    Example:
        >>> decision = AgentDecision(75, 85, 50, 70, 80, 70)  # Pushing hard
        >>> state = RaceState(10, 85.0, 3, 10, 85.0, 80.0, 0)
        >>> baseline = load_baseline()
        >>> new_life = update_tire_condition(decision, state, baseline)
        >>> print(f"Tire life: {new_life:.1f}%")
    """
    # Base degradation per lap (percent)
    # SOFT tires: 2.0% per lap (can last ~50 laps)
    # HARD tires: 1.5% per lap (can last ~65 laps)
    if tire_compound == 'SOFT':
        base_degradation = 2.0
    else:  # HARD
        base_degradation = 1.5

    # Modify by tire management strategy
    # Higher tire_management value = MORE tire care = LESS degradation
    # This matches how real F1 drivers "manage" their tires
    if decision.tire_management > 70:
        # High tire management = conserving tires
        management_multiplier = 0.7
    elif decision.tire_management < 40:
        # Low tire management = pushing hard
        management_multiplier = 1.5
    else:
        # Balanced approach
        management_multiplier = 1.0

    # Calculate total degradation (no compound_factor multiplication bug)
    total_degradation = base_degradation * management_multiplier

    # Update tire life
    new_tire_life = state.tire_life - total_degradation

    # Clamp to valid range
    return max(0.0, min(100.0, new_tire_life))


def update_fuel(
    decision: AgentDecision,
    state: RaceState,
    baseline: Dict[str, Any]
) -> float:
    """
    Update fuel remaining based on fuel strategy.

    Fuel consumption model:
    - Lean (0-40): 1.5 kg/lap (saves fuel)
    - Balanced (40-60): 1.8 kg/lap (baseline)
    - Rich (60-100): 2.2 kg/lap (burns more fuel)

    Args:
        decision: Agent's strategic decisions
        state: Current race state
        baseline: Physics parameters

    Returns:
        float: Remaining fuel in kg

    Example:
        >>> decision = AgentDecision(75, 60, 80, 70, 80, 70)  # Rich mixture
        >>> state = RaceState(10, 85.0, 3, 10, 85.0, 80.0, 0)
        >>> baseline = load_baseline()
        >>> new_fuel = update_fuel(decision, state, baseline)
        >>> print(f"Fuel remaining: {new_fuel:.1f}kg")
    """
    # Determine consumption based on fuel strategy
    if decision.fuel_strategy < 40:
        # Lean mixture - save fuel
        consumption = 1.5
    elif decision.fuel_strategy < 60:
        # Balanced - baseline consumption
        consumption = baseline['fuel_effect']['consumption_per_lap']
    else:
        # Rich mixture - burn more fuel
        consumption = 2.2

    # Update fuel remaining
    new_fuel = state.fuel_remaining - consumption

    # Clamp to zero minimum (can't have negative fuel)
    return max(0.0, new_fuel)


def update_battery(
    decision: AgentDecision,
    state: RaceState,
    baseline: Dict[str, Any]
) -> float:
    """
    Update battery SOC based on deployment and harvesting.

    Battery dynamics (2024 regulations):
    - Deployment drain: 0.02% per % of energy_deployment
    - Harvest gain: Based on ERS mode
        - ers_mode=0 (full harvest): +1.5% per lap
        - ers_mode=50 (balanced): +0.75% per lap
        - ers_mode=100 (full deploy): +0% per lap

    Args:
        decision: Agent's strategic decisions
        state: Current race state
        baseline: Physics parameters

    Returns:
        float: New battery SOC (0-100%)

    Example:
        >>> decision = AgentDecision(75, 60, 50, 30, 80, 70)  # Deploy + harvest
        >>> state = RaceState(10, 85.0, 3, 10, 85.0, 80.0, 0)
        >>> baseline = load_baseline()
        >>> new_soc = update_battery(decision, state, baseline)
        >>> print(f"Battery: {new_soc:.1f}%")
    """
    # Deployment drain (2024 spec: 120kW MGU-K)
    drain = decision.energy_deployment * 0.02

    # Harvest gain
    # Lower ers_mode = more harvesting
    # Higher ers_mode = more deployment (less harvesting)
    charge = (100 - decision.ers_mode) * 0.015

    # Update battery SOC
    new_soc = state.battery_soc - drain + charge

    # Clamp to valid range [0, 100]
    return max(0.0, min(100.0, new_soc))


def calculate_overtake_probability(
    attacker_decision: AgentDecision,
    defender_decision: AgentDecision,
    gap: float,
    baseline: Dict[str, Any]
) -> float:
    """
    Calculate probability of successful overtake.

    Overtake model:
    - Base probability from gap distance:
        - gap < 0.3s: 0.6 base (very close)
        - gap 0.3-0.5s: 0.4 base (close)
        - gap 0.5-1.0s: 0.2 base (medium)
        - gap > 1.0s: 0.05 base (difficult)
    - Modified by overtake_aggression: +0.3% per % aggression
    - Modified by defense_intensity: -0.2% per % defense

    Args:
        attacker_decision: Attacking agent's decisions
        defender_decision: Defending agent's decisions
        gap: Time gap in seconds
        baseline: Physics parameters

    Returns:
        float: Overtake probability (0.0-1.0)

    Example:
        >>> attacker = AgentDecision(80, 60, 50, 70, 90, 70)  # Aggressive
        >>> defender = AgentDecision(75, 60, 50, 70, 80, 85)  # Defensive
        >>> baseline = load_baseline()
        >>> prob = calculate_overtake_probability(attacker, defender, 0.4, baseline)
        >>> print(f"Overtake probability: {prob*100:.1f}%")
    """
    # Base probability from gap
    if gap < 0.3:
        base_prob = 0.6  # Very close - high chance
    elif gap < 0.5:
        base_prob = 0.4  # Close - medium chance
    elif gap < 1.0:
        base_prob = 0.2  # Medium gap - low chance
    else:
        base_prob = 0.05  # Large gap - very difficult

    # Attacker's aggression bonus
    aggression_bonus = attacker_decision.overtake_aggression * 0.003

    # Defender's defensive penalty (reduces attacker's chance)
    defense_penalty = defender_decision.defense_intensity * 0.002

    # Calculate final probability
    probability = base_prob + aggression_bonus - defense_penalty

    # Clamp to valid probability range [0.0, 1.0]
    return max(0.0, min(1.0, probability))


# Export all public functions and classes
__all__ = [
    'AgentDecision',
    'RaceState',
    'load_baseline',
    'calculate_lap_time',
    'update_tire_condition',
    'update_fuel',
    'update_battery',
    'calculate_overtake_probability'
]
