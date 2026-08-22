# 🇮🇳 Tripora Bharat — Personalized Indian Multi-City Travel Platform

> **Discover destinations → Build a trip → Compare travel options → Add stays/food/activities → Automatically calculate budget → Optimize plan → Share trip.**

Tripora Bharat is a single-source-of-truth travel planning platform tailored for personalized multi-city trips across India. Built on authoritative backend cost calculations, live DuckDuckGo food/stay scrapers, multi-modal IRCTC train/flight/bus/cab transit engines, and hybrid ML recommendation algorithms.

---

## 🏗 System Architecture & Domain Model

Tripora Bharat enforces a **relational, single-source-of-truth domain architecture**. All financial metrics, dates, and journey legs originate from the backend database:

```mermaid
graph TD
    User([Traveler / Group]) -->|HTTP / React UI| Frontend[React + Vite Frontend]
    Frontend -->|REST APIs| Backend[FastAPI Backend Server]
    
    subgraph Authoritative Backend Engine
        Backend -->|Async ORM| DB[(Supabase Async PostgreSQL)]
        Backend -->|Live Scrapers| DDG[DuckDuckGo Live Search Engine]
        Backend -->|SentenceTransformers| ML[Hybrid ML & Budget Predictor]
        
        DB --> Stops[TripStops & Sequence]
        DB --> Stays[TripStays & Room Allocation]
        DB --> Transit[TransitLegs & Multi-Modal Options]
        DB --> Activities[ItineraryItems & Costs]
        
        Stays --> BudgetService[Authoritative Budget Engine]
        Transit --> BudgetService
        Activities --> BudgetService
        BudgetService -->|JSON Read Model| Backend
    end

    Backend -->|Single Read Model| Frontend
```

---

## ✨ Key Features

- **🇮🇳 Full Indian Coverage**: Personalized search & planning across all 36 Indian states & union territories (Udaipur, Manali, Munnar, Varanasi, Leh, etc.) in Indian Rupees (₹ INR).
- **🚆 Multi-Modal Transit Engine**: Calculates real distances (Haversine formula) and generates multi-modal transit options:
  - **Indian Railways (IRCTC)**: Sleeper (SL @ ₹2/km), 3AC (@ ₹4/km), 2AC (@ ₹6/km), Vande Bharat Express.
  - **Domestic Flights**: Automated distance threshold checking (>400 km) with baseline fare math (₹4,000 + ₹5/km).
  - **Volvo AC Buses**: Regional highways & hill station routes (@ ₹3.5/km).
  - **Outstation Cabs**: Group flex transfers (@ ₹14/km).
- **🏨 Group Budgeting & Room Allocation**: Dynamic room calculations ($\lceil \text{Travelers} / 2 \rceil$) and per-person cost splitting.
- **🔍 Live DuckDuckGo Food & Stay Recommendations**: Real-time web search for local street food, thalis, hostels, luxury heritage havelis, and resorts without API key dependencies.
- **🤖 Hybrid ML Recommender**: Sentence-Transformers (`all-MiniLM-L6-v2`) embeddings combined with budget predictors for personalized city and activity suggestions.
- **🔗 Trip Sharing & Copying**: Public share links (`/shared/{token}`) allowing users to clone trips as their own independent copy with isolated stops, transit, and stays.

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: Async PostgreSQL on Supabase (`sqlalchemy[asyncio]`, `asyncpg`, `alembic`)
- **Authentication**: JWT Auth (`passlib`, `bcrypt`, `python-jose`)
- **Machine Learning**: `sentence-transformers`, `scikit-learn`, `pandas`, `numpy`
- **Live Search**: DuckDuckGo HTML & JSON scrapers (`httpx`, `BeautifulSoup4`)

### Frontend
- **Framework**: React 18 + Vite
- **Routing**: React Router v6
- **Styling**: Tailwind CSS + Custom Design System (CSS variables, tactile controls)
- **Icons & Charts**: `lucide-react`, `recharts`
- **Map Visualizations**: Leaflet / Custom Map Engine

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase PostgreSQL Database (or local Postgres)

### 2. Environment Setup

Create `.env` file in `backend/`:
```env
PROJECT_NAME="Tripora Bharat"
DATABASE_URL="postgresql+asyncpg://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT].supabase.co:5432/postgres"
SECRET_KEY="super_secret_tripora_bharat_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_DAYS=7
MEALS_PER_DAY_INR=600.0
DEFAULT_CITY_COST_INDEX=55.0
```

### 3. Run Backend

```bash
cd backend
python -m venv venv
# Activate virtual environment
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 🧪 Automated Testing

Run the full end-to-end connectivity test suite:

```bash
cd frontend
node test-connectivity.js
```

---

## 📁 Repository Structure

```text
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── controllers/      # Route handler logic & access checks
│   │   ├── models/           # SQLAlchemy Async ORM models
│   │   ├── routes/           # FastAPI API sub-routers
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Authoritative business & budget logic
│   │   └── ml/               # Sentence-Transformers ML models
│   └── seed_india_complete.py# Indian cities & activities seed script
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI cards, modals, & budget views
│   │   ├── pages/            # Page view controllers
│   │   └── services/         # Axios API client wrapper
│   └── test-connectivity.js  # E2E test suite
└── README.md
```