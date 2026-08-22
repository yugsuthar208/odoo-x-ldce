# 🎨 Tripora Bharat — Frontend Web Application

The frontend client for **Tripora Bharat** built with **React 18**, **Vite**, **Tailwind CSS**, and custom micro-interactions.

---

## 🏛 Design Philosophy & State Integration

Tripora Bharat follows a **Single-Source-of-Truth Server-State Pattern**:
1. **No Competing Math**: React components do NOT perform local budget or stay cost math.
2. **Single Read Model**: `TripDetailPage` fetches the complete trip state via `GET /api/v1/trips/{id}`, which includes stops, transit choices, stay selections, scheduled activities, and authoritative backend budget metrics.
3. **Mutation & Refetch**: When a user selects a transit option, adds a stop, or updates a budget target, the frontend calls `POST/PATCH/PUT` endpoints on the backend, and invokes `onRefresh()` to re-sync the entire trip server state.

---

## 🧩 Component Directory Structure

```text
src/
├── components/
│   ├── activities/
│   │   ├── ActivityList.jsx        # Scheduled activities view
│   │   └── ActivityPickerModal.jsx# Catalog picker modal
│   ├── budget/
│   │   ├── TripBudget.jsx          # Pie charts, breakdown, & budget target editor
│   │   └── ExpenseList.jsx         # Manual expense logging table
│   ├── cities/
│   │   └── CityCard.jsx            # City catalog card with INR tariffs
│   ├── map/
│   │   ├── TripMap.jsx             # Interactive route map visualization
│   │   └── StopDetailBar.jsx       # Stop summary bar
│   ├── trips/
│   │   ├── LiveFoodStayFinder.jsx  # Live DuckDuckGo search viewer
│   │   ├── TransitOptimizer.jsx    # Multi-modal transit selection UI
│   │   ├── StopCard.jsx            # Destination stop card
│   │   └── TripCard.jsx           # Trip overview card
│   └── common/                     # Loaders, toasts, error boundaries
├── pages/
│   ├── ExplorePage.jsx             # Destination search & hybrid recommendations
│   ├── TripsPage.jsx               # User trips dashboard
│   ├── TripDetailPage.jsx          # Trip workspace controller
│   └── SignupPage.jsx              # Auth views
└── services/
    ├── apiClient.js                # Axios instance with auth interceptors
    └── tripService.js              # API client methods
```

---

## 🛠 Local Development Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
Runs Vite dev server at `http://localhost:5173`.

### 3. Build for Production
```bash
npm run build
```

---

## 🧪 Connectivity & E2E Verification

Run the full end-to-end integration test suite against the local running backend:

```bash
node test-connectivity.js
```
Expected output: 100% tests passed (`16/16`).
