import type { RaceState, TelemetryGauge } from '../../types';
import CountUpNumber from '../shared/CountUpNumber';

interface TelemetryPanelProps {
  state: RaceState;
  telemetry: TelemetryGauge[];
}

const gaugePercentage = (value: number, max: number) => Math.min(100, Math.round((value / max) * 100));

export default function TelemetryPanel({ state, telemetry }: TelemetryPanelProps) {
  return (
    <div className="grid gap-4 rounded-3xl border border-[#1f1f1f] bg-[#0C0C0C] p-6 shadow-[0_18px_60px_rgba(0,0,0,0.45)]">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-[#1f1f1f] bg-[#121212] p-4 text-[#bbbbbb]">
          <div className="text-[10px] uppercase tracking-[0.32em] text-[#777]">Lap</div>
          <div className="mt-2 text-3xl font-black text-white">
            <CountUpNumber value={state.lap} suffix={` / ${state.total_laps}`} />
          </div>
        </div>
        <div className="rounded-2xl border border-[#1f1f1f] bg-[#121212] p-4 text-[#bbbbbb]">
          <div className="text-[10px] uppercase tracking-[0.32em] text-[#777]">Position</div>
          <div className="mt-2 flex items-baseline gap-2 text-white">
            <span className="text-3xl font-black">P{state.position}</span>
            <span className="text-xs uppercase tracking-[0.32em] text-[#777]">
              Gap ahead +{state.gap_ahead.toFixed(1)}s
            </span>
          </div>
          <div className="mt-1 text-xs uppercase tracking-[0.32em] text-[#777]">
            Gap behind {state.gap_behind > 0 ? '+' : ''}
            {state.gap_behind.toFixed(1)}s
          </div>
        </div>
        <div className="rounded-2xl border border-[#1f1f1f] bg-[#121212] p-4 text-[#bbbbbb]">
          <div className="text-[10px] uppercase tracking-[0.32em] text-[#777]">Tyres & Conditions</div>
          <div className="mt-2 text-lg font-semibold text-white">{state.tyre_compound}</div>
          <div className="text-xs uppercase tracking-[0.28em] text-[#777]">
            {state.track_condition}
          </div>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {telemetry.map((gauge) => {
          const percent = gaugePercentage(gauge.value, gauge.max);
          return (
            <div
              key={gauge.label}
              className="rounded-2xl border border-[#1f1f1f] bg-[#101010] p-4 text-xs uppercase tracking-[0.28em] text-[#777]"
            >
              <div className="mb-3 flex items-center justify-between">
                <span>{gauge.label}</span>
                <span className="font-mono text-sm text-white">
                  {gauge.value}
                  {gauge.unit ?? ''}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-[#1C1C1C]">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${percent}%`,
                    background: `linear-gradient(90deg, ${gauge.color}55, ${gauge.color})`,
                    boxShadow: `0 0 16px ${gauge.color}44`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
