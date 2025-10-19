import type { StrategicRule } from '../../types';
import PerformanceBar from '../shared/PerformanceBar';
import EffectivenessHeatmap from './EffectivenessHeatmap';

interface RuleCardProps {
  rule: StrategicRule;
}

const disciplineColors: Record<string, string> = {
  energy: '#DC0000',
  tyre: '#FFD700',
  fuel: '#00A0E9',
  aero: '#67E8F9',
};

export default function RuleCard({ rule }: RuleCardProps) {
  const borderColor = disciplineColors[rule.discipline] ?? '#FF4444';
  const confidencePercent = Math.round(rule.confidence * 100);
  const upliftPercent = Math.round(rule.impact.uplift * 100);

  return (
    <article
      className="relative flex flex-col gap-5 rounded-3xl border border-[#1f1f1f] bg-[#101010] p-6 shadow-[0_20px_60px_rgba(0,0,0,0.45)]"
      style={{
        boxShadow: `0 20px 60px rgba(0,0,0,0.45), 0 0 40px ${borderColor}22`,
        borderImage: `linear-gradient(135deg, ${borderColor}55, rgba(30,30,30,0.6)) 1`,
      }}
    >
      <header className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 text-sm text-white">
            <span className="text-2xl">{rule.icon}</span>
            <div>
              <h3 className="text-2xl font-black uppercase tracking-[0.08em] text-white">
                {rule.rule}
              </h3>
              <span className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#777]">
                Discipline · {rule.discipline.toUpperCase()}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right text-xs uppercase tracking-[0.28em] text-[#888]">
              Confidence
            </div>
            <div className="w-28 rounded-full border border-[#1f1f1f] bg-[#0F0F0F] p-1">
              <div
                className="h-2 rounded-full"
                style={{
                  width: `${confidencePercent}%`,
                  background: `linear-gradient(90deg, ${borderColor}55, ${borderColor})`,
                  boxShadow: `0 0 16px ${borderColor}44`,
                }}
              />
            </div>
            <div className="font-mono text-sm text-white">{confidencePercent}%</div>
          </div>
        </div>
        <p className="text-sm font-mono text-[#aaaaaa]">{rule.condition}</p>
      </header>

      <div className="grid gap-4 rounded-2xl border border-[#1b1b1b] bg-[#0B0B0B] p-4 md:grid-cols-2">
        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#777]">
            Action Map
          </span>
          <PerformanceBar label="Deploy Straight" value={rule.action.deploy_straight} color="#DC0000" />
          <PerformanceBar label="Deploy Corner" value={rule.action.deploy_corner} color="#FF4444" />
          <PerformanceBar label="Harvest" value={rule.action.harvest} color="#4ADE80" />
        </div>
        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#777]">
            Impact
          </span>
          <div className="rounded-2xl border border-[#1f1f1f] bg-[#111] p-4">
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-[#888]">
              <span>Win uplift</span>
              <span className="font-mono text-white">+{upliftPercent}%</span>
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-[#1D1D1D]">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${upliftPercent}%`,
                  background: `linear-gradient(90deg, ${borderColor}55, ${borderColor})`,
                  boxShadow: `0 0 16px ${borderColor}66`,
                }}
              />
            </div>
            <div className="mt-4 text-xs text-[#999]">
              Expected outcome: <span className="font-mono text-white">{rule.impact.expected_outcome}</span>
            </div>
          </div>
        </div>
      </div>

      <p className="text-sm leading-relaxed text-[#9f9f9f]">{rule.rationale}</p>

      {rule.caveats && (
        <div className="rounded-2xl border border-[#322] bg-[#1a0f0f] px-4 py-3 text-xs text-[#ffb4b4]">
          Caveat: {rule.caveats}
        </div>
      )}

      <EffectivenessHeatmap data={rule.heatmap} />
    </article>
  );
}
