'use client';

import {
  Area,
  AreaChart,
  CartesianGrid,
  Label,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import type { LapBatteryPoint, LapDeltaPoint } from '../../types';

interface LapComparisonProps {
  batteryData: LapBatteryPoint[];
  deltaData: LapDeltaPoint[];
}

const tooltipStyle = {
  backgroundColor: '#141414',
  border: '1px solid #333333',
  borderRadius: '12px',
  color: '#f5f5f5',
};

export default function LapComparison({ batteryData, deltaData }: LapComparisonProps) {
  return (
    <div className="grid gap-6 rounded-3xl border border-[#1f1f1f] bg-[#0B0B0B] p-6 shadow-[0_18px_60px_rgba(0,0,0,0.45)] lg:grid-cols-2">
      <div className="flex flex-col gap-4">
        <header className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.32em] text-[#777]">
          <span>Battery SOC (%)</span>
          <span>Agent overlay</span>
        </header>
        <div className="h-64 w-full">
          <ResponsiveContainer>
            <LineChart data={batteryData} margin={{ top: 20, right: 20, left: -10, bottom: 10 }}>
              <defs>
                <linearGradient id="batteryOne" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#DC0000" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#DC0000" stopOpacity={0.2} />
                </linearGradient>
                <linearGradient id="batteryTwo" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FFD700" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#FFD700" stopOpacity={0.2} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1a1a1a" strokeDasharray="3 3" />
              <XAxis dataKey="lap" stroke="#666" tick={{ fill: '#888888', fontSize: 12 }}>
                <Label value="Lap" offset={-8} position="insideBottom" style={{ fill: '#666666' }} />
              </XAxis>
              <YAxis stroke="#666" tick={{ fill: '#888888', fontSize: 12 }} />
              <Tooltip cursor={{ stroke: '#333', strokeWidth: 1 }} contentStyle={tooltipStyle} />
              <Line
                type="monotone"
                dataKey="agent_one"
                stroke="#DC0000"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: '#DC0000', stroke: '#FFF', strokeWidth: 2 }}
              />
              <Line
                type="monotone"
                dataKey="agent_two"
                stroke="#FFD700"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: '#FFD700', stroke: '#FFF', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        <header className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.32em] text-[#777]">
          <span>Lap Time Delta (Agent 1 - Agent 2)</span>
          <span>Negative favours Electric Blitzer</span>
        </header>
        <div className="h-64 w-full">
          <ResponsiveContainer>
            <AreaChart data={deltaData} margin={{ top: 20, right: 20, left: -10, bottom: 10 }}>
              <defs>
                <linearGradient id="deltaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF4444" stopOpacity={0.6} />
                  <stop offset="95%" stopColor="#FF4444" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1a1a1a" strokeDasharray="3 3" />
              <XAxis dataKey="lap" stroke="#666" tick={{ fill: '#888888', fontSize: 12 }}>
                <Label value="Lap" offset={-8} position="insideBottom" style={{ fill: '#666666' }} />
              </XAxis>
              <YAxis
                stroke="#666"
                tick={{ fill: '#888888', fontSize: 12 }}
                domain={['dataMin - 0.2', 'dataMax + 0.2']}
                tickFormatter={(value) => `${value.toFixed(2)}s`}
              />
              <Tooltip cursor={{ stroke: '#333', strokeWidth: 1 }} contentStyle={tooltipStyle} />
              <Area
                type="monotone"
                dataKey="delta"
                stroke="#FF4444"
                strokeWidth={2.2}
                fill="url(#deltaGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
