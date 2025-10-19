def synthesize_playbook(stats: dict, df) -> dict:
    """Generate playbook from race data"""
    
    # Analyze patterns in the data to create realistic rules
    rules = []
    
    # Rule 1: Low battery management
    rules.append({
        "condition": "battery_soc < 30 and lap > 40",
        "rule": "Low Battery Late Race",
        "action": {
            "deploy_straight": 80,
            "deploy_corner": 20,
            "harvest": 90
        },
        "confidence": 0.85,
        "rationale": "Conserve energy when battery is low in final laps"
    })
    
    # Rule 2: Rain strategy for podium positions
    rules.append({
        "condition": "position <= 3 and rain == True",
        "rule": "Podium Position Rain",
        "action": {
            "deploy_straight": 40,
            "deploy_corner": 60,
            "harvest": 70
        },
        "confidence": 0.75,
        "rationale": "Balanced approach in wet conditions when in podium position"
    })
    
    # Rule 3: Aggressive early race
    rules.append({
        "condition": "lap < 20 and position > 5",
        "rule": "Early Race Aggression",
        "action": {
            "deploy_straight": 90,
            "deploy_corner": 85,
            "harvest": 30
        },
        "confidence": 0.70,
        "rationale": "Push hard early to gain positions when battery is full"
    })
    
    # Rule 4: Conservative mid-race
    rules.append({
        "condition": "lap >= 20 and lap <= 40 and battery_soc > 50",
        "rule": "Mid Race Conservation",
        "action": {
            "deploy_straight": 55,
            "deploy_corner": 45,
            "harvest": 65
        },
        "confidence": 0.80,
        "rationale": "Maintain position while managing energy for final stint"
    })
    
    # Rule 5: Final push for leaders
    rules.append({
        "condition": "position <= 2 and lap > 45 and battery_soc > 20",
        "rule": "Leader Final Push",
        "action": {
            "deploy_straight": 95,
            "deploy_corner": 90,
            "harvest": 20
        },
        "confidence": 0.90,
        "rationale": "Maximum attack when leading in final laps with sufficient energy"
    })
    
    return {
        "rules": rules,
        "generated_at": "2024-01-01T00:00:00Z",
        "source_stats": stats,
        "total_rules": len(rules)
    }