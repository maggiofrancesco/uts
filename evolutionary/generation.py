# -*- coding: utf-8 -*-

import sys
import copy
import logging
import selection
import matrix as mtx
from database import dao


class Generation(object):

    def __init__(self, population_amount):
        self.buses = dao.get_buses()
        self.requests = dao.get_requests()
        self.population_amount = population_amount
        self.prev_generation = [None for i in range(self.population_amount)]
        self.next_generation = [None for i in range(self.population_amount)]

    """
    Metodo per la creazione della prima generazione di matrici.
    """
    def start_first_generation(self):
        logging.info("Generating first generation...")

        for index in range(len(self.prev_generation)):
            buses = copy.deepcopy(self.buses)
            requests = copy.deepcopy(self.requests)
            self.prev_generation[index] = mtx.Matrix(buses, requests)

        logging.info("Doing operations on {0} matrixes...".format(self.population_amount))

        for matrix in self.prev_generation:
            matrix.initializing()
            matrix.compatibility()
            matrix.priority()
            matrix.fitness()

        self.next_generation = copy.deepcopy(self.prev_generation)

    """
    Metodo per la creazione delle generazioni successive alla prima.
    Rispetto alla creazione della prima generazione, per ciascuna matrice viene richiamato il metodo
    per l'esecuzione della mutazione. Inoltre, dopo aver effettuato le operazioni sulle singole matrici
    che compongono la generazione, viene richiamato il metodo exchange del modulo selection per lo scambio
    delle matrici migliori della generazione precedente con le matrici peggiori della generazione successiva.
    """
    def start_next_generation(self):
        logging.info("Generating another generation...")

        self.prev_generation = copy.deepcopy(self.next_generation)

        logging.info("Doing operations on {0} matrixes...".format(self.population_amount))

        for matrix in self.next_generation:
            matrix.mutation()
            matrix.compatibility()
            matrix.priority()
            matrix.fitness()
        selection.exchange(self.prev_generation, self.next_generation)

    """
    Metodo per l'individuazione della migliore soluzione tra quelle presenti nell'ultima generazione.
    """
    def best_solution(self):
        ordered_by_distance = sorted(self.next_generation, key=lambda x: x.fitness_data["distance"])
        return ordered_by_distance[0].fitness_data


if __name__ == "__main__":

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    generation = Generation(population_amount=5)
    generation.start_first_generation()
    number_generation = 1
    print generation.best_solution()
    for i in range(7):
        logger.info("{0}^ generation will be created.".format(number_generation + 1))
        generation.start_next_generation()
        number_generation += 1
        print generation.best_solution()
