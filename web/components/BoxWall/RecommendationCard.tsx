import type { RecommendationDetail } from '../../types';
import PerformanceBar from '../shared/PerformanceBar';

interface RecommendationCardProps {
  recommendation: RecommendationDetail;
  loading: boolean;
  latencyMs: number;
  lastUpdated: string;
}

export default function RecommendationCard({
  recommendation,
  loading,
  latencyMs,
  lastUpdated,
}: RecommendationCardProps) {
  const confidencePercent = Math.round(recommendation.confidence * 100);

  return (
    <div className="flex flex-col gap-5 rounded-3xl border border-[#1f1f1f] bg-[#101010] p-6 shadow-[0_20px_60px_rgba(0,0,0,0.45)]">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#777]">
            Recommendation
          </span>
          <h3 className="text-3xl font-black uppercase tracking-[0.08em] text-white">
            {recommendation.strategy}
          </h3>
        </div>
        <div className="rounded-full border border-[#1f1f1f] bg-[#0D0D0D] px-4 py-2 text-xs uppercase tracking-[0.28em] text-[#777]">
          {loading ? 'Analyzing…' : `Latency ${latencyMs.toFixed(0)} ms · Updated ${new Date(lastUpdated).toLocaleTimeString()}`}
        </div>
      </header>

      <p className="text-sm leading-relaxed text-[#9f9f9f]">{recommendation.rationale}</p>

      <div className="grid gap-3 rounded-2xl border border-[#1f1f1f] bg-[#0C0C0C] p-5">
        <div className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-[#777]">
          <span>Execution Plan</span>
          <span className="font-mono text-white">{recommendation.expected_outcome}</span>
        </div>
        <PerformanceBar
          label="Deploy straight"
          value={recommendation.action.deploy_straight}
          color="#DC0000"
          unit="%"
        />
        <PerformanceBar
          label="Deploy corner"
          value={recommendation.action.deploy_corner}
          color="#FF5555"
          unit="%"
        />
        <PerformanceBar
          label="Harvest"
          value={recommendation.action.harvest}
          color="#4ADE80"
          unit="%"
        />
        <div className="text-xs text-[#888]">
          Fuel mode: <span className="font-mono text-white">{recommendation.action.fuel_mode}</span>
          {recommendation.action.note && (
            <>
              {' '}
              · <span className="text-[#bbb]">{recommendation.action.note}</span>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="w-32 rounded-full border border-[#1f1f1f] bg-[#0D0D0D] p-1">
          <div
            className="h-2 rounded-full"
            style={{
              width: `${confidencePercent}%`,
              background: 'linear-gradient(90deg, #FFD70055, #FFD700)',
              boxShadow: '0 0 16px rgba(255,215,0,0.45)',
            }}
          />
        </div>
        <span className="font-mono text-sm text-white">{confidencePercent}% confident</span>
      </div>

      {recommendation.alternative && (
        <div className="rounded-2xl border border-[#1f1f1f] bg-[#0C0C0C] p-5 text-sm text-[#9f9f9f]">
          <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.28em] text-[#777]">
            Alternative Play · {recommendation.alternative.summary}
          </div>
          <div className="grid gap-2">
            <div className="flex flex-wrap items-center gap-3 text-xs text-[#bbb]">
              <span>Deploy straight {recommendation.alternative.deploy_straight}%</span>
              <span>Deploy corner {recommendation.alternative.deploy_corner}%</span>
              <span>Harvest {recommendation.alternative.harvest}%</span>
            </div>
            <div className="text-xs text-[#777]">
              Fuel mode: <span className="font-mono text-white">{recommendation.alternative.fuel_mode}</span>
              {recommendation.alternative.note && (
                <>
                  {' '}
                  · <span className="text-[#bbb]">{recommendation.alternative.note}</span>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
