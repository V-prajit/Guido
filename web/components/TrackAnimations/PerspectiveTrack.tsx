'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

// Mock data structure for race positions
interface CarPosition {
  id: string;
  driver: string;
  position: number; // 0-100 (percentage along track)
  lane: number; // 0-1 (left to right across track width)
  isUser?: boolean;
}

// Bahrain track layout - simplified with key turns
const BAHRAIN_TRACK_POINTS = [
  // Start/Finish straight
  { x: 50, y: 80 },
  { x: 50, y: 60 },

  // Turn 1 (heavy braking)
  { x: 55, y: 50 },
  { x: 65, y: 45 },

  // Turn 2-3 complex
  { x: 75, y: 40 },
  { x: 80, y: 35 },
  { x: 82, y: 30 },

  // Back straight
  { x: 82, y: 20 },
  { x: 80, y: 15 },

  // Turn 4
  { x: 75, y: 12 },
  { x: 70, y: 10 },

  // Middle section
  { x: 60, y: 10 },
  { x: 50, y: 12 },
  { x: 40, y: 15 },

  // Turn 8-9
  { x: 30, y: 20 },
  { x: 25, y: 25 },
  { x: 22, y: 30 },

  // Turn 10
  { x: 20, y: 40 },
  { x: 18, y: 50 },

  // Turn 11-12-13
  { x: 20, y: 60 },
  { x: 25, y: 68 },
  { x: 32, y: 72 },

  // Final sector
  { x: 40, y: 75 },
  { x: 50, y: 80 }, // Back to start
];

// Calculate 3D perspective position
const calculatePerspectivePosition = (
  x: number,
  y: number,
  viewAngle: number = 45
): { x: number; y: number; scale: number; zIndex: number } => {
  // Isometric projection with depth
  // Higher Y values = closer to viewer (bottom of screen)
  // Lower Y values = farther from viewer (top of screen)

  const depth = (100 - y) / 100; // 0 = close, 1 = far
  const perspective = 0.6; // Perspective strength

  // Scale based on depth (farther = smaller)
  const scale = 1 - (depth * perspective);

  // Isometric angle transformation (30 degrees)
  const isoAngle = Math.PI / 6; // 30 degrees
  const isoX = x + (y * Math.cos(isoAngle) * 0.3);
  const isoY = y * 0.8 - (depth * 20); // Compress Y and add depth

  // Z-index for proper layering
  const zIndex = Math.floor(y);

  return { x: isoX, y: isoY, scale, zIndex };
};

// Get position on track based on progress percentage
const getTrackPosition = (
  progress: number,
  laneOffset: number = 0
): { x: number; y: number } => {
  const totalPoints = BAHRAIN_TRACK_POINTS.length;
  const segment = (progress / 100) * (totalPoints - 1);
  const index = Math.floor(segment);
  const fraction = segment - index;

  const p1 = BAHRAIN_TRACK_POINTS[index];
  const p2 = BAHRAIN_TRACK_POINTS[(index + 1) % totalPoints];

  // Interpolate between points
  const baseX = p1.x + (p2.x - p1.x) * fraction;
  const baseY = p1.y + (p2.y - p1.y) * fraction;

  // Add lane offset (perpendicular to track direction)
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const length = Math.sqrt(dx * dx + dy * dy);
  const perpX = -dy / length;
  const perpY = dx / length;

  return {
    x: baseX + perpX * laneOffset * 3,
    y: baseY + perpY * laneOffset * 3,
  };
};

// Generate track path with 3D effect
const generateTrackPath = (): string => {
  const perspectivePoints = BAHRAIN_TRACK_POINTS.map((point) => {
    const pos = calculatePerspectivePosition(point.x, point.y);
    return `${pos.x},${pos.y}`;
  });

  return `M ${perspectivePoints.join(' L ')} Z`;
};

