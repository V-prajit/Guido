import type { AgentProfile } from '../../types';
import PerformanceBar from '../shared/PerformanceBar';

interface AgentCardProps {
  agent: AgentProfile;
  align?: 'left' | 'right';
}

export default function AgentCard({ agent, align = 'left' }: AgentCardProps) {
  const layoutClasses =
    align === 'left'
      ? 'items-start text-left border-l-4'
      : 'items-end text-right border-r-4';

  const accentStyle =
    align === 'left'
      ? { borderColor: agent.accent, boxShadow: `-8px 0 30px ${agent.glow}` }
      : { borderColor: agent.accent, boxShadow: `8px 0 30px ${agent.glow}` };

  return (
    <div
      className={`relative flex h-full w-full flex-col gap-4 rounded-3xl border bg-[#111111] px-6 py-6 shadow-[0_20px_60px_rgba(0,0,0,0.45)] ${layoutClasses}`}
      style={accentStyle}
    >
      <div className="flex flex-col gap-2">
        <span className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#666]">
          Agent
        </span>
        <h3
          className="text-4xl font-black uppercase text-white"
          style={{ textShadow: `0 0 22px ${agent.glow}` }}
        >
          {agent.codename}
        </h3>
        <span className="text-sm text-[#aaaaaa]">{agent.strapline}</span>
      </div>

      <div className="flex items-center gap-4 text-sm text-[#cccccc]">
        <div className="rounded-full border border-[#222] bg-[#151515] px-4 py-2 font-mono text-lg text-white">
          P{agent.position}
        </div>
        <div className="rounded-full border border-[#222] bg-[#151515] px-4 py-2 font-mono text-lg text-white">
          {agent.lap_time.toFixed(2)}s
        </div>
        <div className="rounded-full border border-[#222] bg-[#151515] px-4 py-2 font-mono text-lg text-white">
          {agent.gap_to_leader === 0 ? 'Leader' : `+${agent.gap_to_leader.toFixed(2)}s`}
        </div>
      </div>

      <p className="text-sm leading-relaxed text-[#9f9f9f]">{agent.description}</p>

      <div className="grid gap-3">
        <PerformanceBar
          label="Deploy Straight"
          value={agent.energy_split.deploy_straight}
          color={agent.color}
        />
        <PerformanceBar
          label="Deploy Corner"
          value={agent.energy_split.deploy_corner}
          color={agent.accent}
        />
        <PerformanceBar
          label="Harvest"
          value={agent.energy_split.harvest}
          color="#4ADE80"
        />
      </div>
    </div>
  );
}
