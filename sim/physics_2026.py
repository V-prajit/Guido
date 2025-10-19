"""
Strategy Gym 2026 - 2026 Extrapolated Physics Module

This module extrapolates 2024 physics to 2026 F1 regulations with 3x electric power.

KEY CHANGES IN 2026:
- MGU-K power: 120kW → 350kW (2.92x increase, rounded to 3x)
- Battery capacity: 4MJ (unchanged)
- Result: 3x more powerful BUT drains 3x faster
- ICE/Electric split: 50/50 (from 80/20 in 2024)

This creates a fundamentally different strategic landscape where energy management
becomes the dominant factor in race outcomes.
"""

from sim.physics_2024 import (
    AgentDecision,
    RaceState,
    load_baseline,
    update_tire_condition,
    update_fuel,
    calculate_overtake_probability
)
from typing import Dict, Any


# Re-export unchanged functions and classes
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


def calculate_lap_time(
    decision: AgentDecision,
    state: RaceState,
    baseline: Dict[str, Any],
    tire_compound: str = 'HARD',
    use_2026_rules: bool = True,
    track_type: str = 'balanced',
    temperature: float = 25.0
) -> float:
    """
    Calculate lap time with optional 2026 rules and scenario-specific effects.

    2026 CHANGES:
    - Energy deployment effect: 3x stronger (0.012 → 0.036 seconds per %)
    - At 100% deployment: 3.6s faster per lap (vs 1.2s in 2024)
    - Strategic impact: Energy becomes dominant variable

    TRACK TYPE EFFECTS (creates strategic diversity):
    - 'power': Energy deployment 1.3x more effective (Monza, Baku)
    - 'technical': Tire management 1.3x more important (Monaco, Singapore)
    - 'balanced': Neutral multipliers (default)

    TEMPERATURE EFFECTS:
    - Hot (>30°C): +30% tire degradation
    - Cold (<22°C): -20% tire degradation
    - Normal (22-30°C): baseline degradation

    Args:
        decision: Agent's strategic decisions for this lap
        state: Current race state
        baseline: Physics parameters from baseline_2024.json
        tire_compound: 'SOFT' or 'HARD' (default: 'HARD')
        use_2026_rules: If True, apply 3x electric power boost (default: True)
        track_type: 'power' | 'technical' | 'balanced' (default: 'balanced')
        temperature: Ambient temperature in Celsius (default: 25.0)

    Returns:
        float: Lap time in seconds

    Example:
        >>> decision = AgentDecision(75, 60, 50, 70, 80, 70)
        >>> state = RaceState(10, 85.0, 3, 10, 85.0, 80.0, 0)
        >>> baseline = load_baseline()
        >>> # Power track favors high energy deployment
        >>> lap_power = calculate_lap_time(decision, state, baseline, track_type='power')
        >>> # Technical track favors high tire management
        >>> lap_tech = calculate_lap_time(decision, state, baseline, track_type='technical')
    """
    # Start with tire compound base time
    tire_data = baseline['tire_compounds'][tire_compound]
    base_time = tire_data['base_time']
    deg_rate = tire_data['deg_rate']

    lap_time = base_time

    # Track type multipliers (creates scenario-dependent optimal strategies)
    energy_track_multiplier = 1.0
    tire_track_multiplier = 1.0

    if track_type == 'power':
        # Power tracks (Monza, Baku): Long straights favor energy deployment
        # EXTREME multipliers to create clear track-specific winners
        energy_track_multiplier = 2.0  # Double energy effectiveness
        tire_track_multiplier = 0.5    # Tires half as important
    elif track_type == 'technical':
        # Technical tracks (Monaco, Singapore): Tight corners favor tire management
        energy_track_multiplier = 0.5  # Energy half as effective
        tire_track_multiplier = 2.0    # Double tire importance
    # 'balanced' uses 1.0 for both (no change)

    # Temperature-based tire degradation multiplier
    temp_multiplier = 1.0
    if temperature > 30:
        temp_multiplier = 1.5  # Hot: +50% tire degradation (more punishing)
    elif temperature < 22:
        temp_multiplier = 0.7  # Cold: -30% tire degradation (more forgiving)

    # 1. Tire degradation effect (ENHANCED with track type and temperature)
    degradation_factor = 2.0 - (decision.tire_management / 100.0)
    # Apply track type multiplier to tire importance
    tire_degradation_penalty = state.tire_age * deg_rate * degradation_factor * tire_track_multiplier * temp_multiplier
    lap_time += tire_degradation_penalty

    # Extra penalty if tire_life is very low (also affected by temperature)
    if state.tire_life < 30:
        lap_time += (30 - state.tire_life) * 0.05 * temp_multiplier

    # 2. Fuel weight effect (UNCHANGED from 2024)
    # NOTE: Base lap time already accounts for average fuel load (55kg mid-race)
    # Only apply penalty/benefit for deviation from average
    avg_fuel = 55.0
    fuel_effect = baseline['fuel_effect']['penalty_per_kg']
    lap_time += (state.fuel_remaining - avg_fuel) * fuel_effect

    # 3. Energy deployment bonus (ENHANCED FOR 2026 with track type and diminishing returns)
    # 2024: 120kW MGU-K → 0.03s per % (at 30% deploy = 0.9s faster)
    # 2026: 350kW MGU-K → 0.09s per % (3x multiplier, at 30% deploy = 2.7s faster)
    energy_multiplier = 3.0 if use_2026_rules else 1.0

    # Apply diminishing returns for very high energy deployment (>80%)
    # This prevents single "max everything" dominant strategy
    effective_energy = decision.energy_deployment
    if effective_energy > 80:
        # Energy above 80% is only 70% as effective
        effective_energy = 80 + (effective_energy - 80) * 0.7

    # Apply track type multiplier to energy effectiveness
    energy_bonus = effective_energy * 0.03 * energy_multiplier * energy_track_multiplier
    lap_time -= energy_bonus

    # ADDITIONAL: Track-specific strategic bonuses/penalties
    # This creates clear track-type winners by rewarding specialized strategies
    if track_type == 'power':
        # Power tracks: Bonus for high energy, penalty for low energy
        if decision.energy_deployment > 75:
            lap_time -= 2.0  # 2s bonus for energy specialists on power tracks
        elif decision.energy_deployment < 50:
            lap_time += 2.5  # 2.5s penalty for low energy on power tracks
        # Penalty for being too balanced (high both energy AND tire)
        if decision.energy_deployment > 75 and decision.tire_management > 75:
            lap_time += 2.5  # Strong penalty to force specialization
    elif track_type == 'technical':
        # Technical tracks: Bonus for high tire management, penalty for low
        if decision.tire_management > 85:
            lap_time -= 2.0  # 2s bonus for tire specialists on technical tracks
        elif decision.tire_management < 60:
            lap_time += 2.5  # 2.5s penalty for low tire management on technical tracks
        # Penalty for being too balanced
        if decision.tire_management > 85 and decision.energy_deployment > 65:
            lap_time += 2.5  # Strong penalty to force specialization

    # 4. Fuel strategy effect (UNCHANGED from 2024)
    if decision.fuel_strategy < 40:
        lap_time += 0.3  # Lean mixture penalty
    elif decision.fuel_strategy > 60:
        lap_time -= 0.2  # Rich mixture bonus

    # 5. Tire push penalty (UNCHANGED from 2024)
    # Pushing hard (low tire management) causes extra wear and slight time loss
    if decision.tire_management < 20:
        lap_time += 0.15

    # 6. Battery low penalty (INCREASED to discourage running out completely)
    # Old: 0.02s per % below 20% (max +0.4s at 0%)
    # New: 0.05s per % below 20% (max +1.0s at 0%)
    # This makes energy conservation more strategic
    if state.battery_soc < 20:
        lap_time += (20 - state.battery_soc) * 0.05

    return lap_time


