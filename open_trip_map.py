import requests
from typing import Tuple, Dict, Any
import urllib.parse
import stamina
from collections import OrderedDict

class OpenTripMapHandler:
    def __init__(self, api_key):
        self.__api_key = api_key

    def get_points_of_interest(self, coordinates, optional_params: Dict[str, Any] = None):
        """API reference: https://dev.opentripmap.org/docs#/Objects%20list/getListOfPlacesByRadius"""
        lat, lon = coordinates

        params = {
            "lat": lat,
            "lon": lon,
            "apikey": self.__api_key,
            "radius": 2000,
            "limit": 25
        }

        if optional_params is not None:
            params.update(optional_params)

        base_url = "https://api.opentripmap.com/0.1/en/places/radius"
        url = base_url + "?" + urllib.parse.urlencode(params)

        try:
            for attempt in stamina.retry_context(on=requests.exceptions.Timeout):
                with attempt:
                    response = requests.get(url)
                    response.raise_for_status()
        except requests.exceptions.RequestException as e:
            response_text = getattr(e.response, 'text', "")
            error_message = f"{str(e)}\nResponse: {response_text}".replace(self.__api_key, "***")
            print(error_message)
            return [{"name": None, "coords": None, "kinds": None}]

        data = response.json()
        pois = data['features']
        filtered_data = [
            OrderedDict([
                ('name', entry['properties']['name']),
                ('coords', tuple(entry['geometry']['coordinates'])),
                ('kinds', entry['properties']['kinds'])
            ])
            for entry in pois
            if entry['properties']['name'] != ""
        ]
        return filtered_data


def main():
    api_key = "API_KEY"
    otm = OpenTripMapHandler(api_key)
    coords = (50.049683, 19.944544)
    xd = otm.get_points_of_interest(coords, {"kinds": "museums", "radius": 10000})

if __name__ == "__main__":
    main()
