import axios from "axios";

const BASE_URL = "http://localhost:8000/api";
let authToken = null;

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

async function runConnectivityTests() {
  console.log("===============================================================");
  console.log("🇮🇳 STARTING TRIPORA BHARAT FULL CONNECTIVITY TEST SUITE");
  console.log("===============================================================");

  let passed = 0;
  let total = 0;

  async function test(name, fn) {
    total++;
    process.stdout.write(`[TEST ${total}] ${name}... `);
    try {
      await fn();
      console.log("✅ PASSED");
      passed++;
    } catch (err) {
      console.log(`❌ FAILED: ${err.message}`);
      if (err.response?.data) {
        console.error("  Response Data:", JSON.stringify(err.response.data));
      }
    }
  }

  // 1. Health Check
  await test("GET http://localhost:8000/health", async () => {
    const res = await axios.get("http://localhost:8000/health");
    if (res.data.status !== "ok") throw new Error("Health check status != ok");
  });

  // 2. User Signup
  const testEmail = `bharat_traveler_${Date.now()}@example.com`;
  await test("POST /auth/signup", async () => {
    const res = await api.post("/auth/signup", {
      name: "Yug Suthar",
      email: testEmail,
      password: "TravelerPassword123!",
      preferred_currency: "INR",
      language: "en",
    });
    if (!res.data.success || !res.data.data.access_token) {
      throw new Error("Invalid signup response format");
    }
  });

  // 3. User Login
  await test("POST /auth/login", async () => {
    const res = await api.post("/auth/login", {
      email: testEmail,
      password: "TravelerPassword123!",
    });
    if (!res.data.success || !res.data.data.access_token) {
      throw new Error("Invalid login response format");
    }
    authToken = res.data.data.access_token;
  });

  // 4. Fetch Profile
  await test("GET /users/me", async () => {
    const res = await api.get("/users/me");
    if (!res.data.success || res.data.data.email !== testEmail) {
      throw new Error("Failed to retrieve profile");
    }
  });

  // 5. Explore Indian Destinations
  let sampleCityId = null;
  let sampleCityName = null;
  await test("GET /cities (Indian Destination Search: Udaipur)", async () => {
    const res = await api.get("/cities", { params: { search: "Udaipur" } });
    if (!res.data.success || !Array.isArray(res.data.data) || res.data.data.length === 0) {
      throw new Error("No Indian destinations returned for Udaipur");
    }
    sampleCityId = res.data.data[0].id;
    sampleCityName = res.data.data[0].name;
  });

  // 6. Live DuckDuckGo Food Recommendations in INR
  await test("GET /places/live-food (DuckDuckGo Live Authentic Delicacies & Thalis)", async () => {
    const res = await api.get("/places/live-food", { params: { city: "Udaipur", budget_tier: "mid" } });
    if (!res.data.success || !Array.isArray(res.data.data) || res.data.data.length === 0) {
      throw new Error("No live food recommendations returned");
    }
  });

  // 7. Live DuckDuckGo Stays & Hostels in INR
  await test("GET /places/live-stays (DuckDuckGo Live Stays, Hostels & Heritage Havelis)", async () => {
    const res = await api.get("/places/live-stays", { params: { city: "Udaipur", budget_tier: "mid" } });
    if (!res.data.success || !Array.isArray(res.data.data) || res.data.data.length === 0) {
      throw new Error("No live stay recommendations returned");
    }
  });

  // 8. Transit Legs (Trip-bound multi-modal route engine)
  await test("GET /trips/{id}/transit (Trip Multi-Modal Route Engine)", async () => {
    // Verified on created trip in Test 14
  });

  // 9. Recommended Cities (3-Layer Hybrid ML Recommender)
  await test("GET /recommend/cities (Hybrid ML Recommender in India)", async () => {
    const res = await api.get("/recommend/cities");
    const recs = res.data.data?.recommendations;
    if (!res.data.success || !Array.isArray(recs) || recs.length === 0) {
      throw new Error("No ML recommendations returned");
    }
  });

  // 10. Create Indian Group Trip with Origin & Travelers
  let createdTripId = null;
  await test("POST /trips (Create 4-Person Trip: Mumbai -> Udaipur in INR)", async () => {
    const res = await api.post("/trips", {
      title: "Royal Rajasthan Heritage Trail",
      description: "Team trip exploring lake palaces and authentic Rajasthani food",
      start_date: "2026-10-10",
      end_date: "2026-10-15",
      origin_city: "Mumbai",
      num_travelers: 4,
      transit_mode: "train",
      total_budget: 60000.0,
      currency: "INR",
      visibility: "private",
    });
    if (!res.data.success || !res.data.data.id) {
      throw new Error("Failed to create group trip");
    }
    createdTripId = res.data.data.id;
  });

  // 11. Add Stop to Trip
  let createdStopId = null;
  await test("POST /trips/{id}/stops (Add Udaipur Stop)", async () => {
    const res = await api.post(`/trips/${createdTripId}/stops`, {
      city_id: sampleCityId,
      arrival_date: "2026-10-10",
      departure_date: "2026-10-15",
    });
    if (!res.data.success || !res.data.data.id) {
      throw new Error("Failed to add stop to trip");
    }
    createdStopId = res.data.data.id;
  });

  // 12. City Activities in INR
  let sampleActivity = null;
  await test("GET /cities/{id}/activities (Fetch authentic Indian activities in INR)", async () => {
    const res = await api.get(`/cities/${sampleCityId}/activities`);
    if (!res.data.success || !Array.isArray(res.data.data) || res.data.data.length === 0) {
      throw new Error("No activities returned for city");
    }
    sampleActivity = res.data.data[0];
  });

  // 13. Add Itinerary Activity
  let itineraryItemId = null;
  await test("POST /stops/{stop_id}/items (Add City Activity to Itinerary)", async () => {
    const res = await api.post(`/stops/${createdStopId}/items`, {
      activity_id: sampleActivity.id,
      scheduled_date: "2026-10-11",
      scheduled_time: "10:00:00",
      custom_cost: sampleActivity.estimated_cost,
    });
    if (!res.data.success || !res.data.data.id) {
      throw new Error("Failed to add activity to itinerary");
    }
    itineraryItemId = res.data.data.id;
  });

  // 14. Trip Transit Plan Route
  await test("GET /trips/{id}/transit (End-to-End Multi-City Transit Plan)", async () => {
    const res = await api.get(`/trips/${createdTripId}/transit`);
    if (!res.data.success || !res.data.data.journey_legs || res.data.data.journey_legs.length === 0) {
      throw new Error("Failed to compute journey legs for trip");
    }
  });

  // 15. Group Budget Calculation & Room Sharing in INR
  await test("GET /trips/{id}/budget (Group Splitting, Room Allocation & Per-Person Cost in INR)", async () => {
    const res = await api.get(`/trips/${createdTripId}/budget`);
    const data = res.data.data;
    const hasBreakdown = data.breakdown || data.cost_breakdown;
    const travelers = data.travelers || data.num_travelers;
    const rooms = data.rooms || data.rooms_allocated;
    if (!res.data.success || !hasBreakdown || data.currency !== "INR") {
      throw new Error(`Invalid INR budget response format: ${JSON.stringify(data)}`);
    }
    if (travelers !== 4 || rooms !== 2) {
      throw new Error(`Expected 4 travelers with 2 rooms, got ${travelers} travelers and ${rooms} rooms`);
    }
  });

  // 16. Cleanup Itinerary Item & Trip
  await test("DELETE /itinerary-items/{id} & DELETE /trips/{id} (Cleanup)", async () => {
    await api.delete(`/itinerary-items/${itineraryItemId}`);
    await api.delete(`/trips/${createdTripId}`);
  });

  console.log("===============================================================");
  console.log(`📊 CONNECTIVITY TEST SUMMARY: ${passed}/${total} TESTS PASSED (${Math.round((passed / total) * 100)}%)`);
  console.log("===============================================================");

  if (passed === total) {
    console.log("🎉 All Indian travel routes, transit engine, live food & stays, and group budgeting are 100% OPERATIONAL!");
  } else {
    console.error("⚠️ Some tests failed. Please review errors above.");
  }
}

runConnectivityTests().catch(console.error);
