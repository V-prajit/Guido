"use client";

import type { CSSProperties, ReactNode } from 'react';
import { useMemo } from 'react';
import { useGame } from "@/contexts/GameContext";

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '7 / span 3',
  gridRow: '1 / span 3',
};

const overlayStyle: CSSProperties = {
  display: "none",
};

export default function Box6({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { player, opponents, gameStarted } = useGame();

  // Calculate performance metrics (gap to leader as % of optimal)
  const performanceMetrics = useMemo(() => {
    if (!gameStarted || !player || opponents.length === 0) return [];

    const allRacers = [
      { name: 'You', gap: player.gap_to_leader, isPlayer: true },
      ...opponents.map(opp => ({ name: opp.name, gap: opp.gap_to_leader, isPlayer: false }))
    ];

    // Sort by gap (smallest = best performance)
    allRacers.sort((a, b) => a.gap - b.gap);

    const leaderGap = allRacers[0].gap;

    // Calculate % optimal (inverse of gap ratio)
    return allRacers.slice(0, 4).map(racer => {
      const gapDiff = racer.gap - leaderGap;
      const optimal = Math.max(0, Math.min(100, 100 - (gapDiff * 5))); // 1s gap = 5% penalty
      return {
        name: racer.name,
        optimal: Math.round(optimal),
        isPlayer: racer.isPlayer,
      };
    });
  }, [player, opponents, gameStarted]);

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-lg font-bold text-text-primary mb-4 tracking-wide">AGENT PERFORMANCE</h3>
        <div className="space-y-3">
          {!gameStarted || performanceMetrics.length === 0 ? (
            <div className="text-sm text-text-secondary">Start race to see performance</div>
          ) : (
            performanceMetrics.map((metric, index) => (
              <div
                key={metric.name}
                className={`${
                  index < performanceMetrics.length - 1 ? 'border-b border-border/20' : ''
                } pb-2`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className={`text-base ${metric.isPlayer ? 'font-bold' : ''} text-text-primary`}>
                    {metric.name}
                  </span>
                  <span className="text-sm text-text-secondary">
                    {metric.optimal}% optimal
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
