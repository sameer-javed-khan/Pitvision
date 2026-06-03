"""
RUN THE WHOLE DATA PIPELINE WITH ONE COMMAND.

This runs Layer 1 (download) -> Layer 2 (clean) -> Layer 3 (features) in order.
After it finishes, data/features/features.parquet is ready for training.

HOW TO RUN (from the pitvision/ folder, venv active):
    python run_pipeline.py
"""

from src.data_pipeline import download_races
from src.clean import clean_all
from src.features import build_features

if __name__ == "__main__":
    print("STEP 1/3: Downloading races...")
    download_races()

    print("\nSTEP 2/3: Cleaning data...")
    clean_all()

    print("\nSTEP 3/3: Building features...")
    build_features()

    print("\nPipeline complete -> data/features/features.parquet")
    print("Next: open notebooks/02_training.ipynb to train the models.")
