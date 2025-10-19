# Quick Start Guide - Realistic Physics Engine

## Installation

```bash
# Install dependencies (already done if following main setup)
pip install fastf1  # For real F1 data

# Verify installation
python -c "import fastf1; print('✓ FastF1 installed')"
```

## Running the System

### 1. Validate 2024 Physics (30 seconds)

```bash
python scripts/validate_2024.py
```

**What it does:**
- Runs simulation with 2024 physics
- Compares to real 2024 Bahrain GP results
- Proves accuracy within ±2 seconds

**Expected output:**
```
✓ VerstappenStyle: 0.59s difference from real
✓ HamiltonStyle: 0.04s difference from real
✓ AlonsoStyle: 1.08s difference from real
✓ VALIDATION PASSED
```

### 2. Run Comprehensive Benchmark (1 second)

```bash
python scripts/comprehensive_benchmark.py
```

**What it does:**
- Tests full pipeline (100 scenarios)
- Measures performance vs targets
- Validates AdaptiveAI effectiveness

**Expected output:**
```
✓ Simulated 100 races in 0.54s
✓ Performance: 186 scenarios/sec
✓ AdaptiveAI wins: 100/100 (100%)
🎉 ALL TARGETS MET
```

### 3. Full Scale Test (5 seconds)

```bash
python scripts/full_scale_test.py
```

**What it does:**
- Runs 1000 complete races
- Tests 2026 physics at scale
- Proves production performance

**Expected output:**
```
✓ 1000 scenarios in 5.38s
✓ AdaptiveAI: 1000 wins (100%)
✓ Total laps simulated: 456,000
```

## Using the API

### Start the Server

```bash
uvicorn api.main:app --reload
```

### Test Endpoints

```bash
# Run simulations
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"num_scenarios": 100, "num_agents": 8}'

# Get recommendations
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "lap": 30,
    "battery_soc": 45,
    "position": 3,
    "tire_life": 60,
    "fuel_remaining": 50
  }'
```

## Understanding the Output

### Simulation DataFrame (15 columns)

| Column | Description |
|--------|-------------|
| agent | Agent name |
| lap | Lap number (1-57) |
| battery_soc | Battery charge (0-100%) |
| tire_life | Tire condition (0-100%) |
| fuel_remaining | Fuel in kg |
| lap_time | Lap time in seconds |
| cumulative_time | Total race time |
| final_position | Race position (1-8) |
| won | True if winner |
| energy_deployment | Energy decision (0-100) |
| tire_management | Tire decision (0-100) |
| fuel_strategy | Fuel decision (0-100) |
| ers_mode | ERS decision (0-100) |
| overtake_aggression | Attack decision (0-100) |
| defense_intensity | Defense decision (0-100) |

### Performance Metrics

- **Simulation Speed:** ~186 scenarios/sec (1000 in ~5s)
- **Recommendation Latency:** <1ms (P95: 0.15ms)
- **AdaptiveAI Win Rate:** 100% (beats all other agents)

## Troubleshooting

**Issue:** FastF1 cache errors
**Solution:** Delete `cache/` directory and re-run

**Issue:** Slow simulations
**Solution:** Check if running in debug mode, use production mode

**Issue:** AdaptiveAI not winning
**Solution:** Ensure `data/playbook.json` exists with schema v2.0

## Next Steps

1. **Frontend Integration:** Connect Next.js UI to API endpoints
2. **Gemini Integration:** Use real Gemini API to generate playbooks
3. **Track Expansion:** Run `extract_baseline.py` on other races
4. **Optimization:** Add Numba JIT for even faster simulations

## Support

See full documentation:
- `PHYSICS_README.md` - Physics details
- `AGENTS_V2_SUMMARY.md` - Agent strategies
- `BENCHMARK_REPORT.md` - Performance analysis
- `DEMO_SCRIPT.md` - Hackathon demo guide
