# -*- coding: utf-8 -*-

import os
from entities.bus import Bus
from datetime import date, timedelta
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


def sign_up(name, surname, email, username, user_password):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO public.\"Utenti\"(username, email, nome, cognome, password) VALUES ("
                   "'{0}','{1}','{2}','{3}','{4}')".format(username, email, name, surname, user_password))

    connection.commit()
    connection.close()


def sign_in(email, user_password):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    username = None

    cursor.execute("SELECT username FROM public.\"Utenti\" WHERE email = '{0}' and password = '{1}'"
                   "".format(email, user_password))
    row = cursor.fetchone()
    if row is not None:
        username = row[0]

    connection.close()
    return username


def check_user(username, email):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    result = {"username": None, "email": None}

    cursor.execute("SELECT username FROM public.\"Utenti\" WHERE username = '{0}'".format(username))
    row = cursor.fetchone()
    if row is not None:
        result["username"] = row[0]

    cursor.execute("SELECT email FROM public.\"Utenti\" WHERE email = '{0}'".format(email))
    row = cursor.fetchone()
    if row is not None:
        result["email"] = row[0]

    connection.close()
    return result


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


def get_bus_id(license_plate):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM public.\"Mezzi\" WHERE targa = '{0}'".format(license_plate))
    row = cursor.fetchone()
    if row is not None:
        id_bus = row[0]
    else:
        id_bus = None

    connection.close()
    return id_bus


def get_requests(previous_day):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()
    requests = []
    if previous_day:
        yesterday = str(date.today() - timedelta(days=1))
        query = "SELECT * FROM public.\"Richieste\" WHERE ora_arrivo::date = '{0}'".format(yesterday)
    else:
        query = 'SELECT * FROM public."Richieste"'

    cursor.execute(query)
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


def insert_request(lat_departure, lon_departure, lat_arrival, lon_arrival, time_departure, time_arrival,
                   request_user, departure='', arrival=''):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO public.\"Richieste\"(origine, lat_origine, lon_origine, destinazione, "
                   "lat_destinazione, lon_destinazione, ora_partenza, ora_arrivo, utente) "
                   "VALUES('{0}', {1}, {2}, '{3}', {4}, {5}, '{6}', '{7}', '{8}') RETURNING id".format(departure,
                    lat_departure, lon_departure, arrival, lat_arrival, lon_arrival, time_departure, time_arrival,
                                                                                                       request_user))

    request_inserted_id = cursor.fetchone()[0]

    connection.commit()
    connection.close()

    return request_inserted_id


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
    if route is not None:
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


def insert_coordinates(license_plate, travel_date, lat, lon):

    connection = DBConnection(host, port, database, user, password).connect()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO public.\"Posizioni_Mezzi\"(mezzo, data_viaggio, lat, lon) "
                   "VALUES ('{0}', '{1}', {2}, {3})".format(license_plate, travel_date, lat, lon))

    connection.commit()
    connection.close()
