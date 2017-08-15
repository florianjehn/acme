# -*- coding: utf-8 -*-

# Author: Clinton Sheppard <fluentcoder@gmail.com>
# Copyright (c) 2016 Clinton Sheppard
# Modification Copyright (c) 2017 Florian Ulrich Jehn <florianjehn@posteo.de>
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

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
    Generates on individual form a given gene_set and ss its fitness.

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
    Mutates the genome of a parent and ss its fitness.

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
