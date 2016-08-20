# -*- coding: utf-8 -*-

import os
import uuid
import numpy as np
import maps as gmaps
from database import dao
from random import randint
from datetime import timedelta
from ConfigParser import SafeConfigParser


config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config_evol.cfg'))
minutes_range = int(config.get("generation", "minutes_range"))


class Matrix(object):

    def __init__(self, buses, requests):
        self.buses = buses
        self.requests = requests
        self.n_requests = len(requests)
        self.n_buses = len(buses)
        self.matrix = np.zeros((self.n_requests, self.n_buses), dtype=np.int16)
        self.status = {i: {"seats": buses[i].seats, "requests": 0} for i in range(self.n_buses)}
        self.fitness_data = {'id': None, 'distance': None, 'duration': None}
        self.actions = {}   # Struttura destinata a contenere le action da compiere da ciascun bus (salita o discesa)

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
    Per ciascuna navetta, le richieste vengono riordinate tenendo conto del vincolo di tempo stabilito dagli utenti.
    Per fare in modo che le richieste vengano riordinate tenenendo conto anche delle distanze, il gruppo di richieste
    associato a ciascuna navetta viene suddiviso in chunk orari. In questo modo, in ciascun chunk sono presenti le
    richieste da soddisfare nell'arco mezz'ora (questo parametro è modificabile) e si ottimizza a seconda delle
    distanze. A seconda di come vengono ordinate, successivamente si effettuano i relativi scambi in matrice, con
    un'accurata gestione degli indici. E' importante sottolineare che l'ottimizzazione viene effettuata considerando
    l'action più vicina da effettuare (salita o discesa di un passeggero). Le action da compiere da ciascuna navetta
    vengono man mano collezionate all'interno di un apposita struttura (self.actions), utilizzata in seguito per
    fitness e print_matrix.
    """
    def priority(self):
        maps = gmaps.Maps()
        for j in range(self.n_buses):

            bus_position_lat = self.buses[j].lat
            bus_position_lon = self.buses[j].lon
            self.actions[self.buses[j].id_bus] = []
            bus_actions = self.actions[self.buses[j].id_bus]

            start = "{0},{1}".format(bus_position_lat, bus_position_lon)

            count = 0
            requests = []
            requests_indexes = []
            for i in range(self.n_requests):
                if self.matrix[i][j] == 1:
                    count += 1
                    requests.append({"index": i, "request": self.requests[i]})
                    requests_indexes.append(i)

            # Richieste ordinate per datetime
            requests_ordered = sorted(requests, key=lambda x: x["request"].time_arr)

            while len(requests_ordered) >= 1:

                # Considero tutte le richieste vicine temporalmente, nell'arco di un certo intervallo di minuti
                request_datetime = requests_ordered[0]["request"].time_arr
                time_threshold = request_datetime + timedelta(minutes=minutes_range)
                requests_chunk = [data for data in requests_ordered if data["request"].time_arr <= time_threshold]

                # Le richieste nell'arco orario vengono gestite per vicinanza
                requests_chunk_ordered = maps.order_by_distance(start, requests_chunk, bus_actions)
                len_request_chunk = len(requests_chunk)

                # Spostamenti sfruttando le richieste ordinate ottenute precedentemente
                # Si deve inoltre gestire i cambiamenti negli indici
                closer_request_index = requests_chunk_ordered[0]["index"]
                closer_request = requests_chunk_ordered[0]["request"]

                while len(requests_chunk_ordered) >= 1:
                    request_to_move = self.requests[requests_indexes[0]]

                    if closer_request != request_to_move:
                        self.requests[requests_indexes[0]] = closer_request
                        self.requests[closer_request_index] = request_to_move

                        # Modificare l'indice delle richieste spostate. Andrebbe fatto anche sulla
                        # struttura requests_chunk_ordered ma dato che quest'ultima non è altro che
                        # una shallow copy della prima, allora non serve.
                        done = [False, False]
                        for value_in_list in requests:
                            if done == [True, True]:
                                break
                            if request_to_move in value_in_list.values():
                                value_in_list["index"] = closer_request_index
                                done[0] = True
                                continue
                            if closer_request in value_in_list.values():
                                value_in_list["index"] = requests_indexes[0]
                                done[1] = True
                                continue

                        # Modificare l'indice delle richieste spostate. In questo caso la modifica
                        # viene effettuata in requests_ordered, dato che i dati in essa contenuti
                        # vengono poi riposti nella struttura actions
                        done = [False, False]
                        for value_in_list in requests_ordered:
                            if done == [True, True]:
                                break
                            if request_to_move in value_in_list.values():
                                value_in_list["index"] = closer_request_index
                                done[0] = True
                                continue
                            if closer_request in value_in_list.values():
                                value_in_list["index"] = requests_indexes[0]
                                done[1] = True
                                continue

                    # Si elimina la richiesta piazzata, sia da requests che da requests_chunk_ordered
                    requests.remove(requests_chunk_ordered[0])
                    requests_chunk_ordered.remove(requests_chunk_ordered[0])
                    requests_indexes.remove(requests_indexes[0])

                    if len(requests_chunk_ordered) >= 1:
                        closer_request_index = requests_chunk_ordered[0]["index"]
                        closer_request = requests_chunk_ordered[0]["request"]

                # Si elimina il chunk contenente le richieste piazzate
                requests_ordered = requests_ordered[len_request_chunk:]
                bus_position_lat = closer_request.lat_arr   # Priorità su partenza o arrivo? lat_dep o lat_arr ?
                bus_position_lon = closer_request.lon_arr   # Priorità su partenza o arrivo? lat_dep o lat_arr ?
                start = "{0},{1}".format(bus_position_lat, bus_position_lon)

    """
    Metodo creazione del valore di fitness.
    Assegna a ciascuna matrice due valori di fitness, in tale contesto relativi al tempo e alla distanza
    che i mezzi devono impiegare per soddisfare le richieste ricevute. La struttura fondamente utilizzata è quella
    contenente le action che ciascun mezzo dovrà effettuare. A seconda della action (get_on/get_off), vengono
    calcolati distanza e tempo che la navetta dovrà sopportare per eseguirla. Di volta in volta, i movimenti
    effettuati dalla navetta vengono inseriti nel database, per poterli utilizzare in seguito con print_matrix.
    """
    def fitness(self):
        maps = gmaps.Maps()
        self.fitness_data['id'] = str(uuid.uuid4())
        distance = 0
        duration = 0
        for j in range(self.n_buses):
            id_bus = self.buses[j].id_bus
            dao.insert_movement(self.fitness_data['id'], self.buses[j].id_bus, self.buses[j].lat,
                                self.buses[j].lon, self.buses[j].place)

            bus_position_lat = self.buses[j].lat
            bus_position_lon = self.buses[j].lon
            for data in self.actions[id_bus]:

                bus_origin = "{0},{1}".format(bus_position_lat, bus_position_lon)
                request = data["request_data"]["request"]
                if data["action"] == "get_on":
                    req_departure_lat = request.lat_dep
                    req_departure_lon = request.lon_dep
                    req_departure = "{0},{1}".format(req_departure_lat, req_departure_lon)
                    directions_from_bus = maps.get_directions(bus_origin, req_departure)
                    distance += directions_from_bus["distance"]
                    duration += directions_from_bus["duration"]

                    bus_position_lat = req_departure_lat
                    bus_position_lon = req_departure_lon

                else:
                    req_arrival_lat = request.lat_arr
                    req_arrival_lon = request.lon_arr
                    req_arrival = "{0},{1}".format(req_arrival_lat, req_arrival_lon)
                    directions_from_bus = maps.get_directions(bus_origin, req_arrival)
                    distance += directions_from_bus["distance"]
                    duration += directions_from_bus["duration"]

                    bus_position_lat = req_arrival_lat
                    bus_position_lon = req_arrival_lon

                dao.insert_movement(self.fitness_data["id"], self.buses[j].id_bus, bus_position_lat, bus_position_lon)

        self.fitness_data['distance'] = distance
        self.fitness_data['duration'] = duration

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
            x_column = randint(0, self.n_buses - 1)
            y_column = randint(0, self.n_buses - 1)
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

    """
    Conta il numero di richieste assegnate ad un mezzo specifico.
    """
    def num_bus_requests(self, bus):
        num_requests = 0
        for i in range(len(self.matrix)):
            if self.matrix[i][bus] == 1:
                num_requests += 1

        return num_requests

    """
    Effettua una stampa in console della matrice Richieste-Mezzi.
    """
    def print_row_matrix(self):
        for j in range(self.n_buses):
            print self.buses[j]
            for i in range(self.n_requests):
                if self.matrix[i][j] == 1:
                    print self.requests[i]

    """
    Restituisce una struttura dati contenente i risultati dell'ottimizzazione.
    """
    def print_matrix(self):
        maps = gmaps.Maps()
        data = {}
        for j in range(self.n_buses):
            bus = self.buses[j]
            id_bus = bus.id_bus
            bus_requests = []
            movements = dao.get_movements(self.fitness_data["id"], bus.id_bus)
            movements_index = 0
            for action in self.actions[id_bus]:
                request_data = {}
                request = action["request_data"]["request"]
                movement = movements[movements_index]
                movement_lat = movement["lat"]
                movement_lon = movement["lon"]
                bus_origin = "{0},{1}".format(movement_lat, movement_lon)

                if action["action"] == "get_on":
                    req_departure_lat = request.lat_dep
                    req_departure_lon = request.lon_dep
                    req_departure = "{0},{1}".format(req_departure_lat, req_departure_lon)
                    directions_from_bus = maps.get_directions(bus_origin, req_departure)

                else:
                    req_arrival_lat = request.lat_arr
                    req_arrival_lon = request.lon_arr
                    req_arrival = "{0},{1}".format(req_arrival_lat, req_arrival_lon)
                    directions_from_bus = maps.get_directions(bus_origin, req_arrival)

                distance = directions_from_bus["distance"]
                duration = directions_from_bus["duration"]

                request_data["action"] = action["action"]
                request_data["id_request"] = request.id_request
                request_data["license_plate"] = bus.license_plate
                request_data["place"] = movement["place"]
                request_data["lat_place"] = movement["lat"]
                request_data["lon_place"] = movement["lon"]
                request_data["departure"] = request.departure
                request_data["lat_dep"] = request.lat_dep
                request_data["lon_dep"] = request.lon_dep
                request_data["arrival"] = request.arrival
                request_data["lat_arr"] = request.lat_arr
                request_data["lon_arr"] = request.lon_arr
                request_data["time_arrival"] = str(request.time_arr)
                request_data["distance"] = distance
                request_data["duration"] = duration
                bus_requests.append(request_data)

                movements_index += 1

            data[bus.id_bus] = bus_requests

        return data


if __name__ == "__main__":

    buses = dao.get_buses()
    requests = dao.get_requests(previous_day=True)

    matrice = Matrix(buses, requests)
    matrice.initializing()
    print '\nDopo popolamento...\n'
    matrice.print_row_matrix()
    print '\nDopo compatibility e prima di priority: \n'
    matrice.compatibility()
    matrice.print_row_matrix()
    print '\nPrint row matrix (inizio)\n'
    matrice.print_row_matrix()
    print '\nDopo priority e prima di fitness (stampa matrice): \n'
    matrice.priority()
    print '\nPrint row matrix (fine): \n'
    matrice.print_row_matrix()
    print '\nDopo fitness, e prima di mutazione (stampa matrice): \n'
    matrice.fitness()
    print matrice.fitness_data
    print matrice.print_matrix()
    print '\nDopo mutation: \n'
    matrice.mutation()
    matrice.print_row_matrix()
