"use client";

import type { CSSProperties, ReactNode } from 'react';
import { useState } from 'react';

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '4 / span 6',
  gridRow: '4 / span 5',
};

const overlayStyle: CSSProperties = {
  display: "none",
};
export default function Box4({ className, style, children }: BoxProps) {
  const [selectedStrategy, setSelectedStrategy] = useState<number>(0);

  const strategies = [
    {
      name: "AGGRESSIVE ATTACK",
      probability: "75%",
      explanation: "Rain reduces grip advantage. Deploy power now to gain track position before conditions worsen."
    },
    {
      name: "CONSERVATIVE PLAY",
      probability: "58%",
      explanation: "Maintain current pace and tire management. Wait for opponent mistakes in difficult conditions."
    },
    {
      name: "BALANCED DRIVE",
      probability: "67%",
      explanation: "Moderate push with strategic overtaking. Balance risk and reward for optimal position gain."
    }
  ];

  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-lg font-bold text-text-primary mb-6 tracking-wide">MULTI-AGENTIC INSIGHTS</h3>
        <div className="grid grid-cols-3 gap-4">
          {strategies.map((strategy, index) => (
            <div
              key={index}
              onClick={() => setSelectedStrategy(index)}
              className={`border ${
                selectedStrategy === index ? 'border-text-primary bg-text-primary/5' : 'border-border/40'
              } rounded-lg p-4 cursor-pointer transition-all hover:border-text-primary hover:bg-text-primary/5`}
            >
              <h4 className="text-sm font-bold text-text-primary mb-3">{strategy.name}</h4>
              <p className="text-4xl font-bold text-text-primary mb-4">{strategy.probability}</p>
              <p className="text-xs text-text-secondary leading-relaxed">{strategy.explanation}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
