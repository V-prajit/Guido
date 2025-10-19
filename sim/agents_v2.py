"""
Strategy Gym 2026 - Agent System V2

8 agents using 6-variable strategic decision system:
- 3 learned agents (based on real 2024 Bahrain GP data)
- 5 synthetic agents (diverse strategic approaches)

All agents use AgentDecision with 6 strategic variables:
1. energy_deployment (0-100)
2. tire_management (0-100)
3. fuel_strategy (0-100)
4. ers_mode (0-100)
5. overtake_aggression (0-100)
6. defense_intensity (0-100)
"""

from sim.physics_2024 import AgentDecision, RaceState
import json
import random
from pathlib import Path
from typing import Dict, Any


class AgentV2:
    """Base class for all agents using 6-variable decision system."""

    def __init__(self, name: str, strategy_profile: Dict[str, float]):
        self.name = name
        self.profile = strategy_profile  # Default values for 6 variables

    def decide(self, state: RaceState) -> AgentDecision:
        """
        Make strategic decision for current lap.
        Override in subclasses for specific strategies.
        """
        raise NotImplementedError

    def _add_variance(self, value: float, variance: float = 5.0) -> float:
        """Add ±variance% randomness to avoid robotic behavior."""
        return max(0, min(100, value + random.uniform(-variance, variance)))


class VerstappenStyle(AgentV2):
    """
    Learned from Max Verstappen's 2024 Bahrain GP victory.

    Characteristics:
    - Conservative energy (29.5) - manages power efficiently
    - Aggressive tire usage (100) - high variance push/conserve
    - Strong defense (100) - protects position relentlessly
    - Cautious overtaking (40) - started P1, defended rather than attacked

    Strategy:
    - Controlled energy deployment to maintain battery throughout race
    - Dynamic tire management based on stint phase
    - Excellent defensive positioning
    - Focus on track position management over risky overtakes
    """
    def __init__(self):
        # Load from learned_strategies.json
        try:
            strategies_path = Path(__file__).parent.parent / 'data' / 'learned_strategies.json'
            with open(strategies_path) as f:
                data = json.load(f)
                profile = data['verstappen_2024']
        except:
            # Fallback if file not found
            profile = {
                'energy_deployment': 29.5,
                'tire_management': 100,
                'fuel_strategy': 52.9,
                'ers_mode': 35.4,
                'overtake_aggression': 40,
                'defense_intensity': 100
            }

        super().__init__("VerstappenStyle", profile)

    def decide(self, state: RaceState) -> AgentDecision:
        # Base strategy from learned profile
        energy = self.profile['energy_deployment']
        tire = self.profile['tire_management']
        fuel = self.profile['fuel_strategy']
        ers = self.profile['ers_mode']
        overtake = self.profile['overtake_aggression']
        defense = self.profile['defense_intensity']

        # Adjust based on race state
        # Low battery → harvest more (lower ers_mode)
        if state.battery_soc < 30:
            ers = max(0, ers - 20)
            energy = max(0, energy - 10)

        # Late race with high battery → deploy more
        if state.lap > 45 and state.battery_soc > 70:
            energy = min(100, energy + 15)
            ers = min(100, ers + 15)

        # Adjust tire management based on tire life
        if state.tire_life < 40:
            tire = max(0, tire - 30)  # Conserve worn tires

        return AgentDecision(
            energy_deployment=self._add_variance(energy),
            tire_management=self._add_variance(tire),
            fuel_strategy=self._add_variance(fuel),
            ers_mode=self._add_variance(ers),
            overtake_aggression=self._add_variance(overtake),
            defense_intensity=self._add_variance(defense)
        )


