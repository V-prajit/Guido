# API Contracts

## POST /run
Input: {num_scenarios: int, num_agents: int, repeats: int}
Output: {run_id: str, scenarios_completed: int, csv_path: str}

## POST /analyze
Input: {} (reads latest CSV)
Output: {stats: dict, playbook_preview: dict}

## GET /playbook
Output: {rules: [], generated_at: str, num_simulations: int}

## POST /recommend
Input: {lap: int, battery_soc: float, position: int, rain: bool}
Output: {recommendations: [], latency_ms: float}
