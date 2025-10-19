'use client';

import { useMemo, useState } from 'react';
import mockResponse from '../mock/boxWall.json';
import type { BoxWallResponse, Recommendation } from '../types';

const advisorMock = mockResponse as BoxWallResponse;

interface ControlSliderProps {
  label: string;
  min: number;
  max: number;
  value: number;
  unit?: string;
  accent?: string;
  onChange: (value: number) => void;
}

const ControlSlider = ({
  label,
  min,
  max,
  value,
  unit,
  accent,
  onChange,
}: ControlSliderProps) => (
  <div className="space-y-2 rounded-xl border border-white/5 bg-gray-900/70 p-4 shadow-inner">
    <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[0.28em] text-gray-400">
      <span>{label}</span>
      <span className={`text-sm font-semibold ${accent ?? 'text-white'}`}>
        {value}
        {unit}
      </span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      value={value}
      onChange={(event) => onChange(parseInt(event.target.value, 10))}
      className="w-full accent-f1-red"
    />
    <div className="flex justify-between text-[10px] uppercase tracking-[0.2em] text-gray-500">
      <span>{min}</span>
      <span>{max}</span>
    </div>
  </div>
);

const RecommendationCard = ({ recommendation }: { recommendation: Recommendation }) => (
  <div className="rounded-2xl border border-white/5 bg-gray-950/70 p-5 transition hover:border-f1-blue/50 hover:shadow-lg hover:shadow-f1-blue/10">
    <div className="flex items-start justify-between gap-4">
      <div>
        <h4 className="text-lg font-semibold text-white">{recommendation.rule}</h4>
        <p className="mt-1 text-xs text-gray-400">{recommendation.rationale}</p>
      </div>
      <div className="rounded-full border border-yellow-500/40 bg-yellow-500/10 px-3 py-1 text-xs font-mono text-yellow-300">
        {(recommendation.confidence * 100).toFixed(0)}% confident
      </div>
    </div>

    <div className="mt-4 grid grid-cols-3 gap-3 text-center text-xs font-mono text-gray-300">
      <div className="rounded-xl border border-white/5 bg-gray-900/80 px-3 py-3">
        <span className="block text-[10px] uppercase tracking-[0.3em] text-gray-500">Straights</span>
        <span className="text-lg text-white">{recommendation.action.deploy_straight}%</span>
      </div>
      <div className="rounded-xl border border-white/5 bg-gray-900/80 px-3 py-3">
        <span className="block text-[10px] uppercase tracking-[0.3em] text-gray-500">Corners</span>
        <span className="text-lg text-white">{recommendation.action.deploy_corner}%</span>
      </div>
      <div className="rounded-xl border border-white/5 bg-gray-900/80 px-3 py-3">
        <span className="block text-[10px] uppercase tracking-[0.3em] text-gray-500">Harvest</span>
        <span className="text-lg text-white">{recommendation.action.harvest}%</span>
      </div>
    </div>
  </div>
);

