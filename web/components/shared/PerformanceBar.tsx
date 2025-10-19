import type { ReactNode } from 'react';

interface PerformanceBarProps {
  label: string;
  value: number;
  comparison?: number;
  unit?: string;
  color: string;
  icon?: ReactNode;
}

const clamp = (value: number) => Math.min(100, Math.max(0, value));

export default function PerformanceBar({
  label,
  value,
  comparison,
  unit = '%',
  color,
  icon,
}: PerformanceBarProps) {
  return (
    <div className="rounded-2xl border border-[#1f1f1f] bg-[#121212] p-4 shadow-[0_12px_32px_rgba(0,0,0,0.35)]">
      <div className="mb-2 flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.28em] text-[#888]">
        <span className="flex items-center gap-2">
          {icon && <span className="text-base text-white">{icon}</span>}
          {label}
        </span>
        {typeof comparison === 'number' && (
          <span className="text-[#666]">
            vs <span className="font-bold text-white">{comparison.toFixed(0) + unit}</span>
          </span>
        )}
      </div>
      <div className="flex items-center gap-3">
        <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-[#1F1F1F]">
          <div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{
              width: `${clamp(value)}%`,
              background: `linear-gradient(90deg, ${color}44, ${color})`,
              boxShadow: `0 0 16px ${color}55`,
            }}
          />
        </div>
        <div className="font-mono text-sm text-white">
          {value.toFixed(0)}
          {unit}
        </div>
      </div>
    </div>
  );
}
