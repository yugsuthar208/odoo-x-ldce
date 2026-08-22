import logging
from typing import List, Optional
import httpx
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.city import City
from app.schemas.city import CityCreate

logger = logging.getLogger("CityController")


async def discover_and_create_city(db: AsyncSession, query_text: str) -> Optional[City]:
    """Geocodes a destination and creates standard starter activities."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query_text, "format": "json", "limit": 1, "addressdetails": 1}
    headers = {"User-Agent": "GlobeTrotterTravelApp/1.0 (contact: info@globetrotter.local)"}

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data:
            return None

        item = data[0]
        address = item.get("address", {})
        city_name = query_text.strip().title()
        country_name = address.get("country", "Global")
        lat = float(item.get("lat", 0.0))
        lon = float(item.get("lon", 0.0))

        # Check again if city exists with that exact name
        existing = await db.execute(select(City).where(City.name.ilike(city_name)))
        existing_city = existing.scalar_one_or_none()
        if existing_city:
            return existing_city

        new_city = City(
            name=city_name,
            country=country_name,
            region=address.get("continent", "Global"),
            description=f"Explore the sights, culture, cuisine, and attractions of {city_name}, {country_name}.",
            cost_index=55.0 if "India" in country_name else 75.0,
            popularity_score=8.5,
            latitude=lat,
            longitude=lon,
            image_url="https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800",
            tags=["sightseeing", "culture", "discovery", "travel"],
            vibe_tags=["charming", "cultural"],
            climate_type="temperate",
            best_months=["All Year"],
            safety_index=80.0,
            budget_tier="mid",
            rent_index=30.0,
            restaurant_price_index=45.0,
        )
        db.add(new_city)
        await db.flush()

        # Add starter activities
        starter_activities = [
            {"name": f"{city_name} Historic City Center Tour", "category": "history", "estimated_cost": 15.0, "duration_hours": 2.5, "description": f"Guided walking tour around key monuments and heritage sites in {city_name}."},
            {"name": f"{city_name} Local Food & Market Walk", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "description": f"Taste iconic regional delicacies and street foods of {city_name}."},
            {"name": f"{city_name} Scenic Panoramic Sunset", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 1.5, "description": f"Enjoy sunset views and photography spots across {city_name}."},
            {"name": f"{city_name} Cultural Museum Experience", "category": "sightseeing", "estimated_cost": 12.0, "duration_hours": 2.0, "description": f"Discover the traditions and rich cultural exhibits of {city_name}."},
        ]

        for act in starter_activities:
            a = Activity(
                city_id=new_city.id,
                name=act["name"],
                category=act["category"],
                description=act["description"],
                estimated_cost=act["estimated_cost"],
                duration_hours=act["duration_hours"],
                tags=["popular", "starter"],
                vibe="cultural",
                best_for=["solo", "couple", "family"],
            )
            db.add(a)

        await db.commit()
        await db.refresh(new_city)
        return new_city


async def list_cities(
    db: AsyncSession,
    search: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
) -> List[City]:
    """
    Searches and filters destination cities by name, country, and region.
    If no cities match the search query, dynamically discovers the destination.
    """
    query = select(City).order_by(City.popularity_score.desc())

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                City.name.ilike(search_pattern),
                City.country.ilike(search_pattern),
                City.region.ilike(search_pattern),
            )
        )

    if region:
        query = query.where(City.region.ilike(f"%{region.strip()}%"))

    if country:
        query = query.where(City.country.ilike(f"%{country.strip()}%"))

    result = await db.execute(query)
    cities = list(result.scalars().all())

    # If no cities matched the search query, dynamically discover destination via OpenStreetMap
    if not cities and search and len(search.strip()) >= 2:
        try:
            discovered = await discover_and_create_city(db=db, query_text=search.strip())
            if discovered:
                cities.append(discovered)
        except Exception as e:
            logger.warning(f"Dynamic city discovery failed: {e}")

    return cities


async def get_city(db: AsyncSession, city_id: str) -> City:
    """Retrieves a single city with its activities."""
    query = (
        select(City)
        .options(selectinload(City.activities))
        .where(City.id == city_id)
    )
    result = await db.execute(query)
    city = result.scalar_one_or_none()

    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id '{city_id}' not found",
        )
    return city


async def create_city(db: AsyncSession, payload: CityCreate) -> City:
    """Creates a new city."""
    city = City(
        name=payload.name.strip(),
        country=payload.country.strip(),
        region=payload.region.strip() if payload.region else None,
        description=payload.description,
        cost_index=payload.cost_index,
        popularity_score=payload.popularity_score,
        latitude=payload.latitude or 0.0,
        longitude=payload.longitude or 0.0,
        image_url=payload.image_url,
    )
    db.add(city)
    await db.flush()
    await db.refresh(city)
    return city
