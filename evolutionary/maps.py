# -*- coding: utf-8 -*-

import os
import copy
import googlemaps
from database import dao
from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser


config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config_evol.cfg'))
google_directions_api_key = config.get("google_api_key", "directions")
minutes_range = int(config.get("generation", "minutes_range"))


class Maps(object):

    def __init__(self):
        self.gmaps = googlemaps.Client(key=google_directions_api_key)
        self.routes = {}    # Struttura per la tenuta dei risultati delle ricerche effettuate in esecuzione

    """
    Metodo per la gestione delle chiamate verso Google Maps.
    Il seguente metodo consente la gestione delle chiamate in modo da ridurre il traffico al minimo possibile e
    cercare di ottimizzare le tempistiche per l'ottenimento delle informazioni di distanza e durata di un viaggio.
    Se la ricerca in questione è stata effettuata durante l'esecuzione, questa sarà presente all'interno della
    struttura self.routes. Se, invece, la medesima richiesta è stata effettuata in esecuzioni passate, allora si
    dovrà effettuara la chiamata al database. Infine, se la richiesta non è mai stata effettuata in precedenza, si
    dovranno necessariamente interpellare i server di Google Maps. In quest'ultimo caso, si provvede subito ad
    inserire la nuova ricerca sia nella struttura self.routes che nel database, ottimizzando le richieste future.
    """
    def get_directions(self, origin, destination, mode="driving"):
        if (origin, destination) in self.routes:
            return self.routes[(origin, destination)]
        else:
            lat_departure, lon_departure = origin.split(",")
            lat_arrival, lon_arrival = destination.split(",")
            route = dao.get_route(lat_departure, lon_departure, lat_arrival, lon_arrival)
            if route is not None:
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

    """
    Metodo per l'individuazione della richiesta più vicina al mezzo, che sia salita o discesa di un passeggero.
    Considerata una struttura contenente le richieste da ordinare e una struttura contenente le richieste "prese",
    (cioè passeggeri che sono saliti a bordo della navetta), il metodo si occupa dell'individuazione della action
    più vicina, che sia get_on oppure get_off, avendo a disposizione le action di get_on effettuate fino a quel
    momento. Quindi, prima individua la richiesta di get_on più vicina e, successivamente, verifica la presenza o
    meno di una richiesta di get_off più vicina rispetto a quella di get_on, servendosi di requests_loaded.
    """
    def closer_action_finder(self, start, requests, requests_loaded):
        closer_request_data = requests[0]
        closer_req = requests[0]['request']
        stop = "{0},{1}".format(closer_req.lat_dep, closer_req.lon_dep)
        closer_distance = self.get_directions(start, stop)['distance']
        operation = 'get_on'

        for index in range(len(requests)):
            if index == 0:
                continue
            request_data = requests[index]
            stop = "{0},{1}".format(request_data['request'].lat_dep, request_data['request'].lon_dep)
            distance = self.get_directions(start, stop)['distance']
            if distance < closer_distance:
                closer_request_data = request_data
                closer_distance = distance

        for index in range(len(requests_loaded)):
            request_data = requests_loaded[index]
            stop = "{0},{1}".format(request_data['request'].lat_arr, request_data['request'].lon_arr)
            distance = self.get_directions(start, stop)['distance']
            if distance < closer_distance:
                closer_request_data = request_data
                closer_distance = distance
                operation = 'get_off'

        return {'request_data': closer_request_data, 'action': operation}

    """
    Metodo per l'individuazione della richiesta di discesa (action get_off) più vicina.
    Tale metodo individua la richiesta più vicina restituendo un dizionario contente l'oggetto Richiesta e la action.
    """
    def closer_get_off(self, start, requests_loaded):
        closer_request_data = requests_loaded[0]
        stop = "{0},{1}".format(closer_request_data['request'].lat_arr, closer_request_data['request'].lon_arr)
        closer_distance = self.get_directions(start, stop)["distance"]

        for index in range(len(requests_loaded)):
            if index == 0:
                continue
            request_data = requests_loaded[index]
            stop = "{0},{1}".format(request_data['request'].lat_arr, request_data['request'].lon_arr)
            distance = self.get_directions(start, stop)["distance"]
            if distance < closer_distance:
                closer_request_data = request_data
                closer_distance = distance

        return {'request_data': closer_request_data, 'action': 'get_off'}

    """
    Metodo per l'ordinamento di un chunk di richieste assegnate ad una navetta specifica.
    Il metodo riordana le richieste presenti nel chunk, memorizzando di volta in volta le action che la navetta
    dovrà eseguire (get_on/get_off) all'interno della struttura che gli viene passata (actions). L'ordinamento
    procede in maniera incrementale, iterando su di una copia della struttura requests, requests_copy (shallow copy).
    La action più vicina viene individuata chiamando il metodo self.closer_action_finder e si gestisce la casistica,
    a seconda che sia salita o discesa di un passeggero. Alla fine, vengono gestite le richieste di discesa che
    eventualmente possono essere rimaste.
    Importante sottolineare che la struttura requests ricevuta dal metodo contiene una lista di dizionari contententi
    l'indice della richiesta all'interno della matrice e l'oggetto Richiesta.
    """
    def order_by_distance(self, start, requests, actions):

        requests_loaded = []
        requests_copy = copy.copy(requests)

        index = 0
        while len(requests_copy) >= 1:
            # la prossima azione da compiere: salita o discesa di un passeggero ?
            data = self.closer_action_finder(start, requests[index:], requests_loaded)
            actions.append(data)

            # action contiene la richiesta con l'info su salita o discesa
            if data['action'] == 'get_on':
                closer_index = requests.index(data['request_data'])
                request_to_move = requests[index]
                requests[index] = data['request_data']
                requests[closer_index] = request_to_move

                requests_loaded.append(data['request_data'])
                start = "{0},{1}".format(data['request_data']['request'].lat_dep,
                                         data['request_data']['request'].lon_dep)
                requests_copy.remove(data['request_data'])
                index += 1  # si deve passare alla prossima persona da far salire a bordo

            else:   # data["action"] == "get_off"
                requests_loaded.remove(data['request_data'])
                start = "{0},{1}".format(data['request_data']['request'].lat_arr,
                                         data['request_data']['request'].lon_arr)

        # Bisogna far scendere i passeggeri a bordo rimasti
        if len(requests_loaded) >= 1:
            while len(requests_loaded) >= 1:
                data = self.closer_get_off(start, requests_loaded)
                actions.append(data)
                requests_loaded.remove(data['request_data'])
                start = "{0},{1}".format(data['request_data']['request'].lat_arr,
                                         data['request_data']['request'].lon_arr)

        return requests

