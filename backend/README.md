# GlobeTrotter Backend API

Production-ready, high-performance asynchronous backend for **GlobeTrotter** — an AI-powered personalized travel planning and budget estimation platform.

---

## 🚀 Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL (with `asyncpg` driver and async SQLAlchemy ORM)
- **Migrations:** Alembic
- **Authentication:** JWT (JSON Web Tokens) with Bcrypt password hashing
- **Machine Learning:** Scikit-Learn, Pandas, NumPy, Joblib
- **Server:** Uvicorn ASGI

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory, CORS, exception handlers & lifespan
│   ├── database.py                 # Async SQLAlchemy engine, session maker, Base
│   ├── config.py                   # Pydantic Settings & environment loader
│   ├── models/                     # SQLAlchemy ORM Data Models
│   │   ├── __init__.py
│   │   ├── user.py                 # User account model
│   │   ├── city.py                 # Destination city model
│   │   ├── trip.py                 # Trip itinerary model
│   │   ├── stop.py                 # Itinerary stop model
│   │   ├── activity.py             # City activity model
│   │   ├── stop_activity.py        # Assigned stop activity model
│   │   └── budget.py               # Trip budget model
│   ├── schemas/                    # Pydantic v2 Request/Response Schemas
│   │   ├── __init__.py
│   │   ├── common.py               # Standardized APIResponse & ErrorResponse
│   │   ├── user.py                 # Auth & user schemas
│   │   ├── city.py                 # City schemas
│   │   ├── trip.py                 # Trip schemas
│   │   ├── stop.py                 # Stop schemas
│   │   ├── activity.py             # Activity schemas
│   │   └── budget.py               # Budget calculation & prediction schemas
│   ├── routes/                     # API Routers
│   │   ├── __init__.py
│   │   ├── auth.py                 # /api/auth endpoints
│   │   ├── users.py                # /api/users endpoints
│   │   ├── cities.py               # /api/cities endpoints
│   │   ├── trips.py                # /api/trips endpoints
│   │   ├── stops.py                # /api/stops endpoints
│   │   ├── activities.py           # /api/activities endpoints
│   │   └── recommend.py            # /api/recommend endpoints
│   ├── controllers/                # Business Logic & DB operations
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── city_controller.py
│   │   ├── trip_controller.py
│   │   ├── stop_controller.py
│   │   └── activity_controller.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py                 # JWT verification & dependency injection
│   └── ml/                         # Machine Learning Modules
│       ├── __init__.py
│       ├── recommender.py          # Content-based cosine similarity city recommender
│       ├── budget_predictor.py     # Linear regression budget inference engine
│       ├── train.py                # Synthetic dataset generator & model trainer
│       └── budget_model.pkl        # Serialized model artifact
├── alembic/                        # Alembic Database Migration Environment
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
├── alembic.ini                     # Alembic configuration file
├── seed.py                         # Complete seed dataset (20 cities, 100 activities, demo trips)
├── test_api.py                     # Automated end-to-end test suite
├── requirements.txt                # Production dependencies
├── .env.example                    # Sample environment variables
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone & Set Up Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/globetrotter
SECRET_KEY=your_jwt_secret_key_here_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
```
*(Note: If `DATABASE_URL` is omitted, the application seamlessly defaults to SQLite async `sqlite+aiosqlite:///./globetrotter.db` for instant local testing without needing an external database server).*

---

## 🗄️ Database Migrations

### Run Migrations to Latest Version
```bash
alembic upgrade head
```

### Create New Migrations (Autogenerate)
```bash
alembic revision --autogenerate -m "description_of_changes"
```

---

## 🧠 Train Machine Learning Model

To train or re-train the Linear Regression Budget Predictor on 500 synthetic trip data points:

```bash
python app/ml/train.py
```
This generates `app/ml/budget_model.pkl`. If this file is missing when the server starts, the application automatically trains and creates it on startup.

---

## 🌱 Seed Database

Populates the database with:
- **20 Global Destination Cities** (Europe, Asia, Americas, Africa, Oceania, Middle East) with accurate cost indices and popularity scores.
- **100 Curated Activities** (5 per city across Sightseeing, Food, Adventure).
- **1 Demo Traveler Account** (`demo@globetrotter.com` / `demo1234`).
- **2 Complete Sample Trips** with scheduled stops, activities, and budget allocations.

Run:
```bash
python seed.py
```

---

## 🚀 Running the Server

Start the Uvicorn ASGI server with hot reloading:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Automated Tests

Run the comprehensive integration test suite:

```bash
python test_api.py
```

---

## 📋 API Endpoints Catalog

### Unified Response Format

All successful responses return:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

All error responses return:
```json
{
  "success": false,
  "error": "Detailed error message",
  "status_code": 400
}
```

---

### 1. Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/signup` | Register new user with bcrypt hash & return JWT | No |
| `POST` | `/api/auth/login` | Authenticate email/password & return JWT | No |
| `POST` | `/api/auth/forgot-password` | Generate password reset token | No |

#### Signup Example Body:
```json
{
  "name": "Jane Traveler",
  "email": "jane@example.com",
  "password": "password123",
  "profile_photo": "https://example.com/photo.jpg",
  "language": "en"
}
```

---

### 2. User Profile (`/api/users`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/users/me` | Get authenticated user profile | Bearer JWT |
| `PUT` | `/api/users/me` | Update name, profile photo, or language | Bearer JWT |
| `DELETE` | `/api/users/me` | Delete traveler account & cascade trip data | Bearer JWT |

---

