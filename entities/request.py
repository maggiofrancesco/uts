# -*- coding: utf-8 -*-


class Request(object):

    def __init__(self, id_request, lat_dep, lon_dep, lat_arr, lon_arr, departure='',
                 arrival='', time_dep=None, time_arr=None, user=None):
        self.id_request = id_request
        self.lat_dep = lat_dep
        self.lon_dep = lon_dep
        self.lat_arr = lat_arr
        self.lon_arr = lon_arr
        self.departure = departure
        self.arrival = arrival
        self.time_dep = time_dep
        self.time_arr = time_arr
        self.user = user

    def __str__(self):
        return "ID Richiesta: {0} - Lat. Partenza: {1} - Lon. Partenza: {2} - Lat. Arrivo: {3} - Lon. Arrivo: {4}" \
               " - Indirizzo partenza: {5} - Indirizzo arrivo: {6} - Time partenza: {7} - Time arrivo: {8} - Range " \
               "arrivo: {9}".format(self.id_request, self.lat_dep, self.lon_dep, self.lat_arr, self.lon_arr,
                                    self.departure, self.arrival, str(self.time_dep), str(self.time_arr), self.user
        )