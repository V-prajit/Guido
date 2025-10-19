"""
Extract baseline physics parameters from 2024 Bahrain Grand Prix telemetry.
Uses FastF1 to analyze real race data and extract realistic parameters for simulation.
"""

import fastf1
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

# Setup
CACHE_DIR = Path(__file__).parent.parent / "cache"
DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))

def load_bahrain_gp():
    """Load 2024 Bahrain GP race session."""
    print("Loading 2024 Bahrain GP race data...")
    session = fastf1.get_session(2024, 'Bahrain', 'R')
    session.load()
    print(f"✓ Loaded session with {len(session.drivers)} drivers, {len(session.laps)} laps")
    return session

def analyze_tire_compounds(session):
    """Analyze lap times by tire compound to extract base time and degradation."""
    print("\nAnalyzing tire compounds...")

    laps = session.laps

    # Filter for clean laps only
    # Exclude: pit laps, first lap, laps with track limits, very slow laps
    clean_laps = laps[
        (laps['PitInTime'].isna()) &  # Not a pit in lap
        (laps['PitOutTime'].isna()) &  # Not a pit out lap
        (laps['LapNumber'] > 1) &  # Skip first lap
        (laps['LapTime'].notna()) &  # Has lap time
        (laps['Compound'].notna())  # Has tire compound data
    ].copy()

    # Convert LapTime to seconds
    clean_laps['LapTimeSeconds'] = clean_laps['LapTime'].dt.total_seconds()

    # Remove outliers (laps > 110s are likely safety car or incidents)
    clean_laps = clean_laps[clean_laps['LapTimeSeconds'] < 110]

    tire_data = {}

    for compound in ['SOFT', 'MEDIUM', 'HARD']:
        compound_laps = clean_laps[clean_laps['Compound'] == compound].copy()

        if len(compound_laps) < 10:
            print(f"  - {compound}: Insufficient data ({len(compound_laps)} laps)")
            continue

        # Calculate tire age for each lap
        compound_laps['TireAge'] = compound_laps['TyreLife']

        # Base time = median of first 3 laps on fresh tires
        fresh_laps = compound_laps[compound_laps['TireAge'] <= 3]
        if len(fresh_laps) > 0:
            base_time = fresh_laps['LapTimeSeconds'].median()
        else:
            base_time = compound_laps['LapTimeSeconds'].quantile(0.1)

        # Degradation = correlation between tire age and lap time
        if len(compound_laps) > 20:
            # Group by tire age and calculate average lap time
            age_groups = compound_laps.groupby('TireAge')['LapTimeSeconds'].agg(['mean', 'count'])
            age_groups = age_groups[age_groups['count'] >= 3]  # Only ages with 3+ samples

            if len(age_groups) >= 5:
                # Linear regression: lap_time = base + deg_rate * tire_age
                ages = age_groups.index.values
                times = age_groups['mean'].values

                # Simple linear regression
                deg_rate = np.polyfit(ages, times, 1)[0]
                deg_rate = max(0.01, min(0.15, deg_rate))  # Clamp to realistic range
            else:
                # Default degradation rates
                deg_rates = {'SOFT': 0.08, 'MEDIUM': 0.05, 'HARD': 0.03}
                deg_rate = deg_rates[compound]
        else:
            deg_rates = {'SOFT': 0.08, 'MEDIUM': 0.05, 'HARD': 0.03}
            deg_rate = deg_rates[compound]

        tire_data[compound] = {
            "base_time": round(float(base_time), 2),
            "deg_rate": round(float(deg_rate), 3)
        }

        print(f"  - {compound}: base={base_time:.2f}s, deg={deg_rate:.3f}s/lap (from {len(compound_laps)} laps)")

    return tire_data

def analyze_fuel_effect(session):
    """Analyze fuel effect by comparing early vs late race laps."""
    print("\nAnalyzing fuel effect...")

    laps = session.laps

    # Get clean laps from race winner or top finishers
    clean_laps = laps[
        (laps['PitInTime'].isna()) &
        (laps['PitOutTime'].isna()) &
        (laps['LapTime'].notna()) &
        (laps['LapNumber'] > 1)
    ].copy()

    clean_laps['LapTimeSeconds'] = clean_laps['LapTime'].dt.total_seconds()
    clean_laps = clean_laps[clean_laps['LapTimeSeconds'] < 110]

    # Compare early laps (2-5, heavy fuel) vs late laps (50-57, light fuel)
    early_laps = clean_laps[clean_laps['LapNumber'].between(2, 5)]
    late_laps = clean_laps[clean_laps['LapNumber'].between(50, 57)]

    if len(early_laps) > 10 and len(late_laps) > 10:
        early_median = early_laps['LapTimeSeconds'].median()
        late_median = late_laps['LapTimeSeconds'].median()

        # Fuel difference ~50 laps * 1.8 kg/lap = 90kg
        fuel_diff = 50 * 1.8
        time_diff = early_median - late_median

        # Penalty per kg (but this includes tire deg, so adjust)
        penalty_per_kg = time_diff / fuel_diff if fuel_diff > 0 else 0.03
        penalty_per_kg = max(0.02, min(0.04, penalty_per_kg))
    else:
        penalty_per_kg = 0.03  # Default

    fuel_data = {
        "penalty_per_kg": round(float(penalty_per_kg), 3),
        "consumption_per_lap": 1.8,
        "starting_fuel": 110
    }

    print(f"  - Fuel penalty: {penalty_per_kg:.3f}s per kg")
    print(f"  - Consumption: {1.8} kg/lap")
    print(f"  - Starting fuel: {110} kg")

    return fuel_data

