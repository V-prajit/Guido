'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface Position {
  x: number;
  y: number;
  angle: number;
}

interface SectorTime {
  sector: 1 | 2 | 3;
  time: number;
  status: 'personal-best' | 'fastest' | 'normal' | 'slower';
}

interface CarTelemetry {
  id: string;
  driverName: string;
  driverCode: string;
  teamColor: string;
  position: number;
  speed: number;
  throttle: number;
  brake: number;
  gear: number;
  rpm: number;
  drs: boolean;
  ers: number;
  currentSector: 1 | 2 | 3;
  sectorTimes: SectorTime[];
  lapTime: number;
  gap: string;
  tyreCompound: 'SOFT' | 'MEDIUM' | 'HARD' | 'INTER' | 'WET';
  tyreLaps: number;
  trackPosition: Position;
}

interface SectorZone {
  id: 1 | 2 | 3;
  startPercent: number;
  endPercent: number;
  label: string;
}

// ============================================================================
// BAHRAIN CIRCUIT SVG PATH & SECTOR DEFINITIONS
// ============================================================================

const BAHRAIN_TRACK_PATH = `
  M 120 300
  L 180 300
  Q 210 300 210 270
  L 210 150
  Q 210 120 240 120
  L 400 120
  Q 430 120 430 150
  L 430 180
  Q 430 210 400 210
  L 320 210
  Q 290 210 290 240
  L 290 320
  Q 290 350 320 350
  L 450 350
  Q 480 350 480 320
  L 480 280
  Q 480 250 510 250
  L 560 250
  Q 590 250 590 280
  L 590 380
  Q 590 410 560 410
  L 280 410
  Q 250 410 250 440
  L 250 480
  Q 250 510 220 510
  L 150 510
  Q 120 510 120 480
  L 120 300
  Z
`;

const SECTOR_ZONES: SectorZone[] = [
  { id: 1, startPercent: 0, endPercent: 33, label: 'S1' },
  { id: 2, startPercent: 33, endPercent: 66, label: 'S2' },
  { id: 3, startPercent: 66, endPercent: 100, label: 'S3' },
];

// ============================================================================
// MOCK TELEMETRY DATA GENERATOR
// ============================================================================

const generateMockTelemetry = (
  carId: string,
  isPlayer: boolean,
  lapProgress: number
): CarTelemetry => {
  const drivers = [
    { name: 'Max Verstappen', code: 'VER', color: '#1E40AF', team: 'Red Bull' },
    { name: 'Lewis Hamilton', code: 'HAM', color: '#6B7280', team: 'Mercedes' },
    { name: 'Charles Leclerc', code: 'LEC', color: '#DC2626', team: 'Ferrari' },
    { name: 'Lando Norris', code: 'NOR', color: '#F97316', team: 'McLaren' },
  ];

  const driverIndex = parseInt(carId) % drivers.length;
  const driver = drivers[driverIndex];

  // Calculate position on track based on lap progress
  const pathLength = 2000; // Approximate path length
  const currentDistance = (lapProgress % 100) / 100 * pathLength;

  // Simplified track position calculation (you'd use actual path following in production)
  const angle = (lapProgress * 3.6) % 360;
  const radius = 150;
  const centerX = 350;
  const centerY = 300;

  const trackPosition: Position = {
    x: centerX + Math.cos((angle * Math.PI) / 180) * radius,
    y: centerY + Math.sin((angle * Math.PI) / 180) * radius,
    angle: angle + 90,
  };

  // Current sector based on lap progress
  const currentSector =
    lapProgress < 33 ? 1 : lapProgress < 66 ? 2 : 3;

  // Mock sector times with variation
  const sectorTimes: SectorTime[] = [
    {
      sector: 1,
      time: 27.3 + Math.random() * 0.5,
      status: Math.random() > 0.7 ? 'fastest' : 'normal'
    },
    {
      sector: 2,
      time: 35.8 + Math.random() * 0.5,
      status: Math.random() > 0.7 ? 'personal-best' : 'normal'
    },
    {
      sector: 3,
      time: 29.1 + Math.random() * 0.5,
      status: Math.random() > 0.8 ? 'slower' : 'normal'
    },
  ];

  return {
    id: carId,
    driverName: driver.name,
    driverCode: driver.code,
    teamColor: isPlayer ? '#3B82F6' : driver.color,
    position: parseInt(carId),
    speed: 280 + Math.sin(lapProgress / 10) * 50 + Math.random() * 20,
    throttle: Math.max(0, Math.min(100, 80 + Math.random() * 20)),
    brake: Math.random() > 0.8 ? Math.random() * 100 : 0,
    gear: Math.floor(3 + Math.random() * 5),
    rpm: 8000 + Math.random() * 4000,
    drs: Math.random() > 0.7,
    ers: Math.random() * 100,
    currentSector: currentSector as 1 | 2 | 3,
    sectorTimes,
    lapTime: 92.1 + Math.random() * 2,
    gap: carId === '1' ? 'LEADER' : `+${(parseInt(carId) * 0.5 + Math.random() * 0.3).toFixed(3)}`,
    tyreCompound: ['SOFT', 'MEDIUM', 'HARD'][Math.floor(Math.random() * 3)] as any,
    tyreLaps: Math.floor(Math.random() * 15) + 1,
    trackPosition,
  };
};

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

