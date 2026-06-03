"""
Layer 2 — PROCESSED DATA
Cleans the raw F1 laps and saves one tidy parquet file per race.

WHY THIS FILE EXISTS:
Raw F1 data is full of laps that are NOT normal racing pace: pit-stop laps,
safety-car laps, and slow laps. If we trained on those, the model would learn
wrong patterns. This file removes the junk so the model only sees clean,
representative racing laps. These are exactly the steps from Section 4.4 of
your documentation.

HOW TO RUN:
    python src/clean.py
"""

import os
import fastf1

fastf1.Cache.enable_cache("data/cache")

RACES = ["Bahrain", "Monaco", "Silverstone", "Belgium", "Monza"]
SEASON = 2024


def clean_race(race, season=SEASON):
    """Load one race from cache and return a cleaned table of laps."""
    session = fastf1.get_session(season, race, "R")
    session.load()

    laps = session.laps
    laps = laps.pick_quicklaps()   # drop laps slower than 107% of the median pace
    laps = laps.pick_wo_box()      # drop in-laps / out-laps (entering/leaving pits)

    # Keep only the columns we need.
    df = laps[["Driver", "LapNumber", "LapTime",
               "Compound", "TyreLife", "Stint"]].copy()

    # Convert lap time from a time-duration into plain seconds (e.g. 78.42).
    df["LapTimeSeconds"] = df["LapTime"].dt.total_seconds()

    # Total laps in this race — needed later to compute race progress.
    df["TotalLaps"] = session.total_laps

    # Remove any rows with missing values in the columns the model needs.
    df = df.dropna(subset=["LapTimeSeconds", "Compound", "TyreLife", "Stint"])

    return df


def clean_all():
    """Clean every race and save each as a parquet file."""
    os.makedirs("data/processed", exist_ok=True)
    for race in RACES:
        df = clean_race(race)
        out_path = f"data/processed/{race}.parquet"
        df.to_parquet(out_path)
        print(f"{race}: {len(df)} clean laps -> {out_path}")
    print("Cleaning complete.")


if __name__ == "__main__":
    clean_all()
