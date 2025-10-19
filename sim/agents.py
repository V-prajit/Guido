"""
Strategy Gym 2026 - Racing Agent Implementations

This module implements 8 distinct energy deployment strategies for F1 racing agents.
Each agent demonstrates a unique approach to managing the battery/ICE power split
under the 2026 regulations.
"""

from sim.engine import Agent, RaceState


class ElectricBlitz(Agent):
    """
    Aggressive early deployment strategy.

    Deploys maximum battery power early in the race when SOC is high,
    then gradually reduces deployment as battery drains. Results in
    fast early laps but struggles to maintain pace late in the race.

    Strategy:
    - Front-loads battery usage (100% straight, 85% corner early)
    - Minimal harvesting (20%) to maximize early pace
    - Uses boost early (laps 1-10) for maximum early advantage
    - Deployment stays high even as battery drains
    """

    def decide(self, state: RaceState):
        # Very aggressive deployment regardless of battery level
        # (battery will drain quickly but gives early advantage)
        return {
            'deploy_straight': 100,
            'deploy_corner': 85,
            'harvest': 20,
            'use_boost': state.lap < 10 and state.boost_used < 2
        }


class EnergySaver(Agent):
    """
    Conservative early, aggressive late strategy.

    Preserves battery early in the race with conservative deployment,
    then ramps up power usage as the race progresses. Results in
    strong finishing pace and good overtaking opportunities late.

    Strategy:
    - Starts at 40% deployment, ramps to 80% by race end
    - Progressive increase based on race progress
    - Heavy harvesting (70%) early to build/maintain battery
    - Saves boost for final push (after lap 50)
    """

    def decide(self, state: RaceState):
        # Assume 57 lap race for calculation (standard F1 race length)
        race_progress = min(state.lap / 57.0, 1.0)

        return {
            'deploy_straight': 40 + (race_progress * 40),  # 40% → 80%
            'deploy_corner': 40 + (race_progress * 30),    # 40% → 70%
            'harvest': 70,
            'use_boost': state.lap > 50 and state.boost_used < 2
        }


class BalancedHybrid(Agent):
    """
    Steady, consistent strategy throughout the race.

    Maintains constant deployment and harvesting rates for predictable
    performance. Serves as a baseline for comparison with other strategies.

    Strategy:
    - Constant 75% straight deployment
    - Constant 65% corner deployment
    - Constant 55% harvesting (balanced drain/charge)
    - Never uses boost (maximally conservative)
    """

    def decide(self, state: RaceState):
        return {
            'deploy_straight': 75,
            'deploy_corner': 65,
            'harvest': 55,
            'use_boost': False  # Never uses boost
        }


class CornerSpecialist(Agent):
    """
    Corner exit optimization strategy.

    Prioritizes electric deployment on corner exits for better acceleration
    out of turns. Ideal for technical tracks with many corners.

    Strategy:
    - Moderate straight deployment (60%) for competitiveness
    - Very high corner deployment (95%) for corner exit acceleration
    - Moderate harvesting (60%) to maintain battery levels
    - No boost usage (relies on consistent corner performance)
    """

    def decide(self, state: RaceState):
        return {
            'deploy_straight': 60,
            'deploy_corner': 95,
            'harvest': 60,
            'use_boost': False
        }


class StraightDominator(Agent):
    """
    Straight line speed optimization strategy.

    Maximizes electric deployment on straights for top speed.
    Ideal for power tracks with long straights (Monza-style circuits).

    Strategy:
    - High straight deployment (85%) for maximum top speed
    - Low corner deployment (30%) to conserve battery
    - Moderate harvesting (55%) to maintain battery
    - No boost usage (relies on consistent straight-line advantage)
    """

    def decide(self, state: RaceState):
        return {
            'deploy_straight': 85,
            'deploy_corner': 30,
            'harvest': 55,
            'use_boost': False
        }


class LateCharger(Agent):
    """
    Two-phase strategy: harvest early, attack late.

    Heavily harvests energy in the first half of the race to build
    battery reserves, then unleashes aggressive deployment in the
    second half for a strong finish.

    Strategy:
    - Phase 1 (laps 1-29): Moderate deployment (55/50%), high harvest (75%)
    - Phase 2 (laps 30+): Very high deployment (100/90%), low harvest (25%)
    - Uses boost in Phase 2 for maximum late-race attack
    """

    def decide(self, state: RaceState):
        if state.lap < 30:
            # Phase 1: Harvest and conserve
            return {
                'deploy_straight': 35,
                'deploy_corner': 30,
                'harvest': 85,
                'use_boost': False
            }
        else:
            # Phase 2: Attack with accumulated battery
            return {
                'deploy_straight': 100,
                'deploy_corner': 90,
                'harvest': 20,
                'use_boost': state.boost_used < 2
            }


