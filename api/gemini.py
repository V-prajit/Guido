"""
Gemini AI Integration for Strategy Gym 2026
Synthesizes strategic playbooks from F1 simulation data.
"""

import os
import json
from typing import Dict
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def load_system_prompt() -> str:
    """Load the system prompt from file."""
    prompt_path = 'prompts/gemini_system.txt'
    with open(prompt_path, 'r') as f:
        return f.read()


def prepare_context(stats: Dict, df: pd.DataFrame) -> str:
    """Prepare analysis context for Gemini from simulation results."""

    low_battery = df[df['battery_soc'] < 30]
    med_battery = df[(df['battery_soc'] >= 30) & (df['battery_soc'] < 70)]
    high_battery = df[df['battery_soc'] >= 70]

    early_laps = df[df['lap'] < 20]
    mid_laps = df[(df['lap'] >= 20) & (df['lap'] < 45)]
    late_laps = df[df['lap'] >= 45]

    def safe_win_rate(data):
        if len(data) == 0:
            return 0.0
        return data['won'].mean() * 100

    context = f"""
AGENT PERFORMANCE SUMMARY:
{json.dumps(stats, indent=2)}

SITUATIONAL ANALYSIS:

Battery State Impact on Win Rate:
- Low Battery (<30%): {safe_win_rate(low_battery):.1f}% win rate ({len(low_battery)} observations)
- Medium Battery (30-70%): {safe_win_rate(med_battery):.1f}% win rate ({len(med_battery)} observations)
- High Battery (>70%): {safe_win_rate(high_battery):.1f}% win rate ({len(high_battery)} observations)

Race Phase Impact on Win Rate:
- Early Race (Laps 1-19): {safe_win_rate(early_laps):.1f}% win rate ({len(early_laps)} observations)
- Mid Race (Laps 20-44): {safe_win_rate(mid_laps):.1f}% win rate ({len(mid_laps)} observations)
- Late Race (Laps 45+): {safe_win_rate(late_laps):.1f}% win rate ({len(late_laps)} observations)

KEY INSIGHTS TO EXTRACT:
1. When should drivers deploy electric power aggressively vs conservatively?
2. What battery thresholds trigger strategy changes?
3. How does race phase affect optimal deployment?
4. What patterns separate winners from losers?

REQUIREMENTS:
- Generate 5-7 rules
- Each rule must have specific numeric thresholds
- Focus on multi-condition rules (use AND/OR logic where appropriate)
- Prioritize surprising or non-obvious insights
- Rules should be mutually exclusive or complementary (not contradictory)

Output ONLY the JSON object with rules array. No markdown, no explanation.
"""

    return context


def synthesize_playbook(stats: Dict, df: pd.DataFrame) -> Dict:
    """Use Gemini to synthesize strategic playbook from simulation results."""

    print("=" * 60)
    print("GEMINI PLAYBOOK SYNTHESIS")
    print("=" * 60)

    try:
        print("\n📋 Loading system prompt...")
        system_prompt = load_system_prompt()
        print(f"✅ Loaded system prompt ({len(system_prompt)} chars)")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return fallback_playbook(stats, df)

    print("\n📊 Preparing analysis context...")
    context = prepare_context(stats, df)
    print(f"✅ Context prepared ({len(context)} chars)")

    full_prompt = f"{system_prompt}\n\n{context}"

    try:
        print("\n🤖 Calling Gemini 2.0 Flash...")

        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000
            )
        )

        text = response.text.strip()
        print(f"📝 Response received ({len(text)} chars)")

        if text.startswith('```'):
            print("⚠️  Stripping markdown backticks...")
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()

        if text.endswith('```'):
            text = text[:-3].strip()

        print("\n🔍 Parsing JSON...")
        playbook_data = json.loads(text)

        if isinstance(playbook_data, list):
            rules = playbook_data
        elif isinstance(playbook_data, dict) and 'rules' in playbook_data:
            rules = playbook_data['rules']
        else:
            print("⚠️  Unexpected format")
            return fallback_playbook(stats, df)

        playbook = {
            "rules": rules,
            "generated_at": pd.Timestamp.now().isoformat(),
            "num_simulations": len(df),
            "model": "gemini-2.0-flash-exp"
        }

        if not playbook['rules'] or len(playbook['rules']) < 3:
            print(f"⚠️  Too few rules ({len(playbook['rules'])}), using fallback")
            return fallback_playbook(stats, df)

        print(f"✅ Synthesized {len(playbook['rules'])} rules")
        print("=" * 60)

        return playbook

    except json.JSONDecodeError as e:
        print(f"\n❌ JSON error: {e}")
        print(f"   Preview: {text[:200]}...")
        return fallback_playbook(stats, df)

    except Exception as e:
        print(f"\n❌ Synthesis failed: {type(e).__name__}: {e}")
        return fallback_playbook(stats, df)


