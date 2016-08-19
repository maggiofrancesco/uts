# -*- coding: utf-8 -*-

import os
import sys
import json
import copy
import maps
import selection
import matrix as mtx
from database import dao
from datetime import date, timedelta
from ConfigParser import SafeConfigParser
from logbook import Logger, StreamHandler


StreamHandler(sys.stdout).push_application()
log = Logger('Generation Module - Urban Transport System')
config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config_evol.cfg'))
writing_routes_folder = config.get("generation", "writing_routes_folder")
population_amount = int(config.get("generation", "population_amount"))
generations_amount = int(config.get("generation", "generations_amount"))


class Generation(object):

    def __init__(self, population_amount, previous_day=False):
        self.buses = dao.get_buses()
        self.requests = dao.get_requests(previous_day)
        self.population_amount = population_amount
        self.prev_generation = [None for _ in range(self.population_amount)]
        self.next_generation = [None for _ in range(self.population_amount)]

    """
    Metodo per la creazione della prima generazione di matrici.
    """
    def start_first_generation(self):
        log.notice("Generating first generation...")

        for index in range(len(self.prev_generation)):
            buses = self.buses
            requests = copy.copy(self.requests)
            self.prev_generation[index] = mtx.Matrix(buses, requests)

        log.notice("Doing operations on {0} matrixes...".format(self.population_amount))

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
        log.notice("Generating another generation...")

        self.prev_generation = copy.deepcopy(self.next_generation)

        log.notice("Doing operations on {0} matrixes...".format(self.population_amount))

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
        return ordered_by_distance[0]


def main():

    generation = Generation(population_amount=population_amount, previous_day=True)
    generation.start_first_generation()
    number_generation = 1
    print generation.best_solution().fitness_data
    for i in range(generations_amount - 1):
        log.notice("{0}^ generation will be created.".format(number_generation + 1))
        generation.start_next_generation()
        number_generation += 1
        print generation.best_solution().fitness_data

    # Writing of the best solution found on a json file
    best_matrix = generation.best_solution()
    data_best_matrix = best_matrix.print_matrix()
    result = maps.estimate_departures(data_best_matrix)
    if not os.path.exists('../{0}'.format(writing_routes_folder)):
        os.mkdir('../{0}'.format(writing_routes_folder))
    yesterday = str(date.today() - timedelta(days=1))
    with open('../{0}/{1}.json'.format(writing_routes_folder, yesterday), 'w') as outfile:
        json.dump(result, outfile)