class HamiltonStyle(AgentV2):
    """
    Learned from Lewis Hamilton's 2024 Bahrain GP (P7).

    Characteristics:
    - Conservative energy (27.5) - even more efficient than Verstappen
    - Aggressive tire usage (100)
    - Extremely aggressive overtaking (100) - made 8 passes
    - Strong defense (96.4)

    Strategy:
    - Energy efficiency expert
    - Aggressive in overtaking situations (race craft specialist)
    - Strong defensive abilities
    - Long stint capability
    """
    def __init__(self):
        try:
            strategies_path = Path(__file__).parent.parent / 'data' / 'learned_strategies.json'
            with open(strategies_path) as f:
                data = json.load(f)
                profile = data['hamilton_2024']
        except:
            profile = {
                'energy_deployment': 27.5,
                'tire_management': 100,
                'fuel_strategy': 51.9,
                'ers_mode': 30.9,
                'overtake_aggression': 100,
                'defense_intensity': 96.4
            }

        super().__init__("HamiltonStyle", profile)

    def decide(self, state: RaceState) -> AgentDecision:
        energy = self.profile['energy_deployment']
        tire = self.profile['tire_management']
        fuel = self.profile['fuel_strategy']
        ers = self.profile['ers_mode']
        overtake = self.profile['overtake_aggression']
        defense = self.profile['defense_intensity']

        # Increase aggression when behind (overtaking specialist)
        if state.position > 5:
            overtake = min(100, overtake + 10)
            energy = min(100, energy + 10)

        # Battery management
        if state.battery_soc < 25:
            ers = max(0, ers - 25)
            energy = max(0, energy - 15)

        # Tire preservation on long stints
        if state.tire_age > 25:
            tire = max(0, tire - 20)

        return AgentDecision(
            energy_deployment=self._add_variance(energy),
            tire_management=self._add_variance(tire),
            fuel_strategy=self._add_variance(fuel),
            ers_mode=self._add_variance(ers),
            overtake_aggression=self._add_variance(overtake),
            defense_intensity=self._add_variance(defense)
        )


class AlonsoStyle(AgentV2):
    """
    Learned from Fernando Alonso's 2024 Bahrain GP (P9).

    Characteristics:
    - Most conservative energy (25.7) - energy efficiency expert
    - Aggressive tire usage (100)
    - Very aggressive overtaking (100) - 10 passes in midfield battles
    - Strong defense (85.7)

    Strategy:
    - Master of energy management
    - Midfield specialist - aggressive in battles
    - Tire whisperer - can extend stints
    - Opportunistic overtaker
    """
    def __init__(self):
        try:
            strategies_path = Path(__file__).parent.parent / 'data' / 'learned_strategies.json'
            with open(strategies_path) as f:
                data = json.load(f)
                profile = data['alonso_2024']
        except:
            profile = {
                'energy_deployment': 25.7,
                'tire_management': 100,
                'fuel_strategy': 53.8,
                'ers_mode': 30.5,
                'overtake_aggression': 100,
                'defense_intensity': 85.7
            }

        super().__init__("AlonsoStyle", profile)

    def decide(self, state: RaceState) -> AgentDecision:
        energy = self.profile['energy_deployment']
        tire = self.profile['tire_management']
        fuel = self.profile['fuel_strategy']
        ers = self.profile['ers_mode']
        overtake = self.profile['overtake_aggression']
        defense = self.profile['defense_intensity']

        # Opportunistic energy deployment when battery is high
        if state.battery_soc > 80:
            energy = min(100, energy + 20)
        elif state.battery_soc < 30:
            ers = max(0, ers - 30)
            energy = max(0, energy - 10)

        # Midfield battle mode - extra aggressive when P5-P10
        if 5 <= state.position <= 10:
            overtake = min(100, overtake + 5)
            defense = min(100, defense + 10)

        # Tire management mastery
        if state.tire_life < 50:
            tire = max(0, tire - 25)

        return AgentDecision(
            energy_deployment=self._add_variance(energy),
            tire_management=self._add_variance(tire),
            fuel_strategy=self._add_variance(fuel),
            ers_mode=self._add_variance(ers),
            overtake_aggression=self._add_variance(overtake),
            defense_intensity=self._add_variance(defense)
        )


class ElectricBlitzer(AgentV2):
    """
    Aggressive early-race strategy.
    Deploys all battery power early for track position.
    Weakens in final laps but aims to build insurmountable gap.

    Strategy:
    - Maximum deployment early race (laps 1-20): 95%
    - Reduced mid race (laps 21-40): 70%
    - Minimal late race (laps 41+): 40% (battery depleted)
    - Push tires hard throughout
    - Rich fuel mixture for maximum performance
    """
    def __init__(self):
        profile = {
            'energy_deployment': 95,
            'tire_management': 90,
            'fuel_strategy': 85,
            'ers_mode': 95,
            'overtake_aggression': 95,
            'defense_intensity': 60
        }
        super().__init__("ElectricBlitzer", profile)

    def decide(self, state: RaceState) -> AgentDecision:
        # Ramp down deployment as race progresses
        if state.lap <= 20:
            energy_mult = 1.0
            ers_mult = 1.0
        elif state.lap <= 40:
            energy_mult = 0.7
            ers_mult = 0.7
        else:
            energy_mult = 0.4
            ers_mult = 0.5

        # If battery is critically low, switch to harvest mode
        if state.battery_soc < 15:
            ers_mult = 0.2
            energy_mult = 0.3

        return AgentDecision(
            energy_deployment=self._add_variance(self.profile['energy_deployment'] * energy_mult),
            tire_management=self._add_variance(self.profile['tire_management']),
            fuel_strategy=self._add_variance(self.profile['fuel_strategy']),
            ers_mode=self._add_variance(self.profile['ers_mode'] * ers_mult),
            overtake_aggression=self._add_variance(self.profile['overtake_aggression']),
            defense_intensity=self._add_variance(self.profile['defense_intensity'])
        )


