"use client";

import type { CSSProperties, ReactNode } from 'react';
import { useGame } from "@/contexts/GameContext";
import { motion } from "framer-motion";

interface BoxProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

const baseClasses =
  'relative flex h-full w-full flex-col overflow-hidden rounded-2xl border border-border bg-bg-secondary text-text-primary shadow-lg shadow-black/20';

const defaultLayout: CSSProperties = {
  gridColumn: '10 / span 3',
  gridRow: '1 / span 5',
};

const overlayStyle: CSSProperties = {
  display: "none",
};

export default function Box8({ className, style, children }: BoxProps) {
  const composedClassName = className ? `${baseClasses} ${className}` : baseClasses;
  const mergedStyle = style ? { ...defaultLayout, ...style } : defaultLayout;

  const { getCarsForTrack, gameStarted } = useGame();
  const cars = gameStarted ? getCarsForTrack() : [];
  const sortedCars = [...cars].sort((a, b) => a.position - b.position);

  return (
    <section className={composedClassName} style={mergedStyle}>
      <div className="pointer-events-none absolute inset-0 rounded-[inherit]" style={overlayStyle} aria-hidden />
      <div className="relative z-[1] flex flex-1 flex-col p-4">
        <h3 className="absolute top-3 text-sm font-bold text-gray-400 tracking-widest uppercase">
          Live Standings
        </h3>
        <div className="mt-10 flex flex-col space-y-1 overflow-y-auto pr-2">
          {!gameStarted || sortedCars.length === 0 ? (
            <div className="flex items-center justify-center h-full text-xs text-text-secondary">
              Start race to see live standings
            </div>
          ) : (
            sortedCars.map((car, index) => (
              <motion.div
                key={car.id}
                className={`flex items-center space-x-3 p-1.5 rounded-md transition-colors ${
                  car.isUserCar ? 'bg-blue-500/20' : ''
                }`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <span
                  className={`text-sm font-bold w-5 text-center ${
                    car.isUserCar ? 'text-blue-300' : 'text-gray-500'
                  }`}
                >
                  {car.position}
                </span>
                <div className="flex-1">
                  <p
                    className={`text-sm font-semibold truncate ${
                      car.isUserCar ? 'text-blue-100' : 'text-gray-300'
                    }`}
                  >
                    {car.driverName}
                  </p>
                </div>
                <span className="text-xs font-mono text-gray-500 pr-1">{car.lapTime}</span>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}