import asyncio
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, Base, engine
from app.middleware.auth import hash_password
from app.models.activity import Activity
from app.models.budget import Budget
from app.models.city import City
from app.models.stop import Stop
from app.models.stop_activity import StopActivity
from app.models.trip import Trip
from app.models.user import User

# 20 Diverse Global Cities Data
CITIES_DATA = [
    {
        "name": "Paris",
        "country": "France",
        "region": "Europe",
        "cost_index": 220.0,
        "popularity_score": 98.0,
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "activities": [
            {"name": "Eiffel Tower Summit Tour", "type": "sightseeing", "cost": 35.0, "duration_hours": 2.5, "description": "Panoramic elevator ascent to the highest observation deck."},
            {"name": "Louvre Museum Masterpieces", "type": "sightseeing", "cost": 22.0, "duration_hours": 3.5, "description": "Guided walking tour through world famous Renaissance art."},
            {"name": "Montmartre Bakery & Pastry Walk", "type": "food", "cost": 45.0, "duration_hours": 2.0, "description": "Taste freshly baked croissants, baguettes, and macarons."},
            {"name": "Seine Sunset Dinner Cruise", "type": "food", "cost": 85.0, "duration_hours": 2.5, "description": "Fine 3-course French dining on an illuminated river boat."},
            {"name": "Catacombs Underground Exploration", "type": "adventure", "cost": 29.0, "duration_hours": 2.0, "description": "Subterranean labyrinth housing historical ossuaries."},
        ]
    },
    {
        "name": "Rome",
        "country": "Italy",
        "region": "Europe",
        "cost_index": 175.0,
        "popularity_score": 95.0,
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800",
        "activities": [
            {"name": "Colosseum & Roman Forum Tour", "type": "sightseeing", "cost": 30.0, "duration_hours": 3.0, "description": "Step into the gladiatorial arena and ancient imperial ruins."},
            {"name": "Vatican Museums & Sistine Chapel", "type": "sightseeing", "cost": 38.0, "duration_hours": 3.5, "description": "Marvel at Michelangelo's ceiling fresco and papal treasures."},
            {"name": "Trastevere Street Food & Wine Safari", "type": "food", "cost": 55.0, "duration_hours": 2.5, "description": "Authentic supplì, wood-fired pizza, and crisp Frascati wine."},
            {"name": "Handmade Pasta & Tiramisu Workshop", "type": "food", "cost": 65.0, "duration_hours": 3.0, "description": "Roll fresh fettuccine and whip up traditional Italian dessert."},
            {"name": "Appian Way E-Bike & Catacombs Ride", "type": "adventure", "cost": 49.0, "duration_hours": 4.0, "description": "Cycle the ancient cobblestone Roman military highway."},
        ]
    },
    {
        "name": "Barcelona",
        "country": "Spain",
        "region": "Europe",
        "cost_index": 160.0,
        "popularity_score": 93.0,
        "image_url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800",
        "activities": [
            {"name": "Sagrada Familia Basilica Tour", "type": "sightseeing", "cost": 28.0, "duration_hours": 2.0, "description": "Explore Antoni Gaudi's visionary modernist architectural masterpiece."},
            {"name": "Park Guell Mosaic Wonderland", "type": "sightseeing", "cost": 15.0, "duration_hours": 2.0, "description": "Vibrant tile benches and whimsical gingerbread gatehouses."},
            {"name": "Boqueria Market Tapas Tasting", "type": "food", "cost": 40.0, "duration_hours": 2.0, "description": "Sample Jamon Iberico, grilled calçots, and sangria."},
            {"name": "Paella Cooking Masterclass with Chef", "type": "food", "cost": 60.0, "duration_hours": 3.0, "description": "Cook seafood paella in an authentic rooftop kitchen."},
            {"name": "Barceloneta Paddleboarding & Kayak", "type": "adventure", "cost": 35.0, "duration_hours": 2.0, "description": "Morning Mediterranean coast water sports experience."},
        ]
    },
    {
        "name": "London",
        "country": "United Kingdom",
        "region": "Europe",
        "cost_index": 240.0,
        "popularity_score": 96.0,
        "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800",
        "activities": [
            {"name": "Tower of London & Crown Jewels", "type": "sightseeing", "cost": 34.0, "duration_hours": 2.5, "description": "Discover centuries of royal fortress and dungeon history."},
            {"name": "British Museum Guided Highlights", "type": "sightseeing", "cost": 20.0, "duration_hours": 2.5, "description": "Rosetta Stone and Parthenon Sculptures guided tour."},
            {"name": "Borough Market Artisanal Food Walk", "type": "food", "cost": 45.0, "duration_hours": 2.0, "description": "Gourmet cheeses, British sausage rolls, and sweet treats."},
            {"name": "Traditional Afternoon Tea at Mayfair", "type": "food", "cost": 65.0, "duration_hours": 1.5, "description": "Clotted cream scones and delicate finger sandwiches."},
            {"name": "Speedboat Thrill on River Thames", "type": "adventure", "cost": 50.0, "duration_hours": 1.0, "description": "High-octane RIB boat ride past Tower Bridge."},
        ]
    },
    {
        "name": "Amsterdam",
        "country": "Netherlands",
        "region": "Europe",
        "cost_index": 190.0,
        "popularity_score": 91.0,
        "image_url": "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800",
        "activities": [
            {"name": "Rijksmuseum & Rembrandt Gallery", "type": "sightseeing", "cost": 25.0, "duration_hours": 2.5, "description": "Dutch Golden Age masterpieces including The Night Watch."},
            {"name": "Canal Belt Historic Open Boat Cruise", "type": "sightseeing", "cost": 20.0, "duration_hours": 1.5, "description": "Scenic waterway cruise through UNESCO heritage bridges."},
            {"name": "Jordaan Cheese & Stroopwafel Tasting", "type": "food", "cost": 35.0, "duration_hours": 2.0, "description": "Aged Gouda tasting paired with local craft beers."},
            {"name": "Dutch Pancake & Herring Food Tour", "type": "food", "cost": 42.0, "duration_hours": 2.0, "description": "Street food bites across charming canal alleys."},
            {"name": "Countryside Windmill Cycling Tour", "type": "adventure", "cost": 48.0, "duration_hours": 4.0, "description": "Cycle to Zaanse Schans historic windmills and clog shops."},
        ]
    },
    {
        "name": "Tokyo",
        "country": "Japan",
        "region": "Asia",
        "cost_index": 180.0,
        "popularity_score": 99.0,
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800",
        "activities": [
            {"name": "Senso-ji Temple & Asakusa Heritage", "type": "sightseeing", "cost": 15.0, "duration_hours": 2.0, "description": "Tokyo's oldest Buddhist temple and traditional market stalls."},
            {"name": "Shibuya Sky Observation Deck", "type": "sightseeing", "cost": 20.0, "duration_hours": 1.5, "description": "Panoramic open-air view of Shibuya Scramble and Tokyo skyline."},
            {"name": "Tsukiji Outer Market Sushi Safari", "type": "food", "cost": 55.0, "duration_hours": 2.5, "description": "Ultra-fresh sashimi, wagyu skewers, and tamagoyaki."},
            {"name": "Shinjuku Omoide Yokocho Izakaya Tour", "type": "food", "cost": 60.0, "duration_hours": 2.5, "description": "Yakitori skewers and sake inside cozy alley taverns."},
            {"name": "Real-Life Street Karting Experience", "type": "adventure", "cost": 75.0, "duration_hours": 2.0, "description": "Costumed go-kart ride through central Tokyo streets."},
        ]
    },
    {
        "name": "Kyoto",
        "country": "Japan",
        "region": "Asia",
        "cost_index": 150.0,
        "popularity_score": 94.0,
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800",
        "activities": [
            {"name": "Fushimi Inari 10,000 Torii Gates Hike", "type": "sightseeing", "cost": 0.0, "duration_hours": 3.0, "description": "Climb sacred Mount Inari through vibrant vermilion shrines."},
            {"name": "Kinkaku-ji Golden Pavilion Tour", "type": "sightseeing", "cost": 10.0, "duration_hours": 1.5, "description": "Glistening Zen temple reflected on the surrounding mirror pond."},
            {"name": "Gion Geisha District Tea Ceremony", "type": "food", "cost": 45.0, "duration_hours": 1.5, "description": "Authentic ceremonial matcha preparation with sweet wagashi."},
            {"name": "Nishiki Market Kaiseki Tasting", "type": "food", "cost": 50.0, "duration_hours": 2.0, "description": "Taste Kyoto specialties in the city's 400-year-old pantry."},
            {"name": "Arashiyama Bamboo Grove & River Raft", "type": "adventure", "cost": 40.0, "duration_hours": 3.0, "description": "Towering bamboo stalks followed by scenic Hozugawa rafting."},
        ]
    },
    {
        "name": "Bangkok",
        "country": "Thailand",
        "region": "Asia",
        "cost_index": 70.0,
        "popularity_score": 92.0,
        "image_url": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800",
        "activities": [
            {"name": "Grand Palace & Wat Phra Kaew", "type": "sightseeing", "cost": 16.0, "duration_hours": 3.0, "description": "Opulent royal palace grounds and Emerald Buddha shrine."},
            {"name": "Wat Arun Dawn Temple Sunset", "type": "sightseeing", "cost": 5.0, "duration_hours": 1.5, "description": "Porcelain-decorated river temple with majestic spire."},
            {"name": "Chinatown Yaowarat Street Food Crawl", "type": "food", "cost": 25.0, "duration_hours": 2.5, "description": "Pad Thai, crispy pork belly, and mango sticky rice."},
            {"name": "Chef-Led Thai Culinary School Class", "type": "food", "cost": 38.0, "duration_hours": 3.5, "description": "Cook tom yum goong and green curry from scratch."},
            {"name": "Canal Longtail Boat & Floating Market", "type": "adventure", "cost": 30.0, "duration_hours": 3.0, "description": "Fast motorized longtail boat ride across historic canals."},
        ]
    },
    {
        "name": "Singapore",
        "country": "Singapore",
        "region": "Asia",
        "cost_index": 210.0,
        "popularity_score": 90.0,
        "image_url": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800",
        "activities": [
            {"name": "Gardens by the Bay & Supertree Grove", "type": "sightseeing", "cost": 28.0, "duration_hours": 3.0, "description": "Futuristic vertical gardens and Cloud Forest indoor waterfall."},
            {"name": "Marina Bay Sands SkyPark Deck", "type": "sightseeing", "cost": 24.0, "duration_hours": 1.5, "description": "Breathtaking 57th floor panoramic harbor observation deck."},
            {"name": "Michelin Hawker Center Food Safari", "type": "food", "cost": 30.0, "duration_hours": 2.5, "description": "Hainanese chicken rice, laksa, and satay skewers."},
            {"name": "Chinatown & Little India Culinary Trek", "type": "food", "cost": 40.0, "duration_hours": 2.5, "description": "Multicultural gastronomic journey across ethnic enclaves."},
            {"name": "Sentosa Mega Adventure Zipline", "type": "adventure", "cost": 45.0, "duration_hours": 2.0, "description": "High-speed 450m canopy zipline down to Siloso Beach."},
        ]
    },
    {
        "name": "Bali",
        "country": "Indonesia",
        "region": "Asia",
        "cost_index": 65.0,
        "popularity_score": 95.0,
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
        "activities": [
            {"name": "Uluwatu Cliff Temple & Kecak Dance", "type": "sightseeing", "cost": 15.0, "duration_hours": 3.0, "description": "Dramatic sunset cliff views accompanied by hypnotic fire dance."},
            {"name": "Tegallalang Rice Terraces Trek", "type": "sightseeing", "cost": 8.0, "duration_hours": 2.0, "description": "Lush emerald-green stepped hillsides and jungle swings."},
            {"name": "Jimbaran Bay Seafood Candlelit Dinner", "type": "food", "cost": 35.0, "duration_hours": 2.0, "description": "Fresh grilled snapper and prawns served right on the sand."},
            {"name": "Traditional Balinese Farm Cooking", "type": "food", "cost": 30.0, "duration_hours": 3.5, "description": "Harvest organic spices and grind traditional bumbu paste."},
            {"name": "Mount Batur Sunrise Volcano Trek", "type": "adventure", "cost": 45.0, "duration_hours": 5.0, "description": "Hike active volcano summit in time for stunning cloud sunrise."},
        ]
    },
    {
        "name": "New York City",
        "country": "United States",
        "region": "Americas",
        "cost_index": 260.0,
        "popularity_score": 97.0,
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800",
        "activities": [
            {"name": "Statue of Liberty & Ellis Island", "type": "sightseeing", "cost": 32.0, "duration_hours": 3.5, "description": "Ferry cruise to historic immigration museum and monument."},
            {"name": "Summit One Vanderbilt Glass View", "type": "sightseeing", "cost": 45.0, "duration_hours": 2.0, "description": "Immersive mirrors and glass skyboxes above Grand Central."},
            {"name": "Chelsea Market & High Line Food Tour", "type": "food", "cost": 65.0, "duration_hours": 2.5, "description": "Lobster rolls, artisanal chocolates, and historic rail park walk."},
            {"name": "Lower East Side Bagel & Pastrami Safari", "type": "food", "cost": 50.0, "duration_hours": 2.0, "description": "Katz's Deli style corned beef and hand-rolled bagels."},
            {"name": "Central Park Guided Bike Tour", "type": "adventure", "cost": 40.0, "duration_hours": 2.0, "description": "Cycle through 843 acres of bridges, lakes, and hidden trails."},
        ]
    },
    {
        "name": "San Francisco",
        "country": "United States",
        "region": "Americas",
        "cost_index": 230.0,
        "popularity_score": 88.0,
        "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800",
        "activities": [
            {"name": "Alcatraz Island Cellhouse Tour", "type": "sightseeing", "cost": 42.0, "duration_hours": 3.0, "description": "Ferry to the notorious federal prison on the bay."},
            {"name": "Golden Gate Bridge & Sausalito Cycle", "type": "sightseeing", "cost": 35.0, "duration_hours": 3.5, "description": "Ride across the iconic suspension bridge to Sausalito."},
            {"name": "Mission District Burrito & Mural Tour", "type": "food", "cost": 45.0, "duration_hours": 2.0, "description": "Mission-style burritos paired with vibrant Chicano street art."},
            {"name": "Ferry Building Artisanal Market Bites", "type": "food", "cost": 55.0, "duration_hours": 2.0, "description": "Artisan sourdough, Dungeness crab, and local cheeses."},
            {"name": "Bay Sunset Catamaran Sailing", "type": "adventure", "cost": 65.0, "duration_hours": 1.5, "description": "Sail under the Golden Gate Bridge aboard a twin-hull vessel."},
        ]
    },
    {
        "name": "Cancun",
        "country": "Mexico",
        "region": "Americas",
        "cost_index": 120.0,
        "popularity_score": 89.0,
        "image_url": "https://images.unsplash.com/photo-1518638150340-f706e86654de?w=800",
        "activities": [
            {"name": "Chichen Itza Mayan Wonder Day Tour", "type": "sightseeing", "cost": 55.0, "duration_hours": 6.0, "description": "Explore El Castillo pyramid and UNESCO ancient Mayan city."},
            {"name": "Tulum Oceanfront Ruins Walk", "type": "sightseeing", "cost": 25.0, "duration_hours": 2.5, "description": "Ancient walled port perched directly above turquoise waters."},
            {"name": "Authentic Taco & Mezcal Tasting Safari", "type": "food", "cost": 40.0, "duration_hours": 2.5, "description": "Al pastor tacos, ceviche, and artisanal Oaxaca mezcal."},
            {"name": "Yucatan Maya Cooking Workshop", "type": "food", "cost": 50.0, "duration_hours": 3.0, "description": "Traditional cochinita pibil and handmade corn tortillas."},
            {"name": "Cenote Cave Diving & Jungle Ziplines", "type": "adventure", "cost": 70.0, "duration_hours": 4.5, "description": "Swim crystal subterranean sinkholes and fly through treetops."},
        ]
    },
    {
        "name": "Rio de Janeiro",
        "country": "Brazil",
        "region": "Americas",
        "cost_index": 95.0,
        "popularity_score": 87.0,
        "image_url": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=800",
        "activities": [
            {"name": "Christ the Redeemer & Corcovado Train", "type": "sightseeing", "cost": 28.0, "duration_hours": 2.5, "description": "Iconic art deco monument with 360-degree city overlook."},
            {"name": "Sugarloaf Mountain Cable Car", "type": "sightseeing", "cost": 30.0, "duration_hours": 2.0, "description": "Two-stage aerial tramway above Guanabara Bay."},
            {"name": "Churrascaria Brazilian BBQ Feast", "type": "food", "cost": 45.0, "duration_hours": 2.0, "description": "All-you-can-eat picanha beef skewers carved tableside."},
            {"name": "Santa Teresa Bohemian Boteco Crawl", "type": "food", "cost": 35.0, "duration_hours": 2.5, "description": "Pastel de queijo and refreshing caipirinhas in hilltop taverns."},
            {"name": "Hang Gliding over Sao Conrado Beach", "type": "adventure", "cost": 120.0, "duration_hours": 2.0, "description": "Tandem glide from Pedra Bonita ramp onto coastal sands."},
        ]
    },
    {
        "name": "Buenos Aires",
        "country": "Argentina",
        "region": "Americas",
        "cost_index": 80.0,
        "popularity_score": 86.0,
        "image_url": "https://images.unsplash.com/photo-1612294037637-ec328d0e075e?w=800",
        "activities": [
            {"name": "Teatro Colon Architectural Tour", "type": "sightseeing", "cost": 18.0, "duration_hours": 1.5, "description": "Acoustically legendary opera house in classical European grandeur."},
            {"name": "Recoleta Cemetery & Eva Peron Tomb", "type": "sightseeing", "cost": 10.0, "duration_hours": 1.5, "description": "Elaborate marble mausoleums and aristocratic history."},
            {"name": "Palermo Steakhouse & Malbec Tasting", "type": "food", "cost": 42.0, "duration_hours": 2.5, "description": "Grass-fed bife de chorizo paired with premium Mendoza wine."},
            {"name": "Empanada Making & Yerba Mate Class", "type": "food", "cost": 32.0, "duration_hours": 2.0, "description": "Fold artisanal repulgues and learn sacred mate etiquette."},
            {"name": "San Telmo Tango Milonga Experience", "type": "adventure", "cost": 35.0, "duration_hours": 3.0, "description": "Dance lessons followed by live midnight orchestra tango club."},
        ]
    },
    {
        "name": "Sydney",
        "country": "Australia",
        "region": "Oceania",
        "cost_index": 215.0,
        "popularity_score": 93.0,
        "image_url": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800",
        "activities": [
            {"name": "Sydney Opera House Inside Tour", "type": "sightseeing", "cost": 33.0, "duration_hours": 1.5, "description": "Discover Utzon's architecture under iconic sail shells."},
            {"name": "Bondi to Coogee Coastal Walk", "type": "sightseeing", "cost": 0.0, "duration_hours": 2.5, "description": "Dramatic sandstone cliffs and ocean pool panoramas."},
            {"name": "Sydney Fish Market Oyster Feasting", "type": "food", "cost": 45.0, "duration_hours": 1.5, "description": "Freshly shucked Sydney rock oysters and grilled barramundi."},
            {"name": "Surry Hills Specialty Coffee & Brunch", "type": "food", "cost": 35.0, "duration_hours": 2.0, "description": "Aussie flat whites, avocado smash, and ricotta hotcakes."},
            {"name": "Sydney Harbour BridgeClimb", "type": "adventure", "cost": 195.0, "duration_hours": 3.5, "description": "Climb 134 meters to the summit of the world famous bridge."},
        ]
    },
    {
        "name": "Dubai",
        "country": "United Arab Emirates",
        "region": "Middle East",
        "cost_index": 250.0,
        "popularity_score": 92.0,
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800",
        "activities": [
            {"name": "Burj Khalifa At the Top (124th Floor)", "type": "sightseeing", "cost": 45.0, "duration_hours": 2.0, "description": "Ride high speed lift to the world's tallest tower observatory."},
            {"name": "Dubai Miracle Garden & Floral Domes", "type": "sightseeing", "cost": 20.0, "duration_hours": 2.5, "description": "Over 150 million blooming flowers in fantastical sculptures."},
            {"name": "Al Fahidi Heritage & Shawarma Walk", "type": "food", "cost": 35.0, "duration_hours": 2.0, "description": "Traditional Emirati coffee, cardamom sweets, and chicken wraps."},
            {"name": "Luxury Marina Yacht Dinner Cruise", "type": "food", "cost": 80.0, "duration_hours": 2.5, "description": "International buffet dinner cruise past illuminated skyscrapers."},
            {"name": "Red Dune Desert Safari & Dune Bashing", "type": "adventure", "cost": 65.0, "duration_hours": 5.0, "description": "4x4 sand drifting, camel riding, and starlit BBQ camp."},
        ]
    },
    {
        "name": "Cairo",
        "country": "Egypt",
        "region": "Africa",
        "cost_index": 55.0,
        "popularity_score": 88.0,
        "image_url": "https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=800",
        "activities": [
            {"name": "Giza Pyramids & Great Sphinx Tour", "type": "sightseeing", "cost": 25.0, "duration_hours": 3.5, "description": "Explore the last standing ancient Wonder of the World."},
            {"name": "Grand Egyptian Museum & King Tut", "type": "sightseeing", "cost": 30.0, "duration_hours": 3.0, "description": "Treasures of Tutankhamun and pharaonic antiquities."},
            {"name": "Khan el-Khalili Bazaar Tea & Koshary", "type": "food", "cost": 15.0, "duration_hours": 2.0, "description": "Eat iconic Egyptian koshary and sip mint tea in El Fishawy."},
            {"name": "Nile Felucca Sailing with Mezze Lunch", "type": "food", "cost": 28.0, "duration_hours": 2.0, "description": "Traditional wooden sailboat with hummus and grilled kofta."},
            {"name": "Quad Biking by Giza Desert Sands", "type": "adventure", "cost": 40.0, "duration_hours": 2.0, "description": "ATV sand racing with backdrop views of the pyramids."},
        ]
    },
    {
        "name": "Cape Town",
        "country": "South Africa",
        "region": "Africa",
        "cost_index": 110.0,
        "popularity_score": 91.0,
        "image_url": "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=800",
        "activities": [
            {"name": "Table Mountain Aerial Cableway", "type": "sightseeing", "cost": 25.0, "duration_hours": 2.0, "description": "Revolving cable car to flat top plateau overlooking two oceans."},
            {"name": "Boulders Beach African Penguin Colony", "type": "sightseeing", "cost": 12.0, "duration_hours": 2.0, "description": "Boardwalks surrounded by wild breeding African penguins."},
            {"name": "Bo-Kaap Malay Spice & Samosa Tour", "type": "food", "cost": 30.0, "duration_hours": 2.0, "description": "Brightly painted cottages and Cape Malay curry tasting."},
            {"name": "Stellenbosch Vineyard Wine & Cheese", "type": "food", "cost": 55.0, "duration_hours": 4.5, "description": "Sample award-winning Pinotage in historic Cape Dutch estates."},
            {"name": "Shark Cage Diving at Gansbaai", "type": "adventure", "cost": 150.0, "duration_hours": 5.0, "description": "Up-close marine encounter with great white sharks."},
        ]
    },
    {
        "name": "Reykjavik",
        "country": "Iceland",
        "region": "Europe",
        "cost_index": 260.0,
        "popularity_score": 90.0,
        "image_url": "https://images.unsplash.com/photo-1504893524553-b855bce32c67?w=800",
        "activities": [
            {"name": "Golden Circle Geysir & Gullfoss", "type": "sightseeing", "cost": 65.0, "duration_hours": 6.0, "description": "Continental tectonic rift, exploding hot springs, and roaring waterfalls."},
            {"name": "Northern Lights Aurora Hunt", "type": "sightseeing", "cost": 55.0, "duration_hours": 4.0, "description": "Super-jeep excursion to dark skies for aurora borealis."},
            {"name": "Reykjavik Rye Bread & Smoked Lamb Walk", "type": "food", "cost": 60.0, "duration_hours": 2.5, "description": "Geothermally baked bread, Arctic char, and Skyr desserts."},
            {"name": "Blue Lagoon Geothermal Spa & Drinks", "type": "food", "cost": 95.0, "duration_hours": 3.0, "description": "Mineral-rich silica mud mask and swim-up bar cocktails."},
            {"name": "Solheimajokull Glacier Ice Hike & Crevasses", "type": "adventure", "cost": 110.0, "duration_hours": 4.0, "description": "Crampon and ice axe trek across ancient glacial ice."},
        ]
    },
]


