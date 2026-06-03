# 🏎️ PitVision — F1 Tire Degradation Predictor

PitVision is an end-to-end machine learning project that predicts Formula 1 lap
times from tire compound, tire age, race progress, and stint number. It trains
regression models on real 2024 F1 race data (via the FastF1 library) and serves
predictions through an interactive Streamlit web dashboard.

**Live app:** https://pitvision.streamlit.app
---

## What it does

Given a tire compound (Soft / Medium / Hard), how many laps old the tire is, how
far through the race you are, and the stint number, PitVision predicts the lap
time in seconds and plots a full tire-degradation curve.

---

## Tech stack

Python · FastF1 · Pandas / NumPy · scikit-learn · XGBoost · Streamlit · Git/GitHub

---

## Project structure

```
pitvision/
├── data/
│   ├── cache/        # FastF1 raw download cache (gitignored)
│   ├── processed/    # cleaned parquet, one per race
│   └── features/     # final combined feature table
├── models/
│   └── tire_degradation.pkl   # the saved best model
├── notebooks/
│   ├── 01_eda.ipynb           # exploratory data analysis
│   └── 02_training.ipynb      # train + evaluate + save the model
├── src/
│   ├── data_pipeline.py       # Layer 1: download races
│   ├── clean.py               # Layer 2: clean junk laps
│   ├── features.py            # Layer 3: feature engineering
│   └── inference.py           # Layer 5: predict_lap_time()
├── streamlit_app.py           # Layer 6: the dashboard
├── run_pipeline.py            # runs Layers 1->3 in one command
├── requirements.txt
└── README.md
```

---

## Setup (macOS, Apple Silicon)

1. **Install Homebrew** (if you don't have it):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install libomp** (required by XGBoost on Apple Silicon):
   ```bash
   brew install libomp
   ```

3. **Create and activate a virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## How to run

**1. Build the dataset** (downloads + cleans + engineers features):
```bash
python run_pipeline.py
```

**2. Explore the data** (optional but recommended):
```bash
jupyter notebook
# open notebooks/01_eda.ipynb and run all cells
```

**3. Train the models** and save the best one:
```bash
# open notebooks/02_training.ipynb and run all cells
```

**4. Launch the dashboard:**
```bash
streamlit run streamlit_app.py
```
Opens at http://localhost:8501

---

## Model performance

| Metric | Result |
|--------|--------|
| MAE    | 0.612s (XGBoost) |
| R²     | 0.600 |
| Best model | XGBoost |

---

## Deployment

Hosted on [Streamlit Community Cloud](https://share.streamlit.io). Push to GitHub,
connect the repo, set the main file to `streamlit_app.py`, and deploy.

---

## Authors

Sameer Javed Khan · Narmeen Javed — AI Lab, Section F-4