### 3. Destination Cities (`/api/cities`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/cities` | Search cities (`?search=Tokyo&region=Asia`) | No |
| `GET` | `/api/cities/{id}` | Get city details with activity catalog | No |
| `GET` | `/api/cities/{id}/activities` | Filter activities (`?type=food&max_cost=50`) | No |

---

### 4. Trips & Itineraries (`/api/trips`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/trips` | List all trips for current user | Bearer JWT |
| `POST` | `/api/trips` | Create new trip with default budget | Bearer JWT |
| `GET` | `/api/trips/{id}` | Get single trip with stops, activities, budget | Bearer JWT |
| `PUT` | `/api/trips/{id}` | Update trip details (dates, title, visibility) | Bearer JWT |
| `DELETE` | `/api/trips/{id}` | Delete trip and associated data | Bearer JWT |
| `GET` | `/api/trips/public/{id}` | Public read-only trip overview | No |
| `GET` | `/api/trips/{id}/budget` | Upgraded full cost breakdown, savings target & stop breakdown | Bearer JWT |
| `POST` | `/api/trips/{id}/stops` | Add a city stop to trip | Bearer JWT |

#### Trip Creation Example Body:
```json
{
  "title": "Summer in Japan",
  "description": "Tokyo and Kyoto adventure",
  "start_date": "2026-06-01",
  "end_date": "2026-06-10",
  "cover_photo": "https://example.com/japan.jpg",
  "is_public": true
}
```

---

### 5. Stops & Stop Activities (`/api/stops`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `PUT` | `/api/stops/{id}` | Edit stop dates or order index | Bearer JWT |
| `DELETE` | `/api/stops/{id}` | Remove stop from trip | Bearer JWT |
| `POST` | `/api/stops/{id}/activities` | Schedule an activity to a stop | Bearer JWT |
| `DELETE` | `/api/stops/{stop_id}/activities/{activity_id}` | Remove activity from stop | Bearer JWT |

#### Schedule Activity Example Body:
```json
{
  "activity_id": "activity-uuid-here",
  "scheduled_date": "2026-06-03",
  "scheduled_time": "14:00:00",
  "notes": "Bring camera and comfortable shoes"
}
```

---

### 6. Machine Learning Recommendations (`/api/recommend`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/recommend/cities` | Recommend cities via Cosine Similarity | Bearer JWT |
| `GET` | `/api/recommend/budget/{trip_id}` | Predict trip cost using Linear Regression | Bearer JWT |

#### Budget Prediction Response Example:
```json
{
  "success": true,
  "data": {
    "trip_id": "8f03c405-b1a7-47b2-84fc-ea35a298bfd3",
    "predicted_total_cost": 2145.50,
    "features_used": {
      "total_days": 10,
      "num_stops": 3,
      "num_activities": 5,
      "avg_city_cost_index": 185.0,
      "region_encoded": 0
    }
  },
  "message": "Trip budget predicted successfully using machine learning model"
}
```

---

## 🧮 Upgraded Budget Calculation Formula & Schema

When `GET /api/trips/{id}/budget` is called by the trip owner:

1. **`stay_cost`** = $\sum (\text{city.cost\_index} \times \text{days\_at\_stop})$ for all stops (minimum 1 day/stop, fallback $80/day)
2. **`activities_cost`** = $\sum (\text{activity.cost})$ for all assigned stop activities
3. **`meals_cost`** = $\text{MEALS\_PER\_DAY\_USD} \times \text{total\_trip\_days}$ (configurable via `.env`, default $25/day)
4. **`transport_cost`** & **`misc_cost`** = from `budgets` table (default 0.0)
5. **`total_cost`** = $\text{stay} + \text{activities} + \text{meals} + \text{transport} + \text{misc}$
6. **`cost_per_day`** = $\text{total\_cost} / \text{total\_trip\_days}$
7. **`savings_needed_per_day`** = $\text{total\_cost} / \text{days\_until\_trip}$ (if trip has not yet started)
8. **`budget_status`** = `is_over_budget`, `budget_overage`, `budget_remaining` against `total_budget_limit`
9. **`stop_breakdown`** = Per-stop breakdown with `stay_cost`, `activities_cost`, `meals_cost`, and `stop_total`
10. **`cost_distribution_percent`** = Percentage breakdown across categories (stay, activities, meals, transport, misc)

#### Example Output:
```json
{
  "success": true,
  "data": {
    "trip_id": "8f03c405-b1a7-47b2-84fc-ea35a298bfd3",
    "trip_title": "Europe 2025",
    "trip_status": "upcoming",
    "total_trip_days": 14,
    "days_until_trip": 45,
    "cost_breakdown": {
      "stay_cost": 980.00,
      "activities_cost": 320.00,
      "meals_cost": 350.00,
      "transport_cost": 200.00,
      "misc_cost": 100.00,
      "total_cost": 1950.00
    },
    "per_day": {
      "cost_per_day": 139.28,
      "savings_needed_per_day": 43.33
    },
    "budget_status": {
      "total_budget_limit": 1800.00,
      "is_over_budget": true,
      "budget_overage": 150.00,
      "budget_remaining": -150.00
    },
    "stop_breakdown": [
      {
        "stop_id": "stop-uuid",
        "city_name": "Paris",
        "days": 4,
        "stay_cost": 400.00,
        "activities_cost": 120.00,
        "meals_cost": 100.00,
        "stop_total": 620.00
      }
    ],
    "cost_distribution_percent": {
      "stay": 50.3,
      "activities": 16.4,
      "meals": 17.9,
      "transport": 10.3,
      "misc": 5.1
    }
  },
  "message": "Budget calculated successfully"
}
```