async def seed_database():
    """Seeds the database with cities, activities, demo user, and demo trips."""
    print("[Seed] Connecting to database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Check or Insert Demo User
        demo_email = "demo@globetrotter.com"
        user_res = await session.execute(select(User).where(User.email == demo_email))
        demo_user = user_res.scalar_one_or_none()

        if demo_user is None:
            demo_user = User(
                name="Demo Traveler",
                email=demo_email,
                password_hash=hash_password("demo1234"),
                profile_photo="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
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
                    cost_index=c_data["cost_index"],
                    popularity_score=c_data["popularity_score"],
                    image_url=c_data["image_url"],
                )
                session.add(city)
                await session.flush()
                print(f"[Seed] Added city: {city.name} ({city.country})")

                # Add 5 activities for this city
                for act_data in c_data["activities"]:
                    activity = Activity(
                        city_id=city.id,
                        name=act_data["name"],
                        type=act_data["type"],
                        description=act_data["description"],
                        cost=act_data["cost"],
                        duration_hours=act_data["duration_hours"],
                        image_url=city.image_url,
                    )
                    session.add(activity)

                await session.flush()
            created_cities[city.name] = city

        # 3. Check or Insert Demo Trips for Demo User
        trips_res = await session.execute(select(Trip).where(Trip.user_id == demo_user.id))
        existing_trips = trips_res.scalars().all()

        if not existing_trips:
            print("[Seed] Creating 2 sample trips for demo user...")

            # --- Sample Trip 1: "Grand European Adventure" (Paris -> Rome -> Barcelona) ---
            start_date1 = date.today() + timedelta(days=30)
            end_date1 = start_date1 + timedelta(days=10)

            trip1 = Trip(
                user_id=demo_user.id,
                title="Grand European Odyssey",
                description="A scenic cultural escapade across Paris, Rome, and Barcelona with culinary highlights.",
                start_date=start_date1,
                end_date=end_date1,
                cover_photo="https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800",
                is_public=True,
            )
            session.add(trip1)
            await session.flush()

            budget1 = Budget(
                trip_id=trip1.id,
                transport_cost=350.0,
                stay_cost=0.0,
                meals_cost=0.0,
                misc_cost=50.0,
                total_budget_limit=2500.0,
            )
            session.add(budget1)
            await session.flush()

            # Add Stop 1 (Paris)
            paris = created_cities["Paris"]
            stop1 = Stop(
                trip_id=trip1.id,
                city_id=paris.id,
                arrival_date=start_date1,
                departure_date=start_date1 + timedelta(days=4),
                order_index=0,
            )
            session.add(stop1)
            await session.flush()

            # Assign activity in Paris
            paris_acts = (await session.execute(select(Activity).where(Activity.city_id == paris.id))).scalars().all()
            if paris_acts:
                session.add(StopActivity(stop_id=stop1.id, activity_id=paris_acts[0].id, scheduled_date=start_date1 + timedelta(days=1)))
                session.add(StopActivity(stop_id=stop1.id, activity_id=paris_acts[2].id, scheduled_date=start_date1 + timedelta(days=2)))

            # Add Stop 2 (Rome)
            rome = created_cities["Rome"]
            stop2 = Stop(
                trip_id=trip1.id,
                city_id=rome.id,
                arrival_date=start_date1 + timedelta(days=4),
                departure_date=start_date1 + timedelta(days=7),
                order_index=1,
            )
            session.add(stop2)
            await session.flush()

            rome_acts = (await session.execute(select(Activity).where(Activity.city_id == rome.id))).scalars().all()
            if rome_acts:
                session.add(StopActivity(stop_id=stop2.id, activity_id=rome_acts[0].id, scheduled_date=start_date1 + timedelta(days=5)))
                session.add(StopActivity(stop_id=stop2.id, activity_id=rome_acts[3].id, scheduled_date=start_date1 + timedelta(days=6)))

            # Add Stop 3 (Barcelona)
            bcn = created_cities["Barcelona"]
            stop3 = Stop(
                trip_id=trip1.id,
                city_id=bcn.id,
                arrival_date=start_date1 + timedelta(days=7),
                departure_date=end_date1,
                order_index=2,
            )
            session.add(stop3)
            await session.flush()

            bcn_acts = (await session.execute(select(Activity).where(Activity.city_id == bcn.id))).scalars().all()
            if bcn_acts:
                session.add(StopActivity(stop_id=stop3.id, activity_id=bcn_acts[0].id, scheduled_date=start_date1 + timedelta(days=8)))

            # --- Sample Trip 2: "Colors of Japan" (Tokyo -> Kyoto) ---
            start_date2 = date.today() + timedelta(days=90)
            end_date2 = start_date2 + timedelta(days=7)

            trip2 = Trip(
                user_id=demo_user.id,
                title="Colors of Japan",
                description="Exploring futuristic Tokyo neon streets and ancient tranquil Kyoto temples.",
                start_date=start_date2,
                end_date=end_date2,
                cover_photo="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800",
                is_public=False,
            )
            session.add(trip2)
            await session.flush()

            budget2 = Budget(
                trip_id=trip2.id,
                transport_cost=280.0,
                stay_cost=0.0,
                meals_cost=0.0,
                misc_cost=40.0,
                total_budget_limit=2000.0,
            )
            session.add(budget2)
            await session.flush()

            # Add Tokyo Stop
            tokyo = created_cities["Tokyo"]
            stop_tokyo = Stop(
                trip_id=trip2.id,
                city_id=tokyo.id,
                arrival_date=start_date2,
                departure_date=start_date2 + timedelta(days=4),
                order_index=0,
            )
            session.add(stop_tokyo)
            await session.flush()

            tokyo_acts = (await session.execute(select(Activity).where(Activity.city_id == tokyo.id))).scalars().all()
            if tokyo_acts:
                session.add(StopActivity(stop_id=stop_tokyo.id, activity_id=tokyo_acts[0].id, scheduled_date=start_date2 + timedelta(days=1)))
                session.add(StopActivity(stop_id=stop_tokyo.id, activity_id=tokyo_acts[2].id, scheduled_date=start_date2 + timedelta(days=2)))

            # Add Kyoto Stop
            kyoto = created_cities["Kyoto"]
            stop_kyoto = Stop(
                trip_id=trip2.id,
                city_id=kyoto.id,
                arrival_date=start_date2 + timedelta(days=4),
                departure_date=end_date2,
                order_index=1,
            )
            session.add(stop_kyoto)
            await session.flush()

            kyoto_acts = (await session.execute(select(Activity).where(Activity.city_id == kyoto.id))).scalars().all()
            if kyoto_acts:
                session.add(StopActivity(stop_id=stop_kyoto.id, activity_id=kyoto_acts[0].id, scheduled_date=start_date2 + timedelta(days=5)))

            await session.commit()
            print("[Seed] Successfully seeded demo trips and scheduled activities.")
        else:
            print(f"[Seed] Sample trips already exist ({len(existing_trips)} trips found).")

    print("[Seed] Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
