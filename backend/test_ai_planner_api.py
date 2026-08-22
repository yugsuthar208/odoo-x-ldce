import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000/api"

async def test_ai_planner_flow():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Login to get token
        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "qa_auto@tripora.com",
            "password": "QATest123!"
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(" [PASS] User authenticated successfully.")

        # 2. Generate Master AI Plan
        print(" -> Requesting AI Master Plan Generation...")
        gen_payload = {
            "origin_city": "Mumbai",
            "destination_input": "Gandhinagar, Udaipur",
            "duration_days": 4,
            "travelers": 2,
            "budget_tier": "mid",
            "travel_style": "cultural",
            "transit_preference": "train",
            "dietary_preference": "authentic_regional",
            "interests": ["heritage", "food", "sightseeing"]
        }
        gen_res = await client.post(f"{BASE_URL}/ai-planner/generate", json=gen_payload, headers=headers)
        assert gen_res.status_code == 200, f"Generate failed: {gen_res.text}"
        data = gen_res.json()["data"]
        
        print(" [PASS] AI Blueprint Generated:")
        print(f"   Title: {data['trip_title'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"   Tagline: {data['tagline'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"   Days count: {len(data['itinerary_days'])}")
        print(f"   Culinary guides count: {len(data['culinary_guides'])}")
        print(f"   Total cost est: INR {data['budget_summary']['total_estimated_cost']}")
        
        # Verify Day 1 Schedule
        day1 = data["itinerary_days"][0]
        print(f"   Day 1 theme: {day1['theme'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"   Day 1 schedule items: {len(day1['schedule'])}")
        for item in day1["schedule"][:2]:
            print(f"     - [{item['time_slot']}] {item['title'].encode('ascii', 'ignore').decode('ascii')} (INR {item['estimated_cost_inr']})")

        # 3. 1-Click Save to Database
        print(" -> Saving AI Blueprint as an active Database Trip...")
        save_res = await client.post(f"{BASE_URL}/ai-planner/save-trip", json={"ai_blueprint": data}, headers=headers)
        assert save_res.status_code == 201, f"Save trip failed: {save_res.text}"
        save_data = save_res.json()["data"]
        trip_id = save_data["trip_id"]
        print(f" [PASS] Trip successfully saved to database with ID: {trip_id}")

        # 4. Fetch the newly saved trip via standard /trips/{id} endpoint
        trip_res = await client.get(f"{BASE_URL}/trips/{trip_id}", headers=headers)
        assert trip_res.status_code == 200, f"Get saved trip failed: {trip_res.text}"
        trip_detail = trip_res.json()["data"]
        print(f" [PASS] Fetched saved trip from DB:")
        print(f"   Stops: {len(trip_detail['stops'])}")
        print(f"   Transit Legs: {len(trip_detail.get('transit_legs', []))}")
        b_val = trip_detail.get('budget', {}).get('total_estimated_cost') or trip_detail.get('budget', {}).get('total_budget_limit') or trip_detail.get('total_budget')
        print(f"   Budget Total: INR {b_val}")
        print("\n ALL AI PLANNER TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    asyncio.run(test_ai_planner_flow())
