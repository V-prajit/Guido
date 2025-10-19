'use client';

import { useMemo, useState } from 'react';

import mockData from '../../mock/boxWall.json';
import type { BoxWallData, RecommendationDetail, ScenarioControls } from '../../types';
import Button from '../shared/Button';
import RecommendationCard from './RecommendationCard';
import StateSliders from './StateSliders';
import TelemetryPanel from './TelemetryPanel';

const data = mockData as BoxWallData;

export default function BoxWall() {
  const [controls, setControls] = useState<ScenarioControls>(data.controls);
  const [recommendation, setRecommendation] = useState<RecommendationDetail>(data.recommendation);
  const [loading, setLoading] = useState(false);
  const [latency, setLatency] = useState(data.latency_ms);
  const [lastUpdated, setLastUpdated] = useState(data.last_updated);

  const rainSummary = useMemo(
    () => (controls.rain_forecasted ? 'Rain offset engaged' : 'Dry trim baseline'),
    [controls.rain_forecasted],
  );

  const handleFetch = () => {
    if (loading) return;
    setLoading(true);

    window.setTimeout(() => {
      // For now we reuse the mock recommendation but tweak latency to simulate fresh result.
      setLatency(data.latency_ms + Math.round(Math.random() * 120 - 60));
      setRecommendation({
        ...data.recommendation,
        strategy: controls.rain_forecasted
          ? 'Rain Offset Energy Save'
          : data.recommendation.strategy,
      });
      setLastUpdated(new Date().toISOString());
      setLoading(false);
    }, 680);
  };

  return (
    <section className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <div className="text-[11px] font-semibold uppercase tracking-[0.38em] text-[#777]">
          Box-Wall Advisor · Real-time strategy recommendation
        </div>
        <h2 className="text-4xl font-black uppercase leading-tight tracking-[0.08em] text-white">
          Pit Wall-grade Decision Support
        </h2>
        <p className="text-sm text-[#9f9f9f]">
          Live telemetry fused with Gemini reasoning surfaces the next call in under 1.2 seconds.
        </p>
      </header>

      <TelemetryPanel state={data.state} telemetry={data.telemetry} />

      <StateSliders controls={controls} setControls={setControls} />

      <div className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-[#1f1f1f] bg-[#0B0B0B] px-6 py-5">
        <div className="text-xs uppercase tracking-[0.3em] text-[#777]">
          Scenario modifiers · {rainSummary} · Safety car risk {controls.safety_car_risk}% · Aggression{' '}
          {controls.aggression}%
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={handleFetch} loading={loading}>
            Get New Recommendation
          </Button>
          <Button variant="secondary">Simulate Outcome</Button>
          <Button variant="ghost">Manual Override</Button>
        </div>
      </div>

      <RecommendationCard
        recommendation={recommendation}
        loading={loading}
        latencyMs={latency}
        lastUpdated={lastUpdated}
      />
    </section>
  );
}
