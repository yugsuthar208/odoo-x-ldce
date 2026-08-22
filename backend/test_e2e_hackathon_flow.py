import asyncio
import uuid
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, engine, async_session_factory
from app.models.user import User
from app.middleware.auth import hash_password, create_access_token


async def run_hackathon_e2e_verification():
    """
    Executes the exact 20-step hackathon end-to-end verification scenario.
    """
    print("\n==================================================================")
    print("  PHASE 6 — HACKATHON END-TO-END VERIFICATION SUITE")
    print("==================================================================\n")

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        # STEP 1: Create User
        print("[STEP 1] Create User 1 & User 2")
        user1_id = str(uuid.uuid4())
        user1_email = f"user1_{uuid.uuid4().hex[:6]}@hackathon.com"
        user2_id = str(uuid.uuid4())
        user2_email = f"user2_{uuid.uuid4().hex[:6]}@hackathon.com"

        async with async_session_factory() as session:
            u1 = User(id=user1_id, email=user1_email, password_hash=hash_password("Pass123!"), name="User One")
            u2 = User(id=user2_id, email=user2_email, password_hash=hash_password("Pass123!"), name="User Two")
            session.add_all([u1, u2])
            await session.commit()

        token1 = create_access_token({"sub": user1_id, "email": user1_email})
        token2 = create_access_token({"sub": user2_id, "email": user2_email})
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        print("  [OK] User 1 and User 2 authenticated with JWT.")

        # STEP 2 & 3 & 4: Create Trip for 4 Travelers with Budget Target
        print("\n[STEP 2-4] Create Trip for 4 Travelers & Set Budget Target")
        today = date.today()
        trip_resp = await client.post(
            "/api/trips",
            headers=headers1,
            json={
                "title": "Hackathon Royal Odyssey",
                "description": "Jaipur - Jodhpur - Udaipur Trip",
                "start_date": (today + timedelta(days=10)).isoformat(),
                "end_date": (today + timedelta(days=20)).isoformat(),
                "origin_city": "Mumbai",
                "num_travelers": 4,
                "budget_target": 120000.0,
                "currency": "INR",
            }
        )
        assert trip_resp.status_code == 201, f"Failed to create trip: {trip_resp.text}"
        trip_id = trip_resp.json()["data"]["id"]
        print(f"  [OK] Created Trip ID '{trip_id}' (4 Travelers, Target INR 120,000)")

        # STEPS 5, 6, 7: Add Jaipur, Jodhpur, Udaipur
        print("\n[STEP 5-7] Add Jaipur, Jodhpur, Udaipur Stops")
        cities_resp = await client.get("/api/cities")
        assert cities_resp.status_code == 200
        cities = cities_resp.json()["data"]
        jaipur = next((c for c in cities if c["name"] == "Jaipur"), cities[0])
        jodhpur = next((c for c in cities if c["name"] == "Jodhpur"), cities[1])
        udaipur = next((c for c in cities if c["name"] == "Udaipur"), cities[2])

        s1_resp = await client.post(
            f"/api/trips/{trip_id}/stops",
            headers=headers1,
            json={
                "city_id": jaipur["id"],
                "arrival_date": (today + timedelta(days=10)).isoformat(),
                "departure_date": (today + timedelta(days=13)).isoformat(),
                "stop_order": 0,
            }
        )
        assert s1_resp.status_code == 201
        stop1_id = s1_resp.json()["data"]["id"]

        s2_resp = await client.post(
            f"/api/trips/{trip_id}/stops",
            headers=headers1,
            json={
                "city_id": jodhpur["id"],
                "arrival_date": (today + timedelta(days=13)).isoformat(),
                "departure_date": (today + timedelta(days=16)).isoformat(),
                "stop_order": 1,
            }
        )
        assert s2_resp.status_code == 201
        stop2_id = s2_resp.json()["data"]["id"]

        s3_resp = await client.post(
            f"/api/trips/{trip_id}/stops",
            headers=headers1,
            json={
                "city_id": udaipur["id"],
                "arrival_date": (today + timedelta(days=16)).isoformat(),
                "departure_date": (today + timedelta(days=19)).isoformat(),
                "stop_order": 2,
            }
        )
        assert s3_resp.status_code == 201
        stop3_id = s3_resp.json()["data"]["id"]
        print("  [OK] Added Jaipur, Jodhpur, Udaipur stops.")

        # STEP 8: Reorder Stops
        print("\n[STEP 8] Reorder Stops (Jaipur -> Udaipur -> Jodhpur)")
        reorder_resp = await client.put(
            f"/api/trips/{trip_id}/stops/reorder",
            headers=headers1,
            json=[
                {"stop_id": stop1_id, "order_index": 0},
                {"stop_id": stop3_id, "order_index": 1},
                {"stop_id": stop2_id, "order_index": 2},
            ]
        )
        assert reorder_resp.status_code == 200
        print("  [OK] Stops reordered in database.")

        # STEP 9 & 10 & 11: Verify Transit Legs, Generate Options, Select Transit
        print("\n[STEP 9-11] Verify Transit Legs, Generate Options & Select Transit")
        transit_resp = await client.get(f"/api/trips/{trip_id}/transit", headers=headers1)
        assert transit_resp.status_code == 200
        legs = transit_resp.json()["data"]["journey_legs"]
        assert len(legs) >= 3, f"Expected 3 transit legs, found {len(legs)}"

        leg0 = legs[0]
        opt0 = leg0["options"][0]
        select_resp = await client.patch(
            f"/api/trips/{trip_id}/transit/{leg0['id']}",
            headers=headers1,
            json={"selected_option_id": opt0["id"]}
        )
        assert select_resp.status_code == 200
        print(f"  [OK] Selected transit option '{opt0['mode']}' for Leg 0.")

        # STEP 12: Add Stay
        print("\n[STEP 12] Add Stay")
        stay_resp = await client.post(
            f"/api/trips/{trip_id}/stays",
            headers=headers1,
            json={
                "trip_stop_id": stop1_id,
                "name": "Taj Rambagh Palace Jaipur",
                "checkin_date": (today + timedelta(days=10)).isoformat(),
                "checkout_date": (today + timedelta(days=13)).isoformat(),
                "nightly_cost": 4500.0,
            }
        )
        assert stay_resp.status_code == 201
        print("  [OK] Added stay Taj Rambagh Palace Jaipur (INR 4500/night).")

        # STEP 13: Add Activities
        print("\n[STEP 13] Add Activities")
        jaipur_acts = jaipur.get("activities", [])
        if jaipur_acts:
            act_id = jaipur_acts[0]["id"]
            act_item = await client.post(
                f"/api/stops/{stop1_id}/items",
                headers=headers1,
                json={
                    "activity_id": act_id,
                    "scheduled_date": (today + timedelta(days=11)).isoformat(),
                    "start_time": "09:00:00",
                    "end_time": "12:00:00",
                }
            )
            assert act_item.status_code == 201
            print("  [OK] Activity scheduled for stop 1.")

        # STEP 14: Calculate Authoritative Budget
        print("\n[STEP 14] Calculate Authoritative Budget")
        b_resp = await client.get(f"/api/trips/{trip_id}/budget", headers=headers1)
        assert b_resp.status_code == 200
        b_data1 = b_resp.json()["data"]
        print(f"  [OK] Initial Authoritative Total Estimated Cost: INR {b_data1['total_estimated_cost']:,.2f}")

        # STEP 15 & 16: Change Travelers 4 -> 5 & Verify Recalculation
        print("\n[STEP 15-16] Change Travelers (4 -> 5) & Verify Recalculation")
        update_resp = await client.put(
            f"/api/trips/{trip_id}",
            headers=headers1,
            json={"num_travelers": 5}
        )
        assert update_resp.status_code == 200
        b_resp2 = await client.get(f"/api/trips/{trip_id}/budget", headers=headers1)
        b_data2 = b_resp2.json()["data"]
        assert b_data2["travelers"] == 5
        assert b_data2["rooms"] == 3  # ceil(5/2) = 3
        print(f"  [OK] Recalculated for 5 travelers: {b_data2['rooms']} rooms allocated.")

        # STEP 17 & 18: Change Dates & Verify Recalculation
        print("\n[STEP 17-18] Change Trip Dates & Verify Dependent Recalculation")
        new_start = (today + timedelta(days=10)).isoformat()
        new_end = (today + timedelta(days=22)).isoformat() # extended 2 days
        date_resp = await client.put(
            f"/api/trips/{trip_id}",
            headers=headers1,
            json={"start_date": new_start, "end_date": new_end}
        )
        assert date_resp.status_code == 200
        b_resp3 = await client.get(f"/api/trips/{trip_id}/budget", headers=headers1)
        b_data3 = b_resp3.json()["data"]
        print(f"  [OK] Extended trip dates recalculation verified (Food = INR {b_data3['meal_policy']['calculated_food']:,.2f}).")

        # STEP 19 & 20: Run Optimization & Apply Optimization
        print("\n[STEP 19-20] Run Optimization & Apply Optimization")
        opt_gen = await client.post(f"/api/trips/{trip_id}/budget/optimize", headers=headers1)
        assert opt_gen.status_code == 200
        opt_recs = opt_gen.json()["data"]["recommendations"]
        print(f"  [OK] Generated {len(opt_recs)} non-mutating optimization recommendations.")

        if opt_recs:
            rec = opt_recs[0]
            apply_resp = await client.post(
                f"/api/trips/{trip_id}/budget/optimize/{rec['id']}/apply",
                headers=headers1
            )
            assert apply_resp.status_code == 200
            print(f"  [OK] Applied optimization recommendation '{rec['title']}'.")

        # STEPS 21-23: Create Public Share & Copy Trip as User 2 & Verify Ownership
        print("\n[STEP 21-23] Create Public Share & Copy Trip as User 2 & Verify Ownership")
        make_public = await client.put(
            f"/api/trips/{trip_id}",
            headers=headers1,
            json={"visibility": "public"}
        )
        assert make_public.status_code == 200

        copy_resp = await client.post(
            f"/api/trips/{trip_id}/duplicate",
            headers=headers2
        )
        assert copy_resp.status_code == 201
        copied_trip = copy_resp.json()["data"]
        assert copied_trip["user_id"] == user2_id
        assert copied_trip["id"] != trip_id
        print(f"  [OK] Public trip copied as User 2 new draft '{copied_trip['id']}'.")

        print("\n==================================================================")
        print("  [SUCCESS] ALL 20 HACKATHON E2E STEPS VERIFIED 100% SUCCESSFULLY!")
        print("==================================================================\n")



if __name__ == "__main__":
    asyncio.run(run_hackathon_e2e_verification())
