"use client";

/**
 * Game Controller Component
 *
 * Main controller for the interactive game mode.
 * Manages WebSocket connection, game state, and UI coordination.
 */

import React, { useState, useCallback } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import Box1_RaceTrack from "@/components/BentoBoxes/Box1_RaceTrack";
import RaceHUD from "./RaceHUD";
import DecisionModal from "./DecisionModal";
import { motion, AnimatePresence } from "framer-motion";

interface CarData {
  id: string;
  driverName: string;
  position: number;
  lapProgress: number;
  speed: number;
  lapTime: string;
  isUserCar: boolean;
}

interface PlayerState {
  position: number;
  battery_soc: number;
  tire_life: number;
  fuel_remaining: number;
  lap_time: number;
  cumulative_time: number;
  speed: number;  // km/h from backend
  gap_to_leader: number;  // seconds behind leader
}

interface OpponentState {
  name: string;
  agent_type: string;
  position: number;
  lap_progress: number;  // 0-1, calculated from cumulative_time
  battery_soc: number;
  tire_life: number;
  fuel_remaining: number;
  cumulative_time: number;
  speed: number;  // km/h from backend
  gap_to_leader: number;  // seconds behind leader
  last_lap_time: number;  // last lap time in seconds
}

interface DecisionPoint {
  event_type: string;
  lap: number;
  position: number;
  battery_soc: number;
  tire_life: number;
  fuel_remaining: number;
  recommended: any[];
  avoid?: any;
  latency_ms?: number;
  used_fallback?: boolean;
}

interface GameControllerProps {
  backendUrl?: string;
}

