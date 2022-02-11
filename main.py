"""Map generator"""

import argparse
import math
import folium
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def parcing():
    """
    Parces the arguments.
    """
    parcer = argparse.ArgumentParser()
    parcer.add_argument('year')
    parcer.add_argument('latitude')
    parcer.add_argument('longitude')
    parcer.add_argument('filepath')
    return parcer.parse_args()


def read_data_from_file(filename, year):
    """
    Reads a dataset and parces it, then returns the films of a given year.
    >>> read_data_from_file('locator1.list', '2012')[:3]
    [['"2012 Stanley Cup Finals" (2012) {Game 1 (#1.1)}', 'Prudential Center, \
Newark, New Jersey, USA'], \
['"2012 Stanley Cup Finals" (2012) {Game 3 (#1.3)}', 'Staples Center - 1111 S. \
Figueroa Street, Downtown, \
Los Angeles, California, USA'], ['"2012 UEFA European Football Championship" (2012)', \
'National Stadium, Warsaw, Mazowieckie, Poland']]
    """
    file = open(filename, mode='r', encoding='utf-8', errors='ignore')
    data = file.readline()
    while not data.startswith("=============="):
        data = file.readline()
    lst = []
    while not data.startswith('---------'):
        data = file.readline().strip()
        if '('+year+')' in data:
            lst.append(data)
    for i in range(len(lst)):
        lst[i] = lst[i].split('\t')
        while '' in lst[i]:
            lst[i].remove('')
        if lst[i][-1].startswith('('):
            lst[i].pop(-1)
    # print('done')
    return lst


def convert_data_to_coordinates(data_list):
    """
    Finds films' filming coordinates using geopy and adds them to the list.
    If location was found for the 1st time caches it.
    For every next time that location used cache is used to hasten the process.
    If location isn't found with original address, then it gets shorter to become less precise.
    >>> convert_data_to_coordinates([['"Noble Soul" (2015)', 'Krasne, Lviv oblast, Ukraine']])
    [['"Noble Soul" (2015)', 'Krasne, Lviv oblast, Ukraine', (49.9125099, 24.608186)]]
    """
    storage = {}
    for i in range(len(data_list)):
        geolocator = Nominatim(user_agent='map')
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)
        location = geocode(data_list[i][-1], timeout=None)
        if data_list[i][-1] not in storage:
            try:
                storage[data_list[i][-1]
                        ] = (location.latitude, location.longitude)
                data_list[i].append(
                    (location.latitude, location.longitude))
            except AttributeError:
                try:
                    data_list[i][-1] = ', '.join(data_list[i]
                                                 [-1].split(', ')[1:])
                    location = geolocator.geocode(
                        data_list[i][-1], timeout=None)
                    storage[data_list[i][-1]
                            ] = (location.latitude, location.longitude)
                    data_list[i].append(
                        (location.latitude, location.longitude))
                except AttributeError:
                    pass
        else:
            data_list[i].append(storage[data_list[i][-1]])
        if len(data_list[i]) == 2:
            data_list[i] = ''
    while '' in data_list:
        data_list.remove('')
    # print('done')
    return data_list


def get_closest_places(coordinate, list_of_coordinates):
    """
    Finds distance between 2 points on a sphere using haversine formula.
    Returns 10 closest places from dataset.
    >>> get_closest_places((49.8397, 24.0297), [['"Noble Soul" (2015)', 'Krasne,\
 Lviv oblast, Ukraine', (49.9125099, 24.608186)]])
    [['"Noble Soul" (2015)', 'Krasne, Lviv oblast, Ukraine', (49.9125099, 24.608186),\
 3432.9469932841685]]
    """
    for i in range(len(list_of_coordinates)):
        list_of_coordinates[i].append(2*6371*math.asin(math.sqrt((math.sin((
            float(coordinate[0])-list_of_coordinates[i][-1][0])/2))**2+math.cos(
                float(coordinate[0]))*math.cos(list_of_coordinates[i][-1][0])*(math.sin((
                    float(coordinate[1])-list_of_coordinates[i][-1][1])/2))**2)))
    # print('done')
    return sorted(list_of_coordinates, key=lambda x: x[-1])[:10]


def build_map(list_of_closest, coordinates):
    """
    Builds .html map using folium.
    Creates 3 layers:
    1. World map
    2. Markers with main point, and 10 closest filming locations.
    3. Lines that mean the distances that get_closest_places() function calculated.
    And a LayerControl option that allow to enable or disable these layers.
    """
    map1 = folium.Map(location=coordinates, zoom_start=10)
    featgr = folium.FeatureGroup(name='Closest places')
    colors = ['red', 'darkgreen', 'darkred', 'lightblue',
              'black', 'purple', 'white', 'pink', 'orange', 'gray']
    for i in range(len(list_of_closest)):
        featgr.add_child(folium.Marker(
            location=list_of_closest[i][-2], popup=folium.Popup(
                list_of_closest[i][0].split('{')[0]), icon=folium.Icon(icon='',
                                                                       color=colors[i])))
    featgr.add_child(folium.Marker(location=coordinates, popup='main location',
                                   icon=folium.Icon(icon='arrow-down', color='beige')))
    map1.add_child(featgr)
    color_line = folium.FeatureGroup(name='Lines between places')
    for i in range(len(list_of_closest)):
        color_line.add_child(folium.PolyLine(
            [list_of_closest[i][2], coordinates], color=colors[i]))
    map1.add_child(color_line)
    map1.add_child(folium.LayerControl())
    map1.save('Test.html')
    # print('done')


def main():
    """
    Main function.
    """
    args = parcing()
    build_map(get_closest_places((args.latitude, args.longitude), convert_data_to_coordinates(
        read_data_from_file(args.filepath, args.year))), (args.latitude, args.longitude))


if __name__ == '__main__':
    # import doctest
    # print(doctest.testmod())
    main()

# start=time.time()
# build_map(get_closest_places((50.4501, 30.5234), convert_data_to_coordinates(
#     read_data_from_file('locator.list', '2004')[:10000])), (50.4501, 30.5234))
# end=time.time()
# print(end-start)
