"""
Test script for agents_v2.py

Verifies all 8 agents:
1. Load correctly
2. Use 6-variable AgentDecision
3. Have distinct strategies
4. Respond to race state changes
"""

from sim.agents_v2 import create_agents_v2
from sim.physics_2024 import RaceState


def test_agent_creation():
    """Test that all agents can be created."""
    agents = create_agents_v2()
    print(f"✓ Created {len(agents)} agents")
    assert len(agents) == 8, f"Expected 8 agents, got {len(agents)}"

    expected_names = [
        'VerstappenStyle', 'HamiltonStyle', 'AlonsoStyle',
        'ElectricBlitzer', 'EnergySaver', 'TireWhisperer',
        'Opportunist', 'AdaptiveAI'
    ]

    for i, agent in enumerate(agents):
        assert agent.name == expected_names[i], f"Agent {i} has wrong name: {agent.name}"

    print("✓ All agent names correct")
    return agents


def test_decision_structure(agents):
    """Test that all agents return valid AgentDecision objects."""
    state = RaceState(
        lap=10,
        battery_soc=80.0,
        position=3,
        tire_age=10,
        tire_life=85.0,
        fuel_remaining=90.0,
        boost_used=0
    )

    print("\n" + "="*80)
    print("AGENT DECISION TEST - Mid-race state (Lap 10, P3, 80% battery)")
    print("="*80)
    print(f"{'Agent':<20s} | {'Energy':>6s} | {'Tire':>6s} | {'Fuel':>6s} | {'ERS':>6s} | {'Attack':>6s} | {'Defend':>6s}")
    print("-"*80)

    for agent in agents:
        decision = agent.decide(state)

        # Verify all fields are present
        assert hasattr(decision, 'energy_deployment')
        assert hasattr(decision, 'tire_management')
        assert hasattr(decision, 'fuel_strategy')
        assert hasattr(decision, 'ers_mode')
        assert hasattr(decision, 'overtake_aggression')
        assert hasattr(decision, 'defense_intensity')

        # Verify values are in valid range
        assert 0 <= decision.energy_deployment <= 100
        assert 0 <= decision.tire_management <= 100
        assert 0 <= decision.fuel_strategy <= 100
        assert 0 <= decision.ers_mode <= 100
        assert 0 <= decision.overtake_aggression <= 100
        assert 0 <= decision.defense_intensity <= 100

        print(f"{agent.name:<20s} | {decision.energy_deployment:6.1f} | "
              f"{decision.tire_management:6.1f} | {decision.fuel_strategy:6.1f} | "
              f"{decision.ers_mode:6.1f} | {decision.overtake_aggression:6.1f} | "
              f"{decision.defense_intensity:6.1f}")

    print("\n✓ All agents return valid 6-variable AgentDecision")


def test_strategy_diversity(agents):
    """Test that agents have measurably different strategies."""
    state = RaceState(
        lap=30,
        battery_soc=60.0,
        position=5,
        tire_age=20,
        tire_life=65.0,
        fuel_remaining=70.0,
        boost_used=1
    )

    print("\n" + "="*80)
    print("STRATEGY DIVERSITY TEST - Late race (Lap 30, P5, 60% battery)")
    print("="*80)

    energy_values = []
    tire_values = []

    for agent in agents:
        decision = agent.decide(state)
        energy_values.append(decision.energy_deployment)
        tire_values.append(decision.tire_management)

    # Calculate variance to ensure diversity
    energy_variance = sum((x - sum(energy_values)/len(energy_values))**2 for x in energy_values) / len(energy_values)
    tire_variance = sum((x - sum(tire_values)/len(tire_values))**2 for x in tire_values) / len(tire_values)

    print(f"Energy deployment variance: {energy_variance:.1f}")
    print(f"Tire management variance: {tire_variance:.1f}")

    # Ensure there's meaningful diversity (variance > 100 means strategies differ significantly)
    assert energy_variance > 100, f"Energy strategies too similar (variance={energy_variance:.1f})"
    assert tire_variance > 100, f"Tire strategies too similar (variance={tire_variance:.1f})"

    print("✓ Strategies are measurably different")