class EnergySaver(AgentV2):
    """
    Conservative early, aggressive late strategy.
    Reverse of ElectricBlitzer.

    Strategy:
    - Early race (laps 1-20): 30% energy, heavy harvest
    - Mid race (laps 21-40): 60% energy, balanced
    - Late race (laps 41+): 90% energy, full deployment
    - Moderate tire management (60)
    - Lean fuel mixture (40)
    """
    def __init__(self):
        profile = {
            'energy_deployment': 30,
            'tire_management': 60,
            'fuel_strategy': 40,
            'ers_mode': 30,
            'overtake_aggression': 50,
            'defense_intensity': 70
        }
        super().__init__("EnergySaver", profile)

    def decide(self, state: RaceState) -> AgentDecision:
        # Progressive ramp up through race
        if state.lap <= 20:
            energy_mult = 1.0
            ers_mult = 1.0
            overtake_mult = 0.8
        elif state.lap <= 40:
            energy_mult = 2.0
            ers_mult = 1.7
            overtake_mult = 1.2
        else:
            energy_mult = 3.0
            ers_mult = 2.5
            overtake_mult = 1.5

        # Don't overdeploy if battery is low
        if state.battery_soc < 30:
            energy_mult = min(energy_mult, 1.0)
            ers_mult = min(ers_mult, 0.5)

        return AgentDecision(
            energy_deployment=self._add_variance(min(100, self.profile['energy_deployment'] * energy_mult)),
            tire_management=self._add_variance(self.profile['tire_management']),
            fuel_strategy=self._add_variance(self.profile['fuel_strategy']),
            ers_mode=self._add_variance(min(100, self.profile['ers_mode'] * ers_mult)),
            overtake_aggression=self._add_variance(min(100, self.profile['overtake_aggression'] * overtake_mult)),
            defense_intensity=self._add_variance(self.profile['defense_intensity'])
        )


class TireWhisperer(AgentV2):
    """
    Tire preservation specialist.
    Aims for minimal degradation to enable one-stop or long stints.
    Sacrifices pace for tire life.

    Strategy:
    - Very gentle tire management (35)
    - Moderate energy (60)
    - Balanced fuel (50)
    - Even more conservative when tires are old
    - Focus on consistency over speed
    """
    def __init__(self):
        profile = {
            'energy_deployment': 60,
            'tire_management': 35,
            'fuel_strategy': 50,
            'ers_mode': 50,
            'overtake_aggression': 50,
            'defense_intensity': 65
        }
        super().__init__("TireWhisperer", profile)

    def decide(self, state: RaceState) -> AgentDecision:
        # Even more conservative if tires are old or degraded
        tire_mult = 1.0
        if state.tire_age > 20:
            tire_mult = 0.7
        if state.tire_life < 50:
            tire_mult = min(tire_mult, 0.6)

        # Can be more aggressive if tires are fresh
        if state.tire_age < 5 and state.tire_life > 90:
            tire_mult = 1.3

        return AgentDecision(
            energy_deployment=self._add_variance(self.profile['energy_deployment']),
            tire_management=self._add_variance(self.profile['tire_management'] * tire_mult),
            fuel_strategy=self._add_variance(self.profile['fuel_strategy']),
            ers_mode=self._add_variance(self.profile['ers_mode']),
            overtake_aggression=self._add_variance(self.profile['overtake_aggression']),
            defense_intensity=self._add_variance(self.profile['defense_intensity'])
        )


