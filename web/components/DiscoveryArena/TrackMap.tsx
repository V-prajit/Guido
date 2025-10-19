import type { TrackSection } from '../../types';

interface TrackMapProps {
  sections: TrackSection[];
  agentOneColor: string;
  agentTwoColor: string;
}

const valueToOpacity = (value: number) => 0.25 + (value / 100) * 0.65;
const valueToWidth = (value: number) => 6 + (value / 100) * 4;

export default function TrackMap({ sections, agentOneColor, agentTwoColor }: TrackMapProps) {
  return (
    <div className="relative h-full w-full rounded-3xl border border-[#1f1f1f] bg-[#0D0D0D] p-6 shadow-[0_20px_60px_rgba(0,0,0,0.55)]">
      <div className="mb-4 flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.32em] text-[#666]">
        <span>Track Deployment Heat</span>
        <span>Battery flow per sector</span>
      </div>
      <div className="relative h-[260px] w-full">
        <svg viewBox="0 0 1140 360" className="h-full w-full">
          <defs>
            <filter id="glow-red" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="8" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="glow-gold" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="8" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {sections.map((section) => (
            <g key={section.id}>
              <path
                d={section.svg_path}
                fill="none"
                stroke={agentTwoColor}
                strokeOpacity={valueToOpacity(section.agent_two_deploy)}
                strokeWidth={valueToWidth(section.agent_two_deploy)}
                strokeLinecap="round"
                filter="url(#glow-gold)"
              />
              <path
                d={section.svg_path}
                fill="none"
                stroke={agentOneColor}
                strokeOpacity={valueToOpacity(section.agent_one_deploy)}
                strokeWidth={valueToWidth(section.agent_one_deploy) + 3}
                strokeLinecap="round"
                filter="url(#glow-red)"
              />
            </g>
          ))}
        </svg>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-[#9f9f9f]">
        {sections.map((section) => (
          <div
            key={section.id}
            className="flex items-center justify-between rounded-xl border border-[#1f1f1f] bg-[#121212] px-3 py-2 font-mono"
          >
            <span className="uppercase tracking-[0.26em] text-[#777]">{section.label}</span>
            <span className="flex items-center gap-3">
              <span className="flex items-center gap-1 text-[#f5f5f5]">
                <span className="inline-block h-2 w-2 rounded-full" style={{ background: agentOneColor }} />
                {section.agent_one_deploy}%
              </span>
              <span className="flex items-center gap-1 text-[#f5f5f5]">
                <span className="inline-block h-2 w-2 rounded-full" style={{ background: agentTwoColor }} />
                {section.agent_two_deploy}%
              </span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
