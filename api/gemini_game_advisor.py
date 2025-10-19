"""
Real-time Gemini advisor for F1 racing game.
Analyzes strategic alternatives and provides instant recommendations.

Author: Claude Code
Date: 2025-10-19
"""

import os
import json
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

# Try to import Gemini, gracefully handle if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai not installed. Install with: pip install google-generativeai")


class GameAdvisor:
    """Provides real-time strategy recommendations during gameplay."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GameAdvisor with Gemini model.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.gemini_available = False
        self.model = None

        # CHERRY-PICKED PATTERN from PR #6 (graceful degradation)
        if GEMINI_AVAILABLE and self.api_key and self.api_key != 'your_key_here':
            try:
                genai.configure(api_key=self.api_key)

                # Try to create model with system_instruction (v0.5.0+)
                try:
                    self.model = genai.GenerativeModel(
                        'gemini-2.0-flash-exp',
                        system_instruction=self._load_system_prompt()
                    )
                except TypeError:
                    # Fallback for older versions without system_instruction support
                    print("⚠️ Old google-generativeai version detected, using model without system_instruction")
                    print("   (Upgrade with: pip install --upgrade google-generativeai)")
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

                self.gemini_available = True
                print("✅ GameAdvisor initialized with Gemini")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                print("📋 Will use fallback recommendations")
        else:
            print("📋 GameAdvisor initialized in fallback mode (no Gemini)")

    def analyze_decision_point(
        self,
        sim_results: pd.DataFrame,
        race_context: dict,
        strategy_params: List[dict],
        timeout_seconds: float = 2.5
    ) -> dict:
        """
        Main entry point for game loop decision analysis.

        Args:
            sim_results: DataFrame with simulation results (100 rows per strategy)
                Required columns: strategy_id, final_position, won
                Optional columns: battery_soc, lap, tire_life, fuel_remaining

            race_context: Current race state
                {
                    'lap': 15,
                    'total_laps': 57,
                    'position': 4,
                    'battery_soc': 45.0,
                    'tire_life': 62.0,
                    'fuel_remaining': 28.0,
                    'event_type': 'RAIN_START'  # or SAFETY_CAR, TIRE_CRITICAL, etc.
                }

            strategy_params: List of 3 strategy configurations (6 variables each)
                [
                    {
                        'energy_deployment': 85,
                        'tire_management': 70,
                        'fuel_strategy': 60,
                        'ers_mode': 80,
                        'overtake_aggression': 90,
                        'defense_intensity': 40
                    },
                    {...},  # Strategy B
                    {...}   # Strategy C
                ]

            timeout_seconds: Max time for Gemini analysis (fallback after)

        Returns:
            {
                'recommended': [
                    {
                        'strategy_id': 0,
                        'strategy_name': 'Aggressive',
                        'strategy_params': {...},
                        'win_rate': 42.0,
                        'avg_position': 2.3,
                        'rationale': 'Rain reduces grip, deploy electric now...',
                        'confidence': 0.85
                    },
                    {...}  # Second best
                ],
                'avoid': {
                    'strategy_id': 2,
                    'strategy_name': 'Conservative',
                    'strategy_params': {...},
                    'win_rate': 8.0,
                    'avg_position': 4.8,
                    'rationale': 'Too passive, will lose positions...',
                    'risk': '82% chance of dropping to P7+'
                },
                'latency_ms': 1850,
                'used_fallback': False,
                'gemini_available': True
            }
        """

        start_time = time.time()

        # Step 1: Aggregate simulation results
        strategy_stats = self._aggregate_strategy_results(sim_results, strategy_params)

        # Step 2: Try Gemini (with timeout and retry)
        if self.gemini_available:
            try:
                recommendations = self._call_gemini_with_timeout(
                    strategy_stats,
                    race_context,
                    timeout_seconds
                )
                recommendations['used_fallback'] = False
                recommendations['gemini_available'] = True
            except Exception as e:
                print(f"⚠️ Gemini analysis failed: {e}")
                print("📋 Using fallback recommendations")
                recommendations = self._fallback_recommendations(strategy_stats, strategy_params)
                recommendations['used_fallback'] = True
                recommendations['gemini_available'] = False
        else:
            recommendations = self._fallback_recommendations(strategy_stats, strategy_params)
            recommendations['used_fallback'] = True
            recommendations['gemini_available'] = False

        # Step 3: Add metadata
        recommendations['latency_ms'] = int((time.time() - start_time) * 1000)
        recommendations['timestamp'] = datetime.utcnow().isoformat() + 'Z'

        return recommendations

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _aggregate_strategy_results(
        self,
        sim_results: pd.DataFrame,
        strategy_params: List[dict]
    ) -> List[dict]:
        """
        Summarize simulation results for each strategy.

        Returns:
            [
                {
                    'strategy_id': 0,
                    'params': {...},
                    'win_rate': 42.0,
                    'avg_position': 2.3,
                    'position_distribution': {
                        'wins': 42,
                        'podium': 35,
                        'points': 18,
                        'outside_points': 5
                    },
                    'avg_final_battery': 15.2,
                    'dnf_rate': 0.0
                },
                ...
            ]
        """
        aggregated = []

        num_strategies = len(strategy_params)

        for strategy_id in range(num_strategies):
            # Filter data for this strategy
            strategy_data = sim_results[sim_results['strategy_id'] == strategy_id].copy()

            if len(strategy_data) == 0:
                print(f"⚠️ No simulation data for strategy {strategy_id}")
                continue

            # Calculate win metrics
            total_sims = len(strategy_data)
            wins = int(strategy_data['won'].sum()) if 'won' in strategy_data.columns else 0

            # Position distribution
            if 'final_position' in strategy_data.columns:
                p1_count = wins
                p2_3_count = len(strategy_data[strategy_data['final_position'].isin([2, 3])])
                p4_10_count = len(strategy_data[
                    (strategy_data['final_position'] >= 4) &
                    (strategy_data['final_position'] <= 10)
                ])
                outside_points = total_sims - p1_count - p2_3_count - p4_10_count

                avg_position = float(strategy_data['final_position'].mean())
            else:
                p1_count = wins
                p2_3_count = 0
                p4_10_count = 0
                outside_points = total_sims - wins
                avg_position = 5.0

            # Battery analysis (get final battery from last lap of each sim)
            avg_final_battery = 50.0  # default
            if 'battery_soc' in strategy_data.columns:
                # Group by simulation run and get last battery value
                if 'sim_run_id' in strategy_data.columns:
                    final_batteries = strategy_data.groupby('sim_run_id')['battery_soc'].last()
                    avg_final_battery = float(final_batteries.mean())
                else:
                    # If no sim_run_id, assume last rows are final states
                    avg_final_battery = float(strategy_data['battery_soc'].tail(total_sims).mean())

            aggregated.append({
                'strategy_id': strategy_id,
                'params': strategy_params[strategy_id],
                'win_rate': (wins / total_sims * 100) if total_sims > 0 else 0.0,
                'avg_position': avg_position,
                'position_distribution': {
                    'wins': p1_count,
                    'podium': p2_3_count,
                    'points': p4_10_count,
                    'outside_points': outside_points
                },
                'avg_final_battery': avg_final_battery,
                'dnf_rate': 0.0  # TODO: Track DNFs when physics supports it
            })

        return aggregated

    def _build_game_decision_prompt(
        self,
        strategy_stats: List[dict],
        race_context: dict
    ) -> str:
        """
        Build Gemini prompt for real-time decision analysis.
        """

        strategy_names = ['Aggressive', 'Balanced', 'Conservative']

        prompt = f"""