class Opportunist(AgentV2):
    """
    Position-aware adaptive strategy.
    Attacks aggressively when behind (P4-P8).
    Defends and conserves when ahead (P1-P3).

    Strategy:
    - Leading (P1-P3): Defend and conserve
    - Midfield (P4-P6): Balanced approach
    - Back (P7+): Attack hard
    """
    def __init__(self):
        profile = {
            'energy_deployment': 70,
            'tire_management': 65,
            'fuel_strategy': 55,
            'ers_mode': 60,
            'overtake_aggression': 50,
            'defense_intensity': 50
        }
        super().__init__("Opportunist", profile)

    def decide(self, state: RaceState) -> AgentDecision:
        # Adjust strategy based on position
        if state.position <= 3:
            # Leading: defend and conserve
            overtake = 40
            defense = 90
            energy = 60
            tire = 55
        elif state.position <= 6:
            # Midfield: balanced
            overtake = 70
            defense = 65
            energy = 75
            tire = 65
        else:
            # Back: attack hard
            overtake = 95
            defense = 50
            energy = 85
            tire = 75

        # Adjust for battery state
        if state.battery_soc < 30:
            energy = max(40, energy - 20)

        return AgentDecision(
            energy_deployment=self._add_variance(energy),
            tire_management=self._add_variance(tire),
            fuel_strategy=self._add_variance(self.profile['fuel_strategy']),
            ers_mode=self._add_variance(self.profile['ers_mode']),
            overtake_aggression=self._add_variance(overtake),
            defense_intensity=self._add_variance(defense)
        )


class AdaptiveAI(AgentV2):
    """
    Playbook-powered AI agent.
    Reads rules from data/playbook.json and applies them dynamically.
    Falls back to balanced strategy if no rules match.

    Strategy:
    - Evaluates playbook rules each lap
    - Applies matching rule actions
    - Uses safe eval() with restricted context
    - Gracefully handles missing playbook
    """
    def __init__(self, playbook_path='data/playbook.json'):
        profile = {
            'energy_deployment': 70,
            'tire_management': 65,
            'fuel_strategy': 55,
            'ers_mode': 60,
            'overtake_aggression': 70,
            'defense_intensity': 70
        }
        super().__init__("AdaptiveAI", profile)

        # Load playbook
        try:
            # Try relative to current file
            playbook_full_path = Path(__file__).parent.parent / playbook_path
            with open(playbook_full_path) as f:
                self.playbook = json.load(f)
        except:
            # Fallback: empty playbook
            self.playbook = {"rules": []}

    def decide(self, state: RaceState) -> AgentDecision:
        # Start with base profile
        decision_dict = self.profile.copy()

        # Apply playbook rules
        for rule in self.playbook.get('rules', []):
            condition = rule.get('condition', '')
            action = rule.get('action', {})

            # Safe eval with restricted context
            safe_vars = {
                'battery_soc': state.battery_soc,
                'lap': state.lap,
                'position': state.position,
                'tire_age': state.tire_age,
                'tire_life': state.tire_life,
                'fuel_remaining': state.fuel_remaining,
                'boost_used': state.boost_used
            }

            try:
                # Evaluate condition safely
                if eval(condition, {"__builtins__": {}}, safe_vars):
                    # Apply action (update decision)
                    # Only update if action contains valid keys
                    for key in ['energy_deployment', 'tire_management', 'fuel_strategy',
                               'ers_mode', 'overtake_aggression', 'defense_intensity']:
                        if key in action:
                            decision_dict[key] = action[key]
            except:
                # Skip invalid rules silently
                pass

        return AgentDecision(
            energy_deployment=self._add_variance(decision_dict.get('energy_deployment', 70)),
            tire_management=self._add_variance(decision_dict.get('tire_management', 65)),
            fuel_strategy=self._add_variance(decision_dict.get('fuel_strategy', 55)),
            ers_mode=self._add_variance(decision_dict.get('ers_mode', 60)),
            overtake_aggression=self._add_variance(decision_dict.get('overtake_aggression', 70)),
            defense_intensity=self._add_variance(decision_dict.get('defense_intensity', 70))
        )


def create_agents_v2() -> list:
    """
    Create all 8 agents for simulation.
    Returns list of AgentV2 instances.

    Returns:
        list: [VerstappenStyle, HamiltonStyle, AlonsoStyle, ElectricBlitzer,
               EnergySaver, TireWhisperer, Opportunist, AdaptiveAI]
    """
    return [
        VerstappenStyle(),
        HamiltonStyle(),
        AlonsoStyle(),
        ElectricBlitzer(),
        EnergySaver(),
        TireWhisperer(),
        Opportunist(),
        AdaptiveAI()
    ]


# Export all public classes and functions
__all__ = [
    'AgentV2',
    'VerstappenStyle',
    'HamiltonStyle',
    'AlonsoStyle',
    'ElectricBlitzer',
    'EnergySaver',
    'TireWhisperer',
    'Opportunist',
    'AdaptiveAI',
    'create_agents_v2'
]
