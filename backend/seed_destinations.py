import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.city import City
from app.models.activity import Activity

EXTRA_CITIES = [
    {
        "name": "Goa", "country": "India", "region": "Asia",
        "cost_index": 45.0, "popularity_score": 9.5, "latitude": 15.2993, "longitude": 74.1240,
        "tags": ["beaches", "nightlife", "seafood", "portuguese_heritage", "watersports"],
        "vibe_tags": ["relaxed", "vibrant", "tropical"],
        "climate_type": "tropical",
        "best_months": ["November", "December", "January", "February", "March"],
        "safety_index": 78.0, "budget_tier": "budget",
        "rent_index": 20.0, "restaurant_price_index": 35.0,
        "description": "Goa is India's premier coastal paradise, celebrated for golden sun-drenched beaches, Portuguese colonial architecture, vibrant night markets, and world-class seafood shacks.",
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800",
        "activities": [
            {"name": "Anjuna Beach Sunset & Flea Market", "category": "nature", "estimated_cost": 10.0, "duration_hours": 3.0, "tags": ["beach", "sunset", "shopping"], "vibe": "vibrant", "best_for": ["couple", "group", "solo"], "description": "Browse bohemian handicrafts and enjoy oceanfront seafood at sunset."},
            {"name": "Old Goa Portuguese Cathedrals Walk", "category": "history", "estimated_cost": 5.0, "duration_hours": 2.5, "tags": ["church", "heritage", "unesco"], "vibe": "cultural", "best_for": ["family", "solo"], "description": "Explore Basilica of Bom Jesus and Sé Cathedral UNESCO world heritage monuments."},
            {"name": "Dudhsagar Waterfalls Jeep Safari", "category": "adventure", "estimated_cost": 35.0, "duration_hours": 5.0, "tags": ["waterfall", "jungle", "safari"], "vibe": "thrilling", "best_for": ["group", "solo"], "description": "Off-road through Bhagwan Mahaveer Sanctuary to the majestic 4-tiered falls."},
            {"name": "Panaji Latin Quarter (Fontainhas) Food Crawl", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "tags": ["foodie", "goan", "seafood"], "vibe": "relaxing", "best_for": ["couple", "foodie"], "description": "Taste authentic Goan fish curry, Bebinca, and Poee bread in colorful alleys."},
            {"name": "Scuba Diving & Watersports at Grande Island", "category": "adventure", "estimated_cost": 45.0, "duration_hours": 4.0, "tags": ["scuba", "marine", "adventure"], "vibe": "thrilling", "best_for": ["group", "couple"], "description": "Explore vibrant coral reefs and marine life around Grande Island."},
        ]
    },
    {
        "name": "Jaipur", "country": "India", "region": "Asia",
        "cost_index": 40.0, "popularity_score": 9.2, "latitude": 26.9124, "longitude": 75.7873,
        "tags": ["palaces", "forts", "culture", "shopping", "historic"],
        "vibe_tags": ["royal", "cultural", "colorful"],
        "climate_type": "arid",
        "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 75.0, "budget_tier": "budget",
        "rent_index": 18.0, "restaurant_price_index": 30.0,
        "description": "The Pink City of Rajasthan, Jaipur mesmerizes with grand hilltop fortresses, majestic royal palaces, vibrant bazaars, and opulent Rajasthani culinary traditions.",
        "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800",
        "activities": [
            {"name": "Amber Palace & Elephant Pathway Tour", "category": "history", "estimated_cost": 15.0, "duration_hours": 3.0, "tags": ["fort", "architecture", "royal"], "vibe": "immersive", "best_for": ["family", "couple", "solo"], "description": "Marvel at the Sheesh Mahal (Mirror Palace) and Rajput architecture."},
            {"name": "Hawa Mahal & City Palace Royal Museum", "category": "sightseeing", "estimated_cost": 12.0, "duration_hours": 2.5, "tags": ["palace", "photography", "pink_city"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "Iconic honeycomb facade and royal museum courtyards."},
            {"name": "Johari Bazaar Gem & Textile Walk", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["bazaar", "jewelry", "textiles"], "vibe": "vibrant", "best_for": ["couple", "family"], "description": "Traditional jewelry, bandhani sarees, and Rajasthani handicrafts."},
            {"name": "Authentic Rajasthani Thali Dining", "category": "food", "estimated_cost": 18.0, "duration_hours": 1.5, "tags": ["thali", "dal_baati", "foodie"], "vibe": "delightful", "best_for": ["foodie", "family"], "description": "Feast on Dal Baati Churma, Gatte ki Sabzi, and sweet Ghevar."},
        ]
    },
    {
        "name": "Delhi", "country": "India", "region": "Asia",
        "cost_index": 50.0, "popularity_score": 9.4, "latitude": 28.6139, "longitude": 77.2090,
        "tags": ["heritage", "monuments", "street_food", "history", "markets"],
        "vibe_tags": ["bustling", "historic", "culinary"],
        "climate_type": "continental",
        "best_months": ["October", "November", "December", "January", "February"],
        "safety_index": 65.0, "budget_tier": "budget",
        "rent_index": 24.0, "restaurant_price_index": 38.0,
        "description": "India's dynamic capital seamlessly fuses centuries of Mughal and colonial heritage with modern cosmopolitan culture and world-famous street food.",
        "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800",
        "activities": [
            {"name": "Old Delhi Chandni Chowk Food Walk", "category": "food", "estimated_cost": 15.0, "duration_hours": 3.0, "tags": ["street_food", "parathe", "jalebi"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Sample legendary street food from centuries-old vendors."},
            {"name": "Qutub Minar & Mehrauli Heritage Park", "category": "history", "estimated_cost": 8.0, "duration_hours": 2.5, "tags": ["unesco", "minaret", "ancient"], "vibe": "cultural", "best_for": ["solo", "family"], "description": "World's tallest brick minaret and ancient Mughal tombs."},
            {"name": "Humayun's Tomb Gardens", "category": "sightseeing", "estimated_cost": 10.0, "duration_hours": 2.0, "tags": ["mughal", "garden", "architecture"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "The red sandstone inspiration behind the Taj Mahal."},
        ]
    },
    {
        "name": "Bengaluru", "country": "India", "region": "Asia",
        "cost_index": 55.0, "popularity_score": 9.0, "latitude": 12.9716, "longitude": 77.5946,
        "tags": ["tech", "craft_beer", "gardens", "cafes", "weather"],
        "vibe_tags": ["modern", "green", "youthful"],
        "climate_type": "tropical",
        "best_months": ["All Year"],
        "safety_index": 76.0, "budget_tier": "mid-range",
        "rent_index": 28.0, "restaurant_price_index": 42.0,
        "description": "The Silicon Valley of India, known as the Garden City for its lush botanical parks, buzzing microbreweries, and pleasant year-round climate.",
        "image_url": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=800",
        "activities": [
            {"name": "Lalbagh Botanical Garden Glass House Walk", "category": "nature", "estimated_cost": 5.0, "duration_hours": 2.0, "tags": ["botanical", "flowers", "park"], "vibe": "relaxing", "best_for": ["family", "couple"], "description": "Historic 240-acre botanical garden with tropical flora."},
            {"name": "Indiranagar Craft Brewery Crawl", "category": "food", "estimated_cost": 30.0, "duration_hours": 3.0, "tags": ["craft_beer", "nightlife", "pubs"], "vibe": "vibrant", "best_for": ["group", "solo"], "description": "Tour Bengaluru's famous artisan microbreweries."},
            {"name": "Bengaluru Palace Royal Guided Tour", "category": "history", "estimated_cost": 12.0, "duration_hours": 2.0, "tags": ["palace", "tudor", "heritage"], "vibe": "cultural", "best_for": ["solo", "family"], "description": "Tudor-style royal estate with ornate wood carvings and historical artifacts."},
        ]
    },
    {
        "name": "London", "country": "United Kingdom", "region": "Europe",
        "cost_index": 140.0, "popularity_score": 9.9, "latitude": 51.5074, "longitude": -0.1278,
        "tags": ["history", "museums", "theatre", "royal", "shopping"],
        "vibe_tags": ["cosmopolitan", "historic", "vibrant"],
        "climate_type": "oceanic",
        "best_months": ["May", "June", "July", "August", "September"],
        "safety_index": 74.0, "budget_tier": "luxury",
        "rent_index": 65.0, "restaurant_price_index": 90.0,
        "description": "A global capital of culture, commerce, and royalty, London seamlessly bridges iconic royal monuments with cutting-edge art and world cuisine.",
        "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800",
        "activities": [
            {"name": "Tower of London & Crown Jewels", "category": "history", "estimated_cost": 38.0, "duration_hours": 3.0, "tags": ["tower", "royal", "jewels"], "vibe": "immersive", "best_for": ["family", "couple"], "description": "Explore the medieval fortress and the British Crown Jewels."},
            {"name": "West End Musical Performance", "category": "sightseeing", "estimated_cost": 75.0, "duration_hours": 2.5, "tags": ["theatre", "musical", "entertainment"], "vibe": "luxurious", "best_for": ["couple", "solo"], "description": "World-class musical show in London's premier theatre district."},
            {"name": "Borough Market Gourmet Food Tasting", "category": "food", "estimated_cost": 30.0, "duration_hours": 2.0, "tags": ["market", "foodie", "artisan"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Artisan cheeses, street food, and oysters in London's oldest market."},
        ]
    },
    {
        "name": "Kyoto", "country": "Japan", "region": "Asia",
        "cost_index": 105.0, "popularity_score": 9.7, "latitude": 35.0116, "longitude": 135.7681,
        "tags": ["temples", "zen", "geisha", "gardens", "tradition"],
        "vibe_tags": ["peaceful", "historic", "zen"],
        "climate_type": "temperate",
        "best_months": ["March", "April", "October", "November"],
        "safety_index": 92.0, "budget_tier": "mid-range",
        "rent_index": 35.0, "restaurant_price_index": 65.0,
        "description": "The cultural heart of Japan, Kyoto boasts thousands of classical Buddhist temples, serene Zen gardens, imperial palaces, and traditional wooden machiya houses.",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800",
        "activities": [
            {"name": "Fushimi Inari 10,000 Torii Gates Hike", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 3.0, "tags": ["shrine", "hiking", "torii"], "vibe": "peaceful", "best_for": ["solo", "couple"], "description": "Walk through thousands of vermilion torii gates winding up Mount Inari."},
            {"name": "Arashiyama Bamboo Grove & Monkey Park", "category": "nature", "estimated_cost": 8.0, "duration_hours": 2.5, "tags": ["bamboo", "nature", "wildlife"], "vibe": "peaceful", "best_for": ["couple", "family"], "description": "Towering bamboo stalks and scenic mountain river walks."},
            {"name": "Gion Traditional Tea Ceremony & Kaiseki", "category": "food", "estimated_cost": 65.0, "duration_hours": 2.0, "tags": ["tea", "ceremony", "kaiseki"], "vibe": "cultural", "best_for": ["couple", "solo"], "description": "Experience authentic matcha preparation and multi-course Kyoto dining."},
        ]
    }
]

async def seed_extra():
    async with AsyncSessionLocal() as session:
        print("[Seed] Seeding extra popular destinations...")
        for c in EXTRA_CITIES:
            # Check if city already exists
            res = await session.execute(select(City).where(City.name == c["name"]))
            existing = res.scalar_one_or_none()
            if existing:
                print(f"[Seed] City {c['name']} already exists in database.")
                continue

            city = City(
                name=c["name"],
                country=c["country"],
                region=c["region"],
                description=c["description"],
                cost_index=c["cost_index"],
                popularity_score=c["popularity_score"],
                latitude=c["latitude"],
                longitude=c["longitude"],
                image_url=c["image_url"],
                tags=c.get("tags"),
                vibe_tags=c.get("vibe_tags"),
                climate_type=c.get("climate_type"),
                best_months=c.get("best_months"),
                safety_index=c.get("safety_index", 80.0),
                budget_tier=c.get("budget_tier", "mid"),
                rent_index=c.get("rent_index", 40.0),
                restaurant_price_index=c.get("restaurant_price_index", 50.0),
            )
            session.add(city)
            await session.flush()
            print(f"[Seed] Added city: {city.name} ({city.country})")

            for a in c.get("activities", []):
                act = Activity(
                    city_id=city.id,
                    name=a["name"],
                    category=a["category"],
                    description=a["description"],
                    estimated_cost=a["estimated_cost"],
                    duration_hours=a["duration_hours"],
                    tags=a.get("tags"),
                    vibe=a.get("vibe"),
                    best_for=a.get("best_for"),
                )
                session.add(act)

        await session.commit()
        print("[Seed] Extra destinations and activities successfully added to Supabase!")

if __name__ == "__main__":
    asyncio.run(seed_extra())
