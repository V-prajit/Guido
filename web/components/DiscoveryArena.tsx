'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import mockPayload from '../mock/discoveryArena.json';
import type {
  DiscoveryArenaMock,
  DiscoveryTelemetryFrame,
  DiscoveryStrategyMetric,
} from '../types';

const discoveryMock = mockPayload as DiscoveryArenaMock;
const telemetryTimeline = discoveryMock.telemetry;

interface MetricProps {
  label: string;
  value: string;
  hint?: string;
  accent?: string;
}

const RaceMetric = ({ label, value, hint, accent }: MetricProps) => (
  <div className="rounded-xl border border-white/5 bg-gray-900/80 px-4 py-3 shadow-inner">
    <div className="text-[11px] uppercase tracking-[0.3em] text-gray-500">{label}</div>
    <div className={`mt-1 text-2xl font-semibold ${accent ?? 'text-f1-white'}`}>{value}</div>
    {hint && <div className="mt-1 text-[11px] text-gray-500">{hint}</div>}
  </div>
);

const StrategyCard = ({ strategy }: { strategy: DiscoveryStrategyMetric }) => (
  <div className="rounded-xl border border-gray-800/70 bg-gray-900/80 px-4 py-3 transition hover:border-f1-blue/60 hover:shadow-lg hover:shadow-f1-blue/10">
    <div className="flex items-start justify-between gap-3">
      <h4 className="text-base font-semibold text-white">{strategy.codename}</h4>
      <span className="rounded-full border border-white/10 px-2 py-[2px] text-xs font-mono text-gray-300">
        {(strategy.win_share * 100).toFixed(0)}% win
      </span>
    </div>
    <p className="mt-2 text-xs text-gray-400">{strategy.focus}</p>
    <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono text-gray-300">
      <div className="rounded-lg bg-gray-800/70 px-2 py-2">
        <span className="block text-[10px] uppercase tracking-widest text-gray-500">Delta Lap</span>
        <span className="text-white">{strategy.fastest_lap_delta.toFixed(2)}s</span>
      </div>
      <div className="rounded-lg bg-gray-800/70 px-2 py-2">
        <span className="block text-[10px] uppercase tracking-widest text-gray-500">Battery</span>
        <span className="text-white">+{(strategy.battery_margin * 100).toFixed(0)}%</span>
      </div>
    </div>
  </div>
);

const TelemetryStep = ({
  frame,
  isActive,
  isComplete,
}: {
  frame: DiscoveryTelemetryFrame;
  isActive: boolean;
  isComplete: boolean;
}) => {
  const base = 'flex items-start gap-3 text-sm transition';
  const palette = isActive
    ? 'text-f1-blue'
    : isComplete
    ? 'text-gray-200'
    : 'text-gray-500';

  return (
    <div className={`${base} ${palette}`}>
      <div
        className={`mt-1 h-2 w-2 rounded-full ${
          isComplete ? 'bg-f1-red' : isActive ? 'bg-f1-blue' : 'bg-gray-600'
        }`}
      />
      <div>
        <div className="text-[11px] font-semibold uppercase tracking-[0.25em] text-gray-500">
          {frame.phase.replace('-', ' ')}
        </div>
        <p className="text-sm leading-relaxed text-gray-300">{frame.message}</p>
      </div>
    </div>
  );
};

