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

// --- GAUGE CONFIGURATION ---
const MAX_FUEL = 110; // kg

// --- UI COMPONENTS ---

const Sparkline: React.FC<{ data: number[]; color: string }> = ({ data, color }) => {
  const width = 120;
  const height = 30;
  const max = Math.max(...data, 0.01);
  const min = Math.min(...data);
  const gradientId = `gradient-${color.replace('#', '')}`;

  const points = useMemo(() => 
    data.map((d, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = (max - min) === 0 ? height / 2 : height - ((d - min) / (max - min)) * height;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    }).join(' ')
  , [data, max, min]);

  if (!points || data.length < 2) return <div style={{ width, height }} />;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="mt-2">
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor={color} stopOpacity={0} />
          <stop offset="100%" stopColor={color} stopOpacity={1} />
        </linearGradient>
      </defs>
      <motion.polyline
        fill="none"
        stroke={`url(#${gradientId})`}
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

  useEffect(() => { spring.set(progress); }, [spring, progress]);

  const angle = useTransform(spring, (p) => p * 180 - 90);

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
export default function Box2({ className, style }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { player, gameStarted } = useGame();

  const [liveTelemetry, setLiveTelemetry] = useState({ fuel: 110, energy: 100 });
  const [history, setHistory] = useState<{ fuel: number[], energy: number[] }>({ fuel: [], energy: [] });
  const [ersMode, setErsMode] = useState<'DEPLOY' | 'HARVEST' | 'IDLE'>('IDLE');
  const timeRef = useRef(0);
  const prevLiveTelemetryRef = useRef(liveTelemetry);

  useEffect(() => {
    if (!gameStarted) {
      setLiveTelemetry({ fuel: 110, energy: 100 });
      setHistory({ fuel: [], energy: [] });
      timeRef.current = 0;
      return;
    }

    const interval = setInterval(() => {
      timeRef.current += 1;
      setLiveTelemetry(prev => {
        const newFuel = Math.max(0, prev.fuel - (0.03 + (Math.random() - 0.5) * 0.01));
        const energyChange = Math.sin(timeRef.current / 10) * 0.5;
        const newEnergy = Math.max(0, Math.min(100, prev.energy - energyChange));
        return { fuel: newFuel, energy: newEnergy };
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [gameStarted]);

  useEffect(() => {
    if (gameStarted) {
      const fuelDelta = prevLiveTelemetryRef.current.fuel - liveTelemetry.fuel;
      const energyDelta = prevLiveTelemetryRef.current.energy - liveTelemetry.energy;

      setHistory(h => ({
        fuel: [...h.fuel, fuelDelta].slice(-30),
        energy: [...h.energy, energyDelta].slice(-30),
      }));

      if (energyDelta > 0.05) setErsMode('DEPLOY');
      else if (energyDelta < -0.05) setErsMode('HARVEST');
      else setErsMode('IDLE');
    }
    prevLiveTelemetryRef.current = liveTelemetry;
  }, [liveTelemetry, gameStarted]);

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-4 items-center justify-center">
        <h3 className="absolute top-3 text-lg font-bold text-gray-400 tracking-widest uppercase">
          Propulsion Status
        </h3>
        <div className="flex items-start justify-center gap-8 w-full mt-8">
          {/* Energy Display */}
          <div className="flex flex-col items-center gap-1">
            <FlatGauge value={liveTelemetry.energy} maxValue={100} />
            <div className="text-center w-28 h-16">
              <div className="flex justify-center items-center gap-1.5">
                <p className="text-sm font-bold tracking-wider uppercase">ENERGY</p>
                <p className="font-mono text-sm font-bold text-cyan-400">[{ersMode}]</p>
              </div>
              <p className="text-4xl font-bold text-text-primary">{liveTelemetry.energy.toFixed(1)}<span className="text-base text-text-secondary font-medium ml-1">%</span></p>
            </div>
            <Sparkline data={history.energy} color="#06b6d4" />
          </div>
          {/* Fuel Display */}
          <div className="flex flex-col items-center gap-1">
            <FlatGauge value={liveTelemetry.fuel} maxValue={MAX_FUEL} />
            <div className="text-center w-28 h-16">
              <p className="text-sm font-bold tracking-wider uppercase">FUEL</p>
              <p className="text-4xl font-bold text-text-primary">{liveTelemetry.fuel.toFixed(2)}<span className="text-base text-text-secondary font-medium ml-1">kg</span></p>
            </div>
            <Sparkline data={history.fuel} color="#a855f7" />
          </div>
        </div>
      </div>
    </section>
  );
}