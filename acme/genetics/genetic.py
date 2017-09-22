# -*- coding: utf-8 -*-

# Author: Clinton Sheppard <fluentcoder@gmail.com>
# Modifications: Florian U. Jehn <florianjehn@posteo.de>
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

This tool is the genetic engine, which makes the most important computations.
"""

import random
from bisect import bisect_left
from math import exp
from enum import Enum


class Chromosome:
    """
    Combines the genes, the age since the last improvement,
    the strategy of reproduction and the fitness in a single object.
    """
    def __init__(self, genes, fitness, Strategy):
        self.genes = genes
        self.fitness = fitness
        self.age = 0
        self.Strategy = Strategy


class Strategies(Enum):
    """
    Crossover is used as a supplement to mutation. So the algorithm should
    always prefer whichever way works best. For this it is necessary to keep
    of which way was used to create that parent. This is saved in the
    strategy class.
    """
    create = 0,
    mutate = 1,
    crossover = 2


def get_best(get_fitness, target_len, optimal_fitness, gene_set, display,
             custom_mutate=None, custom_create=None, max_age=None,
             pool_size=1, crossover=None):
    """
    Reusable genetic engine to find the best solution for a given fitness.
    Responsible for displaying improvements and breaking the loop.

    :param get_fitness: Function which determines the fitness of individuals
    :param target_len: Length of the solution to be found
    :param optimal_fitness: Desired fitness value
    :param gene_set: Set of possible genes
    :param display: Function that displays the current progress
    :param custom_mutate: custom mutation function if the regular one is not
    working for the problem at hand
    :param custom_create: custom creation function if the regular one is not
    working for the problem at hand
    :param max_age: Maximum age a genotype can have before its discarded
    :param pool_size: amount of parents (in crossover)
    :param crossover: Function which defines how the crossover should
    happen. Is not directly implemented here, as it is very project specific
    :return: The best found solution
    """
    # Switch between different mutating behaviours
    if custom_mutate is None:
        def fn_mutate(parent):
            return _mutate(parent, gene_set, get_fitness)
    else:
        def fn_mutate(parent):
            return _mutate_custom(parent, custom_mutate, get_fitness)

    # Switch between different creating behaviours
    if custom_create is None:
        def fn_generate_parent():
            return _generate_parent(target_len, gene_set, get_fitness)
    else:
        def fn_generate_parent():
            genes = custom_create()
            return Chromosome(genes, get_fitness(genes), Strategies.create)
    # Strategy lookup maps the counter of the different strategies to the
    # strategies itself. Allowing an easier access.
    strategy_lookup = {
        Strategies.create: lambda p, i, o: fn_generate_parent(),
        Strategies.mutate: lambda p, i, o: fn_mutate(p),
        Strategies.crossover: lambda p, i, o: _crossover(p.genes, i, o,
                                                         get_fitness,
                                                         crossover,
                                                         fn_mutate,
                                                         fn_generate_parent)
    }
    # Used strategies documents which strategies were used to create parents.
    used_strategies = [strategy_lookup[Strategies.mutate]]
    # Create a child by selecting a random strategy if a crossover method is
    #  implemented.
    if crossover is not None:
        used_strategies.append(strategy_lookup[Strategies.crossover])

        def fn_new_child(parent, index, parents):
            return random.choice(used_strategies)(parent, index, parents)

    else:
        # Index and parents a kept here even as they are not used, to allow
        # the same access to fn_new_child regardless if a crossover is
        # implemented or not.
        def fn_new_child(parent, index, parents):
            return fn_mutate(parent)

    # _get_improvement is used as a kind of generator here.
    for improvement in _get_improvement(fn_new_child, fn_generate_parent,
                                        max_age, pool_size):
        display(improvement)
        f = strategy_lookup[improvement.Strategy]
        # Update used strategies, when _get_improvement sends a new
        # improvement.
        used_strategies.append(f)
        if not optimal_fitness > improvement.fitness:
            return improvement


def _get_improvement(new_child, generate_parent, max_age, pool_size):
    """
    Responsible for generating successively better gene sequences,
    which will be send back with yield.

    :param new_child: Mutate function
    :param generate_parent: Function
    :param max_age: Maximum age a genotype can reach before its replace.
    Needed for simulated annealing.
    :param pool_size: Amount of parents, for crossover
    :return: Chromosome object of improved genotype
    """
    # Generate a parent and return it
    best_parent = generate_parent()
    yield best_parent
    # Add best_parent to the parents pool
    parents = [best_parent]
    # keep the historical fitnesses for later possible comparisons
    historical_fitnesses = [best_parent.fitness]
    # Fill the parents pool
    for _ in range(pool_size - 1):
        parent = generate_parent()
        # If one newly generated parent has a higher fitness, then the best
        # parent so far replace him and update historical fitnesses.
        if parent.fitness > best_parent.fitness:
            yield parent
            best_parent = parent
            historical_fitnesses.append(parent.fitness)
        parents.append(parent)
    # When called next time go into while loop.
    # Create a new child. If it has a worse fitness then the best parent
    # discard it and try again.
    # Since we have a pool of parents, each time through the loop select a
    # different one to be the current parent.
    last_parent_index = pool_size - 1
    p_index = 1
    while True:
        p_index = p_index - 1 if p_index > 0 else last_parent_index
        parent = parents[p_index]
        child = new_child(parent, p_index, parents)
        # Try again if the best parent is better then the child
        if parent.fitness > child.fitness:
            if max_age is None:
                continue
            parent.age += 1
            if max_age > parent.age:
                continue
            # Searches for child.fitness in historical fitnesses and returns
            #  its index
            index = bisect_left(historical_fitnesses, child.fitness, 0,
                                len(historical_fitnesses))
            # Comparison of how high the current genotype is ranked in the
            # historical fitnesses
            difference = len(historical_fitnesses) - index
            # change the difference to a proportion
            proportion_similar = difference / len(historical_fitnesses)
            # Randomly decided to make the child a new parent or generate a
            # new parent. exp(-proportion_similar) generates values between
            # 0.36 (fitness close to best fitness) and 1 (fitness far away
            # from best fitness)
            if random.random() < exp(-proportion_similar):
                parents[p_index] = child
                continue
            parents[p_index] = best_parent
            parent.age = 0
            continue
        # This if is used to retain children which have the same fitness as
        # the parent. It if implement this way to avoid having to write an
        # __eq__ function. But as the child is not better than the parent
        # it is not returned but only used for further mutation.
        if not child.fitness > parent.fitness:
            child.age = parent.age + 1
            parents[p_index] = child
            continue
        parents[p_index] = child
        parent.age = 0
        # Return the child if it better than the best parent so far.
        if child.fitness > best_parent.fitness:
            yield child
            best_parent = child
            historical_fitnesses.append(child.fitness)


def _generate_parent(length, gene_set, get_fitness):
    """
    Generates one individual from a given gene_set.

    :param length: length of the genome of the individual
    :param gene_set: possible genes to create parent
    :param get_fitness: Function to determine the fitness value of a genotype
    :return: A Chromosome object, which contains the genes and the fitness
    """
    # Create an empty list, which will contain the genome of the parent
    genes = []
    # add gene to genes until the predefined length is reached
    while len(genes) < length:
        # the sample size is equal to the predefined length minus the genes
        # already in place. Except when this would be longer than the
        # possible gene_set. Then this has to be repeated, as extend can
        # only use as many things as are in gene_set
        sample_size = min(length - len(genes), len(gene_set))
        genes.extend(random.sample(gene_set, sample_size))
    # Calculate the fitness for the new parent and return it as a Chromosome
    # object which contains the genes and the fitness combined.
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness, Strategies.create)


def _mutate(parent, gene_set, get_fitness):
    """
    Mutates one char of the genome of parent

    :param parent: Chromosome object of the parent
    :param gene_set: possible genes to use for mutation
    :param get_fitness: Function to determine the fitness value of a genotype
    :return: Chromosome object which contains genes and fitness of the child
    """
    # Make a copy of the parent genes
    child_genes = parent.genes[:]
    # create a index for a random place in the parent genome
    index = random.randrange(0, len(parent.genes))
    # take two random samples out of the gene set
    new_gene, alternate = random.sample(gene_set, 2)
    # replace the gene at index with another one, if it is randomly the
    # same, exchange it with the alternative.
    child_genes[index] = (alternate if new_gene == child_genes[index]
                          else new_gene)
    # Calculate the fitness for the new parent and return it as a Chromosome
    #  object which contains the genes and the fitness combined.
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness, Strategies.mutate)


def _mutate_custom(parent, custom_mutate, get_fitness):
    """
    Only used to execute the custom_mutate function from the calling function
    """
    child_genes = parent.genes[:]
    custom_mutate(child_genes)
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness, Strategies.mutate)


def _crossover(parent_genes, index, parents, get_fitness, crossover, mutate,
               generate_parent):
    """
    This function allows the use of a passed over crossover function.

    :param parent_genes: Genotype of the parent
    :param index: Index of the parent in the parent pool.
    :param parents: Pool of parents
    :param get_fitness: Function to calculate fitness
    :param crossover: Function to perform crossover
    :param mutate: Function to perform mutation
    :param generate_parent: Function to create a new parent.
    :return: Chromosome of a child created by crossover.
    """
    # Choose a random donor from the parents list.
    donor_index = random.randrange(0, len(parents))
    # If the donor_index and index are equal the crossover would happen
    # between only one individual and itself. Therefore create a different
    # donor index.
    if donor_index == index:
        donor_index = (donor_index + 1) % len(parents)
    # Create a new child with the provided crossover method from parents[
    # index] and parents[donor_index].
    child_genes = crossover(parent_genes, parents[donor_index].genes)
    # If the parents[index] and parents[donor_index] have the same genotype,
    #  a crossover makes no sense and therefore newly created and mutated
    # parent is returned.
    if child_genes is None:
        # parent and donor are indistinguishable
        parents[donor_index] = generate_parent()
        return mutate(parents[index])
    # If the crossover was successful, calculate its fitness and return it.
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness, Strategies.crossover)