"""
Metodo per effettuare una stima dell'ora di partenza relativa a ciascuna richiesta di viaggio.
Il metodo si serve delle action calcolate precedentemente, dividendole per chunk di un certo
numero di minuti (minutes_range). Quindi, ad esempio, data l'ora di arrivo della prima richiesta,
si considerano tutte le richieste da quell'ora, di mezz'ora in mezz'ora. Per ciascun chunk,
selezionando solo le action get_on, si individua l'ora di arrivo più imminente e, successivamente,
utilizzando tutte le action, si calcola la durata totale dell'esecuzione di tutte le azioni
(get on e get off). L'ora di partenza della prima richiesta viene individuata sottraendo all'ora
di arrivo più imminente la durata totale per l'esecuzione di tutte le azioni. A partire dall'ora
di partenza della prima richiesta, si somma di volta in volta la durata di ciascuna azione. Se
l'azione in questione è una get_on, il valore appena calcolato contenuto in departure_time coincide
con l'ora di partenza della richiesta.
"""
def estimate_departures(actions):

    for bus, bus_requests in actions.iteritems():

        bus_requests_copy = copy.copy(bus_requests)
        requests = []

        while len(bus_requests_copy) >= 1:
            first_request = bus_requests_copy[0]   # First request or first request remained
            requests.append(first_request)
            bus_requests_copy.remove(first_request)
            first_request_time_arrival = datetime.strptime(first_request["time_arrival"], "%Y-%m-%d %H:%M:%S")
            time_threshold = first_request_time_arrival + timedelta(minutes=minutes_range)
            for request in bus_requests_copy:

                time_arrival = datetime.strptime(request["time_arrival"], "%Y-%m-%d %H:%M:%S")
                if time_arrival > time_threshold:
                    break
                else:
                    requests.append(request)

            for request in requests:
                if request == first_request:
                    continue
                bus_requests_copy.remove(request)

            requests_get_on = [req for req in requests if req["action"] == "get_on"]
            closer_time_arrival = sorted(requests_get_on, key=lambda x: x["time_arrival"])[0]["time_arrival"]
            closer_time_arrival = datetime.strptime(closer_time_arrival, "%Y-%m-%d %H:%M:%S")

            duration = 0
            for request in requests:
                duration += request["duration"]
            minutes = duration / 60
            departure_time = closer_time_arrival - timedelta(minutes=minutes)

            index = bus_requests.index(requests[0])
            bus_requests[index]["estimated_departure"] = str(departure_time)
            requests.remove(requests[0])
            for request in requests:
                minutes = request["duration"] / 60
                departure_time = departure_time + timedelta(minutes=minutes)
                if request["action"] == "get_on":
                    index = bus_requests.index(request)
                    bus_requests[index]["estimated_departure"] = str(departure_time)

            requests = []

    return actions