# -*- coding: utf-8 -*-

import os
from entities.bus import Bus
from entities.request import Request
from db_connection import DBConnection
from ConfigParser import SafeConfigParser


config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config_db.cfg'))
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

    connection.close()
    return requests


def insert_movement(id_fitness, id_mezzo, lat, lon, luogo=''):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO public.\"Spostamenti\"(id_fitness, id_mezzo, luogo, lat, lon) "
                   "VALUES ('{0}', {1}, '{2}', {3}, {4})".format(id_fitness, id_mezzo, luogo, lat, lon))

    connection.commit()
    connection.close()


def get_movements(id_fitness, id_mezzo):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM public.\"Spostamenti\" WHERE id_fitness='{0}' and id_mezzo='{1}'"
                   "ORDER BY id".format(id_fitness, id_mezzo))

    spostamenti = cursor.fetchall()
    result = []
    for spostamento in spostamenti:
        result.append({
            "id_movement": spostamento[0],
            "id_fitness": spostamento[1],
            "id_bus": spostamento[2],
            "place": spostamento[3],
            "lat": spostamento[4],
            "lon": spostamento[5]
        })

    connection.close()
    return result


def insert_route(lat_ori, lon_ori, lat_dest, lon_dest, distanza, durata, origine='', destinazione=''):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO public.\"Itinerari\"(origine, lat_origine, lon_origine, destinazione,"
                   " lat_destinazione, lon_destinazione, distanza, durata) VALUES ('{0}',{1},{2},'{3}',{4},{5},{6},{7})"
                   "".format(origine, lat_ori, lon_ori, destinazione, lat_dest, lon_dest, distanza, durata))

    connection.commit()
    connection.close()


def get_route(lat_origine, lon_origine, lat_destinazione, lon_destinazione):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM public.\"Itinerari\" WHERE lat_origine={0} and lon_origine={1} "
                   "and lat_destinazione={2} and lon_destinazione={3}".format(lat_origine, lon_origine,
                                                                                lat_destinazione, lon_destinazione))

    route = cursor.fetchone()
    if route != None:
        result = {
            "id_route": route[0],
            "departure": route[1],
            "lat_dep": route[2],
            "lon_dep": route[3],
            "arrival": route[4],
            "lat_arr": route[5],
            "lon_arr": route[6],
            "distance": route[7],
            "duration": route[8]
        }
    else:
        result = None

    connection.close()
    return result


if __name__ == "__main__":
    buses = get_buses()
    requests = get_requests()
    #import pdb; pdb.set_trace()
    for bus in buses:
        print(str(bus))
    for request in requests:
        print(str(request))

    insert_movement("asdasdasd", 10, 41.109024, 16.679656)

    print get_movements("3f8ef40f-9a00-40f4-9217-f4a96f0b7b60", 12)
    insert_route(123.2, 1111.2, 1231.2, 1234.4, 1231, 123, origine="Piazza Marconi", destinazione="Piazza Aldo Moro")
    print get_route(123.2,1111.2,1231.2,1234.4)