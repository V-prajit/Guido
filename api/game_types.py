"""
Game WebSocket Message Types
Pydantic models for WebSocket message validation.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict


# ==========================================
# CLIENT → SERVER MESSAGES
# ==========================================

class StartGameMessage(BaseModel):
    """Client requests to start a new game"""
    type: str = "START_GAME"
    player_name: str = "Player"
    total_laps: int = 57
    rain_lap: Optional[int] = None
    safety_car_lap: Optional[int] = None


class SelectStrategyMessage(BaseModel):
    """Client selects a strategy during decision point"""
    type: str = "SELECT_STRATEGY"
    strategy_id: int  # 0, 1, or 2


class AdvanceLapMessage(BaseModel):
    """Client requests to advance to next lap (for manual control)"""
    type: str = "ADVANCE_LAP"


# ==========================================
# SERVER → CLIENT MESSAGES
# ==========================================

class PlayerStateData(BaseModel):
    """Player car state"""
    position: int
    battery_soc: float
    tire_life: float
    fuel_remaining: float
    lap_time: float
    cumulative_time: float
    energy_deployment: float
    tire_management: float
    fuel_strategy: float
    ers_mode: float
    overtake_aggression: float
    defense_intensity: float


class OpponentStateData(BaseModel):
    """Opponent car state"""
    name: str
    agent_type: str
    position: int
    lap_progress: float
    battery_soc: float
    tire_life: float
    fuel_remaining: float
    cumulative_time: float


class RaceStartedMessage(BaseModel):
    """Server confirms race has started"""
    type: str = "RACE_STARTED"
    session_id: str
    total_laps: int
    player: PlayerStateData
    opponents: List[OpponentStateData]


class LapUpdateMessage(BaseModel):
    """Server sends lap-by-lap update"""
    type: str = "LAP_UPDATE"
    lap: int
    player: PlayerStateData
    opponents: List[OpponentStateData]
    is_raining: bool
    safety_car_active: bool


class StrategyRecommendation(BaseModel):
    """Single strategy recommendation"""
    strategy_id: int
    strategy_name: str
    win_rate: float
    avg_position: float
    rationale: str
    confidence: float
    strategy_params: Dict[str, float]


class StrategyToAvoid(BaseModel):
    """Strategy to avoid"""
    strategy_id: int
    strategy_name: str
    win_rate: float
    rationale: str
    risk: str
    strategy_params: Dict[str, float]


class DecisionPointMessage(BaseModel):
    """Server requests player decision"""
    type: str = "DECISION_POINT"
    event_type: str
    lap: int
    position: int
    battery_soc: float
    tire_life: float
    fuel_remaining: float
    recommended: List[StrategyRecommendation]
    avoid: Optional[StrategyToAvoid] = None
    latency_ms: float
    used_fallback: bool


class RaceCompleteMessage(BaseModel):
    """Server notifies race is complete"""
    type: str = "RACE_COMPLETE"
    final_position: int
    player: PlayerStateData
    opponents: List[OpponentStateData]
    decision_count: int
    race_summary: Dict


class ErrorMessage(BaseModel):
    """Server sends error"""
    type: str = "ERROR"
    message: str
    details: Optional[str] = None
