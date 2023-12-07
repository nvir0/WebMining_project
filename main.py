from cities_data import CitiesHandler

c_handler = CitiesHandler()

cities_from_wiki_1 = c_handler.get_cities_elevation() # df with city, country, lat, lon
cities_from_wiki_2 = c_handler.list_eur_cities_over_300() # df with city

# xd = c_handler.get_coordinates_dict(cities_from_wiki_2['city'])
xd = c_handler.get_coordinates_df(cities_from_wiki_2['city'])
...