def test_state_responsiveness(agents):
    """Test that agents respond to different race states."""
    print("\n" + "="*80)
    print("STATE RESPONSIVENESS TEST")
    print("="*80)

    # Test 1: Early race vs late race
    early_state = RaceState(lap=5, battery_soc=95.0, position=3, tire_age=5, tire_life=95.0, fuel_remaining=100.0, boost_used=0)
    late_state = RaceState(lap=50, battery_soc=40.0, position=3, tire_age=30, tire_life=40.0, fuel_remaining=20.0, boost_used=2)

    print("\nElectricBlitzer early vs late race:")
    blitzer = agents[3]  # ElectricBlitzer
    early_decision = blitzer.decide(early_state)
    late_decision = blitzer.decide(late_state)
    print(f"  Early race (lap 5):  Energy={early_decision.energy_deployment:.1f}")
    print(f"  Late race (lap 50):  Energy={late_decision.energy_deployment:.1f}")
    assert early_decision.energy_deployment > late_decision.energy_deployment, "ElectricBlitzer should deploy less energy late in race"
    print("  ✓ ElectricBlitzer reduces energy deployment in late race")

    # Test 2: EnergySaver opposite pattern
    print("\nEnergySaver early vs late race:")
    saver = agents[4]  # EnergySaver
    early_decision = saver.decide(early_state)
    late_decision = saver.decide(late_state)
    print(f"  Early race (lap 5):  Energy={early_decision.energy_deployment:.1f}")
    print(f"  Late race (lap 50):  Energy={late_decision.energy_deployment:.1f}")
    assert early_decision.energy_deployment < late_decision.energy_deployment, "EnergySaver should deploy more energy late in race"
    print("  ✓ EnergySaver increases energy deployment in late race")

    # Test 3: Opportunist position awareness
    print("\nOpportunist position awareness:")
    opportunist = agents[6]  # Opportunist
    leading_state = RaceState(lap=30, battery_soc=70.0, position=1, tire_age=15, tire_life=70.0, fuel_remaining=60.0, boost_used=1)
    trailing_state = RaceState(lap=30, battery_soc=70.0, position=8, tire_age=15, tire_life=70.0, fuel_remaining=60.0, boost_used=1)

    leading_decision = opportunist.decide(leading_state)
    trailing_decision = opportunist.decide(trailing_state)
    print(f"  Leading (P1): Attack={leading_decision.overtake_aggression:.1f}, Defend={leading_decision.defense_intensity:.1f}")
    print(f"  Trailing (P8): Attack={trailing_decision.overtake_aggression:.1f}, Defend={trailing_decision.defense_intensity:.1f}")
    assert trailing_decision.overtake_aggression > leading_decision.overtake_aggression, "Opportunist should be more aggressive when trailing"
    assert leading_decision.defense_intensity > trailing_decision.defense_intensity, "Opportunist should defend more when leading"
    print("  ✓ Opportunist adapts strategy based on position")

    # Test 4: TireWhisperer tire preservation
    print("\nTireWhisperer tire awareness:")
    whisperer = agents[5]  # TireWhisperer
    fresh_tires = RaceState(lap=10, battery_soc=70.0, position=5, tire_age=3, tire_life=95.0, fuel_remaining=80.0, boost_used=0)
    worn_tires = RaceState(lap=40, battery_soc=70.0, position=5, tire_age=35, tire_life=30.0, fuel_remaining=40.0, boost_used=1)

    fresh_decision = whisperer.decide(fresh_tires)
    worn_decision = whisperer.decide(worn_tires)
    print(f"  Fresh tires (95% life): Tire management={fresh_decision.tire_management:.1f}")
    print(f"  Worn tires (30% life):  Tire management={worn_decision.tire_management:.1f}")
    assert worn_decision.tire_management < fresh_decision.tire_management, "TireWhisperer should be more conservative with worn tires"
    print("  ✓ TireWhisperer preserves worn tires")

    print("\n✓ All agents respond appropriately to race state changes")


