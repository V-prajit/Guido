"use client";

import type { CSSProperties, ReactNode } from 'react';
import { useState, useEffect } from 'react';
import { useGame } from "@/contexts/GameContext";

// --- BASE STYLES ---
const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';
const defaultLayout: CSSProperties = {
  gridColumn: '4 / span 6',
  gridRow: '4 / span 5',
};

// --- TYPE DEFINITIONS ---
interface Insight {
  name: string;
  value: string;
  explanation: string;
  color: string;
}

// --- HELPER FUNCTIONS ---
const generateInsights = (player: any, isRaining: boolean, currentLap: number): Insight[] => {
  // 1. Pit Stop Window
  const tireFactor = Math.pow(100 - (player?.tire_life ?? 100), 2) / 7000;
  const lapFactor = currentLap > 10 && currentLap < 45 ? 0.1 : 0;
  const pitProbability = Math.min(1, tireFactor + lapFactor) * 100;

  // 2. Overtake Opportunity
  const batteryFactor = (player?.battery_soc ?? 0) / 1000;
  const randomFactor = Math.random() * 0.15;
  const overtakeProbability = Math.min(1, batteryFactor + randomFactor) * 100;

  // 3. Safety Car Risk
  const rainFactor = isRaining ? 0.25 : 0;
  const generalRisk = 0.05 + (Math.sin(currentLap * 3 * Math.PI / 10) * 0.05);
  const safetyCarProbability = Math.min(1, rainFactor + generalRisk) * 100;

  return [
    {
      name: "Pit Window",
      value: `${pitProbability.toFixed(0)}%`,
      explanation: "Likelihood that pitting in the next 2 laps is the optimal strategy.",
      color: '#a78bfa',
    },
    {
      name: "Overtake",
      value: `${overtakeProbability.toFixed(0)}%`,
      explanation: "Probability of a successful overtake attempt on the car ahead.",
      color: '#34d399',
    },
    {
      name: "Safety Car",
      value: `${safetyCarProbability.toFixed(0)}%`,
      explanation: "Risk of a safety car deployment in the current race conditions.",
      color: '#fbbf24',
    },
  ];
};

const placeholderInsights: Insight[] = [
  { name: "Pit Window", value: "—", explanation: "Optimal pit stop timing analysis.", color: '#a78bfa' },
  { name: "Overtake", value: "—", explanation: "Successful overtake probability.", color: '#34d399' },
  { name: "Safety Car", value: "—", explanation: "Risk of a safety car deployment.", color: '#fbbf24' },
];

// --- MAIN COMPONENT ---
export default function Box4({ className, style }: { className?: string; style?: CSSProperties }) {
  const [insights, setInsights] = useState<Insight[]>(placeholderInsights);
  const { player, currentLap, isRaining, gameStarted } = useGame();

  useEffect(() => {
    if (!gameStarted || !player) {
      setInsights(placeholderInsights);
      return;
    }

    // Set initial insights immediately
    setInsights(generateInsights(player, isRaining, currentLap));

    // Then set up the interval for subsequent updates
    const interval = setInterval(() => {
      setInsights(generateInsights(player, isRaining, currentLap));
    }, 2000);

    return () => clearInterval(interval);
  }, [gameStarted, player, currentLap, isRaining]);

  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-lg font-bold text-text-primary mb-6 tracking-wide">
          STRATEGIC INSIGHTS
        </h3>
        <div className="grid grid-cols-3 gap-4 h-full">
          {insights.map((insight) => (
            <div
              key={insight.name}
              className="border border-border/40 rounded-lg p-4 flex flex-col justify-between bg-bg-secondary"
              style={{ borderColor: insight.color, boxShadow: `0 0 20px -5px ${insight.color}30` }}
            >
              <div>
                <h4 className="text-sm font-bold text-text-primary mb-3 uppercase tracking-wider">{insight.name}</h4>
                <p className="text-5xl font-bold text-text-primary mb-4" style={{ color: insight.color }}>{insight.value}</p>
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">{insight.explanation}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
