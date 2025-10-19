"use client";

/**
 * BOX 1: RACE TRACK VIEW
 *
 * This is a standalone component for the race track visualization
 * using the actual Bahrain International Circuit GeoJSON coordinates.
 *
 * INTEGRATION INSTRUCTIONS:
 * 1. Copy this file to your components/BentoBoxes folder
 * 2. Import: import Box1_RaceTrack from '@/components/BentoBoxes/Box1_RaceTrack'
 * 3. Use: <Box1_RaceTrack />
 *
 * DEPENDENCIES:
 * - framer-motion (npm install framer-motion)
 *
 * PROPS:
 * - cars (optional): Array of car data to override mock data
 */

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

// Type definitions
interface CarData {
  id: string;
  driverName: string;
  position: number;
  lapProgress: number; // 0 to 1
  speed: number; // km/h
  lapTime: string;
  isUserCar: boolean;
}

interface TrackPoint {
  x: number;
  y: number;
}

// Mock data - replace with real data from your backend
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

// Real Bahrain International Circuit coordinates from GeoJSON
// Converted and scaled for SVG viewport
const BAHRAIN_TRACK_COORDINATES = [
  [50.510539, 26.031766], [50.510633, 26.034797], [50.510722, 26.036782],
  [50.510764, 26.036871], [50.510852, 26.036885], [50.510947, 26.036862],
  [50.511018, 26.036815], [50.511474, 26.0364], [50.511598, 26.036358],
  [50.511734, 26.036367], [50.512527, 26.036598], [50.512717, 26.036617],
  [50.512889, 26.036607], [50.518091, 26.035702], [50.518269, 26.035655],
  [50.518364, 26.035566], [50.518387, 26.035452], [50.518369, 26.035344],
  [50.51831, 26.035222], [50.518198, 26.035099], [50.518068, 26.035],
  [50.51789, 26.034877], [50.517263, 26.034458], [50.516759, 26.033987],
  [50.516635, 26.033878], [50.516535, 26.033723], [50.51631, 26.033265],
  [50.516233, 26.033166], [50.516114, 26.033096], [50.515996, 26.033039],
  [50.515807, 26.03302], [50.515238, 26.033105], [50.515084, 26.0331],
  [50.514925, 26.033072], [50.514794, 26.033011], [50.514635, 26.032879],
  [50.51348, 26.031564], [50.513368, 26.031474], [50.513208, 26.031451],
  [50.513108, 26.031521], [50.513072, 26.031663], [50.513078, 26.031879],
  [50.513356, 26.033369], [50.513516, 26.034302], [50.51354, 26.034486],
  [50.51351, 26.034656], [50.513469, 26.034783], [50.513386, 26.03491],
  [50.512912, 26.035278], [50.512847, 26.035306], [50.512776, 26.035288],
  [50.512735, 26.035222], [50.512563, 26.034071], [50.512516, 26.033303],
  [50.512433, 26.031922], [50.512374, 26.030479], [50.512314, 26.029164],
  [50.512338, 26.028948], [50.512433, 26.02882], [50.512581, 26.02875],
  [50.512788, 26.028712], [50.513001, 26.028726], [50.513267, 26.028773],
  [50.51354, 26.028891], [50.51377, 26.029037], [50.513995, 26.029244],
  [50.514132, 26.029447], [50.514386, 26.030041], [50.514528, 26.030291],
  [50.514664, 26.030437], [50.514842, 26.030569], [50.515055, 26.030687],
  [50.515351, 26.030753], [50.515676, 26.030758], [50.515907, 26.03071],
  [50.516215, 26.030578], [50.517026, 26.030216], [50.517192, 26.030107],
  [50.517334, 26.02998], [50.517405, 26.029862], [50.517493, 26.02973],
  [50.517493, 26.029612], [50.517422, 26.02949], [50.51728, 26.029367],
  [50.517085, 26.029235], [50.510941, 26.026143], [50.510829, 26.026091],
  [50.510651, 26.026086], [50.510574, 26.026152], [50.510302, 26.026671],
  [50.510278, 26.026878], [50.510284, 26.027269], [50.510361, 26.029414],
  [50.510539, 26.031766]
];

// Convert GeoJSON coordinates to SVG path
function convertToSVGPath(coordinates: number[][]): string {
  // Find bounds
  const lons = coordinates.map(c => c[0]);
  const lats = coordinates.map(c => c[1]);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);

  // Scale to SVG viewport (800x500 with padding)
  const padding = 50;
  const width = 800 - (padding * 2);
  const height = 500 - (padding * 2);

  const scaledPoints = coordinates.map(([lon, lat]) => {
    const x = ((lon - minLon) / (maxLon - minLon)) * width + padding;
    const y = ((maxLat - lat) / (maxLat - minLat)) * height + padding; // Flip Y
    return [x, y];
  });

  // Create SVG path
  let path = `M ${scaledPoints[0][0]} ${scaledPoints[0][1]}`;
  for (let i = 1; i < scaledPoints.length; i++) {
    path += ` L ${scaledPoints[i][0]} ${scaledPoints[i][1]}`;
  }
  path += " Z";

  return path;
}

const BAHRAIN_TRACK_PATH = convertToSVGPath(BAHRAIN_TRACK_COORDINATES);

// Calculate point on path
const getPointOnPath = (progress: number, pathElement: SVGPathElement): TrackPoint => {
  const length = pathElement.getTotalLength();
  const point = pathElement.getPointAtLength(progress * length);
  return { x: point.x, y: point.y };
};

// Main Component
interface Box1_RaceTrackProps {
  cars?: CarData[];
}

const Box1_RaceTrack: React.FC<Box1_RaceTrackProps> = ({ cars = MOCK_CARS }) => {
  const [animatedCars, setAnimatedCars] = useState<CarData[]>(cars);
  const pathRef = React.useRef<SVGPathElement>(null);

  // Animate cars
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimatedCars((prevCars) =>
        prevCars.map((car) => {
          const speedFactor = car.speed / 300;
          const progressIncrement = 0.002 * speedFactor;

          let newProgress = car.lapProgress + progressIncrement;
          if (newProgress >= 1) newProgress = newProgress - 1;

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

  const getCarPosition = (lapProgress: number): TrackPoint => {
    if (!pathRef.current) return { x: 100, y: 250 };
    return getPointOnPath(lapProgress, pathRef.current);
  };

  return (
    <div className="col-span-3 bg-white border border-black rounded-lg p-4">
      <h3 className="text-sm font-bold text-black mb-3 tracking-wide">RACE TRACK VIEW</h3>
      <div className="h-[400px] -mx-4 -mb-4">
        <div className="w-full h-full flex items-center justify-center bg-zinc-950">
          <svg
            viewBox="0 0 800 500"
            className="w-full h-full"
            style={{ filter: "drop-shadow(0 0 20px rgba(239, 68, 68, 0.15))" }}
          >
            <defs>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>

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

            {/* Inner track line */}
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
              x1={BAHRAIN_TRACK_COORDINATES[0][0] * 10 - 455}
              y1={BAHRAIN_TRACK_COORDINATES[0][1] * 10 - 220}
              x2={BAHRAIN_TRACK_COORDINATES[0][0] * 10 - 445}
              y2={BAHRAIN_TRACK_COORDINATES[0][1] * 10 - 220}
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
                  {/* Car glow */}
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

                  {/* User car ring */}
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
      </div>
    </div>
  );
};

export default Box1_RaceTrack;
