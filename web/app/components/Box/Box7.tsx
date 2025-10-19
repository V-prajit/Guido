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
  gridColumn: '10 / span 3',
  gridRow: '6 / span 3',
};

const overlayStyle: CSSProperties = {
  display: "none",
};

const EVENT_LABELS: Record<string, string> = {
  'RAIN_START': 'Rain started - strategy adjustment',
  'BATTERY_LOW': 'Low battery - energy management',
  'TIRE_DEGRADED': 'Tire degradation - pit decision',
  'SAFETY_CAR': 'Safety car deployed',
  'OVERTAKE_OPPORTUNITY': 'Overtake opportunity detected',
};

export default function Box7({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { decisionHistory, gameStarted } = useGame();

  // Format timestamp to MM:SS
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  };

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">DECISION LOG</h3>
        <div className="space-y-2 max-h-full overflow-y-auto">
          {!gameStarted || decisionHistory.length === 0 ? (
            <div className="text-xs text-text-secondary">No decisions made yet</div>
          ) : (
            decisionHistory.slice().reverse().map((decision, index) => (
              <div
                key={`${decision.lap}-${decision.timestamp}`}
                className={`flex items-center justify-between ${
                  index < decisionHistory.length - 1 ? 'border-b border-border/20' : ''
                } pb-2`}
              >
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-text-primary">Lap {decision.lap}</span>
                    <span className="text-xs text-text-secondary/40">
                      {formatTime(decision.timestamp)}
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary">
                    {EVENT_LABELS[decision.event_type] || decision.event_type}
                  </p>
                </div>
                <span className="text-text-primary ml-3">
                  {decision.outcome === 'success' ? '✓' : decision.outcome === 'failure' ? '✗' : '—'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
