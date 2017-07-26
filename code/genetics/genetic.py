#/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Jul 26 14:20 2017
@author(s): Florian U. Jehn

This tool performs most of the work related to genetic algorithms
"""

import random
import statistics
import sys
import time


class Chromosome:
    """
    Combines the genes and the fitness in a single object.
    """
    def __init__(self, genes, fitness):
        self.genes = genes
        self.fitness = fitness


def _generate_parent(length, gene_set, get_fitness):
    """
    Generates on individual form a given gene_set and tests its fitness.

    :param length:
    :param gene_set:
    :param get_fitness:
    :return:
    """
    # TODO: Devise a way to create CMF Model parents which certainly have a
    # TODO: connection to the outlet.
    pass


def _mutate(parent, gene_set, get_fitness):
    """
    Mutates the genome of a parent and tests its fitness.

    :param parent:
    :param gene_set:
    :param get_fitness:
    :return:
    """
    # TODO: Write mutate function
    pass


def get_best(get_fitness, target_len, optimal_fitness, gene_set, display):
    """
    Reusable genetic engine to find the best solution for a given fitness.
    Responsible for displaying improvements and breaking the loop.

    :param get_fitness:
    :param target_len:
    :param optimal_fitness:
    :param gene_set:
    :param display:
    :return:
    """
    # TODO: Write get best
    pass


def _get_improvement(new_child, generate_parent):
    """
    Responsible for generating successively better gene sequences,
    which will be send back with yield.

    :param new_child:
    :param generate_parent:
    :return:
    """
    # TODO: Find out if this is needed for ACME
    pass
