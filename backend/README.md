# GlobeTrotter Backend API 🌍✈️

GlobeTrotter is an enterprise-grade, production-ready backend for a personalized multi-city travel planning platform with **Scikit-Learn Machine Learning recommendations**, an **AI-powered rule-based itinerary generation engine**, **interactive map route distance calculation (Haversine)**, **schedule conflict detection**, **collaborator permissions**, **public share tokens**, and **comprehensive expense tracking**.

---

## 🛠 Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI (High performance, OpenAPI 3.0, Swagger UI & ReDoc)
- **Database:** PostgreSQL (with SQLite async fallback for local dev & testing)
- **ORM:** SQLAlchemy 2.0 (Async with `asyncpg` / `aiosqlite`)
- **Authentication:** JWT tokens (`python-jose` + `passlib` with `bcrypt`)
- **Machine Learning & AI:** `scikit-learn`, `pandas`, `numpy`, `joblib`
- **Validation:** Pydantic v2
- **Database Migrations:** Alembic
- **Server:** Uvicorn ASGI

---

## 🗄 Database Schema (11 Models)

1. **`users`**: id, name, email, password_hash, profile_photo, preferred_currency, language, created_at.
2. **`cities`**: id, name, country, region, description, cost_index, popularity_score, latitude, longitude, image_url.
3. **`trips`**: id, user_id, title, description, start_date, end_date, cover_photo, total_budget, currency, visibility (`private`/`public`/`friends`), status (`draft`/`upcoming`/`ongoing`/`completed`), created_at.
4. **`trip_stops`**: id, trip_id, city_id, arrival_date, departure_date, stop_order, notes.
5. **`activities`**: id, city_id, name, category (`sightseeing`, `food`, `adventure`, `shopping`, `nature`, `history`, `wellness`), description, estimated_cost, duration_hours, latitude, longitude, image_url.
6. **`itinerary_items`**: id, trip_stop_id, activity_id, scheduled_date, start_time, end_time, custom_cost, notes, status (`planned`, `confirmed`, `cancelled`).
7. **`expenses`**: id, trip_id, category (`transport`, `stay`, `food`, `activity`, `misc`), description, estimated_amount, actual_amount, currency, paid_by, created_at.
8. **`budgets`**: id, trip_id, transport_cost, stay_cost, meals_cost, misc_cost, total_budget_limit.
9. **`favorites`**: id, user_id, city_id, activity_id, created_at.
10. **`shared_links`**: id, trip_id, share_token (`secrets.token_urlsafe(16)`), expires_at, created_at.
11. **`trip_collaborators`**: id, trip_id, user_id, role (`editor`, `viewer`), joined_at.

---

## 🚀 Quickstart & Setup

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in `backend/`:
```env
PROJECT_NAME=GlobeTrotter
DATABASE_URL=sqlite+aiosqlite:///./globetrotter.db
SECRET_KEY=super_secret_jwt_key_globetrotter_2026_change_in_prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
MEALS_PER_DAY_USD=25.0
DEFAULT_CITY_COST_INDEX=80.0
```

### 4. Train ML Models & Seed Database
```bash
# Train ML linear regression budget model
python app/ml/train.py

# Populate 20 global cities, 100 activities, demo user, and 2 full sample trips
python seed.py
```

### 5. Run the Server
```bash
python -m uvicorn app.main:app --port 8000 --reload
```
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`
- **Health Check:** `http://127.0.0.1:8000/health`

### 6. Run Automated Test Suite (26 Tests)
```bash
python test_api.py
```

---

## 📌 API Endpoints Reference

