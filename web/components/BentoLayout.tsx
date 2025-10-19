'use client';

import { useState } from 'react';
import Box1_RaceTrack from './BentoBoxes/Box1_RaceTrack';

export default function BentoLayout() {
  const [selectedStrategy, setSelectedStrategy] = useState<number>(0);

  const strategies = [
    {
      name: "Aggressive Attack",
      probability: "75%",
      explanation: "Rain reduces grip advantage. Deploy power now to gain track position before conditions worsen."
    },
    {
      name: "Conservative Play",
      probability: "58%",
      explanation: "Maintain current pace and tire management. Wait for opponent mistakes in difficult conditions."
    },
    {
      name: "Balanced Drive",
      probability: "67%",
      explanation: "Moderate push with strategic overtaking. Balance risk and reward for optimal position gain."
    }
  ];

  return (
    <div className="w-full min-h-screen bg-white p-6">
      <div className="max-w-[1800px] mx-auto">
        {/* Top Section - 4 Boxes */}
        <div className="grid grid-cols-12 gap-4 mb-4">
          {/* BOX 1: Race Track View */}
          <Box1_RaceTrack />

          {/* Simulation Progress */}
          <div className="col-span-3 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">SIMULATION PROGRESS</h3>
            <div className="space-y-3">
              <p className="text-2xl font-bold text-black">Running 80/100 Simulations</p>
              <div className="w-full h-2 bg-black/20 rounded-full overflow-hidden">
                <div className="h-full bg-black w-4/5 transition-all duration-300"></div>
              </div>
              <p className="text-xs text-black/60">Estimated completion: 2m 15s</p>
            </div>
          </div>

          {/* Opponent Strategy */}
          <div className="col-span-3 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">OPPONENT STRATEGY</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between border-b border-black/20 pb-2">
                <span className="text-sm text-black">Early Pit</span>
                <span className="text-xs text-black/60">Verstappen</span>
              </div>
              <div className="flex items-center justify-between border-b border-black/20 pb-2">
                <span className="text-sm text-black">Fuel Management</span>
                <span className="text-xs text-black/60">Hamilton</span>
              </div>
              <div className="flex items-center justify-between pb-2">
                <span className="text-sm text-black">Tire Conservation</span>
                <span className="text-xs text-black/60">Leclerc</span>
              </div>
            </div>
          </div>

          {/* Player Telemetry */}
          <div className="col-span-3 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">PLAYER TELEMETRY</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-black/60">Lap</span>
                <span className="text-sm font-bold text-black">15/57</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-black/60">Position</span>
                <span className="text-sm font-bold text-black">P4</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-black/60">Battery</span>
                <span className="text-sm font-bold text-black">45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-black/60">Tires</span>
                <span className="text-sm font-bold text-black">62%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-black/60">Fuel</span>
                <span className="text-sm font-bold text-black">28kg</span>
              </div>
            </div>
          </div>
        </div>

        {/* Mid Section - Multi-Agentic Insights (Large Center) */}
        <div className="grid grid-cols-12 gap-4 mb-4">
          <div className="col-span-9 bg-white border border-black rounded-lg p-6">
            <h3 className="text-lg font-bold text-black mb-6 tracking-wide">MULTI-AGENTIC INSIGHTS</h3>
            <div className="grid grid-cols-3 gap-4">
              {strategies.map((strategy, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedStrategy(index)}
                  className={`border ${
                    selectedStrategy === index ? 'border-black bg-black/5' : 'border-black/40'
                  } rounded-lg p-4 cursor-pointer transition-all hover:border-black hover:bg-black/5`}
                >
                  <h4 className="text-sm font-bold text-black mb-3">{strategy.name}</h4>
                  <p className="text-4xl font-bold text-black mb-4">{strategy.probability}</p>
                  <p className="text-xs text-black/70 leading-relaxed">{strategy.explanation}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Agent Performance */}
          <div className="col-span-3 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">AGENT PERFORMANCE</h3>
            <div className="space-y-3">
              <div className="border-b border-black/20 pb-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-bold text-black">You</span>
                  <span className="text-xs text-black/60">P2</span>
                </div>
                <p className="text-xs text-black/60">65% optimal</p>
              </div>
              <div className="border-b border-black/20 pb-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-black">Pure AI</span>
                  <span className="text-xs text-black/60">P1</span>
                </div>
                <p className="text-xs text-black/60">98% optimal</p>
              </div>
              <div className="border-b border-black/20 pb-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-black">Verstappen Agent</span>
                  <span className="text-xs text-black/60">P3</span>
                </div>
                <p className="text-xs text-black/60">72% optimal</p>
              </div>
              <div className="pb-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-black">Hamilton Agent</span>
                  <span className="text-xs text-black/60">P4</span>
                </div>
                <p className="text-xs text-black/60">68% optimal</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section - 2 Boxes (Equal Width) */}
        <div className="grid grid-cols-12 gap-4">
          {/* Decision Log */}
          <div className="col-span-6 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">DECISION LOG</h3>
            <div className="space-y-2 max-h-[250px] overflow-y-auto">
              <div className="flex items-center justify-between border-b border-black/20 pb-2">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-black">Lap 15</span>
                    <span className="text-xs text-black/40">14:23:45</span>
                  </div>
                  <p className="text-xs text-black/60">Deploy aggressive overtake mode</p>
                </div>
                <span className="text-black ml-3">✓</span>
              </div>
              <div className="flex items-center justify-between border-b border-black/20 pb-2">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-black">Lap 12</span>
                    <span className="text-xs text-black/40">14:18:32</span>
                  </div>
                  <p className="text-xs text-black/60">Pit stop for soft compound tires</p>
                </div>
                <span className="text-black ml-3">✗</span>
              </div>
              <div className="flex items-center justify-between border-b border-black/20 pb-2">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-black">Lap 8</span>
                    <span className="text-xs text-black/40">14:12:18</span>
                  </div>
                  <p className="text-xs text-black/60">Maintain pace, conserve battery</p>
                </div>
                <span className="text-black ml-3">✓</span>
              </div>
              <div className="flex items-center justify-between border-b border-black/20 pb-2">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-black">Lap 5</span>
                    <span className="text-xs text-black/40">14:07:45</span>
                  </div>
                  <p className="text-xs text-black/60">Increase fuel mix to mode 3</p>
                </div>
                <span className="text-black ml-3">✓</span>
              </div>
              <div className="flex items-center justify-between pb-2">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-black">Lap 3</span>
                    <span className="text-xs text-black/40">14:04:12</span>
                  </div>
                  <p className="text-xs text-black/60">Deploy ERS on main straight</p>
                </div>
                <span className="text-black ml-3">✓</span>
              </div>
            </div>
          </div>

          {/* Graph */}
          <div className="col-span-6 bg-white border border-black rounded-lg p-4">
            <h3 className="text-sm font-bold text-black mb-4 tracking-wide">POSITION GRAPH</h3>
            <div className="h-[250px] flex items-end justify-between gap-2 border-b border-l border-black/20 pb-4 pl-4">
              {/* Placeholder graph bars */}
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15].map((lap) => (
                <div key={lap} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full bg-black/20 rounded-t" style={{ height: `${Math.random() * 100 + 50}px` }}>
                    <div className="w-full bg-black rounded-t" style={{ height: `${Math.random() * 60 + 20}%` }}></div>
                  </div>
                  <span className="text-[8px] text-black/40">{lap}</span>
                </div>
              ))}
            </div>
            <div className="mt-2 flex justify-between text-xs text-black/60">
              <span>Lap</span>
              <span>Position</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
