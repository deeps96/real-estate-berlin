from typing import List, Optional, Dict

from googlemaps import Client
from googlemaps.exceptions import Timeout, ApiError, _OverQueryLimit

from config import google_maps_api_key
from travel_time import TravelTime

NETLIGHT = {
    'lat': 52.502756932671005,
    'lng': 13.40785791342653
}


class GMaps:

    def __init__(self):
        self.gmaps = Client(key=google_maps_api_key, retry_over_query_limit=False)

    def _fetch_lat_lng(self, address: str) -> Dict[str, float]:
        response = self.gmaps.geocode(address=address)
        return response[0]['geometry']['location']

    def _fetch_closest_edeka(self, address: str) -> Dict[str, str]:
        lat_lng = self._fetch_lat_lng(address)
        response = self.gmaps.places_nearby(
            keyword='Edeka',
            location=lat_lng,
            rank_by='distance',
            type='supermarket'
        )
        result = response['results'][0]
        return {
            'name': result['name'],
            'address': result['vicinity']
        }

    def fetch_travel_times(self, address: str) -> Optional[List[TravelTime]]:
        closest_edeka = self._fetch_closest_edeka(address)
        try:
            response = self.gmaps.distance_matrix(
                origins=address,
                destinations=[NETLIGHT, closest_edeka['address']],
                mode='bicycling'
            )
            return [
                TravelTime(target=name, bike=element['duration']['text'])
                for element, name in zip(response['rows'][0]['elements'], ['Netlight', closest_edeka['name']])
            ]
        except (ApiError, Timeout, _OverQueryLimit) as e:
            print(e)
            return None
