"use client";

/**
 * Race HUD (Heads-Up Display) Component
 *
 * Displays real-time telemetry for the player's car during the race.
 */

import React from "react";
import { motion } from "framer-motion";

interface RaceHUDProps {
  lap: number;
  totalLaps: number;
  position: number;
  batterySOC: number;
  tireLife: number;
  fuelRemaining: number;
  lapTime?: number;
  speed?: number;  // Current speed in km/h
  energyDeployment?: number;  // 0-100
  tireManagement?: number;    // 0-100
  gapAhead?: string;
  gapBehind?: string;
  isRaining?: boolean;
  safetyCarActive?: boolean;
}

const RaceHUD: React.FC<RaceHUDProps> = ({
  lap,
  totalLaps,
  position,
  batterySOC,
  tireLife,
  fuelRemaining,
  lapTime,
  speed,
  energyDeployment = 60,
  tireManagement = 70,
  gapAhead,
  gapBehind,
  isRaining,
  safetyCarActive,
}) => {
  // Color coding for gauges
  const getBatteryColor = (level: number): string => {
    if (level > 50) return "bg-green-500";
    if (level > 20) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getTireColor = (level: number): string => {
    if (level > 50) return "bg-green-500";
    if (level > 25) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getFuelColor = (level: number): string => {
    if (level > 30) return "bg-green-500";
    if (level > 15) return "bg-yellow-500";
    return "bg-red-500";
  };

  // Strategy indicators (DEMO FEATURE)
  const getBatteryDrainRate = (energy: number): string => {
    if (energy > 80) return "⚡ High Drain";
    if (energy > 50) return "⚡ Med Drain";
    return "⚡ Low Drain";
  };

  const getTireWearRate = (tireMgmt: number): string => {
    if (tireMgmt < 50) return "🔴 High Wear";
    if (tireMgmt < 70) return "🟡 Med Wear";
    return "🟢 Low Wear";
  };

  return (
    <div className="bg-white border-4 border-black rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold tracking-wide">YOUR TELEMETRY</h3>
        <div className="flex gap-2">
          {isRaining && (
            <span className="px-3 py-1 bg-blue-500 text-white text-xs font-bold rounded-full">
              🌧️ RAIN
            </span>
          )}
          {safetyCarActive && (
            <span className="px-3 py-1 bg-yellow-500 text-black text-xs font-bold rounded-full">
              🚗 SC
            </span>
          )}
        </div>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        {/* Lap */}
        <div className="text-center">
          <div className="text-xs text-gray-600 mb-1">LAP</div>
          <div className="text-3xl font-bold">
            {lap}<span className="text-lg text-gray-400">/{totalLaps}</span>
          </div>
        </div>

        {/* Position */}
        <div className="text-center">
          <div className="text-xs text-gray-600 mb-1">POSITION</div>
          <div className="text-5xl font-bold text-blue-600">
            P{position}
          </div>
        </div>

        {/* Speed */}
        <div className="text-center">
          <div className="text-xs text-gray-600 mb-1">SPEED</div>
          <div className="text-3xl font-mono font-bold">
            {speed ? `${speed.toFixed(0)}` : '---'}
            <span className="text-sm text-gray-400"> km/h</span>
          </div>
        </div>
      </div>

      {/* Lap Time Row */}
      <div className="text-center mb-4 p-2 bg-gray-100 rounded">
        <div className="text-xs text-gray-600 mb-1">LAP TIME</div>
        <div className="text-2xl font-mono font-bold">
          {lapTime ? `${lapTime.toFixed(3)}s` : '--:--'}
        </div>
      </div>

      {/* Gap Information */}
      {(gapAhead || gapBehind) && (
        <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
          <div className="text-center p-2 bg-gray-100 rounded">
            <div className="text-xs text-gray-600">GAP AHEAD</div>
            <div className="font-mono font-bold text-red-600">
              {gapAhead || '--'}
            </div>
          </div>
          <div className="text-center p-2 bg-gray-100 rounded">
            <div className="text-xs text-gray-600">GAP BEHIND</div>
            <div className="font-mono font-bold text-green-600">
              {gapBehind || '--'}
            </div>
          </div>
        </div>
      )}

      {/* Resource Gauges with Strategy Indicators */}
      <div className="space-y-3">
        {/* Battery with Drain Rate */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-gray-700">⚡ BATTERY</span>
              <span className="text-[9px] font-bold text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                {getBatteryDrainRate(energyDeployment)}
              </span>
            </div>
            <span className="text-xs font-mono font-bold">{batterySOC.toFixed(1)}%</span>
          </div>
          <div className="h-4 bg-gray-200 rounded-full overflow-hidden border-2 border-black">
            <motion.div
              className={`h-full ${getBatteryColor(batterySOC)}`}
              initial={{ width: 0 }}
              animate={{ width: `${batterySOC}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Tire Life with Wear Rate */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-gray-700">🛞 TIRES</span>
              <span className="text-[9px] font-bold text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                {getTireWearRate(tireManagement)}
              </span>
            </div>
            <span className="text-xs font-mono font-bold">{tireLife.toFixed(1)}%</span>
          </div>
          <div className="h-4 bg-gray-200 rounded-full overflow-hidden border-2 border-black">
            <motion.div
              className={`h-full ${getTireColor(tireLife)}`}
              initial={{ width: 0 }}
              animate={{ width: `${tireLife}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Fuel */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold text-gray-700">⛽ FUEL</span>
            <span className="text-xs font-mono font-bold">{fuelRemaining.toFixed(1)}%</span>
          </div>
          <div className="h-4 bg-gray-200 rounded-full overflow-hidden border-2 border-black">
            <motion.div
              className={`h-full ${getFuelColor(fuelRemaining)}`}
              initial={{ width: 0 }}
              animate={{ width: `${fuelRemaining}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>

      {/* Warnings */}
      <div className="mt-4 space-y-2">
        {batterySOC < 15 && (
          <motion.div
            className="p-2 bg-red-100 border-2 border-red-500 rounded text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <span className="text-xs font-bold text-red-700">⚠️ BATTERY CRITICAL</span>
          </motion.div>
        )}
        {tireLife < 25 && (
          <motion.div
            className="p-2 bg-yellow-100 border-2 border-yellow-500 rounded text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <span className="text-xs font-bold text-yellow-700">⚠️ TIRE WEAR HIGH</span>
          </motion.div>
        )}
        {fuelRemaining < 20 && (
          <motion.div
            className="p-2 bg-orange-100 border-2 border-orange-500 rounded text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <span className="text-xs font-bold text-orange-700">⚠️ FUEL LOW</span>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default RaceHUD;
