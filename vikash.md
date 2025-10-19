# DEV 3 (FRONTEND/UX) - YOUR MISSION

# FOLLOW CELESTIAL THEME FOR ALL FRONTEND UI/UX

You are building the USER INTERFACE for Strategy Gym 2026.

## YOUR TOOLS
- **Gemini CLI**: For UI copy, component text, design suggestions
- **Claude Code**: For React component implementation

## YOUR DELIVERABLES (By Hour)

### H0-H1: Next.js Setup
**Goal:** Three-panel layout with routing

**Step 1:** Initialize Next.js
```bash
cd web
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
npm install recharts
```

**Step 2:** Create `app/page.tsx` (main layout)
```typescript
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
```

**Step 3:** Create component stubs

`app/components/DiscoveryArena.tsx`:
```typescript
export default function DiscoveryArena() {
  return <div className="bg-gray-800 p-6 rounded-lg">Discovery Arena (TODO)</div>;
}
```

`app/components/PlaybookView.tsx`:
```typescript
export default function PlaybookView() {
  return <div className="bg-gray-800 p-6 rounded-lg">Playbook (TODO)</div>;
}
```

`app/components/BoxWall.tsx`:
```typescript
export default function BoxWall() {
  return <div className="bg-gray-800 p-6 rounded-lg">Box Wall (TODO)</div>;
}
```

**Checkpoint H1:** Three tabs working, can switch between views

---

### H1-H2: Discovery Arena Implementation
**Goal:** Run button + progress indicator

**Step 4:** Implement Discovery Arena

**USE GEMINI CLI FOR COPY:**
Prompt: "Generate engaging UI copy for a 'Run Simulation' button that starts 1000 F1 race simulations. Make it exciting and technical. Output 3 options."
```typescript
'use client';

import { useState } from 'react';

interface RunResult {
  run_id: string;
  scenarios_completed: number;
  elapsed_sec: number;
}

export default function DiscoveryArena() {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<RunResult | null>(null);

  const runSimulation = async () => {
    setRunning(true);
    setProgress(0);
    setResult(null);

    // Simulate progress (fake for now)
    const interval = setInterval(() => {
      setProgress(p => Math.min(p + 10, 90));
    }, 200);

    try {
      const res = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_scenarios: 1000, num_agents: 8, repeats: 1 })
      });

      clearInterval(interval);
      setProgress(100);

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      clearInterval(interval);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg">
      <h2 className="text-3xl font-bold mb-6">Discovery Arena</h2>

      <p className="text-gray-300 mb-8">
        Run 1000 simulated races with 8 competing energy deployment strategies.
        Watch as adversarial agents battle to discover optimal 2026 hybrid tactics.
      </p>

      <button
        onClick={runSimulation}
        disabled={running}
        className={`w-full py-4 text-xl font-bold rounded-lg transition ${
          running
            ? 'bg-gray-600 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
        }`}
      >
        {running ? `Running... ${progress}%` : 'Launch 1000 Races'}
      </button>

      {running && (
        <div className="mt-6">
          <div className="w-full bg-gray-700 rounded-full h-4">
            <div
              className="bg-blue-500 h-4 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {result && (
        <div className="mt-8 p-6 bg-gray-700 rounded-lg">
          <h3 className="text-xl font-bold mb-4">✓ Simulation Complete</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-3xl font-bold text-green-400">{result.scenarios_completed}</div>
              <div className="text-sm text-gray-400">Scenarios</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-400">{result.elapsed_sec.toFixed(2)}s</div>
              <div className="text-sm text-gray-400">Total Time</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-400">
                {(result.scenarios_completed / result.elapsed_sec).toFixed(0)}
              </div>
              <div className="text-sm text-gray-400">Scenarios/sec</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

**Checkpoint H2:** Can run simulation, see progress bar, see results

---

### H2-H3: Playbook Cards
**Goal:** Display rules with confidence/uplift

**Step 5:** Implement Playbook View

**USE GEMINI CLI FOR RULE TEXT:**
Prompt: "Given this playbook rule JSON: {rule: 'Low Battery Conservation', condition: 'battery_soc < 30 and lap > 40', confidence: 0.85, uplift_win_pct: 18}, write a concise 1-sentence rationale that explains why this strategy works. Make it technical but accessible."
```typescript
'use client';

