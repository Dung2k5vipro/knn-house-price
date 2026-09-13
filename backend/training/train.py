from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "house_data1.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "knn_house_model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"
FEATURE_COLUMNS = ["area", "rooms", "distance"]
TARGET_COLUMN = "price"
RANDOM_STATE = 42
SEATTLE_CENTER_LAT = 47.6062
SEATTLE_CENTER_LONG = -122.3321
SQFT_TO_M2 = 0.092903


def haversine_km(
    lat: pd.Series,
    lon: pd.Series,
    center_lat: float = SEATTLE_CENTER_LAT,
    center_lon: float = SEATTLE_CENTER_LONG,
) -> pd.Series:
    radius_km = 6371.0
    lat1 = np.radians(lat.astype(float))
    lon1 = np.radians(lon.astype(float))
    lat2 = np.radians(center_lat)
    lon2 = np.radians(center_lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return pd.Series(2 * radius_km * np.arcsin(np.sqrt(a)), index=lat.index)


def load_house_dataset(data_path: Path = DATA_PATH) -> pd.DataFrame:
    raw_df = pd.read_csv(data_path)
    required_columns = {"price", "bedrooms", "sqft_living", "lat", "long"}
    missing_columns = sorted(required_columns - set(raw_df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df = raw_df[list(required_columns)].copy()
    for column in required_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna()
    df = df[
        (df["price"] > 0)
        & (df["bedrooms"] >= 1)
        & (df["sqft_living"] > 0)
        & (df["lat"] != 0)
        & (df["long"] != 0)
    ].copy()

    dataset = pd.DataFrame(
        {
            "area": (df["sqft_living"] * SQFT_TO_M2).round(2),
            "rooms": df["bedrooms"].round().astype(int),
            "distance": haversine_km(df["lat"], df["long"]).round(3),
            "price": df["price"].astype(float),
        }
    )
    return dataset.reset_index(drop=True)


def evaluate_k_values(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    k_values: list[int],
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for k in k_values:
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("knn", KNeighborsRegressor(n_neighbors=k)),
            ]
        )
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        rows.append(
            {
                "k": k,
                "mae": float(mean_absolute_error(y_test, predictions)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
                "r2": float(r2_score(y_test, predictions)),
            }
        )
    return rows


def select_best_k(k_results: list[dict[str, float]]) -> dict[str, float]:
    ranked = sorted(k_results, key=lambda row: (row["rmse"], row["mae"], row["k"]))
    min_rmse = ranked[0]["rmse"]
    near_best = [row for row in ranked if row["rmse"] <= min_rmse * 1.01]
    stable_candidates = [row for row in near_best if row["k"] >= 5]
    if stable_candidates:
        return sorted(stable_candidates, key=lambda row: (row["rmse"], row["mae"], row["k"]))[0]
    return ranked[0]


def train_model(
    data_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
    metadata_path: Path = METADATA_PATH,
) -> dict[str, object]:
    dataset = load_house_dataset(data_path)
    x = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    k_values = [1, 3, 5, 7, 9, 11, 15, 21, 31]
    k_results = evaluate_k_values(x_train, x_test, y_train, y_test, k_values)
    best_row = select_best_k(k_results)
    best_k = int(best_row["k"])

    final_pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("knn", KNeighborsRegressor(n_neighbors=best_k)),
        ]
    )
    final_pipeline.fit(x_train, y_train)
    final_predictions = final_pipeline.predict(x_test)

    final_metrics = {
        "mae": float(mean_absolute_error(y_test, final_predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, final_predictions))),
        "r2": float(r2_score(y_test, final_predictions)),
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_pipeline, model_path)

    metadata: dict[str, object] = {
        "model": "StandardScaler + KNeighborsRegressor",
        "best_k": best_k,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "area_unit": "m2",
        "distance_unit": "km",
        "price_unit": "usd",
        "source_dataset": str(data_path),
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "metrics": final_metrics,
        "k_results": k_results,
        "random_state": RANDOM_STATE,
        "distance_reference": {
            "name": "Seattle center",
            "lat": SEATTLE_CENTER_LAT,
            "long": SEATTLE_CENTER_LONG,
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Training rows: {len(x_train)}")
    print(f"Test rows: {len(x_test)}")
    print(f"Best K: {best_k}")
    print(f"MAE: {final_metrics['mae']:.2f}")
    print(f"RMSE: {final_metrics['rmse']:.2f}")
    print(f"R2: {final_metrics['r2']:.4f}")
    print(f"Saved model to {model_path}")
    print(f"Saved metadata to {metadata_path}")
    return metadata


if __name__ == "__main__":
    train_model()

