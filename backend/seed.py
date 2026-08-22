import asyncio
from datetime import date, time, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, Base, engine
from app.middleware.auth import hash_password
from app.models.activity import Activity
from app.models.budget import Budget
from app.models.city import City
from app.models.itinerary_item import ItineraryItem
from app.models.stop import TripStop
from app.models.trip import Trip
from app.models.user import User

# 20 Global Cities with Full Tags, Vibes, Climate, and Cost Metrics
CITIES_DATA = [
    # --- Europe (8) ---
    {
        "name": "Paris", "country": "France", "region": "Europe",
        "cost_index": 130.0, "popularity_score": 9.8, "latitude": 48.8566, "longitude": 2.3522,
        "tags": ["romantic", "fashion", "art", "foodie", "historic"],
        "vibe_tags": ["vibrant", "cultural", "luxurious"],
        "climate_type": "oceanic",
        "best_months": ["April", "May", "June", "September", "October"],
        "safety_index": 72.0, "budget_tier": "luxury",
        "rent_index": 52.0, "restaurant_price_index": 85.0,
        "description": "The City of Light is renowned for its world-class art, fashion, gastronomy, and culture. Its 19th-century cityscape is crisscrossed by wide boulevards and the River Seine.",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "activities": [
            {"name": "Eiffel Tower Summit Tour", "category": "sightseeing", "estimated_cost": 35.0, "duration_hours": 2.5, "tags": ["iconic", "views", "romantic"], "vibe": "thrilling", "best_for": ["couple", "solo", "family"], "description": "Elevator ascent to the highest deck overlooking Paris."},
            {"name": "Louvre Museum Masterpieces", "category": "history", "estimated_cost": 22.0, "duration_hours": 3.0, "tags": ["art", "cultural", "historic"], "vibe": "immersive", "best_for": ["solo", "couple"], "description": "Guided walking tour through Renaissance art and antiquities."},
            {"name": "Montmartre Bakery & Pastry Walk", "category": "food", "estimated_cost": 45.0, "duration_hours": 2.0, "tags": ["foodie", "pastry", "walking"], "vibe": "relaxing", "best_for": ["couple", "foodie"], "description": "Sample fresh baguettes, croissants, and macarons."},
            {"name": "Seine River Sunset Cruise", "category": "nature", "estimated_cost": 20.0, "duration_hours": 1.5, "tags": ["boat", "scenic", "sunset"], "vibe": "relaxing", "best_for": ["couple", "family"], "description": "Scenic boat cruise passing Notre Dame and historic bridges."},
            {"name": "Champs-Élysées Luxury Boutique Walk", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["luxury", "fashion", "shopping"], "vibe": "luxurious", "best_for": ["solo", "couple"], "description": "Stroll down the world's most famous shopping avenue."},
        ]
    },
    {
        "name": "Rome", "country": "Italy", "region": "Europe",
        "cost_index": 110.0, "popularity_score": 9.6, "latitude": 41.9028, "longitude": 12.4964,
        "tags": ["historic", "ancient", "foodie", "architecture", "monuments"],
        "vibe_tags": ["cultural", "lively", "historic"],
        "climate_type": "mediterranean",
        "best_months": ["April", "May", "September", "October"],
        "safety_index": 68.0, "budget_tier": "mid-range",
        "rent_index": 38.5, "restaurant_price_index": 72.0,
        "description": "Rome is a living open-air museum boasting nearly 3,000 years of globally influential art, architecture, and culture. Ancient ruins like the Forum and Colosseum evoke the power of the Roman Empire.",
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800",
        "activities": [
            {"name": "Colosseum & Roman Forum", "category": "history", "estimated_cost": 30.0, "duration_hours": 3.0, "tags": ["ancient", "gladiators", "monument"], "vibe": "immersive", "best_for": ["solo", "family"], "description": "Step into the gladiatorial arena and imperial palace ruins."},
            {"name": "Vatican & Sistine Chapel", "category": "sightseeing", "estimated_cost": 38.0, "duration_hours": 3.5, "tags": ["renaissance", "religious", "art"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "Michelangelo's ceiling fresco and Saint Peter's Basilica."},
            {"name": "Trastevere Street Food Crawl", "category": "food", "estimated_cost": 50.0, "duration_hours": 2.5, "tags": ["foodie", "pasta", "gelato"], "vibe": "lively", "best_for": ["group", "couple"], "description": "Authentic supplì, wood-fired pizza slices, and gelato."},
            {"name": "Appian Way Ancient E-Bike Tour", "category": "adventure", "estimated_cost": 48.0, "duration_hours": 3.5, "tags": ["cycling", "nature", "outdoor"], "vibe": "thrilling", "best_for": ["solo", "couple"], "description": "Cycle the preserved cobblestone Roman military highway."},
            {"name": "Villa Borghese Thermal Spa & Wellness", "category": "wellness", "estimated_cost": 60.0, "duration_hours": 2.0, "tags": ["spa", "thermal", "relaxation"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Relaxing mineral water baths and herbal steam rooms."},
        ]
    },
    {
        "name": "Barcelona", "country": "Spain", "region": "Europe",
        "cost_index": 95.0, "popularity_score": 9.4, "latitude": 41.3851, "longitude": 2.1734,
        "tags": ["beaches", "gaudi", "tapas", "nightlife", "architecture"],
        "vibe_tags": ["vibrant", "artistic", "coastal"],
        "climate_type": "mediterranean",
        "best_months": ["May", "June", "September", "October"],
        "safety_index": 74.0, "budget_tier": "mid-range",
        "rent_index": 36.2, "restaurant_price_index": 60.5,
        "description": "Barcelona is famed for its Mediterranean coastline and Antoni Gaudí's whimsical architecture. The city combines vibrant seaside culture with rich Catalan artistic heritage.",
        "image_url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800",
        "activities": [
            {"name": "Sagrada Familia Basilica Tour", "category": "sightseeing", "estimated_cost": 28.0, "duration_hours": 2.0, "tags": ["architecture", "gaudi", "iconic"], "vibe": "immersive", "best_for": ["couple", "family"], "description": "Explore Gaudi's awe-inspiring modernist architectural cathedral."},
            {"name": "Park Güell Mosaic Exploration", "category": "nature", "estimated_cost": 15.0, "duration_hours": 2.0, "tags": ["mosaic", "views", "park"], "vibe": "relaxing", "best_for": ["family", "couple"], "description": "Color-rich mosaic benches with views of the Mediterranean."},
            {"name": "Boqueria Market Tapas & Sangria", "category": "food", "estimated_cost": 40.0, "duration_hours": 2.0, "tags": ["tapas", "seafood", "market"], "vibe": "lively", "best_for": ["group", "couple"], "description": "Taste Jamon Iberico, grilled seafood tapas, and local cava."},
            {"name": "Barceloneta Paddleboarding & Surf", "category": "adventure", "estimated_cost": 35.0, "duration_hours": 2.0, "tags": ["water", "beach", "sports"], "vibe": "thrilling", "best_for": ["solo", "group"], "description": "Coastal watersports along the sunny Barcelona shores."},
            {"name": "Gothic Quarter Artisanal Boutiques", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "tags": ["vintage", "leather", "shopping"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "Discover local leather goods and vintage jewelers."},
        ]
    },
    {
        "name": "Amsterdam", "country": "Netherlands", "region": "Europe",
        "cost_index": 125.0, "popularity_score": 9.2, "latitude": 52.3676, "longitude": 4.9041,
        "tags": ["canals", "museums", "cycling", "nightlife", "beer"],
        "vibe_tags": ["relaxed", "cultural", "lively"],
        "climate_type": "oceanic",
        "best_months": ["April", "May", "June", "July", "August"],
        "safety_index": 82.0, "budget_tier": "luxury",
        "rent_index": 56.4, "restaurant_price_index": 78.0,
        "description": "Amsterdam is known for its artistic heritage, elaborate canal system, and narrow houses with gabled facades. Cycling is key to the city's character, with countless bike paths.",
        "image_url": "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800",
        "activities": [
            {"name": "Rijksmuseum Dutch Masters", "category": "history", "estimated_cost": 25.0, "duration_hours": 2.5, "tags": ["art", "rembrandt", "museum"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "Admire Rembrandt's Night Watch and Golden Age masterpieces."},
            {"name": "Canal Belt Historic Boat Cruise", "category": "sightseeing", "estimated_cost": 20.0, "duration_hours": 1.5, "tags": ["cruise", "canals", "scenic"], "vibe": "relaxing", "best_for": ["couple", "family"], "description": "Cruise past UNESCO heritage 17th-century canal houses."},
            {"name": "Jordaan Cheese & Stroopwafel Safari", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.0, "tags": ["cheese", "dessert", "foodie"], "vibe": "relaxing", "best_for": ["couple", "family"], "description": "Gouda cheese tastings and fresh hot stroopwafels."},
            {"name": "Countryside Windmill Bike Trek", "category": "nature", "estimated_cost": 45.0, "duration_hours": 4.0, "tags": ["cycling", "windmills", "countryside"], "vibe": "thrilling", "best_for": ["solo", "group"], "description": "Cycle out to Zaanse Schans historic working windmills."},
            {"name": "Nine Streets Boutique Shopping", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["boutiques", "fashion", "vintage"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "Charming district packed with indie fashion and bookshops."},
        ]
    },
    {
        "name": "Prague", "country": "Czech Republic", "region": "Europe",
        "cost_index": 75.0, "popularity_score": 8.9, "latitude": 50.0755, "longitude": 14.4378,
        "tags": ["historic", "romantic", "beer", "gothic", "castles"],
        "vibe_tags": ["cultural", "relaxed", "fairytale"],
        "climate_type": "continental",
        "best_months": ["May", "June", "September"],
        "safety_index": 79.0, "budget_tier": "mid-range",
        "rent_index": 29.8, "restaurant_price_index": 48.2,
        "description": "Prague is known as the City of a Hundred Spires, with a historic core reflecting millennia of European architecture. Charles Bridge and Prague Castle provide unforgettable skyline vistas.",
        "image_url": "https://images.unsplash.com/photo-1541849546-216549ae216d?w=800",
        "activities": [
            {"name": "Prague Castle & St. Vitus Cathedral", "category": "history", "estimated_cost": 18.0, "duration_hours": 3.0, "tags": ["gothic", "castle", "views"], "vibe": "cultural", "best_for": ["family", "couple"], "description": "Largest ancient castle complex in the world."},
            {"name": "Old Town Square & Astronomical Clock", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 1.5, "tags": ["monument", "clock", "square"], "vibe": "immersive", "best_for": ["solo", "couple"], "description": "Gothic spires and the mechanical clock show."},
            {"name": "Traditional Bohemian Beer & Goulash", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "tags": ["beer", "foodie", "dining"], "vibe": "lively", "best_for": ["group", "solo"], "description": "Pilsner beer tasting paired with slow-cooked beef goulash."},
            {"name": "Vltava River Kayaking Excursion", "category": "adventure", "estimated_cost": 30.0, "duration_hours": 2.0, "tags": ["kayak", "river", "outdoor"], "vibe": "thrilling", "best_for": ["solo", "group"], "description": "Paddle beneath historic arches of Charles Bridge."},
            {"name": "Beer Spa & Thermal Hop Bath", "category": "wellness", "estimated_cost": 65.0, "duration_hours": 1.5, "tags": ["spa", "beer", "bath"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Relax in warm oak tubs infused with natural hop extracts."},
        ]
    },
    {
        "name": "Vienna", "country": "Austria", "region": "Europe",
        "cost_index": 115.0, "popularity_score": 9.1, "latitude": 48.2082, "longitude": 16.3738,
        "tags": ["imperial", "classical-music", "palaces", "coffeehouse", "art"],
        "vibe_tags": ["luxurious", "cultural", "elegant"],
        "climate_type": "continental",
        "best_months": ["April", "May", "September", "October"],
        "safety_index": 84.0, "budget_tier": "luxury",
        "rent_index": 41.0, "restaurant_price_index": 69.4,
        "description": "Vienna's artistic and intellectual legacy was shaped by residents including Mozart, Beethoven, and Freud. The city is celebrated for its imperial palaces and vibrant coffeehouse culture.",
        "image_url": "https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800",
        "activities": [
            {"name": "Schönbrunn Imperial Palace", "category": "history", "estimated_cost": 26.0, "duration_hours": 3.0, "tags": ["habsburg", "palace", "gardens"], "vibe": "luxurious", "best_for": ["family", "couple"], "description": "Habsburg summer residence and Baroque gardens."},
            {"name": "St. Stephen's Cathedral Tower Climb", "category": "sightseeing", "estimated_cost": 12.0, "duration_hours": 1.5, "tags": ["gothic", "tower", "views"], "vibe": "thrilling", "best_for": ["solo", "couple"], "description": "Gothic cathedral with panoramic views across Vienna."},
            {"name": "Viennese Coffeehouse & Sachertorte", "category": "food", "estimated_cost": 20.0, "duration_hours": 1.5, "tags": ["coffee", "sachertorte", "cafe"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Classic Melange coffee and original chocolate apricot cake."},
            {"name": "Wienerwald Woods Nature Hike", "category": "nature", "estimated_cost": 0.0, "duration_hours": 3.0, "tags": ["hiking", "woods", "forest"], "vibe": "relaxing", "best_for": ["solo", "nature"], "description": "Lush beech forests overlooking the Danube River."},
            {"name": "Graben & Kärntner Straße Promenade", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["promenade", "shopping", "luxury"], "vibe": "luxurious", "best_for": ["couple", "solo"], "description": "Pedestrian avenues filled with Austrian craftsmanship."},
        ]
    },
    {
        "name": "Lisbon", "country": "Portugal", "region": "Europe",
        "cost_index": 85.0, "popularity_score": 9.3, "latitude": 38.7223, "longitude": -9.1393,
        "tags": ["coastal", "fado", "seafood", "tiles", "hills"],
        "vibe_tags": ["warm", "vibrant", "artistic"],
        "climate_type": "mediterranean",
        "best_months": ["March", "April", "May", "September", "October"],
        "safety_index": 80.0, "budget_tier": "mid-range",
        "rent_index": 34.0, "restaurant_price_index": 52.0,
        "description": "Lisbon is a coastal capital of pastel buildings, steep hills, and melancholic Fado music. From imposing São Jorge Castle, the view encompasses old quarter buildings and the Tagus Estuary.",
        "image_url": "https://images.unsplash.com/photo-1509840841025-9088ba78a826?w=800",
        "activities": [
            {"name": "Jerónimos Monastery & Belém Tower", "category": "history", "estimated_cost": 15.0, "duration_hours": 2.5, "tags": ["unesco", "monastery", "monument"], "vibe": "cultural", "best_for": ["couple", "family"], "description": "Manueline architecture and maritime Age of Discovery history."},
            {"name": "Tram 28 Scenic City Ride", "category": "sightseeing", "estimated_cost": 4.0, "duration_hours": 1.0, "tags": ["tram", "iconic", "views"], "vibe": "immersive", "best_for": ["solo", "couple"], "description": "Vintage yellow tram climbing Lisbon's steep hills."},
            {"name": "Pastéis de Belém & Seafood Tasting", "category": "food", "estimated_cost": 30.0, "duration_hours": 2.0, "tags": ["pastry", "seafood", "tasting"], "vibe": "relaxing", "best_for": ["foodie", "couple"], "description": "Warm custard tarts and garlic butter grilled prawns."},
            {"name": "Sintra Mountains Trail Hike", "category": "adventure", "estimated_cost": 22.0, "duration_hours": 4.0, "tags": ["hiking", "palace", "mountains"], "vibe": "thrilling", "best_for": ["solo", "group"], "description": "Hike through mystical forests up to colorful Pena Palace."},
            {"name": "LX Factory Concept Stores", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["indie", "art", "shopping"], "vibe": "artistic", "best_for": ["solo", "couple"], "description": "Revitalized industrial complex of indie makers and designers."},
        ]
    },
    {
        "name": "Athens", "country": "Greece", "region": "Europe",
        "cost_index": 80.0, "popularity_score": 9.0, "latitude": 37.9838, "longitude": 23.7275,
        "tags": ["ancient-ruins", "mythology", "mediterranean", "meze", "beaches"],
        "vibe_tags": ["historic", "sunny", "cultural"],
        "climate_type": "mediterranean",
        "best_months": ["April", "May", "October", "November"],
        "safety_index": 67.0, "budget_tier": "budget",
        "rent_index": 22.4, "restaurant_price_index": 54.0,
        "description": "Athens was the heart of Ancient Greece, a powerful civilization and empire. Landmarks including the 5th-century BC Acropolis fortress still dominate the sun-drenched capital.",
        "image_url": "https://images.unsplash.com/photo-1555993539-1732b0258235?w=800",
        "activities": [
            {"name": "Acropolis & Parthenon Monument", "category": "history", "estimated_cost": 25.0, "duration_hours": 3.0, "tags": ["acropolis", "ancient", "parthenon"], "vibe": "cultural", "best_for": ["family", "solo"], "description": "Iconic ancient citadel and temple to goddess Athena."},
            {"name": "Plaka Ancient Quarter Walk", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["walking", "plaka", "neoclassical"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Village-like labyrinth of neoclassical architecture."},
            {"name": "Authentic Souvlaki & Meze Safari", "category": "food", "estimated_cost": 22.0, "duration_hours": 2.0, "tags": ["souvlaki", "greek-food", "wine"], "vibe": "lively", "best_for": ["group", "foodie"], "description": "Tzatziki, grilled souvlaki skewers, and Greek wine."},
            {"name": "Mount Lycabettus Sunset Hike", "category": "nature", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["sunset", "hiking", "views"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Limestone hill summit offering Aegean sea views."},
            {"name": "Monastiraki Flea Market", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["market", "flea", "antiques"], "vibe": "lively", "best_for": ["solo", "group"], "description": "Bustling market for Greek olive oil, leather, and relics."},
        ]
    },

    # --- Asia (7) ---
    {
        "name": "Tokyo", "country": "Japan", "region": "Asia",
        "cost_index": 120.0, "popularity_score": 9.9, "latitude": 35.6762, "longitude": 139.6503,
        "tags": ["technology", "anime", "foodie", "historic", "shopping"],
        "vibe_tags": ["vibrant", "cultural", "unique"],
        "climate_type": "continental",
        "best_months": ["March", "April", "October", "November"],
        "safety_index": 91.0, "budget_tier": "mid-range",
        "rent_index": 42.6, "restaurant_price_index": 58.0,
        "description": "Tokyo mixes ultra-modern skyscrapers and neon signs with historic temples. The city is a culinary capital of world-renowned gastronomy, pristine transport, and cutting-edge pop culture.",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800",
        "activities": [
            {"name": "Senso-ji Temple & Asakusa Heritage", "category": "history", "estimated_cost": 10.0, "duration_hours": 2.0, "tags": ["temple", "asakusa", "heritage"], "vibe": "cultural", "best_for": ["family", "solo"], "description": "Tokyo's oldest Buddhist temple and traditional stall street."},
            {"name": "Shibuya Sky Observation Deck", "category": "sightseeing", "estimated_cost": 20.0, "duration_hours": 1.5, "tags": ["shibuya", "skyline", "views"], "vibe": "thrilling", "best_for": ["couple", "solo"], "description": "Panoramic open-air view of Shibuya Scramble intersection."},
            {"name": "Tsukiji Outer Market Sushi Safari", "category": "food", "estimated_cost": 55.0, "duration_hours": 2.5, "tags": ["sushi", "tsukiji", "wagyu"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Ultra-fresh sashimi, wagyu skewers, and tamagoyaki."},
            {"name": "Akihabara Tech & Anime Shopping", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "tags": ["anime", "gaming", "electronics"], "vibe": "vibrant", "best_for": ["solo", "group"], "description": "World-famous district for gadgets, manga, and retro games."},
            {"name": "Natural Onsen Hot Spring & Spa", "category": "wellness", "estimated_cost": 30.0, "duration_hours": 2.0, "tags": ["onsen", "spa", "mineral"], "vibe": "relaxing", "best_for": ["solo", "couple"], "description": "Traditional Japanese mineral hot springs and sauna."},
        ]
    },
    {
        "name": "Bangkok", "country": "Thailand", "region": "Asia",
        "cost_index": 55.0, "popularity_score": 9.3, "latitude": 13.7563, "longitude": 100.5018,
        "tags": ["street-food", "temples", "nightlife", "markets", "massages"],
        "vibe_tags": ["vibrant", "exotic", "bustling"],
        "climate_type": "tropical",
        "best_months": ["November", "December", "January", "February"],
        "safety_index": 64.0, "budget_tier": "budget",
        "rent_index": 21.0, "restaurant_price_index": 32.5,
        "description": "Bangkok is famous for ornate shrines, bustling boat-filled canals, and vibrant street life. The city offers rich contrasts between golden royal palaces and towering modern rooftops.",
        "image_url": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800",
        "activities": [
            {"name": "Grand Palace & Emerald Buddha", "category": "history", "estimated_cost": 16.0, "duration_hours": 3.0, "tags": ["palace", "buddha", "temple"], "vibe": "cultural", "best_for": ["family", "couple"], "description": "Spectacular royal grounds and holy Buddhist temple."},
            {"name": "Wat Arun Temple of Dawn", "category": "sightseeing", "estimated_cost": 5.0, "duration_hours": 1.5, "tags": ["temple", "river", "porcelain"], "vibe": "immersive", "best_for": ["solo", "couple"], "description": "Porcelain-decorated river temple with majestic spire."},
            {"name": "Yaowarat Chinatown Street Food Crawl", "category": "food", "estimated_cost": 20.0, "duration_hours": 2.5, "tags": ["street-food", "chinatown", "pad-thai"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Pad Thai, crispy pork, and mango sticky rice."},
            {"name": "Chatuchak Weekend Market Trek", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 3.0, "tags": ["market", "shopping", "crafts"], "vibe": "bustling", "best_for": ["solo", "group"], "description": "Over 15,000 stalls of Thai crafts, clothing, and food."},
            {"name": "Traditional Royal Thai Massage", "category": "wellness", "estimated_cost": 25.0, "duration_hours": 1.5, "tags": ["massage", "spa", "wellness"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Deep acupressure and yoga-assisted relaxation."},
        ]
    },
    {
        "name": "Bali", "country": "Indonesia", "region": "Asia",
        "cost_index": 45.0, "popularity_score": 9.5, "latitude": -8.4095, "longitude": 115.1889,
        "tags": ["beaches", "spiritual", "nature", "yoga", "nightlife"],
        "vibe_tags": ["relaxed", "adventurous", "spiritual"],
        "climate_type": "tropical",
        "best_months": ["April", "May", "June", "July", "August"],
        "safety_index": 65.0, "budget_tier": "budget",
        "rent_index": 18.5, "restaurant_price_index": 28.0,
        "description": "Bali is an Indonesian island paradise known for its forested volcanic mountains, iconic rice paddies, and coral reefs. It is home to spiritual religious sites such as cliffside Uluwatu Temple.",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
        "activities": [
            {"name": "Uluwatu Sunset Temple & Fire Dance", "category": "sightseeing", "estimated_cost": 15.0, "duration_hours": 2.5, "tags": ["temple", "dance", "sunset"], "vibe": "immersive", "best_for": ["couple", "family"], "description": "Perched cliff views paired with hypnotic Kecak fire dance."},
            {"name": "Tegallalang Emerald Rice Terraces", "category": "nature", "estimated_cost": 8.0, "duration_hours": 2.0, "tags": ["rice-fields", "nature", "swing"], "vibe": "relaxing", "best_for": ["solo", "couple"], "description": "Stepped green hillside trails and jungle canopy swings."},
            {"name": "Jimbaran Bay Beach Seafood Feast", "category": "food", "estimated_cost": 30.0, "duration_hours": 2.0, "tags": ["seafood", "beach", "dining"], "vibe": "romantic", "best_for": ["couple", "group"], "description": "Fresh grilled snapper and prawns served on the sand."},
            {"name": "Mount Batur Sunrise Volcano Hike", "category": "adventure", "estimated_cost": 45.0, "duration_hours": 5.0, "tags": ["volcano", "hiking", "sunrise"], "vibe": "thrilling", "best_for": ["solo", "group"], "description": "Pre-dawn trek to active volcano crater for cloud sunrise."},
            {"name": "Ubud Herbal Yoga & Spa Retreat", "category": "wellness", "estimated_cost": 35.0, "duration_hours": 2.5, "tags": ["yoga", "spa", "flower-bath"], "vibe": "relaxing", "best_for": ["solo", "couple"], "description": "Flower petal bath and outdoor tropical yoga session."},
        ]
    },
    {
        "name": "Singapore", "country": "Singapore", "region": "Asia",
        "cost_index": 140.0, "popularity_score": 9.1, "latitude": 1.3521, "longitude": 103.8198,
        "tags": ["modern", "gardens", "street-food", "luxury", "cleanliness"],
        "vibe_tags": ["futuristic", "luxurious", "clean"],
        "climate_type": "tropical",
        "best_months": ["January", "February", "June", "July"],
        "safety_index": 93.0, "budget_tier": "luxury",
        "rent_index": 75.4, "restaurant_price_index": 72.0,
        "description": "Singapore is a global financial center and island city-state known for cleanliness and tropical garden city architecture. It features UNESCO botanical gardens and world-class street food.",
        "image_url": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800",
        "activities": [
            {"name": "Gardens by the Bay & Cloud Forest", "category": "nature", "estimated_cost": 28.0, "duration_hours": 3.0, "tags": ["gardens", "supertrees", "waterfall"], "vibe": "futuristic", "best_for": ["family", "couple"], "description": "Futuristic vertical Supertrees and indoor waterfall dome."},
            {"name": "Marina Bay Sands SkyPark Observation", "category": "sightseeing", "estimated_cost": 24.0, "duration_hours": 1.5, "tags": ["skyline", "views", "skypark"], "vibe": "luxurious", "best_for": ["couple", "solo"], "description": "57th floor panoramic harbor and skyline views."},
            {"name": "Michelin Hawker Center Food Tour", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "tags": ["hawker", "michelin", "chicken-rice"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Hainanese chicken rice, laksa noodle soup, and satay."},
            {"name": "Orchard Road Luxury Malls", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "tags": ["shopping", "luxury", "fashion"], "vibe": "luxurious", "best_for": ["solo", "couple"], "description": "Premier retail street with international fashion flagships."},
            {"name": "Sentosa Mega Adventure Zipline", "category": "adventure", "estimated_cost": 45.0, "duration_hours": 2.0, "tags": ["zipline", "adventure", "beach"], "vibe": "thrilling", "best_for": ["solo", "group"], "description": "High-speed 450m canopy zipline down to Siloso beach."},
        ]
    },
    {
        "name": "Istanbul", "country": "Turkey", "region": "Asia",
        "cost_index": 65.0, "popularity_score": 9.2, "latitude": 41.0082, "longitude": 28.9784,
        "tags": ["bazaars", "history", "mosques", "bosphorus", "foodie"],
        "vibe_tags": ["exotic", "historic", "vibrant"],
        "climate_type": "mediterranean",
        "best_months": ["April", "May", "September", "October"],
        "safety_index": 60.0, "budget_tier": "budget",
        "rent_index": 24.8, "restaurant_price_index": 41.0,
        "description": "Istanbul straddles Europe and Asia across the Bosphorus Strait. Its historic center reflects cultural influences of the many empires that once ruled here.",
        "image_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800",
        "activities": [
            {"name": "Hagia Sophia & Blue Mosque", "category": "history", "estimated_cost": 25.0, "duration_hours": 3.0, "tags": ["mosque", "byzantine", "mosaics"], "vibe": "cultural", "best_for": ["family", "couple"], "description": "Stunning Byzantine dome mosaics and Ottoman minarets."},
            {"name": "Bosphorus Strait Sunset Cruise", "category": "sightseeing", "estimated_cost": 15.0, "duration_hours": 2.0, "tags": ["cruise", "sunset", "bosphorus"], "vibe": "romantic", "best_for": ["couple", "solo"], "description": "Sail between European and Asian continents at dusk."},
            {"name": "Grand Bazaar Spice & Delights Tour", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "tags": ["bazaar", "spices", "shopping"], "vibe": "bustling", "best_for": ["solo", "group"], "description": "Over 4,000 shops of Turkish carpets, ceramics, and sweets."},
            {"name": "Kebabs, Baklava & Turkish Coffee", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "tags": ["kebab", "baklava", "coffee"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Sample charcoal lamb kebabs and pistachio baklava."},
            {"name": "Historic Turkish Hamam Bath Experience", "category": "wellness", "estimated_cost": 50.0, "duration_hours": 1.5, "tags": ["hamam", "spa", "massage"], "vibe": "relaxing", "best_for": ["solo", "couple"], "description": "Marble steam room, body scrub, and foam massage."},
        ]
    },
    {
        "name": "Dubai", "country": "United Arab Emirates", "region": "Asia",
        "cost_index": 160.0, "popularity_score": 9.3, "latitude": 25.2048, "longitude": 55.2708,
        "tags": ["luxury", "skyscrapers", "desert", "shopping", "nightlife"],
        "vibe_tags": ["luxurious", "futuristic", "opulent"],
        "climate_type": "arid",
        "best_months": ["November", "December", "January", "February", "March"],
        "safety_index": 88.0, "budget_tier": "luxury",
        "rent_index": 58.2, "restaurant_price_index": 70.0,
        "description": "Dubai is known for luxury shopping, ultramodern architecture, and a lively nightlife scene. Burj Khalifa, an 830m-tall tower, dominates the skyscraper-filled skyline.",
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800",
        "activities": [
            {"name": "Burj Khalifa Top of the World View", "category": "sightseeing", "estimated_cost": 45.0, "duration_hours": 2.0, "tags": ["burj-khalifa", "skyline", "views"], "vibe": "thrilling", "best_for": ["couple", "family"], "description": "Ascend the world's tallest tower for desert and sea views."},
            {"name": "Red Dune 4x4 Desert Safari & Camp", "category": "adventure", "estimated_cost": 65.0, "duration_hours": 5.0, "tags": ["desert", "safari", "bbq"], "vibe": "thrilling", "best_for": ["group", "family"], "description": "Sand dune bashing, camel riding, and starlit BBQ."},
            {"name": "Dubai Mall & Underwater Aquarium", "category": "shopping", "estimated_cost": 30.0, "duration_hours": 3.0, "tags": ["mall", "aquarium", "shopping"], "vibe": "luxurious", "best_for": ["family", "solo"], "description": "Massive mall featuring indoor zoo and gold souk."},
            {"name": "Emirati Food & Spices Tasting", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.0, "tags": ["emirati", "coffee", "foodie"], "vibe": "cultural", "best_for": ["foodie", "couple"], "description": "Cardamom coffee, shawarma, and sweet luqaimat."},
            {"name": "Al Maha Desert Luxury Spa", "category": "wellness", "estimated_cost": 90.0, "duration_hours": 2.0, "tags": ["spa", "desert", "luxury"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Private thermal pool and Arabian aromatherapy oils."},
        ]
    },
    {
        "name": "Mumbai", "country": "India", "region": "Asia",
        "cost_index": 50.0, "popularity_score": 8.8, "latitude": 19.0760, "longitude": 72.8777,
        "tags": ["bollywood", "street-food", "seaside", "colonial", "markets"],
        "vibe_tags": ["bustling", "vibrant", "coastal"],
        "climate_type": "tropical",
        "best_months": ["November", "December", "January", "February"],
        "safety_index": 62.0, "budget_tier": "budget",
        "rent_index": 22.0, "restaurant_price_index": 26.0,
        "description": "Mumbai is India's financial powerhouse, fashion capital, and home to the Bollywood film industry. It features grand colonial Victorian architecture alongside bustling seaside promenades.",
        "image_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800",
        "activities": [
            {"name": "Gateway of India & Colaba Heritage", "category": "history", "estimated_cost": 5.0, "duration_hours": 2.5, "tags": ["gateway", "colaba", "heritage"], "vibe": "cultural", "best_for": ["family", "solo"], "description": "Monumental arch on the waterfront and Victorian hotels."},
            {"name": "Marine Drive Queen's Necklace Stroll", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 1.5, "tags": ["marine-drive", "seaside", "promenade"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "C-shaped seaside boulevard overlooking Arabian Sea."},
            {"name": "Chowpatty Beach Street Food Crawl", "category": "food", "estimated_cost": 15.0, "duration_hours": 2.0, "tags": ["pani-puri", "street-food", "beach"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Pani puri, pav bhaji, bhel puri, and kulfi ice cream."},
            {"name": "Elephanta Island Cave Rock Sculptures", "category": "adventure", "estimated_cost": 20.0, "duration_hours": 4.0, "tags": ["ferry", "caves", "sculptures"], "vibe": "immersive", "best_for": ["solo", "group"], "description": "Ferry excursion to ancient rock-cut cave temples."},
            {"name": "Traditional Ayurvedic Wellness Treatment", "category": "wellness", "estimated_cost": 35.0, "duration_hours": 2.0, "tags": ["ayurveda", "massage", "wellness"], "vibe": "relaxing", "best_for": ["solo", "couple"], "description": "Herbal oil body massage and Shirodhara therapy."},
        ]
    },

    # --- Americas (5) ---
    {
        "name": "New York", "country": "United States", "region": "Americas",
        "cost_index": 180.0, "popularity_score": 9.7, "latitude": 40.7128, "longitude": -74.0060,
        "tags": ["broadway", "skyscrapers", "museums", "foodie", "shopping"],
        "vibe_tags": ["energetic", "iconic", "metropolitan"],
        "climate_type": "continental",
        "best_months": ["April", "May", "September", "October"],
        "safety_index": 66.0, "budget_tier": "luxury",
        "rent_index": 100.0, "restaurant_price_index": 100.0,
        "description": "New York City comprises 5 boroughs sitting where the Hudson River meets the Atlantic Ocean. At its core is Manhattan, a densely populated world capital of finance, theater, and arts.",
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800",
        "activities": [
            {"name": "Statue of Liberty & Ellis Island", "category": "history", "estimated_cost": 32.0, "duration_hours": 3.5, "tags": ["statue-of-liberty", "ferry", "monument"], "vibe": "cultural", "best_for": ["family", "couple"], "description": "Ferry cruise to historic immigration museum and monument."},
            {"name": "Summit One Vanderbilt Glass View", "category": "sightseeing", "estimated_cost": 45.0, "duration_hours": 2.0, "tags": ["skyline", "glass", "views"], "vibe": "thrilling", "best_for": ["couple", "solo"], "description": "Immersive glass skyboxes overlooking Chrysler Building."},
            {"name": "Chelsea Market & High Line Food Tour", "category": "food", "estimated_cost": 60.0, "duration_hours": 2.5, "tags": ["chelsea-market", "high-line", "foodie"], "vibe": "lively", "best_for": ["foodie", "couple"], "description": "Lobster rolls, artisanal tacos, and elevated rail park walk."},
            {"name": "Central Park Guided Bike Tour", "category": "nature", "estimated_cost": 35.0, "duration_hours": 2.0, "tags": ["central-park", "bike", "nature"], "vibe": "relaxing", "best_for": ["family", "solo"], "description": "Cycle through lakes, bridges, and peaceful green lawns."},
            {"name": "Fifth Avenue & SoHo Shopping", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 3.0, "tags": ["fifth-ave", "fashion", "luxury"], "vibe": "luxurious", "best_for": ["solo", "couple"], "description": "Iconic department stores and cast-iron designer boutiques."},
        ]
    },
    {
        "name": "Mexico City", "country": "Mexico", "region": "Americas",
        "cost_index": 60.0, "popularity_score": 9.0, "latitude": 19.4326, "longitude": -99.1332,
        "tags": ["aztec", "tacos", "museums", "art", "nightlife"],
        "vibe_tags": ["vibrant", "cultural", "bohemian"],
        "climate_type": "subtropical highland",
        "best_months": ["March", "April", "May", "October", "November"],
        "safety_index": 55.0, "budget_tier": "budget",
        "rent_index": 25.4, "restaurant_price_index": 42.0,
        "description": "Mexico City is the densely populated, high-altitude capital of Mexico. It is renowned for its Aztec Templo Mayor, grand Metropolitan Cathedral, and vibrant contemporary culinary scene.",
        "image_url": "https://images.unsplash.com/photo-1518638150340-f706e86654de?w=800",
        "activities": [
            {"name": "Teotihuacan Pyramids of Sun & Moon", "category": "history", "estimated_cost": 40.0, "duration_hours": 5.0, "tags": ["pyramids", "ancient", "aztec"], "vibe": "immersive", "best_for": ["solo", "group"], "description": "Climb monumental ancient Mesoamerican pyramids."},
            {"name": "Frida Kahlo Museum Casa Azul", "category": "sightseeing", "estimated_cost": 18.0, "duration_hours": 2.0, "tags": ["frida-kahlo", "art", "museum"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "Cobalt-blue home and personal art gallery of Frida Kahlo."},
            {"name": "Roma Norte Taco & Mezcal Safari", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.5, "tags": ["tacos", "mezcal", "street-food"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Al pastor tacos, quesadillas, and artisanal mezcal tasting."},
            {"name": "Chapultepec Forest & Castle Walk", "category": "nature", "estimated_cost": 10.0, "duration_hours": 3.0, "tags": ["castle", "park", "forest"], "vibe": "relaxing", "best_for": ["family", "solo"], "description": "Imperial hilltop palace inside sprawling urban park."},
            {"name": "Coyoacán Artisan Crafts Bazaar", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["crafts", "pottery", "bazaar"], "vibe": "bohemian", "best_for": ["solo", "couple"], "description": "Handcrafted textiles, silver jewelry, and folk pottery."},
        ]
    },
    {
        "name": "Buenos Aires", "country": "Argentina", "region": "Americas",
        "cost_index": 70.0, "popularity_score": 8.9, "latitude": -34.6037, "longitude": -58.3816,
        "tags": ["tango", "steak", "wine", "architecture", "bookstores"],
        "vibe_tags": ["passionate", "bohemian", "cultural"],
        "climate_type": "oceanic",
        "best_months": ["March", "April", "May", "October", "November"],
        "safety_index": 58.0, "budget_tier": "budget",
        "rent_index": 20.2, "restaurant_price_index": 44.5,
        "description": "Buenos Aires is Argentina's cosmopolitan capital with a European architectural feel. Its center is the Plaza de Mayo, lined with 19th-century buildings and the presidential Casa Rosada.",
        "image_url": "https://images.unsplash.com/photo-1612294037637-ec328d0e075e?w=800",
        "activities": [
            {"name": "Teatro Colón Architectural Tour", "category": "history", "estimated_cost": 18.0, "duration_hours": 1.5, "tags": ["opera", "theater", "architecture"], "vibe": "cultural", "best_for": ["couple", "solo"], "description": "Acoustically celebrated opera house in European style."},
            {"name": "Recoleta Cemetery & Eva Perón Tomb", "category": "sightseeing", "estimated_cost": 10.0, "duration_hours": 1.5, "tags": ["recoleta", "mausoleum", "eva-peron"], "vibe": "immersive", "best_for": ["solo", "couple"], "description": "Elaborate marble mausoleums and aristocratic history."},
            {"name": "Palermo Steakhouse & Malbec Tasting", "category": "food", "estimated_cost": 40.0, "duration_hours": 2.5, "tags": ["steak", "malbec", "foodie"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Grass-fed bife de chorizo paired with Mendoza wine."},
            {"name": "San Telmo Tango Milonga Show", "category": "adventure", "estimated_cost": 35.0, "duration_hours": 3.0, "tags": ["tango", "dance", "nightlife"], "vibe": "thrilling", "best_for": ["couple", "solo"], "description": "Midnight live tango dance show and orchestra."},
            {"name": "Palermo Soho Independent Boutiques", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["leather", "boutiques", "fashion"], "vibe": "bohemian", "best_for": ["solo", "couple"], "description": "Trendy leafy streets of Argentine leather and clothing."},
        ]
    },
    {
        "name": "Cancun", "country": "Mexico", "region": "Americas",
        "cost_index": 90.0, "popularity_score": 9.1, "latitude": 21.1619, "longitude": -86.8515,
        "tags": ["beaches", "mayan", "resorts", "cenotes", "nightlife"],
        "vibe_tags": ["tropical", "sunny", "adventurous"],
        "climate_type": "tropical",
        "best_months": ["December", "January", "February", "March", "April"],
        "safety_index": 61.0, "budget_tier": "mid-range",
        "rent_index": 28.0, "restaurant_price_index": 52.0,
        "description": "Cancun is a Mexican city on the Yucatan Peninsula bordering the Caribbean Sea. It is known for its white sand beaches, numerous resorts, and proximity to Mayan civilization ruins.",
        "image_url": "https://images.unsplash.com/photo-1518638150340-f706e86654de?w=800",
        "activities": [
            {"name": "Chichen Itza Mayan Wonder Day Tour", "category": "history", "estimated_cost": 55.0, "duration_hours": 6.0, "tags": ["mayan", "unesco", "pyramid"], "vibe": "immersive", "best_for": ["family", "solo"], "description": "Ancient UNESCO pyramid and Mayan astronomical observatory."},
            {"name": "Tulum Oceanfront Ruins Walk", "category": "sightseeing", "estimated_cost": 25.0, "duration_hours": 2.5, "tags": ["tulum", "ruins", "oceanfront"], "vibe": "cultural", "best_for": ["couple", "solo"], "description": "Coastal clifftop Mayan ruins overlooking turquoise waters."},
            {"name": "Yucatan Maya Cooking Workshop", "category": "food", "estimated_cost": 45.0, "duration_hours": 3.0, "tags": ["cooking", "ceviche", "maya"], "vibe": "lively", "best_for": ["foodie", "couple"], "description": "Cook traditional cochinita pibil and fresh ceviche."},
            {"name": "Cenote Cave Snorkeling & Zipline", "category": "adventure", "estimated_cost": 60.0, "duration_hours": 4.0, "tags": ["cenote", "snorkeling", "zipline"], "vibe": "thrilling", "best_for": ["group", "solo"], "description": "Swim crystalline sinkholes and fly across jungle canopies."},
            {"name": "Mayan Clay Holistic Beach Spa", "category": "wellness", "estimated_cost": 75.0, "duration_hours": 2.0, "tags": ["clay", "spa", "holistic"], "vibe": "relaxing", "best_for": ["couple", "solo"], "description": "Natural detoxifying mineral clay body treatment."},
        ]
    },
    {
        "name": "Toronto", "country": "Canada", "region": "Americas",
        "cost_index": 120.0, "popularity_score": 8.9, "latitude": 43.6532, "longitude": -79.3832,
        "tags": ["multicultural", "skyline", "foodie", "islands", "museums"],
        "vibe_tags": ["vibrant", "cosmopolitan", "clean"],
        "climate_type": "continental",
        "best_months": ["May", "June", "July", "August", "September"],
        "safety_index": 78.0, "budget_tier": "luxury",
        "rent_index": 54.0, "restaurant_price_index": 76.5,
        "description": "Toronto is a dynamic metropolis with a core of soaring skyscrapers, all dwarfed by the iconic CN Tower. The city features abundant green spaces from Queen's Park to the Toronto Islands.",
        "image_url": "https://images.unsplash.com/photo-1517090504586-fde19ea6066f?w=800",
        "activities": [
            {"name": "CN Tower EdgeWalk Experience", "category": "adventure", "estimated_cost": 85.0, "duration_hours": 2.0, "tags": ["cn-tower", "edgewalk", "thrill"], "vibe": "thrilling", "best_for": ["solo", "group"], "description": "Hands-free open-air walk on the ledge of the tower pod."},
            {"name": "Royal Ontario Museum", "category": "history", "estimated_cost": 24.0, "duration_hours": 3.0, "tags": ["museum", "dinosaurs", "culture"], "vibe": "cultural", "best_for": ["family", "solo"], "description": "World cultures, dinosaur fossils, and art collections."},
            {"name": "St. Lawrence Market Food Tour", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.0, "tags": ["market", "peameal", "foodie"], "vibe": "lively", "best_for": ["foodie", "couple"], "description": "Peameal bacon sandwiches, local cheeses, and maple treats."},
            {"name": "Toronto Islands Ferry & Kayak", "category": "nature", "estimated_cost": 20.0, "duration_hours": 3.0, "tags": ["ferry", "kayak", "skyline"], "vibe": "relaxing", "best_for": ["family", "couple"], "description": "Scenic boat cruise and paddling with city skyline views."},
            {"name": "Distillery District Historic Boutiques", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["distillery", "art", "boutiques"], "vibe": "bohemian", "best_for": ["solo", "couple"], "description": "19th-century brick distillery turned arts district."},
        ]
    },
]


async def seed_database():
    """Seeds the database with cities, activities, demo user, and demo trips."""
    print("[Seed] Synchronizing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create or verify Demo User
        demo_email = "demo@globetrotter.com"
        user_res = await session.execute(select(User).where(User.email == demo_email))
        demo_user = user_res.scalar_one_or_none()

        if demo_user is None:
            demo_user = User(
                name="Demo Traveler",
                email=demo_email,
                password_hash=hash_password("demo1234"),
                profile_photo="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
                preferred_currency="USD",
                language="en",
            )
            session.add(demo_user)
            await session.flush()
            print(f"[Seed] Created demo user: {demo_email}")
        else:
            print(f"[Seed] Demo user already exists: {demo_email}")

        # 2. Insert or update Cities & Activities
        created_cities = {}
        for c_data in CITIES_DATA:
            city_res = await session.execute(select(City).where(City.name == c_data["name"]))
            city = city_res.scalar_one_or_none()

            if city is None:
                city = City(
                    name=c_data["name"],
                    country=c_data["country"],
                    region=c_data["region"],
                    description=c_data["description"],
                    cost_index=c_data["cost_index"],
                    popularity_score=c_data["popularity_score"],
                    latitude=c_data["latitude"],
                    longitude=c_data["longitude"],
                    image_url=c_data["image_url"],
                    tags=c_data["tags"],
                    vibe_tags=c_data["vibe_tags"],
                    climate_type=c_data["climate_type"],
                    best_months=c_data["best_months"],
                    safety_index=c_data["safety_index"],
                    budget_tier=c_data["budget_tier"],
                    rent_index=c_data["rent_index"],
                    restaurant_price_index=c_data["restaurant_price_index"],
                )
                session.add(city)
                await session.flush()
                print(f"[Seed] Added city: {city.name} ({city.country})")

                for act_data in c_data["activities"]:
                    activity = Activity(
                        city_id=city.id,
                        name=act_data["name"],
                        category=act_data["category"],
                        description=act_data["description"],
                        estimated_cost=act_data["estimated_cost"],
                        duration_hours=act_data["duration_hours"],
                        latitude=city.latitude,
                        longitude=city.longitude,
                        image_url=city.image_url,
                        tags=act_data["tags"],
                        vibe=act_data["vibe"],
                        best_for=act_data["best_for"],
                    )
                    session.add(activity)

                await session.flush()
            else:
                city.description = c_data["description"]
                city.latitude = c_data["latitude"]
                city.longitude = c_data["longitude"]
                city.cost_index = c_data["cost_index"]
                city.popularity_score = c_data["popularity_score"]
                city.tags = c_data["tags"]
                city.vibe_tags = c_data["vibe_tags"]
                city.climate_type = c_data["climate_type"]
                city.best_months = c_data["best_months"]
                city.safety_index = c_data["safety_index"]
                city.budget_tier = c_data["budget_tier"]
                city.rent_index = c_data["rent_index"]
                city.restaurant_price_index = c_data["restaurant_price_index"]
                session.add(city)
                await session.flush()

            created_cities[city.name] = city

        # 3. Create Sample Trips for demo user
        trips_res = await session.execute(select(Trip).where(Trip.user_id == demo_user.id))
        existing_trips = trips_res.scalars().all()

        if not existing_trips:
            print("[Seed] Creating sample trips for demo user...")

            # --- Sample Trip 1: "Europe Explorer" ---
            start_date1 = date.today() + timedelta(days=30)
            end_date1 = start_date1 + timedelta(days=10)

            trip1 = Trip(
                user_id=demo_user.id,
                title="Europe Explorer",
                description="Scenic cultural escapade across Paris, Rome, and Barcelona with curated highlights.",
                start_date=start_date1,
                end_date=end_date1,
                cover_photo="https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800",
                total_budget=2500.0,
                currency="USD",
                visibility="public",
                status="upcoming",
            )
            session.add(trip1)
            await session.flush()

            session.add(Budget(
                trip_id=trip1.id,
                transport_cost=300.0,
                stay_cost=0.0,
                meals_cost=0.0,
                misc_cost=50.0,
                total_budget_limit=2500.0,
            ))
            await session.flush()

            # Stop 1: Paris (4 days)
            paris = created_cities["Paris"]
            stop1 = TripStop(
                trip_id=trip1.id,
                city_id=paris.id,
                arrival_date=start_date1,
                departure_date=start_date1 + timedelta(days=4),
                stop_order=1,
                notes="Hotel booked near Saint-Germain-des-Prés",
            )
            session.add(stop1)
            await session.flush()

            paris_acts = (await session.execute(select(Activity).where(Activity.city_id == paris.id))).scalars().all()
            for idx, act in enumerate(paris_acts[:3]):
                session.add(ItineraryItem(
                    trip_stop_id=stop1.id,
                    activity_id=act.id,
                    scheduled_date=start_date1 + timedelta(days=idx),
                    start_time=time(10, 0),
                    end_time=time(12, 30),
                    custom_cost=act.estimated_cost,
                    notes=f"Scheduled activity: {act.name}",
                    status="confirmed",
                ))

            # Stop 2: Rome (3 days)
            rome = created_cities["Rome"]
            stop2 = TripStop(
                trip_id=trip1.id,
                city_id=rome.id,
                arrival_date=start_date1 + timedelta(days=4),
                departure_date=start_date1 + timedelta(days=7),
                stop_order=2,
                notes="Boutique hotel near Trevi Fountain",
            )
            session.add(stop2)
            await session.flush()

            rome_acts = (await session.execute(select(Activity).where(Activity.city_id == rome.id))).scalars().all()
            for idx, act in enumerate(rome_acts[:3]):
                session.add(ItineraryItem(
                    trip_stop_id=stop2.id,
                    activity_id=act.id,
                    scheduled_date=start_date1 + timedelta(days=4 + idx),
                    start_time=time(10, 0),
                    end_time=time(13, 0),
                    custom_cost=act.estimated_cost,
                    notes=f"Scheduled activity: {act.name}",
                    status="confirmed",
                ))

            # Stop 3: Barcelona (3 days)
            bcn = created_cities["Barcelona"]
            stop3 = TripStop(
                trip_id=trip1.id,
                city_id=bcn.id,
                arrival_date=start_date1 + timedelta(days=7),
                departure_date=end_date1,
                stop_order=3,
                notes="Apartment in Eixample district",
            )
            session.add(stop3)
            await session.flush()

            bcn_acts = (await session.execute(select(Activity).where(Activity.city_id == bcn.id))).scalars().all()
            for idx, act in enumerate(bcn_acts[:3]):
                session.add(ItineraryItem(
                    trip_stop_id=stop3.id,
                    activity_id=act.id,
                    scheduled_date=start_date1 + timedelta(days=7 + idx),
                    start_time=time(11, 0),
                    end_time=time(13, 30),
                    custom_cost=act.estimated_cost,
                    notes=f"Scheduled activity: {act.name}",
                    status="confirmed",
                ))

            # --- Sample Trip 2: "Asia Adventure" ---
            start_date2 = date.today() + timedelta(days=90)
            end_date2 = start_date2 + timedelta(days=9)

            trip2 = Trip(
                user_id=demo_user.id,
                title="Asia Adventure",
                description="Street food in Bangkok, serene rice paddies in Bali, and futuristic gardens in Singapore.",
                start_date=start_date2,
                end_date=end_date2,
                cover_photo="https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800",
                total_budget=1800.0,
                currency="USD",
                visibility="private",
                status="draft",
            )
            session.add(trip2)
            await session.flush()

            session.add(Budget(
                trip_id=trip2.id,
                transport_cost=250.0,
                stay_cost=0.0,
                meals_cost=0.0,
                misc_cost=40.0,
                total_budget_limit=1800.0,
            ))
            await session.flush()

            # Stop 1: Bangkok (3 days)
            bkk = created_cities["Bangkok"]
            stop_bkk = TripStop(
                trip_id=trip2.id,
                city_id=bkk.id,
                arrival_date=start_date2,
                departure_date=start_date2 + timedelta(days=3),
                stop_order=1,
            )
            session.add(stop_bkk)
            await session.flush()

            bkk_acts = (await session.execute(select(Activity).where(Activity.city_id == bkk.id))).scalars().all()
            for idx, act in enumerate(bkk_acts[:3]):
                session.add(ItineraryItem(
                    trip_stop_id=stop_bkk.id,
                    activity_id=act.id,
                    scheduled_date=start_date2 + timedelta(days=idx),
                    start_time=time(10, 0),
                    end_time=time(12, 30),
                    custom_cost=act.estimated_cost,
                    notes=f"Activity: {act.name}",
                    status="planned",
                ))

            # Stop 2: Bali (4 days)
            bali = created_cities["Bali"]
            stop_bali = TripStop(
                trip_id=trip2.id,
                city_id=bali.id,
                arrival_date=start_date2 + timedelta(days=3),
                departure_date=start_date2 + timedelta(days=7),
                stop_order=2,
            )
            session.add(stop_bali)
            await session.flush()

            bali_acts = (await session.execute(select(Activity).where(Activity.city_id == bali.id))).scalars().all()
            for idx, act in enumerate(bali_acts[:3]):
                session.add(ItineraryItem(
                    trip_stop_id=stop_bali.id,
                    activity_id=act.id,
                    scheduled_date=start_date2 + timedelta(days=3 + idx),
                    start_time=time(9, 30),
                    end_time=time(12, 0),
                    custom_cost=act.estimated_cost,
                    notes=f"Activity: {act.name}",
                    status="planned",
                ))

            # Stop 3: Singapore (2 days)
            sing = created_cities["Singapore"]
            stop_sing = TripStop(
                trip_id=trip2.id,
                city_id=sing.id,
                arrival_date=start_date2 + timedelta(days=7),
                departure_date=end_date2,
                stop_order=3,
            )
            session.add(stop_sing)
            await session.flush()

            sing_acts = (await session.execute(select(Activity).where(Activity.city_id == sing.id))).scalars().all()
            for idx, act in enumerate(sing_acts[:3]):
                session.add(ItineraryItem(
                    trip_stop_id=stop_sing.id,
                    activity_id=act.id,
                    scheduled_date=start_date2 + timedelta(days=7 + idx),
                    start_time=time(10, 30),
                    end_time=time(13, 0),
                    custom_cost=act.estimated_cost,
                    notes=f"Activity: {act.name}",
                    status="planned",
                ))

            await session.commit()
            print("[Seed] Successfully seeded sample trips!")
        else:
            print(f"[Seed] Trips already exist ({len(existing_trips)} found).")

    print("[Seed] Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
