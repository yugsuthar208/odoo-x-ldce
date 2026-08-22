import json
import logging
import os
import sys
from pathlib import Path

# Add backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from app.ml.data_collector import SEED_CITIES_REF, collect_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLTrainingPipeline")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PROCESSED_FILE = BASE_DIR / "data" / "processed" / "training_dataset.csv"
MODELS_DIR = Path(__file__).resolve().parent / "models"


def train_budget_model() -> XGBRegressor:
    """
    Step 2: Trains XGBRegressor on the processed travel dataset.
    """
    logger.info("==================================================")
    logger.info("🚀 STEP 2: TRAINING XGBOOST BUDGET PREDICTOR")
    logger.info("==================================================")

    if not DATA_PROCESSED_FILE.exists():
        logger.info("Processed dataset not found. Running data collection...")
        collect_data()

    df = pd.read_csv(DATA_PROCESSED_FILE)

    # Feature mapping
    season_map = {"off-peak": 0, "off_peak": 0, "shoulder": 1, "peak": 2}
    acc_map = {"budget": 0, "mid": 1, "luxury": 2}
    style_map = {"backpacker": 0, "explorer": 1, "luxury": 2}
    density_map = {"low": 0, "medium": 1, "high": 2}

    df["season_encoded"] = df["season"].map(season_map).fillna(1).astype(int)
    df["accommodation_tier_encoded"] = df["accommodation_tier"].map(acc_map).fillna(1).astype(int)
    df["travel_style_encoded"] = df["travel_style"].map(style_map).fillna(1).astype(int)
    df["activity_density_encoded"] = df["activity_density"].map(density_map).fillna(1).astype(int)

    feature_cols = [
        "cost_of_living_index", "rent_index", "restaurant_price_index",
        "travel_month", "season_encoded", "duration_days", "num_travelers",
        "accommodation_tier_encoded", "travel_style_encoded", "activity_density_encoded",
        "flight_distance_km", "num_stops"
    ]

    X = df[feature_cols]
    y = df["total_cost"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    logger.info(f"[XGBoost Evaluation Metrics]")
    logger.info(f" - MAE:  ${mae:.2f}")
    logger.info(f" - RMSE: ${rmse:.2f}")
    logger.info(f" - R²:   {r2:.4f}")

    # Feature importances
    importances = model.feature_importances_
    logger.info("[XGBoost Feature Importance Ranking]")
    sorted_idx = np.argsort(importances)[::-1]
    for idx in sorted_idx[:5]:
        logger.info(f" - {feature_cols[idx]}: {importances[idx]:.4f}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODELS_DIR / "budget_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "budget_scaler.pkl")
    logger.info("✓ Saved budget model & scaler artifacts to app/ml/models/")
    return model


def train_recommender():
    """
    Step 3: Builds SentenceTransformer semantic embeddings & KMeans traveler clusters.
    """
    logger.info("==================================================")
    logger.info("🚀 STEP 3: TRAINING HYBRID RECOMMENDER")
    logger.info("==================================================")

    from sentence_transformers import SentenceTransformer

    cache_folder = str(MODELS_DIR / "sentence_model")
    logger.info("Loading SentenceTransformer ('all-MiniLM-L6-v2')...")
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_folder)

    # City documents
    city_documents = []
    city_ids = []

    for c in SEED_CITIES_REF:
        cid = f"city_{c['city_name'].lower()}"
        doc = (
            f"{c['city_name']} is located in {c['country']}, {c['region']}. "
            f"Cost level is {c['budget_tier']}. Safety score is {c['safety_index']}/100. "
            f"Famed for scenic architecture, local cuisine, culture, and rich heritage."
        )
        city_documents.append(doc)
        city_ids.append(cid)

    logger.info(f"Encoding {len(city_documents)} city documents into 384-dim semantic embeddings...")
    embeddings = sentence_model.encode(city_documents)

    np.save(str(MODELS_DIR / "city_embeddings.npy"), embeddings)
    with open(MODELS_DIR / "city_ids.json", "w", encoding="utf-8") as f:
        json.dump(city_ids, f)

    # Train KMeans on synthetic user archetypes
    np.random.seed(42)
    user_features = np.random.uniform(50.0, 300.0, size=(500, 5))
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(user_features)

    joblib.dump(kmeans, MODELS_DIR / "kmeans_model.pkl")
    logger.info("✓ Saved city embeddings, city IDs, and KMeans model artifacts to app/ml/models/")


def validate_all_models():
    """
    Step 4: Validates that all models load and predict successfully.
    """
    logger.info("==================================================")
    logger.info("🚀 STEP 4: VALIDATING ALL ML ARTIFACTS")
    logger.info("==================================================")

    from app.ml.budget_predictor import BudgetPredictor
    from app.ml.recommender import HybridRecommender

    bp = BudgetPredictor()
    assert bp.load() is True, "BudgetPredictor failed to load"
    test_pred = bp.predict({
        "cost_of_living_index": 82.5,
        "rent_index": 52.0,
        "restaurant_price_index": 85.0,
        "travel_month": 7,
        "duration_days": 10,
        "num_travelers": 2,
        "accommodation_tier": "mid",
        "travel_style": "explorer",
        "activity_density": "medium",
        "flight_distance_km": 3000.0,
        "num_stops": 2,
    })
    logger.info(f" - Smoke Test Budget Prediction: ${test_pred['predicted_total_cost']:.2f}")

    hr = HybridRecommender()
    assert hr.load() is True, "HybridRecommender failed to load"
    test_recs = hr.recommend_cities(
        user_query={"interests": ["historic", "art"], "budget": 3000.0, "travel_month": 6},
        candidate_cities=[
            {"id": "city_paris", "name": "Paris", "country": "France", "tags": ["romantic", "art", "historic"], "cost_index": 82.5, "popularity_score": 9.8, "safety_index": 72.0, "budget_tier": "luxury", "best_months": ["June", "July"]},
            {"id": "city_prague", "name": "Prague", "country": "Czech Republic", "tags": ["historic", "gothic"], "cost_index": 51.3, "popularity_score": 8.9, "safety_index": 79.0, "budget_tier": "mid-range", "best_months": ["June", "September"]},
        ]
    )
    logger.info(f" - Smoke Test Top City Recommendation: {test_recs['recommendations'][0]['city_name']}")

    logger.info("\n==================================================")
    logger.info("🎉 ALL ML MODELS LOADED AND VALIDATED SUCCESSFULLY ✓")
    logger.info("==================================================\n")


def run_pipeline():
    """Runs full pipeline in order."""
    collect_data()
    train_budget_model()
    train_recommender()
    validate_all_models()


if __name__ == "__main__":
    run_pipeline()
