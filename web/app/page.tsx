'use client';

import { useMemo, useState } from 'react';

import BoxWall from '../components/BoxWall/BoxWall';
import DiscoveryArena from '../components/DiscoveryArena/DiscoveryArena';
import PlaybookView from '../components/PlaybookView/PlaybookView';

type ViewKey = 'arena' | 'playbook' | 'boxwall';

const tabs: Array<{ key: ViewKey; label: string; subtitle: string }> = [
  { key: 'arena', label: 'Discovery Arena', subtitle: 'Agent vs agent race comparison' },
  { key: 'playbook', label: 'Playbook Analysis', subtitle: 'Gemini strategic insights' },
  { key: 'boxwall', label: 'Box-Wall Advisor', subtitle: 'Real-time pit wall calls' },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<ViewKey>('arena');

  const ActiveView = useMemo(() => {
    switch (activeTab) {
      case 'playbook':
        return <PlaybookView />;
      case 'boxwall':
        return <BoxWall />;
      case 'arena':
      default:
        return <DiscoveryArena />;
    }
  }, [activeTab]);

  return (
    <main className="min-h-screen w-full text-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-10 px-6 py-10 lg:px-12">
        <header className="flex flex-col gap-4 rounded-3xl border border-[#1f1f1f] bg-[#0B0B0B]/80 p-8 shadow-[0_25px_80px_rgba(0,0,0,0.55)] backdrop-blur">
          <div className="text-[11px] font-semibold uppercase tracking-[0.38em] text-[#777]">
            Strategy Gym 2026 • Simulation-first race intelligence
          </div>
          <h1 className="text-5xl font-black uppercase leading-tight tracking-[0.06em] text-white lg:text-6xl">
            F1-grade Analytics for the 2026 Hybrid Era
          </h1>
          <p className="max-w-3xl text-sm text-[#9f9f9f]">
            Spin up virtual race weekends, distil winning playbooks with Gemini, and deliver pit wall
            calls in sub-second latency. This is the Strategy Gym control centre—built to feel like a
            $10M broadcast graphic.
          </p>
        </header>

        <nav className="grid gap-3 rounded-3xl border border-[#1f1f1f] bg-[#0A0A0A] p-4 shadow-[0_18px_60px_rgba(0,0,0,0.45)] md:grid-cols-3">
          {tabs.map((tab) => {
            const isActive = tab.key === activeTab;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`flex flex-col gap-2 rounded-2xl border px-5 py-4 text-left transition ${
                  isActive
                    ? 'border-transparent bg-gradient-to-br from-[#DC0000] via-[#FF4444] to-[#DC0000] text-white shadow-[0_16px_45px_rgba(220,0,0,0.45)]'
                    : 'border-[#1f1f1f] bg-[#111111] text-[#aaaaaa] hover:border-[#DC0000] hover:text-white'
                }`}
              >
                <span className="text-sm font-bold uppercase tracking-[0.2em]">{tab.label}</span>
                <span className="text-xs uppercase tracking-[0.28em] text-[#777]">{tab.subtitle}</span>
              </button>
            );
          })}
        </nav>

        {ActiveView}
      </div>
    </main>
  );
}
