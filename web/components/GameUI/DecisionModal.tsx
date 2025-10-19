"use client";

/**
 * Decision Modal Component
 *
 * Displays strategy recommendations during decision points in the race.
 * Shows 3 strategy cards with Gemini-powered analysis.
 */

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface StrategyParams {
  energy_deployment: number;
  tire_management: number;
  fuel_strategy: number;
  ers_mode: number;
  overtake_aggression: number;
  defense_intensity: number;
}

interface StrategyRecommendation {
  strategy_id: number;
  strategy_name: string;
  win_rate: float;
  avg_position?: number;
  rationale: string;
  confidence: number;
  strategy_params: StrategyParams;
}

interface StrategyToAvoid {
  strategy_id: number;
  strategy_name: string;
  win_rate: number;
  rationale: string;
  risk: string;
  strategy_params: StrategyParams;
}

interface DecisionModalProps {
  isOpen: boolean;
  eventType: string;
  lap: number;
  position: number;
  batterySOC: number;
  tireLife: number;
  fuelRemaining: number;
  recommended: StrategyRecommendation[];
  avoid?: StrategyToAvoid | null;
  onSelect: (strategyId: number) => void;
  latencyMs?: number;
  usedFallback?: boolean;
}

const DECISION_TIMER_SECONDS = 30;

