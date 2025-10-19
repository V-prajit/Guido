
'use client';

import { useState } from 'react';
import { Playbook } from '../types';
import RuleCard from './RuleCard';
import mockData from '../mock/mockPlaybook.json';

export default function PlaybookView() {
  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [loading, setLoading] = useState(false);

  const loadPlaybook = () => {
    setLoading(true);
    // Simulate network delay
    setTimeout(() => {
      setPlaybook(mockData as Playbook);
      setLoading(false);
    }, 500);
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg">
      <h2 className="text-3xl font-bold mb-6">Strategic Playbook</h2>

      {!playbook && (
        <div className="text-center">
          <p className="text-gray-400 mb-4">No playbook loaded. Generate one from the Discovery Arena or load mock data.</p>
          <button
            onClick={loadPlaybook}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 px-8 py-3 rounded-lg font-bold transition-all duration-300 disabled:bg-gray-500"
          >
            {loading ? 'Loading Mock Data...' : 'Load Mock Playbook'}
          </button>
        </div>
      )}

      {playbook && (
        <>
          <div className="mb-6 text-gray-400 flex justify-between items-center">
            <span>
              <span className="font-bold text-white">{playbook.rules.length}</span> rules discovered from <span className="font-bold text-white">{playbook.num_simulations.toLocaleString()}</span> simulations.
            </span>
            <span className="text-xs">Generated at: {new Date(playbook.generated_at).toLocaleString()}</span>
          </div>

          <div className="space-y-4">
            {playbook.rules.map((rule, i) => (
              <RuleCard key={i} rule={rule} />
            ))}
          </div>
        </> 
      )}
    </div>
  );
}