const SectorIndicator: React.FC<{
  sector: SectorZone;
  isActive: boolean;
  activeCar: number
}> = ({ sector, isActive, activeCar }) => {
  const colors = {
    1: '#DC2626',
    2: '#DC2626',
    3: '#DC2626',
  };

  return (
    <motion.g
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: sector.id * 0.2 }}
    >
      <motion.circle
        cx={120 + sector.id * 160}
        cy={80}
        r={20}
        fill={isActive ? colors[sector.id] : 'rgba(220, 38, 38, 0.3)'}
        stroke={colors[sector.id]}
        strokeWidth={2}
        animate={isActive ? {
          scale: [1, 1.1, 1],
          opacity: [0.8, 1, 0.8]
        } : {}}
        transition={{
          duration: 1,
          repeat: isActive ? Infinity : 0
        }}
      />
      <text
        x={120 + sector.id * 160}
        y={85}
        textAnchor="middle"
        fill="white"
        fontSize="14"
        fontWeight="bold"
      >
        {sector.label}
      </text>
    </motion.g>
  );
};

const CarMarker: React.FC<{
  telemetry: CarTelemetry;
  isPlayer: boolean;
  onClick: () => void;
}> = ({ telemetry, isPlayer, onClick }) => {
  const { trackPosition, speed, driverCode } = telemetry;

  return (
    <motion.g
      initial={{ scale: 0 }}
      animate={{
        x: trackPosition.x,
        y: trackPosition.y,
        scale: 1,
        rotate: trackPosition.angle
      }}
      transition={{
        x: { type: 'spring', stiffness: 50, damping: 20 },
        y: { type: 'spring', stiffness: 50, damping: 20 },
        rotate: { duration: 0.1 }
      }}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Car body */}
      <motion.rect
        x={-8}
        y={-12}
        width={16}
        height={24}
        rx={3}
        fill={isPlayer ? '#3B82F6' : '#FFFFFF'}
        stroke={isPlayer ? '#1E40AF' : '#9CA3AF'}
        strokeWidth={2}
        whileHover={{ scale: 1.1 }}
      />

      {/* Front wing */}
      <rect
        x={-10}
        y={-14}
        width={20}
        height={3}
        fill={isPlayer ? '#1E40AF' : '#6B7280'}
      />

      {/* Driver code label */}
      {!isPlayer && (
        <text
          x={0}
          y={-20}
          textAnchor="middle"
          fill="white"
          fontSize="10"
          fontWeight="bold"
          style={{ pointerEvents: 'none' }}
        >
          {driverCode}
        </text>
      )}

      {/* Speed indicator for player */}
      {isPlayer && (
        <motion.g
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <rect
            x={-25}
            y={-8}
            width={50}
            height={16}
            rx={4}
            fill="rgba(0, 0, 0, 0.8)"
            stroke="#3B82F6"
            strokeWidth={1}
          />
          <text
            x={0}
            y={2}
            textAnchor="middle"
            fill="#3B82F6"
            fontSize="11"
            fontWeight="bold"
          >
            {Math.round(speed)} KPH
          </text>
        </motion.g>
      )}

      {/* Position indicator */}
      <motion.circle
        cx={0}
        cy={18}
        r={8}
        fill={isPlayer ? '#3B82F6' : '#1F2937'}
        stroke={isPlayer ? '#1E40AF' : '#4B5563'}
        strokeWidth={2}
        animate={isPlayer ? {
          boxShadow: ['0 0 10px #3B82F6', '0 0 20px #3B82F6', '0 0 10px #3B82F6']
        } : {}}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <text
        x={0}
        y={22}
        textAnchor="middle"
        fill="white"
        fontSize="10"
        fontWeight="bold"
      >
        P{telemetry.position}
      </text>
    </motion.g>
  );
};

