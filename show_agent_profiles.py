"""
Display all agent strategy profiles in a comparison table
"""

from sim.agents_v2 import create_agents_v2


def main():
    agents = create_agents_v2()

    print("\n" + "="*100)
    print("AGENT STRATEGY PROFILES - BASE CONFIGURATIONS")
    print("="*100)
    print(f"\n{'Agent':<20s} | {'Energy':>7s} | {'Tire':>7s} | {'Fuel':>7s} | {'ERS':>7s} | {'Attack':>7s} | {'Defend':>7s}")
    print("-"*100)

    for agent in agents:
        profile = agent.profile
        print(f"{agent.name:<20s} | "
              f"{profile.get('energy_deployment', 0):7.1f} | "
              f"{profile.get('tire_management', 0):7.1f} | "
              f"{profile.get('fuel_strategy', 0):7.1f} | "
              f"{profile.get('ers_mode', 0):7.1f} | "
              f"{profile.get('overtake_aggression', 0):7.1f} | "
              f"{profile.get('defense_intensity', 0):7.1f}")

    print("\n" + "="*100)
    print("AGENT CATEGORIES")
    print("="*100)

    print("\n🏎️  LEARNED AGENTS (from 2024 Bahrain GP):")
    print("   1. VerstappenStyle  - P1 winner, defensive, efficient energy")
    print("   2. HamiltonStyle    - P7, 8 overtakes, race craft specialist")
    print("   3. AlonsoStyle      - P9, 10 overtakes, midfield master")

    print("\n⚡ SYNTHETIC AGENTS (strategic diversity):")
    print("   4. ElectricBlitzer  - Deploy early, build gap, fade late")
    print("   5. EnergySaver      - Conserve early, attack late")
    print("   6. TireWhisperer    - Preserve tires, one-stop specialist")
    print("   7. Opportunist      - Adapt to position (attack when behind)")
    print("   8. AdaptiveAI       - Playbook-powered, learns from simulations")

    print("\n" + "="*100)
    print("KEY INSIGHTS")
    print("="*100)

    print("\n📊 Energy Management Rankings (lowest = most efficient):")
    energy_agents = [(agent.name, agent.profile['energy_deployment']) for agent in agents]
    energy_agents.sort(key=lambda x: x[1])
    for i, (name, energy) in enumerate(energy_agents, 1):
        print(f"   {i}. {name:<20s} {energy:5.1f}")

    print("\n🏁 Overtake Aggression Rankings (highest = most aggressive):")
    overtake_agents = [(agent.name, agent.profile['overtake_aggression']) for agent in agents]
    overtake_agents.sort(key=lambda x: x[1], reverse=True)
    for i, (name, aggression) in enumerate(overtake_agents, 1):
        print(f"   {i}. {name:<20s} {aggression:5.1f}")

    print("\n🛡️  Defense Intensity Rankings (highest = strongest defense):")
    defense_agents = [(agent.name, agent.profile['defense_intensity']) for agent in agents]
    defense_agents.sort(key=lambda x: x[1], reverse=True)
    for i, (name, defense) in enumerate(defense_agents, 1):
        print(f"   {i}. {name:<20s} {defense:5.1f}")

    print("\n" + "="*100)


if __name__ == "__main__":
    main()
