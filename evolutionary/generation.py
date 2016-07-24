# -*- coding: utf-8 -*-

import sys
import copy
import logging
import selection
import matrix as mtx
from database import dao


class Generation(object):

    def __init__(self, population):
        self.buses = dao.get_buses()
        self.requests = dao.get_requests()
        self.population = population

    def start_first_generation(self):
        logging.info("Generating first generation...")

        self.prev_generation = [None for i in range(self.population)]
        self.next_generation = [None for i in range(self.population)]

        for index in range(len(self.prev_generation)):
            buses = copy.deepcopy(self.buses)
            requests = copy.deepcopy((self.requests))
            self.prev_generation[index] = mtx.Matrix(buses, requests)

        logging.info("Doing operations on {0} matrixes...".format(self.population))

        for matrix in self.prev_generation:
            matrix.initializing()
            matrix.compatibility()
            matrix.priority()
            matrix.fitness()

        self.next_generation = self.prev_generation

    def start_next_generation(self):
        logging.info("Generating another generation...")

        self.prev_generation = copy.deepcopy(self.next_generation)

        logging.info("Doing operations on {0} matrixes...".format(self.population))

        for matrix in self.next_generation:
            matrix.mutation()
            matrix.compatibility()
            matrix.priority()
            matrix.fitness()
            selection.exchange(self.prev_generation, self.next_generation)


if __name__ == "__main__":

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    generation = Generation(2)
    generation.start_first_generation()
    number_generation = 1
    for i in range(1):
        logger.info("{0}^ generation will be created.".format(number_generation+1))
        generation.start_next_generation()
        number_generation += 1
