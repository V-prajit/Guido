import type { PerformanceMetric } from '../../types';
import PerformanceBar from '../shared/PerformanceBar';

interface PerformanceMatrixProps {
  metrics: PerformanceMetric[];
  agentOneColor: string;
  agentTwoColor: string;
}

export default function PerformanceMatrix({
  metrics,
  agentOneColor,
  agentTwoColor,
}: PerformanceMatrixProps) {
  return (
    <div className="grid gap-4 rounded-3xl border border-[#1f1f1f] bg-[#0E0E0E] p-6 shadow-[0_18px_50px_rgba(0,0,0,0.45)] lg:grid-cols-2">
      {metrics.map((metric) => (
        <div key={metric.label} className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#777]">
            {metric.label}
          </span>
          <div className="grid gap-3">
            <PerformanceBar
              label="Agent Δ"
              value={metric.agent_one}
              comparison={metric.agent_two}
              unit={metric.unit}
              color={agentOneColor}
            />
            <PerformanceBar
              label="Opponent"
              value={metric.agent_two}
              unit={metric.unit}
              color={agentTwoColor}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
