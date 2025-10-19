#!/usr/bin/env python3
import os
import sys
import subprocess

def print_header(title):
    print(f"\n{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}\n")

def run_command(cmd, description):
    print(f">>> {description}")
    print(f"$ {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        return False
    print(f"\n✅ Completed: {description}")
    return True

def main():
    print_header("END-TO-END VALIDATION PIPELINE")

    playbook_path = 'data/playbook.json'

    print(f"Step 1: Check for playbook at {playbook_path}")
    if not os.path.exists(playbook_path):
        print(f"⚠️  Playbook not found. Generating with 100 scenarios...\n")
        if not run_command(
            [sys.executable, 'scripts/generate_playbook.py', '100'],
            "Generate playbook"
        ):
            return 1
    else:
        print(f"✅ Playbook exists at {playbook_path}\n")

    print(f"\nStep 2: Run validation tests")
    if not run_command(
        [sys.executable, 'scripts/validate.py'],
        "Validate playbook performance"
    ):
        return 1

    print(f"\nStep 3: Evaluate playbook quality")
    if not run_command(
        [sys.executable, 'scripts/evaluate_playbook.py'],
        "Evaluate playbook structure"
    ):
        return 1

    print_header("VALIDATION PIPELINE COMPLETE")

    print("Summary:")
    print(f"  ✅ Playbook verified at {playbook_path}")
    print(f"  ✅ Performance validation passed")
    print(f"  ✅ Quality evaluation passed")
    print(f"\nResults saved to:")
    print(f"  - data/playbook.json")
    print(f"  - data/validation.json")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
