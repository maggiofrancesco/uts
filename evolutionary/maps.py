# -*- coding: utf-8 -*-

import googlemaps

gmaps = googlemaps.Client(key='AIzaSyDPIwBmGSv8LYLur-YTGB0KiKQQojUjNsw')


def get_directions(origin, destination, mode="driving"):
    directions_result = gmaps.directions(origin, destination, mode)
    distance = directions_result[0]["legs"][0]["distance"]
    duration = directions_result[0]["legs"][0]["duration"]
    return {"distance": distance, "duration": duration}


def closer_request(start, requests, requests_indexes):
    closer_req = requests[requests_indexes[0]]
    stop = "{0},{1}".format(closer_req.lat_dep, closer_req.lon_dep)
    closer_distance = get_directions(start, stop)["distance"]["value"]
    request_index = requests_indexes[0]

    for index in range(len(requests)):
        if index == 0:
            continue
        request = requests[requests_indexes[index]]
        stop = "{0},{1}".format(request.lat_dep, request.lon_dep)
        distance = get_directions(start, stop)["distance"]["value"]
        if distance < closer_distance:
            closer_req = request
            closer_distance = distance
            request_index = requests_indexes[index]

    return request_index, closer_req


if __name__ == "__main__":
    print get_directions("Viale due cappelle 25, bitonto", "Via benedetto tripes 23, giovinazzo")
    print get_directions("Viale due cappelle 25, bitonto", "Via sparano, Bari")
