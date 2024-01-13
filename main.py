import os
import urllib.parse

from dotenv import load_dotenv

import pandas as pd

import streamlit as st
import plotly.express as px
import numpy as np

from cities import CitiesHandler
from open_weather import OpenWeatherHandler
from open_trip_map import OpenTripMapHandler


def main():
    load_dotenv()

    # HANDLERS
    bing_api_key = os.getenv("BING_API_KEY")
    ow_api_key = os.getenv("OPENWEATHER_API_KEY")
    otm_api_key = os.getenv("OPENTRIPMAP_API_KEY")

    c_handler = CitiesHandler(api_keys={"BING_API_KEY": bing_api_key})
    otm_handler = OpenTripMapHandler(otm_api_key)
    ow_handler = OpenWeatherHandler(api_key=ow_api_key)

    # GET CITIES COORDS
    eur_cities = c_handler.list_eur_cities_over_300() # df with city
    cities_df = c_handler.get_coordinates_df(eur_cities['city'] + " Europe", service='bing')
    cities_df['city'] = cities_df['city'].str.replace(" Europe", "")
    # TEMPERATURE, AIR QUALITY
    cities_df['temperature'] = cities_df.apply(lambda x: ow_handler.get_temperature((x['lat'], x['lon'])), axis=1)
    cities_df['air_quality'] = cities_df.apply(lambda x: ow_handler.get_air_quality((x['lat'], x['lon']))[0], axis=1)


    # TEMPORARY
    # cities_df = pd.read_csv('temp2.csv').iloc[:,1:]  # TODO for demonstration purposes
    # END TEMPORARY

    # MAIN PAGE
    col1, col2 = st.columns([1, 2])
    selection = col1.radio("Select Temperature", ("Hot", "Cold"))
    num_cities = col2.slider("Select Number of Cities", min_value=1, max_value=len(cities_df), value=5)
    # selected_cities['air_quality'] = selected_cities.apply(lambda x: ow_handler.get_air_quality((x['lat'], x['lon']))[0], axis=1)
    # selected_cities['temperature'] = selected_cities.apply(lambda x: ow_handler.get_temperature((x['lat'], x['lon'])), axis=1)

    if selection == "Hot":
        title = f"Top {num_cities} Hottest Cities"
        selected_cities = cities_df.sort_values(by="temperature", ascending=False)[:num_cities]
    else:
        title = f"Top {num_cities} Coldest Cities"
        selected_cities = cities_df.sort_values(by="temperature")[:num_cities]

    st.title(title)

    # MAP
    fig = px.scatter_mapbox(
        selected_cities,
        lat="lat",
        lon="lon",
        size= 6 - selected_cities['air_quality'],
        hover_name="city",
        hover_data=["temperature", "air_quality"],
        color="temperature",
        color_continuous_scale=px.colors.cyclical.IceFire,
        zoom=1
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)


    # TABLE WITH DETAILS
    st.subheader("City Weather Details")
    st.table(selected_cities[["city", "temperature", "air_quality"]].reset_index(drop=True))

    selected_city = st.sidebar.selectbox('Select City', selected_cities['city'])
    st.sidebar.divider()

    coords = tuple(selected_cities[selected_cities['city'] == selected_city][['lat', 'lon']].iloc[0])

    # ATTRACTIONS
    st.sidebar.subheader(f"Attractions in {selected_city}")
    attraction_kinds = ['museums', 'other', 'natural', 'sport', 'shops', 'theaters_and_entertainments', 'archeology', 'historic', 'religion']
    selected_attractions_list = st.sidebar.multiselect("Select attractions", attraction_kinds)
    attr_kinds = ",".join(selected_attractions_list) if selected_attractions_list else None

    attr_opt_params = {"radius": 5000, "kinds": "interesting_places"}
    if attr_kinds is not None:
        attr_opt_params['kinds'] = attr_kinds
    attractions_for_city = pd.DataFrame(otm_handler.get_points_of_interest(coords, optional_params=attr_opt_params))
    # attractions_for_city['lat'],  attractions_for_city['lon'] = zip(*attractions_for_city['coords'])
    if st.sidebar.button('Refresh attractions'):
        if len(attractions_for_city) != 0:
            attr_max_len = len(attractions_for_city) if len(attractions_for_city) < 5 else 5
            attr_sampled = attractions_for_city.sample(attr_max_len)
            for i, row in attr_sampled.iterrows():
                name = row['name']
                url = "https://www.google.com/search"
                url = url + "?" + urllib.parse.urlencode({"q": name})
                txt = f"[{name}]({url})"
                st.sidebar.markdown(txt)
    st.sidebar.divider()

    # ACCOMODATION
    st.sidebar.subheader(f"Accomodation in {selected_city}")
    accomodation_kinds = ['other_hotels', 'campsites', 'hostels', 'guest_houses', 'motels']
    selected_accomodation_list = st.sidebar.multiselect("Select accomodation", accomodation_kinds)
    accm_kinds = ",".join(selected_accomodation_list) if selected_attractions_list else None

    accm_opt_params = {"radius": 5000, "kinds": "accomodations"}
    if accm_kinds is not None:
        accm_opt_params['kinds'] = accm_kinds
    accomodation_for_city = pd.DataFrame(otm_handler.get_points_of_interest(coords, optional_params=accm_opt_params))
    # accomodation_for_city['lat'],  accomodation_for_city['lon'] = zip(*attractions_for_city['coords'])

    if st.sidebar.button('Refresh accomodation'):
        if len(accomodation_for_city) != 0:
            accm_max_len = len(accomodation_for_city) if len(accomodation_for_city) < 5 else 5
            accm_sampled = accomodation_for_city.sample(accm_max_len)
            for i, row in accm_sampled.iterrows():
                name = row['name']
                url = "https://www.google.com/search"
                url = url + "?" + urllib.parse.urlencode({"q": name})
                txt = f"[{name}]({url})"
                st.sidebar.markdown(txt)
    st.sidebar.divider()



if __name__ == "__main__":
    main()
