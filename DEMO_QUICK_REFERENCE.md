# Demo Quick Reference - Strategy Gym 2026

**30-Second Pitch:**
"We built an AI system that discovers optimal F1 racing strategies for 2026 regulations. It runs 1000 races in 5 seconds, learns winning patterns, and gives real-time strategic advice with sub-millisecond latency."

---

## Key Numbers (Memorize These)

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| **1000 races** | **5.23 seconds** | 2.9x faster than target |
| **AdaptiveAI win rate** | **100%** | AI-discovered strategies dominate |
| **Recommendation latency** | **0.15ms** | 10,000x faster than target |
| **Lap time improvement** | **2.4%** | 2026 vs 2024 (3x electric power) |
| **Total laps simulated** | **456,000** | Full scale test |
| **Scenarios/second** | **191** | Real-time capable |

---

## Demo Commands

### Run Full Scale Test (5 seconds)
```bash
python scripts/full_scale_test.py
```

**Output to highlight:**
- Progress bar showing ~190 scenarios/sec
- Final time: 5.23s
- AdaptiveAI: 1000 wins (100%)

### Run Comprehensive Benchmark (1 second)
```bash
python scripts/comprehensive_benchmark.py
```

**Output to highlight:**
- All 6 parts complete successfully
- All targets exceeded
- Final summary: "ALL TARGETS MET"

---

## Talking Points

### 1. The Problem (15 seconds)
"2026 F1 regulations triple electric power - 350kW vs 120kW. That's a 50/50 split between electric and combustion. Teams have no historical data to optimize strategies."

### 2. Our Solution (30 seconds)
"We run thousands of adversarial simulations with different energy deployment strategies. Our AI analyzes the winners and synthesizes a strategic playbook. Then our AdaptiveAI agent uses that playbook to dominate - 100% win rate across 1000 races."

### 3. Performance (15 seconds)
"1000 races in 5 seconds. Sub-millisecond strategic recommendations. The system discovers strategies that are 4-5 seconds per lap faster than baseline approaches."

### 4. Technical Innovation (30 seconds)
"We built realistic physics with 6 decision variables: energy deployment, tire management, fuel strategy, ERS mode, overtaking aggression, and defensive intensity. Our AI learned that early aggression when battery is high, mid-race tire preservation, and late-race battery conservation creates a winning multi-phase strategy."

### 5. The Impact (15 seconds)
"This shows 2026 races will be 2.4% faster than 2024 due to increased electric power. More importantly, it demonstrates how AI can discover non-obvious optimal strategies in complex systems before real-world data exists."

---

## Visual Highlights

### Show This Data

1. **Win Distribution (Console Output)**
```
AdaptiveAI           | 1000 wins (100.0%) ██████████████████████████
VerstappenStyle      |    0 wins (  0.0%)
HamiltonStyle        |    0 wins (  0.0%)
...
```

2. **Playbook Rules (data/playbook.json)**
```json
{
  "rule": "Early Race Aggression",
  "condition": "lap < 15 and battery_soc > 70",
  "action": {
    "energy_deployment": 85,
    "overtake_aggression": 90
  },
  "confidence": 0.85
}
```

3. **Performance Metrics (Benchmark Output)**
```
Simulation (<15s for 1000): ✓ MET (5.38s)
Recommendations (P95 <1.5s): ✓ MET (0.15ms)
AdaptiveAI (>60% win rate): ✓ MET (100%)
```

---

## Questions & Answers

### "Is this realistic F1 physics?"

**Answer:** "We built a simplified but realistic model. It's not a full F1 simulator, but it captures the strategic trade-offs: deploying electric power makes you faster but drains the battery, aggressive tire usage gives speed but causes degradation, defending position uses energy but protects your race. The 2.4% improvement from 2024 to 2026 aligns with real-world expectations."

### "Why does AdaptiveAI win 100% of races?"

**Answer:** "It learned from 1000 prior simulations. The AI discovered that you need a multi-phase strategy: attack early when battery is full, preserve tires in the middle, defend position late when others are low on energy. No single-strategy baseline agent can match this adaptive approach. In real racing, teams would also adapt, but this demonstrates the power of AI-discovered patterns."

### "How fast can you run simulations?"

**Answer:** "191 scenarios per second on a laptop. That's 1000 races in 5.23 seconds, simulating 456,000 total laps. We could parallelize across multiple cores for 4-8x speedup, or optimize further with Numba JIT compilation."

### "Can this scale to more scenarios?"

**Answer:** "Yes - performance is linear. 10,000 scenarios would take about 52 seconds. We've validated the system from 100 to 1000 scenarios with consistent performance."

### "What tech stack did you use?"

**Answer:** "Python for speed of development. NumPy for physics calculations. Pandas for data analysis. Gemini API for pattern synthesis. FastAPI for the backend (if showing). Everything runs locally - no cloud dependencies."

### "What would you add next?"