def fallback_playbook(stats: Dict, df: pd.DataFrame) -> Dict:
    """Generate rule-based fallback playbook when Gemini unavailable."""

    print("\n" + "=" * 60)
    print("FALLBACK PLAYBOOK GENERATION")
    print("=" * 60)

    if not stats:
        best_agent = "Unknown"
        best_wins = 0
    else:
        best_agent = max(stats.items(), key=lambda x: x[1]['wins'])[0]
        best_wins = stats[best_agent]['wins']

    print(f"\n📊 Best performer: {best_agent} ({best_wins} wins)")

    rules = [
        {
            "rule": "Emergency Battery Conservation",
            "condition": "battery_soc < 20",
            "action": {
                "deploy_straight": 40,
                "deploy_corner": 35,
                "harvest": 80
            },
            "confidence": 0.92,
            "uplift_win_pct": 25.0,
            "rationale": "Critical low battery requires aggressive harvesting to prevent DNF"
        },
        {
            "rule": "Late Race Battery Conservation",
            "condition": "battery_soc < 30 and lap > 40",
            "action": {
                "deploy_straight": 50,
                "deploy_corner": 45,
                "harvest": 75
            },
            "confidence": 0.85,
            "uplift_win_pct": 18.0,
            "rationale": "Heavy harvesting when battery critical in late race prevents DNF"
        },
        {
            "rule": "Early Race Aggression",
            "condition": "lap < 15 and battery_soc > 70",
            "action": {
                "deploy_straight": 85,
                "deploy_corner": 70,
                "harvest": 30
            },
            "confidence": 0.70,
            "uplift_win_pct": 8.0,
            "rationale": "Deploy heavily early when battery full to gain track position"
        },
        {
            "rule": "Mid-Race Balance",
            "condition": "lap >= 20 and lap < 45 and battery_soc > 40",
            "action": {
                "deploy_straight": 65,
                "deploy_corner": 55,
                "harvest": 45
            },
            "confidence": 0.65,
            "uplift_win_pct": 5.0,
            "rationale": "Maintain steady pace while managing battery for late race"
        },
        {
            "rule": "Follow Top Performer Strategy",
            "condition": "battery_soc > 30",
            "action": {
                "deploy_straight": 60,
                "deploy_corner": 50,
                "harvest": 50
            },
            "confidence": 0.75,
            "uplift_win_pct": 12.0,
            "rationale": f"Balanced strategy based on {best_agent} performance"
        }
    ]

    playbook = {
        "rules": rules,
        "generated_at": pd.Timestamp.now().isoformat(),
        "num_simulations": len(df) if df is not None else 0,
        "fallback": True,
        "model": "rule-based-fallback",
        "note": "Gemini synthesis unavailable, using domain-knowledge fallback"
    }

    print(f"✅ Generated {len(rules)} fallback rules")
    print("=" * 60)

    return playbook


if __name__ == "__main__":
    print("Testing Gemini Integration")
    print("=" * 60)

    mock_stats = {
        'Electric_Blitz': {'wins': 150, 'avg_position': 3.2},
        'Energy_Saver': {'wins': 200, 'avg_position': 2.8},
        'Corner_Master': {'wins': 180, 'avg_position': 3.0}
    }

    mock_df = pd.DataFrame({
        'lap': [1, 30, 50] * 100,
        'battery_soc': [80, 50, 20] * 100,
        'agent': ['Electric_Blitz'] * 300,
        'position': [1, 2, 3] * 100,
        'won': [1, 0, 0] * 100
    })

    print(f"\nMock data: {len(mock_stats)} agents, {len(mock_df)} rows")

    playbook = synthesize_playbook(mock_stats, mock_df)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Rules: {len(playbook['rules'])}")
    print(f"Model: {playbook.get('model', 'unknown')}")
    print(f"Fallback: {playbook.get('fallback', False)}")

    if playbook['rules']:
        print(f"\nFirst rule: {playbook['rules'][0]['rule']}")
        print(f"Condition: {playbook['rules'][0]['condition']}")
