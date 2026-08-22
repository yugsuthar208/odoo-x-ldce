"""
GlobeTrotter Full-Stack QA Test Script
Tests every major API endpoint and reports pass/fail.
"""
import asyncio
import json
import urllib.request
import urllib.error
import sqlite3

BASE = "http://127.0.0.1:8000/api"
TOKEN = None
TRIP_ID = None
STOP_ID = None
EXPENSE_ID = None

RESULTS = []

def req(method, path, data=None, auth=True):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if auth and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = json.dumps(data).encode() if data else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(request, timeout=10)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read())
        except:
            err_body = str(e)
        return e.code, err_body

def test(name, status, body, expect_status=200, check_key=None):
    ok = status == expect_status
    if check_key and ok:
        ok = check_key in str(body)
    status_str = "PASS" if ok else "FAIL"
    RESULTS.append((name, status_str, status, str(body)[:120]))
    print(f"  [{status_str}] {name} -> HTTP {status}")
    if not ok:
        print(f"         Body: {str(body)[:200]}")
    return ok, body

# ============================================================
# DB CHECK
# ============================================================
print("\n=== DATABASE INSPECTION ===")
conn = sqlite3.connect("globetrotter.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables: {tables}")
cur.execute("SELECT id, name, email FROM users;")
users = cur.fetchall()
print(f"Users: {[(u[1], u[2]) for u in users]}")
cur.execute("SELECT id, title, user_id FROM trips;")
trips = cur.fetchall()
print(f"Trips: {[(t[1], t[0][:8]) for t in trips]}")
conn.close()

demo_user_exists = any(u[2] == 'demo@globetrotter.com' for u in users)

# ============================================================
# AUTH TESTS
# ============================================================
print("\n=== AUTH TESTS ===")

# Signup new user
status, body = req("POST", "/auth/signup", {"full_name": "QA Tester", "name": "QA Tester", "email": "qa_auto@tripora.com", "password": "QATest123!"}, auth=False)
if status == 201:
    test("Signup new user", status, body, 201)
    TOKEN = body.get("data", {}).get("access_token")
else:
    # Already exists - try login
    test("Signup (already exists - expected)", status, body, 400)

# Login with QA user
status, body = req("POST", "/auth/login", {"email": "qa_auto@tripora.com", "password": "QATest123!"}, auth=False)
ok, body = test("Login QA user", status, body, 200)
if ok:
    TOKEN = body.get("data", {}).get("access_token")
    print(f"    Token: {TOKEN[:40] if TOKEN else 'NONE'}...")

# Login with wrong password
status, body = req("POST", "/auth/login", {"email": "qa_auto@tripora.com", "password": "wrongpass"}, auth=False)
test("Login wrong password (expect 401)", status, body, 401)

# Get profile (authenticated)
status, body = req("GET", "/users/me")
ok, body = test("Get profile (authenticated)", status, body, 200)
if ok:
    user_data = body.get("data", {})
    print(f"    User: {user_data.get('name') or user_data.get('full_name')}, email: {user_data.get('email')}")

# Get profile (unauthenticated)
old_token = TOKEN
TOKEN = None
status, body = req("GET", "/users/me")
test("Get profile (unauthenticated, expect 401 or 403)", status, body, 401)
TOKEN = old_token

# ============================================================
# CITIES TESTS
# ============================================================
print("\n=== CITIES TESTS ===")
status, body = req("GET", "/cities")
ok, body = test("List all cities", status, body, 200)
if ok:
    cities = body.get("data", [])
    print(f"    Found {len(cities)} cities")

status, body = req("GET", "/cities?search=mumbai")
ok, body = test("Search cities by name", status, body, 200)
if ok:
    print(f"    Mumbai search results: {len(body.get('data', []))} found")

status, body = req("GET", "/cities?region=Europe")
ok, body = test("Filter cities by region=Europe", status, body, 200)
if ok:
    result = body.get("data", [])
    print(f"    Europe cities: {len(result)}")

# ============================================================
# TRIPS TESTS
# ============================================================
print("\n=== TRIPS TESTS ===")
status, body = req("GET", "/trips")
ok, body = test("List user trips", status, body, 200)
if ok:
    trip_list = body.get("data", [])
    print(f"    Found {len(trip_list)} trips")
    if trip_list:
        TRIP_ID = trip_list[0].get("id")
        print(f"    Using trip: {trip_list[0].get('title')} ({TRIP_ID})")

# Create a new trip
status, body = req("POST", "/trips", {
    "title": "QA Test Trip - Rajasthan",
    "description": "Automated QA test trip",
    "start_date": "2026-10-01",
    "end_date": "2026-10-10",
    "origin_city": "Mumbai",
    "num_travelers": 2,
    "transit_mode": "train",
    "total_budget": 50000.0,
    "currency": "INR",
    "visibility": "private",
    "status": "draft"
})
ok, body = test("Create trip", status, body, 201)
new_trip_id = None
if ok:
    data = body.get("data", {})
    # Handle different response shapes
    if "trip" in data:
        new_trip_id = data["trip"].get("id")
    else:
        new_trip_id = data.get("id")
    print(f"    Created trip: {new_trip_id}")

