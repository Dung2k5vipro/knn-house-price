from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline


MODEL_NAME = "knn_house_price_regressor"
FEATURE_COLUMNS = ["area", "rooms", "distance"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "knn_house_model.pkl"
DEFAULT_METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.json"


class HousePriceModel:
    def __init__(self) -> None:
        self.model_path = Path(os.getenv("KNN_MODEL_PATH", DEFAULT_MODEL_PATH))
        self.metadata_path = Path(os.getenv("KNN_MODEL_METADATA_PATH", DEFAULT_METADATA_PATH))
        self.pipeline: Pipeline | None = None
        self.metadata: dict[str, Any] = {}

    @property
    def is_loaded(self) -> bool:
        return self.pipeline is not None

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. Run `python training/train.py` first."
            )

        self.pipeline = joblib.load(self.model_path)
        if self.metadata_path.exists():
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        else:
            self.metadata = {}

    def predict(self, area: float, rooms: int, distance: float) -> float:
        if self.pipeline is None:
            raise RuntimeError("Model has not been loaded")

        features = pd.DataFrame(
            [{"area": area, "rooms": rooms, "distance": distance}],
            columns=FEATURE_COLUMNS,
        )
        predicted_price = float(self.pipeline.predict(features)[0])
        return round(max(predicted_price, 0.0), 2)

