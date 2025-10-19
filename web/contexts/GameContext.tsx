"use client";

/**
 * Game Context Provider
 *
 * Central state management for the interactive F1 race game.
 * Manages WebSocket connection, race state, and provides data to all Box components.
 */

import React, { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import type {
  PlayerState,
  OpponentState,
  DecisionPoint,
  DecisionHistoryEntry,
  PositionHistoryEntry,
  CarData,
} from '@/types';

interface GameContextValue {
  // Connection state
  isConnected: boolean;
  sessionId: string;

  // Race state
  gameStarted: boolean;
  raceComplete: boolean;
  currentLap: number;
  totalLaps: number;
  isRaining: boolean;
  safetyCarActive: boolean;

  // Player & opponents
  player: PlayerState | null;
  opponents: OpponentState[];

  // Decision system
  decisionPoint: DecisionPoint | null;
  decisionHistory: DecisionHistoryEntry[];

  // Historical tracking
  positionHistory: PositionHistoryEntry[];

  // Race results
  finalPosition: number | null;

  // Actions
  startRace: (totalLaps?: number, rainLap?: number | null, safetyCarLap?: number | null) => void;
  selectStrategy: (strategyId: number) => void;
  restartRace: () => void;

  // Computed values for UI
  getCarsForTrack: () => CarData[];
}

const GameContext = createContext<GameContextValue | undefined>(undefined);

export const useGame = () => {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within GameProvider');
  }
  return context;
};

interface GameProviderProps {
  children: React.ReactNode;
  backendUrl?: string;
}