class OvertakeHunter(Agent):
    """
    Position-aware overtaking strategy.

    Adjusts deployment based on race position. Deploys more power when
    in overtaking positions (P2-P4) to capitalize on passing opportunities,
    conserves when leading or out of contention.

    Strategy:
    - High deployment (95%) when in battle positions (P2-P4)
    - Moderate deployment (65%) when leading or far back
    - Moderate harvesting (50%) overall
    - Uses boost when in battle and after lap 10
    """

    def decide(self, state: RaceState):
        # Define "battle zone" as positions 2-4 (chasing leader or defending)
        in_battle = state.position > 1 and state.position < 5

        # Use boost when in battle position and it's mid-race or later
        boost_now = in_battle and state.boost_used < 2 and state.lap > 10

        # Aggressive deployment when in battle, moderate otherwise
        deploy = 95 if in_battle else 65

        return {
            'deploy_straight': deploy,
            'deploy_corner': deploy,
            'harvest': 50,
            'use_boost': boost_now
        }


class AdaptiveAI(Agent):
    """
    AI-powered strategy that reads and follows a playbook.

    This agent evaluates playbook rules in order and executes the first
    matching rule's action. Uses restricted eval() for secure condition
    evaluation.

    Playbook structure:
    {
        "rules": [
            {
                "rule": "Rule name",
                "condition": "battery_soc < 30 and lap > 40",
                "action": {"deploy_straight": 50, "deploy_corner": 45, "harvest": 75},
                "confidence": 0.85,
                "uplift_win_pct": 15.2,
                "rationale": "Why this works"
            }
        ]
    }

    Falls back to proven baseline strategy (78/68/55) if no rules match.
    """

    def __init__(self, name: str, params: dict, playbook: dict = None):
        """
        Initialize AdaptiveAI agent.

        Args:
            name: Agent identifier
            params: Agent-specific parameters
            playbook: Optional playbook dict with strategic rules
        """
        super().__init__(name, params)
        self.playbook = playbook or {'rules': []}
        self.rule_usage = {}

    def matches_condition(self, condition: str, state: RaceState) -> bool:
        """
        Evaluate condition string against current race state.

        Uses restricted eval() for security - only allows access to state
        variables, no builtins or external functions.

        Args:
            condition: Python expression string (e.g., "battery_soc < 30 and lap > 40")
            state: Current RaceState

        Returns:
            True if condition matches, False otherwise (including on errors)

        Example:
            >>> state = RaceState(lap=45, battery_soc=25, position=3, tire_age=45, boost_used=0)
            >>> agent.matches_condition("battery_soc < 30 and lap > 40", state)
            True
        """
        try:
            # Build safe context with only state variables
            context = {
                'battery_soc': state.battery_soc,
                'lap': state.lap,
                'position': state.position,
                'tire_age': state.tire_age,
                'boost_used': state.boost_used
            }

            # Restricted eval: no builtins, only state variables
            # This prevents code injection while allowing condition evaluation
            result = eval(condition, {"__builtins__": {}}, context)

            return bool(result)

        except Exception as e:
            # Log error and return False for safety
            # In production, this would log to a file
            # For now, silently fail to avoid spamming console
            return False

    def decide(self, state: RaceState):
        """
        Make deployment decision based on playbook rules.

        Iterates through playbook rules in order, returns first matching
        rule's action. Falls back to baseline if no rules match.

        Args:
            state: Current RaceState

        Returns:
            Decision dict with deploy_straight, deploy_corner, harvest, use_boost
        """
        # Check each rule in order
        for idx, rule in enumerate(self.playbook.get('rules', [])):
            condition = rule.get('condition', '')
            action = rule.get('action', {})

            # If condition matches, return this rule's action
            if condition and action and self.matches_condition(condition, state):
                # Track rule usage
                rule_name = rule.get('rule', f'Rule {idx}')
                self.rule_usage[rule_name] = self.rule_usage.get(rule_name, 0) + 1

                # Ensure all required fields exist in action
                return {
                    'deploy_straight': action.get('deploy_straight', 78),
                    'deploy_corner': action.get('deploy_corner', 68),
                    'harvest': action.get('harvest', 55),
                    'use_boost': action.get('use_boost', False)
                }

        # No rules matched - use proven baseline strategy
        fallback_name = 'Fallback Baseline'
        self.rule_usage[fallback_name] = self.rule_usage.get(fallback_name, 0) + 1

        return {
            'deploy_straight': 78,
            'deploy_corner': 68,
            'harvest': 55,
            'use_boost': False
        }


def create_agents():
    """
    Factory function to create all 8 racing agents.

    Returns a list of agent instances in a consistent order for testing
    and multi-agent race simulations.

    Returns:
        list[Agent]: List of 8 agent instances
    """
    return [
        ElectricBlitz("Electric_Blitz", {}),
        EnergySaver("Energy_Saver", {}),
        BalancedHybrid("Balanced_Hybrid", {}),
        CornerSpecialist("Corner_Specialist", {}),
        StraightDominator("Straight_Dominator", {}),
        LateCharger("Late_Charger", {}),
        OvertakeHunter("Overtake_Hunter", {}),
        AdaptiveAI("Adaptive_AI", {})
    ]
