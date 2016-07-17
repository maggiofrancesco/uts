# -*- coding: utf-8 -*-

import numpy as np
from random import randint


class Matrix(object):

    def __init__(self, n_requests, n_buses):
        self.n_requests = n_requests
        self.n_bus = n_buses
        self.matrix = np.zeros((n_requests, n_buses), dtype=np.int16)

    """
    Metodo inizializzatore.
    Per ciascuna richiesta presente nella matrice, associa uno (ed un solo) mezzo.
    """
    def initializing(self):
        for row in self.matrix:
            random = randint(0, self.n_bus - 1)
            row[random] = 1

    """
    Metodo compatibilità.
    Verifica che le associazioni richiesta-mezzo siano effettivamente possibili,
    considerando il numero di posti disponibili sul mezzo. In questo modo,
    l'utente è certo di trovare posto a sedere all'interno della navetta.
    """
    def compatibility(self):
        pass

    """
    Stampa la matrice.
    """
    def print_matrix(self):
        print self.matrix


if __name__ == "__main__":

    matrice = Matrix(10, 10)
    matrice2 = Matrix(10, 10)
    matrice.print_matrix()
    print "Dopo popolamento...\n"
    matrice.initializing()
    matrice.print_matrix()