RACE SITUATION:
- Lap: {race_context.get('lap', 0)}/{race_context.get('total_laps', 57)}
- Current Position: P{race_context.get('position', 0)}
- Battery SOC: {race_context.get('battery_soc', 50.0):.1f}%
- Tire Life: {race_context.get('tire_life', 100.0):.1f}%
- Fuel Remaining: {race_context.get('fuel_remaining', 50.0):.1f} kg
- **EVENT: {race_context.get('event_type', 'DECISION_POINT')}**

STRATEGY ALTERNATIVES TESTED (100 simulations each):

"""

        for i, stats in enumerate(strategy_stats):
            strategy_name = strategy_names[i] if i < len(strategy_names) else f"Strategy {i}"

            params_formatted = "\n".join([
                f"  • {key.replace('_', ' ').title()}: {value}"
                for key, value in stats['params'].items()
            ])

            dist = stats['position_distribution']

            prompt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strategy {chr(65+i)}: {strategy_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configuration:
{params_formatted}

Results (100 races):
- Win Rate: {stats['win_rate']:.1f}% ({dist['wins']} wins)
- Podium Finishes: {dist['podium']} (P2-P3)
- Points Finishes: {dist['points']} (P4-P10)
- Outside Points: {dist['outside_points']}
- Average Final Position: P{stats['avg_position']:.1f}
- Average Final Battery: {stats['avg_final_battery']:.1f}%
- DNF Rate: {stats['dnf_rate']:.1f}%

"""

        prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR TASK:
