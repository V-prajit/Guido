import type { Dispatch, SetStateAction } from 'react';

import type { ScenarioControls } from '../../types';

interface StateSlidersProps {
  controls: ScenarioControls;
  setControls: Dispatch<SetStateAction<ScenarioControls>>;
}

export default function StateSliders({ controls, setControls }: StateSlidersProps) {
  return (
    <div className="grid gap-4 rounded-3xl border border-[#1f1f1f] bg-[#0C0C0C] p-6 shadow-[0_18px_60px_rgba(0,0,0,0.45)] md:grid-cols-2">
      <div className="flex flex-col gap-3">
        <span className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#777]">
          Rain Forecasted
        </span>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setControls((prev) => ({ ...prev, rain_forecasted: false }))}
            className={`w-1/2 rounded-full border px-4 py-3 text-sm font-semibold uppercase tracking-[0.28em] transition ${
              controls.rain_forecasted
                ? 'border-[#1f1f1f] bg-[#111111] text-[#777]'
                : 'border-[#FFD700] bg-[#1a1504] text-[#FFD700]'
            }`}
          >
            Off
          </button>
          <button
            type="button"
            onClick={() => setControls((prev) => ({ ...prev, rain_forecasted: true }))}
            className={`w-1/2 rounded-full border px-4 py-3 text-sm font-semibold uppercase tracking-[0.28em] transition ${
              controls.rain_forecasted
                ? 'border-[#00A0E9] bg-[#06141d] text-[#00A0E9]'
                : 'border-[#1f1f1f] bg-[#111111] text-[#777]'
            }`}
          >
            On
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <span className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#777]">
          Safety Car Risk
        </span>
        <input
          type="range"
          min={0}
          max={100}
          value={controls.safety_car_risk}
          onChange={(event) =>
            setControls((prev) => ({ ...prev, safety_car_risk: Number(event.target.value) }))
          }
        />
        <div className="font-mono text-sm text-white">{controls.safety_car_risk}%</div>
      </div>

      <div className="flex flex-col gap-3">
        <span className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#777]">
          Aggression Level
        </span>
        <input
          type="range"
          min={0}
          max={100}
          value={controls.aggression}
          onChange={(event) =>
            setControls((prev) => ({ ...prev, aggression: Number(event.target.value) }))
          }
        />
        <div className="font-mono text-sm text-white">{controls.aggression}%</div>
      </div>
    </div>
  );
}
