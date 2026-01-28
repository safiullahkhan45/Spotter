"""
Routing service using OSRM (Open Source Routing Machine)
Free routing API - no API key required
"""

import requests
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RoutingService:
    """Handle routing calculations using OSRM"""

    OSRM_API_BASE = "http://router.project-osrm.org"
    GEOCODING_API = "https://nominatim.openstreetmap.org"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FMCSA-ELD-App/1.0'
        })

    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Convert location name to coordinates

        Args:
            location: Location name (e.g., "Richmond, VA")

        Returns:
            (latitude, longitude) or None if not found
        """
        try:
            url = f"{self.GEOCODING_API}/search"
            params = {
                'q': location,
                'format': 'json',
                'limit': 1
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data and len(data) > 0:
                result = data[0]
                return (float(result['lat']), float(result['lon']))

            return None

        except Exception as e:
            logger.error(f"Geocoding error for '{location}': {e}")
            return None

    def calculate_route(
        self,
        waypoints: List[Tuple[float, float]]
    ) -> Optional[Dict]:
        """
        Calculate route through multiple waypoints

        Args:
            waypoints: List of (lat, lon) tuples

        Returns:
            Route data including distance, duration, and geometry
        """
        try:
            # Format coordinates for OSRM: lon,lat (reversed from geocoding)
            coords = ";".join([f"{lon},{lat}" for lat, lon in waypoints])

            url = f"{self.OSRM_API_BASE}/route/v1/driving/{coords}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'true'
            }

            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            if data['code'] == 'Ok' and data.get('routes'):
                route = data['routes'][0]

                # Convert meters to miles, seconds to hours
                distance_miles = route['distance'] * 0.000621371
                duration_hours = route['duration'] / 3600

                return {
                    'distance_miles': distance_miles,
                    'duration_hours': duration_hours,
                    'geometry': route['geometry'],
                    'waypoints': waypoints,
                    'legs': route.get('legs', [])
                }

            return None

        except Exception as e:
            logger.error(f"Routing error: {e}")
            return None

    def get_route_for_trip(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str
    ) -> Optional[Dict]:
        """
        Calculate full route for a trip

        Args:
            current_location: Starting location
            pickup_location: Pickup location
            dropoff_location: Dropoff location

        Returns:
            Complete route data with distance and waypoints
        """
        # Geocode all locations
        current_coords = self.geocode_location(current_location)
        pickup_coords = self.geocode_location(pickup_location)
        dropoff_coords = self.geocode_location(dropoff_location)

        if not all([current_coords, pickup_coords, dropoff_coords]):
            # Fallback to estimated distances if geocoding fails
            logger.warning("Geocoding failed, using estimated distances")
            return self._estimate_route(current_location, pickup_location, dropoff_location)

        # Calculate route through all three points
        waypoints = [current_coords, pickup_coords, dropoff_coords]
        route = self.calculate_route(waypoints)

        if route:
            route['locations'] = {
                'current': {
                    'name': current_location,
                    'coordinates': current_coords
                },
                'pickup': {
                    'name': pickup_location,
                    'coordinates': pickup_coords
                },
                'dropoff': {
                    'name': dropoff_location,
                    'coordinates': dropoff_coords
                }
            }

        return route

    def _estimate_route(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str
    ) -> Dict:
        """
        Fallback: Estimate route when geocoding fails
        Uses approximate distances between major cities
        """
        # Simple estimation: ~300-500 miles for typical interstate haul
        estimated_distance = 400

        return {
            'distance_miles': estimated_distance,
            'duration_hours': estimated_distance / 60,  # 60 mph average
            'geometry': None,
            'waypoints': [],
            'locations': {
                'current': {'name': current_location, 'coordinates': None},
                'pickup': {'name': pickup_location, 'coordinates': None},
                'dropoff': {'name': dropoff_location, 'coordinates': None}
            },
            'estimated': True
        }
