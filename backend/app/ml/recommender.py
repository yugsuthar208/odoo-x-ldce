from typing import List, Set
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ml.train import encode_region
from app.models.city import City
from app.models.stop import TripStop
from app.models.trip import Trip
from app.models.user import User


async def recommend_cities_for_user(
    db: AsyncSession,
    current_user: User,
    top_n: int = 5,
) -> dict:
    """
    Recommends cities using content-based filtering + cosine similarity:
    1. Loads current_user's past trips -> extracts all cities visited.
    2. Builds city feature matrix: [cost_index, popularity_score, region_encoded, lat_normalized, lng_normalized].
    3. For cities user HAS visited -> computes average feature vector.
    4. For cities user has NOT visited -> computes cosine similarity to that average vector.
    5. Returns top 5 cities sorted by similarity score descending with personalized reasoning.
    6. If user has no trips yet -> returns top 5 by popularity_score.
    """
    # 1. Fetch all cities
    result_cities = await db.execute(select(City))
    all_cities = list(result_cities.scalars().all())

    if not all_cities:
        return {"recommendations": []}

    # 2. Extract visited cities from user's trips
    result_trips = await db.execute(
        select(Trip)
        .options(selectinload(Trip.stops))
        .where(Trip.user_id == current_user.id)
    )
    user_trips = list(result_trips.scalars().all())

    visited_city_ids: Set[str] = set()
    for trip in user_trips:
        for stop in trip.stops:
            if stop.city_id:
                visited_city_ids.add(stop.city_id)

    # 3. Fallback: If user has no trips or visited cities yet, return top 5 by popularity
    if not visited_city_ids:
        sorted_by_pop = sorted(all_cities, key=lambda c: c.popularity_score, reverse=True)[:top_n]
        recs = [
            {
                "city_id": c.id,
                "city_name": c.name,
                "country": c.country,
                "similarity_score": 1.0,
                "reason": "Top trending destination worldwide",
                "cost_index": c.cost_index,
                "popularity_score": c.popularity_score,
            }
            for c in sorted_by_pop
        ]
        return {"recommendations": recs}

    # 4. Filter unvisited cities
    unvisited_cities = [c for c in all_cities if c.id not in visited_city_ids]
    if not unvisited_cities:
        unvisited_cities = all_cities

    # 5. Build feature matrix for all cities
    city_data = []
    for c in all_cities:
        city_data.append({
            "id": c.id,
            "cost_index": c.cost_index,
            "popularity_score": c.popularity_score,
            "region_encoded": float(encode_region(c.region or "")),
            "lat": c.latitude or 0.0,
            "lng": c.longitude or 0.0,
        })

    df = pd.DataFrame(city_data)
    feature_cols = ["cost_index", "popularity_score", "region_encoded", "lat", "lng"]

    scaler = MinMaxScaler()
    df_scaled = df.copy()
    df_scaled[feature_cols] = scaler.fit_transform(df[feature_cols])
    df_scaled.set_index("id", inplace=True)

    # Extract visited vectors and average
    valid_visited = [cid for cid in visited_city_ids if cid in df_scaled.index]
    if not valid_visited:
        valid_visited = [all_cities[0].id]

    visited_vectors = df_scaled.loc[valid_visited]
    user_profile_vector = visited_vectors.values.mean(axis=0).reshape(1, -1)

    # Unvisited matrix
    unvisited_ids = [c.id for c in unvisited_cities]
    unvisited_matrix = df_scaled.loc[unvisited_ids].values

    # 6. Compute Cosine Similarity
    similarities = cosine_similarity(user_profile_vector, unvisited_matrix)[0]

    city_map = {c.id: c for c in unvisited_cities}
    ranked_indices = np.argsort(similarities)[::-1]

    recommendations = []
    for idx in ranked_indices[:top_n]:
        cid = unvisited_ids[idx]
        c = city_map[cid]
        score = float(round(similarities[idx], 2))
        recommendations.append({
            "city_id": c.id,
            "city_name": c.name,
            "country": c.country,
            "similarity_score": score,
            "reason": f"Similar travel style and cost index to destinations in your past trips",
            "cost_index": c.cost_index,
            "popularity_score": c.popularity_score,
        })

    return {"recommendations": recommendations}