# Get specific trip
if new_trip_id:
    status, body = req("GET", f"/trips/{new_trip_id}")
    ok, body = test("Get trip by ID", status, body, 200)
    if ok:
        data = body.get("data", {})
        trip_title = data.get("trip", {}).get("title") or data.get("title")
        print(f"    Trip title: {trip_title}")
    
    # Update trip
    status, body = req("PUT", f"/trips/{new_trip_id}", {
        "title": "QA Test Trip - Rajasthan UPDATED",
        "description": "Updated by QA test"
    })
    test("Update trip", status, body, 200)
    
    # Add a stop
    udaipur_id = next((c["id"] for c in cities if c.get("name") == "Udaipur"), cities[0]["id"])
    status, body = req("POST", f"/trips/{new_trip_id}/stops", {
        "city_id": udaipur_id,
        "arrival_date": "2026-10-02",
        "departure_date": "2026-10-04",
        "notes": "Lake city stopover"
    })
    ok, body = test("Add stop to trip", status, body, 201)
    if ok:
        stop_data = body.get("data", {})
        STOP_ID = stop_data.get("id")
        print(f"    Stop ID: {STOP_ID}")
    
    # Get trip budget
    status, body = req("GET", f"/trips/{new_trip_id}/budget")
    test("Get trip budget", status, body, 200)
    
    # Add expense
    status, body = req("POST", f"/trips/{new_trip_id}/expenses", {
        "description": "Train tickets Mumbai to Udaipur",
        "amount": 2400.0,
        "category": "transport",
        "currency": "INR",
        "type": "actual"
    })
    ok, body = test("Add expense", status, body, 201)
    if ok:
        EXPENSE_ID = body.get("data", {}).get("id")
    
    # Get expenses
    status, body = req("GET", f"/trips/{new_trip_id}/expenses")
    ok, body = test("Get trip expenses", status, body, 200)
    if ok:
        print(f"    Expenses: {len(body.get('data', []))} items")
    
    # Generate share link
    status, body = req("POST", f"/trips/{new_trip_id}/share", {})
    ok, body = test("Generate share link", status, body, 201)
    if ok:
        share_data = body.get("data", {})
        share_token = share_data.get("share_token") or share_data.get("token")
        print(f"    Share token: {share_token}")
    
    # Get collaborators
    status, body = req("GET", f"/trips/{new_trip_id}/collaborators")
    test("Get collaborators", status, body, 200)
    
    # Get map route
    status, body = req("GET", f"/trips/{new_trip_id}/map-route")
    test("Get map route", status, body, 200)
    
    # Delete the test trip at end
    status, body = req("DELETE", f"/trips/{new_trip_id}")
    test("Delete trip", status, body, 200)

# ============================================================
# ITINERARY ROUTE TESTS
# ============================================================
print("\n=== ITINERARY ROUTE TESTS ===")
if TRIP_ID:
    status, body = req("GET", f"/trips/{TRIP_ID}/itinerary")
    ok, body = test("Get trip itinerary", status, body, 200)

# ============================================================
# PROFILE UPDATE TEST
# ============================================================
print("\n=== PROFILE TESTS ===")
status, body = req("PUT", "/users/me", {
    "name": "Demo Traveler Updated",
    "preferred_currency": "INR"
})
ok, body = test("Update user profile", status, body, 200)

# Restore original name
req("PUT", "/users/me", {"name": "Demo Traveler", "preferred_currency": "INR"})

# ============================================================
# RECOMMENDATIONS TEST
# ============================================================
print("\n=== RECOMMENDATION TESTS ===")
status, body = req("GET", "/recommend/cities")
test("Get destination recommendations", status, body, 200)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("FINAL TEST SUMMARY")
print("="*60)
passed = sum(1 for r in RESULTS if r[1] == "PASS")
failed = sum(1 for r in RESULTS if r[1] == "FAIL")
print(f"PASSED: {passed}/{len(RESULTS)}")
print(f"FAILED: {failed}/{len(RESULTS)}")
print()
print(f"{'TEST':<50} {'RESULT':<8} {'STATUS'}")
print("-"*75)
for name, result, http_status, _ in RESULTS:
    print(f"{name:<50} {result:<8} HTTP {http_status}")

if failed > 0:
    print("\nFAILED TESTS:")
    for name, result, http_status, body in RESULTS:
        if result == "FAIL":
            print(f"  - {name}: HTTP {http_status}")
            print(f"    {body[:200]}")
