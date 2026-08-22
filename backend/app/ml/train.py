import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

REGION_MAP = {
    "Europe": 0,
    "Americas": 1,
    "North America": 1,
    "South America": 1,
    "Asia": 2,
    "Oceania": 3,
    "Africa": 4,
    "Middle East": 5,
}


def encode_region(region: str) -> int:
    """Encodes region name to a consistent integer index."""
    if not region:
        return 0
    for key, val in REGION_MAP.items():
        if key.lower() in region.lower():
            return val
    return 0


def generate_synthetic_data(n_samples: int = 500, random_state: int = 42) -> pd.DataFrame:
    """
    Generates synthetic trip training data with realistic multi-city expense patterns:
    - days range 3-30
    - stops range 1-8
    - activities per stop range 2-6
    - cost_index range 40-200
    - cost = (avg_cost_index * days * 1.1) + total_activity_cost + (25 * days) + noise
    """
    np.random.seed(random_state)

    total_days = np.random.randint(3, 31, size=n_samples)
    num_stops = np.clip(np.random.randint(1, 9, size=n_samples), 1, total_days)
    activities_per_stop = np.random.randint(2, 7, size=n_samples)
    num_activities = num_stops * activities_per_stop
    avg_city_cost_index = np.random.uniform(40.0, 200.0, size=n_samples)
    total_activity_cost = num_activities * np.random.uniform(20.0, 60.0, size=n_samples)
    region_encoded = np.random.choice(list(set(REGION_MAP.values())), size=n_samples)

    # Realistic calculation formula
    base_stay = avg_city_cost_index * total_days * 1.1
    meals = 25.0 * total_days
    noise = np.random.normal(0, 40.0, size=n_samples)

    total_cost = base_stay + total_activity_cost + meals + noise
    total_cost = np.maximum(total_cost, 100.0)

    df = pd.DataFrame({
        "total_days": total_days,
        "num_stops": num_stops,
        "num_activities": num_activities,
        "avg_city_cost_index": avg_city_cost_index,
        "total_activity_cost": total_activity_cost,
        "region_encoded": region_encoded,
        "total_cost": total_cost,
    })
    return df


def train_and_save_model(output_path: str = None) -> LinearRegression:
    """
    Trains the LinearRegression model on synthetic data and saves the model artifact using joblib.
    """
    if output_path is None:
        current_dir = Path(__file__).resolve().parent
        output_path = current_dir / "budget_model.pkl"
    else:
        output_path = Path(output_path)

    df = generate_synthetic_data(n_samples=500)
    features = ["total_days", "num_stops", "num_activities", "avg_city_cost_index", "total_activity_cost", "region_encoded"]
    X = df[features]
    y = df["total_cost"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))

    print(f"[ML Training] Budget Predictor Model Trained successfully:")
    print(f" - R² Score: {r2:.4f}")
    print(f" - RMSE: ${rmse:.2f}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, str(output_path))
    print(f" - Model artifact saved to: {output_path}")

    return model


if __name__ == "__main__":
    train_and_save_model()
