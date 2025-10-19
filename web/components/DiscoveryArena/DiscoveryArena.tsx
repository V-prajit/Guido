import dynamic from 'next/dynamic';

import mockData from '../../mock/discoveryArena.json';
import type { DiscoveryArenaData } from '../../types';
import Button from '../shared/Button';
import AgentCard from './AgentCard';
import PerformanceMatrix from './PerformanceMatrix';
import TrackMap from './TrackMap';

const data = mockData as DiscoveryArenaData;
const LapComparison = dynamic(() => import('./LapComparison'), { ssr: false });

export default function DiscoveryArena() {
  const [agentOne, agentTwo] = data.agents;

  const headerSubtitle = `${data.circuit.name.toUpperCase()}  |  ${data.circuit.weekend}  →  ${data.circuit.season}`;

  return (
    <section className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <div className="text-[11px] font-semibold uppercase tracking-[0.38em] text-[#777]">
          Strategy Gym 2026 • powered by {data.circuit.powered_by}
        </div>
        <h1 className="text-4xl font-black uppercase leading-tight tracking-[0.08em] text-white">
          Discovery Arena • Agent Showdown
        </h1>
        <p className="text-sm uppercase tracking-[0.3em] text-[#999]">{headerSubtitle}</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.3fr)_minmax(0,1.1fr)]">
        <AgentCard agent={agentOne} align="left" />
        <TrackMap sections={data.track_sections} agentOneColor={agentOne.color} agentTwoColor={agentTwo.color} />
        <AgentCard agent={agentTwo} align="right" />
      </div>

      <PerformanceMatrix
        metrics={data.metrics}
        agentOneColor={agentOne.color}
        agentTwoColor={agentTwo.color}
      />

      <LapComparison batteryData={data.lap_battery} deltaData={data.lap_delta} />

      <div className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-[#1f1f1f] bg-[#0B0B0B] px-6 py-5">
        <div className="flex flex-col gap-1 text-xs uppercase tracking-[0.3em] text-[#777]">
          <span>
            {data.circuit.total_laps} laps • {data.circuit.turns} turns • Comparative energy deployment
          </span>
          <span className="text-[#555]">
            Run virtual race weekends to surface winning playbooks for the 2026 hybrid era.
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button>Run New Race</Button>
          <Button variant="secondary">Compare Different Agents</Button>
          <Button variant="ghost">Export Data</Button>
        </div>
      </div>
    </section>
  );
}
