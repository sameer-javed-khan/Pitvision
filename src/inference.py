"""
Layer 5 — INFERENCE
"""
import os
import joblib
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH = os.path.join(_HERE, "..", "models", "tire_degradation.pkl")

_bundle = joblib.load(_MODEL_PATH)
_model = _bundle["model"]
_features = _bundle["features"]

# A representative reference lap time so users see a sensible absolute number.
# Average of fresh-tire pace across the 5 races (~75-95s territory).
REFERENCE_LAP_TIME = 85.0


def predict_lap_time(compound, tyre_life, race_progress, stint):
    """Predict a lap time in seconds (reference pace + predicted degradation)."""
    row = {
        "TyreLife": tyre_life,
        "tyre_life_squared": tyre_life ** 2,
        "race_progress": race_progress,
        "Stint": stint,
        "compound_SOFT": 1 if compound == "SOFT" else 0,
        "compound_MEDIUM": 1 if compound == "MEDIUM" else 0,
        "compound_HARD": 1 if compound == "HARD" else 0,
    }
    X = pd.DataFrame([row])[_features]
    delta = float(_model.predict(X)[0])
    return REFERENCE_LAP_TIME + delta