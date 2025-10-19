"use client";

import type { CSSProperties, ReactNode } from 'react';
import { useGame } from "@/contexts/GameContext";
import { motion } from "framer-motion";

// --- BASE COMPONENT PROPS & STYLES ---
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

// --- EVENT METADATA ---
const EVENT_LABELS: Record<string, string> = {
  RAIN_START: 'Rain forecast prompts strategy review',
  BATTERY_LOW: 'Low battery requires energy saving',
  TIRE_DEGRADED: 'High tire wear suggests pit stop',
  SAFETY_CAR: 'Safety car deployed, opportunity arises',
  OVERTAKE_OPPORTUNITY: 'Overtake chance on rival ahead',
};

const EVENT_ICONS: Record<string, ReactNode> = {
  RAIN_START: (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/>
    </svg>
  ),
  BATTERY_LOW: (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 7h1a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-2"/><path d="M6 7H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h1"/><line x1="7" y1="7" x2="7" y2="17"/><line x1="13" y1="7" x2="13" y2="17"/>
    </svg>
  ),
  TIRE_DEGRADED: (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21.18 10.82a10 10 0 1 0-10.36 10.36"/><path d="M12 2a4.5 4.5 0 0 0-4.5 4.5c0 1.33.62 2.52 1.63 3.29"/><path d="M12 12a4.5 4.5 0 0 0 4.5-4.5c0-1.33-.62-2.52-1.63-3.29"/>
    </svg>
  ),
  SAFETY_CAR: (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.5 19.5 2 15V9l8.5-4.5L19 9v3"/><path d="m10.5 19.5 8.5-4.5"/><path d="M12 11.5V21"/><path d="m2 15 6 3"/><path d="M14 19.12h8"/>
    </svg>
  ),
  OVERTAKE_OPPORTUNITY: (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m5 12 7-7 7 7"/><path d="m5 19 7-7 7 7"/>
    </svg>
  ),
};

const getOutcomeStyle = (outcome?: string) => {
  switch (outcome) {
    case 'success':
      return { bg: 'bg-green-500/10', text: 'text-green-300', iconBg: 'bg-green-500/20' };
    case 'failure':
      return { bg: 'bg-red-500/10', text: 'text-red-300', iconBg: 'bg-red-500/20' };
    default:
      return { bg: 'bg-gray-500/10', text: 'text-gray-400', iconBg: 'bg-gray-500/20' };
  }
};

// --- MAIN COMPONENT ---
export default function Box7({ className, style }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { decisionHistory, gameStarted } = useGame();

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-4">
        <h3 className="absolute top-3 text-sm font-bold text-gray-400 tracking-widest uppercase">
          Decision Log
        </h3>
        <div className="mt-5 flex flex-col space-y-2 overflow-y-auto pr-2 flex-grow">
          {!gameStarted || decisionHistory.length === 0 ? (
            <div className="flex items-center justify-center h-full text-xs text-text-secondary">
              No decisions made yet
            </div>
          ) : (
            decisionHistory.slice().reverse().map((decision, index) => {
              const { bg, text, iconBg } = getOutcomeStyle(decision.outcome);
              return (
                <motion.div
                  key={`${decision.lap}-${decision.timestamp}`}
                  className={`flex items-center space-x-3 p-2 rounded-lg ${bg}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${iconBg} ${text}`}>
                    {EVENT_ICONS[decision.event_type] || '!'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-200 truncate">
                      {EVENT_LABELS[decision.event_type] || decision.event_type}
                    </p>
                    <p className={`text-xs ${text} font-medium`}>
                      Lap {decision.lap} &bull; {decision.outcome ? `Outcome: ${decision.outcome}` : 'Strategy Executed'}
                    </p>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </section>
  );
}