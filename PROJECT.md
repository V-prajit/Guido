PROJECT_REFERENCE.md
markdown# STRATEGY GYM 2026 - AI REFERENCE

**Quick context file for LLMs working on this project**

---

## WHAT WE'RE BUILDING

A multi-agent simulation system that discovers optimal F1 energy deployment strategies for 2026 regulations through adversarial competition and AI-powered pattern synthesis.

**The Real Problem:**
- 2026 F1 regulations triple electric power (120kW → 350kW)
- Creates 50/50 ICE/Electric power split
- NO historical race data exists yet
- Teams must discover strategies through simulation
- Challenge: Interpreting patterns from thousands of simulation runs

**Our Solution:**
- Run 1000+ races with 8 competing energy deployment strategies
- Use Gemini to synthesize winning patterns into actionable playbook
- Provide real-time strategic recommendations (<1.5s)
- Show how real F1 teams will prepare for 2026

---

## SYSTEM ARCHITECTURE
```
┌─────────────────────────────────────┐
│     FRONTEND (Next.js + React)      │
│  3 Panels: Arena, Playbook, Advisor │
└──────────────┬──────────────────────┘
               │ HTTP/JSON
┌──────────────▼──────────────────────┐
│     BACKEND API (FastAPI)           │
│  /run /analyze /playbook /recommend │
└──┬────────┬─────────┬───────────┬──┘
   │        │         │           │
   ▼        ▼         ▼           ▼
Runner   Gemini   Analysis   Recommend
   │        │         │           │
   ▼        │         │           │
┌──────────────────────────────────┐ │
│ SIMULATION ENGINE (NumPy+Numba)  │ │
│  8 Agents × 1000 Scenarios       │ │
└──────────────────────────────────┘ │
               │                      │
               ▼                      │
         CSV Results ─────────────────┘
               │
               ▼
        Playbook JSON
```

---

## TEAM ROLES & RESPONSIBILITIES

### R1 (Sim/Perf)
**Owns:** Core simulation engine, 8 agent strategies, performance optimization

**Delivers:**
- `sim/engine.py`: simulate_race(scenario, agents) → DataFrame
- `sim/agents.py`: 8 agent classes with distinct strategies
- `sim/scenarios.py`: generate_scenarios(n) → list of scenario dicts
- Performance: 1000 races in <5 seconds

**Key Constraint:** Must be parallelizable (pure Python, picklable returns)

### R2 (Backend/Orchestrator)
**Owns:** FastAPI server, multiprocessing, all API endpoints, integration

**Delivers:**
- `api/main.py`: 7 endpoints (run, analyze, playbook, recommend, validate, perf, health)
- `api/runner.py`: Multiprocessing orchestration
- `api/analysis.py`: Result aggregation
- `api/recommend.py`: Fast recommendation engine (<1.5s)

**Key Constraint:** Must handle Gemini failures gracefully (fallbacks)

### R3 (Frontend/UX)
**Owns:** User interface, real-time updates, data visualization

**Delivers:**
- Next.js app with 3 panels
- Discovery Arena: Run button, progress bar, results
- Playbook View: Rule cards with confidence/uplift
- Box Wall: Interactive sliders for recommendations

**Key Constraint:** Must work offline (demo mode with static JSON)

### R4 (AI/Insights/Narrative)
**Owns:** Gemini integration, playbook synthesis, copy, narrative

**Delivers:**
- `api/gemini.py`: synthesize_playbook(stats, df) → JSON
- System prompts for Gemini
- Demo script and presentation narrative
- Fallback logic if Gemini fails

**Key Constraint:** Output must match playbook schema exactly

---

## KEY DATA FLOWS

### Flow 1: Run Simulation
```
User clicks "Run 1000 Races"
  → POST /run {num_scenarios: 1000}
  → Backend spawns multiprocessing pool
  → Each worker: generate scenario → simulate_race()
  → Collect all results into CSV
  → Return {run_id, csv_path, elapsed_sec}
  → Frontend shows scenarios/sec
```

