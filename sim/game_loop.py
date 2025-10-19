"""
Game Loop Orchestrator
Runs lap-by-lap race simulation with decision point pauses.
"""

import asyncio
import numpy as np
from typing import Dict, Optional, List
from dataclasses import asdict

from sim.quick_sim import (
    RaceState,
    run_quick_sims_from_state,
    generate_strategy_variations,
    check_decision_point
)
from api.gemini_game_advisor import GameAdvisor
from api.game_sessions import GameState, PlayerState, OpponentState


class GameLoopOrchestrator:
    """
    Orchestrates the game loop:
    - Advances laps
    - Detects decision points
    - Pauses for player input
    - Resumes with chosen strategy
    """

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.advisor = GameAdvisor()
        self.handled_events = set()  # Track which events we've already shown

        # Pre-computation for instant decision display
        self.pre_computed_decision = None  # Cache for lap 3 rain decision
        self.pre_compute_started = False   # Track if we've started pre-computing

        # Timing configuration: adjust LAP_TIME_MULTIPLIER for demo speed
        # 1.0 = realistic 90s laps (57 laps = 85 min race)
        # 5.0 = demo-friendly 18s laps (57 laps = 17 min race)
        # 10.0 = fast 9s laps (57 laps = 8.5 min race)
        # 50.0 = ultra-fast 1.8s laps (57 laps = 2.7 min race)
        import os
        self.lap_time_multiplier = float(os.getenv("LAP_TIME_MULTIPLIER", "5.0"))
        self.base_lap_time = 90.0

    def advance_lap(self) -> Dict:
        """
        Simulate one lap for all racers.

        Returns:
            Dict with lap results and events
        """
        self.game_state.current_lap += 1
        lap = self.game_state.current_lap

        # Check for race completion
        if lap > self.game_state.total_laps:
            self.game_state.is_complete = True
            return {
                'lap': lap,
                'race_complete': True,
                'final_position': self.game_state.player.position
            }

        # Check for scenario events
        if lap == self.game_state.rain_lap:
            self.game_state.is_raining = True

        if lap == self.game_state.safety_car_lap:
            self.game_state.safety_car_active = True

        # Simulate player lap
        player_result = self._simulate_player_lap()

        # Simulate opponent laps
        opponent_results = self._simulate_opponent_laps()

        # Update positions
        self._update_race_positions(player_result, opponent_results)

        # Calculate speed, gap, and lap progress for visualization
        self._update_visualization_metrics(lap)

        return {
            'lap': lap,
            'race_complete': False,
            'player': asdict(self.game_state.player),
            'opponents': [asdict(opp) for opp in self.game_state.opponents],
            'is_raining': self.game_state.is_raining,
            'safety_car_active': self.game_state.safety_car_active
        }

    def _simulate_player_lap(self) -> Dict:
        """Simulate one lap for player"""
        player = self.game_state.player

        # Get current strategy parameters
        energy = player.energy_deployment
        tire_mgmt = player.tire_management
        fuel_strat = player.fuel_strategy
        ers = player.ers_mode

        # Battery dynamics (AMPLIFIED for demo visibility)
        # High energy deployment = faster drain, more dramatic changes
        battery_drain = (energy / 100) * 1.2  # Increased from 0.8 to 1.2
        battery_gain = (ers / 100) * 0.8      # Increased from 0.6 to 0.8
        player.battery_soc = max(0, min(100, player.battery_soc - battery_drain + battery_gain))

        # Tire degradation (AMPLIFIED - aggressive driving = faster wear)
        # Low tire management (aggressive) = 2-3x faster wear for visible impact
        base_tire_wear = (100 - tire_mgmt) / 100 * 1.5
        if tire_mgmt < 50:  # Aggressive tire usage
            tire_wear = base_tire_wear * 2.0  # Double wear when aggressive
        else:
            tire_wear = base_tire_wear
        player.tire_life = max(0, player.tire_life - tire_wear)

        # Fuel consumption (AMPLIFIED - aggressive = higher burn rate)
        base_fuel_burn = (100 - fuel_strat) / 100 * 0.5
        if fuel_strat < 50:  # Aggressive fuel usage
            fuel_burn = base_fuel_burn * 1.5  # 50% more fuel burn
        else:
            fuel_burn = base_fuel_burn
        player.fuel_remaining = max(0, player.fuel_remaining - fuel_burn)

        # Lap time calculation (base: 90s) - AMPLIFIED for dramatic speed differences
        lap_time = 90.0

        # Energy deployment impact (AMPLIFIED - 2x more impact for demo)
        # Low (30) = +0.3s, Medium (60) = baseline, High (90) = -0.6s
        lap_time -= (energy / 100) * 0.6  # Doubled from 0.3 to 0.6

        # Tire management impact (AMPLIFIED)
        lap_time += (100 - tire_mgmt) / 100 * 0.4  # Doubled from 0.2 to 0.4

        # Battery penalty (AMPLIFIED)
        if player.battery_soc < 20:
            lap_time += (20 - player.battery_soc) * 0.04  # Doubled from 0.02 to 0.04
        if self.game_state.is_raining:
            lap_time += 2.0  # Rain penalty
        if self.game_state.safety_car_active:
            lap_time += 30.0  # Safety car neutralizes pace

        # Add some randomness
        lap_time += np.random.uniform(-0.5, 0.5)

        # Apply LAP_TIME_MULTIPLIER for demo speed (e.g., 90s / 5.0 = 18s)
        lap_time = lap_time / self.lap_time_multiplier

        player.lap_time = lap_time
        player.cumulative_time += lap_time

        return {
            'agent': 'Player',
            'lap_time': lap_time,
            'cumulative_time': player.cumulative_time,
            'battery_soc': player.battery_soc,
            'tire_life': player.tire_life,
            'fuel_remaining': player.fuel_remaining
        }

    def _simulate_opponent_laps(self) -> List[Dict]:
        """Simulate laps for all AI opponents"""
        results = []

        for opponent in self.game_state.opponents:
            # AI opponents have fixed strategies based on their agent type
            # Simplified simulation for speed

            # Get agent-specific strategy tendency
            if 'Verstappen' in opponent.agent_type:
                energy, tire_mgmt, fuel_strat, ers = 70, 80, 70, 70
            elif 'Hamilton' in opponent.agent_type:
                energy, tire_mgmt, fuel_strat, ers = 60, 90, 75, 65
            elif 'Alonso' in opponent.agent_type:
                energy, tire_mgmt, fuel_strat, ers = 55, 85, 80, 75
            elif 'Aggressive' in opponent.agent_type:
                energy, tire_mgmt, fuel_strat, ers = 85, 60, 55, 80
            elif 'Tire' in opponent.agent_type:
                energy, tire_mgmt, fuel_strat, ers = 50, 95, 75, 60
            elif 'Energy' in opponent.agent_type:
                energy, tire_mgmt, fuel_strat, ers = 90, 70, 60, 85
            else:  # Balanced
                energy, tire_mgmt, fuel_strat, ers = 60, 75, 70, 65

            # Battery dynamics (AMPLIFIED to match player)
            battery_drain = (energy / 100) * 1.2  # Increased from 0.8 to 1.2
            battery_gain = (ers / 100) * 0.8      # Increased from 0.6 to 0.8
            opponent.battery_soc = max(0, min(100, opponent.battery_soc - battery_drain + battery_gain))

            # Tire degradation (AMPLIFIED to match player - aggressive = 2x faster wear)
            base_tire_wear = (100 - tire_mgmt) / 100 * 1.5
            if tire_mgmt < 50:  # Aggressive tire usage
                tire_wear = base_tire_wear * 2.0  # Double wear when aggressive
            else:
                tire_wear = base_tire_wear
            opponent.tire_life = max(0, opponent.tire_life - tire_wear)

            # Fuel consumption (AMPLIFIED to match player - aggressive = 1.5x faster burn)
            base_fuel_burn = (100 - fuel_strat) / 100 * 0.5
            if fuel_strat < 50:  # Aggressive fuel usage
                fuel_burn = base_fuel_burn * 1.5  # 50% more fuel burn
            else:
                fuel_burn = base_fuel_burn
            opponent.fuel_remaining = max(0, opponent.fuel_remaining - fuel_burn)

            # Lap time (AMPLIFIED to match player)
            lap_time = 90.0
            lap_time -= (energy / 100) * 0.6  # Doubled from 0.3 to 0.6
            lap_time += (100 - tire_mgmt) / 100 * 0.4  # Doubled from 0.2 to 0.4
            if opponent.battery_soc < 20:
                lap_time += (20 - opponent.battery_soc) * 0.04  # Doubled from 0.02 to 0.04
            if self.game_state.is_raining:
                lap_time += 2.0
            if self.game_state.safety_car_active:
                lap_time += 30.0

            # Add randomness (AI varies more than player for realism)
            lap_time += np.random.uniform(-1.0, 1.0)

            # Apply LAP_TIME_MULTIPLIER for demo speed (e.g., 90s / 5.0 = 18s)
            lap_time = lap_time / self.lap_time_multiplier

            opponent.cumulative_time += lap_time
            opponent.last_lap_time = lap_time  # Track for speed calculation

            results.append({
                'agent': opponent.name,
                'agent_type': opponent.agent_type,
                'lap_time': lap_time,
                'cumulative_time': opponent.cumulative_time,
                'battery_soc': opponent.battery_soc,
                'tire_life': opponent.tire_life,
                'fuel_remaining': opponent.fuel_remaining
            })

        return results

    def _update_race_positions(self, player_result: Dict, opponent_results: List[Dict]):
        """Update race positions based on cumulative times"""
        # Combine all results
        all_racers = [(player_result['cumulative_time'], 'Player', None)]
        for i, opp_result in enumerate(opponent_results):
            all_racers.append((
                opp_result['cumulative_time'],
                opp_result['agent'],
                self.game_state.opponents[i]
            ))

        # Sort by cumulative time
        all_racers.sort(key=lambda x: x[0])

        # Update positions
        for position, (_, name, opponent) in enumerate(all_racers, start=1):
            if name == 'Player':
                self.game_state.player.position = position
            else:
                opponent.position = position

    def _update_visualization_metrics(self, current_lap: int):
        """
        Calculate speed, gap_to_leader, and lap_progress for smooth visualization.

        Speed: Derived from lap_time (faster lap = higher speed)
        Gap to leader: Time difference from leader's cumulative time
        Lap progress: Position within current lap (0-1 cycling per lap for smooth track animation)

        CRITICAL FIX: Use modulo-based calculation to avoid reliance on global current_lap,
        which caused cars to get stuck when cumulative_time didn't align with expected schedule.
        """
        # Find the race leader (lowest cumulative time)
        all_racers = [self.game_state.player] + self.game_state.opponents
        leader_time = min(racer.cumulative_time for racer in all_racers)

        # Expected lap time in demo units (e.g., 90s / 5.0 = 18s)
        expected_lap_time = self.base_lap_time / self.lap_time_multiplier

        # Update player metrics
        player = self.game_state.player
        player.speed = self._calculate_speed(player.lap_time)
        player.gap_to_leader = player.cumulative_time - leader_time

        # FIX: Modulo-based lap_progress (independent of global current_lap)
        # This gives fractional laps (e.g., 5.7 laps), take remainder for 0-1 progress
        car_fractional_laps = player.cumulative_time / expected_lap_time
        player.lap_progress = float(car_fractional_laps - int(car_fractional_laps))  # Equivalent to % 1.0

        # Update opponent metrics
        for opponent in self.game_state.opponents:
            opponent.speed = self._calculate_speed(opponent.last_lap_time)
            opponent.gap_to_leader = opponent.cumulative_time - leader_time

            # FIX: Same modulo-based calculation per car
            opp_fractional_laps = opponent.cumulative_time / expected_lap_time
            opponent.lap_progress = float(opp_fractional_laps - int(opp_fractional_laps))

    def _calculate_speed(self, lap_time: float) -> float:
        """
        Convert lap_time to approximate speed in km/h for visualization.

        Faster laps = higher speed.
        Accounts for LAP_TIME_MULTIPLIER to show accurate speeds in demo mode.
        """
        # Expected lap time in demo units (e.g., 90s / 5.0 = 18s)
        expected_demo_time = self.base_lap_time / self.lap_time_multiplier

        base_speed = 300.0  # km/h at expected demo lap time

        # Speed delta: each second faster/slower = ~50 km/h change (increased sensitivity)
        # This gives visible speed differences in demo mode
        speed_delta = (expected_demo_time - lap_time) * 50.0
        speed = base_speed + speed_delta

        # Clamp to realistic F1 speeds (250-330 km/h for tighter visual range)
        return max(250.0, min(330.0, speed))

    def check_for_decision_point(self) -> Optional[Dict]:
        """
        Check if game should pause for player decision.

        Returns:
            Decision point dict if triggered, None otherwise
        """
        # Build current race state
        current_state = RaceState(
            lap=self.game_state.current_lap,
            total_laps=self.game_state.total_laps,
            position=self.game_state.player.position,
            battery_soc=self.game_state.player.battery_soc,
            tire_life=self.game_state.player.tire_life,
            fuel_remaining=self.game_state.player.fuel_remaining,
            gap_ahead=0.0,  # TODO: Calculate from cumulative times
            gap_behind=0.0,
            rain=self.game_state.is_raining,
            safety_car=self.game_state.safety_car_active
        )

        # Check for decision triggers (HIGH-IMPACT EVENTS ONLY)
        event_type = check_decision_point(current_state, self.handled_events)

        if event_type:
            # Only trigger on specific high-impact events
            high_impact_events = {
                'RAIN_START', 'RAIN_STOP', 'SAFETY_CAR',
                'BATTERY_LOW', 'BATTERY_CRITICAL',
                'TIRE_CRITICAL'
            }

            if event_type in high_impact_events:
                # Mark as handled
                self.handled_events.add(event_type)

                return {
                    'triggered': True,
                    'event_type': event_type,
                    'state': current_state
                }

        # No routine strategic checkpoints - car runs on configured parameters
        return {
            'triggered': False
        }

    async def get_decision_recommendations(
        self,
        event_type: str,
        current_state: RaceState
    ) -> Dict:
        """
        Run quick sims and get Gemini recommendations.

        Returns:
            Recommendations dict with top 2 recommended + 1 to avoid
        """
        # Generate 3 strategy alternatives
        strategy_params = generate_strategy_variations(current_state, event_type)

        # Run 100 quick sims per strategy (300 total)
        # NOTE: Using quick_sim for speed. If performance allows, switch to decision_sim
        # for more realistic physics-based results.
        sim_results = run_quick_sims_from_state(
            current_state,
            strategy_params,
            num_sims_per_strategy=100
        )

        # Get Gemini analysis
        race_context = {
            'lap': current_state.lap,
            'total_laps': current_state.total_laps,
            'position': current_state.position,
            'battery_soc': current_state.battery_soc,
            'tire_life': current_state.tire_life,
            'fuel_remaining': current_state.fuel_remaining,
            'event_type': event_type
        }

        recommendations = self.advisor.analyze_decision_point(
            sim_results=sim_results,
            race_context=race_context,
            strategy_params=strategy_params,
            timeout_seconds=2.5
        )

        # Add strategy names for UI
        strategy_names = ['Aggressive', 'Balanced', 'Conservative']
        for rec in recommendations['recommended']:
            rec['strategy_name'] = strategy_names[rec['strategy_id']]
            rec['strategy_params'] = strategy_params[rec['strategy_id']]

        if 'avoid' in recommendations and recommendations['avoid']:
            recommendations['avoid']['strategy_name'] = strategy_names[recommendations['avoid']['strategy_id']]
            recommendations['avoid']['strategy_params'] = strategy_params[recommendations['avoid']['strategy_id']]

        return recommendations

    def apply_strategy_choice(self, strategy_id: int):
        """
        Apply player's chosen strategy.

        Updates player's strategy parameters.
        """
        # Build current state
        current_state = RaceState(
            lap=self.game_state.current_lap,
            total_laps=self.game_state.total_laps,
            position=self.game_state.player.position,
            battery_soc=self.game_state.player.battery_soc,
            tire_life=self.game_state.player.tire_life,
            fuel_remaining=self.game_state.player.fuel_remaining,
            rain=self.game_state.is_raining,
            safety_car=self.game_state.safety_car_active
        )

        # Get the event type from last decision
        event_type = self._get_current_event_type()

        # Generate strategies (same as in recommendations)
        strategy_params = generate_strategy_variations(current_state, event_type)

        # Get selected strategy
        if 0 <= strategy_id < len(strategy_params):
            chosen_strategy = strategy_params[strategy_id]

            # Update player parameters
            self.game_state.player.energy_deployment = chosen_strategy['energy_deployment']
            self.game_state.player.tire_management = chosen_strategy['tire_management']
            self.game_state.player.fuel_strategy = chosen_strategy['fuel_strategy']
            self.game_state.player.ers_mode = chosen_strategy['ers_mode']
            self.game_state.player.overtake_aggression = chosen_strategy['overtake_aggression']
            self.game_state.player.defense_intensity = chosen_strategy['defense_intensity']

            # Record decision
            self.game_state.decision_history.append({
                'lap': self.game_state.current_lap,
                'event_type': event_type,
                'strategy_chosen': strategy_id,
                'strategy_params': chosen_strategy
            })

            return True
        return False

    def _get_current_event_type(self) -> str:
        """Get current event type for strategy generation"""
        if self.game_state.is_raining and 'RAIN_START' in self.handled_events:
            return 'RAIN_START'
        elif self.game_state.safety_car_active and 'SAFETY_CAR' in self.handled_events:
            return 'SAFETY_CAR'
        elif self.game_state.player.battery_soc < 15 and 'BATTERY_LOW' in self.handled_events:
            return 'BATTERY_LOW'
        elif self.game_state.player.tire_life < 25 and 'TIRE_CRITICAL' in self.handled_events:
            return 'TIRE_CRITICAL'
        else:
            return 'STRATEGIC_CHECKPOINT'

    def should_pre_compute_next_lap(self) -> Optional[str]:
        """
        Check if next lap will trigger a known decision point that can be pre-computed.

        Returns:
            Event type string if pre-computation should be triggered, None otherwise
        """
        next_lap = self.game_state.current_lap + 1

        # Only pre-compute for high-certainty events (scheduled events)
        # Don't pre-compute dynamic events (battery low, tire degraded) as they're unpredictable

        # Rain starting next lap
        if (self.game_state.rain_lap == next_lap
            and not self.game_state.is_raining
            and 'RAIN_START' not in self.handled_events
            and not self.pre_compute_started):
            return 'RAIN_START'

        # Safety car deploying next lap
        if (self.game_state.safety_car_lap == next_lap
            and not self.game_state.safety_car_active
            and 'SAFETY_CAR' not in self.handled_events
            and not self.pre_compute_started):
            return 'SAFETY_CAR'

        return None

    def pre_compute_rain_decision(self):
        """
        Pre-compute rain decision on lap 2 for instant display on lap 3.

        This is a SYNCHRONOUS method designed to run in ThreadPoolExecutor.
        Runs 300 simulations + Gemini analysis in a separate thread.
        """
        print(f"[PRE-COMPUTE] Starting rain decision pre-computation on lap {self.game_state.current_lap}")

        # Build predicted state for lap 3 with rain
        predicted_state = RaceState(
            lap=3,
            total_laps=self.game_state.total_laps,
            position=self.game_state.player.position,
            battery_soc=self.game_state.player.battery_soc,
            tire_life=self.game_state.player.tire_life,
            fuel_remaining=self.game_state.player.fuel_remaining,
            gap_ahead=0.0,
            gap_behind=0.0,
            rain=True,
            safety_car=False
        )

        # Generate 3 strategy alternatives
        strategy_params = generate_strategy_variations(predicted_state, 'RAIN_START')

        # Run 300 quick sims (100 per strategy)
        sim_results = run_quick_sims_from_state(
            predicted_state,
            strategy_params,
            num_sims_per_strategy=100
        )

        # Get Gemini analysis
        race_context = {
            'lap': 3,
            'total_laps': self.game_state.total_laps,
            'position': self.game_state.player.position,
            'battery_soc': self.game_state.player.battery_soc,
            'tire_life': self.game_state.player.tire_life,
            'fuel_remaining': self.game_state.player.fuel_remaining,
            'event_type': 'RAIN_START'
        }

        recommendations = self.advisor.analyze_decision_point(
            sim_results=sim_results,
            race_context=race_context,
            strategy_params=strategy_params,
            timeout_seconds=2.5
        )

        # Add strategy names
        strategy_names = ['Aggressive', 'Balanced', 'Conservative']
        for rec in recommendations['recommended']:
            rec['strategy_name'] = strategy_names[rec['strategy_id']]
            rec['strategy_params'] = strategy_params[rec['strategy_id']]

        if 'avoid' in recommendations and recommendations['avoid']:
            recommendations['avoid']['strategy_name'] = strategy_names[recommendations['avoid']['strategy_id']]
            recommendations['avoid']['strategy_params'] = strategy_params[recommendations['avoid']['strategy_id']]

        # Cache the result
        self.pre_computed_decision = recommendations
        print(f"[PRE-COMPUTE] ✓ Rain decision pre-computed successfully (latency: {recommendations.get('latency_ms', 0):.0f}ms)")

    def _project_state_forward(self) -> RaceState:
        """
        Project player state forward one lap for pre-computation.

        Estimates battery, tire, fuel consumption based on current strategy.

        Returns:
            Projected RaceState for next lap
        """
        player = self.game_state.player

        # Estimate resource consumption for one lap
        energy = player.energy_deployment
        tire_mgmt = player.tire_management
        fuel_strat = player.fuel_strategy
        ers = player.ers_mode

        # Battery projection (AMPLIFIED to match game_loop dynamics)
        battery_drain = (energy / 100) * 1.2
        battery_gain = (ers / 100) * 0.8
        projected_battery = max(0, min(100, player.battery_soc - battery_drain + battery_gain))

        # Tire projection (AMPLIFIED to match game_loop dynamics)
        base_tire_wear = (100 - tire_mgmt) / 100 * 1.5
        if tire_mgmt < 50:
            tire_wear = base_tire_wear * 2.0
        else:
            tire_wear = base_tire_wear
        projected_tire = max(0, player.tire_life - tire_wear)

        # Fuel projection (AMPLIFIED to match game_loop dynamics)
        base_fuel_burn = (100 - fuel_strat) / 100 * 0.5
        if fuel_strat < 50:
            fuel_burn = base_fuel_burn * 1.5
        else:
            fuel_burn = base_fuel_burn
        projected_fuel = max(0, player.fuel_remaining - fuel_burn)

        return RaceState(
            lap=self.game_state.current_lap + 1,
            total_laps=self.game_state.total_laps,
            position=player.position,  # Assume position stays same (reasonable approximation)
            battery_soc=projected_battery,
            tire_life=projected_tire,
            fuel_remaining=projected_fuel,
            gap_ahead=0.0,
            gap_behind=0.0,
            rain=self.game_state.rain_lap == (self.game_state.current_lap + 1),
            safety_car=self.game_state.safety_car_lap == (self.game_state.current_lap + 1)
        )