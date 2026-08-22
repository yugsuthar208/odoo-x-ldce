# ⚙️ Tripora Bharat — Backend API & Microservices

The backend service for **Tripora Bharat** provides authoritative trip calculations, multi-modal transit leg generation, DuckDuckGo live search scraping, dynamic room & group budget allocation, and Sentence-Transformer hybrid recommendations.

---

## 🛠 Backend Architecture

### 1. Authoritative Budget Engine (`app/services/budget_service.py`)
Calculates single-source-of-truth totals in INR (₹) using explicit database relational records:
$$\text{Total Cost} = \text{Stays Cost} + \text{Transit Cost} + \text{Activities Cost} + \text{Meals Cost} + \text{Misc Cost}$$

Where:
- $\text{Stays Cost} = \sum (\text{room\_night\_tariff} \times \text{nights} \times \lceil \text{num\_travelers} / 2 \rceil)$
- $\text{Transit Cost} = \sum (\text{selected\_option.total\_estimated\_cost})$
- $\text{Activities Cost} = \sum (\text{effective\_cost} \times \text{num\_travelers})$
- $\text{Meals Cost} = \text{MEALS\_PER\_DAY\_INR} \times \text{num\_travelers} \times \text{trip\_days}$

### 2. Multi-Modal Transit Generator (`app/services/transit_service.py`)
Generates persisted `TransitLeg` and `TransitOption` rows for every consecutive stop sequence in a trip using distance math:
- **Train (IRCTC)**: Sleeper Class (₹2/km), 3AC (₹4/km), 2AC (₹6/km), Vande Bharat (₹7.5/km).
- **Flight**: Generated if distance > 400km (₹4,000 base + ₹5/km).
- **Bus**: Volvo AC Seater/Sleeper (₹3.5/km).
- **Cab**: Outstation SUV/Sedan (₹14/km).

### 3. Live Search Scraper (`app/services/live_search_service.py`)
Scrapes DuckDuckGo for authentic regional food, thalis, street food, heritage havelis, hostels, and resorts across India with fallback mock data when offline.

---

## 🗄 Relational Schema Overview

- **`users`**: User accounts and credentials.
- **`trips`**: Trip metadata (`origin_city`, `num_travelers`, `budget_target`, `status`).
- **`trip_stops`**: Destination stops ordered by `stop_order`.
- **`stays` & `trip_stays`**: Hotel / hostel / homestay selections per stop.
- **`transit_legs` & `transit_options`**: Multi-modal travel choices between origin and stops.
- **`activities` & `itinerary_items`**: Catalog activities scheduled into stop dates.
- **`expenses`**: Manual & extra expense logs.
- **`recommendations` & `ml_predictions`**: User preference embeddings and similarity scores.

---

## 🔌 Core API Endpoints

### 🔐 Authentication (`/api/v1/auth`)
- `POST /auth/signup` — Create user account
- `POST /auth/login` — Authenticate and receive JWT token

### 🗺 Trips Workspace (`/api/v1/trips`)
- `GET /trips` — List user trips
- `POST /trips` — Create new trip (with origin city & traveler count)
- `GET /trips/{id}` — Single Read-Model workspace endpoint (returns trip, stops, transit legs, stays, activities, & budget)
- `PUT /trips/{id}` — Update trip metadata
- `DELETE /trips/{id}` — Delete trip

### 🚆 Transit Engine (`/api/v1/trips/{id}/transit`)
- `GET /trips/{id}/transit` — Fetch persisted transit legs and multi-modal options
- `PATCH /trips/{id}/transit/{leg_id}` — Select transit option and recalculate authoritative budget

### 💰 Budget & Expenses (`/api/v1/trips/{id}/budget`)
- `GET /trips/{id}/budget` — Authoritative budget breakdown in INR
- `PUT /trips/{id}/budget` — Update budget target limit (`budget_target`)

### 🔍 Live Food & Stays (`/api/v1/places`)
- `GET /places/live-food?city=Udaipur&budget_tier=mid` — Scraping regional delicacies & thalis
- `GET /places/live-stays?city=Udaipur&budget_tier=mid` — Scraping hostels, hotels & havelis

---

## 💻 Database Migrations (Alembic)

To apply migrations against your Supabase PostgreSQL database:

```bash
alembic upgrade head
```

To create a new migration after updating SQLAlchemy models:
```bash
alembic revision --autogenerate -m "describe changes"
```

---

## 🧪 Seeding Database

To seed complete Indian travel data (cities, activities, cost indices, and sample trips):

```bash
python seed_india_complete.py
```