### Flow 2: Generate Playbook
```
User clicks "Generate Playbook"
  → POST /analyze
  → Load latest CSV
  → Aggregate stats (wins, positions per agent)
  → Calculate situational win rates (battery levels, lap phases)
  → Call Gemini with stats + context
  → Gemini returns 5-7 strategic rules as JSON
  → Save to playbook.json
  → Frontend displays rule cards
```

### Flow 3: Get Recommendation
```
User adjusts sliders (lap 30, battery 45%, P3)
  → POST /recommend {lap, battery_soc, position}
  → Load cached playbook
  → Evaluate each rule's condition against state
  → Return matching recommendations
  → Frontend displays action + rationale
  → Must complete in <1.5 seconds
```

---

## PHYSICS MODEL (SIMPLIFIED)

**NOT realistic F1 physics - optimized for strategy discovery.**

### Agent Decisions (per lap)
```
deploy_straight: 0-100%  (electric power on straights)
deploy_corner: 0-100%    (electric power on corner exits)
harvest: 0-100%          (energy recovery intensity)
use_boost: boolean       (manual override, 2 per race)
```

### Lap Time Formula
```
base_time = 90.0 seconds
- (deploy_straight × 0.003)  [max -0.3s]
- (deploy_corner × 0.002)    [max -0.2s]
+ (harvest × 0.0015)         [max +0.15s penalty]
+ battery_penalty if SOC < 20%
+ 2.0s if rain
```

### Battery Dynamics
```
drain = (deploy_straight × 0.02) + (deploy_corner × 0.015)
charge = harvest × 0.025
new_soc = clamp(current_soc - drain + charge, 0, 100)
```

**Why This Works:**
- Captures strategic tradeoff: deploy vs. harvest
- Fast enough to run 1000 races in seconds
- Complex enough that different strategies win different scenarios

---

## API CONTRACTS

### POST /run
```
Request:  {num_scenarios: 1000, num_agents: 8}
Response: {run_id: "abc123", csv_path: "data/runs_abc123.csv", elapsed_sec: 8.2}
```

### POST /analyze
```
Request:  {}
Response: {stats: {...}, playbook_preview: {num_rules: 6}}
Side Effect: Saves playbook.json
```

### GET /playbook
```
Response: {
  rules: [{
    rule: "Low Battery Conservation",
    condition: "battery_soc < 30 and lap > 40",
    action: {deploy_straight: 30, deploy_corner: 30, harvest: 80},
    confidence: 0.85,
    uplift_win_pct: 18.2,
    rationale: "Heavy harvesting critical when battery low in late race"
  }],
  generated_at: "2025-10-18T12:34:56",
  num_simulations: 1000
}
```

### POST /recommend
```
Request:  {lap: 30, battery_soc: 45, position: 3, rain: false}
Response: {recommendations: [{rule, action, rationale}], latency_ms: 45}
Requirement: P95 latency < 1500ms
```

### POST /validate
```
Request:  {}
Response: {adaptive_wins: 13, adaptive_win_rate: 65%, median_baseline_rate: 40%, passed: true}
Success: Adaptive > median baseline on 20 unseen scenarios
```

---

## INTEGRATION POINTS

### R1 → R2
**Interface:** `simulate_race(scenario: dict, agents: list) → pd.DataFrame`

**Contract:**
- R1 provides pure function, no side effects
- Returns DataFrame with columns: agent, lap, battery_soc, lap_time, final_position, won
- Must be picklable for multiprocessing

### R2 → R4
**Interface:** `synthesize_playbook(stats: dict, df: pd.DataFrame) → dict`

**Contract:**
- R2 passes aggregated stats + full simulation DataFrame
- R4 returns JSON matching playbook schema
- R4 provides fallback_playbook() if Gemini fails

### R2 → R3
**Interface:** HTTP REST API on localhost:8000

