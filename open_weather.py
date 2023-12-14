import stamina
import pandas as pd
import requests
from typing import Tuple
import re


class OpenWeatherHandler:
    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key

    def get_air_quality(self, coordinates: Tuple[float, float]) -> Tuple[str, pd.Series]:
        lat, lon = coordinates
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.__api_key}"

        try:
            for attempt in stamina.retry_context(on=requests.exceptions.Timeout):
                with attempt:
                    response = requests.get(url)
                    response.raise_for_status()
        except requests.exceptions.Timeout:
            return "Failed to get air quality. Request timed out and reached its retries limit.", pd.Series()
        except requests.exceptions.RequestException as e:
            response_text = e.response.text if e.response is not None else ""
            error_message = str(e)
            # url_pattern = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
            api_key_pattern = re.compile(r'&appid=([^&]+)$')
            error_message = api_key_pattern.sub('&appid=***', error_message)
            error_message += f"\nResponse: {response_text}"
            return f"Failed to get air quality. Request error {error_message}", pd.Series()

        aq_mapping = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very poor"
        }
        data = response.json()
        components = pd.Series(data['list'][0]['components'])
        air_quality = aq_mapping[data['list'][0]['main']['aqi']]

        return air_quality, components
