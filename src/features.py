"""
Layer 3 — FEATURES
Combines all cleaned races into ONE table and adds engineered features.
Normalizes lap times per race so the model learns degradation patterns,
not raw lap-time differences between tracks.
"""

import os
import glob
import pandas as pd


def build_features():
    files = glob.glob("data/processed/*.parquet")
    if not files:
        raise FileNotFoundError("No processed files found. Run clean.py first.")

    frames = []
    for f in files:
        race_df = pd.read_parquet(f)
        race_name = os.path.basename(f).replace(".parquet", "")
        race_df["Race"] = race_name
        # Reference time: the median of the FASTEST 5 laps in this race
        # (a stable baseline of peak pace on fresh tires).
        ref = race_df["LapTimeSeconds"].nsmallest(5).median()
        race_df["LapTimeDelta"] = race_df["LapTimeSeconds"] - ref
        frames.append(race_df)

    df = pd.concat(frames, ignore_index=True)

    # Engineered features
    df["tyre_life_squared"] = df["TyreLife"] ** 2
    df["race_progress"] = df["LapNumber"] / df["TotalLaps"]
    df = pd.get_dummies(df, columns=["Compound"], prefix="compound")

    for col in ["compound_SOFT", "compound_MEDIUM", "compound_HARD"]:
        if col not in df.columns:
            df[col] = 0

    os.makedirs("data/features", exist_ok=True)
    df.to_parquet("data/features/features.parquet")
    print(f"Feature table saved: {len(df)} rows, {df.shape[1]} columns")
    return df


if __name__ == "__main__":
    build_features()