const GameController: React.FC<GameControllerProps> = ({
  backendUrl = "ws://localhost:8000",
}) => {
  const [gameStarted, setGameStarted] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substring(7));
  const [currentLap, setCurrentLap] = useState(0);
  const [totalLaps, setTotalLaps] = useState(57);
  const [playerState, setPlayerState] = useState<PlayerState | null>(null);
  const [opponents, setOpponents] = useState<OpponentState[]>([]);
  const [isRaining, setIsRaining] = useState(false);
  const [safetyCarActive, setSafetyCarActive] = useState(false);
  const [decisionPoint, setDecisionPoint] = useState<DecisionPoint | null>(null);
  const [raceComplete, setRaceComplete] = useState(false);
  const [finalPosition, setFinalPosition] = useState<number | null>(null);

  // Convert game state to car data for track visualization
  // ALL DATA NOW COMES FROM BACKEND - NO CALCULATIONS
  const getCarsForTrack = useCallback((): CarData[] => {
    if (!playerState || opponents.length === 0) return [];

    const cars: CarData[] = [];

    // Player car - use real backend data for ALL fields
    cars.push({
      id: "player",
      driverName: "You",
      position: playerState.position,
      lapProgress: playerState.gap_to_leader === 0
        ? (currentLap / totalLaps)  // Leader uses lap-based progress
        : playerState.cumulative_time / (currentLap * 90.0 || 1),  // Others use cumulative time
      speed: playerState.speed,  // Direct from backend calculation
      lapTime: playerState.lap_time.toFixed(3),
      isUserCar: true,
    });

    // Opponent cars - use real backend data for ALL fields
    opponents.forEach((opp) => {
      cars.push({
        id: opp.name,
        driverName: opp.name.split(' ')[0],  // First name only (e.g., "Lewis" instead of "Lewis Hamilton")
        position: opp.position,
        lapProgress: opp.lap_progress,  // Already calculated in backend using cumulative_time
        speed: opp.speed,  // Direct from backend calculation
        lapTime: opp.last_lap_time?.toFixed(3) || "90.000",
        isUserCar: false,
      });
    });

    // Sort by position
    return cars.sort((a, b) => a.position - b.position);
  }, [playerState, opponents, currentLap, totalLaps]);

  // Handle WebSocket messages
  const handleMessage = useCallback((data: any) => {
    console.log("WebSocket message:", data);

    switch (data.type) {
      case "RACE_STARTED":
        setGameStarted(true);
        setSessionId(data.session_id);
        setTotalLaps(data.total_laps);
        setPlayerState(data.player);
        setOpponents(data.opponents);
        setCurrentLap(0);
        setRaceComplete(false);
        break;

      case "LAP_UPDATE":
        setCurrentLap(data.lap);
        setPlayerState(data.player);
        setOpponents(data.opponents);
        setIsRaining(data.is_raining || false);
        setSafetyCarActive(data.safety_car_active || false);
        break;

      case "DECISION_POINT":
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

      case "STRATEGY_APPLIED":
        // Decision modal will close, race resumes
        setDecisionPoint(null);
        break;

      case "RACE_COMPLETE":
        setRaceComplete(true);
        setFinalPosition(data.final_position);
        break;

      case "ERROR":
        console.error("Game error:", data.message, data.details);
        break;
    }
  }, []);

  // WebSocket connection
  const { isConnected, sendMessage } = useWebSocket({
    url: `${backendUrl}/ws/game/${sessionId}`,
    onMessage: handleMessage,
    onOpen: () => console.log("Connected to game server"),
    onClose: () => console.log("Disconnected from game server"),
    onError: (error) => console.error("WebSocket error:", error),
  });

  // Start new race
  const handleStartRace = () => {
    sendMessage({
      type: "START_GAME",
      player_name: "Player",
      total_laps: 57,
      rain_lap: Math.random() < 0.5 ? Math.floor(Math.random() * 30) + 15 : null,
      safety_car_lap: Math.random() < 0.3 ? Math.floor(Math.random() * 25) + 20 : null,
    });
  };

  // Handle strategy selection
  const handleStrategySelect = (strategyId: number) => {
    sendMessage({
      type: "SELECT_STRATEGY",
      strategy_id: strategyId,
    });
    setDecisionPoint(null);
  };

  // Restart race
  const handleRestartRace = () => {
    setGameStarted(false);
    setRaceComplete(false);
    setFinalPosition(null);
    setCurrentLap(0);
    setPlayerState(null);
    setOpponents([]);
    setDecisionPoint(null);
    setIsRaining(false);
    setSafetyCarActive(false);
  };

  return (
    <div className="min-h-screen bg-zinc-50 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-black mb-2">
          🏎️ Interactive Race Mode
        </h1>
        <p className="text-gray-600">
          Race against 7 AI opponents • Make strategic decisions • Win the championship
        </p>
        <div className="mt-4 flex items-center gap-4">
          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
            isConnected ? "bg-green-500 text-white" : "bg-red-500 text-white"
          }`}>
            {isConnected ? "● CONNECTED" : "● DISCONNECTED"}
          </div>
          {!gameStarted && (
            <button
              onClick={handleStartRace}
              disabled={!isConnected}
              className="px-6 py-2 bg-black text-white font-bold rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              START RACE
            </button>
          )}
          {gameStarted && !raceComplete && (
            <div className="text-sm text-gray-600">
              Lap {currentLap} / {totalLaps}
            </div>
          )}
        </div>
      </div>

      {/* Game Area */}
      <div className="max-w-7xl mx-auto">
        {!gameStarted && !raceComplete && (
          <div className="text-center py-20">
            <h2 className="text-2xl font-bold text-gray-400 mb-4">
              Ready to race?
            </h2>
            <p className="text-gray-500 mb-8">
              Connect to the server and click START RACE to begin
            </p>
          </div>
        )}

        {gameStarted && !raceComplete && (
          <div className="grid grid-cols-3 gap-6">
            {/* Left: Race Track */}
            <div className="col-span-2">
              <Box1_RaceTrack cars={getCarsForTrack()} />
            </div>

            {/* Right: HUD */}
            <div>
              {playerState && (
                <RaceHUD
                  lap={currentLap}
                  totalLaps={totalLaps}
                  position={playerState.position}
                  batterySOC={playerState.battery_soc}
                  tireLife={playerState.tire_life}
                  fuelRemaining={playerState.fuel_remaining}
                  lapTime={playerState.lap_time}
                  gapAhead={playerState.position > 1 ? `+${playerState.gap_to_leader.toFixed(3)}s` : undefined}
                  gapBehind={opponents.find(o => o.position === playerState.position + 1)?.gap_to_leader ?
                    `${(opponents.find(o => o.position === playerState.position + 1)!.gap_to_leader - playerState.gap_to_leader).toFixed(3)}s` : undefined}
                  isRaining={isRaining}
                  safetyCarActive={safetyCarActive}
                />
              )}
            </div>
          </div>
        )}

        {raceComplete && (
          <AnimatePresence>
            <motion.div
              className="text-center py-20"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <h2 className="text-5xl font-bold text-black mb-4">
                RACE COMPLETE!
              </h2>
              <div className="text-8xl font-bold text-blue-600 mb-8">
                P{finalPosition}
              </div>
              <p className="text-xl text-gray-600 mb-8">
                You finished in position {finalPosition} after {totalLaps} laps
              </p>
              <button
                onClick={handleRestartRace}
                className="px-8 py-4 bg-black text-white font-bold rounded-lg hover:bg-gray-800 transition-colors text-lg"
              >
                RACE AGAIN
              </button>
            </motion.div>
          </AnimatePresence>
        )}
      </div>

      {/* Decision Modal */}
      {decisionPoint && (
        <DecisionModal
          isOpen={true}
          eventType={decisionPoint.event_type}
          lap={decisionPoint.lap}
          position={decisionPoint.position}
          batterySOC={decisionPoint.battery_soc}
          tireLife={decisionPoint.tire_life}
          fuelRemaining={decisionPoint.fuel_remaining}
          recommended={decisionPoint.recommended}
          avoid={decisionPoint.avoid}
          onSelect={handleStrategySelect}
          latencyMs={decisionPoint.latency_ms}
          usedFallback={decisionPoint.used_fallback}
        />
      )}
    </div>
  );
};

export default GameController;