const DecisionModal: React.FC<DecisionModalProps> = ({
  isOpen,
  eventType,
  lap,
  position,
  batterySOC,
  tireLife,
  fuelRemaining,
  recommended,
  avoid,
  onSelect,
  latencyMs,
  usedFallback,
}) => {
  const [timeRemaining, setTimeRemaining] = useState(DECISION_TIMER_SECONDS);
  const [selectedStrategy, setSelectedStrategy] = useState<number | null>(null);

  // Countdown timer
  useEffect(() => {
    if (!isOpen) {
      setTimeRemaining(DECISION_TIMER_SECONDS);
      setSelectedStrategy(null);
      return;
    }

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          // Auto-select best strategy when time runs out
          if (recommended.length > 0) {
            onSelect(recommended[0].strategy_id);
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, recommended, onSelect]);

  // Keyboard shortcuts
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === "1") {
        handleStrategySelect(0);
      } else if (e.key === "2") {
        handleStrategySelect(1);
      } else if (e.key === "3") {
        handleStrategySelect(2);
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [isOpen]);

  const handleStrategySelect = (strategyId: number) => {
    setSelectedStrategy(strategyId);
    // Small delay for visual feedback
    setTimeout(() => {
      onSelect(strategyId);
    }, 300);
  };

  const getEventTitle = (type: string): string => {
    const titles: Record<string, string> = {
      'RAIN_START': '🌧️ RAIN STARTING',
      'SAFETY_CAR': '🚗 SAFETY CAR',
      'TIRE_CRITICAL': '🛞 TIRE WEAR CRITICAL',
      'BATTERY_LOW': '⚡ BATTERY LOW',
      'OVERTAKE_OPPORTUNITY': '🏁 OVERTAKE OPPORTUNITY',
      'STRATEGIC_CHECKPOINT': '📊 STRATEGIC DECISION',
    };
    return titles[type] || '⚠️ DECISION POINT';
  };

  // All 3 strategies (recommended + avoid)
  const allStrategies = [
    ...(recommended || []),
    ...(avoid ? [avoid] : [])
  ].sort((a, b) => a.strategy_id - b.strategy_id);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="w-full max-w-6xl mx-4 bg-white border-4 border-black rounded-lg shadow-2xl overflow-hidden"
            initial={{ scale: 0.9, y: 50 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 50 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          >
            {/* Header */}
            <div className="bg-black text-white p-6 border-b-4 border-black">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold tracking-tight">
                    {getEventTitle(eventType)}
                  </h2>
                  <p className="text-gray-300 mt-1">
                    Lap {lap} • P{position} • Battery {batterySOC.toFixed(1)}% • Tires {tireLife.toFixed(1)}%
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-5xl font-bold tabular-nums">
                    {timeRemaining}s
                  </div>
                  <div className="text-sm text-gray-400">
                    {usedFallback && '⚠️ Fallback Mode'}
                    {latencyMs && !usedFallback && `⚡ ${Math.round(latencyMs)}ms`}
                  </div>
                </div>
              </div>

              {/* Timer bar */}
              <div className="mt-4 h-2 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-green-500 to-red-500"
                  initial={{ width: "100%" }}
                  animate={{ width: `${(timeRemaining / DECISION_TIMER_SECONDS) * 100}%` }}
                  transition={{ duration: 1, ease: "linear" }}
                />
              </div>
            </div>

            {/* Strategy Cards */}
            <div className="p-6 grid grid-cols-3 gap-4">
              {allStrategies.map((strategy) => {
                const isRecommended = recommended.some(r => r.strategy_id === strategy.strategy_id);
                const isAvoid = avoid && avoid.strategy_id === strategy.strategy_id;
                const isSelected = selectedStrategy === strategy.strategy_id;

                const borderColor = isRecommended
                  ? "border-green-500"
                  : isAvoid
                  ? "border-red-500"
                  : "border-gray-300";

                const bgColor = isSelected
                  ? "bg-blue-50"
                  : "bg-white";

                return (
                  <motion.button
                    key={strategy.strategy_id}
                    onClick={() => handleStrategySelect(strategy.strategy_id)}
                    className={`relative border-4 ${borderColor} ${bgColor} rounded-lg p-6 text-left transition-all hover:shadow-xl ${
                      isSelected ? "scale-105" : ""
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {/* Tag */}
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-xl font-bold text-black">
                        {strategy.strategy_name}
                      </h3>
                      {isRecommended && (
                        <span className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full">
                          ✓ RECOMMENDED
                        </span>
                      )}
                      {isAvoid && (
                        <span className="px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
                          ✗ AVOID
                        </span>
                      )}
                    </div>

                    {/* Win Rate */}
                    <div className="mb-4">
                      <div className="text-4xl font-bold text-black">
                        {strategy.win_rate.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Win Rate</div>
                    </div>

                    {/* Rationale */}
                    <p className="text-sm text-gray-700 mb-4 min-h-[60px]">
                      {strategy.rationale}
                    </p>

                    {/* Risk (for avoid strategy) */}
                    {isAvoid && 'risk' in strategy && (
                      <div className="mb-4 p-3 bg-red-50 border-2 border-red-200 rounded">
                        <div className="text-xs font-bold text-red-700 mb-1">⚠️ RISK</div>
                        <div className="text-xs text-red-600">{strategy.risk}</div>
                      </div>
                    )}

                    {/* Confidence (for recommended strategies) */}
                    {isRecommended && 'confidence' in strategy && (
                      <div className="mb-4">
                        <div className="text-xs text-gray-600 mb-1">
                          Confidence: {(strategy.confidence * 100).toFixed(0)}%
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500"
                            style={{ width: `${strategy.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Strategy Parameters */}
                    <div className="space-y-1">
                      <div className="text-xs font-bold text-gray-700 mb-2">PARAMETERS</div>
                      <div className="grid grid-cols-2 gap-1 text-xs">
                        <div className="text-gray-600">Energy:</div>
                        <div className="font-mono font-bold text-right">
                          {strategy.strategy_params.energy_deployment}
                        </div>
                        <div className="text-gray-600">Tires:</div>
                        <div className="font-mono font-bold text-right">
                          {strategy.strategy_params.tire_management}
                        </div>
                        <div className="text-gray-600">Fuel:</div>
                        <div className="font-mono font-bold text-right">
                          {strategy.strategy_params.fuel_strategy}
                        </div>
                        <div className="text-gray-600">ERS:</div>
                        <div className="font-mono font-bold text-right">
                          {strategy.strategy_params.ers_mode}
                        </div>
                        <div className="text-gray-600">Attack:</div>
                        <div className="font-mono font-bold text-right">
                          {strategy.strategy_params.overtake_aggression}
                        </div>
                        <div className="text-gray-600">Defense:</div>
                        <div className="font-mono font-bold text-right">
                          {strategy.strategy_params.defense_intensity}
                        </div>
                      </div>
                    </div>

                    {/* Selected indicator */}
                    {isSelected && (
                      <motion.div
                        className="absolute inset-0 border-4 border-blue-500 rounded-lg pointer-events-none"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.2 }}
                      />
                    )}
                  </motion.button>
                );
              })}
            </div>

            {/* Footer */}
            <div className="bg-gray-100 p-4 text-center text-sm text-gray-600">
              <p>
                Press <kbd className="px-2 py-1 bg-white border border-gray-300 rounded font-mono text-xs">1</kbd>,
                <kbd className="px-2 py-1 bg-white border border-gray-300 rounded font-mono text-xs ml-1">2</kbd>, or
                <kbd className="px-2 py-1 bg-white border border-gray-300 rounded font-mono text-xs ml-1">3</kbd> to select a strategy,
                or click a card • Best strategy auto-selected at 0s
              </p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default DecisionModal;
