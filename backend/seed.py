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

# 20 Global Cities exact specifications
CITIES_DATA = [
    # --- Europe (8) ---
    {
        "name": "Paris", "country": "France", "region": "Europe",
        "cost_index": 130.0, "popularity_score": 9.8, "latitude": 48.8566, "longitude": 2.3522,
        "description": "The City of Light is renowned for its world-class art, fashion, gastronomy, and culture. Its 19th-century cityscape is crisscrossed by wide boulevards and the River Seine.",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "activities": [
            {"name": "Eiffel Tower Summit Tour", "category": "sightseeing", "estimated_cost": 35.0, "duration_hours": 2.5, "description": "Elevator ascent to the highest deck overlooking Paris."},
            {"name": "Louvre Museum Masterpieces", "category": "history", "estimated_cost": 22.0, "duration_hours": 3.0, "description": "Guided walking tour through Renaissance art and antiquities."},
            {"name": "Montmartre Bakery & Pastry Walk", "category": "food", "estimated_cost": 45.0, "duration_hours": 2.0, "description": "Sample fresh baguettes, croissants, and macarons."},
            {"name": "Seine River Sunset Cruise", "category": "nature", "estimated_cost": 20.0, "duration_hours": 1.5, "description": "Scenic boat cruise passing Notre Dame and historic bridges."},
            {"name": "Champs-Élysées Luxury Boutique Walk", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Stroll down the world's most famous shopping avenue."},
        ]
    },
    {
        "name": "Rome", "country": "Italy", "region": "Europe",
        "cost_index": 110.0, "popularity_score": 9.6, "latitude": 41.9028, "longitude": 12.4964,
        "description": "Rome is a living open-air museum boasting nearly 3,000 years of globally influential art, architecture, and culture. Ancient ruins like the Forum and Colosseum evoke the power of the Roman Empire.",
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800",
        "activities": [
            {"name": "Colosseum & Roman Forum", "category": "history", "estimated_cost": 30.0, "duration_hours": 3.0, "description": "Step into the gladiatorial arena and imperial palace ruins."},
            {"name": "Vatican & Sistine Chapel", "category": "sightseeing", "estimated_cost": 38.0, "duration_hours": 3.5, "description": "Michelangelo's ceiling fresco and Saint Peter's Basilica."},
            {"name": "Trastevere Street Food Crawl", "category": "food", "estimated_cost": 50.0, "duration_hours": 2.5, "description": "Authentic supplì, wood-fired pizza slices, and gelato."},
            {"name": "Appian Way Ancient E-Bike Tour", "category": "adventure", "estimated_cost": 48.0, "duration_hours": 3.5, "description": "Cycle the preserved cobblestone Roman military highway."},
            {"name": "Villa Borghese Thermal Spa & Wellness", "category": "wellness", "estimated_cost": 60.0, "duration_hours": 2.0, "description": "Relaxing mineral water baths and herbal steam rooms."},
        ]
    },
    {
        "name": "Barcelona", "country": "Spain", "region": "Europe",
        "cost_index": 95.0, "popularity_score": 9.4, "latitude": 41.3851, "longitude": 2.1734,
        "description": "Barcelona is famed for its Mediterranean coastline and Antoni Gaudí's whimsical architecture. The city combines vibrant seaside culture with rich Catalan artistic heritage.",
        "image_url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800",
        "activities": [
            {"name": "Sagrada Familia Basilica Tour", "category": "sightseeing", "estimated_cost": 28.0, "duration_hours": 2.0, "description": "Explore Gaudi's awe-inspiring modernist architectural cathedral."},
            {"name": "Park Güell Mosaic Exploration", "category": "nature", "estimated_cost": 15.0, "duration_hours": 2.0, "description": "Color-rich mosaic benches with views of the Mediterranean."},
            {"name": "Boqueria Market Tapas & Sangria", "category": "food", "estimated_cost": 40.0, "duration_hours": 2.0, "description": "Taste Jamon Iberico, grilled seafood tapas, and local cava."},
            {"name": "Barceloneta Paddleboarding & Surf", "category": "adventure", "estimated_cost": 35.0, "duration_hours": 2.0, "description": "Coastal watersports along the sunny Barcelona shores."},
            {"name": "Gothic Quarter Artisanal Boutiques", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "description": "Discover local leather goods and vintage jewelers."},
        ]
    },
    {
        "name": "Amsterdam", "country": "Netherlands", "region": "Europe",
        "cost_index": 125.0, "popularity_score": 9.2, "latitude": 52.3676, "longitude": 4.9041,
        "description": "Amsterdam is known for its artistic heritage, elaborate canal system, and narrow houses with gabled facades. Cycling is key to the city's character, with countless bike paths.",
        "image_url": "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800",
        "activities": [
            {"name": "Rijksmuseum Dutch Masters", "category": "history", "estimated_cost": 25.0, "duration_hours": 2.5, "description": "Admire Rembrandt's Night Watch and Golden Age masterpieces."},
            {"name": "Canal Belt Historic Boat Cruise", "category": "sightseeing", "estimated_cost": 20.0, "duration_hours": 1.5, "description": "Cruise past UNESCO heritage 17th-century canal houses."},
            {"name": "Jordaan Cheese & Stroopwafel Safari", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.0, "description": "Gouda cheese tastings and fresh hot stroopwafels."},
            {"name": "Countryside Windmill Bike Trek", "category": "nature", "estimated_cost": 45.0, "duration_hours": 4.0, "description": "Cycle out to Zaanse Schans historic working windmills."},
            {"name": "Nine Streets Boutique Shopping", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Charming district packed with indie fashion and bookshops."},
        ]
    },
    {
        "name": "Prague", "country": "Czech Republic", "region": "Europe",
        "cost_index": 75.0, "popularity_score": 8.9, "latitude": 50.0755, "longitude": 14.4378,
        "description": "Prague is known as the City of a Hundred Spires, with a historic core reflecting millennia of European architecture. Charles Bridge and Prague Castle provide unforgettable skyline vistas.",
        "image_url": "https://images.unsplash.com/photo-1541849546-216549ae216d?w=800",
        "activities": [
            {"name": "Prague Castle & St. Vitus Cathedral", "category": "history", "estimated_cost": 18.0, "duration_hours": 3.0, "description": "Largest ancient castle complex in the world."},
            {"name": "Old Town Square & Astronomical Clock", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 1.5, "description": "Gothic spires and the mechanical clock show."},
            {"name": "Traditional Bohemian Beer & Goulash", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "description": "Pilsner beer tasting paired with slow-cooked beef goulash."},
            {"name": "Vltava River Kayaking Excursion", "category": "adventure", "estimated_cost": 30.0, "duration_hours": 2.0, "description": "Paddle beneath historic arches of Charles Bridge."},
            {"name": "Beer Spa & Thermal Hop Bath", "category": "wellness", "estimated_cost": 65.0, "duration_hours": 1.5, "description": "Relax in warm oak tubs infused with natural hop extracts."},
        ]
    },
    {
        "name": "Vienna", "country": "Austria", "region": "Europe",
        "cost_index": 115.0, "popularity_score": 9.1, "latitude": 48.2082, "longitude": 16.3738,
        "description": "Vienna's artistic and intellectual legacy was shaped by residents including Mozart, Beethoven, and Freud. The city is celebrated for its imperial palaces and vibrant coffeehouse culture.",
        "image_url": "https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800",
        "activities": [
            {"name": "Schönbrunn Imperial Palace", "category": "history", "estimated_cost": 26.0, "duration_hours": 3.0, "description": "Habsburg summer residence and Baroque gardens."},
            {"name": "St. Stephen's Cathedral Tower Climb", "category": "sightseeing", "estimated_cost": 12.0, "duration_hours": 1.5, "description": "Gothic cathedral with panoramic views across Vienna."},
            {"name": "Viennese Coffeehouse & Sachertorte", "category": "food", "estimated_cost": 20.0, "duration_hours": 1.5, "description": "Classic Melange coffee and original chocolate apricot cake."},
            {"name": "Wienerwald Woods Nature Hike", "category": "nature", "estimated_cost": 0.0, "duration_hours": 3.0, "description": "Lush beech forests overlooking the Danube River."},
            {"name": "Graben & Kärntner Straße Promenade", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Pedestrian avenues filled with Austrian craftsmanship."},
        ]
    },
    {
        "name": "Lisbon", "country": "Portugal", "region": "Europe",
        "cost_index": 85.0, "popularity_score": 9.3, "latitude": 38.7223, "longitude": -9.1393,
        "description": "Lisbon is a coastal capital of pastel buildings, steep hills, and melancholic Fado music. From imposing São Jorge Castle, the view encompasses old quarter buildings and the Tagus Estuary.",
        "image_url": "https://images.unsplash.com/photo-1509840841025-9088ba78a826?w=800",
        "activities": [
            {"name": "Jerónimos Monastery & Belém Tower", "category": "history", "estimated_cost": 15.0, "duration_hours": 2.5, "description": "Manueline architecture and maritime Age of Discovery history."},
            {"name": "Tram 28 Scenic City Ride", "category": "sightseeing", "estimated_cost": 4.0, "duration_hours": 1.0, "description": "Vintage yellow tram climbing Lisbon's steep hills."},
            {"name": "Pastéis de Belém & Seafood Tasting", "category": "food", "estimated_cost": 30.0, "duration_hours": 2.0, "description": "Warm custard tarts and garlic butter grilled prawns."},
            {"name": "Sintra Mountains Trail Hike", "category": "adventure", "estimated_cost": 22.0, "duration_hours": 4.0, "description": "Hike through mystical forests up to colorful Pena Palace."},
            {"name": "LX Factory Concept Stores", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Revitalized industrial complex of indie makers and designers."},
        ]
    },
    {
        "name": "Athens", "country": "Greece", "region": "Europe",
        "cost_index": 80.0, "popularity_score": 9.0, "latitude": 37.9838, "longitude": 23.7275,
        "description": "Athens was the heart of Ancient Greece, a powerful civilization and empire. Landmarks including the 5th-century BC Acropolis fortress still dominate the sun-drenched capital.",
        "image_url": "https://images.unsplash.com/photo-1555993539-1732b0258235?w=800",
        "activities": [
            {"name": "Acropolis & Parthenon Monument", "category": "history", "estimated_cost": 25.0, "duration_hours": 3.0, "description": "Iconic ancient citadel and temple to goddess Athena."},
            {"name": "Plaka Ancient Quarter Walk", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Village-like labyrinth of neoclassical architecture."},
            {"name": "Authentic Souvlaki & Meze Safari", "category": "food", "estimated_cost": 22.0, "duration_hours": 2.0, "description": "Tzatziki, grilled souvlaki skewers, and Greek wine."},
            {"name": "Mount Lycabettus Sunset Hike", "category": "nature", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Limestone hill summit offering Aegean sea views."},
            {"name": "Monastiraki Flea Market", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Bustling market for Greek olive oil, leather, and relics."},
        ]
    },

    # --- Asia (7) ---
    {
        "name": "Tokyo", "country": "Japan", "region": "Asia",
        "cost_index": 120.0, "popularity_score": 9.9, "latitude": 35.6762, "longitude": 139.6503,
        "description": "Tokyo mixes ultra-modern skyscrapers and neon signs with historic temples. The city is a culinary capital of world-renowned gastronomy, pristine transport, and cutting-edge pop culture.",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800",
        "activities": [
            {"name": "Senso-ji Temple & Asakusa Heritage", "category": "history", "estimated_cost": 10.0, "duration_hours": 2.0, "description": "Tokyo's oldest Buddhist temple and traditional stall street."},
            {"name": "Shibuya Sky Observation Deck", "category": "sightseeing", "estimated_cost": 20.0, "duration_hours": 1.5, "description": "Panoramic open-air view of Shibuya Scramble intersection."},
            {"name": "Tsukiji Outer Market Sushi Safari", "category": "food", "estimated_cost": 55.0, "duration_hours": 2.5, "description": "Ultra-fresh sashimi, wagyu skewers, and tamagoyaki."},
            {"name": "Akihabara Tech & Anime Shopping", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "description": "World-famous district for gadgets, manga, and retro games."},
            {"name": "Natural Onsen Hot Spring & Spa", "category": "wellness", "estimated_cost": 30.0, "duration_hours": 2.0, "description": "Traditional Japanese mineral hot springs and sauna."},
        ]
    },
    {
        "name": "Bangkok", "country": "Thailand", "region": "Asia",
        "cost_index": 55.0, "popularity_score": 9.3, "latitude": 13.7563, "longitude": 100.5018,
        "description": "Bangkok is famous for ornate shrines, bustling boat-filled canals, and vibrant street life. The city offers rich contrasts between golden royal palaces and towering modern rooftops.",
        "image_url": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800",
        "activities": [
            {"name": "Grand Palace & Emerald Buddha", "category": "history", "estimated_cost": 16.0, "duration_hours": 3.0, "description": "Spectacular royal grounds and holy Buddhist temple."},
            {"name": "Wat Arun Temple of Dawn", "category": "sightseeing", "estimated_cost": 5.0, "duration_hours": 1.5, "description": "Porcelain-decorated river temple with majestic spire."},
            {"name": "Yaowarat Chinatown Street Food Crawl", "category": "food", "estimated_cost": 20.0, "duration_hours": 2.5, "description": "Pad Thai, crispy pork, and mango sticky rice."},
            {"name": "Chatuchak Weekend Market Trek", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 3.0, "description": "Over 15,000 stalls of Thai crafts, clothing, and food."},
            {"name": "Traditional Royal Thai Massage", "category": "wellness", "estimated_cost": 25.0, "duration_hours": 1.5, "description": "Deep acupressure and yoga-assisted relaxation."},
        ]
    },
    {
        "name": "Bali", "country": "Indonesia", "region": "Asia",
        "cost_index": 45.0, "popularity_score": 9.5, "latitude": -8.4095, "longitude": 115.1889,
        "description": "Bali is an Indonesian island paradise known for its forested volcanic mountains, iconic rice paddies, and coral reefs. It is home to spiritual religious sites such as cliffside Uluwatu Temple.",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
        "activities": [
            {"name": "Uluwatu Sunset Temple & Fire Dance", "category": "sightseeing", "estimated_cost": 15.0, "duration_hours": 2.5, "description": "Perched cliff views paired with hypnotic Kecak fire dance."},
            {"name": "Tegallalang Emerald Rice Terraces", "category": "nature", "estimated_cost": 8.0, "duration_hours": 2.0, "description": "Stepped green hillside trails and jungle canopy swings."},
            {"name": "Jimbaran Bay Beach Seafood Feast", "category": "food", "estimated_cost": 30.0, "duration_hours": 2.0, "description": "Fresh grilled snapper and prawns served on the sand."},
            {"name": "Mount Batur Sunrise Volcano Hike", "category": "adventure", "estimated_cost": 45.0, "duration_hours": 5.0, "description": "Pre-dawn trek to active volcano crater for cloud sunrise."},
            {"name": "Ubud Herbal Yoga & Spa Retreat", "category": "wellness", "estimated_cost": 35.0, "duration_hours": 2.5, "description": "Flower petal bath and outdoor tropical yoga session."},
        ]
    },
    {
        "name": "Singapore", "country": "Singapore", "region": "Asia",
        "cost_index": 140.0, "popularity_score": 9.1, "latitude": 1.3521, "longitude": 103.8198,
        "description": "Singapore is a global financial center and island city-state known for cleanliness and tropical garden city architecture. It features UNESCO botanical gardens and world-class street food.",
        "image_url": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800",
        "activities": [
            {"name": "Gardens by the Bay & Cloud Forest", "category": "nature", "estimated_cost": 28.0, "duration_hours": 3.0, "description": "Futuristic vertical Supertrees and indoor waterfall dome."},
            {"name": "Marina Bay Sands SkyPark Observation", "category": "sightseeing", "estimated_cost": 24.0, "duration_hours": 1.5, "description": "57th floor panoramic harbor and skyline views."},
            {"name": "Michelin Hawker Center Food Tour", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "description": "Hainanese chicken rice, laksa noodle soup, and satay."},
            {"name": "Orchard Road Luxury Malls", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "description": "Premier retail street with international fashion flagships."},
            {"name": "Sentosa Mega Adventure Zipline", "category": "adventure", "estimated_cost": 45.0, "duration_hours": 2.0, "description": "High-speed 450m canopy zipline down to Siloso beach."},
        ]
    },
    {
        "name": "Istanbul", "country": "Turkey", "region": "Asia",
        "cost_index": 65.0, "popularity_score": 9.2, "latitude": 41.0082, "longitude": 28.9784,
        "description": "Istanbul straddles Europe and Asia across the Bosphorus Strait. Its historic center reflects cultural influences of the many empires that once ruled here.",
        "image_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800",
        "activities": [
            {"name": "Hagia Sophia & Blue Mosque", "category": "history", "estimated_cost": 25.0, "duration_hours": 3.0, "description": "Stunning Byzantine dome mosaics and Ottoman minarets."},
            {"name": "Bosphorus Strait Sunset Cruise", "category": "sightseeing", "estimated_cost": 15.0, "duration_hours": 2.0, "description": "Sail between European and Asian continents at dusk."},
            {"name": "Grand Bazaar Spice & Delights Tour", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.5, "description": "Over 4,000 shops of Turkish carpets, ceramics, and sweets."},
            {"name": "Kebabs, Baklava & Turkish Coffee", "category": "food", "estimated_cost": 25.0, "duration_hours": 2.0, "description": "Sample charcoal lamb kebabs and pistachio baklava."},
            {"name": "Historic Turkish Hamam Bath Experience", "category": "wellness", "estimated_cost": 50.0, "duration_hours": 1.5, "description": "Marble steam room, body scrub, and foam massage."},
        ]
    },
    {
        "name": "Dubai", "country": "United Arab Emirates", "region": "Asia",
        "cost_index": 160.0, "popularity_score": 9.3, "latitude": 25.2048, "longitude": 55.2708,
        "description": "Dubai is known for luxury shopping, ultramodern architecture, and a lively nightlife scene. Burj Khalifa, an 830m-tall tower, dominates the skyscraper-filled skyline.",
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800",
        "activities": [
            {"name": "Burj Khalifa Top of the World View", "category": "sightseeing", "estimated_cost": 45.0, "duration_hours": 2.0, "description": "Ascend the world's tallest tower for desert and sea views."},
            {"name": "Red Dune 4x4 Desert Safari & Camp", "category": "adventure", "estimated_cost": 65.0, "duration_hours": 5.0, "description": "Sand dune bashing, camel riding, and starlit BBQ."},
            {"name": "Dubai Mall & Underwater Aquarium", "category": "shopping", "estimated_cost": 30.0, "duration_hours": 3.0, "description": "Massive mall featuring indoor zoo and gold souk."},
            {"name": "Emirati Food & Spices Tasting", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.0, "description": "Cardamom coffee, shawarma, and sweet luqaimat."},
            {"name": "Al Maha Desert Luxury Spa", "category": "wellness", "estimated_cost": 90.0, "duration_hours": 2.0, "description": "Private thermal pool and Arabian aromatherapy oils."},
        ]
    },
    {
        "name": "Mumbai", "country": "India", "region": "Asia",
        "cost_index": 50.0, "popularity_score": 8.8, "latitude": 19.0760, "longitude": 72.8777,
        "description": "Mumbai is India's financial powerhouse, fashion capital, and home to the Bollywood film industry. It features grand colonial Victorian architecture alongside bustling seaside promenades.",
        "image_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800",
        "activities": [
            {"name": "Gateway of India & Colaba Heritage", "category": "history", "estimated_cost": 5.0, "duration_hours": 2.5, "description": "Monumental arch on the waterfront and Victorian hotels."},
            {"name": "Marine Drive Queen's Necklace Stroll", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 1.5, "description": "C-shaped seaside boulevard overlooking Arabian Sea."},
            {"name": "Chowpatty Beach Street Food Crawl", "category": "food", "estimated_cost": 15.0, "duration_hours": 2.0, "description": "Pani puri, pav bhaji, bhel puri, and kulfi ice cream."},
            {"name": "Elephanta Island Cave Rock Sculptures", "category": "adventure", "estimated_cost": 20.0, "duration_hours": 4.0, "description": "Ferry excursion to ancient rock-cut cave temples."},
            {"name": "Traditional Ayurvedic Wellness Treatment", "category": "wellness", "estimated_cost": 35.0, "duration_hours": 2.0, "description": "Herbal oil body massage and Shirodhara therapy."},
        ]
    },

    # --- Americas (5) ---
    {
        "name": "New York", "country": "United States", "region": "Americas",
        "cost_index": 180.0, "popularity_score": 9.7, "latitude": 40.7128, "longitude": -74.0060,
        "description": "New York City comprises 5 boroughs sitting where the Hudson River meets the Atlantic Ocean. At its core is Manhattan, a densely populated world capital of finance, theater, and arts.",
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800",
        "activities": [
            {"name": "Statue of Liberty & Ellis Island", "category": "history", "estimated_cost": 32.0, "duration_hours": 3.5, "description": "Ferry cruise to historic immigration museum and monument."},
            {"name": "Summit One Vanderbilt Glass View", "category": "sightseeing", "estimated_cost": 45.0, "duration_hours": 2.0, "description": "Immersive glass skyboxes overlooking Chrysler Building."},
            {"name": "Chelsea Market & High Line Food Tour", "category": "food", "estimated_cost": 60.0, "duration_hours": 2.5, "description": "Lobster rolls, artisanal tacos, and elevated rail park walk."},
            {"name": "Central Park Guided Bike Tour", "category": "nature", "estimated_cost": 35.0, "duration_hours": 2.0, "description": "Cycle through lakes, bridges, and peaceful green lawns."},
            {"name": "Fifth Avenue & SoHo Shopping", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 3.0, "description": "Iconic department stores and cast-iron designer boutiques."},
        ]
    },
    {
        "name": "Mexico City", "country": "Mexico", "region": "Americas",
        "cost_index": 60.0, "popularity_score": 9.0, "latitude": 19.4326, "longitude": -99.1332,
        "description": "Mexico City is the densely populated, high-altitude capital of Mexico. It is renowned for its Aztec Templo Mayor, grand Metropolitan Cathedral, and vibrant contemporary culinary scene.",
        "image_url": "https://images.unsplash.com/photo-1518638150340-f706e86654de?w=800",
        "activities": [
            {"name": "Teotihuacan Pyramids of Sun & Moon", "category": "history", "estimated_cost": 40.0, "duration_hours": 5.0, "description": "Climb monumental ancient Mesoamerican pyramids."},
            {"name": "Frida Kahlo Museum Casa Azul", "category": "sightseeing", "estimated_cost": 18.0, "duration_hours": 2.0, "description": "Cobalt-blue home and personal art gallery of Frida Kahlo."},
            {"name": "Roma Norte Taco & Mezcal Safari", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.5, "description": "Al pastor tacos, quesadillas, and artisanal mezcal tasting."},
            {"name": "Chapultepec Forest & Castle Walk", "category": "nature", "estimated_cost": 10.0, "duration_hours": 3.0, "description": "Imperial hilltop palace inside sprawling urban park."},
            {"name": "Coyoacán Artisan Crafts Bazaar", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Handcrafted textiles, silver jewelry, and folk pottery."},
        ]
    },
    {
        "name": "Buenos Aires", "country": "Argentina", "region": "Americas",
        "cost_index": 70.0, "popularity_score": 8.9, "latitude": -34.6037, "longitude": -58.3816,
        "description": "Buenos Aires is Argentina's cosmopolitan capital with a European architectural feel. Its center is the Plaza de Mayo, lined with 19th-century buildings and the presidential Casa Rosada.",
        "image_url": "https://images.unsplash.com/photo-1612294037637-ec328d0e075e?w=800",
        "activities": [
            {"name": "Teatro Colón Architectural Tour", "category": "history", "estimated_cost": 18.0, "duration_hours": 1.5, "description": "Acoustically celebrated opera house in European style."},
            {"name": "Recoleta Cemetery & Eva Perón Tomb", "category": "sightseeing", "estimated_cost": 10.0, "duration_hours": 1.5, "description": "Elaborate marble mausoleums and aristocratic history."},
            {"name": "Palermo Steakhouse & Malbec Tasting", "category": "food", "estimated_cost": 40.0, "duration_hours": 2.5, "description": "Grass-fed bife de chorizo paired with Mendoza wine."},
            {"name": "San Telmo Tango Milonga Show", "category": "adventure", "estimated_cost": 35.0, "duration_hours": 3.0, "description": "Midnight live tango dance show and orchestra."},
            {"name": "Palermo Soho Independent Boutiques", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "Trendy leafy streets of Argentine leather and clothing."},
        ]
    },
    {
        "name": "Cancun", "country": "Mexico", "region": "Americas",
        "cost_index": 90.0, "popularity_score": 9.1, "latitude": 21.1619, "longitude": -86.8515,
        "description": "Cancun is a Mexican city on the Yucatan Peninsula bordering the Caribbean Sea. It is known for its white sand beaches, numerous resorts, and proximity to Mayan civilization ruins.",
        "image_url": "https://images.unsplash.com/photo-1518638150340-f706e86654de?w=800",
        "activities": [
            {"name": "Chichen Itza Mayan Wonder Day Tour", "category": "history", "estimated_cost": 55.0, "duration_hours": 6.0, "description": "Ancient UNESCO pyramid and Mayan astronomical observatory."},
            {"name": "Tulum Oceanfront Ruins Walk", "category": "sightseeing", "estimated_cost": 25.0, "duration_hours": 2.5, "description": "Coastal clifftop Mayan ruins overlooking turquoise waters."},
            {"name": "Yucatan Maya Cooking Workshop", "category": "food", "estimated_cost": 45.0, "duration_hours": 3.0, "description": "Cook traditional cochinita pibil and fresh ceviche."},
            {"name": "Cenote Cave Snorkeling & Zipline", "category": "adventure", "estimated_cost": 60.0, "duration_hours": 4.0, "description": "Swim crystalline sinkholes and fly across jungle canopies."},
            {"name": "Mayan Clay Holistic Beach Spa", "category": "wellness", "estimated_cost": 75.0, "duration_hours": 2.0, "description": "Natural detoxifying mineral clay body treatment."},
        ]
    },
    {
        "name": "Toronto", "country": "Canada", "region": "Americas",
        "cost_index": 120.0, "popularity_score": 8.9, "latitude": 43.6532, "longitude": -79.3832,
        "description": "Toronto is a dynamic metropolis with a core of soaring skyscrapers, all dwarfed by the iconic CN Tower. The city features abundant green spaces from Queen's Park to the Toronto Islands.",
        "image_url": "https://images.unsplash.com/photo-1517090504586-fde19ea6066f?w=800",
        "activities": [
            {"name": "CN Tower EdgeWalk Experience", "category": "adventure", "estimated_cost": 85.0, "duration_hours": 2.0, "description": "Hands-free open-air walk on the ledge of the tower pod."},
            {"name": "Royal Ontario Museum", "category": "history", "estimated_cost": 24.0, "duration_hours": 3.0, "description": "World cultures, dinosaur fossils, and art collections."},
            {"name": "St. Lawrence Market Food Tour", "category": "food", "estimated_cost": 35.0, "duration_hours": 2.0, "description": "Peameal bacon sandwiches, local cheeses, and maple treats."},
            {"name": "Toronto Islands Ferry & Kayak", "category": "nature", "estimated_cost": 20.0, "duration_hours": 3.0, "description": "Scenic boat cruise and paddling with city skyline views."},
            {"name": "Distillery District Historic Boutiques", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 2.0, "description": "19th-century brick distillery turned arts district."},
        ]
    },
]


async def seed_database():
    """Seeds the database with cities, activities, demo user, and demo trips."""
    print("[Seed] Synchronizing database tables...")
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

        # 2. Insert Cities & Activities
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
                    )
                    session.add(activity)

                await session.flush()
            else:
                # Update lat/lon/desc if needed
                city.description = c_data["description"]
                city.latitude = c_data["latitude"]
                city.longitude = c_data["longitude"]
                city.cost_index = c_data["cost_index"]
                city.popularity_score = c_data["popularity_score"]
                session.add(city)
                await session.flush()

            created_cities[city.name] = city

        # 3. Create Sample Trips for demo user
        trips_res = await session.execute(select(Trip).where(Trip.user_id == demo_user.id))
        existing_trips = trips_res.scalars().all()

        if not existing_trips:
            print("[Seed] Creating 2 sample trips for demo user...")

            # --- Sample Trip 1: "Europe Explorer" ---
            # Paris (4 days), Rome (3 days), Barcelona (3 days) -> 10 days total
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
            # Bangkok (3 days), Bali (4 days), Singapore (2 days) -> 9 days total
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
            print("[Seed] Successfully seeded 2 sample trips with stops & activities!")
        else:
            print(f"[Seed] Trips already exist ({len(existing_trips)} found).")

    print("[Seed] Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