def update_battery(
    decision: AgentDecision,
    state: RaceState,
    baseline: Dict[str, Any],
    use_2026_rules: bool = True
) -> float:
    """
    Update battery SOC with optional 2026 rules.

    2026 CHANGES:
    - Deployment drain: 3x faster (0.02 → 0.06 per %)
    - Battery capacity: UNCHANGED (4MJ)
    - Result: Same energy storage, but depletes 3x faster when deployed

    Harvest rate is UNCHANGED:
    - Same MGU-H (Motor Generator Unit - Heat) in 2026
    - ERS harvesting efficiency remains identical

    This creates critical strategic trade-off:
    - More power available per lap
    - But battery depletes much faster
    - Energy management becomes race-defining

    Args:
        decision: Agent's strategic decisions
        state: Current race state
        baseline: Physics parameters
        use_2026_rules: If True, apply 3x drain rate (default: True)

    Returns:
        float: New battery SOC (0-100%)

    Example:
        >>> decision = AgentDecision(100, 60, 50, 30, 80, 70)  # Max deployment
        >>> state = RaceState(10, 85.0, 3, 10, 85.0, 80.0, 0)
        >>> baseline = load_baseline()
        >>> soc_2024 = update_battery(decision, state, baseline, use_2026_rules=False)
        >>> soc_2026 = update_battery(decision, state, baseline, use_2026_rules=True)
        >>> print(f"2024 drain: {85.0 - soc_2024:.1f}%")
        >>> print(f"2026 drain: {85.0 - soc_2026:.1f}% (3x faster)")
    """
    # Deployment drain (CHANGED FOR 2026)
    # 2024: 0.02% per % of deployment
    # 2026: 0.06% per % of deployment (3x drain rate)
    drain_multiplier = 3.0 if use_2026_rules else 1.0
    drain = decision.energy_deployment * 0.02 * drain_multiplier

    # Harvest gain (UNCHANGED from 2024)
    # MGU-H harvesting efficiency is identical in 2026
    # Lower ers_mode = more harvesting
    charge = (100 - decision.ers_mode) * 0.015

    # Update battery SOC
    new_soc = state.battery_soc - drain + charge

    # Clamp to valid range [0, 100]
    return max(0.0, min(100.0, new_soc))


# Note: The following functions are identical in 2024 and 2026,
# so we simply re-export them from physics_2024:
#
# - update_tire_condition: Tire physics unchanged
# - update_fuel: Fuel consumption unchanged
# - calculate_overtake_probability: Overtaking dynamics unchanged
# - load_baseline: Same baseline data source
#
# They are already exported via the __all__ list at the top of this module.
