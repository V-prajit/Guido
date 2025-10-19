#!/usr/bin/env python3
import json
import os
import sys

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def generate_summary():
    print("\n" + "="*60)
    print("STRATEGY GYM 2026 - FINAL SUMMARY")
    print("="*60 + "\n")

    playbook = load_json('data/playbook.json')
    validation = load_json('data/validation.json')
    perf = load_json('data/perf.json')

    if not playbook:
        print("❌ No playbook found. Run: python scripts/generate_playbook.py")
        return None

    rules = playbook.get('rules', [])
    num_sims = playbook.get('num_simulations', 0)
    model = playbook.get('model', 'unknown')
    fallback = playbook.get('fallback', False)

    print(f"📊 SIMULATION")
    print(f"   Scenarios: {num_sims} races")
    print(f"   Model: {model}")
    print(f"   Fallback: {fallback}")

    print(f"\n📘 PLAYBOOK")
    print(f"   Rules: {len(rules)}")

    if rules:
        avg_conf = sum(r.get('confidence', 0) for r in rules) / len(rules)
        avg_uplift = sum(r.get('uplift_win_pct', 0) for r in rules) / len(rules)
        print(f"   Avg Confidence: {avg_conf:.2f}")
        print(f"   Avg Uplift: {avg_uplift:.1f}%")

    if validation:
        print(f"\n✅ VALIDATION")
        print(f"   Win Rate: {validation.get('adaptive_win_rate', 0):.1f}%")
        print(f"   Wins: {validation.get('adaptive_wins', 0)}/{validation.get('num_scenarios', 0)}")
        print(f"   Median Baseline: {validation.get('median_baseline_rate', 0):.1f}%")
        print(f"   Status: {'PASSED' if validation.get('passed') else 'FAILED'}")

        rule_usage = validation.get('rule_usage', {})
        if rule_usage:
            print(f"\n📈 RULE USAGE")
            total = rule_usage.get('total_decisions', 0)
            print(f"   Total Decisions: {total}")

            rules_data = rule_usage.get('rules', {})
            sorted_rules = sorted(rules_data.items(), key=lambda x: -x[1]['count'])

            for i, (name, data) in enumerate(sorted_rules[:3], 1):
                print(f"   {i}. {name}: {data['count']} times ({data['percentage']:.1f}%)")

    if perf:
        print(f"\n⚡ PERFORMANCE")
        if 'scenarios_per_sec' in perf:
            print(f"   Speed: {perf['scenarios_per_sec']:.1f} scenarios/sec")

    summary = {
        'simulations': num_sims,
        'rules_count': len(rules),
        'model': model,
        'fallback': fallback,
        'validation_win_rate': validation.get('adaptive_win_rate', 0) if validation else 0,
        'validation_passed': validation.get('passed', False) if validation else False,
        'avg_confidence': round(avg_conf, 2) if rules else 0,
        'avg_uplift': round(avg_uplift, 1) if rules else 0
    }

    if validation and validation.get('rule_usage'):
        summary['rule_usage'] = validation['rule_usage']

    with open('data/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n💾 Saved to: data/summary.json")
    print("="*60 + "\n")

    return summary

if __name__ == '__main__':
    generate_summary()
