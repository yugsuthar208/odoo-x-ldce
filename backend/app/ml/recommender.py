from typing import List, Set
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.city import City
from app.models.stop import Stop
from app.models.trip import Trip
from app.models.user import User

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
    """Helper to convert region text into numeric encoding."""
    if not region:
        return 0
    for key, val in REGION_MAP.items():
        if key.lower() in region.lower():
            return val
    return 0


async def recommend_cities_for_user(
    db: AsyncSession,
    current_user: User,
    top_n: int = 5,
) -> List[City]:
    """
    Recommends cities using content-based filtering and cosine similarity:
    1. Extracts all cities visited across past trips of the user.
    2. Builds normalized feature vectors: [cost_index, popularity_score, region_encoded].
    3. Computes cosine similarity between user profile (visited cities) and unvisited cities.
    4. Returns the top 5 most similar unvisited cities.
    5. Falls back to top cities by popularity_score if user has no past trip history.
    """
    # 1. Fetch all cities from DB
    result_cities = await db.execute(select(City))
    all_cities = list(result_cities.scalars().all())

    if not all_cities:
        return []

    # 2. Extract visited city IDs from user trips
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

    # 3. Fallback: If user hasn't visited any cities, return top by popularity_score
    if not visited_city_ids:
        sorted_by_pop = sorted(all_cities, key=lambda c: c.popularity_score, reverse=True)
        return sorted_by_pop[:top_n]

    # 4. Filter unvisited cities
    unvisited_cities = [c for c in all_cities if c.id not in visited_city_ids]
    visited_cities = [c for c in all_cities if c.id in visited_city_ids]

    # If all cities were visited, return top by popularity from all
    if not unvisited_cities:
        return sorted(all_cities, key=lambda c: c.popularity_score, reverse=True)[:top_n]

    # 5. Build feature matrix for all cities
    city_data = []
    for c in all_cities:
        city_data.append({
            "id": c.id,
            "cost_index": c.cost_index,
            "popularity_score": c.popularity_score,
            "region_encoded": float(encode_region(c.region)),
        })

    df = pd.DataFrame(city_data)
    feature_cols = ["cost_index", "popularity_score", "region_encoded"]

    # Normalize features
    scaler = MinMaxScaler()
    df_scaled = df.copy()
    df_scaled[feature_cols] = scaler.fit_transform(df[feature_cols])

    # Index by ID
    df_scaled.set_index("id", inplace=True)

    # Build user preference vector: average of visited cities vectors
    visited_vectors = df_scaled.loc[list(visited_city_ids)]
    user_profile_vector = visited_vectors.values.mean(axis=0).reshape(1, -1)

    # Build unvisited cities matrix
    unvisited_ids = [c.id for c in unvisited_cities]
    unvisited_matrix = df_scaled.loc[unvisited_ids].values

    # 6. Compute Cosine Similarity
    similarities = cosine_similarity(user_profile_vector, unvisited_matrix)[0]

    # 7. Rank and select top N
    city_map = {c.id: c for c in unvisited_cities}
    ranked_indices = np.argsort(similarities)[::-1]

    top_recommended = []
    for idx in ranked_indices[:top_n]:
        cid = unvisited_ids[idx]
        top_recommended.append(city_map[cid])

    return top_recommended
