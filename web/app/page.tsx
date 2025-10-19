'use client';

import { Box1, Box2, Box3, Box5, Box6, Box7, Box8 } from './components/Box';
import { Logo } from './components/Logo';
import { GameProvider, useGame } from '@/contexts/GameContext';
import DecisionModal from '@/tempComponents/GameUI/DecisionModal';

function GameControls() {
  const { isConnected, gameStarted, raceComplete, finalPosition, startRace, restartRace } = useGame();

  return (
    <div className="absolute top-6 right-6 z-50 flex items-center gap-3">
      <div className={`px-3 py-1 rounded-full text-xs font-bold ${
        isConnected ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      }`}>
        {isConnected ? '● CONNECTED' : '● DISCONNECTED'}
      </div>

      {!gameStarted && !raceComplete && (
        <button
          onClick={() => startRace(57)}
          disabled={!isConnected}
          className="px-4 py-2 bg-black text-white font-bold rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm"
        >
          START RACE
        </button>
      )}

      {raceComplete && (
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 bg-blue-500 text-white font-bold rounded-lg text-sm">
            FINISHED P{finalPosition}
          </div>
          <button
            onClick={restartRace}
            className="px-4 py-2 bg-black text-white font-bold rounded-lg hover:bg-gray-800 transition-colors text-sm"
          >
            RESTART
          </button>
        </div>
      )}
    </div>
  );
}

function GameContent() {
  const { decisionPoint, player, currentLap, selectStrategy } = useGame();

  return (
    <>
      <GameControls />
      <div
        className="grid h-full w-full gap-6"
        style={{
          gridTemplateColumns: 'repeat(12, minmax(0, 1fr))',
          gridTemplateRows: 'repeat(12, minmax(0, 1fr))',
        }}
      >
        <Logo />
        <Box1 />
        <Box2 />
        <Box3 />
        <Box5 />
        <Box6 />
        <Box7 />
        <Box8 />
      </div>

      {/* Rain Decision Modal */}
      {decisionPoint && player && (
        <DecisionModal
          isOpen={!!decisionPoint}
          eventType={decisionPoint.event_type}
          lap={currentLap}
          position={player.position}
          batterySOC={player.battery_soc}
          tireLife={player.tire_life}
          fuelRemaining={player.fuel_remaining}
          recommended={decisionPoint.recommendations.recommended || []}
          avoid={decisionPoint.recommendations.avoid || null}
          onSelect={selectStrategy}
          latencyMs={decisionPoint.recommendations.latency_ms}
          usedFallback={decisionPoint.recommendations.used_fallback}
        />
      )}
    </>
  );
}

export default function Home() {
  return (
    <GameProvider backendUrl={process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}>
      <main className="relative flex h-screen w-screen overflow-hidden p-4">
        <GameContent />
      </main>
    </GameProvider>
  );
}
