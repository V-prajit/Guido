#!/usr/bin/env python3
"""
Learn racing strategies from real F1 driver behavior.
Analyzes 2024 Bahrain GP to extract strategic patterns from Verstappen, Hamilton, and Alonso.
"""

import fastf1
import numpy as np
import pandas as pd
import json
from pathlib import Path

# Enable caching to speed up data loading
CACHE_DIR = Path(__file__).parent.parent / 'cache'
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

def calculate_energy_deployment(driver_laps):
    """
    Analyze energy deployment pattern from telemetry.
    Returns 0-100 score where 100 = very aggressive deployment.
    """
    # Use throttle application as proxy for energy deployment aggression
    throttle_values = []

    for lap in driver_laps.iterlaps():
        lap_data = lap[1]
        try:
            telemetry = lap_data.get_telemetry()
            if telemetry is not None and 'Throttle' in telemetry.columns:
                # Average throttle application per lap
                avg_throttle = telemetry['Throttle'].mean()
                throttle_values.append(avg_throttle)
        except Exception:
            continue

    if throttle_values:
        # Normalize to 0-100 scale
        avg_deployment = np.mean(throttle_values)
        # Typical throttle is 60-85%, map to strategic scale
        score = min(100, max(0, (avg_deployment - 50) * 2))
        return round(score, 1)
    return 60.0  # Default moderate


def calculate_tire_management(driver_laps):
    """
    Analyze tire management from lap time consistency.
    Returns 0-100 where 100 = aggressive push, 0 = conservation.
    """
    lap_times = []

    for lap in driver_laps.iterlaps():
        lap_data = lap[1]
        if pd.notna(lap_data['LapTime']):
            lap_times.append(lap_data['LapTime'].total_seconds())

    if len(lap_times) < 5:
        return 60.0

    # Calculate lap time variance (lower variance = more conservation)
    variance = np.std(lap_times)

    # Higher variance = more push/conserve cycling = aggressive
    # Typical variance: 0.5-2.5 seconds
    score = min(100, max(0, variance * 30))
    return round(score, 1)


def calculate_fuel_strategy(driver_laps, position_data):
    """
    Analyze fuel consumption pattern from pace relative to position.
    Returns 0-100 where 100 = aggressive/rich fuel mode.
    """
    # Use early race pace vs late race pace as proxy
    early_laps = []
    late_laps = []

    for idx, lap in enumerate(driver_laps.iterlaps()):
        lap_data = lap[1]
        if pd.notna(lap_data['LapTime']):
            lap_time = lap_data['LapTime'].total_seconds()
            if idx < len(driver_laps) // 3:
                early_laps.append(lap_time)
            elif idx > 2 * len(driver_laps) // 3:
                late_laps.append(lap_time)

    if early_laps and late_laps:
        early_avg = np.mean(early_laps)
        late_avg = np.mean(late_laps)

        # Aggressive fuel = faster early pace (more fuel burning)
        pace_ratio = early_avg / late_avg
        # Ratio close to 1 or below = aggressive early, above = conservative
        score = min(100, max(0, (1.05 - pace_ratio) * 200 + 50))
        return round(score, 1)

    return 50.0  # Default balanced


