'use client';

import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Line,
  LineChart,
} from 'recharts';

interface DriverMetric {
  label: string;
  value: number;
  color: string;
}

interface DriverInfo {
  position: number;
  name: string;
  surname: string;
  team: string;
  lapTime: string;
  lapGap: string;
  badge: string;
  metrics: DriverMetric[];
  accent: string;
  gradient: string;
}

const leftDriver: DriverInfo = {
  position: 1,
  name: 'Charles',
  surname: 'Leclerc',
  team: 'Ferrari',
  lapTime: '1:23.456',
  lapGap: '-0.321s',
  badge: 'Scuderia Ferrari',
  accent: '#f44336',
  gradient: 'from-[#f44336] to-[#c62828]',
  metrics: [
    { label: 'Full Throttle', value: 81, color: '#ff5a47' },
    { label: 'Heavy Braking', value: 5, color: '#ff974d' },
    { label: 'Cornering', value: 14, color: '#ffcd4d' },
  ],
};

const rightDriver: DriverInfo = {
  position: 2,
  name: 'Carlos',
  surname: 'Sainz',
  team: 'Ferrari',
  lapTime: '1:23.777',
  lapGap: '+0.321s',
  badge: 'Scuderia Ferrari',
  accent: '#ffd600',
  gradient: 'from-[#ffe070] to-[#ffb300]',
  metrics: [
    { label: 'Full Throttle', value: 81, color: '#ffd84f' },
    { label: 'Heavy Braking', value: 5, color: '#ffc54f' },
    { label: 'Cornering', value: 14, color: '#ffb84f' },
  ],
};

const speedGraphData = [
  { turn: '1', speed: 302 },
  { turn: '2', speed: 298 },
  { turn: '3', speed: 310 },
  { turn: '4', speed: 320 },
  { turn: '5', speed: 301 },
  { turn: '6', speed: 285 },
  { turn: '7', speed: 292 },
  { turn: '8', speed: 304 },
  { turn: '9', speed: 315 },
  { turn: '10', speed: 323 },
  { turn: '11', speed: 331 },
];

const deltaGraphData = [
  { turn: '1', delta: -0.123 },
  { turn: '2', delta: -0.103 },
  { turn: '3', delta: -0.004 },
  { turn: '4', delta: -0.021 },
  { turn: '5', delta: 0.167 },
  { turn: '6', delta: 0.011 },
  { turn: '7', delta: -0.111 },
  { turn: '8', delta: -0.156 },
  { turn: '9', delta: 0.321 },
  { turn: '10', delta: -0.125 },
  { turn: '11', delta: -0.089 },
];

