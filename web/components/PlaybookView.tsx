


'use client';



import { useState, useMemo } from 'react';

import { Playbook, Rule } from '../types';

import RuleCard from './RuleCard';

import mockData from '../mock/mockPlaybook.json';



type SortKey = 'confidence' | 'uplift_win_pct' | 'default';



export default function PlaybookView() {

  const [playbook, setPlaybook] = useState<Playbook | null>(null);

  const [loading, setLoading] = useState(false);

  const [sortKey, setSortKey] = useState<SortKey>('default');

  const [filter, setFilter] = useState('');



  const loadPlaybook = () => {

    setLoading(true);

    setTimeout(() => {

      setPlaybook(mockData as Playbook);

      setLoading(false);

    }, 500);

  };



  const sortedAndFilteredRules = useMemo(() => {

    if (!playbook) return [];



    const filtered = playbook.rules.filter(rule =>

      rule.rule.toLowerCase().includes(filter.toLowerCase()) ||

      rule.condition.toLowerCase().includes(filter.toLowerCase()) ||

      rule.rationale.toLowerCase().includes(filter.toLowerCase())

    );



    if (sortKey === 'default') {

      return filtered;

    }



    return [...filtered].sort((a, b) => {

      if (sortKey === 'confidence') {

        return b.confidence - a.confidence;

      }

      if (sortKey === 'uplift_win_pct') {

        return b.uplift_win_pct - a.uplift_win_pct;

      }

      return 0;

    });

  }, [playbook, sortKey, filter]);



  const SortButton = ({ value, label }: { value: SortKey; label: string }) => (

    <button

      onClick={() => setSortKey(value)}

      className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${sortKey === value ? 'bg-blue-600 text-white' : 'bg-gray-700 hover:bg-gray-600'}`}>

      {label}

    </button>

  );



  return (

    <div className="bg-gray-800 p-8 rounded-lg">

      <div className="flex justify-between items-center mb-6">

        <h2 className="text-3xl font-bold">Strategic Playbook</h2>

        {!playbook && (

            <button

                onClick={loadPlaybook}

                disabled={loading}

                className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-bold transition-all duration-300 disabled:bg-gray-500">

                {loading ? 'Loading...' : 'Load Mock Playbook'}

            </button>

        )}

      </div>



      {playbook && (

        <>

          <div className="mb-6 p-4 bg-gray-900/50 rounded-lg flex flex-col md:flex-row justify-between items-center gap-4">

            <input

              type="text"

              placeholder="Filter rules by name, condition, or rationale..."

              value={filter}

              onChange={(e) => setFilter(e.target.value)}

              className="w-full md:w-1/3 bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"

            />

            <div className="flex items-center gap-2">

              <span className="text-sm text-gray-400">Sort by:</span>

              <SortButton value="default" label="Default" />

              <SortButton value="confidence" label="Confidence" />

              <SortButton value="uplift_win_pct" label="Win Uplift" />

            </div>

          </div>



          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {sortedAndFilteredRules.map((rule, i) => (

              <RuleCard key={i} rule={rule} />

            ))}

          </div>

        </>

      )}

    </div>

  );

}