import { useState, useEffect } from 'react';

interface Rule {
  rule: string;
  condition: string;
  action: {
    deploy_straight: number;
    deploy_corner: number;
    harvest: number;
  };
  confidence: number;
  uplift_win_pct: number;
  rationale: string;
}

interface Playbook {
  rules: Rule[];
  generated_at: string;
  num_simulations: number;
}

export default function PlaybookView() {
  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [loading, setLoading] = useState(false);

  const loadPlaybook = async () => {
    setLoading(true);
    try {
      // First trigger analysis
      await fetch('http://localhost:8000/analyze', { method: 'POST' });

      // Then fetch playbook
      const res = await fetch('http://localhost:8000/playbook');
      const data = await res.json();
      setPlaybook(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg">
      <h2 className="text-3xl font-bold mb-6">Strategic Playbook</h2>

      {!playbook && (
        <button
          onClick={loadPlaybook}
          disabled={loading}
          className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg"
        >
          {loading ? 'Analyzing...' : 'Generate Playbook'}
        </button>
      )}

      {playbook && (
        <>
          <div className="mb-6 text-gray-400">
            {playbook.rules.length} rules discovered from {playbook.num_simulations.toLocaleString()} simulations
          </div>

          <div className="space-y-4">
            {playbook.rules.map((rule, i) => (
              <div key={i} className="bg-gray-700 p-6 rounded-lg border-l-4 border-blue-500">
                <h3 className="text-xl font-bold mb-2">{rule.rule}</h3>

                <div className="text-sm font-mono text-gray-400 mb-3">
                  {rule.condition}
                </div>

                <div className="flex gap-4 mb-3">
                  <div className="bg-green-900/30 px-3 py-1 rounded">
                    <span className="text-green-400 font-bold">+{rule.uplift_win_pct.toFixed(1)}%</span>
                    {' '}win rate
                  </div>
                  <div className="bg-yellow-900/30 px-3 py-1 rounded">
                    <span className="text-yellow-400 font-bold">{(rule.confidence * 100).toFixed(0)}%</span>
                    {' '}confidence
                  </div>
                </div>

                <p className="text-gray-300 text-sm">{rule.rationale}</p>

                <details className="mt-3">
                  <summary className="cursor-pointer text-sm text-gray-400">Show Actions</summary>
                  <div className="mt-2 grid grid-cols-3 gap-2 text-sm">
                    <div>Straight: {rule.action.deploy_straight}%</div>
                    <div>Corner: {rule.action.deploy_corner}%</div>
                    <div>Harvest: {rule.action.harvest}%</div>
                  </div>
                </details>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
```

**Checkpoint H3:** Playbook loads and displays rules with styling

---

### H6-H7: Box Wall Advisor
**Goal:** Interactive sliders + real-time advice

**Step 6:** Implement Box Wall
```typescript
'use client';

import { useState } from 'react';

interface Recommendation {
  rule: string;
  action: any;
  confidence: number;
  rationale: string;
}

export default function BoxWall() {
  const [state, setState] = useState({
    lap: 30,
    battery_soc: 50,
    position: 3,
    rain: false
  });

  const [advice, setAdvice] = useState<{
    recommendations: Recommendation[];
    latency_ms: number;
  } | null>(null);

  const [loading, setLoading] = useState(false);

  const getAdvice = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state)
      });
      const data = await res.json();
      setAdvice(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg">
      <h2 className="text-3xl font-bold mb-6">Box Wall Advisor</h2>

      <p className="text-gray-300 mb-8">
        Simulate real-time race conditions and get instant strategic recommendations.
      </p>

      <div className="grid grid-cols-2 gap-8 mb-8">
        <div>
          <label className="block mb-2">
            Lap: <span className="font-bold text-blue-400">{state.lap}</span> / 57
          </label>
          <input
            type="range"
            min="1"
            max="57"
            value={state.lap}
            onChange={(e) => setState({ ...state, lap: parseInt(e.target.value) })}
            className="w-full"
          />
        </div>

        <div>
          <label className="block mb-2">
            Battery SOC: <span className="font-bold text-green-400">{state.battery_soc}%</span>
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={state.battery_soc}
            onChange={(e) => setState({ ...state, battery_soc: parseInt(e.target.value) })}
            className="w-full"
          />
        </div>

        <div>
          <label className="block mb-2">
            Position: <span className="font-bold text-yellow-400">P{state.position}</span>
          </label>
          <input
            type="range"
            min="1"
            max="20"
            value={state.position}
            onChange={(e) => setState({ ...state, position: parseInt(e.target.value) })}
            className="w-full"
          />
        </div>

        <div>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={state.rain}
              onChange={(e) => setState({ ...state, rain: e.target.checked })}
            />
            Rain Forecasted
          </label>
        </div>
      </div>

      <button
        onClick={getAdvice}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 py-4 text-xl font-bold rounded-lg mb-6"
      >
        {loading ? 'Analyzing...' : 'Get Recommendation'}
      </button>

      {advice && (
        <div className="bg-gray-700 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">
            {advice.recommendations[0].rule}
          </h3>

          <p className="text-gray-300 mb-4">
            {advice.recommendations[0].rationale}
          </p>

          <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
            <div className="bg-gray-800 p-3 rounded text-center">
              <div className="text-2xl font-bold">{advice.recommendations[0].action.deploy_straight}%</div>
              <div className="text-gray-400">Straight Deploy</div>
            </div>
            <div className="bg-gray-800 p-3 rounded text-center">
              <div className="text-2xl font-bold">{advice.recommendations[0].action.deploy_corner}%</div>
              <div className="text-gray-400">Corner Deploy</div>
            </div>
            <div className="bg-gray-800 p-3 rounded text-center">
              <div className="text-2xl font-bold">{advice.recommendations[0].action.harvest}%</div>
              <div className="text-gray-400">Harvest</div>
            </div>
          </div>

          <div className="text-xs text-gray-400 text-right">
            Latency: {advice.latency_ms.toFixed(1)}ms
          </div>
        </div>
      )}
    </div>
  );
}
```

**Checkpoint H7:** Sliders work, recommendations appear <1.5s

---

### H7-H8: Polish & Dark Theme
**Goal:** Professional look, animations

**Step 7:** Add global styles

Update `app/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-900 text-white;
  }

  input[type="range"] {
    @apply h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer;
  }

  input[type="range"]::-webkit-slider-thumb {
    @apply appearance-none w-4 h-4 bg-blue-500 rounded-full cursor-pointer;
  }

  input[type="range"]::-moz-range-thumb {
    @apply w-4 h-4 bg-blue-500 rounded-full cursor-pointer border-0;
  }
}

@layer utilities {
  .animate-pulse-slow {
    animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
}
```

**Step 8:** Add loading states and transitions
```typescript
// Add to components
className="transition-all duration-300 ease-in-out"
```

**Checkpoint H8:** UI looks polished, smooth animations

---

## TESTING CHECKLIST
```bash
cd web
npm run dev

# Test:
# 1. Discovery Arena button works
# 2. Playbook loads after analysis
# 3. Box Wall sliders update state
# 4. All tabs switch smoothly
# 5. Dark theme looks good
```

---

## FILES YOU WILL CREATE

- `app/page.tsx` (main layout)
- `app/components/DiscoveryArena.tsx`
- `app/components/PlaybookView.tsx`
- `app/components/BoxWall.tsx`
- `app/globals.css` (styling)

---

## SUCCESS CRITERIA

By H8 you should have:
✅ Three panels working
✅ Run simulation with progress bar
✅ Playbook cards with confidence/uplift
✅ Box Wall with interactive sliders
✅ Clean dark theme
✅ Smooth animations

GO BUILD IT!