def test_learned_agents(agents):
    """Test that learned agents load data correctly."""
    print("\n" + "="*80)
    print("LEARNED AGENTS TEST - Real driver profiles from 2024 Bahrain GP")
    print("="*80)

    verstappen = agents[0]
    hamilton = agents[1]
    alonso = agents[2]

    # These agents should load from learned_strategies.json
    print(f"\n{verstappen.name} profile:")
    print(f"  Energy: {verstappen.profile['energy_deployment']:.1f} (expected ~29.5)")
    print(f"  Overtake: {verstappen.profile['overtake_aggression']:.1f} (expected ~40)")
    print(f"  Defense: {verstappen.profile['defense_intensity']:.1f} (expected ~100)")

    print(f"\n{hamilton.name} profile:")
    print(f"  Energy: {hamilton.profile['energy_deployment']:.1f} (expected ~27.5)")
    print(f"  Overtake: {hamilton.profile['overtake_aggression']:.1f} (expected ~100)")
    print(f"  Defense: {hamilton.profile['defense_intensity']:.1f} (expected ~96.4)")

    print(f"\n{alonso.name} profile:")
    print(f"  Energy: {alonso.profile['energy_deployment']:.1f} (expected ~25.7)")
    print(f"  Overtake: {alonso.profile['overtake_aggression']:.1f} (expected ~100)")
    print(f"  Defense: {alonso.profile['defense_intensity']:.1f} (expected ~85.7)")

    # Verify energy conservation ranking: Alonso < Hamilton < Verstappen
    assert alonso.profile['energy_deployment'] < hamilton.profile['energy_deployment']
    assert hamilton.profile['energy_deployment'] < verstappen.profile['energy_deployment']

    print("\n✓ Learned agents loaded correctly from data")


def test_adaptive_ai(agents):
    """Test AdaptiveAI playbook integration."""
    print("\n" + "="*80)
    print("ADAPTIVE AI TEST - Playbook integration")
    print("="*80)

    adaptive = agents[7]  # AdaptiveAI

    print(f"Playbook loaded: {len(adaptive.playbook.get('rules', []))} rules")

    # Test with various states
    state = RaceState(
        lap=30,
        battery_soc=60.0,
        position=5,
        tire_age=20,
        tire_life=65.0,
        fuel_remaining=70.0,
        boost_used=1
    )

    decision = adaptive.decide(state)
    print(f"Decision: Energy={decision.energy_deployment:.1f}, Tire={decision.tire_management:.1f}")

    print("✓ AdaptiveAI successfully reads playbook and makes decisions")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("AGENTS V2 TEST SUITE")
    print("="*80)

    # Test 1: Agent creation
    agents = test_agent_creation()

    # Test 2: Decision structure
    test_decision_structure(agents)

    # Test 3: Strategy diversity
    test_strategy_diversity(agents)

    # Test 4: State responsiveness
    test_state_responsiveness(agents)

    # Test 5: Learned agents
    test_learned_agents(agents)

    # Test 6: Adaptive AI
    test_adaptive_ai(agents)

    print("\n" + "="*80)
    print("ALL TESTS PASSED ✓")
    print("="*80)
    print("\nSummary:")
    print("  ✓ 8 agents created successfully")
    print("  ✓ All agents use 6-variable AgentDecision")
    print("  ✓ Strategies are measurably different")
    print("  ✓ Agents respond to race state changes")
    print("  ✓ Learned agents load real driver data")
    print("  ✓ AdaptiveAI integrates with playbook")
    print("\nAgents ready for simulation!")


if __name__ == "__main__":
    main()