**Contract:**
- All responses are JSON
- CORS enabled for localhost:3000
- Error codes: 200 (success), 404 (not found), 500 (server error)

### R1 → R4
**Interface:** AdaptiveAI agent reads playbook JSON

**Contract:**
- R4's playbook has valid Python conditions (e.g., "battery_soc < 30 and lap > 40")
- R1's AdaptiveAI evaluates conditions with restricted eval()
- Actions must have deploy_straight, deploy_corner, harvest as 0-100 values

---

## EIGHT AGENT STRATEGIES

1. **Electric_Blitz**: Deploy all battery early, fast start, weak finish
2. **Energy_Saver**: Conservative early, strong finish, ramps up deployment
3. **Balanced_Hybrid**: Steady 60/50/50 throughout race
4. **Corner_Specialist**: Saves electric for corner exits, technical tracks
5. **Straight_Dominator**: Max speed on straights, conserves in corners
6. **Late_Charger**: Harvests heavily early, attacks late race
7. **Overtake_Hunter**: Saves battery for overtaking opportunities
8. **Adaptive_AI**: Reads playbook and follows discovered rules (implemented H5-H6)

**Goal:** Each strategy must produce measurably different results across scenarios.

---

## GEMINI PLAYBOOK SYNTHESIS

### What Gemini Does
- Receives: Aggregated stats (wins per agent) + situational analysis (battery bins, lap phases)
- Analyzes: Which conditions correlate with wins
- Outputs: 5-7 strategic rules as strict JSON

### Playbook Rule Schema
```json
{
  "rule": "Short descriptive name",
  "condition": "battery_soc < 30 and lap > 40",
  "action": {
    "deploy_straight": 30,
    "deploy_corner": 30,
    "harvest": 80
  },
  "confidence": 0.85,
  "uplift_win_pct": 18.2,
  "rationale": "One sentence why this works",
  "caveats": "Optional: when not to use"
}
```

### Critical Requirements
- Output ONLY valid JSON (no markdown, no explanation)
- Conditions must be valid Python expressions
- Actions must be 0-100 values
- Rationale must be <200 characters
- Focus on actionable patterns, not physics explanations

### Fallback Strategy
If Gemini fails (rate limit, bad JSON, etc.):
- Use simple rule mining from best-performing agent
- Extract threshold-based rules (e.g., "if battery < 30, harvest 80%")
- Still matches playbook schema
- Mark as {fallback: true} in output

---

## SUCCESS METRICS

### Performance Targets
- **Simulation Speed:** 1000 races in <5 seconds (>200 races/sec)
- **Recommendation Latency:** P95 <1.5 seconds
- **Adaptive Win Rate:** >60% on validation (20 unseen scenarios)
- **Playbook Quality:** 5-7 rules with avg confidence >0.7

### Demo Requirements
**Must Have:**
- ✅ Run 1000 sims and show elapsed time
- ✅ Generate playbook with confidence/uplift scores
- ✅ Validate adaptive beats baseline
- ✅ Real-time recommendations working
- ✅ All 3 UI panels functional

**Nice to Have:**
- Animated progress bars
- Live scenarios/sec counter
- Ablation study results
- Performance visualization

---

## COMPETITION ALIGNMENT

### Northmark Track (HPC + F1)
**Why We Win:**
- Clear parallel compute demonstration (multiprocessing, all cores)
- Real F1 problem (2026 regulations, teams face this now)
- Visible compute→decisions pipeline
- Shows scaling advantage (more sims = better patterns)

### MLH Best Use of Gemini
**Why We Win:**
- Unique use case (strategic synthesis, not chatbot)
- Domain reasoning at scale (analyzing 1000 races)
- Pattern discovery from numerical data
- Strict JSON schema enforcement
- Handles edge cases (fallback if fails)

### Williams Validation
**Why It Matters:**
- Spoke with their Chief Racing Engineer
- This IS how teams prepare for regulation changes
- Simulation-driven strategy discovery is standard practice
- We're showing the future workflow

