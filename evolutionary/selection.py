# -*- coding: utf-8 -*-

"""
Seleziona le matrici con il valore di fitness più basso all'interno di una specifica generazione.
"""
def min_fitness(population):

    exchanges = len(population) / 4
    exchanges = 1 if exchanges == 0 else exchanges
    ordered_by_distance = sorted(population, key=lambda x: x.fitness_data["distance"])
    return ordered_by_distance[:exchanges]

"""
Seleziona le matrici con il valore di fitness più elevato all'interno di una specifica generazione.
"""
def max_fitness(population):

    exchanges = len(population) / 4
    exchanges = 1 if exchanges == 0 else exchanges
    ordered_by_distance = sorted(population, key=lambda x: x.fitness_data["distance"], reverse=True)
    return ordered_by_distance[:exchanges]

"""
Metodo per l'effuazione dello scambio di matrici tra due generazioni.
"""
def exchange(prev_population, next_population):

    good_prev_population = min_fitness(prev_population)
    bad_next_population = max_fitness(next_population)
    index = 0
    for matrix in good_prev_population:
        next_population.remove(bad_next_population[index])
        next_population.append(matrix)
        index += 1
