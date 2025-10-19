'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Mock data structure for race positions
interface CarPosition {
  id: string;
  driver: string;
  team: string;
  position: number;
  progress: number; // 0-100 percentage of lap completion
  speed: number; // km/h
  color: string;
  isUser?: boolean;
}

// Mock race data
const mockRaceData: CarPosition[] = [
  {
    id: '1',
    driver: 'Hamilton',
    team: 'Mercedes',
    position: 1,
    progress: 45,
    speed: 305,
    color: '#00FFFF',
    isUser: true,
  },
  {
    id: '2',
    driver: 'Verstappen',
    team: 'Red Bull',
    position: 2,
    progress: 42,
    speed: 302,
    color: '#FFFFFF',
  },
  {
    id: '3',
    driver: 'Leclerc',
    team: 'Ferrari',
    position: 3,
    progress: 38,
    speed: 298,
    color: '#FFFFFF',
  },
  {
    id: '4',
    driver: 'Norris',
    team: 'McLaren',
    position: 4,
    progress: 35,
    speed: 295,
    color: '#FFFFFF',
  },
];

// Bahrain International Circuit simplified path (approximation)
const bahrainTrackPath = `
  M 150,280
  C 150,280 140,260 140,240
  C 140,220 145,200 160,185
  C 175,170 200,165 220,165
  L 280,165
  C 300,165 315,160 325,145
  C 335,130 335,110 325,95
  C 315,80 300,75 280,75
  L 180,75
  C 160,75 145,70 135,55
  C 125,40 125,20 135,10
  C 145,0 160,0 180,5
  L 420,5
  C 440,5 455,10 465,25
  C 475,40 475,60 465,75
  C 455,90 440,95 420,95
  L 380,95
  C 360,95 350,105 350,120
  L 350,160
  C 350,180 360,190 380,190
  L 460,190
  C 480,190 495,200 505,220
  C 515,240 515,270 505,290
  C 495,310 480,320 460,320
  L 380,320
  C 360,320 345,330 335,350
  C 325,370 325,400 335,420
  C 345,440 360,450 380,450
  L 420,450
  C 440,450 450,460 450,475
  C 450,490 440,500 420,500
  L 200,500
  C 180,500 165,490 155,475
  C 145,460 145,440 155,425
  C 165,410 180,405 200,405
  L 240,405
  C 260,405 270,395 270,380
  L 270,340
  C 270,320 260,310 240,310
  L 180,310
  C 165,310 155,300 150,285
  Z
`;

// Particle effect for trailing
interface Particle {
  id: string;
  x: number;
  y: number;
  opacity: number;
  size: number;
}

