# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
import os

from db_connection import DBConnection
from entities.bus import Bus
from entities.request import Request


config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.cfg'))
host = config.get("database", "host")
port = config.get("database", "port")
user = config.get("database", "user")
password = config.get("database", "password")
database = config.get("database", "database")


def get_buses():

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()
    buses = []

    cursor.execute('SELECT * FROM public."Mezzi"')
    for row in cursor:
        buses.append(
            Bus(
                id_bus=row[0],
                license_plate=row[1],
                seats=row[2],
                place=row[3],
                lat=row[4],
                lon=row[5]
            )
        )

    connection.close()
    return buses


def get_requests():

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()
    requests = []

    cursor.execute('SELECT * FROM public."Richieste"')
    for row in cursor:
        requests.append(
            Request(
                id_request=row[0],
                departure=row[1],
                lat_dep=row[2],
                lon_dep=row[3],
                arrival=row[4],
                lat_arr=row[5],
                lon_arr=row[6],
                time_dep=row[7],
                time_arr=row[8],
                user=row[9]
            )
        )

    return requests


if __name__ == "__main__":
    buses = get_buses()
    requests = get_requests()
    #import pdb; pdb.set_trace()
    for bus in buses:
        print(str(bus))
    for request in requests:
        print(str(request))