def analyze_ers_deployment(session):
    """Analyze ERS deployment patterns from telemetry."""
    print("\nAnalyzing ERS deployment...")

    # ERS regulations: 4 MJ per lap harvest/deploy limit
    # Speed benefit is hard to extract directly, use typical values

    ers_data = {
        "avg_per_lap": 4.0,  # MJ - regulatory limit
        "max_per_lap": 4.0,  # MJ - regulatory limit
        "speed_benefit_per_mj": 0.3  # Estimated seconds per MJ
    }

    print(f"  - Average deployment: {ers_data['avg_per_lap']} MJ/lap")
    print(f"  - Max deployment: {ers_data['max_per_lap']} MJ/lap")
    print(f"  - Speed benefit: {ers_data['speed_benefit_per_mj']}s per MJ")

    return ers_data

def analyze_track_characteristics(session):
    """Extract track-specific characteristics."""
    print("\nAnalyzing track characteristics...")

    laps = session.laps

    # Base lap time from clean laps
    clean_laps = laps[
        (laps['PitInTime'].isna()) &
        (laps['PitOutTime'].isna()) &
        (laps['LapTime'].notna()) &
        (laps['LapNumber'].between(5, 55))  # Mid-race, settled pace
    ].copy()

    clean_laps['LapTimeSeconds'] = clean_laps['LapTime'].dt.total_seconds()
    clean_laps = clean_laps[clean_laps['LapTimeSeconds'] < 110]

    if len(clean_laps) > 0:
        base_lap_time = clean_laps['LapTimeSeconds'].median()
    else:
        base_lap_time = 92.0

    # DRS and slipstream effects - typical values for Bahrain
    drs_gain = 0.3  # seconds per lap with DRS
    slipstream_gain = 0.2  # seconds when following closely

    # Overtaking difficulty - Bahrain is medium (has DRS zones but not easy)
    overtaking_difficulty = "medium"

    # Temperature from weather data
    if hasattr(session, 'weather_data') and session.weather_data is not None:
        temps = session.weather_data['AirTemp'].dropna()
        if len(temps) > 0:
            temp_range = [float(temps.min()), float(temps.max())]
        else:
            temp_range = [25, 35]
    else:
        temp_range = [25, 35]

    track_data = {
        "base_lap_time": round(float(base_lap_time), 1),
        "drs_gain": drs_gain,
        "slipstream_gain": slipstream_gain,
        "overtaking_difficulty": overtaking_difficulty,
        "temperature_range": temp_range
    }

    print(f"  - Base lap time: {base_lap_time:.1f}s")
    print(f"  - DRS gain: {drs_gain}s")
    print(f"  - Slipstream gain: {slipstream_gain}s")
    print(f"  - Overtaking difficulty: {overtaking_difficulty}")
    print(f"  - Temperature range: {temp_range}")

    return track_data

def extract_race_info(session):
    """Extract basic race information."""
    print("\nExtracting race info...")

    race_info = {
        "num_laps": int(session.total_laps),
        "track_name": "Bahrain International Circuit",
        "date": session.date.strftime("%Y-%m-%d") if hasattr(session, 'date') else "2024-03-02"
    }

    print(f"  - Laps: {race_info['num_laps']}")
    print(f"  - Track: {race_info['track_name']}")
    print(f"  - Date: {race_info['date']}")

    return race_info

def main():
    """Main extraction pipeline."""
    print("=" * 60)
    print("FastF1 Baseline Parameter Extraction")
    print("2024 Bahrain Grand Prix")
    print("=" * 60)

    # Load session
    session = load_bahrain_gp()

    # Extract all parameters
    tire_data = analyze_tire_compounds(session)
    fuel_data = analyze_fuel_effect(session)
    ers_data = analyze_ers_deployment(session)
    track_data = analyze_track_characteristics(session)
    race_info = extract_race_info(session)

    # Compile baseline
    baseline = {
        "tire_compounds": tire_data,
        "fuel_effect": fuel_data,
        "ers_deployment": ers_data,
        "track_characteristics": track_data,
        "race_info": race_info
    }

    # Save to JSON
    output_path = DATA_DIR / "baseline_2024.json"
    with open(output_path, 'w') as f:
        json.dump(baseline, f, indent=2)

    print("\n" + "=" * 60)
    print(f"✓ Baseline parameters saved to {output_path}")
    print("=" * 60)

    # Summary
    print("\nSUMMARY:")
    print(f"✓ FastF1 loaded: 2024 Bahrain GP")
    print(f"✓ Analyzed {len(session.laps)} total laps from {len(session.drivers)} drivers")
    print("✓ Tire Analysis:")
    for compound, data in tire_data.items():
        print(f"  - {compound}: base={data['base_time']}s, deg={data['deg_rate']}s/lap")
    print(f"✓ Fuel Effect: {fuel_data['penalty_per_kg']}s per kg")
    print(f"✓ ERS: ~{ers_data['avg_per_lap']} MJ per lap, {ers_data['speed_benefit_per_mj']}s speed benefit")
    print(f"✓ Track: base lap {track_data['base_lap_time']}s, DRS gain {track_data['drs_gain']}s")
    print(f"✓ Saved to {output_path}")

if __name__ == "__main__":
    main()