const NeonTrack: React.FC = () => {
  const [cars, setCars] = useState<CarPosition[]>(mockRaceData);
  const [particles, setParticles] = useState<Particle[]>([]);

  // Simulate race progression
  useEffect(() => {
    const interval = setInterval(() => {
      setCars((prevCars) =>
        prevCars.map((car) => ({
          ...car,
          progress: (car.progress + (car.speed / 3000)) % 100,
          speed: car.speed + (Math.random() - 0.5) * 10,
        }))
      );
    }, 50);

    return () => clearInterval(interval);
  }, []);

  // Generate particles based on car positions
  useEffect(() => {
    const particleInterval = setInterval(() => {
      const newParticles: Particle[] = [];

      cars.forEach((car) => {
        const pathElement = document.getElementById('track-path');
        if (pathElement) {
          const pathLength = (pathElement as SVGPathElement).getTotalLength();
          const point = (pathElement as SVGPathElement).getPointAtLength(
            (car.progress / 100) * pathLength
          );

          // Add trailing particles for user car
          if (car.isUser) {
            for (let i = 0; i < 2; i++) {
              newParticles.push({
                id: `${car.id}-${Date.now()}-${i}`,
                x: point.x + (Math.random() - 0.5) * 8,
                y: point.y + (Math.random() - 0.5) * 8,
                opacity: 0.8,
                size: Math.random() * 4 + 2,
              });
            }
          }
        }
      });

      setParticles((prev) => [...prev, ...newParticles].slice(-150));
    }, 100);

    return () => clearInterval(particleInterval);
  }, [cars]);

  // Calculate car position on path
  const getCarPosition = (progress: number) => {
    const pathElement = document.getElementById('track-path');
    if (!pathElement) return { x: 0, y: 0 };

    const pathLength = (pathElement as SVGPathElement).getTotalLength();
    const point = (pathElement as SVGPathElement).getPointAtLength(
      (progress / 100) * pathLength
    );

    return { x: point.x, y: point.y };
  };

  // Calculate glow intensity based on speed
  const getGlowIntensity = (speed: number) => {
    const minSpeed = 250;
    const maxSpeed = 350;
    const normalized = (speed - minSpeed) / (maxSpeed - minSpeed);
    return Math.max(0.4, Math.min(1, normalized));
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-black via-gray-950 to-black overflow-hidden">
      {/* Background grid effect */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255, 0, 0, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 0, 0, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      {/* Scanline effect */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'linear-gradient(transparent 50%, rgba(0, 255, 255, 0.03) 50%)',
          backgroundSize: '100% 4px',
        }}
        animate={{
          backgroundPosition: ['0% 0%', '0% 100%'],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'linear',
        }}
      />

      <svg
        width="600"
        height="550"
        viewBox="0 0 600 550"
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
        style={{ filter: 'drop-shadow(0 0 20px rgba(255, 0, 0, 0.3))' }}
      >
        <defs>
          {/* Red neon glow filters for track */}
          <filter id="track-glow-outer" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="8" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="track-glow-middle" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="track-glow-inner" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Blue neon glow for user car */}
          <filter id="user-car-glow" x="-200%" y="-200%" width="500%" height="500%">
            <feGaussianBlur stdDeviation="8" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* White glow for other cars */}
          <filter id="car-glow" x="-200%" y="-200%" width="500%" height="500%">
            <feGaussianBlur stdDeviation="5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Radial gradients for cars */}
          <radialGradient id="user-car-gradient">
            <stop offset="0%" stopColor="#00FFFF" stopOpacity="1" />
            <stop offset="50%" stopColor="#0099FF" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#0066FF" stopOpacity="0.3" />
          </radialGradient>

          <radialGradient id="car-gradient">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="1" />
            <stop offset="50%" stopColor="#CCCCCC" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#888888" stopOpacity="0.3" />
          </radialGradient>
        </defs>

        {/* Track layers - outer glow (thickest, most diffuse) */}
        <path
          d={bahrainTrackPath}
          fill="none"
          stroke="#FF0000"
          strokeWidth="18"
          strokeOpacity="0.3"
          filter="url(#track-glow-outer)"
        />

        {/* Track layers - middle glow */}
        <path
          d={bahrainTrackPath}
          fill="none"
          stroke="#FF1111"
          strokeWidth="12"
          strokeOpacity="0.5"
          filter="url(#track-glow-middle)"
        />

        {/* Track layers - inner glow */}
        <path
          d={bahrainTrackPath}
          fill="none"
          stroke="#FF3333"
          strokeWidth="8"
          strokeOpacity="0.7"
          filter="url(#track-glow-inner)"
        />

        {/* Track core - brightest */}
        <path
          id="track-path"
          d={bahrainTrackPath}
          fill="none"
          stroke="#FF6666"
          strokeWidth="4"
          strokeOpacity="1"
        />

        {/* Animated pulse on track */}
        <motion.path
          d={bahrainTrackPath}
          fill="none"
          stroke="#FF0000"
          strokeWidth="6"
          strokeOpacity="0.6"
          filter="url(#track-glow-middle)"
          animate={{
            strokeOpacity: [0.3, 0.7, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* Particle trails */}
        <AnimatePresence>
          {particles.map((particle) => (
            <motion.circle
              key={particle.id}
              cx={particle.x}
              cy={particle.y}
              r={particle.size}
              fill="#00FFFF"
              initial={{ opacity: particle.opacity, scale: 1 }}
              animate={{ opacity: 0, scale: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5 }}
              filter="url(#user-car-glow)"
            />
          ))}
        </AnimatePresence>

        {/* Render cars */}
        {cars.map((car) => {
          const position = getCarPosition(car.progress);
          const glowIntensity = getGlowIntensity(car.speed);
          const isUser = car.isUser;

          return (
            <g key={car.id}>
              {/* Car trail effect */}
              {isUser && (
                <>
                  <motion.circle
                    cx={position.x}
                    cy={position.y}
                    r="12"
                    fill="url(#user-car-gradient)"
                    opacity="0.2"
                    animate={{
                      scale: [1, 1.5, 1],
                      opacity: [0.2, 0.1, 0.2],
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  />
                  <motion.circle
                    cx={position.x}
                    cy={position.y}
                    r="18"
                    fill="url(#user-car-gradient)"
                    opacity="0.1"
                    animate={{
                      scale: [1, 1.8, 1],
                      opacity: [0.1, 0.05, 0.1],
                    }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  />
                </>
              )}

              {/* Main car body with dynamic glow */}
              <motion.circle
                cx={position.x}
                cy={position.y}
                r={isUser ? 7 : 5}
                fill={isUser ? 'url(#user-car-gradient)' : 'url(#car-gradient)'}
                filter={isUser ? 'url(#user-car-glow)' : 'url(#car-glow)'}
                animate={{
                  opacity: [glowIntensity * 0.8, glowIntensity, glowIntensity * 0.8],
                }}
                transition={{
                  duration: 0.5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />

              {/* Core bright spot */}
              <circle
                cx={position.x}
                cy={position.y}
                r={isUser ? 3 : 2}
                fill={isUser ? '#FFFFFF' : '#EEEEEE'}
                opacity={glowIntensity}
              />

              {/* Speed indicator ring */}
              {car.speed > 300 && (
                <motion.circle
                  cx={position.x}
                  cy={position.y}
                  r={isUser ? 10 : 8}
                  fill="none"
                  stroke={isUser ? '#00FFFF' : '#FFFFFF'}
                  strokeWidth="1"
                  opacity="0.6"
                  animate={{
                    r: [isUser ? 10 : 8, isUser ? 16 : 14],
                    opacity: [0.6, 0],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    ease: 'easeOut',
                  }}
                />
              )}
            </g>
          );
        })}
      </svg>

      {/* HUD/UI Elements */}
      <div className="absolute top-8 left-8 font-mono text-cyan-400">
        <motion.div
          className="text-2xl font-bold mb-4"
          style={{
            textShadow: '0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.4)',
          }}
          animate={{
            textShadow: [
              '0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.4)',
              '0 0 15px rgba(0, 255, 255, 1), 0 0 30px rgba(0, 255, 255, 0.6)',
              '0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.4)',
            ],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          BAHRAIN GP
        </motion.div>

        <div className="space-y-2 text-sm">
          {cars.map((car, index) => (
            <motion.div
              key={car.id}
              className={`flex items-center gap-3 ${
                car.isUser ? 'text-cyan-300 font-bold' : 'text-white'
              }`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              style={
                car.isUser
                  ? {
                      textShadow:
                        '0 0 8px rgba(0, 255, 255, 0.8)',
                    }
                  : {}
              }
            >
              <div
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor: car.color,
                  boxShadow: `0 0 10px ${car.color}`,
                }}
              />
              <span className="w-4">{car.position}</span>
              <span className="flex-1">{car.driver}</span>
              <span className="opacity-70">{Math.round(car.speed)} km/h</span>
              <div className="w-20 h-1 bg-gray-800 rounded overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-red-500 to-cyan-400"
                  style={{ width: `${car.progress}%` }}
                  animate={{
                    boxShadow: [
                      '0 0 5px rgba(255, 0, 0, 0.5)',
                      '0 0 10px rgba(0, 255, 255, 0.8)',
                      '0 0 5px rgba(255, 0, 0, 0.5)',
                    ],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                  }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Race stats */}
      <div className="absolute bottom-8 right-8 font-mono text-xs text-gray-500">
        <div className="space-y-1">
          <div className="flex gap-2">
            <span className="text-red-500">TRACK:</span>
            <span>BAHRAIN INTERNATIONAL CIRCUIT</span>
          </div>
          <div className="flex gap-2">
            <span className="text-cyan-400">LAP:</span>
            <span>12 / 57</span>
          </div>
          <div className="flex gap-2">
            <span className="text-white">WEATHER:</span>
            <span>CLEAR 28°C</span>
          </div>
        </div>
      </div>

      {/* Corner effect overlays */}
      <div className="absolute top-0 left-0 w-32 h-32 border-t-2 border-l-2 border-cyan-500 opacity-30" />
      <div className="absolute top-0 right-0 w-32 h-32 border-t-2 border-r-2 border-red-500 opacity-30" />
      <div className="absolute bottom-0 left-0 w-32 h-32 border-b-2 border-l-2 border-red-500 opacity-30" />
      <div className="absolute bottom-0 right-0 w-32 h-32 border-b-2 border-r-2 border-cyan-500 opacity-30" />
    </div>
  );
};

export default NeonTrack;
