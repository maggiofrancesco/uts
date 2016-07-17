# -*- coding: utf-8 -*-


class Bus(object):

    def __init__(self, id, license_plate, seats, lat, lon, place="Address not available"):
        self.id = id
        self.license_plate = license_plate
        self.seats = seats
        self.lat = lat
        self.lon = lon
        self.place = place

    def __str__(self):
        return "ID Mezzo: {0} - Targa: {1} - Posti a sedere: {2} - Lat: {3} - Lon: {4} - Indirizzo luogo: {5}".format(
            self.id, self.license_plate, self.seats, self.lat, self.lon, self.place
        )
