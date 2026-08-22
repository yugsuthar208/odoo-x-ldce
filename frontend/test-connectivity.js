import axios from "axios";

const BASE_URL = "http://localhost:8000/api";
let authToken = null;

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

async function runConnectivityTests() {
  console.log("===============================================================");
  console.log("🌐 STARTING FRONTEND-TO-BACKEND CONNECTIVITY TEST SUITE");
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
  const testEmail = `traveler_${Date.now()}@example.com`;
  await test("POST /auth/signup", async () => {
    const res = await api.post("/auth/signup", {
      name: "Frontend Traveler",
      email: testEmail,
      password: "TravelerPassword123!",
      preferred_currency: "USD",
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

  // 5. Explore Cities
  let sampleCityId = null;
  await test("GET /cities (Search & Filter)", async () => {
    const res = await api.get("/cities", { params: { search: "Tokyo" } });
    if (!res.data.success || !Array.isArray(res.data.data) || res.data.data.length === 0) {
      throw new Error("No cities returned");
    }
    sampleCityId = res.data.data[0].id;
  });

  // 6. Recommended Cities (3-Layer Hybrid ML Recommender)
  await test("GET /recommend/cities (Hybrid ML Recommender)", async () => {
    const res = await api.get("/recommend/cities");
    const recs = res.data.data?.recommendations;
    if (!res.data.success || !Array.isArray(recs) || recs.length === 0) {
      throw new Error("No ML recommendations returned");
    }
  });

  // 7. Create Trip
  let tripId = null;
  await test("POST /trips", async () => {
    const res = await api.post("/trips", {
      title: "Japan Spring Voyage",
      description: "Visiting Tokyo, Kyoto & Osaka",
      start_date: "2026-04-01",
      end_date: "2026-04-12",
      total_budget: 4500.0,
      currency: "USD",
      visibility: "private",
    });
    if (!res.data.success || !res.data.data.id) {
      throw new Error("Trip creation failed");
    }
    tripId = res.data.data.id;
  });

  // 8. Add Stop to Trip
  let stopId = null;
  await test("POST /trips/{id}/stops", async () => {
    const res = await api.post(`/trips/${tripId}/stops`, {
      city_id: sampleCityId,
      arrival_date: "2026-04-01",
      departure_date: "2026-04-05",
      order: 0,
      hotel_name: "Shinjuku Grand Hotel",
    });
    if (!res.data.success || !res.data.data.id) {
      throw new Error("Add stop failed");
    }
    stopId = res.data.data.id;
  });

  // 9. Predict Budget (XGBoost ML)
  await test("GET /recommend/budget/{trip_id} (XGBoost Predictor)", async () => {
    const res = await api.get(`/recommend/budget/${tripId}`);
    const predVal = res.data.data?.prediction?.predicted_total_cost;
    if (!res.data.success || typeof predVal !== "number") {
      throw new Error("Budget prediction failed");
    }
  });

  // 10. Add Expense
  await test("POST /trips/{id}/expenses", async () => {
    const res = await api.post(`/trips/${tripId}/expenses`, {
      category: "accommodation",
      description: "Hotel Deposit",
      actual_amount: 500.0,
      currency: "USD",
    });
    if (!res.data.success || !res.data.data.id) {
      throw new Error("Add expense failed");
    }
  });

  // 11. Get Map Route
  await test("GET /trips/{id}/map-route", async () => {
    const res = await api.get(`/trips/${tripId}/map-route`);
    const routeArr = res.data.data?.route;
    if (!res.data.success || !Array.isArray(routeArr)) {
      throw new Error("Map route failed");
    }
  });

  // 12. In-App Notifications
  await test("GET /notifications", async () => {
    const res = await api.get("/notifications");
    if (!Array.isArray(res.data)) {
      throw new Error("Notifications response format invalid");
    }
  });

  // 13. Audit Trail
  await test("GET /trips/{id}/audit-logs", async () => {
    const res = await api.get(`/trips/${tripId}/audit-logs`);
    if (!Array.isArray(res.data) || res.data.length === 0) {
      throw new Error("Audit logs empty or invalid");
    }
  });

  // 14. Prometheus Metrics
  await test("GET /metrics (Observability)", async () => {
    const res = await axios.get("http://localhost:8000/metrics");
    if (res.status !== 200 || !res.data.includes("globetrotter_")) {
      throw new Error("Prometheus metrics invalid");
    }
  });

  console.log("===============================================================");
  console.log(`📊 CONNECTIVITY TEST SUMMARY: ${passed}/${total} PASSED (${Math.round((passed / total) * 100)}%)`);
  console.log("===============================================================");

  if (passed === total) {
    console.log("🎉 Frontend and Backend are 100% connected and operational!");
  } else {
    process.exit(1);
  }
}

runConnectivityTests().catch((err) => {
  console.error("Fatal Test Runner Error:", err);
  process.exit(1);
});
