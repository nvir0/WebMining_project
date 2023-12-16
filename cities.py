import os
import pandas as pd
from typing import Dict

import stamina
import pickle
import json

from geopy.geocoders import Bing, Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

class CitiesHandler:
    def __init__(self, api_keys: Dict):
        """api_keys = {"BING_API_KEY": "key"}"""
        self._cache_filepath = '_cache.pkl'
        self._cache = self._load_cache()
        self.__api_keys = api_keys

    def _load_cache(self):
        if os.path.exists(self._cache_filepath):
            with open(self._cache_filepath, 'rb') as cache_file:
                return pickle.load(cache_file)
        else:
            return {}

    def _save_cache(self):
        with open(self._cache_filepath, 'wb') as file:
            pickle.dump(self._cache, file)

    def dump_cache(self, file_format: str):
        if file_format == 'csv':
            pd.DataFrame(self._cache).to_csv('dump.csv')
        if file_format == 'json':
            with open('dump.json', 'w') as json_file:
                json.dump(self._cache, json_file, indent=2)

    def get_coordinates(self, query, service='nominatim'):
        if query in self._cache.keys():
            return self._cache.get(query)

        service = service.lower()

        if service not in ['bing', 'nominatim']:
            raise ValueError('Wrong service')
        if service == 'bing':
            service = Bing(self.__api_keys.get("BING_API_KEY"))
        if service == 'nominatim':
            service = Nominatim(user_agent="temp")
        geolocator = service

        try:
            for attempt in stamina.retry_context(on=(GeocoderTimedOut, GeocoderUnavailable)):
                with attempt:
                    location = geolocator.geocode(query)
        except:
            return (None, None)

        if location is None:
            return (None, None)

        coords = (location.latitude, location.longitude)
        self._cache[query] = coords
        self._save_cache()
        return coords

    def get_coordinates_dict(self, iterable, **kwargs):
        service = kwargs.get('service', None)
        coordinates_dict = {}
        for query in iterable:
            coords = self.get_coordinates(query, service)
            coordinates_dict[query] = coords
        return coordinates_dict

    def get_coordinates_df(self, iterable, **kwargs):
        service = kwargs.get('service', 'nominatim')
        df_data = {'city': [],
                   'lat': [],
                   'lon': []}

        for query in iterable:
            lat, lon = self.get_coordinates(query, service)

            df_data['city'].append(query)
            df_data['lat'].append(lat)
            df_data['lon'].append(lon)

        df = pd.DataFrame(df_data)

        return df


    @staticmethod
    def get_cities_wiki_1():
        url = 'https://en.wikipedia.org/wiki/List_of_cities_by_elevation'
        dfs = pd.read_html(url)
        cities = dfs[1]

        cards = {'Latitude': ('N', 'S'),
                 'Longitude': ('E', 'W')}
        for key, item in cards.items():
            for cardinal in item:
                mask = cities[key].str.startswith(cardinal)
                if item.index(cardinal) == 1:
                    const = - 1
                else:
                    const = 1
                cities.loc[mask, key[:3].lower()] = const * pd.to_numeric(cities.loc[mask, key].str[1:],
                                                                          errors='coerce')
        cities.rename(columns={
            'Country/Territory': 'country',
            'City Name/s': 'city',
            'Continental Region': 'continent'}, inplace=True)
        cities = cities.loc[:, ['city', 'lat', 'lon','continent', 'country']]
        return cities

    @staticmethod
    def list_eur_cities_over_300():
        url = 'https://en.wikipedia.org/wiki/List_of_cities_in_the_European_Union_by_population_within_city_limits'
        dfs = pd.read_html(url)
        cities = dfs[0]
        cities = cities.iloc[:, 1:3]
        cities.rename(columns={
            'City': 'city',
            'Member state': 'country'
            }, inplace=True)
        return cities
