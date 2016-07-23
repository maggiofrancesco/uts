# -*- coding: utf-8 -*-

import maps as gmaps
import uuid
import numpy as np
from random import randint
from database import dao


class Matrix(object):

    def __init__(self, buses, requests):
        self.buses = buses
        self.requests = requests
        self.n_requests = len(requests)
        self.n_buses = len(buses)
        self.matrix = np.zeros((self.n_requests, self.n_buses), dtype=np.int16)
        self.status = {i:{"seats":buses[i].seats, "requests": 0} for i in range(self.n_buses)}
        self.fitness_data = {"id": None, "distance": None, "duration": None}

    """
    Metodo inizializzatore.
    Per ciascuna richiesta presente nella matrice, associa uno (ed un solo) mezzo.
    """
    def initializing(self):
        for row in self.matrix:
            random = randint(0, self.n_buses - 1)
            row[random] = 1
            self.status[random]["requests"] += 1

    """
    Metodo compatibilità.
    Verifica che le associazioni richiesta-mezzo siano effettivamente possibili, considerando il numero di posti
    disponibili sul mezzo. In questo modo, l'utente è certo di trovare posto a sedere all'interno della navetta.
    Sfruttando la struttura dati "status", è possibile distribuire le richieste nei mezzi che hanno posti liberi.
    Funziona molto bene quando il numero delle richieste non è superiore al numero totale di posti liberi per tutti
    i mezzi disponibili. Perciò, si potrebbe ancora migliorare gestendo tale casistica.
    """
    def compatibility(self):
        for j in range(self.n_buses):
            count = 0
            requests_indexes = []
            for i in range(self.n_requests):
                if self.matrix[i][j] == 1:
                    count += 1
                    requests_indexes.append(i)

            seats = self.buses[j].seats
            if seats < count:
                requests_to_move = count - seats
                for i in range(requests_to_move):
                    for key, value in self.status.iteritems():
                        if value["requests"] < value["seats"]:
                            random_request = randint(0, len(requests_indexes) - 1)
                            request = requests_indexes[random_request]
                            self.matrix[request][j] = 0
                            self.matrix[request][key] = 1
                            requests_indexes.remove(request)
                            self.status[key]["requests"] += 1
                            self.status[j]["requests"] -= 1
                            break

    """
    Metodo controllo priorità.
    Per ciascuna navetta, le richieste vengono riordinate sulla base della vicinanza.
    """
    def priority(self):
        maps = gmaps.Maps()
        for j in range(self.n_buses):

            bus_position_lat = self.buses[j].lat
            bus_position_lon = self.buses[j].lon
            start = "{0},{1}".format(bus_position_lat, bus_position_lon)

            count = 0
            requests = {}
            requests_indexes = []
            for i in range(self.n_requests):
                if self.matrix[i][j] == 1:
                    count += 1
                    requests[i] = self.requests[i]
                    requests_indexes.append(i)

            while len(requests) > 1:

                closer_request_index, closer_request = maps.closer_request(start, requests, requests_indexes)
                request_to_move = self.requests[requests_indexes[0]]

                if closer_request != request_to_move:
                    self.requests[requests_indexes[0]] = closer_request
                    self.requests[closer_request_index] = request_to_move
                    requests.pop(requests_indexes[0])
                    requests[closer_request_index] = request_to_move

                else:
                    requests.pop(requests_indexes[0])

                requests_indexes.remove(requests_indexes[0])

                bus_position_lat = closer_request.lat_arr       #priorità su partenza o arrivo? lat_dep o lat_arr ?
                bus_position_lon = closer_request.lon_arr       #priorità su partenza o arrivo? lat_dep o lat_arr ?
                start = "{0},{1}".format(bus_position_lat, bus_position_lon)


    """
    Metodo creazione del valore di fitness.
    Assegna a ciascuna matrice due valori di fitness, in tale contesto
    relativi al tempo e alla distanza che i mezzi devono impiegare per
    soddisfare le richieste ricevute.
    """
    def fitness(self):
        maps = gmaps.Maps()
        self.fitness_data["id"] = str(uuid.uuid4())
        distance = 0
        duration = 0
        for j in range(self.n_buses):
            dao.insert_movement(self.fitness_data["id"], self.buses[j].id_bus, self.buses[j].lat,
                                   self.buses[j].lon, self.buses[j].place)

            print "Bus: "+str(self.buses[j])

            for i in range(self.n_requests):
                bus_position_lat = self.buses[j].lat
                bus_position_lon = self.buses[j].lon
                bus_origin = "{0},{1}".format(bus_position_lat, bus_position_lon)

                print "Bus position: "+self.buses[j].place

                if self.matrix[i][j] == 1:
                    req_departure_lat = self.requests[i].lat_dep
                    req_departure_lon = self.requests[i].lon_dep
                    req_departure = "{0},{1}".format(req_departure_lat, req_departure_lon)
                    req_arrival_lat = self.requests[i].lat_arr
                    req_arrival_lon = self.requests[i].lon_arr
                    req_arrival = "{0},{1}".format(req_arrival_lat, req_arrival_lon)
                    print "Request: "+str(self.requests[i])
                    print "Request departure: "+self.requests[i].departure
                    print "Request arrival: "+self.requests[i].arrival
                    print bus_origin, req_departure
                    print req_departure, req_arrival
                    directions_from_bus = maps.get_directions(bus_origin, req_departure)
                    directions_from_request = maps.get_directions(req_departure, req_arrival)
                    distance += directions_from_bus["distance"]
                    distance += directions_from_request["distance"]
                    duration += directions_from_bus["duration"]
                    duration += directions_from_request["duration"]

                    print "Directions_from_bus: "+str(directions_from_bus)
                    print "Directions_from_request "+str(directions_from_request)
                    print "Total Distance: "+str(distance/1000)+"km"+" Total Duration: "+str(duration/60)+"m"

                    self.buses[j].place = self.requests[i].arrival
                    self.buses[j].lat = self.requests[i].lat_arr
                    self.buses[j].lon = self.requests[i].lon_arr
                    dao.insert_movement(self.fitness_data["id"], self.buses[j].id_bus, self.buses[j].lat,
                                           self.buses[j].lon, self.buses[j].place)

        self.fitness_data["distance"] = distance
        self.fitness_data["duration"] = duration


    """
    Metodo per la mutazione di ciascuna matrice della popolazione.
    Si occupa della mutazione scambiando due colonne per ciascuna matrice. Vengono scelte due colonne random e se i due
    indici casuali sono uguali oppure le due colonne scelte risultano vuote, si procede con la scelta di due nuove
    colonne, generando valori casuali fino ad un numero massimo di tentativi pari al 75% del numero dei bus (colonne).
    """
    def mutation(self):
        iterations = int(self.n_buses * 0.75)
        if iterations == 0:
            return

        for i in range(iterations):
            x_column = randint(0, self.n_buses-1)
            y_column = randint(0, self.n_buses-1)
            if x_column == y_column:
                continue
            else:
                x_requests = self.num_bus_requests(x_column)
                y_requests = self.num_bus_requests(y_column)
                if x_requests == 0 and y_requests == 0:
                    continue
                else:
                    break

        for i in range(self.n_requests):
            temp = self.matrix[i][y_column]
            self.matrix[i][y_column] = self.matrix[i][x_column]
            self.matrix[i][x_column] = temp


    def num_bus_requests(self, bus):
        num_requests = 0
        for i in range(len(self.matrix)):
            if self.matrix[i][bus] == 1:
                num_requests += 1

        return num_requests


    def print_row_matrix(self):
        for j in range(self.n_buses):
            print self.buses[j]
            for i in range(self.n_requests):
                if self.matrix[i][j] == 1:
                    print self.requests[i]


    """
    Stampa la matrice.
    """
    def print_matrix(self):
        maps = gmaps.Maps()
        data = {}
        for j in range(self.n_buses):
            bus = self.buses[j]
            bus_requests = []
            movements = dao.get_movements(self.fitness_data["id"], bus.id_bus)
            movements_index = 0
            for i in range(self.n_requests):
                request_data = {}
                if self.matrix[i][j] == 1:
                    request = self.requests[i]
                    req_departure_lat = request.lat_dep
                    req_departure_lon = request.lon_dep
                    req_departure = "{0},{1}".format(req_departure_lat, req_departure_lon)
                    req_arrival_lat = request.lat_arr
                    req_arrival_lon = request.lon_arr
                    req_arrival = "{0},{1}".format(req_arrival_lat, req_arrival_lon)
                    movement = movements[movements_index]
                    movement_lat = movement["lat"]
                    movement_lon = movement["lon"]
                    bus_origin = "{0},{1}".format(movement_lat, movement_lon)

                    directions_from_bus = maps.get_directions(bus_origin, req_departure)
                    directions_from_request = maps.get_directions(req_departure, req_arrival)
                    distance = directions_from_bus["distance"] + directions_from_request["distance"]
                    duration = directions_from_bus["duration"] + directions_from_request["duration"]

                    request_data["id_bus"] = bus.id_bus
                    request_data["license_plate"] = bus.license_plate
                    request_data["place"] = movement["place"]
                    request_data["departure"] = request.departure
                    request_data["arrival"] = request.arrival
                    request_data["distance"] = distance
                    request_data["duration"] = duration
                    bus_requests.append(request_data)

                    movements_index += 1

            data[bus.license_plate] = bus_requests

        return data


if __name__ == "__main__":

    buses = dao.get_buses()
    requests = dao.get_requests()

    matrice = Matrix(buses, requests)
    matrice.initializing()
    print '\nDopo popolamento...\n'
    matrice.print_row_matrix()
    print '\nDopo compatibility e prima di priority: \n'
    matrice.compatibility()
    matrice.print_row_matrix()
    print '\nDopo priority e prima di fitness (stampa matrice): \n'
    matrice.priority()
    matrice.print_row_matrix()
    print '\nDopo fitness, e prima di mutazione (stampa matrice): \n'
    matrice.fitness()
    print matrice.fitness_data
    print matrice.print_matrix()
    print '\nDopo mutation: \n'
    matrice.mutation()
    matrice.print_row_matrix()
