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
  gridColumn: '4 / span 3',
  gridRow: '1 / span 3',
};

const overlayStyle: CSSProperties = {
  display: "none",
};

// Map agent types to strategy labels
const STRATEGY_LABELS: Record<string, string> = {
  'VerstappenStyle': 'Balanced Aggression',
  'HamiltonStyle': 'Tire Conservation',
  'AlonsoStyle': 'Strategic Defense',
  'AggressiveAttacker': 'All-Out Attack',
  'TireWhisperer': 'Maximum Tire Care',
  'EnergyMaximizer': 'Energy Aggressive',
  'BalancedRacer': 'Standard Approach',
};

export default function Box3({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { opponents, gameStarted } = useGame();

  // Get top 3 opponents by position
  const topOpponents = opponents
    .slice()
    .sort((a, b) => a.position - b.position)
    .slice(0, 3);

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-sm font-bold text-text-primary mb-4 tracking-wide">OPPONENT STRATEGY</h3>
        <div className="space-y-2">
          {!gameStarted || topOpponents.length === 0 ? (
            <div className="text-xs text-text-secondary">Start race to see opponent strategies</div>
          ) : (
            topOpponents.map((opponent, index) => (
              <div
                key={opponent.name}
                className={`flex items-center justify-between ${
                  index < topOpponents.length - 1 ? 'border-b border-border/20' : ''
                } pb-2`}
              >
                <span className="text-sm text-text-primary">
                  {STRATEGY_LABELS[opponent.agent_type] || 'Unknown Strategy'}
                </span>
                <span className="text-sm text-text-secondary">
                  {opponent.name} (P{opponent.position})
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