const TelemetryHUD: React.FC<{ telemetry: CarTelemetry }> = ({ telemetry }) => {
  const tyreColors = {
    SOFT: '#DC2626',
    MEDIUM: '#F59E0B',
    HARD: '#F3F4F6',
    INTER: '#10B981',
    WET: '#3B82F6',
  };

  const getSectorColor = (status: string) => {
    switch (status) {
      case 'fastest': return '#A855F7';
      case 'personal-best': return '#10B981';
      case 'slower': return '#F59E0B';
      default: return '#FFFFFF';
    }
  };

  return (
    <motion.div
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 100 }}
      className="absolute top-4 left-4 bg-black/90 backdrop-blur-sm border border-blue-500 rounded-lg p-4 text-white font-mono min-w-[320px]"
    >
      {/* Driver Header */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div
            className="w-1 h-12 rounded"
            style={{ backgroundColor: telemetry.teamColor }}
          />
          <div>
            <div className="text-xs text-gray-400">P{telemetry.position}</div>
            <div className="text-lg font-bold">{telemetry.driverCode}</div>
            <div className="text-xs text-gray-400">{telemetry.driverName}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-400">
            {Math.round(telemetry.speed)}
          </div>
          <div className="text-xs text-gray-400">KPH</div>
        </div>
      </div>

      {/* Timing Information */}
      <div className="mb-3 space-y-1">
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-400">Gap to Leader</span>
          <span className="font-bold text-sm">{telemetry.gap}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-400">Lap Time</span>
          <span className="font-bold text-sm">
            {Math.floor(telemetry.lapTime / 60)}:
            {(telemetry.lapTime % 60).toFixed(3).padStart(6, '0')}
          </span>
        </div>
      </div>

      {/* Sector Times */}
      <div className="mb-3 pb-3 border-b border-gray-700">
        <div className="text-xs text-gray-400 mb-2">Sector Times</div>
        <div className="grid grid-cols-3 gap-2">
          {telemetry.sectorTimes.map((sector) => (
            <div
              key={sector.sector}
              className="text-center p-1 rounded"
              style={{
                backgroundColor: telemetry.currentSector === sector.sector
                  ? 'rgba(59, 130, 246, 0.2)'
                  : 'rgba(0, 0, 0, 0.3)',
                border: telemetry.currentSector === sector.sector
                  ? '1px solid #3B82F6'
                  : '1px solid transparent'
              }}
            >
              <div className="text-xs text-gray-400">S{sector.sector}</div>
              <div
                className="text-sm font-bold"
                style={{ color: getSectorColor(sector.status) }}
              >
                {sector.time.toFixed(3)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Vehicle Systems */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div>
          <div className="text-xs text-gray-400">Gear</div>
          <div className="text-xl font-bold text-green-400">{telemetry.gear}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">RPM</div>
          <div className="text-sm font-bold">{Math.round(telemetry.rpm)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Throttle</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-700 rounded overflow-hidden">
              <motion.div
                className="h-full bg-green-500"
                initial={{ width: 0 }}
                animate={{ width: `${telemetry.throttle}%` }}
                transition={{ duration: 0.1 }}
              />
            </div>
            <span className="text-xs w-10">{Math.round(telemetry.throttle)}%</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Brake</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-700 rounded overflow-hidden">
              <motion.div
                className="h-full bg-red-500"
                initial={{ width: 0 }}
                animate={{ width: `${telemetry.brake}%` }}
                transition={{ duration: 0.1 }}
              />
            </div>
            <span className="text-xs w-10">{Math.round(telemetry.brake)}%</span>
          </div>
        </div>
      </div>

      {/* ERS & DRS */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div>
          <div className="text-xs text-gray-400">ERS</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-700 rounded overflow-hidden">
              <motion.div
                className="h-full bg-purple-500"
                initial={{ width: 0 }}
                animate={{ width: `${telemetry.ers}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <span className="text-xs w-10">{Math.round(telemetry.ers)}%</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400">DRS</div>
          <div
            className={`text-sm font-bold px-2 py-1 rounded text-center ${
              telemetry.drs
                ? 'bg-green-500/20 text-green-400 border border-green-500'
                : 'bg-gray-700 text-gray-400'
            }`}
          >
            {telemetry.drs ? 'ACTIVE' : 'CLOSED'}
          </div>
        </div>
      </div>

      {/* Tyre Information */}
      <div
        className="p-2 rounded border"
        style={{
          borderColor: tyreColors[telemetry.tyreCompound],
          backgroundColor: `${tyreColors[telemetry.tyreCompound]}20`
        }}
      >
        <div className="flex justify-between items-center">
          <div>
            <div className="text-xs text-gray-400">Tyre Compound</div>
            <div
              className="text-sm font-bold"
              style={{ color: tyreColors[telemetry.tyreCompound] }}
            >
              {telemetry.tyreCompound}
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">Tyre Age</div>
            <div className="text-sm font-bold">{telemetry.tyreLaps} Laps</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const LeaderboardHUD: React.FC<{ cars: CarTelemetry[] }> = ({ cars }) => {
  const sortedCars = [...cars].sort((a, b) => a.position - b.position);

  return (
    <motion.div
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 100 }}
      className="absolute top-4 right-4 bg-black/90 backdrop-blur-sm border border-gray-700 rounded-lg overflow-hidden min-w-[280px]"
    >
      <div className="bg-gradient-to-r from-red-600 to-red-800 px-4 py-2">
        <div className="text-white font-bold text-sm">LIVE STANDINGS</div>
      </div>

      <div className="divide-y divide-gray-800">
        {sortedCars.map((car, index) => (
          <motion.div
            key={car.id}
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`px-4 py-2 flex items-center gap-3 ${
              car.teamColor === '#3B82F6' ? 'bg-blue-500/10' : ''
            }`}
          >
            <div className="text-white font-bold text-sm w-6">
              P{car.position}
            </div>
            <div
              className="w-1 h-8 rounded"
              style={{ backgroundColor: car.teamColor }}
            />
            <div className="flex-1">
              <div className="text-white font-bold text-sm">{car.driverCode}</div>
              <div className="text-gray-400 text-xs">{car.driverName}</div>
            </div>
            <div className="text-right">
              <div className="text-white text-xs font-mono">{car.gap}</div>
              <div className="text-gray-400 text-xs">
                S{car.currentSector}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const DataTrack: React.FC = () => {
  const [lapProgress, setLapProgress] = useState(0);
  const [carTelemetries, setCarTelemetries] = useState<CarTelemetry[]>([]);
  const [selectedCarId, setSelectedCarId] = useState('1');
  const [isPaused, setIsPaused] = useState(false);

  // Initialize cars
  useEffect(() => {
    const initialCars = ['1', '2', '3', '4'].map((id) =>
      generateMockTelemetry(id, id === '1', 0)
    );
    setCarTelemetries(initialCars);
  }, []);

  // Animation loop
  useEffect(() => {
    if (isPaused) return;

    const interval = setInterval(() => {
      setLapProgress((prev) => (prev + 0.5) % 100);

      setCarTelemetries((prevCars) =>
        prevCars.map((car, index) => {
          const carProgress = (lapProgress + index * 8) % 100;
          return generateMockTelemetry(car.id, car.id === '1', carProgress);
        })
      );
    }, 50);

    return () => clearInterval(interval);
  }, [lapProgress, isPaused]);

  const selectedCar = carTelemetries.find((car) => car.id === selectedCarId);
  const currentSector = lapProgress < 33 ? 1 : lapProgress < 66 ? 2 : 3;

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 overflow-hidden">
      {/* Track SVG */}
      <div className="absolute inset-0 flex items-center justify-center">
        <svg
          width="700"
          height="600"
          viewBox="0 0 700 600"
          className="drop-shadow-2xl"
        >
          {/* Track background glow */}
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <linearGradient id="trackGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#DC2626" />
              <stop offset="33%" stopColor="#EF4444" />
              <stop offset="66%" stopColor="#DC2626" />
              <stop offset="100%" stopColor="#B91C1C" />
            </linearGradient>
          </defs>

          {/* Track outline */}
          <path
            d={BAHRAIN_TRACK_PATH}
            fill="none"
            stroke="url(#trackGradient)"
            strokeWidth="24"
            strokeLinecap="round"
            strokeLinejoin="round"
            filter="url(#glow)"
            opacity={0.9}
          />

          {/* Track center line */}
          <path
            d={BAHRAIN_TRACK_PATH}
            fill="none"
            stroke="#1F2937"
            strokeWidth="12"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Sector markers on track */}
          {SECTOR_ZONES.map((sector) => (
            <SectorIndicator
              key={sector.id}
              sector={sector}
              isActive={currentSector === sector.id}
              activeCar={currentSector}
            />
          ))}

          {/* Start/Finish line */}
          <motion.line
            x1={120}
            y1={295}
            x2={120}
            y2={305}
            stroke="white"
            strokeWidth={4}
            strokeDasharray="4 4"
            animate={{ strokeDashoffset: [0, 8] }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          <text
            x={90}
            y={295}
            fill="white"
            fontSize="12"
            fontWeight="bold"
          >
            START/FINISH
          </text>

          {/* Car markers */}
          <AnimatePresence>
            {carTelemetries.map((car) => (
              <CarMarker
                key={car.id}
                telemetry={car}
                isPlayer={car.id === '1'}
                onClick={() => setSelectedCarId(car.id)}
              />
            ))}
          </AnimatePresence>
        </svg>
      </div>

      {/* HUD Overlays */}
      {selectedCar && <TelemetryHUD telemetry={selectedCar} />}
      <LeaderboardHUD cars={carTelemetries} />

      {/* Control Panel */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/90 backdrop-blur-sm border border-gray-700 rounded-lg px-6 py-3 flex items-center gap-4">
        <button
          onClick={() => setIsPaused(!isPaused)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-bold transition-colors"
        >
          {isPaused ? 'RESUME' : 'PAUSE'}
        </button>

        <div className="border-l border-gray-700 pl-4">
          <div className="text-gray-400 text-xs">LAP PROGRESS</div>
          <div className="text-white font-bold">{lapProgress.toFixed(1)}%</div>
        </div>

        <div className="border-l border-gray-700 pl-4">
          <div className="text-gray-400 text-xs">SELECTED CAR</div>
          <div className="text-white font-bold">
            {selectedCar?.driverCode || 'N/A'}
          </div>
        </div>

        <div className="border-l border-gray-700 pl-4 flex gap-2">
          {carTelemetries.map((car) => (
            <button
              key={car.id}
              onClick={() => setSelectedCarId(car.id)}
              className={`px-3 py-1 rounded font-bold text-xs transition-colors ${
                selectedCarId === car.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
              }`}
            >
              {car.driverCode}
            </button>
          ))}
        </div>
      </div>

      {/* Race Info Banner */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-black/90 backdrop-blur-sm border border-red-600 rounded-lg px-6 py-2">
        <div className="text-center">
          <div className="text-red-500 font-bold text-xs">BAHRAIN INTERNATIONAL CIRCUIT</div>
          <div className="text-white font-bold">LAP 1 / 57</div>
        </div>
      </div>
    </div>
  );
};

export default DataTrack;
