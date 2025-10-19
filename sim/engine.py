"""
Strategy Gym 2026 - Core Simulation Engine V2

This module implements the realistic F1 physics engine for 2026 regulations.
It uses the 6-variable agent decision system and realistic physics from physics_2026.py.

Key Features:
- Realistic 2024 calibrated physics with 2026 extrapolation
- 6-variable strategic decision system
- Tire life and fuel consumption tracking
- Multiprocessing-compatible (picklable, pure functions)
- Enhanced DataFrame output with all decision variables
"""

from dataclasses import dataclass
import pandas as pd
from typing import List, Dict, Any

# Import from new physics and agents
from sim.physics_2026 import (
    load_baseline,
    calculate_lap_time,
    update_battery,
    update_tire_condition,
    update_fuel,
    calculate_overtake_probability,
    AgentDecision,
    RaceState
)

# Load baseline parameters once at module level for performance
BASELINE = load_baseline()


def simulate_race(scenario: dict, agents: list, use_2026_rules: bool = True) -> pd.DataFrame:
    """
    Simulate a complete F1 race with realistic physics.

    This is the main entry point for race simulation. It runs all agents through
    the specified scenario and returns detailed lap-by-lap results.

    Args:
        scenario: Race parameters (num_laps, track_type, rain_lap, etc.)
            Required keys:
                - num_laps (int): Number of laps in the race
            Optional keys:
                - rain_lap (int or None): Lap when rain starts
                - safety_car_lap (int or None): Lap when safety car deploys
                - track_type (str): 'power' | 'technical' | 'balanced'
                - temperature (float): Ambient temperature in Celsius
        agents: List of AgentV2 instances
        use_2026_rules: If True, use 2026 physics (3x electric power, 3x drain)

    Returns:
        DataFrame with columns:
        - agent (str): Agent name
        - lap (int): Lap number (1 to num_laps)
        - battery_soc (float): Battery state of charge (0-100%)
        - tire_life (float): Tire condition (0-100%)
        - fuel_remaining (float): Fuel in kg
        - lap_time (float): Lap time in seconds
        - cumulative_time (float): Total race time so far
        - final_position (int): Final race position (1-8)
        - won (bool): True if agent won the race
        - energy_deployment (float): Energy deployment decision (0-100)
        - tire_management (float): Tire management decision (0-100)
        - fuel_strategy (float): Fuel strategy decision (0-100)
        - ers_mode (float): ERS mode decision (0-100)
        - overtake_aggression (float): Overtake aggression decision (0-100)
        - defense_intensity (float): Defense intensity decision (0-100)

    Example:
        >>> from sim.agents_v2 import create_agents_v2
        >>> from sim.scenarios import generate_scenarios
        >>> scenarios = generate_scenarios(1)
        >>> agents = create_agents_v2()
        >>> df = simulate_race(scenarios[0], agents)
        >>> print(df.columns.tolist())
    """
    num_laps = scenario.get('num_laps', 57)

    # Initialize state for each agent
    # Track cumulative time separately since it's not in RaceState
    agent_cumulative_times = {agent.name: 0.0 for agent in agents}

    agent_states = {}
    for agent in agents:
        agent_states[agent.name] = RaceState(
            lap=0,
            battery_soc=100.0,           # Start with full battery
            position=0,                   # Will be determined each lap
            tire_age=0,
            tire_life=100.0,             # Start with fresh tires
            fuel_remaining=110.0,        # Start with full tank
            boost_used=0
        )

    # Track all lap results
    results = []

    # Simulate each lap
    for lap_num in range(1, num_laps + 1):
        lap_results = simulate_lap(
            lap_num,
            agents,
            agent_states,
            agent_cumulative_times,
            scenario,
            BASELINE,
            use_2026_rules
        )
        results.extend(lap_results)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Calculate final positions and winners
    df = calculate_final_positions(df, num_laps)

    return df


