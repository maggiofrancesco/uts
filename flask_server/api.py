# -*- coding: utf-8 -*-

import os
import sys
import json
import hashlib
import check_thread
from database import dao
from flask_api import status
from ConfigParser import SafeConfigParser
from logbook import Logger, StreamHandler
from flask import Flask, request, Response
from datetime import datetime, date, timedelta


config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config_server.cfg'))
reading_routes_folder = config.get("server", "reading_routes_folder")
app = Flask(__name__)

users_logged = []


@app.route('/')
def hello_world():
    return 'Urban Transport System'


@app.route('/sign_up', methods=['POST'])
def sign_up():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        name = data["name"]
        surname = data["surname"]
        email = data["email"]
        username = data["username"]
        password = data["password"]

        check_existence = dao.check_user(username, email)

        if not check_existence["username"] and not check_existence["email"]:
            hashed_password = hashlib.md5(password).hexdigest()
            dao.sign_up(name, surname, email, username, hashed_password)
            result = {"result": "New user registered"}
            status_code = status.HTTP_200_OK
        else:

            result = {"result": "Email and/or Username already exists", "data": check_existence}
            status_code = status.HTTP_406_NOT_ACCEPTABLE
    else:

        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/sign_in', methods=['POST'])
def sign_in():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        email = data["email"]
        password = data["password"]
        hashed_password = hashlib.md5(password).hexdigest()

        if email in users_logged:
            result = {"result": "User already logged"}
            status_code = status.HTTP_200_OK
        else:

            username = dao.sign_in(email, hashed_password)
            if username is not None:
                users_logged.append(email)
                result = {"result": username}
                status_code = status.HTTP_200_OK
            else:
                result = {"result": "Email and/or password wrong"}
                status_code = status.HTTP_401_UNAUTHORIZED
    else:

        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/sign_out', methods=['POST'])
def sign_out():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        email = data["email"]
        if email in users_logged:
            users_logged.remove(email)
            result = {"result": "Sign out did"}
            status_code = status.HTTP_200_OK
        else:
            result = {"result": "User not logged"}
            status_code = status.HTTP_401_UNAUTHORIZED
    else:

        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/travel_request', methods=['POST'])
def travel_request():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        departure = data['departure']
        lat_departure = data['lat_departure']
        lon_departure = data['lon_departure']
        arrival = data['arrival']
        lat_arrival = data['lat_arrival']
        lon_arrival = data['lon_arrival']
        time_departure = str(datetime.today())  # Not used, but inserted for future developments
        time_arrival = data['time_arrival']
        user = data['user']

        if user in users_logged:

            id_request = dao.insert_request(
                departure=departure,
                lat_departure=lat_departure,
                lon_departure=lon_departure,
                arrival=arrival,
                lat_arrival=lat_arrival,
                lon_arrival=lon_arrival,
                time_departure=time_departure,
                time_arrival=time_arrival,
                request_user=user
            )

            result = {"result": id_request}
            status_code = status.HTTP_200_OK

        else:

            result = {"result": "User not logged"}
            status_code = status.HTTP_401_UNAUTHORIZED

    else:

        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/optimized', methods=['POST'])
def optimized_route():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        license_plate = data['license_plate']

        if license_plate != "" and license_plate is not None:
            id_bus = dao.get_bus_id(license_plate)
            if id_bus is not None:
                yesterday = str(date.today() - timedelta(days=1))
                try:
                    with open('../{0}/{1}.json'.format(reading_routes_folder, yesterday), 'r') as optimized_routes:
                        data = json.load(optimized_routes)
                        route = data[str(id_bus)]

                    result = {"result": route}
                    status_code = status.HTTP_200_OK
                except IOError:
                    result = {"result": "Optimized route not found"}
                    status_code = status.HTTP_404_NOT_FOUND
            else:
                result = {"result": "License plate inserted not exists"}
                status_code = status.HTTP_204_NO_CONTENT
        else:
            result = {"result": "License plate not provided"}
            status_code = status.HTTP_400_BAD_REQUEST
    else:
        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/estimated_departure', methods=['POST'])
def estimated_departure():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        id_request = data["id_request"]
        departure_time = None

        if id_request != "" and id_request is not None:

            yesterday = str(date.today() - timedelta(days=1))
            with open('../{0}/{1}.json'.format(reading_routes_folder, yesterday), 'r') as optimized_routes:
                data = json.load(optimized_routes)
                found_request = False

                for bus, travel_requests in data.iteritems():
                    for travel_req in travel_requests:
                        if travel_req["id_request"] == id_request:
                            departure_time = travel_req["estimated_departure"]
                            found_request = True
                            break
                    if found_request:
                        break

                if not found_request:
                    result = {"result": "travel request not found"}
                    status_code = status.HTTP_404_NOT_FOUND
                else:
                    result = {"result": {"id_request": id_request, "estimated_departure": departure_time}}
                    status_code = status.HTTP_200_OK
        else:
            result = {"result": "id request not provided"}
            status_code = status.HTTP_400_BAD_REQUEST

    else:
        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/bus_stops', methods=['GET'])
def bus_stops():

    if request.headers['Content-Type'] == 'application/json':
        bus_stops = dao.get_bus_stops()

        result = {"result": bus_stops}
        status_code = status.HTTP_200_OK
    else:
        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/send_coordinates', methods=['POST'])
def send_coordinates():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        license_plate = data["license_plate"]
        lat = data["lat"]
        lon = data["lon"]
        travel_date = data["date"]

        if license_plate != "" and license_plate is not None:
            if lat is not None and lon is not None:
                if travel_date != "" and travel_date is not None:

                    dao.insert_coordinates(license_plate, travel_date, lat, lon)
                    result = {"result": "coordinates inserted"}
                    status_code = status.HTTP_200_OK

                else:
                    result = {"result": "date not provided"}
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                result = {"result": "lat or/and lon not provided"}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            result = {"result": "license plate not provided"}
            status_code = status.HTTP_400_BAD_REQUEST

    else:
        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


if __name__ == "__main__":

    """
    The main entry point of the application
    """

    StreamHandler(sys.stdout).push_application()
    log = Logger('Main - Urban Transport System')

    log.notice("Flask server started.")
    check_thread.main()
    log.notice("Control Thread started.")

    app.run(host="0.0.0.0", port=5000, debug=False)
