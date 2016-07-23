# -*- coding: utf-8 -*-

import os
import googlemaps
from ConfigParser import SafeConfigParser
from database import dao


config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config_maps.cfg'))
google_directions_api_key = config.get("google_api_key", "directions")

class Maps(object):

    def __init__(self):
        self.gmaps = googlemaps.Client(key=google_directions_api_key)
        self.routes = {}


    def get_directions(self, origin, destination, mode="driving"):
        if (origin, destination) in self.routes:
            return self.routes[(origin, destination)]
        else:
            lat_departure, lon_departure = origin.split(",")
            lat_arrival, lon_arrival = destination.split(",")
            route = dao.get_route(lat_departure, lon_departure, lat_arrival, lon_arrival)
            if route != None:
                data = {"distance": route["distance"], "duration": route["duration"]}
                self.routes[(origin, destination)] = data
                return data
            else:
                directions_result = self.gmaps.directions(origin, destination, mode)
                distance = directions_result[0]["legs"][0]["distance"]["value"]
                duration = directions_result[0]["legs"][0]["duration"]["value"]
                data = {"distance": distance, "duration": duration}
                self.routes[(origin, destination)] = data
                dao.insert_route(lat_departure, lon_departure, lat_arrival, lon_arrival, distance, duration)
                return data


    def closer_request(self, start, requests, requests_indexes):
        closer_req = requests[requests_indexes[0]]
        stop = "{0},{1}".format(closer_req.lat_dep, closer_req.lon_dep)
        closer_distance = self.get_directions(start, stop)["distance"]
        request_index = requests_indexes[0]

        for index in range(len(requests)):
            if index == 0:
                continue
            request = requests[requests_indexes[index]]
            stop = "{0},{1}".format(request.lat_dep, request.lon_dep)
            distance = self.get_directions(start, stop)["distance"]
            if distance < closer_distance:
                closer_req = request
                closer_distance = distance
                request_index = requests_indexes[index]

        return request_index, closer_req
