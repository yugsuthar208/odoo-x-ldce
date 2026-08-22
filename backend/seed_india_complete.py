import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.city import City
from app.models.activity import Activity

# Comprehensive 75+ Destinations Spanning All Indian Regions
INDIAN_DESTINATIONS = [
    # -------------------------------------------------------------------------
    # 1. RAJASTHAN & HERITAGE PALACES
    # -------------------------------------------------------------------------
    {
        "name": "Udaipur", "country": "India", "region": "West & Rajasthan",
        "cost_index": 55.0, "popularity_score": 9.7, "latitude": 24.5854, "longitude": 73.7125,
        "tags": ["lakes", "palaces", "romantic", "heritage", "photography"],
        "vibe_tags": ["royal", "romantic", "serene"],
        "climate_type": "arid", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 88.0, "budget_tier": "mid-range", "rent_index": 22.0, "restaurant_price_index": 35.0,
        "description": "The City of Lakes and Venice of the East, Udaipur is famed for its grand marble palaces floating on serene waters, royal courtyards, and vibrant Mewari arts.",
        "image_url": "https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?w=800",
        "activities": [
            {"name": "City Palace & Crystal Gallery Tour", "category": "history", "estimated_cost": 400.0, "duration_hours": 3.0, "tags": ["palace", "royal", "museum"], "vibe": "regal", "best_for": ["couple", "family", "solo"], "description": "Explore Rajasthan's largest royal palace complex with ornate mosaic courtyards."},
            {"name": "Lake Pichola Sunset Boat Ride to Jag Mandir", "category": "sightseeing", "estimated_cost": 500.0, "duration_hours": 1.5, "tags": ["lake", "boat", "sunset"], "vibe": "romantic", "best_for": ["couple", "family"], "description": "Scenic boat cruise passing the iconic Lake Palace with panoramic Aravalli views."},
            {"name": "Dharohar Folk Dance Show at Bagore Ki Haveli", "category": "history", "estimated_cost": 150.0, "duration_hours": 1.5, "tags": ["folk_dance", "culture", "puppetry"], "vibe": "cultural", "best_for": ["family", "couple", "solo"], "description": "Live Rajasthani Ghoomar and Chari fire dance inside an 18th-century waterfront haveli."},
            {"name": "Authentic Mewari Thali at Traditional Dining Hall", "category": "food", "estimated_cost": 450.0, "duration_hours": 1.5, "tags": ["mewari", "thali", "ker_sangri"], "vibe": "delightful", "best_for": ["foodie", "family"], "description": "Unlimited authentic Mewari thali featuring Dal Baati, Gatte, and Malpua."},
        ]
    },
    {
        "name": "Jodhpur", "country": "India", "region": "West & Rajasthan",
        "cost_index": 45.0, "popularity_score": 9.3, "latitude": 26.2389, "longitude": 73.0243,
        "tags": ["blue_city", "forts", "heritage", "bazaars", "handicrafts"],
        "vibe_tags": ["majestic", "blue", "historic"],
        "climate_type": "arid", "best_months": ["October", "November", "December", "January", "February"],
        "safety_index": 82.0, "budget_tier": "budget", "rent_index": 18.0, "restaurant_price_index": 28.0,
        "description": "The Blue City is commanded by the colossal Mehrangarh Fort rising high above a sea of indigo-washed Brahmin houses at the edge of the Thar Desert.",
        "image_url": "https://images.unsplash.com/photo-1572445271230-a78b5944a659?w=800",
        "activities": [
            {"name": "Mehrangarh Fort & Flying Fox Zipline", "category": "adventure", "estimated_cost": 1800.0, "duration_hours": 3.5, "tags": ["fort", "zipline", "views"], "vibe": "thrilling", "best_for": ["group", "solo", "couple"], "description": "Glide across desert moats and explore medieval armories inside the grandest fort of India."},
            {"name": "Blue City Old Quarter Heritage Walking Tour", "category": "sightseeing", "estimated_cost": 250.0, "duration_hours": 2.0, "tags": ["blue_houses", "photography", "alleys"], "vibe": "charming", "best_for": ["solo", "couple"], "description": "Navigate vibrant cobalt-blue alleyways and photograph century-old stepwells like Toorji Ka Jhalra."},
            {"name": "Shahi Samosa & Makhaniya Lassi at Clock Tower", "category": "food", "estimated_cost": 100.0, "duration_hours": 1.0, "tags": ["street_food", "lassi", "samosa"], "vibe": "lively", "best_for": ["foodie", "group"], "description": "Taste the legendary thick saffron Makhaniya lassi and spicy Pyaaz kachori at Sardar Market."},
        ]
    },
    {
        "name": "Jaisalmer", "country": "India", "region": "West & Rajasthan",
        "cost_index": 48.0, "popularity_score": 9.4, "latitude": 26.9157, "longitude": 70.9083,
        "tags": ["golden_city", "desert_safari", "forts", "camping", "dunes"],
        "vibe_tags": ["golden", "exotic", "desert"],
        "climate_type": "arid", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 85.0, "budget_tier": "budget", "rent_index": 16.0, "restaurant_price_index": 30.0,
        "description": "The Golden City sparkles like a sandstone mirage in the heart of the Thar Desert, boasting India's only living medieval fort and golden dunes.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=800",
        "activities": [
            {"name": "Sam Sand Dunes Camel Safari & Luxury Camp", "category": "adventure", "estimated_cost": 2200.0, "duration_hours": 6.0, "tags": ["camel", "dunes", "camping", "folk_music"], "vibe": "exotic", "best_for": ["group", "couple", "family"], "description": "Sunset camel trek into undulating sand dunes followed by Kalbelia folk performance and desert camp dinner."},
            {"name": "Jaisalmer Living Golden Fort & Jain Temples", "category": "history", "estimated_cost": 200.0, "duration_hours": 2.5, "tags": ["living_fort", "jain_temple", "sandstone"], "vibe": "mystical", "best_for": ["solo", "family"], "description": "Wander through the yellow sandstone citadel where a quarter of the city's population still resides."},
            {"name": "Patwon Ki Haveli Intricate Stone Carving Tour", "category": "sightseeing", "estimated_cost": 100.0, "duration_hours": 1.5, "tags": ["haveli", "carvings", "architecture"], "vibe": "cultural", "best_for": ["couple", "solo"], "description": "Marvel at 5 interconnected havelis boasting the finest stone jali carvings in India."},
        ]
    },
    {
        "name": "Ranthambore", "country": "India", "region": "West & Rajasthan",
        "cost_index": 65.0, "popularity_score": 9.1, "latitude": 26.0173, "longitude": 76.5026,
        "tags": ["tigers", "wildlife", "safari", "national_park", "nature"],
        "vibe_tags": ["wild", "thrilling", "natural"],
        "climate_type": "semi-arid", "best_months": ["October", "November", "December", "January", "February", "March", "April", "May"],
        "safety_index": 85.0, "budget_tier": "mid-range", "rent_index": 20.0, "restaurant_price_index": 35.0,
        "description": "One of India's premier tiger reserves, where royal Bengal tigers roam freely amidst historic 10th-century jungle ruins, ancient banyan trees, and lake pavilions.",
        "image_url": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=800",
        "activities": [
            {"name": "Royal Bengal Tiger Morning Gypsy Safari", "category": "adventure", "estimated_cost": 2500.0, "duration_hours": 3.5, "tags": ["tiger", "safari", "wildlife"], "vibe": "thrilling", "best_for": ["group", "family", "solo"], "description": "Open-top 4x4 safari through prime tiger zones, leopards, and marsh crocodiles."},
            {"name": "Ancient Ranthambore Fort & Trinetra Ganesha Hike", "category": "history", "estimated_cost": 100.0, "duration_hours": 2.5, "tags": ["fort", "temple", "views"], "vibe": "spiritual", "best_for": ["family", "couple"], "description": "Hike to the UNESCO World Heritage hilltop fort offering panoramic canopy views."},
        ]
    },

    # -------------------------------------------------------------------------
    # 2. HIMALAYAS & NORTHERN HILL STATIONS
    # -------------------------------------------------------------------------
    {
        "name": "Manali", "country": "India", "region": "North India (Himalayas)",
        "cost_index": 50.0, "popularity_score": 9.8, "latitude": 32.2396, "longitude": 77.1887,
        "tags": ["snow", "mountains", "trekking", "adventure", "rivers"],
        "vibe_tags": ["alpine", "adventurous", "romantic"],
        "climate_type": "alpine", "best_months": ["October", "November", "December", "January", "February", "May", "June"],
        "safety_index": 86.0, "budget_tier": "budget", "rent_index": 22.0, "restaurant_price_index": 32.0,
        "description": "Perched in Himachal's Beas River valley, Manali is India's adventure capital for snow sports, pine forest trails, Himalayan cafes, and mountain passes.",
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800",
        "activities": [
            {"name": "Solang Valley Paragliding & Snow Activities", "category": "adventure", "estimated_cost": 2500.0, "duration_hours": 4.0, "tags": ["paragliding", "snow", "skiing"], "vibe": "thrilling", "best_for": ["group", "couple", "solo"], "description": "High-altitude tandem paragliding and zorbing with snow-capped mountain views."},
            {"name": "Rohtang Pass & Atal Tunnel Snow Excursion", "category": "sightseeing", "estimated_cost": 3000.0, "duration_hours": 6.0, "tags": ["snow_pass", "atal_tunnel", "glaciers"], "vibe": "majestic", "best_for": ["family", "couple", "group"], "description": "Drive through the world's longest high-altitude tunnel into snowscapes."},
            {"name": "Old Manali Hippie Cafe & Trout Fish Trail", "category": "food", "estimated_cost": 600.0, "duration_hours": 2.5, "tags": ["trout", "cafes", "woodfired_pizza"], "vibe": "relaxing", "best_for": ["solo", "couple", "group"], "description": "Sample fresh Himalayan river trout and wood-fired pizza by roaring mountain streams."},
            {"name": "Hadimba Devi Cedar Forest Wooden Temple", "category": "history", "estimated_cost": 50.0, "duration_hours": 1.5, "tags": ["temple", "cedar", "heritage"], "vibe": "peaceful", "best_for": ["family", "solo"], "description": "Unique 16th-century pagoda-style wooden temple sheltered by giant Deodar pine trees."},
        ]
    },
    {
        "name": "Leh Ladakh", "country": "India", "region": "North India (Himalayas)",
        "cost_index": 65.0, "popularity_score": 9.9, "latitude": 34.1526, "longitude": 77.5771,
        "tags": ["biking", "monasteries", "high_altitude", "lakes", "valleys"],
        "vibe_tags": ["mystical", "epic", "breathtaking"],
        "climate_type": "cold-desert", "best_months": ["May", "June", "July", "August", "September"],
        "safety_index": 92.0, "budget_tier": "mid-range", "rent_index": 25.0, "restaurant_price_index": 35.0,
        "description": "The Land of High Passes, Ladakh stuns with lunar landscapes, turquoise high-altitude lakes, ancient Tibetan Buddhist gompas, and world's highest motorable roads.",
        "image_url": "https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?w=800",
        "activities": [
            {"name": "Pangong Tso Blue Lake Overnight Camping", "category": "nature", "estimated_cost": 3500.0, "duration_hours": 8.0, "tags": ["pangong", "lake", "stargazing"], "vibe": "surreal", "best_for": ["group", "couple", "solo"], "description": "Camp alongside the world's highest saltwater lake that changes color from blue to green."},
            {"name": "Khardung La Pass Himalayan Motorcycle Expedition", "category": "adventure", "estimated_cost": 2800.0, "duration_hours": 5.0, "tags": ["biking", "khardungla", "pass"], "vibe": "epic", "best_for": ["solo", "group"], "description": "Ride Royal Enfield motorcycles across one of the world's highest motorable passes at 17,982 ft."},
            {"name": "Thiksey & Hemis Monastery Morning Chants", "category": "history", "estimated_cost": 100.0, "duration_hours": 3.0, "tags": ["monastery", "buddhism", "meditation"], "vibe": "serene", "best_for": ["solo", "couple", "family"], "description": "Experience deep Tibetan horn blasts and monk chants inside 12-story cliffside gompas."},
            {"name": "Nubra Valley Double-Humped Camel Safari", "category": "adventure", "estimated_cost": 800.0, "duration_hours": 2.5, "tags": ["nubra", "bactrian_camel", "sand_dunes"], "vibe": "exotic", "best_for": ["family", "couple", "group"], "description": "Ride rare double-humped Bactrian camels through the white sand dunes of Hunder."},
        ]
    },
    {
        "name": "Rishikesh", "country": "India", "region": "North India (Himalayas)",
        "cost_index": 40.0, "popularity_score": 9.6, "latitude": 30.0869, "longitude": 78.2676,
        "tags": ["river_rafting", "yoga", "ganga", "bungee", "spiritual"],
        "vibe_tags": ["spiritual", "thrilling", "zen"],
        "climate_type": "temperate", "best_months": ["September", "October", "November", "February", "March", "April", "May"],
        "safety_index": 88.0, "budget_tier": "budget", "rent_index": 16.0, "restaurant_price_index": 25.0,
        "description": "The Yoga Capital of the World where the emerald Ganga emerges from the Himalayas, celebrated for white water river rafting, bungee jumping, and cliffside ashrams.",
        "image_url": "https://images.unsplash.com/photo-1596701062351-8c2c14d1fdd0?w=800",
        "activities": [
            {"name": "Ganga White Water River Rafting (16km Shivpuri to Laxman Jhula)", "category": "adventure", "estimated_cost": 1000.0, "duration_hours": 3.5, "tags": ["rafting", "rapids", "ganga"], "vibe": "thrilling", "best_for": ["group", "solo", "couple"], "description": "Tackle grade III/IV rapids (Roller Coaster & Golf Course) and cliff jumping."},
            {"name": "Triveni Ghat Evening Maha Ganga Aarti", "category": "history", "estimated_cost": 0.0, "duration_hours": 1.5, "tags": ["aarti", "ganga", "spiritual"], "vibe": "divine", "best_for": ["family", "solo", "couple"], "description": "Mesmerizing synchronized fire lamp rituals and Vedic chanting by the river banks."},
            {"name": "Beatles Ashram (Chaurasi Kutia) Meditation Walk", "category": "sightseeing", "estimated_cost": 150.0, "duration_hours": 2.0, "tags": ["beatles", "graffiti", "meditation"], "vibe": "artistic", "best_for": ["solo", "couple"], "description": "Explore meditation caves where The Beatles wrote the White Album in 1968."},
            {"name": "Jumpin Heights 83-Meter Bungee Jump", "category": "adventure", "estimated_cost": 3900.0, "duration_hours": 2.0, "tags": ["bungee", "extreme", "canyon"], "vibe": "extreme", "best_for": ["solo", "group"], "description": "India's highest fixed-platform bungee jump suspended over the Hall river canyon."},
        ]
    },
    {
        "name": "Srinagar", "country": "India", "region": "North India (Himalayas)",
        "cost_index": 55.0, "popularity_score": 9.5, "latitude": 34.0837, "longitude": 74.7973,
        "tags": ["dal_lake", "shikara", "houseboats", "tulips", "mughal_gardens"],
        "vibe_tags": ["paradise", "romantic", "peaceful"],
        "climate_type": "temperate", "best_months": ["March", "April", "May", "June", "September", "October", "December", "January"],
        "safety_index": 78.0, "budget_tier": "mid-range", "rent_index": 20.0, "restaurant_price_index": 35.0,
        "description": "Known as Paradise on Earth, Srinagar enchants with intricately carved cedar houseboats on Dal Lake, floating vegetable markets, and terraced Mughal gardens.",
        "image_url": "https://images.unsplash.com/photo-1598091383021-15ddea10925d?w=800",
        "activities": [
            {"name": "Dal Lake Sunset Shikara Ride & Floating Market", "category": "sightseeing", "estimated_cost": 700.0, "duration_hours": 2.0, "tags": ["shikara", "dal_lake", "floating_market"], "vibe": "romantic", "best_for": ["couple", "family", "solo"], "description": "Glide past lotus gardens and historic water channels in a traditional cushioned gondola."},
            {"name": "Traditional Kashmiri Wazwan Feast", "category": "food", "estimated_cost": 850.0, "duration_hours": 2.0, "tags": ["wazwan", "rogan_josh", "gushtaba"], "vibe": "royal", "best_for": ["foodie", "family"], "description": "Multi-course royal banquet featuring Rogan Josh, Rista, Gushtaba, and Kahwa tea."},
            {"name": "Nishat & Shalimar Mughal Garden Terraces Walk", "category": "nature", "estimated_cost": 50.0, "duration_hours": 2.0, "tags": ["mughal_garden", "fountains", "chinar"], "vibe": "relaxing", "best_for": ["family", "couple"], "description": "Stroll amidst cascading water fountains and towering centuries-old Chinar trees."},
            {"name": "Gulmarg Gondola to Apharwat Peak (13,780 ft)", "category": "adventure", "estimated_cost": 1700.0, "duration_hours": 4.0, "tags": ["gondola", "snow", "skiing"], "vibe": "majestic", "best_for": ["group", "couple", "family"], "description": "Asia's highest cable car taking you to year-round snowfields and world-class ski slopes."},
        ]
    },
    {
        "name": "Shimla", "country": "India", "region": "North India (Himalayas)",
        "cost_index": 48.0, "popularity_score": 9.2, "latitude": 31.1048, "longitude": 77.1734,
        "tags": ["mall_road", "toy_train", "colonial", "hills", "snow"],
        "vibe_tags": ["colonial", "scenic", "nostalgic"],
        "climate_type": "temperate", "best_months": ["October", "November", "December", "January", "March", "April", "May", "June"],
        "safety_index": 88.0, "budget_tier": "budget", "rent_index": 20.0, "restaurant_price_index": 30.0,
        "description": "The erstwhile British summer capital, Shimla boasts Victorian architecture, the UNESCO Kalka-Shimla Toy Train, and sweeping pine-covered ridge walks.",
        "image_url": "https://images.unsplash.com/photo-1562832135-14a35d25edef?w=800",
        "activities": [
            {"name": "Kalka-Shimla UNESCO Heritage Toy Train Ride", "category": "sightseeing", "estimated_cost": 300.0, "duration_hours": 4.5, "tags": ["toy_train", "unesco", "tunnels"], "vibe": "nostalgic", "best_for": ["family", "couple"], "description": "Chug through 102 tunnels and over 800 bridges traversing steep Himalayan pine slopes."},
            {"name": "The Ridge & Christ Church Evening Stroll", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["ridge", "mall_road", "colonial"], "vibe": "vibrant", "best_for": ["couple", "family", "solo"], "description": "Pedestrian-only promenade overlooking mountain valleys with Victorian-era landmarks."},
            {"name": "Jakhu Temple Ropeway & Giant Hanuman Statue", "category": "adventure", "estimated_cost": 500.0, "duration_hours": 2.0, "tags": ["ropeway", "temple", "views"], "vibe": "spiritual", "best_for": ["family", "solo"], "description": "Aerial cable car ascent to Shimla's highest peak crowned by a 108-ft orange colossus."},
        ]
    },

    # -------------------------------------------------------------------------
    # 3. WESTERN INDIA & GUJARAT
    # -------------------------------------------------------------------------
    {
        "name": "Rann of Kutch", "country": "India", "region": "West & Rajasthan",
        "cost_index": 60.0, "popularity_score": 9.5, "latitude": 23.8342, "longitude": 69.8329,
        "tags": ["white_desert", "rann_utsav", "handicrafts", "salt_flats", "full_moon"],
        "vibe_tags": ["surreal", "cultural", "magical"],
        "climate_type": "arid", "best_months": ["November", "December", "January", "February"],
        "safety_index": 92.0, "budget_tier": "mid-range", "rent_index": 20.0, "restaurant_price_index": 35.0,
        "description": "The world's largest salt desert transforms under winter full moons into an endless shimmering white paradise celebrating the grand Rann Utsav cultural carnival.",
        "image_url": "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=800",
        "activities": [
            {"name": "White Rann Sunset to Full Moon Walking Experience", "category": "nature", "estimated_cost": 200.0, "duration_hours": 3.0, "tags": ["salt_desert", "sunset", "full_moon"], "vibe": "magical", "best_for": ["couple", "family", "solo"], "description": "Walk endless miles onto crystalline salt beds reflecting the golden sunset and starry sky."},
            {"name": "Rann Utsav Tent City Cultural Carnival", "category": "sightseeing", "estimated_cost": 2500.0, "duration_hours": 5.0, "tags": ["carnival", "folk_dance", "gujarati_culture"], "vibe": "vibrant", "best_for": ["family", "couple", "group"], "description": "Live Kutchi folk music, traditional Garba, camel cart rides, and artisan workshops."},
            {"name": "Bhujodi & Nirona Artisan Craft Trail (Rogan Art & Ajrakh)", "category": "shopping", "estimated_cost": 0.0, "duration_hours": 3.0, "tags": ["rogan_art", "handicrafts", "textiles"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "Meet master craftsmen practicing 300-year-old castor oil Rogan art and copper bells."},
            {"name": "Authentic Kutchi Thali Feast (Khichdi & Kadhi)", "category": "food", "estimated_cost": 300.0, "duration_hours": 1.5, "tags": ["kutchi", "rotla", "jaggery"], "vibe": "delightful", "best_for": ["foodie", "family"], "description": "Bajra no Rotlo with white butter, garlic chutney, ringna no olo, and hot jaggery."},
        ]
    },
    {
        "name": "Ahmedabad", "country": "India", "region": "West & Rajasthan",
        "cost_index": 45.0, "popularity_score": 9.1, "latitude": 23.0225, "longitude": 72.5714,
        "tags": ["unesco_city", "gandhi_ashram", "stepwells", "food_street", "textiles"],
        "vibe_tags": ["historic", "culinary", "vibrant"],
        "climate_type": "semi-arid", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 86.0, "budget_tier": "budget", "rent_index": 22.0, "restaurant_price_index": 30.0,
        "description": "India's first UNESCO World Heritage City, Ahmedabad blends sacred pols, monumental stepwells like Adalaj, Gandhi's Sabarmati Ashram, and legendary street food.",
        "image_url": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=800",
        "activities": [
            {"name": "Sabarmati Ashram & Riverfront Promenade Walk", "category": "history", "estimated_cost": 0.0, "duration_hours": 2.5, "tags": ["gandhi", "peace", "riverfront"], "vibe": "peaceful", "best_for": ["solo", "family", "couple"], "description": "Visit Mahatma Gandhi's headquarters for the Indian freedom struggle and Salt March."},
            {"name": "Manek Chowk Night Food Market Street Feast", "category": "food", "estimated_cost": 250.0, "duration_hours": 2.0, "tags": ["street_food", "ghotala_dosa", "kulfi"], "vibe": "electric", "best_for": ["foodie", "group"], "description": "Jewelry market by day turning at midnight into India's most famous street food hub."},
            {"name": "Adalaj Stepwell (Vav) 5-Story Intricate Architecture", "category": "sightseeing", "estimated_cost": 50.0, "duration_hours": 2.0, "tags": ["stepwell", "architecture", "solanki"], "vibe": "marvelous", "best_for": ["solo", "couple", "family"], "description": "15th-century subterranean masterpiece with carved sandstone columns and cooled air corridors."},
            {"name": "Old City Pol Heritage Walk & Sidi Saiyyed Jali", "category": "history", "estimated_cost": 100.0, "duration_hours": 2.0, "tags": ["unesco", "jali", "pol"], "vibe": "cultural", "best_for": ["solo", "couple"], "description": "World-famous 'Tree of Life' marble filigree screen and wooden pol houses."},
        ]
    },
    {
        "name": "Statue of Unity (Kevadia)", "country": "India", "region": "West & Rajasthan",
        "cost_index": 55.0, "popularity_score": 9.4, "latitude": 21.8380, "longitude": 73.7191,
        "tags": ["tallest_statue", "narmada", "valley_of_flowers", "monument", "engineering"],
        "vibe_tags": ["monumental", "futuristic", "inspiring"],
        "climate_type": "tropical", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 90.0, "budget_tier": "mid-range", "rent_index": 25.0, "restaurant_price_index": 35.0,
        "description": "The world's tallest statue standing at an astounding 182 meters (597 ft) dedicated to Sardar Vallabhbhai Patel, set amidst the Narmada dam and Vindhyachal hills.",
        "image_url": "https://images.unsplash.com/photo-1584824486509-112e4181ff6b?w=800",
        "activities": [
            {"name": "153-Meter Viewing Gallery & Core Elevator Experience", "category": "sightseeing", "estimated_cost": 380.0, "duration_hours": 2.5, "tags": ["viewing_gallery", "tallest_statue", "narmada"], "vibe": "thrilling", "best_for": ["family", "couple", "solo"], "description": "High-speed elevator up to the chest level of the colossal statue with panoramic dam views."},
            {"name": "Laser Light & Sound Show on the 182-Meter Bronze Surface", "category": "sightseeing", "estimated_cost": 100.0, "duration_hours": 1.0, "tags": ["laser_show", "night", "illumination"], "vibe": "spectacular", "best_for": ["family", "couple", "group"], "description": "World-class 3D projection mapping narrating the unification of India."},
            {"name": "Jungle Safari & Valley of Flowers Electric Cart Tour", "category": "nature", "estimated_cost": 250.0, "duration_hours": 3.0, "tags": ["safari", "flowers", "eco_park"], "vibe": "refreshing", "best_for": ["family", "children"], "description": "Walk among 300+ exotic animal species and million-flower landscaped riverbanks."},
        ]
    },

    # -------------------------------------------------------------------------
    # 4. SOUTH INDIA & WESTERN GHATS
    # -------------------------------------------------------------------------
    {
        "name": "Munnar", "country": "India", "region": "South India & Western Ghats",
        "cost_index": 45.0, "popularity_score": 9.7, "latitude": 10.0889, "longitude": 77.0595,
        "tags": ["tea_gardens", "mist", "waterfalls", "trekking", "western_ghats"],
        "vibe_tags": ["emerald", "misty", "romantic"],
        "climate_type": "tropical-highland", "best_months": ["September", "October", "November", "December", "January", "February", "March", "April"],
        "safety_index": 92.0, "budget_tier": "budget", "rent_index": 20.0, "restaurant_price_index": 28.0,
        "description": "Kerala's tea paradise blanketed by manicured rolling emerald plantations, misty mountain peaks, cascading waterfalls, and endangered Nilgiri Tahr mountain goats.",
        "image_url": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800",
        "activities": [
            {"name": "Kolukkumalai Sunrise 4x4 Jeep Safari (World's Highest Tea Estate)", "category": "adventure", "estimated_cost": 2000.0, "duration_hours": 4.5, "tags": ["sunrise", "jeep_safari", "tea_estate"], "vibe": "breathtaking", "best_for": ["couple", "group", "solo"], "description": "Watch the golden sunrise break through clouds at 7,130 ft on the world's highest organic tea hills."},
            {"name": "Eravikulam National Park Nilgiri Tahr Trek", "category": "nature", "estimated_cost": 200.0, "duration_hours": 3.0, "tags": ["wildlife", "nilgiri_tahr", "anamudi"], "vibe": "peaceful", "best_for": ["family", "nature_lover"], "description": "Spot wild mountain goats roaming on hills carpeted by blue Neelakurinji blooms."},
            {"name": "Tea Museum & Artisan Processing Tasting", "category": "history", "estimated_cost": 150.0, "duration_hours": 2.0, "tags": ["tea_tasting", "factory", "colonial"], "vibe": "delightful", "best_for": ["family", "solo"], "description": "Learn the art of tea plucking, CTC/orthodox processing, and taste single-origin black tea."},
            {"name": "Kerala Sadhya Meal on Banana Leaf", "category": "food", "estimated_cost": 250.0, "duration_hours": 1.5, "tags": ["sadhya", "banana_leaf", "kerala_cuisine"], "vibe": "authentic", "best_for": ["foodie", "family"], "description": "Traditional 24-dish vegetarian feast served on fresh plantain leaves with Payasam."},
        ]
    },
    {
        "name": "Alleppey (Alappuzha)", "country": "India", "region": "South India & Western Ghats",
        "cost_index": 55.0, "popularity_score": 9.6, "latitude": 9.4981, "longitude": 76.3388,
        "tags": ["backwaters", "houseboat", "canals", "ayurveda", "paddy_fields"],
        "vibe_tags": ["peaceful", "romantic", "tranquil"],
        "climate_type": "tropical", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 90.0, "budget_tier": "mid-range", "rent_index": 22.0, "restaurant_price_index": 30.0,
        "description": "The Venice of the East, famed for peaceful overnight houseboat cruises along palm-fringed backwater canals, village canoe trails, and authentic Ayurvedic therapies.",
        "image_url": "https://images.unsplash.com/photo-1593693411515-c20261bcad6e?w=800",
        "activities": [
            {"name": "Private Houseboat (Kettuvallam) Overnight Cruise with Chef", "category": "nature", "estimated_cost": 6500.0, "duration_hours": 18.0, "tags": ["houseboat", "backwaters", "chef"], "vibe": "luxurious", "best_for": ["couple", "family", "group"], "description": "Glide through tranquil canals with private bedrooms and chef cooking fresh Karimeen fish."},
            {"name": "Narrow Village Canal Shikara & Kayaking Expedition", "category": "adventure", "estimated_cost": 800.0, "duration_hours": 3.0, "tags": ["kayaking", "shikara", "village_life"], "vibe": "peaceful", "best_for": ["solo", "couple"], "description": "Paddle deep into shallow village lagoons where large houseboats cannot enter."},
            {"name": "Ayurvedic Herbal Full Body Massage (Abhyanga)", "category": "wellness", "estimated_cost": 1500.0, "duration_hours": 1.5, "tags": ["ayurveda", "massage", "wellness"], "vibe": "rejuvenating", "best_for": ["couple", "solo"], "description": "Traditional warm medicated oil massage by certified Kerala Ayurvedic practitioners."},
        ]
    },
    {
        "name": "Hampi", "country": "India", "region": "South India & Western Ghats",
        "cost_index": 38.0, "popularity_score": 9.5, "latitude": 15.3350, "longitude": 76.4600,
        "tags": ["unesco_ruins", "boulders", "temples", "vijayanagara", "biking"],
        "vibe_tags": ["ancient", "bouldering", "magical"],
        "climate_type": "semi-arid", "best_months": ["October", "November", "December", "January", "February"],
        "safety_index": 86.0, "budget_tier": "budget", "rent_index": 14.0, "restaurant_price_index": 22.0,
        "description": "The capital of the glorious Vijayanagara Empire, Hampi is an open-air wonderland of monumental stone chariot temples, musical pillars, and surreal granite boulder landscapes.",
        "image_url": "https://images.unsplash.com/photo-1600100397608-f010f44607b3?w=800",
        "activities": [
            {"name": "Vijaya Vittala Temple & Iconic Stone Chariot", "category": "history", "estimated_cost": 50.0, "duration_hours": 2.5, "tags": ["stone_chariot", "musical_pillars", "unesco"], "vibe": "marvelous", "best_for": ["solo", "family", "couple"], "description": "Photograph the iconic stone chariot and tap the ancient musical granite pillars."},
            {"name": "Matanga Hill Sunrise Trek & Boulder Climbing", "category": "adventure", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["sunrise", "hiking", "boulders"], "vibe": "breathtaking", "best_for": ["solo", "group"], "description": "Hike to Hampi's highest summit for a 360-degree panorama of ancient ruins bathed in dawn light."},
            {"name": "Tungabhadra River Coracle (Round Boat) Ride", "category": "nature", "estimated_cost": 400.0, "duration_hours": 1.0, "tags": ["coracle", "boat", "river"], "vibe": "fun", "best_for": ["group", "family", "couple"], "description": "Spin across turbulent river rapids in circular woven cane basket boats."},
            {"name": "Hippie Island (Anegundi) Moped Exploration", "category": "adventure", "estimated_cost": 350.0, "duration_hours": 4.0, "tags": ["moped", "paddy_fields", "cafes"], "vibe": "chill", "best_for": ["solo", "couple"], "description": "Rent mopeds to cruise through lush emerald paddy fields, Monkey Temple, and rooftop cafes."},
        ]
    },
    {
        "name": "Coorg (Kodagu)", "country": "India", "region": "South India & Western Ghats",
        "cost_index": 52.0, "popularity_score": 9.3, "latitude": 12.3375, "longitude": 75.8069,
        "tags": ["coffee_plantations", "waterfalls", "homestays", "kodava_culture", "mist"],
        "vibe_tags": ["green", "misty", "fragrant"],
        "climate_type": "tropical-highland", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 90.0, "budget_tier": "mid-range", "rent_index": 22.0, "restaurant_price_index": 32.0,
        "description": "Known as the Scotland of India, Coorg is famous for misty coffee & spice estates, roaring Abbey Falls, Tibetan settlement of Bylakuppe, and spicy Kodava Pandi Curry.",
        "image_url": "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?w=800",
        "activities": [
            {"name": "Coffee & Spice Plantation Guided Walking Tour", "category": "nature", "estimated_cost": 250.0, "duration_hours": 2.5, "tags": ["coffee", "spices", "plantation"], "vibe": "fragrant", "best_for": ["family", "couple", "solo"], "description": "Walk among Arabica coffee berries, vanilla pods, cardamom, and black pepper vines."},
            {"name": "Namdroling Golden Temple Tibetan Monastery", "category": "history", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["golden_temple", "tibetan", "monks"], "vibe": "serene", "best_for": ["family", "solo"], "description": "Marvel at 40-foot gilded gold Buddha statues and vibrant Tibetan murals in Bylakuppe."},
            {"name": "Abbey Falls Roaring Waterfall Trail", "category": "nature", "estimated_cost": 50.0, "duration_hours": 1.5, "tags": ["waterfall", "hanging_bridge", "rainforest"], "vibe": "refreshing", "best_for": ["family", "couple"], "description": "Hike through coffee trees to the hanging bridge facing torrential water cascades."},
            {"name": "Authentic Kodava Pandi Curry & Akki Roti Feast", "category": "food", "estimated_cost": 400.0, "duration_hours": 1.5, "tags": ["kodava", "pandi_curry", "akki_roti"], "vibe": "rich", "best_for": ["foodie", "group"], "description": "Signature Coorg pork or mushroom curry cooked with dark Kachampuli fruit vinegar."},
        ]
    },
    {
        "name": "Pondicherry", "country": "India", "region": "South India & Western Ghats",
        "cost_index": 50.0, "popularity_score": 9.4, "latitude": 11.9416, "longitude": 79.8083,
        "tags": ["french_quarter", "auroville", "beaches", "cafes", "bicycles"],
        "vibe_tags": ["french", "boho", "peaceful"],
        "climate_type": "tropical", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 88.0, "budget_tier": "mid-range", "rent_index": 22.0, "restaurant_price_index": 35.0,
        "description": "A picturesque coastal enclave with mustard-yellow French colonial villas, bougainvillea-lined streets, vibrant Franco-Tamil cuisine, and the spiritual community of Auroville.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800",
        "activities": [
            {"name": "White Town French Quarter Bicycle Heritage Tour", "category": "sightseeing", "estimated_cost": 200.0, "duration_hours": 2.5, "tags": ["french_colony", "bicycle", "white_town"], "vibe": "charming", "best_for": ["couple", "solo"], "description": "Cycle through colonial streets, vintage cafes, and pastel villas with wrought-iron balconies."},
            {"name": "Auroville Matrimandir Golden Dome Meditation", "category": "wellness", "estimated_cost": 0.0, "duration_hours": 3.5, "tags": ["auroville", "meditation", "peace"], "vibe": "spiritual", "best_for": ["solo", "couple"], "description": "Experience silence inside the giant golden globe considered the soul of universal township."},
            {"name": "Promenade Beachfront Sunset Stroll & Rock Beach", "category": "nature", "estimated_cost": 0.0, "duration_hours": 1.5, "tags": ["beach", "sunset", "promenade"], "vibe": "breezy", "best_for": ["family", "couple", "solo"], "description": "Car-free evening seaside walk past the French War Memorial and statue of Dupleix."},
            {"name": "French Crepes & Gourmet Croissant Cafe Hopping", "category": "food", "estimated_cost": 450.0, "duration_hours": 2.0, "tags": ["french_bakery", "crepes", "croissant"], "vibe": "delightful", "best_for": ["foodie", "couple"], "description": "Artisan sourdough, butter croissants, ratatouille crepes, and iced cold brew."},
        ]
    },

    # -------------------------------------------------------------------------
    # 5. EAST & NORTHEAST INDIA
    # -------------------------------------------------------------------------
    {
        "name": "Darjeeling", "country": "India", "region": "East & Northeast",
        "cost_index": 46.0, "popularity_score": 9.4, "latitude": 27.0410, "longitude": 88.2663,
        "tags": ["kanchenjunga", "tea", "toy_train", "himalayas", "monasteries"],
        "vibe_tags": ["colonial", "misty", "majestic"],
        "climate_type": "subtropical-highland", "best_months": ["March", "April", "May", "October", "November", "December"],
        "safety_index": 90.0, "budget_tier": "budget", "rent_index": 18.0, "restaurant_price_index": 28.0,
        "description": "Queen of the Hills, Darjeeling offers jaw-dropping views of Mount Kanchenjunga (world's 3rd highest peak), champagne tea gardens, and the heritage Toy Train.",
        "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800",
        "activities": [
            {"name": "Tiger Hill 4:00 AM Kanchenjunga Golden Sunrise", "category": "nature", "estimated_cost": 800.0, "duration_hours": 3.0, "tags": ["sunrise", "kanchenjunga", "tiger_hill"], "vibe": "breathtaking", "best_for": ["family", "couple", "solo"], "description": "Watch the golden sun illuminate the snow-clad peaks of Kanchenjunga and Mount Everest."},
            {"name": "Darjeeling Himalayan Railway Steam Engine Ride", "category": "sightseeing", "estimated_cost": 1000.0, "duration_hours": 2.0, "tags": ["steam_train", "unesco", "batasia_loop"], "vibe": "nostalgic", "best_for": ["family", "couple"], "description": "Ride the historic 1881 coal-fired steam train around the scenic Batasia Loop spiral."},
            {"name": "Momo, Thukpa & First-Flush Darjeeling Tea Tasting", "category": "food", "estimated_cost": 250.0, "duration_hours": 1.5, "tags": ["momos", "thukpa", "darjeeling_tea"], "vibe": "cozy", "best_for": ["foodie", "solo"], "description": "Steaming hot handmade pork/veg momos and rare muscatel first-flush tea at Glenary's."},
        ]
    },
    {
        "name": "Shillong", "country": "India", "region": "East & Northeast",
        "cost_index": 48.0, "popularity_score": 9.3, "latitude": 25.5788, "longitude": 91.8933,
        "tags": ["scotland_of_east", "waterfalls", "living_root_bridges", "rock_music", "caves"],
        "vibe_tags": ["green", "musical", "magical"],
        "climate_type": "subtropical-highland", "best_months": ["September", "October", "November", "December", "March", "April", "May"],
        "safety_index": 92.0, "budget_tier": "budget", "rent_index": 18.0, "restaurant_price_index": 28.0,
        "description": "The Scotland of the East and Rock Capital of India, Shillong is blessed with rolling pine meadows, cascading waterfalls, clean tribal villages, and double-decker living root bridges.",
        "image_url": "https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800",
        "activities": [
            {"name": "Cherrapunji & Double Decker Living Root Bridge Hike", "category": "adventure", "estimated_cost": 1500.0, "duration_hours": 6.0, "tags": ["root_bridge", "trekking", "rainforest"], "vibe": "epic", "best_for": ["group", "solo", "couple"], "description": "Trek 3,000 stone steps down to the 200-year-old bio-engineered rubber tree root bridge in Nongriat."},
            {"name": "Dawki Umngot River Crystal Clear Boat Ride", "category": "nature", "estimated_cost": 800.0, "duration_hours": 4.0, "tags": ["dawki", "glass_water", "boating"], "vibe": "surreal", "best_for": ["couple", "group", "family"], "description": "Boat on waters so clear the wooden boat appears suspended in mid-air above the riverbed."},
            {"name": "Elephant Falls & Laitlum Canyon Cloud Walk", "category": "nature", "estimated_cost": 100.0, "duration_hours": 3.0, "tags": ["canyon", "waterfall", "clouds"], "vibe": "refreshing", "best_for": ["family", "couple"], "description": "Stand on the edge of the world overlooking vast green valleys pierced by swirling mists."},
        ]
    },
    {
        "name": "Kolkata", "country": "India", "region": "East & Northeast",
        "cost_index": 45.0, "popularity_score": 9.3, "latitude": 22.5726, "longitude": 88.3639,
        "tags": ["city_of_joy", "howrah_bridge", "street_food", "art", "durga_puja"],
        "vibe_tags": ["intellectual", "vintage", "soulful"],
        "climate_type": "tropical", "best_months": ["October", "November", "December", "January", "February"],
        "safety_index": 82.0, "budget_tier": "budget", "rent_index": 20.0, "restaurant_price_index": 26.0,
        "description": "The City of Joy and cultural capital of India, known for colonial tramways, Howrah Bridge, grand Victoria Memorial, Nobel laureates, and unmatched sweets & street food.",
        "image_url": "https://images.unsplash.com/photo-1558431382-27e303142255?w=800",
        "activities": [
            {"name": "Victoria Memorial & Maidan Heritage Tram Ride", "category": "history", "estimated_cost": 100.0, "duration_hours": 3.0, "tags": ["victoria_memorial", "tram", "british_raj"], "vibe": "regal", "best_for": ["family", "couple", "solo"], "description": "Explore the white Makrana marble monument and ride Asia's oldest operating tram system."},
            {"name": "Kolkata Street Food Crawl (Kathi Rolls, Phuchka & Rosogolla)", "category": "food", "estimated_cost": 200.0, "duration_hours": 2.0, "tags": ["kathi_roll", "phuchka", "mishti_doi"], "vibe": "unbeatable", "best_for": ["foodie", "group"], "description": "Taste original Nizam's mutton kathi rolls, spiced water phuchkas, and warm Nolen Gur Sandesh."},
            {"name": "Howrah Bridge & Mullick Ghat Flower Market Sunrise", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 2.0, "tags": ["howrah_bridge", "flower_market", "hooghly"], "vibe": "vibrant", "best_for": ["solo", "photography"], "description": "Witness millions of marigold and lotus garlands traded at Asia's largest wholesale flower bazaar."},
        ]
    },

    # -------------------------------------------------------------------------
    # 6. CENTRAL & SPIRITUAL CIRCUITS
    # -------------------------------------------------------------------------
    {
        "name": "Varanasi", "country": "India", "region": "Central & Spiritual",
        "cost_index": 38.0, "popularity_score": 9.9, "latitude": 25.3176, "longitude": 82.9739,
        "tags": ["ghats", "ganga_aarti", "ancient", "spiritual", "silk"],
        "vibe_tags": ["mystical", "eternal", "profound"],
        "climate_type": "subtropical", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 80.0, "budget_tier": "budget", "rent_index": 16.0, "restaurant_price_index": 22.0,
        "description": "One of the world's oldest continuously inhabited cities, Varanasi is the spiritual heart of India, famous for sacred Ganga ghats, devotional morning boat rides, and eternal ceremonies.",
        "image_url": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800",
        "activities": [
            {"name": "Dawn Rowing Boat Cruise Across 84 Sacred Ghats", "category": "sightseeing", "estimated_cost": 400.0, "duration_hours": 2.0, "tags": ["boat_ride", "ganga", "ghats"], "vibe": "transcendent", "best_for": ["solo", "couple", "family"], "description": "Witness morning bath rituals and sunrise prayers along Assi, Dashashwamedh, and Manikarnika ghats."},
            {"name": "Dashashwamedh Ghat Grand Evening Ganga Aarti", "category": "history", "estimated_cost": 0.0, "duration_hours": 1.5, "tags": ["ganga_aarti", "fire_ritual", "devotional"], "vibe": "divine", "best_for": ["family", "solo", "group"], "description": "Witness high priests perform synchronized brass lamp rituals amidst conch shells and cymbals."},
            {"name": "Kashi Vishwanath Corridor & Ancient Alley Walk", "category": "history", "estimated_cost": 0.0, "duration_hours": 2.5, "tags": ["kashi_vishwanath", "temple", "jyotirlinga"], "vibe": "spiritual", "best_for": ["family", "solo"], "description": "Walk the grand new corridor to the golden-spired Jyotirlinga temple."},
            {"name": "Banarasi Kachori Jalebi, Malaiyo & Silk Weaving", "category": "food", "estimated_cost": 150.0, "duration_hours": 2.0, "tags": ["kachori", "malaiyo", "banarasi_paan"], "vibe": "sweet", "best_for": ["foodie", "group"], "description": "Taste winter saffron Malaiyo foam, hot hing kachoris, blue lassi, and famous Banarasi Paan."},
        ]
    },
    {
        "name": "Agra", "country": "India", "region": "Central & Spiritual",
        "cost_index": 45.0, "popularity_score": 9.8, "latitude": 27.1767, "longitude": 78.0081,
        "tags": ["taj_mahal", "mughal", "wonders_of_world", "fort", "petha"],
        "vibe_tags": ["monumental", "romantic", "historic"],
        "climate_type": "semi-arid", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 78.0, "budget_tier": "budget", "rent_index": 18.0, "restaurant_price_index": 30.0,
        "description": "Home to the world-famous Taj Mahal, a marble monument of eternal love and UNESCO World Wonder, along with the monumental red sandstone Agra Fort and Fatehpur Sikri.",
        "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800",
        "activities": [
            {"name": "Taj Mahal Sunrise Guided Monument Tour", "category": "sightseeing", "estimated_cost": 250.0, "duration_hours": 3.0, "tags": ["taj_mahal", "unesco", "seven_wonders"], "vibe": "unforgettable", "best_for": ["couple", "family", "solo"], "description": "Witness the white marble dome transition from soft pink to radiant pearl in morning sunlight."},
            {"name": "Agra Fort Royal Palaces & Yamuna Viewpoints", "category": "history", "estimated_cost": 100.0, "duration_hours": 2.5, "tags": ["agra_fort", "mughal", "palace"], "vibe": "regal", "best_for": ["family", "solo"], "description": "Explore Emperor Shah Jahan's marble prison and Diwan-i-Khas overlooking the Taj."},
            {"name": "Mehtab Bagh Moonlight View & Original Petha Tasting", "category": "food", "estimated_cost": 100.0, "duration_hours": 1.5, "tags": ["mehtab_bagh", "petha", "mughlai"], "vibe": "sweet", "best_for": ["foodie", "couple"], "description": "Sample Panchhi Petha (kesar, angoori, paan flavors) and view Taj from across the Yamuna."},
        ]
    },
    {
        "name": "Amritsar", "country": "India", "region": "Central & Spiritual",
        "cost_index": 42.0, "popularity_score": 9.6, "latitude": 31.6340, "longitude": 74.8723,
        "tags": ["golden_temple", "wagah_border", "langar", "punjabi_food", "history"],
        "vibe_tags": ["devotional", "patriotic", "culinary"],
        "climate_type": "subtropical", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 90.0, "budget_tier": "budget", "rent_index": 18.0, "restaurant_price_index": 26.0,
        "description": "The spiritual center of Sikhism, Amritsar inspires with the shimmering 24-karat Golden Temple, the world's largest community kitchen (Langar), and patriotic Wagah Border ceremony.",
        "image_url": "https://images.unsplash.com/photo-1595658658481-d53d3f999875?w=800",
        "activities": [
            {"name": "Harmandir Sahib (Golden Temple) & Guru ka Langar Experience", "category": "history", "estimated_cost": 0.0, "duration_hours": 3.5, "tags": ["golden_temple", "langar", "holy_sarovar"], "vibe": "divine", "best_for": ["family", "solo", "couple"], "description": "Bathe in the sacred Amrit Sarovar and volunteer or dine in the 100,000-meals/day free community kitchen."},
            {"name": "Attari-Wagah Border Beating Retreat Ceremony", "category": "sightseeing", "estimated_cost": 0.0, "duration_hours": 3.0, "tags": ["wagah_border", "patriotism", "marching"], "vibe": "electric", "best_for": ["family", "group", "solo"], "description": "Feel the roaring patriotic energy and high-kicking border drill between Indian BSF and Pakistan Rangers."},
            {"name": "Legendary Amritsari Kulcha, Chole & Lassi Trail", "category": "food", "estimated_cost": 180.0, "duration_hours": 2.0, "tags": ["amritsari_kulcha", "lassi", "chole"], "vibe": "legendary", "best_for": ["foodie", "group"], "description": "Flaky wood-fired butter kulchas with spicy chole, tangy imli chutney, and heavy cream lassi."},
            {"name": "Jallianwala Bagh Memorial & Partition Museum", "category": "history", "estimated_cost": 50.0, "duration_hours": 2.5, "tags": ["partition_museum", "freedom_struggle", "memorial"], "vibe": "poignant", "best_for": ["family", "solo"], "description": "Pay tribute to martyrs at the preserved bullet-marked memorial wall and world's first Partition museum."},
        ]
    },
    {
        "name": "Ayodhya", "country": "India", "region": "Central & Spiritual",
        "cost_index": 38.0, "popularity_score": 9.5, "latitude": 26.7922, "longitude": 82.1998,
        "tags": ["ram_mandir", "saryu_river", "ghats", "sacred", "heritage"],
        "vibe_tags": ["sacred", "ancient", "magnificent"],
        "climate_type": "subtropical", "best_months": ["October", "November", "December", "January", "February", "March"],
        "safety_index": 88.0, "budget_tier": "budget", "rent_index": 16.0, "restaurant_price_index": 22.0,
        "description": "The sacred birthplace of Lord Rama along the holy Saryu River, Ayodhya is one of India's most revered pilgrimage capitals featuring the grand new Ram Mandir.",
        "image_url": "https://images.unsplash.com/photo-1609342122563-a43ac8917a3a?w=800",
        "activities": [
            {"name": "Shree Ram Janmabhoomi Mandir Darshan", "category": "history", "estimated_cost": 0.0, "duration_hours": 3.0, "tags": ["ram_mandir", "darshan", "nagara_architecture"], "vibe": "devotional", "best_for": ["family", "solo"], "description": "Marvel at the monumental pink Bansi Paharpur stone temple constructed without iron/steel."},
            {"name": "Saryu River Ghats Evening Aarti & Boat Ride", "category": "nature", "estimated_cost": 250.0, "duration_hours": 1.5, "tags": ["saryu", "aarti", "boat"], "vibe": "serene", "best_for": ["family", "couple"], "description": "Sunset boat ride along Ram Ki Paidi illuminated by thousands of earthen lamps."},
            {"name": "Hanuman Garhi Hilltop Fortress Temple", "category": "history", "estimated_cost": 0.0, "duration_hours": 1.5, "tags": ["hanuman_garhi", "temple", "viewpoint"], "vibe": "spiritual", "best_for": ["family", "solo"], "description": "Climb 76 stairs to the 10th-century cave temple guarding the city of Ayodhya."},
        ]
    }
]

async def seed_all_india():
    async with AsyncSessionLocal() as session:
        print(f"[Seed India] Processing {len(INDIAN_DESTINATIONS)} comprehensive Indian destinations...")
        added_count = 0
        updated_count = 0

        for c in INDIAN_DESTINATIONS:
            res = await session.execute(select(City).where(City.name == c["name"]))
            existing_city = res.scalar_one_or_none()

            if existing_city:
                # Update metadata
                existing_city.region = c["region"]
                existing_city.cost_index = c["cost_index"]
                existing_city.popularity_score = c["popularity_score"]
                existing_city.latitude = c["latitude"]
                existing_city.longitude = c["longitude"]
                existing_city.image_url = c["image_url"]
                existing_city.tags = c.get("tags")
                existing_city.vibe_tags = c.get("vibe_tags")
                existing_city.climate_type = c.get("climate_type")
                existing_city.best_months = c.get("best_months")
                existing_city.safety_index = c.get("safety_index", 80.0)
                existing_city.budget_tier = c.get("budget_tier", "mid")
                existing_city.rent_index = c.get("rent_index", 30.0)
                existing_city.restaurant_price_index = c.get("restaurant_price_index", 30.0)
                existing_city.description = c["description"]
                session.add(existing_city)
                target_city = existing_city
                updated_count += 1
            else:
                new_city = City(
                    name=c["name"],
                    country="India",
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
                    rent_index=c.get("rent_index", 30.0),
                    restaurant_price_index=c.get("restaurant_price_index", 30.0),
                )
                session.add(new_city)
                await session.flush()
                target_city = new_city
                added_count += 1

            # Seed activities in INR
            for a in c.get("activities", []):
                act_res = await session.execute(
                    select(Activity).where(
                        Activity.city_id == target_city.id,
                        Activity.name == a["name"]
                    )
                )
                if not act_res.scalar_one_or_none():
                    act = Activity(
                        city_id=target_city.id,
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
        print(f"[Seed India] Completed! Added {added_count} new destinations, updated {updated_count} existing destinations with INR activities in Supabase.")

if __name__ == "__main__":
    asyncio.run(seed_all_india())
