# -*- coding: utf-8 -*-

import copy
import selection
import numpy as np
import matrix as mtx
from database import dao


class Generation(object):

    def __init__(self, population):
        self.buses = dao.get_buses()
        self.requests = dao.get_requests()
        self.population = population

    def first_generation(self):
        self.prev_generation = np.array([None for i in range(self.population)])
        self.next_generation = np.array([None for i in range(self.population)])

        for index in range(len(self.prev_generation)):
            buses = copy.deepcopy(self.buses)
            requests = copy.deepcopy((self.requests))
            self.prev_generation[index] = mtx.Matrix(buses, requests)

        for matrix in self.prev_generation:
            matrix.initializing()
            matrix.compatibility()
            matrix.priority()
            matrix.fitness()

        self.next_generation = self.prev_generation

    def next_generation(self):
        self.prev_generation = copy.deepcopy(self.next_generation)

        for matrix in self.next_generation:
            matrix.mutation()
            matrix.compatibility()
            matrix.priority()
            matrix.fitness()
            selection.exchange()