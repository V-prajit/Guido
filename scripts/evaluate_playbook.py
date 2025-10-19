#!/usr/bin/env python3
"""Playbook quality evaluation"""

import json
import sys
import os

def evaluate_playbook(playbook_path='data/playbook.json'):
    print(f"\n{'='*60}")
    print(f"PLAYBOOK EVALUATION")
    print(f"{'='*60}\n")

    try:
        with open(playbook_path, 'r') as f:
            playbook = json.load(f)
    except FileNotFoundError:
        print(f"❌ Not found: {playbook_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False

    rules = playbook.get('rules', [])

    print(f"Rules: {len(rules)}")
    print(f"Generated: {playbook.get('generated_at', 'unknown')}")
    print(f"Model: {playbook.get('model', 'unknown')}")
    print(f"Fallback: {playbook.get('fallback', False)}")
    print(f"Simulations: {playbook.get('num_simulations', 0)}\n")

    if len(rules) < 3 or len(rules) > 10:
        print(f"⚠️  Rule count unusual: {len(rules)} (expect 5-7)")

    issues = []

    for i, rule in enumerate(rules, 1):
        print(f"\n--- Rule {i}: {rule.get('rule', 'UNNAMED')} ---")

        if 'condition' not in rule:
            issues.append(f"Rule {i}: Missing condition")
            continue

        condition = rule['condition']
        print(f"  Condition: {condition}")

        try:
            test_state = {'battery_soc': 50, 'lap': 30, 'position': 3}
            result = eval(condition, {"__builtins__": {}}, test_state)
            if isinstance(result, bool):
                print(f"  ✓ Valid Python")
            else:
                issues.append(f"Rule {i}: Condition not boolean")
        except Exception as e:
            issues.append(f"Rule {i}: Invalid - {e}")
            print(f"  ✗ Error: {e}")

        if 'action' not in rule:
            issues.append(f"Rule {i}: Missing action")
            continue

        action = rule['action']
        for key in ['deploy_straight', 'deploy_corner', 'harvest']:
            if key not in action:
                issues.append(f"Rule {i}: Missing {key}")
            else:
                val = action[key]
                if not (0 <= val <= 100):
                    issues.append(f"Rule {i}: {key}={val} out of range")

        if 'rationale' in rule:
            rat = rule['rationale']
            if len(rat) > 200:
                issues.append(f"Rule {i}: Rationale too long ({len(rat)})")
            print(f"  Rationale: {rat[:70]}...")
        else:
            issues.append(f"Rule {i}: Missing rationale")

        if 'confidence' in rule:
            conf = rule['confidence']
            if not (0 <= conf <= 1):
                issues.append(f"Rule {i}: Confidence {conf} invalid")
            print(f"  Confidence: {conf:.2f}")
        else:
            issues.append(f"Rule {i}: Missing confidence")

        if 'uplift_win_pct' in rule:
            print(f"  Uplift: {rule['uplift_win_pct']:.1f}%")
        else:
            issues.append(f"Rule {i}: Missing uplift_win_pct")

    print(f"\n{'='*60}")
    if issues:
        print(f"⚠️  {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Playbook valid")

    if rules:
        avg_conf = sum(r.get('confidence', 0) for r in rules) / len(rules)
        avg_uplift = sum(r.get('uplift_win_pct', 0) for r in rules) / len(rules)
        print(f"\nAvg confidence: {avg_conf:.2f}")
        print(f"Avg uplift: {avg_uplift:.1f}%")

    print(f"{'='*60}\n")
    return len(issues) == 0

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/playbook.json'

    if not os.path.exists(path):
        print(f"Trying: data/playbook_test.json")
        path = 'data/playbook_test.json'

    success = evaluate_playbook(path)
    sys.exit(0 if success else 1)
