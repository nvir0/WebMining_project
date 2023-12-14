import os
from dotenv import load_dotenv
from cities import CitiesHandler
from open_weather import OpenWeatherHandler


def main():
    load_dotenv()

    bing_api_key = os.getenv("BING_API_KEY")
    ow_api_key = os.getenv("OPENWEATHER_API_KEY")

    c_handler = CitiesHandler(api_keys={"BING_API_KEY": bing_api_key})
    # cities_from_wiki_1 = c_handler.get_cities_elevation() # df with city, country, lat, lon
    # cities_from_wiki_2 = c_handler.list_eur_cities_over_300() # df with city

    ow_handler = OpenWeatherHandler(api_key=ow_api_key)



if __name__ == "__main__":
    main()