def simulate_lap(
    lap_num: int,
    agents: list,
    agent_states: Dict[str, RaceState],
    agent_cumulative_times: Dict[str, float],
    scenario: dict,
    baseline: Dict[str, Any],
    use_2026_rules: bool
) -> List[dict]:
    """
    Simulate one lap for all agents.

    This function handles:
    - Agent decision making
    - Lap time calculation using realistic physics
    - Battery, tire, and fuel updates
    - Special conditions (rain, safety car)
    - Position updates based on cumulative times

    Args:
        lap_num: Current lap number (1-indexed)
        agents: List of AgentV2 instances
        agent_states: Dictionary mapping agent name to RaceState
        agent_cumulative_times: Dictionary tracking cumulative race time per agent
        scenario: Scenario configuration
        baseline: Physics parameters from baseline_2024.json
        use_2026_rules: Whether to use 2026 physics

    Returns:
        List of result dictionaries, one per agent
    """
    lap_results = []

    for agent in agents:
        state = agent_states[agent.name]
        state.lap = lap_num
        state.tire_age += 1

        # Agent makes decision based on current state
        decision = agent.decide(state)

        # Calculate lap time using realistic physics
        lap_time = calculate_lap_time(decision, state, baseline, 'HARD', use_2026_rules)

        # Apply rain penalty if applicable
        if scenario.get('rain_lap') == lap_num:
            lap_time += 2.0  # Rain adds ~2 seconds

        # Apply safety car effect if applicable
        if scenario.get('safety_car_lap') == lap_num:
            lap_time = 110.0  # Fixed slow lap under safety car

        # Apply low fuel penalty (running out of fuel)
        if state.fuel_remaining <= 0:
            lap_time += 10.0  # Massive penalty for running out of fuel

        # Apply severe tire degradation penalty
        if state.tire_life < 20:
            # Severely degraded tires add time penalty
            lap_time += (20 - state.tire_life) * 0.1

        # Update state using physics functions
        state.battery_soc = update_battery(decision, state, baseline, use_2026_rules)
        state.tire_life = update_tire_condition(decision, state, baseline, 'HARD')
        state.fuel_remaining = update_fuel(decision, state, baseline)

        # Update cumulative time
        agent_cumulative_times[agent.name] += lap_time

        # Record results for this lap
        lap_results.append({
            'agent': agent.name,
            'lap': lap_num,
            'battery_soc': state.battery_soc,
            'tire_life': state.tire_life,
            'fuel_remaining': state.fuel_remaining,
            'lap_time': lap_time,
            'cumulative_time': agent_cumulative_times[agent.name],
            'energy_deployment': decision.energy_deployment,
            'tire_management': decision.tire_management,
            'fuel_strategy': decision.fuel_strategy,
            'ers_mode': decision.ers_mode,
            'overtake_aggression': decision.overtake_aggression,
            'defense_intensity': decision.defense_intensity
        })

    # Update positions based on cumulative times
    lap_results_sorted = sorted(lap_results, key=lambda x: x['cumulative_time'])
    for idx, result in enumerate(lap_results_sorted):
        agent_states[result['agent']].position = idx + 1

    return lap_results


def calculate_final_positions(df: pd.DataFrame, num_laps: int) -> pd.DataFrame:
    """
    Calculate final positions and determine winner.

    Final positions are determined by cumulative time at the end of the race.
    The agent with the lowest cumulative time wins.

    Args:
        df: DataFrame with race results
        num_laps: Total number of laps in the race

    Returns:
        DataFrame with final_position and won columns added
    """
    # Get final cumulative times (last lap)
    final_lap = df[df['lap'] == num_laps].copy()
    final_lap = final_lap.sort_values('cumulative_time')

    # Create position mapping - use enumerate to get correct position
    position_map = {}
    for position, (_, row) in enumerate(final_lap.iterrows(), start=1):
        position_map[row['agent']] = position

    # Add to DataFrame
    df['final_position'] = df['agent'].map(position_map)
    df['won'] = df['final_position'] == 1

    return df


def create_agents():
    """
    Factory function to create agents.

    For compatibility with existing runner.py code that expects this function.
    Delegates to create_agents_v2() from agents_v2.py.

    Returns:
        List of 8 AgentV2 instances:
        [VerstappenStyle, HamiltonStyle, AlonsoStyle, ElectricBlitzer,
         EnergySaver, TireWhisperer, Opportunist, AdaptiveAI]
    """
    from sim.agents_v2 import create_agents_v2
    return create_agents_v2()


# Note: RaceState is re-exported from physics_2024
# It is already defined in physics_2024.py and imported above
# We don't need to redefine it here

# Re-export for backward compatibility
__all__ = [
    'simulate_race',
    'simulate_lap',
    'calculate_final_positions',
    'create_agents',
    'RaceState'
]
