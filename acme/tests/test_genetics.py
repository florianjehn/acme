# -*- coding: utf-8 -*-
"""
Created on Aug 17 14:18 2017
@author(s): Florian U. Jehn

This test suit uses an example from the book "Genetic algorithms with
Python" to test the functionality of the genetic module. The example used is
"Traveling Salesman Problem". It is used because it uses all methods also
needed for ACME.
"""
import unittest
from acme.genetics import genetic
import random
import datetime
import math
from itertools import chain


class GeneticTests(unittest.TestCase):
    def test_8_queens(self):
        id_to_location_lookup = {
            'A': [4, 7],
            'B': [2, 6],
            'C': [0, 5],
            'D': [1, 3],
            'E': [3, 0],
            'F': [5, 1],
            'G': [7, 2],
            'H': [6, 4]
        }
        optimal_sequence = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.solve(id_to_location_lookup, optimal_sequence)

    def test_ulysses16(self):
        id_to_location_lookup = ({1: [38.24, 20.42], 2: [39.57, 26.15],
                                  3: [40.56, 25.32], 4: [36.26, 23.12],
                                  5: [33.48, 10.54], 6: [37.56, 12.19],
                                  7: [38.42, 13.11], 8: [37.52, 20.44],
                                  9: [41.23, 9.1], 10: [41.17, 13.05],
                                  11: [36.08, -5.21], 12: [38.47, 15.13],
                                  13: [38.15, 15.35], 14: [37.51, 15.17],
                                  15: [35.49, 14.32], 16: [39.36, 19.56]})
        optimal_sequence = [14, 13, 12, 16, 1, 3, 2, 4, 8, 15, 5, 11, 9, 10,
                            7, 6]
        self.solve(id_to_location_lookup, optimal_sequence)

    def solve(self, id_to_location_lookup, optimal_sequence):
        gene_set = [i for i in id_to_location_lookup.keys()]

        def fn_create():
            return random.sample(gene_set, len(gene_set))

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes, id_to_location_lookup)

        def fn_mutate(genes):
            mutate(genes, fn_get_fitness)

        def fn_crossover(parent, donor):
            return crossover(parent, donor, fn_get_fitness)

        optimal_fitness = fn_get_fitness(optimal_sequence)
        start_time = datetime.datetime.now()
        best = genetic.get_best(fn_get_fitness, None, optimal_fitness, None,
                                fn_display, fn_mutate, fn_create,
                                max_age=500, pool_size=25,
                                crossover=fn_crossover)
        self.assertTrue(not optimal_fitness > best.fitness)


def get_distance(location_a, location_b):
    """
    Calculate the distance between two cities using the Pythagorean Theorem.

    :param location_a: First city
    :param location_b: Second city
    :return: The distance.
    """
    side_a = location_a[0] - location_b[0]
    side_b = location_a[1] - location_b[1]
    side_c = math.sqrt(side_a ** 2 + side_b ** 2)
    return side_c


class Fitness:
    def __init__(self, total_distance):
        self.total_distance = total_distance

    def __gt__(self, other):
        return self.total_distance < other.total_distance

    def __str__(self):
        return "{:0.2f}".format(self.total_distance)


def get_fitness(genes, id_to_location_lookup):
    fitness = get_distance(id_to_location_lookup[genes[0]],
                           id_to_location_lookup[genes[-1]])

    for i in range(len(genes) - 1):
        start = id_to_location_lookup[genes[i]]
        end = id_to_location_lookup[genes[i + 1]]
        fitness += get_distance(start, end)

    return Fitness(round(fitness, 2))


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    print("{}\t{}\t{}\t{}".format(
        " ".join(map(str, candidate.genes)),
        candidate.fitness, candidate.Strategy.name, time_diff
    ))


def mutate(genes, fn_get_fitness):
    count = random.randint(2, len(genes))
    initial_fitness = fn_get_fitness(genes)
    while count > 0:
        count -= 1
        index_a, index_b = random.sample(range(len(genes)), 2)
        genes[index_a], genes[index_b] = genes[index_b], genes[index_a]
        fitness = fn_get_fitness(genes)
        if fitness > initial_fitness:
            return


def crossover(parent_genes, donor_genes, fn_get_fitness):
    """
    Function to perform a crossover between two genotypes of the TSP problem.

    :param parent_genes: Genotype of a parent
    :param donor_genes: Genotype with which the crossover should happen
    :param fn_get_fitness: Function to determine the fitness.
    :return: Crossover child chromosome or None if
    """
    # Create a lookup table (pairs) of all 2-point pairs in the donor
    # parent's genes.
    pairs = {Pair(donor_genes[0], donor_genes[-1]): 0}
    for i in range(len(donor_genes) - 1):
        pairs[Pair(donor_genes[i], donor_genes[i + 1])] = 0
    # Crossover makes sure that the first and last genes in parent_genes are
    #  not adjacent in donor_genes. If they are crossover searches for a
    # pair of adjacent points from parent_genes that are not adjacent in
    # donor_genes. If one is found it is shifted to the beginning of the
    # array, so no runs wrap around the end of the array.

    # This is needed to avoid breaking the path and is called a discontinuity.
    temp_genes = parent_genes[:]
    if Pair(parent_genes[0], parent_genes[-1]) in pairs:
        # find a discontinuity
        found = False
        for i in range(len(parent_genes) - 1):
            if Pair(parent_genes[i], parent_genes[i + 1]) in pairs:
                continue
            temp_genes = parent_genes[i + 1:] + parent_genes[:i + 1]
            found = True
            break
        # If there is no discontinuity, None is returned as parent and donor
        #  are the same
        if not found:
            return None
    # Collect all runs from parent_genes that are also in donor_genes.
    runs = [[temp_genes[0]]]
    for i in range(len(temp_genes) - 1):
        if Pair(temp_genes[i], temp_genes[i + 1]) in pairs:
            runs[-1].append(temp_genes[i + 1])
            continue
        runs.append([temp_genes[i + 1]])
    # Reorder the runs to try to find a fitness better then the current
    # parent. This is done by swapping any pair os runs and checking the
    # fitness with a chance of reversing the order.
    initial_fitness = fn_get_fitness(parent_genes)
    count = random.randint(2, 20)
    run_indexes = range(len(runs))
    while count > 0:
        count -= 1
        for i in run_indexes:
            if len(runs[i]) == 1:
                continue
            if random.randint(0, len(runs)) == 0:
                runs[i] = [n for n in reversed(runs[i])]

        index_a, index_b = random.sample(run_indexes, 2)
        runs[index_a], runs[index_b] = runs[index_b], runs[index_a]
        child_genes = list(chain.from_iterable(runs))
        if fn_get_fitness(child_genes) > initial_fitness:
            return child_genes
    return child_genes


class Pair:
    """
    Pair orders two genes so that gene pairs can be compared regardless of
    cycle direction.
    """

    def __init__(self, node, adjacent):
        if node < adjacent:
            node, adjacent = adjacent, node
        self.node = node
        self.adjacent = adjacent

    def __eq__(self, other):
        return self.node == other.node and self.adjacent == other.adjacent

    def __hash__(self):
        return hash(self.node) * 397 ^ hash(self.adjacent)


if __name__ == '__main__':
    unittest.main()
