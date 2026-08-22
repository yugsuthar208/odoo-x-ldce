import math
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transit import TransitLeg, TransitOption
from app.models.trip import Trip

INDIAN_ORIGIN_COORDINATES: Dict[str, Dict[str, float]] = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Surat": {"lat": 21.1702, "lon": 72.8311},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Indore": {"lat": 22.7196, "lon": 75.8577},
    "Kochi": {"lat": 9.9312, "lon": 76.2673},
    "Goa": {"lat": 15.2993, "lon": 74.1240},
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


class TransitService:

    @classmethod
    def generate_options_for_distance(
        cls, road_distance_km: float, num_travelers: int, leg_id: str
    ) -> List[TransitOption]:
        """Generates DB TransitOption models for a specific distance."""
        options = []
        num_travelers = max(1, num_travelers)

        # 1. Trains
        if road_distance_km > 0:
            train_duration_hrs = round(max(2.0, road_distance_km / 65.0), 1)
            sleeper_fare = max(180, round(120 + road_distance_km * 0.45))
            ac3_fare = max(550, round(350 + road_distance_km * 1.15))
            ac2_fare = max(950, round(600 + road_distance_km * 1.85))

            options.append(TransitOption(
                transit_leg_id=leg_id, mode="train", provider="Indian Railways (SL)",
                duration_hours=train_duration_hrs, total_estimated_cost=sleeper_fare * num_travelers, cost_per_person=sleeper_fare
            ))
            options.append(TransitOption(
                transit_leg_id=leg_id, mode="train", provider="Indian Railways (3A)",
                duration_hours=train_duration_hrs, total_estimated_cost=ac3_fare * num_travelers, cost_per_person=ac3_fare
            ))
            options.append(TransitOption(
                transit_leg_id=leg_id, mode="train", provider="Vande Bharat (CC)",
                duration_hours=train_duration_hrs, total_estimated_cost=ac2_fare * num_travelers, cost_per_person=ac2_fare
            ))

        # 2. Flights
        if road_distance_km >= 400:
            flight_duration_hrs = round(1.2 + (road_distance_km / 800.0), 1)
            flight_fare = max(2800, round(2200 + (road_distance_km * 3.8)))
            options.append(TransitOption(
                transit_leg_id=leg_id, mode="flight", provider="Domestic Airline",
                duration_hours=flight_duration_hrs, total_estimated_cost=flight_fare * num_travelers, cost_per_person=flight_fare
            ))

        # 3. Buses
        if road_distance_km <= 1200:
            bus_duration_hrs = round(max(2.0, road_distance_km / 50.0), 1)
            bus_fare = max(350, round(200 + road_distance_km * 1.35))
            options.append(TransitOption(
                transit_leg_id=leg_id, mode="bus", provider="Volvo AC Sleeper",
                duration_hours=bus_duration_hrs, total_estimated_cost=bus_fare * num_travelers, cost_per_person=bus_fare
            ))

        # 4. Cab
        if road_distance_km <= 800:
            cab_duration_hrs = round(max(1.5, road_distance_km / 55.0), 1)
            cab_rate_per_km = 14.0 if num_travelers <= 4 else 18.0
            toll_estimate = round(road_distance_km * 1.5)
            total_cab_fare = round((road_distance_km * cab_rate_per_km) + toll_estimate)
            per_person_cab = round(total_cab_fare / num_travelers)
            
            options.append(TransitOption(
                transit_leg_id=leg_id, mode="cab", provider="Private Outstation Cab",
                duration_hours=cab_duration_hrs, total_estimated_cost=total_cab_fare, cost_per_person=per_person_cab
            ))

        return options

    @classmethod
    async def rebuild_transit_legs(cls, db: AsyncSession, trip: Trip) -> None:
        """
        Rebuilds transit legs for a trip based on its ordered stops.
        Preserves selected choices if the from/to stops match an existing leg.
        """
        num_travelers = max(1, int(getattr(trip, "num_travelers", 1) or 1))
        
        # Query fresh stops directly from DB to avoid session relationship caching issues
        from app.models.stop import TripStop
        from sqlalchemy.orm import selectinload
        
        stops_res = await db.execute(
            select(TripStop)
            .options(selectinload(TripStop.city))
            .where(TripStop.trip_id == trip.id)
            .order_by(TripStop.stop_order.asc())
        )
        ordered_stops = list(stops_res.scalars().all())
        
        # Query existing legs directly
        legs_res = await db.execute(
            select(TransitLeg)
            .options(selectinload(TransitLeg.options))
            .where(TransitLeg.trip_id == trip.id)
        )
        existing_legs_list = list(legs_res.scalars().all())
        
        if not ordered_stops:
            # If no stops, delete all legs
            for leg in existing_legs_list:
                await db.delete(leg)
            await db.flush()
            return
            
        # 1. Gather intended legs: [(from_stop_id, to_stop_id), ...]
        # Note: from_stop_id is None for Origin -> First Stop
        intended_pairs = []
        intended_pairs.append((None, ordered_stops[0].id))
        
        for i in range(len(ordered_stops) - 1):
            intended_pairs.append((ordered_stops[i].id, ordered_stops[i+1].id))
            
        # 2. Compare with existing legs
        existing_legs = { (leg.from_stop_id, leg.to_stop_id): leg for leg in existing_legs_list }
        
        # Remove stale legs
        for pair, leg in list(existing_legs.items()):
            if pair not in intended_pairs:
                await db.delete(leg)
                del existing_legs[pair]
        await db.flush()
                
        # Temporarily offset sequences of remaining existing legs to avoid unique constraint collisions
        for temp_idx, leg in enumerate(existing_legs.values()):
            leg.sequence = -1000 - temp_idx
            db.add(leg)
        await db.flush()

        # Generate missing legs and update sequence
        for seq, (from_id, to_id) in enumerate(intended_pairs):
            if (from_id, to_id) in existing_legs:
                leg = existing_legs[(from_id, to_id)]
                leg.sequence = seq
                db.add(leg)
            else:
                # Need to calculate distance
                orig_lat, orig_lon = 0.0, 0.0
                if from_id is None:
                    orig_clean = (trip.origin_city or "Mumbai").strip().title()
                    orig_coords = INDIAN_ORIGIN_COORDINATES.get(orig_clean, {"lat": 19.0760, "lon": 72.8777})
                    orig_lat, orig_lon = orig_coords["lat"], orig_coords["lon"]
                else:
                    from_stop = next((s for s in ordered_stops if s.id == from_id), None)
                    if from_stop and from_stop.city:
                        orig_lat, orig_lon = from_stop.city.latitude or 0.0, from_stop.city.longitude or 0.0
                        
                to_stop = next((s for s in ordered_stops if s.id == to_id), None)
                dest_lat, dest_lon = 0.0, 0.0
                if to_stop and to_stop.city:
                    dest_lat, dest_lon = to_stop.city.latitude or 0.0, to_stop.city.longitude or 0.0
                    
                dist = haversine_km(orig_lat, orig_lon, dest_lat, dest_lon)
                road_dist = round(max(30.0, dist * 1.25), 1)
                
                new_leg = TransitLeg(
                    trip_id=trip.id,
                    from_stop_id=from_id,
                    to_stop_id=to_id,
                    sequence=seq
                )
                db.add(new_leg)
                await db.flush() # get new_leg.id
                
                options = cls.generate_options_for_distance(road_dist, num_travelers, new_leg.id)
                for opt in options:
                    db.add(opt)
        
        await db.flush()

    @classmethod
    def calculate_transit_options(
        cls, origin: str, dest_name: str, dest_lat: float, dest_lon: float, num_travelers: int = 1
    ) -> Dict[str, Any]:
        """Legacy dynamic calculation method preserved for backwards compatibility."""
        orig_clean = origin.strip().title()
        orig_coords = INDIAN_ORIGIN_COORDINATES.get(orig_clean, {"lat": 19.0760, "lon": 72.8777})
        dist = haversine_km(orig_coords["lat"], orig_coords["lon"], dest_lat, dest_lon)
        road_dist = round(max(30.0, dist * 1.25), 1)
        
        options_db = cls.generate_options_for_distance(road_dist, num_travelers, "fake_id")
        
        # Transform back to the old format for any old frontend consumers
        out_options = []
        for opt in options_db:
            out_options.append({
                "mode": opt.mode,
                "provider": opt.provider,
                "classes": [{
                    "name": opt.provider,
                    "fare_per_person": opt.cost_per_person,
                    "total_group_fare": opt.total_estimated_cost
                }],
                "duration_hours": opt.duration_hours,
                "distance_km": road_dist
            })
            
        return {
            "origin": origin,
            "destination": dest_name,
            "distance_km": road_dist,
            "num_travelers": num_travelers,
            "transit_options": out_options
        }
