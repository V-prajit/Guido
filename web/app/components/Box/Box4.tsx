"use client";

import type { CSSProperties, ReactNode } from 'react';
import { useState, useEffect } from 'react';
import { useGame } from "@/contexts/GameContext";
import { getRecommendation } from "@/services/api";

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

interface StrategyDisplay {
  name: string;
  probability: string;
  explanation: string;
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
  const [strategies, setStrategies] = useState<StrategyDisplay[]>([]);
  const [loading, setLoading] = useState(false);

  const { player, currentLap, isRaining, gameStarted } = useGame();

  // Fetch recommendations when player state changes
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!gameStarted || !player) {
        // Show placeholder when no game running
        setStrategies([
          {
            name: "AGGRESSIVE ATTACK",
            probability: "—",
            explanation: "Start race to see AI-powered recommendations"
          },
          {
            name: "CONSERVATIVE PLAY",
            probability: "—",
            explanation: "Strategies will adapt to race conditions"
          },
          {
            name: "BALANCED DRIVE",
            probability: "—",
            explanation: "Real-time analysis from backend"
          }
        ]);
        return;
      }

      setLoading(true);
      try {
        const response = await getRecommendation({
          lap: currentLap,
          battery_soc: player.battery_soc,
          position: player.position,
          rain: isRaining,
          tire_life: player.tire_life,
          fuel_remaining: player.fuel_remaining,
        });

        // Map API response to display format
        const mapped: StrategyDisplay[] = response.recommendations.slice(0, 3).map((rec: any, index: number) => ({
          name: ['AGGRESSIVE ATTACK', 'BALANCED DRIVE', 'CONSERVATIVE PLAY'][index] || 'STRATEGY',
          probability: `${Math.round((rec.confidence || 0.5) * 100)}%`,
          explanation: rec.rationale || rec.expected_outcome || 'No explanation available',
        }));

        setStrategies(mapped.length > 0 ? mapped : [
          {
            name: "NO RECOMMENDATIONS",
            probability: "—",
            explanation: "Unable to generate recommendations at this time"
          }
        ]);
      } catch (error) {
        console.error('[Box4] Failed to fetch recommendations:', error);
        setStrategies([
          {
            name: "ERROR",
            probability: "—",
            explanation: "Failed to connect to backend API"
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    // Debounce API calls - only fetch every 5 laps or when rain starts
    const shouldFetch = gameStarted && player && (currentLap % 5 === 0 || currentLap === 1);
    if (shouldFetch) {
      fetchRecommendations();
    }
  }, [gameStarted, player, currentLap, isRaining]);

  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-6">
        <h3 className="text-lg font-bold text-text-primary mb-6 tracking-wide">
          MULTI-AGENTIC INSIGHTS
        </h3>
        <div className="grid grid-cols-3 gap-4">
          {strategies.map((strategy, index) => (
            <div
              key={`${strategy.name}-${strategy.probability}-${index}`}
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