---

## FILE ORGANIZATION
```
strategy-gym/
├── sim/              # R1: Engine, agents, scenarios
├── api/              # R2: FastAPI, runner, endpoints
├── web/              # R3: Next.js UI components
├── data/             # Generated: CSVs, playbook JSON
├── scripts/          # Utilities: benchmark, validate
├── prompts/          # Shared: specs, schemas, system prompts
└── docs/             # R4: Demo script, slides
```

---

## COMMON INTEGRATION ISSUES

### Multiprocessing Imports
**Problem:** Pool workers can't find modules  
**Fix:** Import inside worker functions, not at top level

### Gemini JSON Parsing
**Problem:** Response wrapped in markdown backticks  
**Fix:** Strip ```json and ``` before parsing

### CORS Errors
**Problem:** Frontend can't reach backend  
**Fix:** Add CORSMiddleware to FastAPI allowing localhost:3000

### Slow Recommendations
**Problem:** Loading playbook from disk each time  
**Fix:** Cache playbook in memory, refresh every 60s

### Condition Eval Security
**Problem:** eval() can execute arbitrary code  
**Fix:** Use eval(condition, {"__builtins__": {}}, safe_context)

---

## DEMO FLOW (4 MINUTES)

1. **Hook (30s):** "2026 regulations, no data exists, teams need simulation"
2. **Arena (60s):** Click "Run 1000 Races", show scenarios/sec, results
3. **Playbook (60s):** Click "Generate", show 6 rules with confidence/uplift
4. **Validation (30s):** "Adaptive wins 65% vs 40% baseline"
5. **Advisor (45s):** Adjust sliders, get recommendation in <1.5s
6. **Numbers (15s):** "125 scenarios/sec, Gemini synthesis, sub-2s advice"

---

## CRITICAL DEPENDENCIES

**R2 depends on R1:** Backend needs working simulate_race() function  
**R4 depends on R2:** Gemini integration called by backend /analyze  
**R3 depends on R2:** Frontend needs API endpoints live  
**Everyone depends on prompts/:** Shared specs in this folder

**Can work without:**
- Real Gemini (fallback exists)
- All 8 agents (start with 4)
- Validation (nice to have)
- Perfect UI polish

**Cannot work without:**
- R1's simulation engine
- R2's /run and /recommend endpoints
- R3's basic UI to trigger actions

---

## QUICK COMMANDS
```bash
# Backend
uvicorn api.main:app --reload

# Frontend
cd web && npm run dev

# Test full flow
python scripts/benchmark.py
curl -X POST http://localhost:8000/analyze
curl http://localhost:8000/playbook

# Validate
python scripts/validate.py
```

---

## KEY DESIGN DECISIONS

**Why simplified physics?**  
Focus on strategy, not realism. Need fast execution (1000 races <5s).

**Why 8 agents?**  
Enough diversity to show different strategies win different scenarios. Not so many that results are noisy.

**Why Gemini specifically?**  
Domain reasoning at scale. Pattern synthesis from numerical data. Strong JSON schema adherence. Free tier sufficient.

**Why local deployment?**  
Hackathon demo, need to work offline. No cloud dependencies.

**Why CSV + JSON storage?**  
Simple, portable, easy to debug. No database setup needed.

---

## WHEN TO REFERENCE THIS DOC

**R1 should check:**
- Physics model specification
- Agent strategy descriptions
- Performance targets (1000 races <5s)

**R2 should check:**
- API contracts
- Integration points with R1/R4
- Data flow diagrams

**R3 should check:**
- UI panel requirements
- API endpoint specifications
- Demo flow sequence

**R4 should check:**
- Gemini synthesis requirements
- Playbook schema
- Fallback strategy
- Demo script structure

---

**This is the single source of truth for project context.**  
**Code details are in individual developer prompts.**  
**Integration contracts are defined here.**

---

END OF PROJECT REFERENCE