def calculate_ers_mode(driver_laps):
    """
    Calculate harvest vs deploy balance.
    Returns 0-100 where 0=heavy harvest, 100=heavy deploy.
    """
    # Use speed in corners vs straights as proxy
    corner_speeds = []
    straight_speeds = []

    for lap in driver_laps.iterlaps():
        lap_data = lap[1]
        try:
            telemetry = lap_data.get_telemetry()
            if telemetry is not None and 'Speed' in telemetry.columns:
                speeds = telemetry['Speed']
                # Assume lowest 30% = corners, highest 30% = straights
                sorted_speeds = speeds.sort_values()
                n = len(sorted_speeds)
                corner_speeds.extend(sorted_speeds.iloc[:n//3].tolist())
                straight_speeds.extend(sorted_speeds.iloc[-n//3:].tolist())
        except Exception:
            continue

    if corner_speeds and straight_speeds:
        corner_avg = np.mean(corner_speeds)
        straight_avg = np.mean(straight_speeds)

        # Higher corner exit speed relative to straight = more deployment
        relative_corner_speed = corner_avg / straight_avg
        # Typical: 0.4-0.6, higher = more deploy
        score = min(100, max(0, (relative_corner_speed - 0.35) * 400))
        return round(score, 1)

    return 60.0  # Default deploy-biased


def calculate_overtake_aggression(driver_laps, driver_name):
    """
    Calculate overtaking aggression from position changes.
    Returns 0-100 based on overtakes made and attempts.
    """
    positions = []

    for lap in driver_laps.iterlaps():
        lap_data = lap[1]
        if pd.notna(lap_data['Position']):
            positions.append(lap_data['Position'])

    if len(positions) < 2:
        return 50.0

    # Count position gains (overtakes)
    overtakes = sum(1 for i in range(1, len(positions)) if positions[i] < positions[i-1])

    # Count position losses (being overtaken)
    losses = sum(1 for i in range(1, len(positions)) if positions[i] > positions[i-1])

    # Aggression = overtakes made, with bonus for net gain
    net_gain = overtakes - losses
    score = min(100, max(0, overtakes * 15 + net_gain * 10 + 40))

    return round(score, 1)


def calculate_defense_intensity(driver_laps, driver_name):
    """
    Calculate defensive capability.
    Returns 0-100 based on position holding and defensive maneuvers.
    """
    positions = []

    for lap in driver_laps.iterlaps():
        lap_data = lap[1]
        if pd.notna(lap_data['Position']):
            positions.append(lap_data['Position'])

    if len(positions) < 2:
        return 50.0

    # Count times position was maintained or improved
    maintained = sum(1 for i in range(1, len(positions)) if positions[i] <= positions[i-1])
    lost = sum(1 for i in range(1, len(positions)) if positions[i] > positions[i-1])

    # Strong defense = high maintain rate
    maintain_rate = maintained / (maintained + lost) if (maintained + lost) > 0 else 0.5
    score = maintain_rate * 100

    # Boost score if started in front and maintained
    if positions[0] <= 3 and positions[-1] <= 3:
        score = min(100, score * 1.2)

    return round(score, 1)


def analyze_driver(session, driver_code, driver_name):
    """
    Comprehensive driver analysis.
    """
    print(f"\n{'='*50}")
    print(f"Analyzing {driver_name} ({driver_code})...")
    print(f"{'='*50}")

    # Get driver data
    driver_laps = session.laps.pick_driver(driver_code)

    if driver_laps.empty:
        print(f"No data found for {driver_code}")
        return None

    # Get final position
    final_position = int(driver_laps.iloc[-1]['Position']) if pd.notna(driver_laps.iloc[-1]['Position']) else 0

    # Calculate average lap time (excluding outliers)
    lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'] if pd.notna(lt)]
    if lap_times:
        # Remove top and bottom 10% to exclude pit laps and incidents
        lap_times_sorted = sorted(lap_times)
        trim_count = len(lap_times_sorted) // 10
        if trim_count > 0:
            lap_times_trimmed = lap_times_sorted[trim_count:-trim_count]
        else:
            lap_times_trimmed = lap_times_sorted
        avg_lap_time = np.mean(lap_times_trimmed)
    else:
        avg_lap_time = 0.0

    # Get tire stints
    tire_stints = []
    current_compound = None
    stint_laps = 0

    for lap in driver_laps.iterlaps():
        lap_data = lap[1]
        compound = lap_data['Compound']
        if pd.notna(compound):
            if compound != current_compound:
                if current_compound is not None:
                    tire_stints.append(f"{current_compound}-{stint_laps}")
                current_compound = compound
                stint_laps = 1
            else:
                stint_laps += 1

    if current_compound is not None:
        tire_stints.append(f"{current_compound}-{stint_laps}")

    # Calculate strategic scores
    print("Calculating strategic variables...")

    energy_deployment = calculate_energy_deployment(driver_laps)
    print(f"  Energy Deployment: {energy_deployment}/100")

    tire_management = calculate_tire_management(driver_laps)
    print(f"  Tire Management: {tire_management}/100")

    fuel_strategy = calculate_fuel_strategy(driver_laps, final_position)
    print(f"  Fuel Strategy: {fuel_strategy}/100")

    ers_mode = calculate_ers_mode(driver_laps)
    print(f"  ERS Mode: {ers_mode}/100")

    overtake_aggression = calculate_overtake_aggression(driver_laps, driver_name)
    print(f"  Overtake Aggression: {overtake_aggression}/100")

    defense_intensity = calculate_defense_intensity(driver_laps, driver_name)
    print(f"  Defense Intensity: {defense_intensity}/100")

    # Count position changes
    positions = [int(p) for p in driver_laps['Position'] if pd.notna(p)]
    overtakes_made = sum(1 for i in range(1, len(positions)) if positions[i] < positions[i-1])
    overtakes_defended = sum(1 for i in range(1, len(positions)) if positions[i] > positions[i-1])

    profile = {
        "energy_deployment": energy_deployment,
        "tire_management": tire_management,
        "fuel_strategy": fuel_strategy,
        "ers_mode": ers_mode,
        "overtake_aggression": overtake_aggression,
        "defense_intensity": defense_intensity,
        "analysis": {
            "laps_analyzed": len(driver_laps),
            "final_position": final_position,
            "avg_lap_time": round(avg_lap_time, 2),
            "tire_stints": tire_stints,
            "overtakes_made": overtakes_made,
            "overtakes_defended": overtakes_defended
        }
    }

    return profile


def print_summary(driver_name, profile):
    """
    Print driver profile summary.
    """
    print(f"\n{driver_name} Summary:")
    print(f"  Position: P{profile['analysis']['final_position']}")
    print(f"  Avg Lap: {profile['analysis']['avg_lap_time']}s")
    print(f"  Stints: {', '.join(profile['analysis']['tire_stints'])}")
    print(f"  Overtakes: {profile['analysis']['overtakes_made']} made, {profile['analysis']['overtakes_defended']} lost")
    print(f"\n  Strategic Profile:")
    print(f"    Energy:   {profile['energy_deployment']}/100 {'(aggressive)' if profile['energy_deployment'] > 70 else '(conservative)' if profile['energy_deployment'] < 50 else '(moderate)'}")
    print(f"    Tire:     {profile['tire_management']}/100 {'(pusher)' if profile['tire_management'] > 70 else '(saver)' if profile['tire_management'] < 50 else '(balanced)'}")
    print(f"    Fuel:     {profile['fuel_strategy']}/100 {'(rich)' if profile['fuel_strategy'] > 60 else '(lean)' if profile['fuel_strategy'] < 40 else '(balanced)'}")
    print(f"    ERS:      {profile['ers_mode']}/100 {'(deploy-heavy)' if profile['ers_mode'] > 60 else '(harvest-heavy)' if profile['ers_mode'] < 40 else '(balanced)'}")
    print(f"    Overtake: {profile['overtake_aggression']}/100 {'(very aggressive)' if profile['overtake_aggression'] > 70 else '(cautious)' if profile['overtake_aggression'] < 50 else '(calculated)'}")
    print(f"    Defense:  {profile['defense_intensity']}/100 {'(strong)' if profile['defense_intensity'] > 70 else '(weak)' if profile['defense_intensity'] < 50 else '(moderate)'}")


def main():
    """
    Main analysis pipeline.
    """
    print("="*60)
    print("F1 STRATEGY LEARNING - 2024 Bahrain Grand Prix")
    print("="*60)

    # Load 2024 Bahrain GP race session
    print("\nLoading race data...")
    try:
        session = fastf1.get_session(2024, 'Bahrain', 'R')
        session.load()
        print("✓ Race data loaded successfully")
    except Exception as e:
        print(f"Error loading race data: {e}")
        return

    # Drivers to analyze
    drivers = [
        ('VER', 'verstappen_2024', 'Max Verstappen'),
        ('HAM', 'hamilton_2024', 'Lewis Hamilton'),
        ('ALO', 'alonso_2024', 'Fernando Alonso')
    ]

    print(f"\n✓ Analyzing {len(drivers)} drivers: {', '.join([d[0] for d in drivers])}")

    # Analyze each driver
    profiles = {}

    for driver_code, profile_key, driver_name in drivers:
        profile = analyze_driver(session, driver_code, driver_name)
        if profile:
            profiles[profile_key] = profile
            print_summary(driver_name, profile)

    # Save results
    if profiles:
        output_path = Path(__file__).parent.parent / 'data' / 'learned_strategies.json'
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(profiles, f, indent=2)

        print(f"\n{'='*60}")
        print(f"✓ Saved {len(profiles)} driver profiles to {output_path}")
        print(f"{'='*60}")
    else:
        print("\nError: No profiles generated")


if __name__ == '__main__':
    main()
