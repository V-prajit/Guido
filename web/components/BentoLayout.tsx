'use client';

import { useEffect, useMemo, useState } from 'react';
import Box1_RaceTrack from './BentoBoxes/Box1_RaceTrack';
import DecisionModal from './GameUI/DecisionModal';
import { useGameSession } from '@/hooks/useGameSession';

const FALLBACK_STRATEGIES = [
  {
    id: -1,
    name: 'Aggressive Attack',
    probability: '75%',
    explanation: 'Deploy power early to build a buffer before tire drop-off.',
  },
  {
    id: -2,
    name: 'Conservative Play',
    probability: '58%',
    explanation: 'Protect battery and wait for mistakes in traffic.',
  },
  {
    id: -3,
    name: 'Balanced Drive',
    probability: '67%',
    explanation: 'Blend energy deployment with tire care for steady gains.',
  },
];

const formatPercentage = (fraction?: number) =>
  typeof fraction === 'number' && Number.isFinite(fraction)
    ? `${Math.round(fraction * 100)}%`
    : '--';

export default function BentoLayout() {
  const [selectedStrategy, setSelectedStrategy] = useState<number>(0);

  const {
    isConnected,
    gameStarted,
    raceComplete,
    startRace,
    restartRace,
    selectStrategy,
    currentLap,
    totalLaps,
    progressFraction,
    carsForTrack,
    playerState,
    opponents,
    isRaining,
    safetyCarActive,
    decisionPoint,
  } = useGameSession();

  const activeDecision = decisionPoint ?? null;

  const strategies = useMemo(() => {
    if (activeDecision?.recommended?.length) {
      return activeDecision.recommended.map((strategy) => ({
        id: strategy.strategy_id,
        name: strategy.strategy_name,
        probability: formatPercentage(strategy.win_rate),
        explanation: strategy.rationale,
        confidence: strategy.confidence,
      }));
    }
    return FALLBACK_STRATEGIES;
  }, [activeDecision]);

  useEffect(() => {
    setSelectedStrategy(0);
  }, [activeDecision?.lap, strategies.length]);

  const cars = carsForTrack.length ? carsForTrack : undefined;

  const topOpponents = useMemo(() => {
    return [...opponents]
      .sort((a, b) => a.position - b.position)
      .slice(0, 3)
      .map((opp) => ({
        name: opp.name,
        shortName: opp.name.split(' ')[0] ?? opp.name,
        position: opp.position,
        speed: Math.round(opp.speed ?? 0),
        gapToLeader: opp.gap_to_leader,
      }));
  }, [opponents]);

  const handleStrategyClick = (index: number) => {
    setSelectedStrategy(index);
    const selected = activeDecision?.recommended?.[index];

    if (decisionPoint && selected) {
      selectStrategy(selected.strategy_id);
    }
  };

  return (
    <div className="w-full min-h-screen bg-white p-6">
      <div className="max-w-[1800px] mx-auto space-y-4">
        {/* Status Banner */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-black rounded-lg px-4 py-3">
          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 text-xs font-bold rounded-full ${
                isConnected ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
              }`}
            >
              {isConnected ? '● CONNECTED' : '● DISCONNECTED'}
            </span>
            <span className="text-sm text-black/70">
              {gameStarted
                ? raceComplete
                  ? 'Race complete — review results or run another'
                  : `Streaming telemetry • Lap ${currentLap} / ${totalLaps}`
                : 'Ready to stream live race telemetry'}
            </span>
          </div>

          <div>
            {!gameStarted && (
              <button
                onClick={startRace}
                disabled={!isConnected}
                className="px-4 py-2 bg-black text-white text-sm font-bold rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:text-white/70 disabled:cursor-not-allowed transition-colors"
              >
                START RACE
              </button>
            )}
            {raceComplete && (
              <button
                onClick={restartRace}
                className="px-4 py-2 bg-black text-white text-sm font-bold rounded-lg hover:bg-gray-800 transition-colors"
              >
                RACE AGAIN
              </button>
            )}
          </div>
        </div>

        {/* Top Section */}
        <div className="grid grid-cols-12 gap-4">
          {/* Race Track */}
          <div className="col-span-6">
            <Box1_RaceTrack cars={cars} />
          </div>

          {/* Simulation Progress */}
          <div className="col-span-3 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">SIMULATION PROGRESS</h3>
            <div className="space-y-3">
              <p className="text-2xl font-bold text-black">
                {gameStarted ? `Lap ${currentLap}/${totalLaps}` : 'Standing by'}
              </p>
              <div className="w-full h-2 bg-black/20 rounded-full overflow-hidden">
                <div
                  className="h-full bg-black transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, progressFraction * 100))}%` }}
                />
              </div>
              <p className="text-xs text-black/60">
                {isRaining ? 'Rain affecting grip' : 'Dry conditions'}
                {safetyCarActive ? ' • Safety car deployed' : ''}
              </p>
            </div>
          </div>

          {/* Opponent Strategy with SPEEDS */}
          <div className="col-span-3 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">OPPONENT LEADERBOARD</h3>
            <div className="space-y-3">
              {topOpponents.length ? (
                topOpponents.map((opp) => (
                  <div
                    key={opp.name}
                    className="flex items-center justify-between border-b border-black/20 pb-2 last:border-b-0 last:pb-0"
                  >
                    <div>
                      <span className="text-sm text-black font-semibold">P{opp.position}: {opp.shortName}</span>
                      <div className="text-xs text-black/50">{opp.speed} km/h</div>
                    </div>
                    <span className="text-xs text-black/60">
                      {opp.gapToLeader > 0 ? `+${opp.gapToLeader.toFixed(2)}s` : 'Leader'}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-black/50">Start the race to stream opponent telemetry.</p>
              )}
            </div>
          </div>
        </div>

        {/* Player Telemetry with PROMINENT SPEED */}
        <div className="bg-white border border-black rounded-lg p-6">
          <h3 className="text-sm font-bold text-black mb-4 tracking-wide">YOUR TELEMETRY</h3>
          <div className="grid grid-cols-2 gap-6">
            {/* Left: Speed (PROMINENT) */}
            <div className="border-r border-black/20 pr-6">
              <div className="text-xs text-black/60 mb-2 tracking-wide">CURRENT SPEED</div>
              <div className="text-7xl font-bold text-black mb-2">
                {playerState?.speed ? Math.round(playerState.speed) : '---'}
              </div>
              <div className="text-xs text-black/50">km/h</div>
              {playerState?.lap_time && (
                <div className="mt-4 text-xs text-black/60">
                  <div>Last Lap: {playerState.lap_time.toFixed(3)}s</div>
                </div>
              )}
            </div>

            {/* Right: Telemetry Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-black/60">Lap</span>
                <p className="text-2xl font-bold text-black">{currentLap}/{totalLaps}</p>
              </div>
              <div>
                <span className="text-xs text-black/60">Position</span>
                <p className="text-2xl font-bold text-black">P{playerState?.position ?? '-'}</p>
              </div>
              <div>
                <span className="text-xs text-black/60">Battery</span>
                <p className="text-lg font-bold text-black">{playerState?.battery_soc?.toFixed(1) ?? '-'}%</p>
              </div>
              <div>
                <span className="text-xs text-black/60">Tires</span>
                <p className="text-lg font-bold text-black">{playerState?.tire_life?.toFixed(1) ?? '-'}%</p>
              </div>
              <div>
                <span className="text-xs text-black/60">Fuel</span>
                <p className="text-lg font-bold text-black">{playerState?.fuel_remaining?.toFixed(1) ?? '-'}kg</p>
              </div>
              <div>
                <span className="text-xs text-black/60">Gap to Leader</span>
                <p className="text-lg font-bold text-black">
                  {playerState?.gap_to_leader ? (playerState.gap_to_leader > 0 ? '+' : '') + playerState.gap_to_leader.toFixed(2) + 's' : '-'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Mid Section */}
        <div className="grid grid-cols-12 gap-4">
          {/* Recommendations - Only show when decision point is active */}
          {decisionPoint && (
            <div className="col-span-9 bg-white border border-black rounded-lg p-6">
              <h3 className="text-lg font-bold text-black mb-6 tracking-wide">MULTI-AGENT STRATEGY RECS</h3>
              <div className="grid grid-cols-3 gap-4">
                {strategies.map((strategy, index) => (
                  <div
                    key={strategy.id ?? index}
                    onClick={() => handleStrategyClick(index)}
                    className={`border rounded-lg p-4 cursor-pointer transition-all hover:border-black hover:bg-black/5 ${
                      selectedStrategy === index ? 'border-black bg-black/5' : 'border-black/40'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-bold text-black">{strategy.name}</h4>
                      {typeof strategy.confidence === 'number' && (
                        <span className="text-[10px] font-bold text-black/50">
                          {formatPercentage(strategy.confidence)}
                        </span>
                      )}
                    </div>
                    <p className="text-4xl font-bold text-black mb-4">{strategy.probability}</p>
                    <p className="text-xs text-black/70 leading-relaxed">
                      {strategy.explanation || 'Awaiting live recommendation data.'}
                    </p>
                    <p className="mt-3 text-[11px] text-blue-600 font-semibold uppercase tracking-wide">
                      Click to apply immediately
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Agent Performance */}
          <div className={`bg-white border border-black rounded-lg p-4 ${decisionPoint ? 'col-span-3' : 'col-span-12'}`}>
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">RACE POSITIONS</h3>
            <div className="space-y-3">
              {playerState ? (
                <>
                  <div className="border-b border-black/20 pb-2">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-bold text-black">You</span>
                      <span className="text-xs text-black/60">P{playerState.position}</span>
                    </div>
                    <p className="text-xs text-black/60">{Math.round(playerState.speed ?? 0)} km/h</p>
                  </div>
                  {topOpponents.map((opp) => (
                    <div key={opp.name} className="border-b border-black/20 pb-2 last:border-b-0">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-black">{opp.shortName}</span>
                        <span className="text-xs text-black/60">P{opp.position}</span>
                      </div>
                      <p className="text-xs text-black/60">{opp.speed} km/h</p>
                    </div>
                  ))}
                </>
              ) : (
                <p className="text-xs text-black/50">Start the race to populate leaderboard.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Decision Modal */}
      {decisionPoint && (
        <DecisionModal
          isOpen={true}
          eventType={decisionPoint.event_type}
          lap={decisionPoint.lap}
          position={decisionPoint.position}
          batterySOC={decisionPoint.battery_soc}
          tireLife={decisionPoint.tire_life}
          fuelRemaining={decisionPoint.fuel_remaining}
          recommended={decisionPoint.recommended}
          avoid={decisionPoint.avoid}
          onSelect={selectStrategy}
          latencyMs={decisionPoint.latency_ms}
          usedFallback={decisionPoint.used_fallback}
        />
      )}
    </div>
  );
}