export const GameProvider: React.FC<GameProviderProps> = ({
  children,
  backendUrl = 'ws://localhost:8000',
}) => {
  // Session & connection
  const [sessionId] = useState(() => Math.random().toString(36).substring(7));

  // Race state
  const [gameStarted, setGameStarted] = useState(false);
  const [raceComplete, setRaceComplete] = useState(false);
  const [currentLap, setCurrentLap] = useState(0);
  const [totalLaps, setTotalLaps] = useState(57);
  const [isRaining, setIsRaining] = useState(false);
  const [safetyCarActive, setSafetyCarActive] = useState(false);

  // Player & opponents
  const [player, setPlayer] = useState<PlayerState | null>(null);
  const [opponents, setOpponents] = useState<OpponentState[]>([]);

  // Decision system
  const [decisionPoint, setDecisionPoint] = useState<DecisionPoint | null>(null);
  const [decisionHistory, setDecisionHistory] = useState<DecisionHistoryEntry[]>([]);

  // Historical tracking
  const [positionHistory, setPositionHistory] = useState<PositionHistoryEntry[]>([]);

  // Race results
  const [finalPosition, setFinalPosition] = useState<number | null>(null);

  // Handle WebSocket messages
  const handleMessage = useCallback((data: any) => {
    console.log('[GameContext] WebSocket message:', data.type);

    switch (data.type) {
      case 'RACE_STARTED':
        setGameStarted(true);
        setTotalLaps(data.total_laps);
        setPlayer(data.player);
        setOpponents(data.opponents);
        setCurrentLap(0);
        setRaceComplete(false);
        setDecisionHistory([]);
        setPositionHistory([]);
        setFinalPosition(null);
        console.log('[GameContext] Race started!');
        break;

      case 'LAP_UPDATE':
        setCurrentLap(data.lap);
        setPlayer(data.player);
        setOpponents(data.opponents);
        setIsRaining(data.is_raining || false);
        setSafetyCarActive(data.safety_car_active || false);

        // Track position history
        if (data.player) {
          setPositionHistory(prev => [
            ...prev,
            {
              lap: data.lap,
              position: data.player.position,
              timestamp: Date.now(),
            },
          ]);
        }
        break;

      case 'DECISION_POINT':
        console.log('[GameContext] Decision point triggered:', data.event_type);
        setDecisionPoint({
          event_type: data.event_type,
          lap: data.lap,
          position: data.position,
          battery_soc: data.battery_soc,
          tire_life: data.tire_life,
          fuel_remaining: data.fuel_remaining,
          recommended: data.recommended,
          avoid: data.avoid,
          latency_ms: data.latency_ms,
          used_fallback: data.used_fallback,
        });
        break;

      case 'STRATEGY_APPLIED':
        console.log('[GameContext] Strategy applied');
        setDecisionPoint(null);
        break;

      case 'RACE_COMPLETE':
        console.log('[GameContext] Race complete!');
        setRaceComplete(true);
        setFinalPosition(data.final_position);
        break;

      case 'ERROR':
        console.error('[GameContext] Server error:', data.message, data.details);
        break;

      default:
        console.warn('[GameContext] Unknown message type:', data.type);
    }
  }, []);

  // WebSocket connection
  const { isConnected, sendMessage } = useWebSocket({
    url: `${backendUrl}/ws/game/${sessionId}`,
    onMessage: handleMessage,
    onOpen: () => console.log('[GameContext] Connected to game server'),
    onClose: () => console.log('[GameContext] Disconnected from game server'),
    onError: (error) => console.error('[GameContext] WebSocket error:', error),
  });

  // Actions
  const startRace = useCallback(
    (totalLaps: number = 57, rainLap: number | null = null, safetyCarLap: number | null = null) => {
      console.log('[GameContext] Starting race...');
      sendMessage({
        type: 'START_GAME',
        player_name: 'Player',
        total_laps: totalLaps,
        rain_lap: rainLap,
        safety_car_lap: safetyCarLap,
      });
    },
    [sendMessage]
  );

  const selectStrategy = useCallback(
    (strategyId: number) => {
      console.log('[GameContext] Selecting strategy:', strategyId);
      sendMessage({
        type: 'SELECT_STRATEGY',
        strategy_id: strategyId,
      });

      // Add to history
      if (decisionPoint) {
        setDecisionHistory(prev => [
          ...prev,
          {
            lap: decisionPoint.lap,
            event_type: decisionPoint.event_type,
            strategy_chosen: strategyId,
            timestamp: Date.now(),
          },
        ]);
      }

      setDecisionPoint(null);
    },
    [sendMessage, decisionPoint]
  );

  const restartRace = useCallback(() => {
    console.log('[GameContext] Restarting race...');
    setGameStarted(false);
    setRaceComplete(false);
    setCurrentLap(0);
    setPlayer(null);
    setOpponents([]);
    setDecisionPoint(null);
    setDecisionHistory([]);
    setPositionHistory([]);
    setFinalPosition(null);
    setIsRaining(false);
    setSafetyCarActive(false);
  }, []);

  // Computed values
  const getCarsForTrack = useCallback((): CarData[] => {
    if (!player || opponents.length === 0) return [];

    const cars: CarData[] = [];

    // Player car
    cars.push({
      id: 'player',
      driverName: 'You',
      position: player.position,
      lapProgress: player.lap_progress || currentLap / totalLaps,
      speed: player.speed || 300,
      lapTime: `${player.lap_time.toFixed(3)}`,
      isUserCar: true,
    });

    // Opponent cars
    opponents.forEach(opp => {
      cars.push({
        id: opp.name,
        driverName: opp.name,
        position: opp.position,
        lapProgress: opp.lap_progress,
        speed: opp.speed || 290,
        lapTime: '1:32.000',
        isUserCar: false,
      });
    });

    return cars.sort((a, b) => a.position - b.position);
  }, [player, opponents, currentLap, totalLaps]);

  const value = useMemo(
    () => ({
      isConnected,
      sessionId,
      gameStarted,
      raceComplete,
      currentLap,
      totalLaps,
      isRaining,
      safetyCarActive,
      player,
      opponents,
      decisionPoint,
      decisionHistory,
      positionHistory,
      finalPosition,
      startRace,
      selectStrategy,
      restartRace,
      getCarsForTrack,
    }),
    [
      isConnected,
      sessionId,
      gameStarted,
      raceComplete,
      currentLap,
      totalLaps,
      isRaining,
      safetyCarActive,
      player,
      opponents,
      decisionPoint,
      decisionHistory,
      positionHistory,
      finalPosition,
      startRace,
      selectStrategy,
      restartRace,
      getCarsForTrack,
    ]
  );

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};
