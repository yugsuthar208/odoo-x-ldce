import asyncio
from datetime import date, timedelta
import httpx

BASE_URL = "http://127.0.0.1:8000"


async def run_integration_tests():
    """
    Comprehensive automated integration test suite for GlobeTrotter backend platform.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("\n========================================================")
        print("[START] STARTING GLOBETROTTER API AUTOMATED TEST SUITE")
        print("========================================================\n")

        # --------------------------------------------------------------------
        # 1. HEALTH CHECK
        # --------------------------------------------------------------------
        print("[TEST 1] GET /health")
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        assert res.json()["status"] == "ok"
        print("  [PASS] Health check passed")

        # --------------------------------------------------------------------
        # 2. AUTHENTICATION & USER PROFILE
        # --------------------------------------------------------------------
        print("\n[TEST 2] POST /api/auth/login with demo user")
        login_res = await client.post(
            "/api/auth/login",
            json={"email": "demo@globetrotter.com", "password": "demo1234"},
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        demo_auth_data = login_res.json()["data"]
        token = demo_auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  [PASS] Login successful, JWT token obtained")

        print("\n[TEST 3] GET /api/users/me")
        profile_res = await client.get("/api/users/me", headers=headers)
        assert profile_res.status_code == 200
        assert profile_res.json()["data"]["email"] == "demo@globetrotter.com"
        print("  [PASS] User profile retrieved")

        print("\n[TEST 4] POST /api/auth/signup for a second collaborator user")
        collab_signup = await client.post(
            "/api/auth/signup",
            json={
                "name": "Jane Collaborator",
                "email": "jane.collab@globetrotter.com",
                "password": "collabpassword123",
                "preferred_currency": "EUR",
            },
        )
        assert collab_signup.status_code in [201, 400]
        collab_login = await client.post(
            "/api/auth/login",
            json={"email": "jane.collab@globetrotter.com", "password": "collabpassword123"},
        )
        collab_token = collab_login.json()["data"]["access_token"]
        collab_headers = {"Authorization": f"Bearer {collab_token}"}
        print("  [PASS] Second user created & authenticated for collaboration testing")

        # --------------------------------------------------------------------
        # 3. CITIES & ACTIVITIES CATALOG
        # --------------------------------------------------------------------
        print("\n[TEST 5] GET /api/cities (search and filter)")
        cities_res = await client.get("/api/cities?region=Europe")
        assert cities_res.status_code == 200
        europe_cities = cities_res.json()["data"]
        assert len(europe_cities) >= 8
        paris = next(c for c in europe_cities if c["name"] == "Paris")
        print(f"  [PASS] Found {len(europe_cities)} Europe cities, including Paris (lat={paris['latitude']}, lon={paris['longitude']})")

        print("\n[TEST 6] GET /api/cities/{id} details")
        paris_detail = await client.get(f"/api/cities/{paris['id']}")
        assert paris_detail.status_code == 200
        assert len(paris_detail.json()["data"]["activities"]) == 5
        print(f"  [PASS] Retrieved Paris details with 5 activities")

        print("\n[TEST 7] GET /api/cities/{city_id}/activities with category & max_cost filter")
        acts_res = await client.get(f"/api/cities/{paris['id']}/activities?category=sightseeing&max_cost=40")
        assert acts_res.status_code == 200
        assert len(acts_res.json()["data"]) >= 1
        print("  [PASS] Filtered city activities successfully")

        # --------------------------------------------------------------------
        # 4. TRIP CRUD & DUPLICATION
        # --------------------------------------------------------------------
        print("\n[TEST 8] POST /api/trips (create new test trip)")
        today = date.today()
        trip_payload = {
            "title": "Summer Grand Tour",
            "description": "Exploration of Paris, Rome, and Barcelona",
            "start_date": (today + timedelta(days=45)).isoformat(),
            "end_date": (today + timedelta(days=55)).isoformat(),
            "total_budget": 3000.0,
            "currency": "USD",
            "visibility": "private",
            "status": "draft",
        }
        create_trip_res = await client.post("/api/trips", json=trip_payload, headers=headers)
        assert create_trip_res.status_code == 201
        trip_id = create_trip_res.json()["data"]["id"]
        print(f"  [PASS] Created trip: '{trip_id}'")

        print("\n[TEST 9] POST /api/trips/{id}/stops (add stops)")
        rome_res = await client.get("/api/cities?search=Rome")
        rome_id = rome_res.json()["data"][0]["id"]
        bcn_res = await client.get("/api/cities?search=Barcelona")
        bcn_id = bcn_res.json()["data"][0]["id"]

        stop1_res = await client.post(
            f"/api/trips/{trip_id}/stops",
            json={
                "city_id": paris["id"],
                "arrival_date": (today + timedelta(days=45)).isoformat(),
                "departure_date": (today + timedelta(days=48)).isoformat(),
                "stop_order": 1,
                "notes": "Hotel booked near Louvre",
            },
            headers=headers,
        )
        assert stop1_res.status_code == 201
        stop1_id = stop1_res.json()["data"]["id"]

        stop2_res = await client.post(
            f"/api/trips/{trip_id}/stops",
            json={
                "city_id": rome_id,
                "arrival_date": (today + timedelta(days=48)).isoformat(),
                "departure_date": (today + timedelta(days=52)).isoformat(),
                "stop_order": 2,
            },
            headers=headers,
        )
        assert stop2_res.status_code == 201
        stop2_id = stop2_res.json()["data"]["id"]

        stop3_res = await client.post(
            f"/api/trips/{trip_id}/stops",
            json={
                "city_id": bcn_id,
                "arrival_date": (today + timedelta(days=52)).isoformat(),
                "departure_date": (today + timedelta(days=55)).isoformat(),
                "stop_order": 3,
            },
            headers=headers,
        )
        assert stop3_res.status_code == 201
        stop3_id = stop3_res.json()["data"]["id"]
        print("  [PASS] Added 3 stops to trip")

        print("\n[TEST 10] PUT /api/trips/{id}/stops/reorder (bulk reorder stops)")
        reorder_res = await client.put(
            f"/api/trips/{trip_id}/stops/reorder",
            json=[
                {"stop_id": stop3_id, "stop_order": 1},
                {"stop_id": stop1_id, "stop_order": 2},
                {"stop_id": stop2_id, "stop_order": 3},
            ],
            headers=headers,
        )
        assert reorder_res.status_code == 200
        reordered = reorder_res.json()["data"]
        assert reordered[0]["id"] == stop3_id
        # Restore normal order
        await client.put(
            f"/api/trips/{trip_id}/stops/reorder",
            json=[
                {"stop_id": stop1_id, "stop_order": 1},
                {"stop_id": stop2_id, "stop_order": 2},
                {"stop_id": stop3_id, "stop_order": 3},
            ],
            headers=headers,
        )
        print("  [PASS] Bulk stop reordering verified")

        # --------------------------------------------------------------------
        # 5. ITINERARY ITEMS & CONFLICT DETECTION
        # --------------------------------------------------------------------
        print("\n[TEST 11] POST /api/stops/{stop_id}/items (schedule activities)")
        paris_acts = paris_detail.json()["data"]["activities"]
        act1 = paris_acts[0]
        act2 = paris_acts[1]

        item1_res = await client.post(
            f"/api/stops/{stop1_id}/items",
            json={
                "activity_id": act1["id"],
                "scheduled_date": (today + timedelta(days=45)).isoformat(),
                "start_time": "10:00:00",
                "end_time": "12:30:00",
                "custom_cost": 30.0,
                "notes": "Buy tickets online",
            },
            headers=headers,
        )
        assert item1_res.status_code == 201
        item1_id = item1_res.json()["data"]["id"]

        # Intentionally schedule an overlapping item for conflict detection testing
        item2_res = await client.post(
            f"/api/stops/{stop1_id}/items",
            json={
                "activity_id": act2["id"],
                "scheduled_date": (today + timedelta(days=45)).isoformat(),
                "start_time": "11:30:00",
                "end_time": "14:00:00",
                "notes": "Overlapping Louvre visit",
            },
            headers=headers,
        )
        assert item2_res.status_code == 201
        item2_id = item2_res.json()["data"]["id"]
        print("  [PASS] Scheduled itinerary items on stop")

        print("\n[TEST 12] GET /api/trips/{id}/conflicts (detect overlapping schedules)")
        conflict_res = await client.get(f"/api/trips/{trip_id}/conflicts", headers=headers)
        assert conflict_res.status_code == 200
        conflicts = conflict_res.json()["data"]["conflicts"]
        assert len(conflicts) >= 1
        assert conflicts[0]["overlap_minutes"] == 60
        print(f"  [PASS] Successfully detected schedule conflict (overlap = {conflicts[0]['overlap_minutes']} mins)")

        print("\n[TEST 13] GET /api/trips/{id}/itinerary (day-wise grouped)")
        itin_res = await client.get(f"/api/trips/{trip_id}/itinerary", headers=headers)
        assert itin_res.status_code == 200
        itin_days = itin_res.json()["data"]["days"]
        assert len(itin_days) >= 1
        print(f"  [PASS] Day-wise itinerary retrieved ({len(itin_days)} days with scheduled events)")

        # --------------------------------------------------------------------
        # 6. AI ITINERARY GENERATOR
        # --------------------------------------------------------------------
        print("\n[TEST 14] POST /api/trips/{id}/generate-itinerary (AI Rule-Based Engine)")
        gen_res = await client.post(
            f"/api/trips/{trip_id}/generate-itinerary",
            json={
                "interests": ["sightseeing", "food", "history"],
                "pace": "moderate",
                "budget_preference": "mid-range",
                "travel_type": "couple",
            },
            headers=headers,
        )
        assert gen_res.status_code == 200
        gen_data = gen_res.json()["data"]
        assert gen_data["total_activities"] > 0
        assert len(gen_data["generated_days"]) > 0
        print(f"  [PASS] AI Engine generated {gen_data['total_activities']} activities across {len(gen_data['generated_days'])} days")

        # --------------------------------------------------------------------
        # 7. MAP ROUTE & HAVERSINE DISTANCE
        # --------------------------------------------------------------------
        print("\n[TEST 15] GET /api/trips/{id}/map-route")
        map_res = await client.get(f"/api/trips/{trip_id}/map-route", headers=headers)
        assert map_res.status_code == 200
        map_data = map_res.json()["data"]
        assert map_data["total_cities"] == 3
        assert map_data["total_distance_km"] > 1000.0  # Paris -> Rome -> Barcelona distance
        print(f"  [PASS] Map route calculated with total Haversine distance: {map_data['total_distance_km']} km")

        # --------------------------------------------------------------------
        # 8. EXPENSES MANAGEMENT
        # --------------------------------------------------------------------
        print("\n[TEST 16] POST & GET /api/trips/{id}/expenses")
        exp_res = await client.post(
            f"/api/trips/{trip_id}/expenses",
            json={
                "category": "transport",
                "description": "High speed train Paris to Rome",
                "estimated_amount": 180.0,
                "actual_amount": 165.0,
                "currency": "EUR",
            },
            headers=headers,
        )
        assert exp_res.status_code == 201
        exp_id = exp_res.json()["data"]["id"]

        list_exp_res = await client.get(f"/api/trips/{trip_id}/expenses", headers=headers)
        assert list_exp_res.status_code == 200
        assert len(list_exp_res.json()["data"]) >= 1
        print("  [PASS] Expense logged and retrieved successfully")

        # --------------------------------------------------------------------
        # 9. COLLABORATION & PERMISSION ENFORCEMENT
        # --------------------------------------------------------------------
        print("\n[TEST 17] POST /api/trips/{id}/collaborators (add editor collaborator)")
        add_collab_res = await client.post(
            f"/api/trips/{trip_id}/collaborators",
            json={"email": "jane.collab@globetrotter.com", "role": "editor"},
            headers=headers,
        )
        assert add_collab_res.status_code == 201
        collab_entry = add_collab_res.json()["data"]
        assert collab_entry["role"] == "editor"
        print("  [PASS] Collaborator added as editor")

        print("\n[TEST 18] Edit trip with collaborator token")
        collab_edit_res = await client.put(
            f"/api/trips/{trip_id}",
            json={"title": "Summer Grand Tour (Collaborator Updated)"},
            headers=collab_headers,
        )
        assert collab_edit_res.status_code == 200
        assert collab_edit_res.json()["data"]["title"] == "Summer Grand Tour (Collaborator Updated)"
        print("  [PASS] Collaborator successfully updated the trip")

        # --------------------------------------------------------------------
        # 10. PUBLIC SHARING & COPYING
        # --------------------------------------------------------------------
        print("\n[TEST 19] POST /api/trips/{id}/share (generate share link)")
        share_res = await client.post(
            f"/api/trips/{trip_id}/share",
            json={"expires_in_days": 14},
            headers=headers,
        )
        assert share_res.status_code == 201
        token_str = share_res.json()["data"]["share_token"]
        print(f"  [PASS] Share token generated: '{token_str}'")

        print("\n[TEST 20] GET /api/shared/{token} (unprotected public view)")
        public_view = await client.get(f"/api/shared/{token_str}")
        assert public_view.status_code == 200
        assert public_view.json()["data"]["title"] == "Summer Grand Tour (Collaborator Updated)"
        print("  [PASS] Public view accessed anonymously")

        print("\n[TEST 21] POST /api/shared/{token}/copy (copy shared trip to new account)")
        copy_res = await client.post(f"/api/shared/{token_str}/copy", headers=collab_headers)
        assert copy_res.status_code == 201
        copied_trip_id = copy_res.json()["data"]["id"]
        assert copied_trip_id != trip_id
        print(f"  [PASS] Shared trip copied to second account as a new draft '{copied_trip_id}'")

        # --------------------------------------------------------------------
        # 11. FAVORITES
        # --------------------------------------------------------------------
        print("\n[TEST 22] POST & GET /api/favorites")
        fav_res = await client.post(
            "/api/favorites",
            json={"city_id": paris["id"]},
            headers=headers,
        )
        assert fav_res.status_code == 201
        fav_id = fav_res.json()["data"]["id"]

        my_favs = await client.get("/api/favorites", headers=headers)
        assert my_favs.status_code == 200
        assert len(my_favs.json()["data"]) >= 1

        del_fav = await client.delete(f"/api/favorites/{fav_id}", headers=headers)
        assert del_fav.status_code == 200
        print("  [PASS] Bookmark added, retrieved, and deleted")

        # --------------------------------------------------------------------
        # 12. BUDGET ENGINE & ML RECOMMENDATIONS
        # --------------------------------------------------------------------
        print("\n[TEST 23] GET /api/trips/{id}/budget (12-step budget forecast)")
        budget_res = await client.get(f"/api/trips/{trip_id}/budget", headers=headers)
        assert budget_res.status_code == 200
        b_data = budget_res.json()["data"]
        assert "cost_breakdown" in b_data
        assert "cost_distribution_percent" in b_data
        assert "stop_breakdown" in b_data
        print(f"  [PASS] Budget calculated: Total = ${b_data['cost_breakdown']['total_cost']}, Per Day = ${b_data['per_day']['cost_per_day']}")

        print("\n[TEST 24] GET /api/recommend/cities (3-Layer Hybrid Recommender)")
        rec_cities = await client.get("/api/recommend/cities?interests=history,art&budget=3000&travel_month=6", headers=headers)
        assert rec_cities.status_code == 200
        rec_payload = rec_cities.json()["data"]
        assert "user_archetype" in rec_payload
        recommendations = rec_payload["recommendations"]
        assert len(recommendations) > 0
        assert "scores" in recommendations[0]
        assert "why_recommended" in recommendations[0]
        print(f"  [PASS] City recommendation: User Archetype='{rec_payload['user_archetype']}', Top pick='{recommendations[0]['city_name']}' (Score = {recommendations[0]['scores']['composite_score']})")

        print("\n[TEST 25] GET /api/recommend/budget/{trip_id} (XGBoost Budget Predictor)")
        ml_pred_res = await client.get(f"/api/recommend/budget/{trip_id}?accommodation_tier=mid&travel_style=explorer", headers=headers)
        assert ml_pred_res.status_code == 200
        ml_data = ml_pred_res.json()["data"]
        assert "prediction" in ml_data
        assert "predicted_total_cost" in ml_data["prediction"]
        assert "calculated_cost" in ml_data
        print(f"  [PASS] ML Prediction: Predicted = ${ml_data['prediction']['predicted_total_cost']}, Calculated = ${ml_data['calculated_cost']}")

        print("\n[TEST 26] GET /api/recommend/activities/{trip_id} (Semantic Activity Recommender)")
        act_rec_res = await client.get(f"/api/recommend/activities/{trip_id}?interests=food,culture", headers=headers)
        assert act_rec_res.status_code == 200
        act_rec_data = act_rec_res.json()["data"]
        assert "recommendations_by_stop" in act_rec_data
        print(f"  [PASS] Activity recommendations generated across {len(act_rec_data['recommendations_by_stop'])} stops")

        # --------------------------------------------------------------------
        # 13. DUPLICATION & CLEANUP
        # --------------------------------------------------------------------
        print("\n[TEST 27] POST /api/trips/{id}/duplicate & DELETE /api/trips/{id}")
        dup_res = await client.post(f"/api/trips/{trip_id}/duplicate", headers=headers)
        assert dup_res.status_code == 201
        dup_id = dup_res.json()["data"]["id"]

        del_dup = await client.delete(f"/api/trips/{dup_id}", headers=headers)
        assert del_dup.status_code == 200

        del_orig = await client.delete(f"/api/trips/{trip_id}", headers=headers)
        assert del_orig.status_code == 200
        print("  [PASS] Trip duplication and cascading deletion verified")

        print("\n========================================================")
        print("[SUCCESS] ALL 27 INTEGRATION TESTS PASSED SUCCESSFULLY (100%)!")
        print("========================================================\n")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
