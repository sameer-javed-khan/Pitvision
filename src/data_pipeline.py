"""
Layer 1 — RAW DATA
Downloads Formula 1 race data from FastF1 and caches it locally.

WHY THIS FILE EXISTS:
FastF1 fetches official F1 timing data over the internet. The first time you
run this, it downloads each race (slow). After that, everything is saved in
data/cache and loads instantly with no internet needed. This protects you
against the #1 project risk in your docs: FastF1 server downtime.

HOW TO RUN (from the pitvision/ folder, with your venv active):
    python src/data_pipeline.py
"""

import os
import fastf1

# Where downloaded data gets stored on your disk.
CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

# The 5 races from your project documentation.
RACES = ["Bahrain", "Monaco", "Silverstone", "Belgium", "Monza"]
SEASON = 2024


def download_races():
    """Download and cache every race's RACE session ('R')."""
    for race in RACES:
        print(f"Downloading {race} {SEASON}... (first run can take a minute)")
        session = fastf1.get_session(SEASON, race, "R")  # "R" = the Race
        session.load()                                   # downloads + caches
        print(f"  -> Loaded {race}: {len(session.laps)} laps")
    print("All races downloaded and cached.")


if __name__ == "__main__":
    download_races()
