# -*- coding: utf-8 -*-
"""
Created on Aug 15 13:28 2017
@author(s): Florian U. Jehn

This file is used to start the construction of a predefined CMF model. The
user only has to provide the forcing data and the kind of techniques (
crossover, mutation, objective function).

The structure is created in such a way, that there is always at least one
connection to the outlet.
"""
import acme.model_generators._lumped_CMF_model_template as template
import acme.model_generators._lookup as lookup
import acme.genetics.genetic as genetic
import datetime


class LumpedCMFGenerator:
    def __init__(self, start_year, 
                 end_year, 
                 validation_time_span,

                 obj_func,
                 optimal_fitness,
                 Distribution, 
                 algorithm, 
                 et,
                 
                 prec, 
                 discharge, 
                 t_mean, 
                 t_min, 
                 t_max,

                 max_age=50,
                 pool_size=10
                 ):
        """
        Sets everything up, ready to be solved.

        :param start_year: year for the start of the calibration period
        :param end_year: year for the end of the calibration period
        :param validation_time_span: time after end_year which should be
        used for calibration
        :param obj_func: the objective function that should be used (only
        the name is needed, all objective functions in spotpy are possible)
        :param Distribution: The way the parameters will be distributed (
        e.g. Weibull)
        :param et: Method for calculation of evapotranspiration
        """
        # Calibration/Validation stuff
        self.start_year = start_year
        self.end_year = end_year
        self.validation_time_span = validation_time_span
        # Get the functions and classes the match the user specified inputs.
        self.obj_func = lookup.get_obj_func(obj_func)
        self.optimal_fitness = optimal_fitness
        self.Distribution = lookup.get_distribution(Distribution)
        self.algorithm = lookup.get_algorithm(algorithm)
        self.et = lookup.get_evapotranspiration(et)
        # Forcing data
        self.data = {
            "prec": prec, 
            "discharge": discharge,
            "t_mean": t_mean,
            "t_min": t_min,
            "t_max": t_max
        }
        # Define gen set
        # This is done so widespread to make it more readable and also allow
        #  it later to check for what is in what.
        self.storages = ["snow", "canopy", "first_layer", "second_layer",
                    "third_layer", "river"]
        self.connections = ["first_out", "first_river", "first_third",
                            "second_third", "second_river", "third_river"]
        self.snow_params = ["meltrate", "snow_melt_temp"]
        self.canopy_params = ["lai", "canopy_closure"]
        self.et_params = ["etv0", "fetv0"]
        self.first_layer_params = ["beta_first_out", "beta_first_river",
                                   "beta_first_second"]
        self.second_layer_params = ["beta_second_river", "beta_second_third"]
        self.third_layer_params = ["beta_third_river"]
        self.river_params = ["beta_river_out"]
        self.params = (self.snow_params + self.canopy_params +
                       self.et_params + self. first_layer_params +
                       self.second_layer_params + self.third_layer_params +
                       self.river_params)
        self.gene_set = self.storages + self.connections + self.params

        # Arguments for genetics behaviour
        self.max_age = max_age
        self.pool_size = pool_size
        
    def solve(self):
        """
        Starts the process of model selection.

        Calls the genetic file with all needed informations.
        :return: None, but writes the best found model to a file
        """
        # Helper functions as interface
        data = self.data
        gene_set = self.gene_set
        def fn_create():
            return create(gene_set)

        def fn_display(candidate, start_time):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes, data)

        def fn_mutate(genes):
            mutate(genes, fn_get_fitness)

        def fn_crossover(parent, donor):
            return crossover(parent, donor, fn_get_fitness)

        start_time = datetime.datetime.now()
        best = genetic.get_best(fn_get_fitness, None, self.optimal_fitness,
                                None, fn_display, fn_mutate, fn_create,
                                max_age=self.max_age,
                                pool_size=self.pool_size,
                                crossover=fn_crossover)
        while not self.optimal_fitness > best.fitness:
            pass

        write_best_model(best)


def get_fitness(obj_func, evaluation, simulation):
    """
    Calculates the fitness of a given genotype.
    :return:
    """
    model = template.LumpedModelCMF()
    return obj_func(evaluation, simulation)


def display(candidate, start_time):
    """
    Display the current candidate and his fitness
    :param candidate:
    :param start_time:
    :return:
    """
    time_diff = datetime.datetime.now() - start_time
    print("{}\t{}\t{}\t{}".format(
        " ".join(map(str, candidate.genes)),
        candidate.fitness, candidate.Strategy.name, time_diff))


def mutate(genes, fn_get_fitness):
    """
    Mutates a genome
    :param genes:
    :param fn_get_fitness:
    :return:
    """
    pass


def crossover(parent, donor, get_fitness):
    """
    Performs a crossover between to genotypes.
    :return:
    """
    pass


def create(gene_set):
    """
    Creates a genotype after given rules.
    
    Allows creation in such a way, that a connection to the outlet is 
    guaranteed. 
    :param gene_set: all possible genes for a model
    :return: a genotype of a model
    """
    pass


def write_best_model(genes):
    """
    Writes the best model to a file.

    :param genes:
    :return:
    """
    pass