'use client';

import { useState } from 'react';
import DiscoveryArena from '../components/DiscoveryArena';
import PlaybookView from '../components/PlaybookView';
import BoxWall from '../components/BoxWall';

export default function Home() {
  const [activeTab, setActiveTab] = useState('arena');

  return (
    <main className="min-h-screen p-8">
      <header className="mb-8 text-center">
        <h1 className="text-6xl font-bold mb-2" style={{ fontFamily: 'Orbitron, sans-serif' }}>Strategy Gym 2026</h1>
        <p className="text-gray-400">F1 Energy Management Strategy Discovery</p>
      </header>

      <nav className="flex justify-center gap-4 mb-8 border-b border-f1-gray pb-4">
        <button
          onClick={() => setActiveTab('arena')}
          className={`px-6 py-2 text-lg font-bold rounded-t-lg ${activeTab === 'arena' ? 'bg-f1-red text-f1-white' : 'bg-f1-gray text-gray-400'}`}
        >
          Discovery Arena
        </button>
        <button
          onClick={() => setActiveTab('playbook')}
          className={`px-6 py-2 text-lg font-bold rounded-t-lg ${activeTab === 'playbook' ? 'bg-f1-red text-f1-white' : 'bg-f1-gray text-gray-400'}`}
        >
          Playbook
        </button>
        <button
          onClick={() => setActiveTab('boxwall')}
          className={`px-6 py-2 text-lg font-bold rounded-t-lg ${activeTab === 'boxwall' ? 'bg-f1-red text-f1-white' : 'bg-f1-gray text-gray-400'}`}
        >
          Box Wall
        </button>
      </nav>

      {activeTab === 'arena' && <DiscoveryArena />}
      {activeTab === 'playbook' && <PlaybookView />}
      {activeTab === 'boxwall' && <BoxWall />}
    </main>
  );
}