"""
Precompute Lookup Table for Fast Recommendations

Generates a lookup table of AdaptiveAI decisions for common race states.
This enables R2's /recommend endpoint to provide instant recommendations
without evaluating playbook conditions every time.

Target latency: <1.5 seconds for recommendations (P95)
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim.agents import AdaptiveAI
from sim.engine import RaceState


def load_playbook(playbook_path='data/playbook_test.json'):
    """
    Load playbook from JSON file.

    Args:
        playbook_path: Path to playbook JSON file

    Returns:
        Playbook dict, or empty dict if file not found
    """
    try:
        with open(playbook_path, 'r') as f:
            playbook = json.load(f)
            return playbook
    except FileNotFoundError:
        print(f"⚠️  No playbook found at {playbook_path}")
        print("   Skipping lookup table generation")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parsing playbook: {e}")
        print("   Skipping lookup table generation")
        return None


def generate_lookup_table(playbook, playbook_path='data/playbook_test.json'):
    """
    Generate lookup table for common race states.

    Grid searches across:
    - Laps: [10, 20, 30, 40, 50]
    - Battery SOC: [20, 40, 60, 80]
    - Position: [1, 3, 5, 10]

    Total: 5 × 4 × 4 = 80 state combinations

    Args:
        playbook: Playbook dict with rules
        playbook_path: Path where playbook was loaded from

    Returns:
        Dictionary mapping state keys to decisions
    """
    print("=" * 70)
    print("PRECOMPUTING LOOKUP TABLE")
    print("=" * 70)

    print(f"\nLoaded playbook from: {playbook_path}")
    print(f"Number of rules: {len(playbook.get('rules', []))}")

    # Create AdaptiveAI instance with playbook
    adaptive = AdaptiveAI("Lookup_Generator", {}, playbook)

    # Grid search parameters
    laps = [10, 20, 30, 40, 50]
    batteries = [20, 40, 60, 80]
    positions = [1, 3, 5, 10]

    total_states = len(laps) * len(batteries) * len(positions)

    print(f"\nGenerating decisions for {total_states} common states...")
    print(f"  Laps: {laps}")
    print(f"  Battery SOC: {batteries}")
    print(f"  Positions: {positions}")
    print()

    # Generate lookup table
    lookup = {}
    count = 0

    for lap in laps:
        for battery in batteries:
            for position in positions:
                # Create race state
                state = RaceState(
                    lap=lap,
                    battery_soc=float(battery),
                    position=position,
                    tire_age=lap,  # Assume tire age = lap (reasonable approximation)
                    boost_used=0   # Assume no boost used yet
                )

                # Get decision from AdaptiveAI
                decision = adaptive.decide(state)

                # Store in lookup with composite key
                key = f"{lap}_{battery}_{position}"
                lookup[key] = decision

                count += 1

                # Progress indicator
                if count % 20 == 0 or count == total_states:
                    progress = (count / total_states) * 100
                    print(f"  Progress: {count}/{total_states} states ({progress:.0f}%)")

    # Add metadata
    lookup_with_metadata = {
        "states": lookup,
        "metadata": {
            "total_states": total_states,
            "grid_params": {
                "laps": laps,
                "batteries": batteries,
                "positions": positions
            },
            "playbook_source": playbook_path,
            "generated_for": "R2 recommendation engine /recommend endpoint"
        }
    }

    return lookup_with_metadata


def main():
    """Generate and save lookup table"""
    # Load playbook
    playbook_path = 'data/playbook_test.json'
    playbook = load_playbook(playbook_path)

    if playbook is None:
        print("\n❌ Cannot generate lookup table without playbook")
        sys.exit(1)

    # Generate lookup table
    lookup_data = generate_lookup_table(playbook, playbook_path)

    # Save to JSON
    output_path = 'data/lookup.json'
    os.makedirs('data', exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(lookup_data, f, indent=2)

    # Display summary
    num_states = lookup_data['metadata']['total_states']
    print("\n" + "=" * 70)
    print("LOOKUP TABLE GENERATED")
    print("=" * 70)
    print(f"\n✅ Precomputed {num_states} state mappings")
    print(f"   Saved to: {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")

    # Example usage
    print(f"\nExample usage (lap=30, battery=60%, position=3):")
    example_key = "30_60_3"
    example_decision = lookup_data['states'][example_key]
    print(f"  Key: '{example_key}'")
    print(f"  Decision: {example_decision}")

    print("\n" + "=" * 70)
    print("Ready for R2's /recommend endpoint!")
    print("=" * 70)

    sys.exit(0)


if __name__ == "__main__":
    main()
