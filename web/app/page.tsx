'use client';

import { useState } from 'react';
import DiscoveryArena from './components/DiscoveryArena';
import PlaybookView from './components/PlaybookView';
import BoxWall from './components/BoxWall';

export default function Home() {
  const [activeTab, setActiveTab] = useState('arena');

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-8">
        <h1 className="text-5xl font-bold mb-2">Strategy Gym 2026</h1>
        <p className="text-gray-400">F1 Energy Management Strategy Discovery</p>
      </header>

      <nav className="flex gap-4 mb-8 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('arena')}
          className={`px-6 py-3 ${activeTab === 'arena' ? 'border-b-2 border-blue-500' : ''}`}
        >
          Discovery Arena
        </button>
        <button
          onClick={() => setActiveTab('playbook')}
          className={`px-6 py-3 ${activeTab === 'playbook' ? 'border-b-2 border-blue-500' : ''}`}
        >
          Playbook
        </button>
        <button
          onClick={() => setActiveTab('boxwall')}
          className={`px-6 py-3 ${activeTab === 'boxwall' ? 'border-b-2 border-blue-500' : ''}`}
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