// Generate shadow/depth path (offset for 3D effect)
const generateShadowPath = (): string => {
  const shadowOffset = 2;
  const perspectivePoints = BAHRAIN_TRACK_POINTS.map((point) => {
    const pos = calculatePerspectivePosition(point.x, point.y + shadowOffset);
    return `${pos.x + 1},${pos.y + 1}`;
  });

  return `M ${perspectivePoints.join(' L ')} Z`;
};

const PerspectiveTrack: React.FC = () => {
  // Mock car data - replace with real race data
  const [cars, setCars] = useState<CarPosition[]>([
    { id: 'user', driver: 'You', position: 0, lane: 0.5, isUser: true },
    { id: 'car1', driver: 'VER', position: 15, lane: 0.3 },
    { id: 'car2', driver: 'LEC', position: 8, lane: 0.7 },
    { id: 'car3', driver: 'HAM', position: 25, lane: 0.4 },
  ]);

  // Animate cars around track
  useEffect(() => {
    const interval = setInterval(() => {
      setCars((prevCars) =>
        prevCars.map((car) => ({
          ...car,
          position: (car.position + (car.isUser ? 0.5 : 0.4)) % 100,
          // Slight lane variation for realism
          lane: 0.5 + Math.sin((car.position / 100) * Math.PI * 4) * 0.2,
        }))
      );
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const trackPath = generateTrackPath();
  const shadowPath = generateShadowPath();

  return (
    <div className="w-full h-full min-h-[600px] bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 rounded-lg overflow-hidden relative">
      <svg
        viewBox="0 0 120 100"
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
        style={{
          filter: 'drop-shadow(0 10px 30px rgba(0,0,0,0.5))',
        }}
      >
        <defs>
          {/* Track gradient for 3D depth */}
          <linearGradient id="trackGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#dc2626" stopOpacity="0.7" />
            <stop offset="50%" stopColor="#dc2626" stopOpacity="1" />
            <stop offset="100%" stopColor="#991b1b" stopOpacity="0.9" />
          </linearGradient>

          {/* Shadow gradient */}
          <linearGradient id="shadowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#000000" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#000000" stopOpacity="0.6" />
          </linearGradient>

          {/* User car glow */}
          <radialGradient id="userGlow">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="1" />
            <stop offset="70%" stopColor="#1d4ed8" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#1e3a8a" stopOpacity="0.4" />
          </radialGradient>

          {/* Other cars gradient */}
          <radialGradient id="carGlow">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
            <stop offset="70%" stopColor="#e5e7eb" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#9ca3af" stopOpacity="0.5" />
          </radialGradient>
        </defs>

        {/* Track shadow (3D depth) */}
        <motion.path
          d={shadowPath}
          fill="url(#shadowGradient)"
          stroke="none"
          strokeWidth="0"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        />

        {/* Main track */}
        <motion.path
          d={trackPath}
          fill="none"
          stroke="url(#trackGradient)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 2, ease: 'easeInOut' }}
        />

        {/* Track edge lines for depth */}
        <motion.path
          d={trackPath}
          fill="none"
          stroke="rgba(255, 255, 255, 0.2)"
          strokeWidth="0.3"
          strokeDasharray="2,2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
        />

        {/* Start/Finish line with perspective */}
        {(() => {
          const startPos = getTrackPosition(0, 0);
          const perspStart = calculatePerspectivePosition(startPos.x, startPos.y);
          const perpX = -2;
          const perpY = 0;

          return (
            <motion.line
              x1={perspStart.x - perpX}
              y1={perspStart.y - perpY}
              x2={perspStart.x + perpX}
              y2={perspStart.y + perpY}
              stroke="white"
              strokeWidth="0.8"
              strokeDasharray="1,1"
              initial={{ opacity: 0 }}
              animate={{ opacity: [0, 1, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            />
          );
        })()}

        {/* Cars with perspective scaling */}
        {cars.map((car) => {
          const trackPos = getTrackPosition(car.position, car.lane - 0.5);
          const perspPos = calculatePerspectivePosition(trackPos.x, trackPos.y);

          // Car size based on perspective and type
          const baseSize = car.isUser ? 3 : 2.5;
          const carSize = baseSize * perspPos.scale;

          return (
            <g key={car.id} style={{ zIndex: perspPos.zIndex }}>
              {/* Car glow effect */}
              <motion.circle
                cx={perspPos.x}
                cy={perspPos.y}
                r={carSize * 1.5}
                fill={car.isUser ? 'url(#userGlow)' : 'url(#carGlow)'}
                opacity={0.4}
                initial={{ scale: 0 }}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.4, 0.6, 0.4],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />

              {/* Main car body */}
              <motion.circle
                cx={perspPos.x}
                cy={perspPos.y}
                r={carSize}
                fill={car.isUser ? '#3b82f6' : '#ffffff'}
                stroke={car.isUser ? '#1d4ed8' : '#d1d5db'}
                strokeWidth={0.3 * perspPos.scale}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  type: 'spring',
                  stiffness: 300,
                  damping: 20,
                }}
              />

              {/* Car highlight for 3D effect */}
              <motion.circle
                cx={perspPos.x - carSize * 0.2}
                cy={perspPos.y - carSize * 0.2}
                r={carSize * 0.3}
                fill="rgba(255, 255, 255, 0.6)"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.6, 0.8, 0.6] }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />

              {/* Driver label - larger when close, smaller when far */}
              <motion.text
                x={perspPos.x}
                y={perspPos.y - carSize - 2}
                textAnchor="middle"
                fill={car.isUser ? '#60a5fa' : '#ffffff'}
                fontSize={2 * perspPos.scale}
                fontWeight="bold"
                style={{
                  textShadow: '0 0 3px rgba(0,0,0,0.8)',
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                {car.driver}
              </motion.text>

              {/* Speed lines effect when moving */}
              {[...Array(3)].map((_, i) => (
                <motion.line
                  key={i}
                  x1={perspPos.x - carSize * 1.5}
                  y1={perspPos.y + (i - 1) * 0.5}
                  x2={perspPos.x - carSize * 2.5}
                  y2={perspPos.y + (i - 1) * 0.5}
                  stroke={car.isUser ? '#3b82f6' : '#ffffff'}
                  strokeWidth={0.2 * perspPos.scale}
                  strokeLinecap="round"
                  initial={{ opacity: 0 }}
                  animate={{
                    opacity: [0, 0.6, 0],
                    x1: [perspPos.x - carSize * 1.5, perspPos.x - carSize * 3],
                    x2: [perspPos.x - carSize * 2.5, perspPos.x - carSize * 4],
                  }}
                  transition={{
                    duration: 0.5,
                    repeat: Infinity,
                    delay: i * 0.1,
                    ease: 'easeOut',
                  }}
                />
              ))}
            </g>
          );
        })}
      </svg>

      {/* Track info overlay */}
      <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/20">
        <h3 className="text-white font-bold text-sm mb-1">Bahrain International Circuit</h3>
        <p className="text-gray-300 text-xs">3D Perspective View</p>
      </div>

      {/* Position info */}
      <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/20">
        <div className="space-y-1">
          {cars
            .sort((a, b) => b.position - a.position)
            .map((car, idx) => (
              <div
                key={car.id}
                className={`flex items-center gap-2 text-xs ${
                  car.isUser ? 'text-blue-400 font-bold' : 'text-white'
                }`}
              >
                <span className="w-4 text-gray-400">P{idx + 1}</span>
                <span
                  className={`w-2 h-2 rounded-full ${
                    car.isUser ? 'bg-blue-500' : 'bg-white'
                  }`}
                />
                <span>{car.driver}</span>
              </div>
            ))}
        </div>
      </div>

      {/* Visual depth indicator */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center gap-2 text-xs text-gray-400">
        <div className="w-2 h-2 rounded-full bg-white opacity-30" />
        <span>Far</span>
        <div className="w-1 h-8 bg-gradient-to-b from-white/30 to-white/70 rounded" />
        <span>Near</span>
        <div className="w-2 h-2 rounded-full bg-white opacity-70" />
      </div>
    </div>
  );
};

export default PerspectiveTrack;