### 🔐 Authentication & Users
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/signup` | Register new user account |
| `POST` | `/api/auth/login` | Login and obtain JWT token |
| `POST` | `/api/auth/forgot-password` | Generate password reset token |
| `GET` | `/api/users/me` | Get current user profile |
| `PUT` | `/api/users/me` | Update name, profile photo, preferred currency |
| `DELETE` | `/api/users/me` | Delete account and all associated trips |

### 🏙 Destination Cities & Catalog
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/cities` | Search and filter cities (`?search=&region=&country=`) |
| `GET` | `/api/cities/{id}` | Get city details with its catalog of activities |
| `GET` | `/api/cities/{city_id}/activities` | Filter activities (`?category=&max_cost=&max_duration=`) |
| `GET` | `/api/activities/{id}` | Get single activity details |
| `POST` | `/api/activities` | Add a new activity catalog item |

### 🗺 Trips & Itinerary Planning
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/trips` | List trips for current user (`?status=&search=`) |
| `POST` | `/api/trips` | Create a new trip |
| `GET` | `/api/trips/{id}` | Get full trip details with stops & budget |
| `PUT` | `/api/trips/{id}` | Update trip metadata |
| `DELETE` | `/api/trips/{id}` | Delete trip (owner only) |
| `POST` | `/api/trips/{id}/duplicate` | Copy trip as a new draft |
| `GET` | `/api/trips/public/{id}` | Public read-only trip overview |
| `GET` | `/api/trips/{id}/map-route` | Route coordinates & Haversine distance in km |

### 🛑 Stops & Schedule Management
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/trips/{id}/stops` | Append a destination stop to trip |
| `PUT` | `/api/trips/{id}/stops/{stop_id}` | Edit stop dates, order, or notes |
| `DELETE` | `/api/trips/{id}/stops/{stop_id}` | Remove stop from trip |
| `PUT` | `/api/trips/{id}/stops/reorder` | Bulk reorder stops sequence |
| `POST` | `/api/stops/{stop_id}/items` | Assign activity with date and time slots |
| `PUT` | `/api/itinerary-items/{item_id}` | Edit scheduled activity item |
| `DELETE` | `/api/itinerary-items/{item_id}` | Delete scheduled activity item |
| `GET` | `/api/trips/{id}/itinerary` | Day-wise grouped itinerary schedule |
| `GET` | `/api/trips/{id}/conflicts` | Detect overlapping schedule conflicts |

### 🤖 AI Itinerary Generator & ML Engine
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/trips/{id}/generate-itinerary` | Rule-based schedule generator with pace and budget constraints |
| `GET` | `/api/recommend/cities` | Content-based cosine similarity city recommender |
| `GET` | `/api/recommend/budget/{trip_id}` | Linear regression budget predictor vs actual cost |

### 💰 Budgets & Expenses
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/trips/{id}/budget` | 12-step budget forecast and breakdown |
| `PUT` | `/api/trips/{id}/budget` | Update manual budget fields |
| `POST` | `/api/trips/{id}/expenses` | Log trip expense (estimated & actual) |
| `GET` | `/api/trips/{id}/expenses` | List all expenses for a trip |
| `PUT` | `/api/expenses/{id}` | Update expense |
| `DELETE` | `/api/expenses/{id}` | Delete expense |

### 🔗 Public Sharing, Collaboration & Favorites
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/trips/{id}/share` | Generate secure share link token |
| `GET` | `/api/shared/{token}` | Public read-only view (sanitized) |
| `POST` | `/api/shared/{token}/copy` | Copy public shared trip to user account |
| `POST` | `/api/trips/{id}/collaborators` | Add editor/viewer collaborator (owner only) |
| `GET` | `/api/trips/{id}/collaborators` | List collaborators |
| `DELETE` | `/api/trips/{id}/collaborators/{user_id}` | Remove collaborator |
| `POST` | `/api/favorites` | Bookmark city or activity |
| `GET` | `/api/favorites` | List all bookmarked items |
| `DELETE` | `/api/favorites/{id}` | Remove bookmark |

---

## 🧪 Demo Account

- **Email:** `demo@globetrotter.com`
- **Password:** `demo1234`
- Preloaded with **"Europe Explorer"** and **"Asia Adventure"** trips.
