import stamina
import pandas as pd
import requests
from typing import Tuple


class OpenWeatherHandler:
    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key

    def get_temperature(self, coordinates: Tuple[float, float]) -> float:
        lat, lon = coordinates
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={self.__api_key}"
        try:
            for attempt in stamina.retry_context(on=requests.exceptions.Timeout):
                with attempt:
                    response = requests.get(url)
                    response.raise_for_status()
        except requests.exceptions.RequestException as e:
            response_text = getattr(e.response, 'text', "")
            error_message = f"{str(e)}\nResponse: {response_text}".replace(self.__api_key, "***")
            print(error_message)
            return float('NaN')

        data = response.json()
        temperature = data['main']['temp']
        return temperature


    def get_air_quality(self, coordinates: Tuple[float, float], map_values=False) -> Tuple[str | int | float, pd.Series]:
        lat, lon = coordinates
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.__api_key}"

        try:
            for attempt in stamina.retry_context(on=requests.exceptions.Timeout):
                with attempt:
                    response = requests.get(url)
                    response.raise_for_status()
        except requests.exceptions.RequestException as e:
            response_text = getattr(e.response, 'text', "")
            error_message = f"{str(e)}\nResponse: {response_text}".replace(self.__api_key, "***")
            print(error_message)
            return float('NaN'), pd.Series()

        data = response.json()
        components = pd.Series(data['list'][0]['components'])
        air_quality = data['list'][0]['main']['aqi']

        if map_values:
            aq_mapping = {
                1: "Good",
                2: "Fair",
                3: "Moderate",
                4: "Poor",
                5: "Very poor"
            }
            air_quality = aq_mapping[air_quality]

        return air_quality, components