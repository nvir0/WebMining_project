import os
from dotenv import load_dotenv
from cities import CitiesHandler
from open_weather import OpenWeatherHandler
from open_trip_map import OpenTripMapHandler


def main():
    load_dotenv()

    bing_api_key = os.getenv("BING_API_KEY")
    ow_api_key = os.getenv("OPENWEATHER_API_KEY")
    otm_api_key = os.getenv("OPENTRIPMAP_API_KEY")

    c_handler = CitiesHandler(api_keys={"BING_API_KEY": bing_api_key})
    # cities_from_wiki_1 = c_handler.get_cities_wiki_1() # df with city, country, lat, lon
    # cities_from_wiki_2 = c_handler.list_eur_cities_over_300() # df with city
    target = c_handler.get_coordinates("Kraków")

    ow_handler = OpenWeatherHandler(api_key=ow_api_key)
    air_qulity, aq_details = ow_handler.get_air_quality(target)

    otm_handler = OpenTripMapHandler(api_key=otm_api_key)
    hotels = otm_handler.get_points_of_interest(target, {"kinds": "accomodations", "radius": 10000})
    ...


if __name__ == "__main__":
    main()
