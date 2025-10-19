"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import { useWebSocket } from "./useWebSocket";

export interface CarData {
  id: string;
  driverName: string;
  position: number;
  lapProgress: number;
  speed: number;
  lapTime: string;
  isUserCar: boolean;
}

export interface PlayerState {
  position: number;
  battery_soc: number;
  tire_life: number;
  fuel_remaining: number;
  lap_time: number;
  cumulative_time: number;
  energy_deployment: number;
  tire_management: number;
  fuel_strategy: number;
  ers_mode: number;
  overtake_aggression: number;
  defense_intensity: number;
  speed: number;
  gap_to_leader: number;
  lap_progress: number;
}

export interface OpponentState {
  name: string;
  agent_type: string;
  position: number;
  lap_progress: number;
  battery_soc: number;
  tire_life: number;
  fuel_remaining: number;
  cumulative_time: number;
  speed: number;
  gap_to_leader: number;
  last_lap_time: number;
}

export interface DecisionPoint {
  event_type: string;
  lap: number;
  position: number;
  battery_soc: number;
  tire_life: number;
  fuel_remaining: number;
  recommended: Array<{
    strategy_id: number;
    strategy_name: string;
    win_rate: number;
    avg_position: number;
    rationale: string;
    confidence: number;
    strategy_params: Record<string, number>;
  }>;
  avoid?: {
    strategy_id: number;
    strategy_name: string;
    win_rate: number;
    rationale: string;
    risk: string;
    strategy_params: Record<string, number>;
  };
  latency_ms?: number;
  used_fallback?: boolean;
}

interface UseGameSessionOptions {
  backendUrl?: string;
}

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

type RaceStartedMessage = {
  type: "RACE_STARTED";
  session_id: string;
  total_laps: number;
  player: PlayerState;
  opponents: OpponentState[];
};

type LapUpdateMessage = {
  type: "LAP_UPDATE";
  lap: number;
  player: PlayerState;
  opponents: OpponentState[];
  is_raining?: boolean;
  safety_car_active?: boolean;
};

type DecisionPointMessage = {
  type: "DECISION_POINT";
  event_type: string;
  lap: number;
  position: number;
  battery_soc: number;
  tire_life: number;
  fuel_remaining: number;
  recommended: DecisionPoint["recommended"];
  avoid?: DecisionPoint["avoid"];
  latency_ms?: number;
  used_fallback?: boolean;
};

type StrategyAppliedMessage = {
  type: "STRATEGY_APPLIED";
  strategy_id: number;
};

type RaceCompleteMessage = {
  type: "RACE_COMPLETE";
  final_position: number;
};

type ErrorMessage = {
  type: "ERROR";
  message: string;
  details?: string;
};

type GameMessage =
  | RaceStartedMessage
  | LapUpdateMessage
  | DecisionPointMessage
  | StrategyAppliedMessage
  | RaceCompleteMessage
  | ErrorMessage;