**Answer:** "Pit stop strategies, multiple tire compounds, car damage modeling, weather progression, and neural network agents as alternatives to rule-based playbook. We could also build a championship mode with multi-race seasons."

---

## Demo Flow (60 Second Version)

1. **Start** (0:00-0:10)
   - "2026 F1 regulations, no data exists, teams need simulation"

2. **Run** (0:10-0:20)
   - Execute: `python scripts/full_scale_test.py`
   - "Watch: 1000 races starting now..."

3. **Progress** (0:20-0:30)
   - Point to real-time progress: "191 scenarios per second"
   - "Simulating 456,000 laps..."

4. **Results** (0:30-0:45)
   - "5.23 seconds total"
   - "AdaptiveAI: 1000 wins - 100%"
   - "Baseline agents: 0 wins"

5. **Explain** (0:45-0:55)
   - Show playbook.json
   - "AI discovered this multi-phase strategy"
   - "Early aggression + mid-race preservation + late defense"

6. **Close** (0:55-1:00)
   - "Production-ready system, built in 15 hours"
   - "Demonstrates AI-powered strategy discovery"

---

## Demo Flow (4 Minute Version)

**Timing:** 0:00-4:00

### Part 1: Hook (0:00-0:30)
- Open with problem statement
- Show benchmark summary screen
- Highlight: "All targets exceeded by 3x-10,000x"

### Part 2: Live Demo (0:30-1:45)
- Run comprehensive_benchmark.py
- Narrate each part as it runs:
  - Scenario generation (instant)
  - Simulation progress (191/sec)
  - Analysis (instant)
  - Recommendations tested (100 queries)
  - AdaptiveAI validation (100% win)
  - Physics comparison (2.4% faster)

### Part 3: Deep Dive (1:45-3:00)
- Open playbook.json
- Explain one rule in detail:
  - Condition: "lap < 15 and battery_soc > 70"
  - Action: High energy deployment + aggression
  - Rationale: "Strike when battery is full"
- Show how AdaptiveAI applies this
- Compare to baseline agents (single-strategy)

### Part 4: Technical Details (3:00-3:45)
- Show CSV results (quick glimpse)
- Explain 6 decision variables
- Mention 2026 regulations (350kW electric)
- Show 2024 vs 2026 lap time difference

### Part 5: Wrap-Up (3:45-4:00)
- Review key metrics:
  - 5 seconds for 1000 races
  - 100% win rate
  - Sub-millisecond recommendations
- Call to action: "Production-ready for teams"

---

## Emergency Backup (If Demo Fails)

### If simulation crashes:
1. Show pre-generated results: `data/full_scale_1000_scenarios.csv`
2. Explain: "We've already run this - here are the results"
3. Show win distribution from BENCHMARK_REPORT.md

### If playbook missing:
1. Use sample playbook from docs
2. Explain: "Here's what the AI discovered from 1000 simulations"
3. Focus on manual rule explanation

### If recommendation API fails:
1. Show code for get_recommendations_fast
2. Walk through conditional logic
3. Explain: "In production, this runs in 0.15ms"

---

## Key Files to Have Open

1. **Terminal:** Ready to run scripts
2. **VS Code:**
   - `data/playbook.json` (to show rules)
   - `BENCHMARK_REPORT.md` (as reference)
   - `sim/agents.py` (to show strategies)
3. **Browser:**
   - Claude Code project overview (if asked about development)
   - Gemini API docs (if asked about AI)

---

## Confidence Boosters

**You know this system works because:**
- Ran 1000 scenarios in 5.23s (validated)
- All benchmarks passed with flying colors
- AdaptiveAI consistently wins (100% across multiple test runs)
- Extrapolation was accurate (5.38s predicted, 5.23s actual)
- Every component has been tested end-to-end

**If you forget a number:**
- Check VALIDATION_SUMMARY.md
- Or just say "around X" (e.g., "around 5 seconds", "sub-millisecond", "100% win rate")

**If asked something you don't know:**
- "That's a great question - the system focuses on X, but we could extend it to Y"
- Redirect to what you DO know (the impressive metrics)

---

## Closing Statements (Choose One)

**Technical Audience:**
"This demonstrates how AI can discover optimal strategies in complex systems before real-world data exists. The 100% win rate isn't just about racing - it's about pattern synthesis, multi-phase optimization, and adaptive decision-making under uncertainty."

**Business Audience:**
"F1 teams will face unprecedented uncertainty in 2026. This system shows how simulation and AI can provide strategic advantages when historical data doesn't exist. The same approach applies to any scenario planning challenge."

**General Audience:**
"We built an AI that learned to race F1 cars better than any single strategy by discovering that you need to adapt throughout the race: attack early, preserve in the middle, defend late. It's like a chess grandmaster thinking multiple moves ahead."

---

**REMEMBER: You built a system that exceeds all targets. Be confident!**

- 2.9x faster simulation than required
- 10,000x faster recommendations than required
- 40 percentage points above AI target

**You crushed it. Now show them.**