function DriverPanel({ driver, align = 'left' }: { driver: DriverInfo; align?: 'left' | 'right' }) {
  const justify = align === 'left' ? 'items-start text-left' : 'items-end text-right';
  const badgeAlign = align === 'left' ? 'left-0' : 'right-0';

  return (
    <article
      className={`relative flex h-full flex-col gap-4 rounded-3xl border border-[#1b1d2d] bg-[#141725] p-6 shadow-[0_18px_45px_rgba(0,0,0,0.45)] ${justify}`}
    >
      <div
        className={`absolute top-0 ${badgeAlign} h-full w-[6px] rounded-full bg-gradient-to-b ${driver.gradient}`}
        aria-hidden
      />
      <div className="flex flex-col gap-1">
        <span className="text-xs font-semibold uppercase tracking-[0.28em] text-[#8c90a9]">
          Position
        </span>
        <div className="flex items-baseline gap-3">
          <span className="text-5xl font-black text-white">P{driver.position}</span>
          <span className="text-sm uppercase tracking-[0.32em] text-[#6f738b]">{driver.team}</span>
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-xs uppercase tracking-[0.28em] text-[#8c90a9]">Driver</span>
        <div className="text-3xl font-black uppercase text-white">
          {driver.name}{' '}
          <span className="text-transparent bg-gradient-to-r from-white to-[#dcdff1] bg-clip-text">
            {driver.surname}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-2 text-sm text-[#a4a8c5]">
        <div className="flex items-center gap-3 font-mono text-lg text-white">
          <span>Lap Time</span>
          <span className="text-[#ffd84f]">{driver.lapTime}</span>
        </div>
        <div className="flex items-center gap-3 font-mono text-lg text-white">
          <span>{driver.position === 1 ? 'Gap' : 'Gap To Leader'}</span>
          <span className="text-[#64ffda]">{driver.lapGap}</span>
        </div>
      </div>

      <div className="mt-1 flex flex-col gap-3">
        {driver.metrics.map((metric) => (
          <div key={metric.label} className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-[#7c8098]">
              <span>{metric.label}</span>
              <span className="font-mono text-sm text-white">{metric.value}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-[#1f2235]">
              <div
                className="h-full rounded-full shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                style={{
                  width: `${metric.value}%`,
                  background: `linear-gradient(90deg, ${metric.color}88, ${metric.color})`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function TrackMap() {
  return (
    <div className="flex h-full flex-col gap-4 rounded-3xl border border-[#1b1d2d] bg-[#151827] p-6 shadow-[0_18px_45px_rgba(0,0,0,0.45)]">
      <header className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-[#7c8098]">
        <span>Monza Circuit</span>
        <span>Low → Medium → High Speed</span>
      </header>
      <div className="flex flex-1 items-center justify-center">
        <svg className="h-56 w-full" viewBox="0 0 480 240" role="img" aria-label="Monza circuit">
          <defs>
            <linearGradient id="trackGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ff5a47" />
              <stop offset="50%" stopColor="#ffd84f" />
              <stop offset="100%" stopColor="#64ffda" />
            </linearGradient>
            <filter id="trackGlow" x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="6" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <path
            d="M40 180 C80 60, 140 40, 200 60 C270 90, 280 190, 360 180 C420 170, 430 120, 410 90 C380 40, 260 30, 210 40 C140 55, 120 110, 100 140 C80 170, 60 190, 40 180 Z"
            fill="none"
            stroke="url(#trackGradient)"
            strokeWidth={12}
            strokeLinecap="round"
            filter="url(#trackGlow)"
          />
          <g fill="#1f2235" stroke="#2f334b" strokeWidth={1}>
            <circle cx="40" cy="180" r="18" />
            <circle cx="410" cy="90" r="14" />
            <circle cx="210" cy="40" r="16" />
            <circle cx="360" cy="180" r="12" />
          </g>
          <g fill="#a4a8c5" fontSize="12" fontFamily="Inter, sans-serif">
            <text x="26" y="182">1</text>
            <text x="398" y="92">6</text>
            <text x="198" y="42">9</text>
            <text x="348" y="182">11</text>
          </g>
        </svg>
      </div>
      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="rounded-2xl border border-[#1f2235] bg-[#191c2d] p-3">
          <div className="text-[10px] uppercase tracking-[0.3em] text-[#7c8098]">Low Speed</div>
          <div className="mt-1 text-lg font-semibold text-white">Turns 1-2</div>
        </div>
        <div className="rounded-2xl border border-[#1f2235] bg-[#191c2d] p-3">
          <div className="text-[10px] uppercase tracking-[0.3em] text-[#7c8098]">Medium Speed</div>
          <div className="mt-1 text-lg font-semibold text-white">Turns 6-8</div>
        </div>
        <div className="rounded-2xl border border-[#1f2235] bg-[#191c2d] p-3">
          <div className="text-[10px] uppercase tracking-[0.3em] text-[#7c8098]">High Speed</div>
          <div className="mt-1 text-lg font-semibold text-white">Turns 10-11</div>
        </div>
      </div>
    </div>
  );
}

function SpeedChart() {
  return (
    <div className="rounded-3xl border border-[#1b1d2d] bg-[#151827] p-6 shadow-[0_18px_45px_rgba(0,0,0,0.45)]">
      <header className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-[#7c8098]">
        <span>Speed Profile</span>
        <span>304 km/h peak</span>
      </header>
      <div className="mt-4 h-60 w-full">
        <ResponsiveContainer>
          <LineChart data={speedGraphData}>
            <defs>
              <linearGradient id="speedLine" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ff5a47" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#ffb84f" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1f2235" strokeDasharray="3 3" />
            <XAxis
              dataKey="turn"
              stroke="#5e6277"
              tick={{ fill: '#7c8098', fontSize: 12 }}
              label={{ value: 'Turn', position: 'insideBottom', offset: -8, fill: '#7c8098' }}
            />
            <YAxis
              stroke="#5e6277"
              tick={{ fill: '#7c8098', fontSize: 12 }}
              domain={[260, 340]}
              label={{ value: 'Speed (km/h)', angle: -90, position: 'insideLeft', fill: '#7c8098' }}
            />
            <Tooltip
              cursor={{ stroke: '#2f334b', strokeWidth: 1 }}
              contentStyle={{
                background: '#1b1d2d',
                border: '1px solid #2f334b',
                borderRadius: '10px',
                color: '#fff',
              }}
            />
            <ReferenceArea x1="1" x2="3" fill="#31203a" fillOpacity={0.35} />
            <ReferenceArea x1="6" x2="8" fill="#1f2f3a" fillOpacity={0.35} />
            <ReferenceArea x1="9" x2="11" fill="#1f3a2f" fillOpacity={0.35} />
            <Line
              type="monotone"
              dataKey="speed"
              stroke="url(#speedLine)"
              strokeWidth={3}
              dot={{ r: 0 }}
              activeDot={{ r: 6, fill: '#ffd84f', stroke: '#0b0d16', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <footer className="mt-4 flex justify-between text-xs font-mono text-[#ff5a47]">
        <span>Faster</span>
        <span className="text-[#64ffda]">Slower</span>
      </footer>
    </div>
  );
}

function DeltaChart() {
  return (
    <div className="rounded-3xl border border-[#1b1d2d] bg-[#151827] p-6 shadow-[0_18px_45px_rgba(0,0,0,0.45)]">
      <header className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-[#7c8098]">
        <span>Lap Time Delta</span>
        <span>Leclerc vs Sainz</span>
      </header>
      <div className="mt-4 h-48 w-full">
        <ResponsiveContainer>
          <AreaChart data={deltaGraphData}>
            <defs>
              <linearGradient id="deltaArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ff5a47" stopOpacity={0.75} />
                <stop offset="100%" stopColor="#ff5a47" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1f2235" strokeDasharray="3 3" />
            <XAxis
              dataKey="turn"
              stroke="#5e6277"
              tick={{ fill: '#7c8098', fontSize: 12 }}
              label={{ value: 'Turn', position: 'insideBottom', offset: -8, fill: '#7c8098' }}
            />
            <YAxis
              stroke="#5e6277"
              tick={{ fill: '#7c8098', fontSize: 12 }}
              domain={[-0.2, 0.2]}
              tickFormatter={(value) => `${value.toFixed(3)}s`}
            />
            <Tooltip
              cursor={{ stroke: '#2f334b', strokeWidth: 1 }}
              contentStyle={{
                background: '#1b1d2d',
                border: '1px solid #2f334b',
                borderRadius: '10px',
                color: '#fff',
              }}
            />
            <Area
              type="monotone"
              dataKey="delta"
              stroke="#ff8566"
              fill="url(#deltaArea)"
              strokeWidth={2}
              activeDot={{ r: 6, fill: '#ffd84f', stroke: '#0b0d16', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen bg-[#080a13] text-white">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-4 py-10 md:px-6 lg:px-10">
        <header className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-[#1b1d2d] bg-[#121422] px-6 py-4 uppercase shadow-[0_18px_45px_rgba(0,0,0,0.45)]">
          <div className="flex items-center gap-3 text-sm tracking-[0.32em] text-[#c5c8e2]">
            <span className="rounded-full border border-[#ff5a47] px-3 py-1 text-[#ff5a47]">F1</span>
            <span>Monza · Qualifying Analysis</span>
          </div>
          <div className="flex items-center gap-2 text-xs tracking-[0.24em] text-[#9ba0bd]">
            <span>Powered by</span>
            <span className="rounded-full bg-[#ffb84f]/10 px-3 py-1 text-[#ffb84f]">AWS</span>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)_320px]">
          <DriverPanel driver={leftDriver} align="left" />
          <TrackMap />
          <DriverPanel driver={rightDriver} align="right" />
        </section>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)]">
          <SpeedChart />
          <DeltaChart />
        </section>
      </div>
    </main>
  );
}
