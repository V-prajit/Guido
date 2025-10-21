"use client";

import type { CSSProperties, ReactNode } from 'react';
import React, { useState, useEffect, useMemo, useRef } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { useGame } from "@/contexts/GameContext";

// --- BASE STYLES ---
const baseClasses = 'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';
const defaultLayout: CSSProperties = { gridColumn: '4 / span 9', gridRow: '9 / span 4' };

// --- GAUGE CONFIGURATION ---
const GAUGE_CONFIG = {
  speed: { label: "Speed", unit: "kph", min: 0, max: 350, color: "#38bdf8" },
  tire_life: { label: "Tires", unit: "%", min: 0, max: 100, color: "#a78bfa" },
  battery_soc: { label: "Battery", unit: "%", min: 0, max: 100, color: "#34d399" },
  fuel_remaining: { label: "Fuel", unit: "kg", min: 0, max: 110, color: "#fbbf24" },
  energy_deployment: { label: "Deploy", unit: "", min: 0, max: 1, color: "#f472b6" },
};
type TelemetryKey = keyof typeof GAUGE_CONFIG;
const GAUGE_ORDER: TelemetryKey[] = ['speed', 'tire_life', 'battery_soc', 'fuel_remaining', 'energy_deployment'];

// --- GAUGE COMPONENT ---
interface GaugeProps {
  value: number;
  configKey: TelemetryKey;
  layout: { cx: number; cy: number; radius: number };
}

const CircularGauge: React.FC<GaugeProps> = ({ value, configKey, layout }) => {
  const { cx, cy, radius } = layout;
  const config = GAUGE_CONFIG[configKey];
  const spring = useSpring(value, { damping: 20, stiffness: 150 });
  useEffect(() => { spring.set(value) }, [spring, value]);

  const arcEnd = useTransform(spring, [config.min, config.max], [0, 360]);

  const arcPath = (r: number, end: number) => {
    const startAngle = 0;
    const endAngle = end;
    const start = { x: cx + r * Math.cos(startAngle), y: cy + r * Math.sin(startAngle) };
    const endPoint = { x: cx + r * Math.cos(endAngle * Math.PI / 180), y: cy + r * Math.sin(endAngle * Math.PI / 180) };
    const largeArcFlag = end > 180 ? 1 : 0;
    return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 1 ${endPoint.x} ${endPoint.y}`;
  };

  return (
    <g transform={`rotate(-90 ${cx} ${cy})`}>
      <circle cx={cx} cy={cy} r={radius} fill="none" stroke="#374151" strokeWidth={8} />
      <motion.path d={arcPath(radius, arcEnd.get())} fill="none" stroke={config.color} strokeWidth={8} strokeLinecap="round" />
      <g transform={`rotate(90 ${cx} ${cy})`}>
        <text x={cx} y={cy} textAnchor="middle" dy="-0.1em" fill="#e5e7eb" fontSize={radius * 0.45} fontWeight="bold">
          {value.toFixed(configKey === 'speed' ? 0 : 1)}
        </text>
        <text x={cx} y={cy + radius * 0.4} textAnchor="middle" fill="#9ca3af" fontSize={radius * 0.25} fontWeight="medium" style={{ textTransform: 'uppercase' }}>
          {config.label}
        </text>
      </g>
    </g>
  );
};

// --- MAIN COMPONENT ---
export default function Box5({ className, style }: { className?: string; style?: CSSProperties }) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { player, gameStarted } = useGame();
  const [telemetry, setTelemetry] = useState<Record<TelemetryKey, number>>({ speed: 0, tire_life: 100, battery_soc: 100, fuel_remaining: 110, energy_deployment: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const observer = new ResizeObserver(entries => {
      if (entries[0]) {
        const { width, height } = entries[0].contentRect;
        setDims({ width, height });
      }
    });
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!gameStarted) return;
    let animationFrameId: number;
    function update() {
      if (player) {
        setTelemetry(prev => {
          const newTelemetry: Record<TelemetryKey, number> = { ...prev };
          (Object.keys(GAUGE_CONFIG) as TelemetryKey[]).forEach(key => {
            newTelemetry[key] = player[key] ?? GAUGE_CONFIG[key].min;
          });
          return newTelemetry;
        });
      }
      animationFrameId = requestAnimationFrame(update);
    }
    animationFrameId = requestAnimationFrame(update);
    return () => cancelAnimationFrame(animationFrameId);
  }, [gameStarted, player]);

  const layout = useMemo(() => {
    if (dims.width === 0 || dims.height === 0) return null;
    const { width, height } = dims;
    const numGauges = 5;
    const padding = 15;
    const segmentWidth = width / numGauges;
    const radius = Math.min(segmentWidth / 2 - padding, height / 2 - padding);

    return GAUGE_ORDER.map((key, i) => ({
        key,
        cx: i * segmentWidth + segmentWidth / 2,
        cy: height / 2,
        radius,
    }));
  }, [dims]);

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div ref={containerRef} className="relative z-[1] flex-1 w-full h-full p-2">
        {!gameStarted ? (
          <div className="w-full h-full flex items-center justify-center text-center text-sm text-text-secondary">
            Start race to view telemetry.
          </div>
        ) : (layout &&
          <svg width="100%" height="100%" viewBox={`0 0 ${dims.width} ${dims.height}`}>
            {layout.map(l => (
              <CircularGauge key={l.key} value={telemetry[l.key]} configKey={l.key} layout={l} />
            ))}
          </svg>
        )}
      </div>
    </section>
  );
}
