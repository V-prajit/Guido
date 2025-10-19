import type { RuleHeatmapCell } from '../../types';

interface EffectivenessHeatmapProps {
  data: RuleHeatmapCell[];
}

const lerpColor = (value: number) => {
  const clamped = Math.min(1, Math.max(0, value));
  const start = [30, 64, 175]; // deep blue
  const end = [99, 255, 191]; // bright green
  const rgb = start.map((component, index) =>
    Math.round(component + (end[index] - component) * clamped),
  );
  return `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${0.85})`;
};

export default function EffectivenessHeatmap({ data }: EffectivenessHeatmapProps) {
  if (!data.length) return null;

  const maxEffectiveness = Math.max(...data.map((item) => item.effectiveness || 0.001));

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.28em] text-[#777]">
        <span>Effectiveness Heatmap</span>
        <span>Battery SOC vs Lap</span>
      </div>
      <div className="grid gap-2">
        {data.map((cell) => (
          <div
            key={`${cell.lap}-${cell.battery}`}
            className="flex items-center gap-3 rounded-xl border border-[#1d1d1d] bg-[#0F0F0F] px-3 py-2 text-xs text-[#aaa]"
          >
            <div className="font-mono text-sm text-white">
              Lap {cell.lap} • {cell.battery}%
            </div>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-[#1C1C1C]">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${(cell.effectiveness / maxEffectiveness) * 100}%`,
                  background: lerpColor(cell.effectiveness / maxEffectiveness),
                  boxShadow: `0 0 14px ${lerpColor(cell.effectiveness / maxEffectiveness)}`,
                }}
              />
            </div>
            <span className="font-mono text-xs text-white">
              {(cell.effectiveness * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
