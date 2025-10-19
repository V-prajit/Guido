import ast
import json
import os
import time
import random
from fastapi import HTTPException

# AST whitelist for safe evaluation
ALLOWED_NODES = {
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
    ast.Compare, ast.Name, ast.Load, ast.Constant, 
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod
}

# Support for older Python versions
try:
    ALLOWED_NODES.update({ast.Num, ast.Str})
except AttributeError:
    pass  # Python 3.8+ uses ast.Constant

def safe_eval_condition(condition: str, context: dict) -> bool:
    """Safely evaluate condition using AST parsing"""
    try:
        tree = ast.parse(condition, mode='eval')
        
        # Check all nodes are whitelisted
        for node in ast.walk(tree):
            if type(node) not in ALLOWED_NODES:
                raise ValueError(f"Unsafe node type: {type(node).__name__}")
        
        # Compile and evaluate
        code = compile(tree, '<condition>', 'eval')
        return bool(eval(code, {"__builtins__": {}}, context))
    except Exception as e:
        print(f"Condition evaluation failed: {condition}, error: {e}")
        return False

def get_recommendations_fast(state: dict):
    """Fast recommendation with transparency"""
    if not os.path.exists('data/playbook.json'):
        raise HTTPException(status_code=404, detail="No playbook available")
    
    with open('data/playbook.json', 'r') as f:
        playbook = json.load(f)
    
    recommendations = []
    conditions_evaluated = []
    seed = random.randint(1000, 9999)
    
    for rule in playbook.get('rules', []):
        condition = rule['condition']
        matched = safe_eval_condition(condition, state)
        conditions_evaluated.append({"condition": condition, "matched": matched})
        
        if matched:
            recommendations.append({
                'rule': rule['rule'],
                'action': rule['action'],
                'confidence': rule['confidence'],
                'rationale': rule['rationale']
            })
    
    # Default fallback if no conditions matched
    if not recommendations:
        recommendations = [{
            'rule': 'Balanced Default',
            'action': {
                'deploy_straight': 60, 
                'deploy_corner': 50, 
                'harvest': 50
            },
            'confidence': 0.5,
            'rationale': 'No conditions matched, using default balanced strategy'
        }]
    
    return recommendations, conditions_evaluated, seed