def create_agents():
    """Create list of racing agents with different strategies"""
    return [
        'Conservative',
        'Aggressive', 
        'Balanced',
        'Opportunist',
        'Defensive',
        'Risk_Taker',
        'Adaptive'
    ]

class AdaptiveAI:
    """Adaptive AI agent that uses playbook rules"""
    
    def __init__(self, name: str, config: dict, playbook: dict):
        self.name = name
        self.config = config
        self.playbook = playbook
        self.strategy = "adaptive"
    
    def get_strategy(self, state: dict) -> dict:
        """Get strategy based on current race state and playbook"""
        # This would contain the logic to apply playbook rules
        # For now, return a balanced default
        return {
            'deploy_straight': 60,
            'deploy_corner': 50,
            'harvest': 55
        }
    
    def __str__(self):
        return self.name