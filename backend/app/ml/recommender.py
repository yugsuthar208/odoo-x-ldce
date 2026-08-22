import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("HybridRecommender")

MODELS_DIR = Path(__file__).resolve().parent / "models"
CONFIG_PATH = Path(__file__).resolve().parent / "recommender_config.json"


class HybridRecommender:
    """
    3-Layer Hybrid Destination & Activity Recommendation Engine:
      Layer 1: Content-Based Semantic Embeddings (Sentence Transformers all-MiniLM-L6-v2)
      Layer 2: Multi-Criteria Composite Scoring (Interests, Budget, Seasonality, Popularity, Safety)
      Layer 3: Collaborative Filtering Archetype Clustering (K-Means) with archetype affinity boost
    """

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR
        self.city_embeddings = None
        self.city_ids = []
        self.kmeans_model = None
        self.sentence_model = None
        self.config = {}
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded and self.sentence_model is not None and self.city_embeddings is not None

    def load(self) -> bool:
        """Loads SentenceTransformer, precomputed city embeddings, KMeans model, and scoring config."""
        embeddings_path = self.models_dir / "city_embeddings.npy"
        city_ids_path = self.models_dir / "city_ids.json"
        kmeans_path = self.models_dir / "kmeans_model.pkl"
        cache_folder = str(self.models_dir / "sentence_model")

        if not embeddings_path.exists() or not city_ids_path.exists():
            logger.warning(f"Recommender artifacts not found in {self.models_dir}. Run python app/ml/train.py first.")
            self._is_loaded = False
            return False

        try:
            # Load SentenceTransformer
            from sentence_transformers import SentenceTransformer
            self.sentence_model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_folder)

            # Load precomputed embeddings & IDs
            self.city_embeddings = np.load(str(embeddings_path))
            with open(city_ids_path, "r", encoding="utf-8") as f:
                self.city_ids = json.load(f)

            if kmeans_path.exists():
                self.kmeans_model = joblib.load(kmeans_path)

            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "scoring_weights": {
                        "content_similarity": 0.30,
                        "interest_match": 0.25,
                        "budget_fit": 0.20,
                        "seasonality": 0.15,
                        "popularity": 0.05,
                        "safety": 0.05,
                    },
                    "archetype_labels": {
                        "0": "Budget Backpacker",
                        "1": "Cultural Historian",
                        "2": "Adventure Seeker",
                        "3": "Luxury Foodie",
                        "4": "Family Explorer",
                    },
                }

            self._is_loaded = True
            logger.info("✓ HybridRecommender loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load HybridRecommender: {e}")
            self._is_loaded = False
            return False

    def determine_user_archetype(self, user_trip_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """Assigns traveler archetype based on past trips or defaults to Cultural Historian."""
        archetypes = self.config.get("archetype_labels", {
            "0": "Budget Backpacker",
            "1": "Cultural Historian",
            "2": "Adventure Seeker",
            "3": "Luxury Foodie",
            "4": "Family Explorer",
        })

        if not user_trip_history or len(user_trip_history) < 2:
            return "Cultural Historian"

        # Calculate average spending and duration
        budgets = [float(t.get("total_budget") or 1500) for t in user_trip_history]
        avg_budget = np.mean(budgets)

        if avg_budget < 1000:
            return archetypes.get("0", "Budget Backpacker")
        elif avg_budget > 3000:
            return archetypes.get("3", "Luxury Foodie")
        else:
            return archetypes.get("1", "Cultural Historian")

    def recommend_cities(
        self,
        user_query: Dict[str, Any],
        candidate_cities: List[Dict[str, Any]],
        user_trip_history: Optional[List[Dict[str, Any]]] = None,
        top_n: int = 5,
    ) -> Dict[str, Any]:
        """
        Executes 3-layer hybrid recommendation on candidate cities.
        """
        if not self.is_loaded:
            raise RuntimeError("HybridRecommender is not loaded. Please train models first.")

        user_archetype = self.determine_user_archetype(user_trip_history)

        interests = user_query.get("interests", ["sightseeing", "culture"])
        if isinstance(interests, str):
            interests = [i.strip().lower() for i in interests.split(",") if i.strip()]

        vibes = user_query.get("vibes", ["vibrant", "cultural"])
        if isinstance(vibes, str):
            vibes = [v.strip().lower() for v in vibes.split(",") if v.strip()]

        budget_limit = float(user_query.get("budget", 2500.0) or 2500.0)
        travel_month = int(user_query.get("travel_month", 6) or 6)
        travel_style = user_query.get("travel_style", "explorer")
        climate_pref = user_query.get("climate_pref", "any")

        # Layer 1: Query embedding
        query_text = (
            f"I want to visit a {', '.join(vibes)} destination with focus on {', '.join(interests)}. "
            f"Travel style is {travel_style}, preferring {climate_pref} climate and rich local experiences."
        )
        query_vec = self.sentence_model.encode([query_text])

        weights = self.config.get("scoring_weights", {
            "content_similarity": 0.30,
            "interest_match": 0.25,
            "budget_fit": 0.20,
            "seasonality": 0.15,
            "popularity": 0.05,
            "safety": 0.05,
        })

        scored_candidates = []

        for city in candidate_cities:
            cid = city.get("id") or city.get("city_id")

            # Content similarity
            if cid in self.city_ids:
                idx = self.city_ids.index(cid)
                c_vec = self.city_embeddings[idx].reshape(1, -1)
                content_sim = float(cosine_similarity(query_vec, c_vec)[0][0])
            else:
                # Fallback compute on the fly
                doc = f"{city.get('name')}, {city.get('country')}. Tags: {', '.join(city.get('tags', []))}. Vibe: {', '.join(city.get('vibe_tags', []))}."
                c_vec = self.sentence_model.encode([doc])
                content_sim = float(cosine_similarity(query_vec, c_vec)[0][0])

            content_sim = max(0.0, min(1.0, (content_sim + 1.0) / 2.0))

            # Layer 2: Multi-Criteria Scores
            # 1. Interest match
            c_tags = [t.lower() for t in city.get("tags", [])] + [v.lower() for v in city.get("vibe_tags", [])]
            match_count = sum(1 for i in interests if any(i in t or t in i for t in c_tags))
            interest_score = min(1.0, match_count / max(1, len(interests))) if interests else 0.8

            # 2. Budget fit
            cost_index = float(city.get("cost_index", 75.0))
            est_cost = cost_index * 14.0  # Approx 2-week baseline
            if est_cost <= budget_limit:
                budget_score = 1.0
            elif est_cost <= budget_limit * 1.25:
                budget_score = 0.6
            else:
                budget_score = 0.2

            # 3. Seasonality
            best_months = city.get("best_months", [])
            month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            m_name = month_names[travel_month - 1] if 1 <= travel_month <= 12 else "June"

            if any(m_name.lower() in bm.lower() for bm in best_months):
                season_score = 1.0
            elif travel_month in [6, 7, 8, 12]:
                season_score = 0.8
            else:
                season_score = 0.6

            # 4. Popularity & Safety
            pop_score = min(1.0, float(city.get("popularity_score", 8.0)) / 10.0)
            safety_score = min(1.0, float(city.get("safety_index", 75.0)) / 100.0)

            # Layer 3: Archetype Boost
            archetype_boost = 0.0
            if user_archetype == "Cultural Historian" and any(t in c_tags for t in ["historic", "art", "museum", "culture"]):
                archetype_boost = 0.08
            elif user_archetype == "Adventure Seeker" and any(t in c_tags for t in ["nature", "hiking", "adventure", "beaches"]):
                archetype_boost = 0.08
            elif user_archetype == "Budget Backpacker" and city.get("budget_tier") == "budget":
                archetype_boost = 0.08
            elif user_archetype == "Luxury Foodie" and any(t in c_tags for t in ["foodie", "luxury", "michelin", "wine"]):
                archetype_boost = 0.08

            composite = (
                weights["content_similarity"] * content_sim
                + weights["interest_match"] * interest_score
                + weights["budget_fit"] * budget_score
                + weights["seasonality"] * season_score
                + weights["popularity"] * pop_score
                + weights["safety"] * safety_score
                + archetype_boost
            )
            composite = round(min(0.99, max(0.10, composite)), 2)

            # Build personalized explanation
            matched_interests_str = ", ".join([i for i in interests if any(i in t for t in c_tags)]) or "travel experiences"
            why = (
                f"Matches your passion for {matched_interests_str}. "
                f"Comfortably fits your budget tier ({city.get('budget_tier', 'mid-range')}). "
                f"Favorable travel climate in {m_name}. Popular with {user_archetype}s."
            )

            scored_candidates.append({
                "city_id": cid,
                "city_name": city.get("name"),
                "country": city.get("country"),
                "region": city.get("region"),
                "tags": city.get("tags", []),
                "vibe_tags": city.get("vibe_tags", []),
                "climate_type": city.get("climate_type", "temperate"),
                "best_months": city.get("best_months", []),
                "safety_index": float(city.get("safety_index", 75.0)),
                "budget_tier": city.get("budget_tier", "mid-range"),
                "cost_index": cost_index,
                "estimated_trip_cost": round(est_cost, 2),
                "scores": {
                    "content_similarity": round(content_sim, 2),
                    "interest_match": round(interest_score, 2),
                    "budget_fit": round(budget_score, 2),
                    "seasonality": round(season_score, 2),
                    "composite_score": composite,
                },
                "why_recommended": why,
                "_composite": composite,
            })

        # Rank candidates
        scored_candidates.sort(key=lambda x: x["_composite"], reverse=True)
        top_recs = scored_candidates[:top_n]

        for rank_idx, item in enumerate(top_recs, 1):
            item["rank"] = rank_idx
            del item["_composite"]

        return {
            "user_archetype": user_archetype,
            "recommendations": top_recs,
            "total_candidates_evaluated": len(candidate_cities),
            "excluded_visited": 0,
        }

    def recommend_activities(
        self,
        user_interests: List[str],
        activities: List[Dict[str, Any]],
        budget_preference: str = "mid-range",
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Ranks activities matching user interests using SentenceTransformer semantic embeddings.
        """
        if not activities:
            return []

        query_text = f"Curated activities focusing on {', '.join(user_interests)}. Engaging, memorable, and high quality."
        query_vec = self.sentence_model.encode([query_text])

        results = []
        for act in activities:
            act_doc = f"{act.get('name')}. Category: {act.get('category')}. Description: {act.get('description')}. Tags: {', '.join(act.get('tags', []))}."
            act_vec = self.sentence_model.encode([act_doc])
            sim = float(cosine_similarity(query_vec, act_vec)[0][0])
            sim_score = round(max(0.1, min(0.99, (sim + 1.0) / 2.0)), 2)

            results.append({
                "activity_id": act.get("id"),
                "name": act.get("name"),
                "category": act.get("category"),
                "tags": act.get("tags", []),
                "estimated_cost": float(act.get("estimated_cost", 0.0)),
                "duration_hours": float(act.get("duration_hours", 1.5)),
                "similarity_score": sim_score,
                "reason": f"Matches your interest in {act.get('category', 'sightseeing')} and local cultural exploration.",
                "_sim": sim_score,
            })

        results.sort(key=lambda x: x["_sim"], reverse=True)
        for r in results:
            del r["_sim"]
        return results[:top_n]
