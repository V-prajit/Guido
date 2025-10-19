"use client";

import type { CSSProperties, ReactNode } from 'react';
import { useGame } from "@/contexts/GameContext";

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '4 / span 9',
  gridRow: '9 / span 4',
};

const overlayStyle: CSSProperties = {
  display: "none",
};

export default function Box5({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { player, currentLap, totalLaps, gameStarted } = useGame();

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">PLAYER TELEMETRY</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">Lap</span>
            <span className="text-sm font-bold text-text-primary">
              {gameStarted && player ? `${currentLap}/${totalLaps}` : '—/—'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">Position</span>
            <span className="text-sm font-bold text-text-primary">
              {gameStarted && player ? `P${player.position}` : '—'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">Battery</span>
            <span className="text-sm font-bold text-text-primary">
              {gameStarted && player ? `${player.battery_soc.toFixed(1)}%` : '—'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">Tires</span>
            <span className="text-sm font-bold text-text-primary">
              {gameStarted && player ? `${player.tire_life.toFixed(1)}%` : '—'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">Fuel</span>
            <span className="text-sm font-bold text-text-primary">
              {gameStarted && player ? `${player.fuel_remaining.toFixed(1)}kg` : '—'}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
