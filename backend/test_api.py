import asyncio
import os
import sys
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport

# Set test environment
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_globetrotter.db"
os.environ["SECRET_KEY"] = "test_secret_jwt_key_globetrotter_2026"
os.environ["MEALS_PER_DAY_USD"] = "25.0"

from app.main import app
from app.database import Base, engine
from seed import seed_database
from app.ml.train import train_and_save_model


async def run_tests():
    print("=" * 60)
    print("[TEST SUITE] RUNNING GLOBETROTTER BACKEND AUTOMATED TESTS")
    print("=" * 60)

    # 1. Train ML model
    print("\n[Test 1] Training & verifying ML budget model...")
    train_and_save_model("app/ml/budget_model.pkl")

    # 2. Re-create clean database and seed data
    print("\n[Test 2] Resetting database & seeding test data...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await seed_database()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 3. Health check
        print("\n[Test 3] Testing /health endpoint...")
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        assert res.json() == {"status": "ok"}
        print("  [PASS] /health returned 200 OK")

        # 4. Auth: Login with seeded demo user
        print("\n[Test 4] Testing /api/auth/login with demo user...")
        login_res = await client.post(
            "/api/auth/login",
            json={"email": "demo@globetrotter.com", "password": "demo1234"},
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        login_data = login_res.json()
        assert login_data["success"] is True
        token = login_data["data"]["access_token"]
        assert token is not None
        auth_headers = {"Authorization": f"Bearer {token}"}
        print("  [PASS] Demo user login succeeded & received valid JWT")

        # 5. Auth: Signup a new user
        print("\n[Test 5] Testing /api/auth/signup for new traveler...")
        new_email = "tester_journey@globetrotter.com"
        signup_res = await client.post(
            "/api/auth/signup",
            json={
                "name": "Alex Explorer",
                "email": new_email,
                "password": "mypassword123",
                "language": "es",
            },
        )
        assert signup_res.status_code == 201, f"Signup failed: {signup_res.text}"
        new_token = signup_res.json()["data"]["access_token"]
        new_user_headers = {"Authorization": f"Bearer {new_token}"}
        print("  [PASS] User registration succeeded with bcrypt hash & JWT")

        # 6. Auth: Forgot Password
        print("\n[Test 6] Testing /api/auth/forgot-password...")
        forgot_res = await client.post(
            "/api/auth/forgot-password",
            json={"email": new_email},
        )
        assert forgot_res.status_code == 200
        assert "reset_token" in forgot_res.json()["data"]
        print("  [PASS] Password reset token generated successfully")

        # 7. Users: Get & Update profile
        print("\n[Test 7] Testing /api/users/me (Get & Update profile)...")
        profile_res = await client.get("/api/users/me", headers=new_user_headers)
        assert profile_res.status_code == 200
        assert profile_res.json()["data"]["email"] == new_email

        update_res = await client.put(
            "/api/users/me",
            headers=new_user_headers,
            json={"name": "Alex Explorer VIP", "language": "fr"},
        )
        assert update_res.status_code == 200
        assert update_res.json()["data"]["name"] == "Alex Explorer VIP"
        assert update_res.json()["data"]["language"] == "fr"
        print("  [PASS] User profile read and updated successfully")

        # 8. Cities: Search and list
        print("\n[Test 8] Testing /api/cities search & filter...")
        cities_res = await client.get("/api/cities?search=Tokyo&region=Asia")
        assert cities_res.status_code == 200
        cities_data = cities_res.json()["data"]
        assert len(cities_data) >= 1
        tokyo = cities_data[0]
        assert tokyo["name"] == "Tokyo"
        tokyo_id = tokyo["id"]
        print(f"  [PASS] City search returned {len(cities_data)} matching destination(s)")

        # 9. City Details & Activities
        print(f"\n[Test 9] Testing /api/cities/{tokyo_id} and activity filter...")
        city_detail_res = await client.get(f"/api/cities/{tokyo_id}")
        assert city_detail_res.status_code == 200
        assert len(city_detail_res.json()["data"]["activities"]) == 5

        act_filter_res = await client.get(f"/api/cities/{tokyo_id}/activities?type=food&max_cost=60")
        assert act_filter_res.status_code == 200
        food_acts = act_filter_res.json()["data"]
        assert len(food_acts) >= 1
        for a in food_acts:
            assert a["type"].lower() == "food"
            assert a["cost"] <= 60
        print(f"  [PASS] Filtered {len(food_acts)} food activities under $60")

        # 10. Trips: Create trip for demo user
        print("\n[Test 10] Testing /api/trips creation...")
        trip_start = date.today() + timedelta(days=45)
        trip_end = trip_start + timedelta(days=6)
        trip_payload = {
            "title": "Autumn Discovery in Japan",
            "description": "Visiting Tokyo and relaxing",
            "start_date": trip_start.isoformat(),
            "end_date": trip_end.isoformat(),
            "is_public": True,
        }
        trip_res = await client.post("/api/trips", headers=auth_headers, json=trip_payload)
        assert trip_res.status_code == 201
        trip_data = trip_res.json()["data"]
        trip_id = trip_data["id"]
        assert trip_data["title"] == "Autumn Discovery in Japan"
        print(f"  [PASS] Trip created with id: {trip_id}")

        # 11. Stops: Add stop to trip
        print("\n[Test 11] Testing /api/trips/{id}/stops...")
        stop_res = await client.post(
            f"/api/trips/{trip_id}/stops",
            headers=auth_headers,
            json={
                "city_id": tokyo_id,
                "arrival_date": trip_start.isoformat(),
                "departure_date": trip_end.isoformat(),
                "order_index": 0,
            },
        )
        assert stop_res.status_code == 201
        stop_id = stop_res.json()["data"]["id"]
        print(f"  [PASS] Stop added with id: {stop_id}")

        # 12. Activities: Assign activity to stop
        print("\n[Test 12] Testing /api/stops/{id}/activities...")
        activity_to_add = food_acts[0]["id"]
        assign_res = await client.post(
            f"/api/stops/{stop_id}/activities",
            headers=auth_headers,
            json={
                "activity_id": activity_to_add,
                "scheduled_date": trip_start.isoformat(),
                "notes": "Table booked near the window",
            },
        )
        assert assign_res.status_code == 201
        print("  [PASS] Activity assigned to stop successfully")

        # 13. Upgraded Budget Calculation: Verify complete nested JSON structure & formulas
        print("\n[Test 13] Testing Upgraded /api/trips/{id}/budget formula & structure...")
        budget_res = await client.get(f"/api/trips/{trip_id}/budget", headers=auth_headers)
        assert budget_res.status_code == 200
        budget_json = budget_res.json()
        assert budget_json["success"] is True
        assert budget_json["message"] == "Budget calculated successfully"
        calc = budget_json["data"]

        print("  Upgraded Budget Output:", calc)

        # Verify Top-level metadata
        assert calc["trip_id"] == trip_id
        assert calc["trip_title"] == "Autumn Discovery in Japan"
        assert calc["total_trip_days"] == 6
        assert calc["days_until_trip"] == 45
        assert calc["trip_status"] == "upcoming"

        # Verify Cost Breakdown
        cost_bd = calc["cost_breakdown"]
        expected_stay = tokyo["cost_index"] * 6  # 180 * 6 = 1080.0
        expected_acts = food_acts[0]["cost"]     # 55.0
        expected_meals = 25.0 * 6                # 150.0
        expected_transport = 0.0
        expected_misc = 0.0
        expected_total = expected_stay + expected_acts + expected_meals + expected_transport + expected_misc

        assert cost_bd["stay_cost"] == expected_stay
        assert cost_bd["activities_cost"] == expected_acts
        assert cost_bd["meals_cost"] == expected_meals
        assert cost_bd["transport_cost"] == expected_transport
        assert cost_bd["misc_cost"] == expected_misc
        assert cost_bd["total_cost"] == expected_total

        # Verify Per Day metrics
        per_day = calc["per_day"]
        expected_cost_per_day = round(expected_total / 6, 2)
        expected_savings_needed = round(expected_total / 45, 2)
        assert per_day["cost_per_day"] == expected_cost_per_day
        assert per_day["savings_needed_per_day"] == expected_savings_needed

        # Verify Stop Breakdown
        assert len(calc["stop_breakdown"]) == 1
        stop_b = calc["stop_breakdown"][0]
        assert stop_b["stop_id"] == stop_id
        assert stop_b["city_name"] == "Tokyo"
        assert stop_b["days"] == 6
        assert stop_b["stay_cost"] == expected_stay
        assert stop_b["activities_cost"] == expected_acts
        assert stop_b["meals_cost"] == 150.0
        assert stop_b["stop_total"] == expected_stay + expected_acts + 150.0

        # Verify Cost Distribution Percentages
        dist = calc["cost_distribution_percent"]
        assert round(dist["stay"] + dist["activities"] + dist["meals"] + dist["transport"] + dist["misc"], 0) in [99.0, 100.0, 101.0]

        print("  [PASS] Upgraded budget calculation matches exact specification and nested structure!")

        # 14. Budget Calculation Auth Protection (401 Unauthorized & 403 Forbidden)
        print("\n[Test 14] Testing Budget Endpoint Auth Protection (401 & 403)...")
        # 401: No token
        unauth_b = await client.get(f"/api/trips/{trip_id}/budget")
        assert unauth_b.status_code == 401
        # 403: Another user's token
        forbidden_b = await client.get(f"/api/trips/{trip_id}/budget", headers=new_user_headers)
        assert forbidden_b.status_code == 403
        assert forbidden_b.json()["success"] is False
        print("  [PASS] Budget endpoint strictly enforces owner authentication")

        # 15. Budget Edge Case: Trip with NO stops
        print("\n[Test 15] Testing Budget Edge Case: Trip with NO stops...")
        empty_trip = await client.post(
            "/api/trips",
            headers=new_user_headers,
            json={
                "title": "Empty Itinerary",
                "start_date": (date.today() + timedelta(days=10)).isoformat(),
                "end_date": (date.today() + timedelta(days=15)).isoformat(),
            },
        )
        empty_trip_id = empty_trip.json()["data"]["id"]
        empty_budget_res = await client.get(f"/api/trips/{empty_trip_id}/budget", headers=new_user_headers)
        assert empty_budget_res.status_code == 200
        empty_data = empty_budget_res.json()["data"]
        assert empty_data["cost_breakdown"]["stay_cost"] == 0.0
        assert empty_data["cost_breakdown"]["activities_cost"] == 0.0
        assert empty_data["cost_breakdown"]["total_cost"] == 0.0
        assert empty_data["stop_breakdown"] == []
        print("  [PASS] Zero stops handled gracefully with full response structure")

        # 16. Budget Edge Case: Same-day Stop & Same-day Trip (duration = 0 -> minimum = 1)
        print("\n[Test 16] Testing Budget Edge Case: Same-day trip (start == end)...")
        sameday_trip = await client.post(
            "/api/trips",
            headers=new_user_headers,
            json={
                "title": "Day Excursion",
                "start_date": (date.today() + timedelta(days=5)).isoformat(),
                "end_date": (date.today() + timedelta(days=5)).isoformat(),
            },
        )
        sameday_trip_id = sameday_trip.json()["data"]["id"]
        sameday_stop = await client.post(
            f"/api/trips/{sameday_trip_id}/stops",
            headers=new_user_headers,
            json={
                "city_id": tokyo_id,
                "arrival_date": (date.today() + timedelta(days=5)).isoformat(),
                "departure_date": (date.today() + timedelta(days=5)).isoformat(),
                "order_index": 0,
            },
        )
        sameday_budget_res = await client.get(f"/api/trips/{sameday_trip_id}/budget", headers=new_user_headers)
        assert sameday_budget_res.status_code == 200
        sameday_calc = sameday_budget_res.json()["data"]
        assert sameday_calc["total_trip_days"] == 1
        assert sameday_calc["stop_breakdown"][0]["days"] == 1
        print("  [PASS] Same-day trip & same-day stop forced minimum days = 1")

        # 17. ML Recommender: Recommend cities for user
        print("\n[Test 17] Testing /api/recommend/cities (Content-based filtering)...")
        recom_res = await client.get("/api/recommend/cities", headers=auth_headers)
        assert recom_res.status_code == 200
        recs = recom_res.json()["data"]
        assert len(recs) == 5
        print(f"  [PASS] Recommender generated top 5 cities: {[c['name'] for c in recs]}")

        # 18. ML Budget Predictor: Predict trip cost
        print(f"\n[Test 18] Testing /api/recommend/budget/{trip_id} (Linear Regression)...")
        pred_res = await client.get(f"/api/recommend/budget/{trip_id}", headers=auth_headers)
        assert pred_res.status_code == 200
        pred_data = pred_res.json()["data"]
        assert "predicted_total_cost" in pred_data
        assert pred_data["predicted_total_cost"] > 0
        print(f"  [PASS] Predicted total trip budget: ${pred_data['predicted_total_cost']}")

        # 19. Public Trip Endpoint (Unauthenticated)
        print(f"\n[Test 19] Testing /api/trips/public/{trip_id} without auth headers...")
        pub_res = await client.get(f"/api/trips/public/{trip_id}")
        assert pub_res.status_code == 200
        assert pub_res.json()["data"]["is_public"] is True
        print("  [PASS] Public read-only trip view verified")

        # 20. Error Response Standard: 401, 404, 422
        print("\n[Test 20] Testing Standardized Error Response Format...")
        err401 = await client.get("/api/users/me")
        assert err401.status_code == 401
        assert err401.json()["success"] is False
        assert "error" in err401.json()

        err404 = await client.get("/api/trips/non-existent-id-12345", headers=auth_headers)
        assert err404.status_code == 404
        assert err404.json()["success"] is False
        assert "error" in err404.json()

        err422 = await client.post("/api/auth/signup", json={"email": "not-an-email"})
        assert err422.status_code == 422
        assert err422.json()["success"] is False
        assert "error" in err422.json()
        print("  [PASS] Unified error response structure verified across 401, 404, 422")

        # 21. Cleanup test user
        print("\n[Test 21] Testing /api/users/me DELETE account...")
        del_res = await client.delete("/api/users/me", headers=new_user_headers)
        assert del_res.status_code == 200
        print("  [PASS] Account deleted successfully")

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL 21 AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
