"""
Strategy Gym 2026 - Core Simulation Engine

This module implements the simplified F1 power unit physics model for 2026 regulations.
It provides the core simulation engine that runs multi-agent races across diverse scenarios.
"""

from dataclasses import dataclass
import pandas as pd


@dataclass
class RaceState:
    """
    Represents the state of a car at a given point in the race.

    Attributes:
        lap: Current lap number (1-57 typically)
        battery_soc: Battery state of charge (0-100%)
        position: Current race position (1-based)
        tire_age: Number of laps on current tires
        boost_used: Number of boost uses already consumed (0-2)
    """
    lap: int
    battery_soc: float
    position: int
    tire_age: int
    boost_used: int


class Agent:
    """
    Base class for all racing agents.

    Each agent implements a specific energy deployment strategy by overriding
    the decide() method to return deployment decisions based on race state.
    """

    def __init__(self, name: str, params: dict):
        """
        Initialize agent.

        Args:
            name: Agent identifier
            params: Dictionary of agent-specific parameters
        """
        self.name = name
        self.params = params

    def decide(self, state: RaceState) -> dict:
        """
        Make deployment decision based on current race state.

        Args:
            state: Current RaceState

        Returns:
            Dictionary with keys:
                - deploy_straight: 0-100 (% electric power on straights)
                - deploy_corner: 0-100 (% electric power on corner exits)
                - harvest: 0-100 (% energy recovery intensity)
                - use_boost: bool (manual override, 2 uses per race)
        """
        raise NotImplementedError("Subclasses must implement decide()")


def simulate_lap(state: RaceState, decision: dict, scenario: dict) -> tuple[RaceState, float]:
    """
    Simulate a single lap based on agent decision and scenario conditions.

    Uses simplified F1 physics model:
    - Base lap time: 90.0 seconds
    - Deployment bonus: -0.003s per % on straights, -0.002s per % on corners
    - Harvesting penalty: +0.0015s per %
    - Low battery penalty: if SOC < 20%, add (20 - SOC) * 0.02s
    - Rain penalty: +2.0s if rain on this lap

    Battery dynamics:
    - Drain: (deploy_straight * 0.02) + (deploy_corner * 0.015)
    - Charge: harvest * 0.025
    - SOC clamped to [0, 100]

    Args:
        state: Current RaceState
        decision: Agent's deployment decision dict
        scenario: Scenario configuration dict

    Returns:
        Tuple of (new_RaceState, lap_time_seconds)
    """
    # Start with base lap time
    base_time = 90.0
    lap_time = base_time

    # Extract decision values
    deploy_straight = decision.get('deploy_straight', 0)
    deploy_corner = decision.get('deploy_corner', 0)
    harvest = decision.get('harvest', 0)
    use_boost = decision.get('use_boost', False)

    # Apply deployment bonuses (faster lap time)
    lap_time -= deploy_straight * 0.003  # max -0.3s
    lap_time -= deploy_corner * 0.002    # max -0.2s

    # Apply harvesting penalty (slower to recover energy)
    lap_time += harvest * 0.0015  # max +0.15s

    # Apply low battery penalty
    if state.battery_soc < 20:
        lap_time += (20 - state.battery_soc) * 0.02

    # Apply rain penalty if this is the rain lap
    if scenario.get('rain_lap') == state.lap:
        lap_time += 2.0

    # Calculate battery drain and charge
    drain = (deploy_straight * 0.02) + (deploy_corner * 0.015)
    charge = harvest * 0.025
    new_soc = state.battery_soc - drain + charge

    # Clamp battery SOC to valid range [0, 100]
    new_soc = max(0.0, min(100.0, new_soc))

    # Update boost usage counter
    new_boost_used = state.boost_used + (1 if use_boost and state.boost_used < 2 else 0)

    # Create new state for next lap
    new_state = RaceState(
        lap=state.lap + 1,
        battery_soc=new_soc,
        position=state.position,  # Position changes handled at race level
        tire_age=state.tire_age + 1,
        boost_used=new_boost_used
    )

    return new_state, lap_time


def simulate_race(scenario: dict, agents: list) -> pd.DataFrame:
    """
    Simulate a complete race with multiple agents.

    Each agent races independently through all laps, making decisions based
    on their current state. The agent with the lowest total time wins.

    Args:
        scenario: Scenario configuration dict with keys:
            - num_laps: Number of laps in the race (default 57)
            - rain_lap: Lap number when rain starts (optional)
            - safety_car_lap: Lap number when safety car deploys (optional)
            - track_type: 'power' | 'technical' | 'balanced' (optional)
            - temperature: Track temperature in Celsius (optional)
        agents: List of Agent instances

    Returns:
        pandas DataFrame with columns:
            - agent: Agent name
            - lap: Lap number
            - battery_soc: Battery state of charge at end of lap
            - lap_time: Time for this lap in seconds
            - cumulative_time: Total race time so far
            - final_position: Final race position (1-based)
            - won: 1 if this agent won, 0 otherwise
    """
    num_laps = scenario.get('num_laps', 57)
    results = []

    # Track cumulative time for each agent
    agent_times = {agent.name: 0.0 for agent in agents}

    # Initialize starting state for each agent
    states = {
        agent.name: RaceState(
            lap=1,
            battery_soc=100.0,
            position=i + 1,
            tire_age=0,
            boost_used=0
        )
        for i, agent in enumerate(agents)
    }

    # Simulate each lap for all agents
    for lap in range(1, num_laps + 1):
        for agent in agents:
            state = states[agent.name]

            # Agent makes decision based on current state
            decision = agent.decide(state)

            # Simulate this lap
            new_state, lap_time = simulate_lap(state, decision, scenario)

            # Update cumulative time
            agent_times[agent.name] += lap_time

            # Update state for next lap
            states[agent.name] = new_state

            # Record this lap's results
            results.append({
                'agent': agent.name,
                'lap': lap,
                'battery_soc': new_state.battery_soc,
                'lap_time': lap_time,
                'cumulative_time': agent_times[agent.name],
                'final_position': 0,  # Will be calculated after race
                'won': 0
            })

    # Create DataFrame
    df = pd.DataFrame(results)

    # Determine winner (lowest total time)
    winner_name = min(agent_times.items(), key=lambda x: x[1])[0]

    # Calculate final positions
    sorted_agents = sorted(agent_times.items(), key=lambda x: x[1])
    position_map = {name: pos + 1 for pos, (name, _) in enumerate(sorted_agents)}

    # Update DataFrame with final positions and winner
    for agent_name in agent_times.keys():
        agent_mask = df['agent'] == agent_name
        df.loc[agent_mask, 'final_position'] = position_map[agent_name]
        df.loc[agent_mask, 'won'] = 1 if agent_name == winner_name else 0

    return df
