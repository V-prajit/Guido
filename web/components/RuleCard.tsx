
'use client';

import { Rule } from '../types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface RuleCardProps {
  rule: Rule;
}

const actionData = (rule: Rule) => [
  { name: 'Straight', value: rule.action.deploy_straight, color: '#60a5fa' }, // blue-400
  { name: 'Corner', value: rule.action.deploy_corner, color: '#4ade80' }, // green-400
  { name: 'Harvest', value: rule.action.harvest, color: '#f87171' }, // red-400
];

export default function RuleCard({ rule }: RuleCardProps) {
  const data = actionData(rule);

  return (
    <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600/50 transition-all duration-300 ease-in-out hover:shadow-xl hover:border-blue-500/50 flex flex-col">
      <div className="flex-grow">
        <h3 className="text-lg font-bold mb-2 text-white">{rule.rule}</h3>

        <div className="text-xs font-mono text-gray-400 mb-3 bg-gray-800 p-2 rounded">
          IF <span className="text-cyan-300">{rule.condition}</span>
        </div>

        <p className="text-gray-300 text-sm mb-4 flex-grow">{rule.rationale}</p>

        <div className="flex flex-wrap gap-2 mb-4">
          <div className="bg-green-900/70 px-3 py-1 rounded-full text-xs flex items-center">
            <span className="text-green-300 font-bold mr-1">▲ +{rule.uplift_win_pct.toFixed(1)}%</span>
            <span className="text-gray-300">Win Uplift</span>
          </div>
          <div className="bg-yellow-900/70 px-3 py-1 rounded-full text-xs flex items-center">
            <span className="text-yellow-300 font-bold mr-1">{(rule.confidence * 100).toFixed(0)}%</span>
            <span className="text-gray-300">Confidence</span>
          </div>
        </div>
      </div>

      <div className="mt-auto">
        <div className="h-28 w-full bg-gray-800/50 p-2 rounded-md">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 15, right: 5, left: -25, bottom: 0 }}>
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#9ca3af" fontSize={10} tickLine={false} axisLine={false} />
              <Tooltip
                cursor={{ fill: 'rgba(100, 116, 139, 0.1)' }}
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', fontSize: '12px' }}
                labelStyle={{ color: '#d1d5db' }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {rule.caveats && (
          <div className="mt-3 text-xs text-yellow-300/80 border-l-2 border-yellow-500/50 pl-3">
            <strong>Caveat:</strong> {rule.caveats}
          </div>
        )}
      </div>
    </div>
  );
}