export default function DiscoveryArena() {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scenarios, setScenarios] = useState(0);
  const [statusMessage, setStatusMessage] = useState(
    'Systems idle — waiting for race control to drop the lights.',
  );
  const [activeStep, setActiveStep] = useState(-1);
  const [result, setResult] = useState<DiscoveryArenaMock | null>(null);
  const scheduleRef = useRef<number[]>([]);

  const clearSchedule = () => {
    scheduleRef.current.forEach(clearTimeout);
    scheduleRef.current = [];
  };

  useEffect(() => {
    return () => clearSchedule();
  }, []);

  const engageSimulation = () => {
    if (isRunning) return;
    clearSchedule();

    setIsRunning(true);
    setResult(null);
    setProgress(0);
    setScenarios(0);
    setStatusMessage('Ignition sequence armed. Power units standing by.');
    setActiveStep(-1);

    let cumulativeDelay = 0;
    telemetryTimeline.forEach((frame, index) => {
      cumulativeDelay += frame.delay_ms;
      const timeoutId = window.setTimeout(() => {
        setProgress(frame.progress);
        setScenarios(frame.scenarios);
        setStatusMessage(frame.message);
        setActiveStep(index);

        if (index === telemetryTimeline.length - 1) {
          const finaliseId = window.setTimeout(() => {
            setResult(discoveryMock);
            setIsRunning(false);
          }, 420);
          scheduleRef.current.push(finaliseId);
        }
      }, cumulativeDelay);

      scheduleRef.current.push(timeoutId);
    });
  };

  const metrics = useMemo(() => {
    if (!result) {
      return null;
    }

    return [
      {
        label: 'Scenarios Completed',
        value: result.scenarios_completed.toLocaleString(),
        hint: 'Adversarial energy maps evaluated',
        accent: 'text-green-400',
      },
      {
        label: 'Elapsed Time',
        value: `${result.elapsed_sec.toFixed(1)}s`,
        hint: `${result.scenarios_per_sec.toFixed(0)} scenarios/sec throughput`,
        accent: 'text-f1-blue',
      },
      {
        label: 'Energy Delta',
        value: `+${result.energy_reclaimed_mj.toFixed(1)} MJ`,
        hint: 'Recovered via strategic regen',
        accent: 'text-amber-300',
      },
      {
        label: 'Tyre Surface Peak',
        value: `${result.peak_tyre_surface_temp.toFixed(0)}°C`,
        hint: 'Thermal ceiling during sweep',
        accent: 'text-red-300',
      },
    ];
  }, [result]);

  return (
    <section className="relative overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-br from-black via-gray-900 to-gray-950 p-8 shadow-2xl">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,24,1,0.15),transparent)] opacity-80" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(135deg,rgba(255,255,255,0.04)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.04)_50%,rgba(255,255,255,0.04)_75%,transparent_75%,transparent)] bg-[length:18px_18px] opacity-[0.08]" />

      <div className="relative z-10 flex flex-col gap-8">
        <header className="max-w-3xl space-y-3">
          <h2 className="text-4xl font-bold text-white">Discovery Arena</h2>
          <p className="text-sm leading-relaxed text-gray-300">
            Fire up 1,000 virtual grands prix with eight rival energy strategies. We stress-test MGU-K
            deploy maps, regen envelopes, and aero trims to surface F1 2026 winning playbooks.
          </p>
        </header>

        <div className="grid gap-8 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <div className="space-y-6">
            <button
              onClick={engageSimulation}
              disabled={isRunning}
              className="group relative flex w-full items-center justify-center gap-3 overflow-hidden rounded-xl border border-f1-red/60 bg-f1-red px-6 py-4 text-lg font-bold uppercase tracking-[0.35em] text-black transition hover:from-f1-red hover:to-amber-400 disabled:cursor-not-allowed disabled:border-gray-700 disabled:bg-gray-700 disabled:text-gray-400"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-white/20 via-transparent to-white/20 opacity-0 transition group-hover:opacity-40" />
              {isRunning ? 'Simulation Armed…' : 'Launch 1000 Scenarios'}
            </button>

            <div className="rounded-xl border border-white/5 bg-gray-950/80 p-5">
              <div className="mb-4 flex items-center justify-between text-xs font-mono uppercase tracking-[0.3em] text-gray-500">
                <span>Live Telemetry Feed</span>
                <span>{progress.toFixed(0)}% complete</span>
              </div>
              <div className="relative h-3 overflow-hidden rounded-full bg-gray-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-f1-red via-orange-400 to-yellow-300 transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                />
                <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,255,255,0.12)_0%,rgba(255,255,255,0)_50%)] bg-[length:20px_100%]" />
              </div>

              <div className="mt-4 flex items-center justify-between text-xs text-gray-400">
                <span>{statusMessage}</span>
                <span>{scenarios.toLocaleString()} sims</span>
              </div>
            </div>

            <div className="space-y-4 rounded-xl border border-white/5 bg-gray-950/70 p-5">
              {telemetryTimeline.map((frame, index) => (
                <TelemetryStep
                  key={frame.phase}
                  frame={frame}
                  isActive={index === activeStep && isRunning}
                  isComplete={index < activeStep || (!!result && index <= activeStep)}
                />
              ))}
            </div>
          </div>

          <aside className="space-y-6">
            {metrics ? (
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                {metrics.map((metric) => (
                  <RaceMetric key={metric.label} {...metric} />
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-white/5 bg-gray-950/80 px-4 py-6 text-sm text-gray-400">
                Run the arena to surface throughput, energy recovery, and thermal metrics.
              </div>
            )}

            <div className="space-y-3">
              <h3 className="text-sm font-semibold uppercase tracking-[0.3em] text-gray-400">
                Strategy Standings
              </h3>
              <div className="grid gap-3">
                {discoveryMock.strategies.map((strategy) => (
                  <StrategyCard key={strategy.codename} strategy={strategy} />
                ))}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}
