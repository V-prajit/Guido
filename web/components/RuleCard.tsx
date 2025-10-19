
'use client';

import { Rule } from '../types';

interface RuleCardProps {
  rule: Rule;
}

export default function RuleCard({ rule }: RuleCardProps) {
  return (
    <div className="bg-gray-700 p-6 rounded-lg border-l-4 border-blue-500 transition-all duration-300 ease-in-out hover:shadow-lg hover:border-blue-400">
      <h3 className="text-xl font-bold mb-2 text-white">{rule.rule}</h3>

      <div className="text-sm font-mono text-gray-400 mb-3 bg-gray-800 p-2 rounded">
        IF <span className="text-cyan-400">{rule.condition}</span>
      </div>

      <p className="text-gray-300 text-sm mb-4">{rule.rationale}</p>

      <div className="flex flex-wrap gap-4 mb-4">
        <div className="bg-green-900/50 px-3 py-1 rounded-full text-sm">
          <span className="text-green-300 font-bold">+{rule.uplift_win_pct.toFixed(1)}%</span>
          <span className="text-gray-300"> Win Rate Uplift</span>
        </div>
        <div className="bg-yellow-900/50 px-3 py-1 rounded-full text-sm">
          <span className="text-yellow-300 font-bold">{(rule.confidence * 100).toFixed(0)}%</span>
          <span className="text-gray-300"> Confidence</span>
        </div>
      </div>

      <details className="mt-3 text-sm">
        <summary className="cursor-pointer text-gray-400 hover:text-white">Show Actions & Caveats</summary>
        <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 bg-gray-800/50 p-3 rounded-md">
          <div className="text-center p-2 rounded-md bg-gray-900">
            <div className="font-bold text-lg text-blue-400">{rule.action.deploy_straight}%</div>
            <div className="text-xs text-gray-400">Straight Deploy</div>
          </div>
          <div className="text-center p-2 rounded-md bg-gray-900">
            <div className="font-bold text-lg text-green-400">{rule.action.deploy_corner}%</div>
            <div className="text-xs text-gray-400">Corner Deploy</div>
          </div>
          <div className="text-center p-2 rounded-md bg-gray-900">
            <div className="font-bold text-lg text-red-400">{rule.action.harvest}%</div>
            <div className="text-xs text-gray-400">Harvest</div>
          </div>
        </div>
        {rule.caveats && (
            <div className="mt-3 text-xs text-gray-400 border-l-2 border-yellow-500 pl-3">
                <strong>Caveat:</strong> {rule.caveats}
            </div>
        )}
      </details>
    </div>
  );
}

