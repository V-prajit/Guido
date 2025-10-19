"use client";

import type { CSSProperties, ReactNode } from 'react';
import React, { useState, useEffect, useMemo, useRef } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { useGame } from "@/contexts/GameContext";

// --- BASELINE STRUCTURE ---
interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}
const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';
const defaultLayout: CSSProperties = {
  gridColumn: '1 / span 3',
  gridRow: '9 / span 4',
};
const overlayStyle: CSSProperties = { display: "none" };

// --- TYPE DEFINITIONS ---
interface TelemetrySnapshot {
  fuelRemaining_kg: number;
  energyRemaining_kWh: number;
  fuelDelta: number;
  energyDelta: number;
}

// --- GAUGE CONFIGURATION ---
const MAX_FUEL = 110; // kg
const MAX_ENERGY = 4.5; // kWh

// --- UI COMPONENTS ---

const Sparkline: React.FC<{ data: number[]; color: string }> = ({ data, color }) => {
  const width = 120;
  const height = 30;
  const max = Math.max(...data, 0.01);
  const min = Math.min(...data);

  const points = useMemo(() => 
    data.map((d, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((d - min) / (max - min)) * height;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    }).join(' ')
  , [data, max, min]);

  if (!points) return <div style={{ width, height }} />;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="mt-2">
      <defs>
        <linearGradient id={`gradient-${color}`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor={color} stopOpacity={0} />
          <stop offset="100%" stopColor={color} stopOpacity={1} />
        </linearGradient>
      </defs>
      <motion.polyline
        fill="none"
        stroke={`url(#gradient-${color})`}
        strokeWidth="2"
        points={points}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      />
    </svg>
  );
};

const FlatGauge: React.FC<{ value: number; maxValue: number }> = ({ value, maxValue }) => {
  const progress = Math.max(0, Math.min(1, value / maxValue));
  const spring = useSpring(progress, { damping: 15, stiffness: 100 });
  const angle = useTransform(spring, (p) => p * 180 - 90);

  useEffect(() => { spring.set(progress); }, [spring, progress]);

  return (
    <svg width="120" height="60" viewBox="0 0 100 50">
      <g>
        <path d="M 5.00 50.00 A 45 45 0 0 1 19.10 20.61" fill="none" strokeWidth={10} stroke="#d9534f" />
        <path d="M 19.10 20.61 A 45 45 0 0 1 50.00 5.00" fill="none" strokeWidth={10} stroke="#f0ad4e" />
        <path d="M 50.00 5.00 A 45 45 0 0 1 80.90 20.61" fill="none" strokeWidth={10} stroke="#ffcd3c" />
        <path d="M 80.90 20.61 A 45 45 0 0 1 95.00 50.00" fill="none" strokeWidth={10} stroke="#5cb85c" />
      </g>
      <motion.g style={{ rotate: angle, transformOrigin: '50px 50px' }}>
        <path d="M 49 50 L 50 8 L 51 50 Z" fill="#E5E7EB" />
        <circle cx="50" cy="50" r="3" fill="#E5E7EB" />
      </motion.g>
    </svg>
  );
};

// --- MAIN BOX COMPONENT ---
export default function Box2({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { player, gameStarted } = useGame();

  // Use ref instead of state to avoid infinite loop
  const prevTelemetryRef = useRef<{ fuel: number; energy: number } | null>(null);
  const [history, setHistory] = useState<{ fuel: number[], energy: number[] }>({ fuel: [], energy: [] });
  const [ersMode, setErsMode] = useState<'DEPLOY' | 'HARVEST' | 'IDLE'>('IDLE');

  // Current telemetry snapshot
  const telemetry: TelemetrySnapshot = useMemo(() => {
    if (!player || !gameStarted) {
      return {
        fuelRemaining_kg: 0,
        energyRemaining_kWh: 0,
        fuelDelta: 0,
        energyDelta: 0,
      };
    }

    const currentFuel = player.fuel_remaining;
    const currentEnergy = player.battery_soc; // Use SOC percentage directly

    const fuelDelta = prevTelemetryRef.current ? prevTelemetryRef.current.fuel - currentFuel : 0;
    const energyDelta = prevTelemetryRef.current ? prevTelemetryRef.current.energy - currentEnergy : 0;

    return {
      fuelRemaining_kg: currentFuel,
      energyRemaining_kWh: currentEnergy, // Actually percentage now, but keeping field name
      fuelDelta,
      energyDelta,
    };
  }, [player, gameStarted]);

  // Update history and ERS mode when telemetry changes
  useEffect(() => {
    if (!player || !gameStarted) return;

    const currentFuel = player.fuel_remaining;
    const currentEnergy = player.battery_soc; // Use percentage directly

    // Calculate deltas
    if (prevTelemetryRef.current) {
      const fuelDelta = prevTelemetryRef.current.fuel - currentFuel;
      const energyDelta = prevTelemetryRef.current.energy - currentEnergy;

      // Update history (keep last 30 points)
      setHistory(prev => ({
        fuel: [...prev.fuel, fuelDelta].slice(-30),
        energy: [...prev.energy, energyDelta].slice(-30),
      }));

      // Determine ERS mode based on energy delta
      if (energyDelta > 0.1) setErsMode('DEPLOY');
      else if (energyDelta < -0.1) setErsMode('HARVEST');
      else setErsMode('IDLE');
    }

    // Store current as previous for next delta calculation
    prevTelemetryRef.current = { fuel: currentFuel, energy: currentEnergy };
  }, [player, gameStarted]);

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-4 items-center justify-center">
        <h3 className="absolute top-3 text-sm font-bold text-gray-400 tracking-widest uppercase">
          Propulsion Status
        </h3>
        <div className="flex items-start justify-center gap-8 w-full mt-8">
          {/* Energy Display */}
          <div className="flex flex-col items-center gap-1">
            <FlatGauge value={telemetry.energyRemaining_kWh} maxValue={100} />
            <div className="text-center w-28 h-16">
              <div className="flex justify-center items-center gap-1.5">
                <p className="text-xs font-bold tracking-wider uppercase">ENERGY</p>
                <p className="font-mono text-xs font-bold text-cyan-400">[{ersMode}]</p>
              </div>
              <p className="text-xl font-bold text-text-primary">{telemetry.energyRemaining_kWh.toFixed(1)}<span className="text-xs text-text-secondary font-medium ml-1">%</span></p>
            </div>
            <Sparkline data={history.energy} color="#06b6d4" />
          </div>
          {/* Fuel Display */}
          <div className="flex flex-col items-center gap-1">
            <FlatGauge value={telemetry.fuelRemaining_kg} maxValue={MAX_FUEL} />
            <div className="text-center w-28 h-16">
              <p className="text-xs font-bold tracking-wider uppercase">FUEL</p>
              <p className="text-xl font-bold text-text-primary">{telemetry.fuelRemaining_kg.toFixed(2)}<span className="text-xs text-text-secondary font-medium ml-1">kg</span></p>
            </div>
            <Sparkline data={history.fuel} color="#a855f7" />
          </div>
        </div>
      </div>
    </section>
  );
}