export default function BoxWall() {
  const [controlState, setControlState] = useState({
    lap: 30,
    battery_soc: 45,
    position: 3,
    rain: false,
  });
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<BoxWallResponse | null>(null);
  const [lastUpdated, setLastUpdated] = useState<number | null>(null);

  const formatLap = (lap: number) => `Lap ${lap}/57`;
  const formatPosition = (position: number) => `P${position}`;

  const launchAdvisor = () => {
    if (loading) return;
    setLoading(true);

    window.setTimeout(() => {
      setResponse(advisorMock);
      setLastUpdated(Date.now());
      setLoading(false);
    }, 520);
  };

  const leadRecommendation = response?.recommendations[0];

  const lapDescriptor = useMemo(() => {
    if (controlState.lap <= 10) return 'Lights-out phase';
    if (controlState.lap <= 35) return 'Mid-race management';
    return 'Final stint attack';
  }, [controlState.lap]);

  return (
    <section className="relative overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-br from-gray-950 via-black to-gray-950 p-8 shadow-2xl">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(0,160,233,0.12),transparent)] opacity-80" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(255,24,1,0.32),transparent_55%)] opacity-50" />

      <div className="relative z-10 space-y-8">
        <header className="max-w-3xl space-y-3">
          <h2 className="text-4xl font-bold text-white">Box Wall Advisor</h2>
          <p className="text-sm leading-relaxed text-gray-300">
            Adjust race telemetry, press the pit wall and get instant guidance on how aggressively to
            deploy the 350kW electric unit. We echo an F1 race engineer—precise, contextual, ruthless.
          </p>
        </header>

        <div className="grid gap-8 lg:grid-cols-[minmax(0,2.4fr)_minmax(0,2fr)]">
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <ControlSlider
                label="Race Lap"
                min={1}
                max={57}
                value={controlState.lap}
                unit=""
                accent="text-f1-blue"
                onChange={(lap) => setControlState((prev) => ({ ...prev, lap }))}
              />
              <ControlSlider
                label="Battery State"
                min={0}
                max={100}
                value={controlState.battery_soc}
                unit="%"
                accent="text-green-400"
                onChange={(battery_soc) => setControlState((prev) => ({ ...prev, battery_soc }))}
              />
              <ControlSlider
                label="Track Position"
                min={1}
                max={20}
                value={controlState.position}
                unit=""
                accent="text-amber-300"
                onChange={(position) => setControlState((prev) => ({ ...prev, position }))}
              />
              <div className="space-y-2 rounded-xl border border-white/5 bg-gray-900/70 p-4 shadow-inner">
                <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[0.28em] text-gray-400">
                  <span>Weather</span>
                  <span className="text-sm font-semibold text-white">
                    {controlState.rain ? 'Rain offset' : 'Dry trim'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() =>
                    setControlState((prev) => ({
                      ...prev,
                      rain: !prev.rain,
                    }))
                  }
                  className={`flex w-full items-center justify-between rounded-xl border border-white/5 px-4 py-3 text-sm transition ${
                    controlState.rain
                      ? 'bg-f1-blue/20 text-f1-blue'
                      : 'bg-gray-950 text-gray-300 hover:border-f1-blue/50 hover:text-white'
                  }`}
                >
                  <span>{controlState.rain ? 'Intermediate strategy engaged' : 'Stay on slicks'}</span>
                  <span className="text-lg">{controlState.rain ? '🌧️' : '☀️'}</span>
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-white/5 bg-gray-950/90 p-5">
              <div className="flex items-center justify-between font-mono text-xs uppercase tracking-[0.32em] text-gray-500">
                <span>{formatLap(controlState.lap)}</span>
                <span>{formatPosition(controlState.position)}</span>
              </div>
              <div className="mt-3 text-sm text-gray-300">
                {lapDescriptor} — Battery window at{' '}
                <span className="font-semibold text-white">{controlState.battery_soc}%</span>.
                {controlState.rain
                  ? ' Expect reduced regen efficiency; prioritize traction stability.'
                  : ' Track evolution favors aggressive deploy patterns.'}
              </div>
            </div>

            <button
              onClick={launchAdvisor}
              disabled={loading}
              className="group relative flex w-full items-center justify-center gap-3 overflow-hidden rounded-xl border border-f1-blue/40 bg-f1-blue/80 px-6 py-4 text-lg font-bold uppercase tracking-[0.35em] text-black transition hover:brightness-110 disabled:cursor-not-allowed disabled:border-gray-700 disabled:bg-gray-800 disabled:text-gray-400"
            >
              <span className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,255,255,0.15)_0%,transparent_45%,transparent_60%,rgba(255,255,255,0.15)_100%)] opacity-0 transition-all duration-300 group-hover:translate-x-12 group-hover:opacity-70" />
              {loading ? 'Crunching telemetry…' : 'Get Recommendation'}
            </button>

            <div className="rounded-xl border border-white/5 bg-gray-950/70 px-4 py-3 text-xs text-gray-500">
              {lastUpdated ? (
                <span>
                  Latest response in {(advisorMock.latency_ms).toFixed(1)} ms — synthetic data source
                  while the live simulator boots.
                </span>
              ) : (
                <span>Mocked box wall used until the simulator backend goes live.</span>
              )}
            </div>
          </div>

          <aside className="space-y-5">
            {leadRecommendation ? (
              <div className="rounded-2xl border border-f1-red/40 bg-f1-red/10 p-5">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold uppercase tracking-[0.35em] text-f1-red">
                    Primary Call
                  </h3>
                  <span className="text-xs font-mono text-gray-300">
                    Latency {advisorMock.latency_ms.toFixed(1)} ms
                  </span>
                </div>
                <div className="mt-3 text-xl font-semibold text-white">{leadRecommendation.rule}</div>
                <p className="mt-2 text-sm text-gray-200">{leadRecommendation.rationale}</p>
                <div className="mt-4 grid grid-cols-3 gap-3 text-center text-xs font-mono text-gray-200">
                  <div className="rounded-xl border border-white/10 bg-gray-950/70 px-3 py-3">
                    <span className="block text-[10px] uppercase tracking-[0.3em] text-gray-500">Deploy</span>
                    <span className="text-lg text-white">{leadRecommendation.action.deploy_straight}%</span>
                    <span className="text-[10px] text-gray-500">Straights</span>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-gray-950/70 px-3 py-3">
                    <span className="block text-[10px] uppercase tracking-[0.3em] text-gray-500">Deploy</span>
                    <span className="text-lg text-white">{leadRecommendation.action.deploy_corner}%</span>
                    <span className="text-[10px] text-gray-500">Corners</span>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-gray-950/70 px-3 py-3">
                    <span className="block text-[10px] uppercase tracking-[0.3em] text-gray-500">Harvest</span>
                    <span className="text-lg text-white">{leadRecommendation.action.harvest}%</span>
                    <span className="text-[10px] text-gray-500">Regen</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="rounded-2xl border border-white/5 bg-gray-950/70 p-5 text-sm text-gray-400">
                Run the advisor to surface a race engineer&apos;s best move for this stint.
              </div>
            )}

            {response && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-[0.35em] text-gray-400">
                  Alternative Plays
                </h3>
                <div className="space-y-3">
                  {response.recommendations.slice(1).map((recommendation) => (
                    <RecommendationCard key={recommendation.rule} recommendation={recommendation} />
                  ))}
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>
    </section>
  );
}
