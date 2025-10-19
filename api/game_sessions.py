"""
Game Session Manager
Manages active game sessions with thread-safe state tracking and auto-cleanup.
"""

import uuid
import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from threading import Lock
import asyncio


@dataclass
class PlayerState:
    """Player car state"""
    position: int
    battery_soc: float  # 0-100
    tire_life: float    # 0-100
    fuel_remaining: float  # 0-100
    lap_time: float
    cumulative_time: float
    speed: float = 0.0  # Current speed (km/h) for visualization
    gap_to_leader: float = 0.0  # Time gap to race leader (seconds)
    lap_progress: float = 0.0  # Position on track 0-1 (normalized across full race)

    # Strategy parameters (6 variables)
    energy_deployment: float = 60.0
    tire_management: float = 70.0
    fuel_strategy: float = 65.0
    ers_mode: float = 60.0
    overtake_aggression: float = 50.0
    defense_intensity: float = 50.0


@dataclass
class OpponentState:
    """AI opponent state"""
    name: str
    agent_type: str
    position: int
    lap_progress: float  # 0-1 for visualization (based on cumulative_time relative to leader)
    battery_soc: float
    tire_life: float
    fuel_remaining: float
    cumulative_time: float
    speed: float = 0.0  # Current speed (km/h) for visualization
    gap_to_leader: float = 0.0  # Time gap to race leader (seconds)
    last_lap_time: float = 90.0  # Last lap time for speed calculation


@dataclass
class GameState:
    """Complete game state for a session"""
    session_id: str
    player_name: str
    current_lap: int
    total_laps: int
    is_paused: bool
    is_complete: bool

    # Race state
    player: PlayerState
    opponents: list[OpponentState] = field(default_factory=list)

    # Events
    rain_lap: Optional[int] = None
    safety_car_lap: Optional[int] = None
    is_raining: bool = False
    safety_car_active: bool = False

    # Decision tracking
    current_decision_point: Optional[dict] = None
    decision_history: list[dict] = field(default_factory=list)

    # Race control - pause/resume mechanism for decision points
    pause_event: Optional[asyncio.Event] = None

    # Metadata
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)


class GameSessionManager:
    """Manages active game sessions with thread-safe operations"""

    def __init__(self, max_session_age_minutes: int = 30):
        self.sessions: Dict[str, GameState] = {}
        self.lock = Lock()
        self.max_session_age = max_session_age_minutes * 60  # Convert to seconds

    def create_session(
        self,
        player_name: str = "Player",
        total_laps: int = 57,
        rain_lap: Optional[int] = None,
        safety_car_lap: Optional[int] = None
    ) -> str:
        """Create a new game session"""
        session_id = str(uuid.uuid4())

        # Initialize player state (EQUAL START - no grid advantage)
        player = PlayerState(
            position=0,  # Will be determined after first lap
            battery_soc=100.0,
            tire_life=100.0,
            fuel_remaining=100.0,
            lap_time=90.0,
            cumulative_time=0.0,  # Equal start
            speed=300.0,  # Starting speed (km/h)
            gap_to_leader=0.0,  # No gap at start
            lap_progress=0.0,  # Equal start on grid
            energy_deployment=60.0,
            tire_management=70.0,
            fuel_strategy=65.0,
            ers_mode=60.0,
            overtake_aggression=50.0,
            defense_intensity=50.0
        )

        # Initialize AI opponents (7 opponents) - EQUAL START
        opponents = []
        opponent_names = [
            ("VerstappenStyle", "Max Verstappen"),
            ("HamiltonStyle", "Lewis Hamilton"),
            ("AlonsoStyle", "Fernando Alonso"),
            ("AggressiveAttacker", "Charles Leclerc"),
            ("TireWhisperer", "Sergio Perez"),
            ("EnergyMaximizer", "Lando Norris"),
            ("BalancedRacer", "Oscar Piastri")
        ]

        for i, (agent_type, name) in enumerate(opponent_names):
            # EQUAL START: All cars start at cumulative_time=0.0
            # Positions will be determined naturally by lap times and strategy
            opponents.append(OpponentState(
                name=name,
                agent_type=agent_type,
                position=0,  # Will be determined after first lap
                lap_progress=0.0,  # Equal start on grid
                battery_soc=100.0,
                tire_life=100.0,
                fuel_remaining=100.0,
                cumulative_time=0.0,  # Equal start - no grid advantage
                speed=300.0,  # Starting speed (km/h)
                gap_to_leader=0.0,  # No gap at start
                last_lap_time=90.0
            ))

        # Create game state
        game_state = GameState(
            session_id=session_id,
            player_name=player_name,
            current_lap=0,
            total_laps=total_laps,
            is_paused=False,
            is_complete=False,
            player=player,
            opponents=opponents,
            rain_lap=rain_lap,
            safety_car_lap=safety_car_lap
        )

        with self.lock:
            self.sessions[session_id] = game_state

        return session_id

    def get_session(self, session_id: str) -> Optional[GameState]:
        """Get a game session by ID"""
        with self.lock:
            return self.sessions.get(session_id)

    def update_session(self, session_id: str, game_state: GameState):
        """Update a game session"""
        with self.lock:
            game_state.last_updated = time.time()
            self.sessions[session_id] = game_state

    def delete_session(self, session_id: str):
        """Delete a game session"""
        with self.lock:
            self.sessions.pop(session_id, None)

    def cleanup_old_sessions(self):
        """Remove sessions older than max_session_age"""
        current_time = time.time()
        expired_sessions = []

        with self.lock:
            for session_id, state in self.sessions.items():
                if current_time - state.last_updated > self.max_session_age:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self.sessions[session_id]

        return len(expired_sessions)

    def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        with self.lock:
            return len(self.sessions)


# Global session manager instance
session_manager = GameSessionManager(max_session_age_minutes=30)


async def start_cleanup_task():
    """Background task to cleanup old sessions"""
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        cleaned = session_manager.cleanup_old_sessions()
        if cleaned > 0:
            print(f"Cleaned up {cleaned} expired game sessions")
