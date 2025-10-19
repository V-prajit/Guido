# 2026 F1 Power Unit Physics (Simplified)

## Constants
- ICE_POWER: 400 kW (constant)
- MGU_K_MAX: 350 kW (variable, controlled by driver)
- BATTERY_CAPACITY: 4.0 MJ
- RACE_LAPS: 57 (default, varies by track)

## Track Section Distribution
- Straights: 40% of lap
- Corners: 45% of lap
- Braking zones: 15% of lap

## Agent Decisions (per lap)
- deploy_straight: 0-100% (how much electric on straights)
- deploy_corner: 0-100% (how much electric on corner exits)
- harvest_intensity: 0-100% (energy recovery aggressiveness)
- use_boost: boolean (manual override, 2 uses per race, 3s each)

## Lap Time Formula
base_time = 90.0 seconds
- Electric deployment bonus: -0.003s per % on straights, -0.002s per % on corners
- Harvesting penalty: +0.0015s per % (slowing down to recover energy)
- Low battery penalty: if SOC < 20%, add (20 - SOC) * 0.02s
- Aero mode: two modes (low/high drag), switching costs 0.15s/lap
