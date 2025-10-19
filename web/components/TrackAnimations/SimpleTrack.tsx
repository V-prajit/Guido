"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

// Type definitions
interface CarData {
  id: string;
  driverName: string;
  position: number;
  lapProgress: number;
  speed: number;
  lapTime: string;
  isUserCar: boolean;
}

interface TrackPoint {
  x: number;
  y: number;
}

// Mock data for cars
const MOCK_CARS: CarData[] = [
  {
    id: "car-1",
    driverName: "You",
    position: 1,
    lapProgress: 0.75,
    speed: 312,
    lapTime: "1:32.145",
    isUserCar: true,
  },
  {
    id: "car-2",
    driverName: "Verstappen",
    position: 2,
    lapProgress: 0.68,
    speed: 308,
    lapTime: "1:32.389",
    isUserCar: false,
  },
  {
    id: "car-3",
    driverName: "Hamilton",
    position: 3,
    lapProgress: 0.54,
    speed: 295,
    lapTime: "1:32.891",
    isUserCar: false,
  },
  {
    id: "car-4",
    driverName: "Leclerc",
    position: 4,
    lapProgress: 0.42,
    speed: 287,
    lapTime: "1:33.125",
    isUserCar: false,
  },
];

// Simplified Bahrain International Circuit path
const BAHRAIN_TRACK_PATH = `
  M 120 280
  L 180 280
  Q 220 280 230 260
  L 250 200
  Q 255 185 270 180
  L 340 170
  Q 360 168 370 155
  L 390 100
  Q 395 85 410 80
  L 480 75
  Q 500 74 510 60
  L 530 20
  Q 535 10 545 10
  Q 560 10 565 20
  L 585 60
  Q 590 70 600 72
  L 650 80
  Q 665 82 670 95
  L 680 130
  Q 682 145 695 150
  L 740 160
  Q 755 162 760 175
  L 770 210
  Q 772 225 760 235
  L 720 260
  Q 705 270 705 285
  L 705 340
  Q 705 355 690 360
  L 620 375
  Q 600 378 595 390
  L 580 420
  Q 575 435 560 438
  L 480 445
  Q 460 446 455 430
  L 445 400
  Q 442 385 430 380
  L 360 365
  Q 340 362 335 350
  L 320 310
  Q 318 295 305 290
  L 240 275
  Q 220 272 215 285
  L 200 320
  Q 195 335 180 338
  L 135 345
  Q 115 346 110 330
  L 100 295
  Q 98 285 108 280
  L 120 280
  Z
`;

// Calculate point on path at given progress (0-1)
const getPointOnPath = (progress: number, pathElement: SVGPathElement): TrackPoint => {
  const length = pathElement.getTotalLength();
  const point = pathElement.getPointAtLength(progress * length);
  return { x: point.x, y: point.y };
};

const SimpleTrack: React.FC<{ cars?: CarData[] }> = ({ cars = MOCK_CARS }) => {
  const [animatedCars, setAnimatedCars] = useState<CarData[]>(cars);
  const pathRef = React.useRef<SVGPathElement>(null);

  // Simulate car movement
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimatedCars((prevCars) =>
        prevCars.map((car) => {
          const speedFactor = car.speed / 300;
          const progressIncrement = 0.002 * speedFactor;

          let newProgress = car.lapProgress + progressIncrement;

          if (newProgress >= 1) {
            newProgress = newProgress - 1;
          }

          let newSpeed = car.speed;
          if (newProgress > 0.05 && newProgress < 0.15) {
            newSpeed = Math.max(car.speed * 0.85, 180);
          } else if (newProgress > 0.45 && newProgress < 0.55) {
            newSpeed = Math.max(car.speed * 0.90, 220);
          } else {
            const maxSpeed = car.isUserCar ? 315 : 300 - (car.position * 5);
            newSpeed = Math.min(car.speed + 2, maxSpeed);
          }

          return {
            ...car,
            lapProgress: newProgress,
            speed: Math.round(newSpeed),
          };
        })
      );
    }, 50);

    return () => clearInterval(interval);
  }, []);

  // Calculate car positions
  const getCarPosition = (lapProgress: number): TrackPoint => {
    if (!pathRef.current) return { x: 120, y: 280 };
    return getPointOnPath(lapProgress, pathRef.current);
  };

  return (
    <div className="w-full h-full flex items-center justify-center bg-zinc-950">
      <svg
        viewBox="0 0 850 500"
        className="w-full h-full"
        style={{ filter: "drop-shadow(0 0 20px rgba(239, 68, 68, 0.15))" }}
      >
        {/* Track Background Glow */}
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Gradient for track */}
          <linearGradient id="trackGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#dc2626" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#b91c1c" stopOpacity="0.8" />
          </linearGradient>
        </defs>

        {/* Main Track */}
        <path
          ref={pathRef}
          d={BAHRAIN_TRACK_PATH}
          fill="none"
          stroke="url(#trackGradient)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#glow)"
          opacity="0.95"
        />

        {/* Inner track line for depth */}
        <path
          d={BAHRAIN_TRACK_PATH}
          fill="none"
          stroke="#991b1b"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.4"
        />

        {/* Start/Finish Line */}
        <motion.line
          x1="115"
          y1="275"
          x2="115"
          y2="295"
          stroke="#ffffff"
          strokeWidth="3"
          strokeLinecap="round"
          initial={{ opacity: 0.5 }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Cars */}
        {animatedCars.map((car) => {
          const position = getCarPosition(car.lapProgress);

          return (
            <g key={car.id}>
              {/* Car glow effect */}
              <motion.circle
                cx={position.x}
                cy={position.y}
                r={car.isUserCar ? 12 : 10}
                fill={car.isUserCar ? "#3b82f6" : "#ffffff"}
                opacity={0.2}
                initial={{ scale: 1 }}
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
              />

              {/* Main car dot */}
              <motion.circle
                cx={position.x}
                cy={position.y}
                r={car.isUserCar ? 8 : 6}
                fill={car.isUserCar ? "#3b82f6" : "#ffffff"}
                initial={{ scale: 0 }}
                animate={{
                  scale: 1,
                  filter: car.isUserCar
                    ? "drop-shadow(0 0 8px rgba(59, 130, 246, 0.8))"
                    : "drop-shadow(0 0 4px rgba(255, 255, 255, 0.6))"
                }}
                transition={{
                  scale: { type: "spring", stiffness: 300, damping: 20 },
                  filter: { duration: 0.3 }
                }}
              />

              {/* Position indicator ring for user car */}
              {car.isUserCar && (
                <motion.circle
                  cx={position.x}
                  cy={position.y}
                  r={14}
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="1.5"
                  opacity={0.6}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{
                    scale: [1, 1.4, 1],
                    opacity: [0.6, 0.2, 0.6]
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default SimpleTrack;
