# -*- coding: utf-8 -*-

import numpy as np
from random import randint


class Matrix(object):

    def __init__(self, buses, requests):
        self.buses = buses
        self.requests = requests
        self.n_requests = len(requests)
        self.n_buses = len(buses)
        self.matrix = np.zeros((self.n_requests, self.n_buses), dtype=np.int16)
        self.status = {i:{"seats":buses[i].seats, "requests": 0} for i in range(self.n_buses)}

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
        for j in range(len(self.matrix[0])):
            count = 0
            indexes_requests = []
            for i in range(len(self.matrix)):
                if self.matrix[i][j] == 1:
                    count += 1
                    indexes_requests.append(i)

            seats = self.buses[j].seats
            if seats < count:
                requests_to_move = count - seats
                for i in range(requests_to_move):
                    for key, value in self.status.iteritems():
                        if value["requests"] < value["seats"]:
                            random_request = randint(0, len(indexes_requests) - 1)
                            request = indexes_requests[random_request]
                            self.matrix[request][j] = 0
                            self.matrix[request][key] = 1
                            indexes_requests.remove(request)
                            self.status[key]["requests"] += 1
                            self.status[j]["requests"] -= 1
                            break

    """
    Metodo controllo priorità.
    Le priorità da seguire sono di due tipologie: soddisfare le richieste che
    più sono vicine al mezzo specifico e rispettare l'ora d'arrivo della richiesta
    effettuata dall'utente
    """
    def priority(self):
        pass

    """
    Metodo creazione del valore di fitness.
    Assegna a ciascuna matrice due valori di fitness, in tale contesto
    relativi al tempo e alla distanza che i mezzi devono impiegare per
    soddisfare le richieste ricevute.
    """
    def fitness(self):
        pass

    """
    Metodo per la mutazione di ciascuna matrice della popolazione.
    Si occupa della mutazione scambiando due colonne per ciascuna matrice.
    Se le due colonne selezionate casualmente sono vuote, seleziona altre colonne.
    """
    def mutation(self):
        pass

    """
    Stampa la matrice.
    """
    def print_matrix(self):
        print self.matrix


if __name__ == "__main__":

    from database import dao
    buses = dao.get_buses()
    requests = dao.get_requests()

    matrice = Matrix(buses, requests)
    matrice.initializing()
    matrice.print_matrix()
    print "\nDopo popolamento...\n"
    matrice.print_matrix()
    print "\nDopo compatibility...\n"
    matrice.compatibility()
    matrice.print_matrix()