1. Recommend the TOP 2 strategies with highest success probability
2. Identify the WORST 1 strategy to AVOID
3. Be DECISIVE and ACTIONABLE - driver needs decision NOW

Consider:
- Current race position and objectives (win vs points)
- Battery, tire, and fuel states
- Event type and its strategic implications
- Risk vs reward tradeoffs

Output ONLY valid JSON (no markdown, no code blocks):

{
  "recommended": [
    {
      "strategy_id": 0,
      "rationale": "Clear 2-3 sentence explanation why this works best",
      "confidence": 0.85
    },
    {
      "strategy_id": 1,
      "rationale": "Clear 2-3 sentence explanation why this is second best",
      "confidence": 0.78
    }
  ],
  "avoid": {
    "strategy_id": 2,
    "rationale": "Clear 2-3 sentence explanation why this fails",
    "risk": "Specific measurable consequence (e.g., 'Drops to P7 in 82% of scenarios')"
  }
}
"""

        return prompt

    def _call_gemini_with_timeout(
        self,
        strategy_stats: List[dict],
        race_context: dict,
        timeout: float
    ) -> dict:
        """
        Call Gemini with timeout and retry logic.
        ADAPTED FROM PR #6 retry pattern.
        """

        prompt = self._build_game_decision_prompt(strategy_stats, race_context)

        max_retries = 2  # Fast retries for game loop (total 3 attempts)

        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.2,  # Low for consistent, deterministic output
                        'max_output_tokens': 1024,
                    },
                    request_options={'timeout': timeout}
                )

                # Parse response (handles markdown wrappers)
                parsed = self._parse_gemini_response(response.text)

                # Validate and enrich with stats
                validated = self._validate_and_enrich_recommendations(parsed, strategy_stats)

                return validated

            except Exception as e:
                if attempt < max_retries:
                    wait_time = 0.3 * (2 ** attempt)  # 0.3s, 0.6s
                    print(f"⚠️ Gemini attempt {attempt+1} failed: {e}")
                    print(f"   Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Gemini failed after {max_retries+1} attempts")
                    raise

    def _parse_gemini_response(self, text: str) -> dict:
        """
        CHERRY-PICKED FROM PR #6 (lines 192-213).
        Parse Gemini JSON, handling markdown code block wrappers.
        """
        text = text.strip()

        # Remove markdown code blocks if present
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]

        if text.endswith('```'):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse Gemini JSON response: {e}\n\n"
                f"Response preview:\n{text[:500]}"
            )

    def _validate_and_enrich_recommendations(
        self,
        recommendations: dict,
        strategy_stats: List[dict]
    ) -> dict:
        """
        Validate Gemini output schema and enrich with strategy data.
        """

        strategy_names = ['Aggressive', 'Balanced', 'Conservative']

        # Check required fields
        if 'recommended' not in recommendations:
            raise ValueError("Missing 'recommended' field in Gemini response")
        if 'avoid' not in recommendations:
            raise ValueError("Missing 'avoid' field in Gemini response")

        if not isinstance(recommendations['recommended'], list):
            raise ValueError("'recommended' must be a list")

        if len(recommendations['recommended']) != 2:
            raise ValueError(
                f"Expected exactly 2 recommendations, got {len(recommendations['recommended'])}"
            )

        # Enrich recommended strategies with stats
        for rec in recommendations['recommended']:
            if 'strategy_id' not in rec:
                raise ValueError("Recommendation missing 'strategy_id'")

            sid = rec['strategy_id']

            if sid < 0 or sid >= len(strategy_stats):
                raise ValueError(f"Invalid strategy_id: {sid}")

            # Add enrichment data
            rec['strategy_name'] = strategy_names[sid] if sid < len(strategy_names) else f"Strategy {sid}"
            rec['strategy_params'] = strategy_stats[sid]['params']
            rec['win_rate'] = strategy_stats[sid]['win_rate']
            rec['avg_position'] = strategy_stats[sid]['avg_position']

            # Ensure confidence exists
            if 'confidence' not in rec:
                rec['confidence'] = 0.75  # Default

        # Enrich avoid strategy
        avoid = recommendations['avoid']
        if 'strategy_id' not in avoid:
            raise ValueError("Avoid recommendation missing 'strategy_id'")

        sid = avoid['strategy_id']

        if sid < 0 or sid >= len(strategy_stats):
            raise ValueError(f"Invalid avoid strategy_id: {sid}")

        avoid['strategy_name'] = strategy_names[sid] if sid < len(strategy_names) else f"Strategy {sid}"
        avoid['strategy_params'] = strategy_stats[sid]['params']
        avoid['win_rate'] = strategy_stats[sid]['win_rate']
        avoid['avg_position'] = strategy_stats[sid]['avg_position']

        return recommendations

    def _fallback_recommendations(
        self,
        strategy_stats: List[dict],
        strategy_params: List[dict]
    ) -> dict:
        """
        Simple heuristic recommendations when Gemini unavailable.
        Ranks strategies by win rate.
        """

        strategy_names = ['Aggressive', 'Balanced', 'Conservative']

        # Sort strategies by win rate (descending)
        sorted_stats = sorted(
            enumerate(strategy_stats),
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )

        # Top 2 strategies
        top1_idx, top1_stats = sorted_stats[0]
        top2_idx, top2_stats = sorted_stats[1]
        worst_idx, worst_stats = sorted_stats[-1]

        return {
            'recommended': [
                {
                    'strategy_id': top1_stats['strategy_id'],
                    'strategy_name': strategy_names[top1_idx] if top1_idx < len(strategy_names) else f"Strategy {top1_idx}",
                    'strategy_params': top1_stats['params'],
                    'win_rate': top1_stats['win_rate'],
                    'avg_position': top1_stats['avg_position'],
                    'rationale': f"Highest win rate ({top1_stats['win_rate']:.1f}%) across 100 simulations. " +
                                f"Average finishing position: P{top1_stats['avg_position']:.1f}.",
                    'confidence': 0.90
                },
                {
                    'strategy_id': top2_stats['strategy_id'],
                    'strategy_name': strategy_names[top2_idx] if top2_idx < len(strategy_names) else f"Strategy {top2_idx}",
                    'strategy_params': top2_stats['params'],
                    'win_rate': top2_stats['win_rate'],
                    'avg_position': top2_stats['avg_position'],
                    'rationale': f"Second highest win rate ({top2_stats['win_rate']:.1f}%). " +
                                f"Safer alternative with {top2_stats['avg_final_battery']:.0f}% avg final battery.",
                    'confidence': 0.75
                }
            ],
            'avoid': {
                'strategy_id': worst_stats['strategy_id'],
                'strategy_name': strategy_names[worst_idx] if worst_idx < len(strategy_names) else f"Strategy {worst_idx}",
                'strategy_params': worst_stats['params'],
                'win_rate': worst_stats['win_rate'],
                'avg_position': worst_stats['avg_position'],
                'rationale': f"Lowest win rate ({worst_stats['win_rate']:.1f}%) in simulations. " +
                            f"Poor finishing position: P{worst_stats['avg_position']:.1f}.",
                'risk': f"Only {worst_stats['position_distribution']['wins']} wins out of 100 races. " +
                       f"{worst_stats['position_distribution']['outside_points']} finishes outside points."
            }
        }

    def _load_system_prompt(self) -> str:
        """Load system prompt from file or use default."""
        prompt_path = 'prompts/gemini_game_advisor_system.txt'

        if os.path.exists(prompt_path):
            with open(prompt_path, 'r') as f:
                return f.read()
        else:
            # Default system prompt if file doesn't exist
            return """You are an expert F1 race strategist providing real-time tactical advice during a live race.

CONTEXT:
- 2026 F1 regulations with 50/50 ICE/Electric power split (350kW MGU-K)
- Battery, tire, and fuel management are critical
- 6 strategic variables control car behavior

YOUR ROLE:
The driver has paused the race at a critical decision point. You have simulation data for 3 possible strategies (100 races each).

YOUR TASK:
1. Recommend the TOP 2 strategies with highest success probability
2. Identify the WORST 1 strategy to AVOID
3. Be DECISIVE and ACTIONABLE - output ONLY valid JSON

Consider race context, current position, resource states, and strategic implications of the current event."""


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def quick_analyze(
    sim_results: pd.DataFrame,
    race_context: dict,
    strategy_params: List[dict]
) -> dict:
    """
    Convenience function for quick analysis.

    Usage:
        from api.gemini_game_advisor import quick_analyze

        recommendations = quick_analyze(sim_df, context, strategies)
    """
    advisor = GameAdvisor()
    return advisor.analyze_decision_point(sim_results, race_context, strategy_params)
