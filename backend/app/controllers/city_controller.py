from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.city import City
from app.schemas.city import CityCreate


async def list_cities(
    db: AsyncSession,
    search: Optional[str] = None,
    region: Optional[str] = None,
) -> List[City]:
    """
    Searches and filters destination cities by name/country query and region.
    """
    query = select(City).order_by(City.popularity_score.desc())

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                City.name.ilike(search_pattern),
                City.country.ilike(search_pattern),
            )
        )

    if region:
        query = query.where(City.region.ilike(f"%{region.strip()}%"))

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_city(db: AsyncSession, city_id: str) -> City:
    """
    Retrieves a single city with its activities.
    """
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
    """Creates a new city in the system (useful for seeding and admin)."""
    city = City(
        name=payload.name.strip(),
        country=payload.country.strip(),
        region=payload.region.strip(),
        cost_index=payload.cost_index,
        popularity_score=payload.popularity_score,
        image_url=payload.image_url,
    )
    db.add(city)
    await db.flush()
    await db.refresh(city)
    return city
