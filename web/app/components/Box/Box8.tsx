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

export default function Box8({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { positionHistory, gameStarted } = useGame();

  // Sample last 12 laps for display
  const displayHistory = positionHistory.slice(-12);

  // Calculate bar height (inverted - position 1 should be tallest)
  const getBarHeight = (position: number) => {
    const maxPosition = 8; // Assuming 8 cars
    const heightPercent = ((maxPosition - position + 1) / maxPosition) * 100;
    return `${Math.max(20, Math.min(100, heightPercent))}%`;
  };

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">POSITION GRAPH</h3>
        <div className="h-full flex items-end justify-between gap-1 border-b border-l border-border/20 pb-4 pl-4">
          {!gameStarted || displayHistory.length === 0 ? (
            <div className="text-xs text-text-secondary">Start race to see position history</div>
          ) : (
            displayHistory.map((entry) => (
              <div key={entry.lap} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full bg-text-primary/20 rounded-t relative" style={{ height: '100px' }}>
                  <div
                    className="w-full bg-text-primary rounded-t absolute bottom-0"
                    style={{ height: getBarHeight(entry.position) }}
                  ></div>
                </div>
                <span className="text-[8px] text-text-secondary/40">{entry.lap}</span>
              </div>
            ))
          )}
        </div>
        <div className="mt-2 flex justify-between text-xs text-text-secondary">
          <span>Lap</span>
          <span>Position</span>
        </div>
      </div>
    </section>
  );
}