export const useGameSession = ({
  backendUrl = "ws://localhost:8000",
}: UseGameSessionOptions = {}) => {
  const clientSessionId = useMemo(
    () => Math.random().toString(36).substring(2, 10),
    []
  );

  const [gameStarted, setGameStarted] = useState(false);
  const [currentLap, setCurrentLap] = useState(0);
  const [totalLaps, setTotalLaps] = useState(57);
  const [playerState, setPlayerState] = useState<PlayerState | null>(null);
  const [opponents, setOpponents] = useState<OpponentState[]>([]);
  const [isRaining, setIsRaining] = useState(false);
  const [safetyCarActive, setSafetyCarActive] = useState(false);
  const [decisionPoint, setDecisionPoint] = useState<DecisionPoint | null>(null);
  const [raceComplete, setRaceComplete] = useState(false);
  const [finalPosition, setFinalPosition] = useState<number | null>(null);

  const resetRaceState = useCallback(() => {
    setGameStarted(false);
    setCurrentLap(0);
    setTotalLaps(57);
    setPlayerState(null);
    setOpponents([]);
    setIsRaining(false);
    setSafetyCarActive(false);
    setDecisionPoint(null);
    setRaceComplete(false);
    setFinalPosition(null);
  }, []);

  const handleMessage = useCallback((data: GameMessage) => {
    console.debug("WebSocket recv:", data);
    switch (data.type) {
      case "RACE_STARTED": {
        setGameStarted(true);
        setTotalLaps(data.total_laps ?? 57);
        setPlayerState(data.player);
        setOpponents(data.opponents || []);
        setCurrentLap(0);
        setRaceComplete(false);
        setFinalPosition(null);
        setDecisionPoint(null);
        break;
      }

      case "LAP_UPDATE": {
        setCurrentLap(data.lap ?? 0);
        setPlayerState(data.player);
        setOpponents(data.opponents || []);
        setIsRaining(Boolean(data.is_raining));
        setSafetyCarActive(Boolean(data.safety_car_active));

        // Debug logging for car positions
        console.log(`[LAP ${data.lap}] Player: pos=${data.player?.position}, lap_progress=${data.player?.lap_progress?.toFixed(4)}, speed=${Math.round(data.player?.speed || 0)} km/h, cumulative=${data.player?.cumulative_time?.toFixed(2)}s`);
        data.opponents?.slice(0, 3).forEach((opp: OpponentState) => {
          console.log(`[LAP ${data.lap}] ${opp.name}: pos=${opp.position}, lap_progress=${opp.lap_progress?.toFixed(4)}, speed=${Math.round(opp.speed || 0)} km/h, cumulative=${opp.cumulative_time?.toFixed(2)}s`);
        });

        break;
      }

      case "DECISION_POINT": {
        const decision: DecisionPoint = {
          event_type: data.event_type,
          lap: data.lap,
          position: data.position,
          battery_soc: data.battery_soc,
          tire_life: data.tire_life,
          fuel_remaining: data.fuel_remaining,
          recommended: data.recommended || [],
          avoid: data.avoid,
          latency_ms: data.latency_ms,
          used_fallback: data.used_fallback,
        };
        setDecisionPoint(decision);
        break;
      }

      case "STRATEGY_APPLIED": {
        setDecisionPoint(null);
        break;
      }

      case "RACE_COMPLETE": {
        setRaceComplete(true);
        setFinalPosition(data.final_position ?? null);
        break;
      }

      case "ERROR": {
        console.error("Game error:", data.message, data.details);
        break;
      }

      default:
        break;
    }
  }, []);

  const { isConnected, sendMessage } = useWebSocket({
    url: `${backendUrl}/ws/game/${clientSessionId}`,
    onMessage: handleMessage,
    onOpen: () => console.log("Connected to game server"),
    onClose: () => console.log("Disconnected from game server"),
    onError: (error) => console.error("WebSocket error:", error),
  });

  const carsForTrack: CarData[] = useMemo(() => {
    if (!playerState) return [];

    const cars: CarData[] = [];

    const playerLapProgress = clamp01(
      Number.isFinite(playerState.lap_progress) ? playerState.lap_progress : 0
    );

    cars.push({
      id: "player",
      driverName: "You",
      position: playerState.position,
      lapProgress: playerLapProgress,
      speed: Math.round(playerState.speed ?? 0),
      lapTime: (playerState.lap_time ?? 0).toFixed(3),
      isUserCar: true,
    });

    opponents.forEach((opp) => {
      cars.push({
        id: opp.name,
        driverName: opp.name.split(" ")[0] ?? opp.name,
        position: opp.position,
        lapProgress: clamp01(opp.lap_progress ?? 0),
        speed: Math.round(opp.speed ?? 0),
        lapTime: (opp.last_lap_time ?? 0).toFixed(3),
        isUserCar: false,
      });
    });

    return cars.sort((a, b) => a.position - b.position);
  }, [playerState, opponents]);

  const startRace = useCallback(() => {
    console.debug("Attempting to start race. Connected:", isConnected);
    sendMessage({
      type: "START_GAME",
      player_name: "Player",
      total_laps: totalLaps,
      rain_lap: Math.random() < 0.5 ? Math.floor(Math.random() * 30) + 15 : null,
      safety_car_lap:
        Math.random() < 0.3 ? Math.floor(Math.random() * 25) + 20 : null,
    });
  }, [sendMessage, totalLaps, isConnected]);

  const selectStrategy = useCallback(
    (strategyId: number) => {
      sendMessage({
        type: "SELECT_STRATEGY",
        strategy_id: strategyId,
      });
      setDecisionPoint(null);
    },
    [sendMessage]
  );

  const restartRace = useCallback(() => {
    resetRaceState();
  }, [resetRaceState]);

  const progressFraction = totalLaps > 0 ? currentLap / totalLaps : 0;

  return {
    isConnected,
    gameStarted,
    currentLap,
    totalLaps,
    playerState,
    opponents,
    isRaining,
    safetyCarActive,
    decisionPoint,
    raceComplete,
    finalPosition,
    carsForTrack,
    startRace,
    selectStrategy,
    restartRace,
    setTotalLaps,
    progressFraction,
  };
};
