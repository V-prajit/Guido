
"use client";

import type { CSSProperties, ReactNode } from 'react';
import React, { useState, useEffect } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import raceData from "../../../mock/box2MD.json";

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

const overlayStyle: CSSProperties = {
  display: "none",
};

// --- TYPE DEFINITIONS ---
interface TelemetryData {
  time_sec: number;
  fuelRemaining_kg: number;
  energyRemaining_kWh: number;
}

// --- GAUGE CONFIGURATION ---
const MAX_FUEL = 110; // kg
const MAX_ENERGY = 4.5; // kWh

// --- NEW GAUGE COMPONENT (Corrected SVG) ---
interface FlatGaugeProps {
  value: number;
  maxValue: number;
  label: string;
  unit: string;
}

const FlatGauge: React.FC<FlatGaugeProps> = ({ value, maxValue, label, unit }) => {
  const progress = Math.max(0, Math.min(1, value / maxValue));
  const spring = useSpring(progress, { damping: 15, stiffness: 100 });
  const angle = useTransform(spring, (p) => p * 180 - 90);

  useEffect(() => {
    spring.set(progress);
  }, [spring, progress]);

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="140" height="70" viewBox="0 0 100 50">
        <style>{`.gauge-arc-segment { fill: none; stroke-width: 10; }`}</style>
        {/* Corrected Arcs: Drawn as individual segments for reliability */}
        <g>
          <path d="M 5.00 50.00 A 45 45 0 0 1 19.10 20.61" className="gauge-arc-segment" stroke="#d9534f" />
          <path d="M 19.10 20.61 A 45 45 0 0 1 50.00 5.00" className="gauge-arc-segment" stroke="#f0ad4e" />
          <path d="M 50.00 5.00 A 45 45 0 0 1 80.90 20.61" className="gauge-arc-segment" stroke="#ffcd3c" />
          <path d="M 80.90 20.61 A 45 45 0 0 1 95.00 50.00" className="gauge-arc-segment" stroke="#5cb85c" />
          {/* This is a simplified 4-segment version as 5 segments were visually cluttered */}
        </g>
        <motion.g style={{ rotate: angle, transformOrigin: '50px 50px' }}>
          <path d="M 49 50 L 50 8 L 51 50 Z" fill="#E5E7EB" />
          <circle cx="50" cy="50" r="3" fill="#E5E7EB" />
        </motion.g>
      </svg>
      <div className="flex flex-col items-center text-center">
        <p className="text-2xl font-bold text-text-primary">{value.toFixed(2)}</p>
        <p className="text-xs text-text-secondary uppercase">{unit}</p>
      </div>
    </div>
  );
};

// --- MAIN BOX COMPONENT ---
export default function Box2({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const [telemetry, setTelemetry] = useState<TelemetryData>(raceData[0]);

  useEffect(() => {
    let frame = 0;
    const timer = setInterval(() => {
      frame = (frame + 1) % raceData.length;
      setTelemetry(raceData[frame]);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-4 items-center justify-center">
        <h3 className="absolute top-3 text-sm font-bold text-gray-400 tracking-widest uppercase">
          Propulsion Status
        </h3>
        <div className="flex items-center justify-center gap-8 w-full mt-4">
          <FlatGauge
            value={telemetry.energyRemaining_kWh}
            maxValue={MAX_ENERGY}
            label="Energy"
            unit="kWh"
          />
          <FlatGauge
            value={telemetry.fuelRemaining_kg}
            maxValue={MAX_FUEL}
            label="Fuel"
            unit="kg"
          />
        </div>
      </div>
    </section>
  );
}
