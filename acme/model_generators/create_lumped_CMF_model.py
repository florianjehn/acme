# -*- coding: utf-8 -*-
"""
Created on Aug 15 13:28 2017
@author(s): Florian U. Jehn

This file is used to start the construction of a predefined CMF model. The
user only has to provide the forcing data and the kind of techniques (
distribution, objective function, etc.).

The structure is created in such a way, that there is always at least one
connection to the outlet.
"""
import acme.model_generators._lumped_CMF_model_template as template
import acme.genetics.genetic as genetic
import datetime
import random
import os
import copy
import spotpy
import time


class LumpedCMFGenerator:
    # Define gene_set
    # This is done so widespread to make it more readable and also allow
    #  it later to check for what is in what.
    # "first_layer" is excluded, as a model without any storage makes no sense.
    # The possible parameters are defined for the class as a whole as they
    # are equal for all instances and are easier to access this way.

    # The storages "first", "second" and "third" refer to "first_layer"
    # "second_layer" and "third_layer" respectively and are shortened for
    # better handling.
    storages = ["snow", "canopy", "second", "third", "river"]
    connections = ["tr_first_out", "tr_first_river", "tr_first_second",
                   "tr_second_third", "tr_second_river",
                   "tr_third_river"]
    snow_params = ["snow_meltrate", "snow_melt_temp"]
    canopy_params = ["canopy_lai", "canopy_closure"]
    first_layer_params = ["beta_first_out", "beta_first_river",
                          "beta_first_second", "v0_first_out",
                          "v0_first_river", "v0_first_second"]
    second_layer_params = ["beta_second_river", "beta_second_third"]
    third_layer_params = ["beta_third_river"]
    river_params = ["beta_river_out"]
    params = (snow_params + canopy_params +
              first_layer_params +
              second_layer_params + third_layer_params +
              river_params)
    gene_set = storages + connections + params

    # Dictionary to save all models that have been tested so far. The key is
    # the genes in the model and the value the best objective function value.
    models_so_far = {}

    def __init__(self, begin_calibration,
                 end_calibration,
                 begin_validation,
                 end_validation,

                 optimal_fitness,

                 prec,
                 discharge,
                 t_mean,
                 t_min,
                 t_max,

                 max_age=50,
                 pool_size=10,
                 max_seconds=None,
                 search_iterations=1,
                 obj_func_increment=0.1
                 ):
        """
        Sets everything up, ready to be solved.

        :param begin_calibration:
        :param end_calibration:
        :param begin_validation:
        :param end_validation:
        :param optimal_fitness:
        :param prec:
        :param discharge:
        :param t_mean:
        :param t_min:
        :param t_max:
        :param max_age:
        :param pool_size:
        :param max_seconds:
        :param search_iterations:
        :param obj_func_increment:
        """

        # Calibration/Validation stuff
        self.begin_calibration = begin_calibration
        self.end_calibration = end_calibration
        self.begin_validation = begin_validation
        self.end_validation = end_validation

        # Get the functions and classes the match the user specified inputs.
        self.optimal_fitness = optimal_fitness

        # Forcing data
        self.data = {
            "prec": prec, 
            "discharge": discharge,
            "t_mean": t_mean,
            "t_min": t_min,
            "t_max": t_max
        }
        # Arguments for genetics behaviour
        self.max_age = max_age
        self.pool_size = pool_size
        self.search_iterations = search_iterations
        self.obj_func_increment = obj_func_increment
        self.max_seconds = max_seconds

    def solve(self):
        """
        Starts the process of model selection.

        Calls the genetic file with all needed information.

        :return: None, but writes the best found model to a file
        """
        # Make the needed variables available for the helper functions.
        data = self.data
        # Calibration/Validation stuff
        begin_calibration = self.begin_calibration
        end_calibration = self.end_calibration
        begin_validation = self.begin_validation
        end_validation = self.end_validation

        # Helper functions used as interface to genetic.

        def fn_create():
            return create()

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes, data,
                               begin_calibration, end_calibration,
                               begin_validation, end_validation)

        def fn_mutate(genes):
            mutate(genes, fn_get_fitness)

        def fn_crossover(parent, donor):
            return crossover(parent, donor)

        # Save the starting time
        start_time = datetime.datetime.now()

        # Give all definitions to the get_best function of genetic to start
        # the whole process of evolutionary selection
        best = genetic.get_best(fn_get_fitness, None, self.optimal_fitness,
                                None, fn_display, fn_mutate, fn_create,
                                max_age=self.max_age,
                                pool_size=self.pool_size,
                                crossover=fn_crossover,
                                max_seconds=self.max_seconds)

        # At this place it might be handy to nest the while loop into a
        # for loop. The for loop starts with a value for the objective
        # function below the desired one and the gives the while loop some
        # time to find best model. If this is accomplished a new run is
        # started with a bit higher value of the objective function. This is
        #  repeated until the algorithm is no longer able to find a model
        # which satisfies the condition.

        # Something like
        if self.search_iterations > 1:
            for iteration in range(self.search_iterations):
                pass

        else:
            # Run the process until the desired fitness value is reached.
            while not self.optimal_fitness > best.fitness:
                pass

        # Write the best model to file.
        write_all_models()


def get_fitness(genes, data,
                begin_calibration, end_calibration,
                begin_validation, end_validation):
    """
        Calculates the fitness of a given genotype.

    :param genes: genotype that is to be tested for its fitness
    :param data: the weather data in the form of a dict of lists
    :param begin_calibration:
    :param end_calibration:
    :param begin_validation:
    :param end_validation:
    :return: Fitness value
    """
    # Check if the model to be generated is able to connect to an output
    check_for_connection(genes)

    # Find the effective structure of the current genes
    effective_structure = find_active_genes(genes)

    # Compare if the genes the function gets, have already been calculated
    #  as a model
    for old_model in LumpedCMFGenerator.models_so_far.keys():
        # Find the effective structure
        # Turn model in list version
        old_model_genes = old_model.split()
        # Find out if the model has already been calculated. If so, simply
        # return the fitness value of the old model
        if set(old_model_genes) == set(genes):
            return LumpedCMFGenerator.models_so_far[old_model]
        if set(old_model_genes) == set(effective_structure):
            return LumpedCMFGenerator.models_so_far[old_model]

    # If not call the template and run the model
    current_model = template.LumpedModelCMF(effective_structure, data,
                                            begin_calibration, end_calibration,
                                            begin_validation, end_validation)

    # Find out if the model should run parallel (for supercomputer)
    parallel = 'mpi' if 'OMPI_COMM_WORLD_SIZE' in os.environ else 'seq'

    # Connect the model to the dream algorithm.
    sampler = spotpy.algorithms.dream(current_model, parallel=parallel,
                                      dbformat="noData")

    # The template runs until the predefined convergence value of dream is
    # reached (or the maximal value for repetitions is reached).
    sampler.sample(500, convergence_limit=1.6)

    # Extract the best value from the model
    best_like = sampler.bestlike

    # Save the current model in the all models list
    model_key = " ".join(genes)
    LumpedCMFGenerator.models_so_far[model_key] = best_like

    # Return best fitness value of all runs
    return best_like


def find_active_genes(genes):
    """
    Calls all other methods which strip the genes to only the active ones.

    :param genes: Current genes
    :return: Copy of current genes, with only the active genes in it.
    """
    # Make a copy, so the original remains unchanged
    genes_copy = copy.deepcopy(genes)
    # Delete all inactive stuff
    genes_copy = del_inactive_storages(genes_copy)
    genes_copy = del_inactive_params(genes_copy)

    return genes_copy


def del_inactive_storages(genes):
    """
    Deletes all storages, which have no inflow from any source.

    :param genes: Current genes
    :return: Current genes, with all inactive storages deleted
    """
    # Find all connection genes
    connections = []
    for gene in genes:
        if "tr" in gene:
            connections.append(gene)

    # Cycle through all connection genes and split them in sources and targets
    sources = []
    targets = []
    for connection in connections:
        name, source, target = connection.split("_")
        sources.append(source)
        targets.append(target)

    # Determine which storages are present in the genes
    possible_storages = LumpedCMFGenerator.storages
    actual_storages = []
    for possible_storage in possible_storages:
        for gene in genes:
            if possible_storage == gene:
                actual_storages.append(gene)

    # Look if storage is in source and target
    # If not, delete storage
    for storage in actual_storages:
        if storage in targets and storage in sources:
            continue
        else:
            genes.remove(storage)

    return genes


def del_inactive_params(genes):
    """
    Deletes all parameters which do not have their storage present in the
    current genes

    :param genes: Current genes
    :return: Current genes, with all inactive params deleted
    """

    # Add the first layer to the copy, so the connections  from first are
    # not all deleted by default.
    # Determine which storages are present in the genes
    possible_storages = LumpedCMFGenerator.storages + ["first"]
    actual_storages = []
    for possible_storage in possible_storages:
        for gene in genes:
            if possible_storage == gene:
                actual_storages.append(gene)

    # Go through all genes to test if their storage is present.
    for gene in genes:
        # Delete all params which do not have their storage present
        storage_present = False
        for storage in actual_storages:
            if storage in gene:
                storage_present = True
                break
        if not storage_present:
            genes.remove(gene)

    return genes


def display(candidate, start_time):
    """
    Display the current candidate and his fitness.

    :param candidate: Model/genotype that is to be displayed
    :param start_time: Time when the current program started
    :return: None
    """
    time_diff = datetime.datetime.now() - start_time
    # calculate how much % of the genes are active
    active_genes = find_active_genes(candidate.genes)
    activity = len(active_genes) / len(candidate.genes) * 100
    print(("Genes: {}\t\nGene Activity: {} % \t\nFitness: {}\tStrategy: {}\t"
           "Time: {}".format(
                            " ".join(map(str, candidate.genes)), activity,
                            candidate.fitness, candidate.Strategy.name,
                            time_diff)))


def mutate(genes, gene_set):
    """
    Mutates a genome
    :param genes: genes of a given individual
    :param gene_set: all possible genes.
    :return: None (the list is directly manipulated)
    """
    mutation_type = random.choice(["add", "del", "swap"])
    max_changes = 3
    if mutation_type == "add":
        for _ in range(random.randint(1, max_changes)):
            # If the genes already contains all possible genes,
            # delete one gene and stop iteration
            if set(genes) == set(gene_set):
                random.shuffle(genes)
                genes.pop()
                break
            while True:
                new_gene = random.choice(gene_set)
                # Check if the random choice to avoid adding it again
                if new_gene not in genes:
                    genes.append(new_gene)
                    break

    elif mutation_type == "del":
        for _ in range(random.randint(1, max_changes)):
            # If the list is empty add an item and stop iteration
            if len(genes) == 0:
                new_gene = random.choice(gene_set)
                genes.append(new_gene)
                break
            # Pick a random genes
            random.shuffle(genes)
            genes.pop()

    elif mutation_type == "swap":
        for _ in range(random.randint(1, max_changes)):
            # Make a copy of the parent genes
            initial_genes = genes[:]
            # create a index for a random place in the parent genome
            index = random.randrange(0, len(genes))
            # take two random samples out of the gene set
            new_gene, alternate = random.sample(gene_set, 2)
            # replace the gene at index with another one, if it is randomly the
            # same, exchange it with the alternative.
            initial_genes[index] = (alternate if new_gene ==
                                    initial_genes[index]
                                    else
                                    new_gene)
    return


def crossover(first_parent, second_parent):
    """
    Performs a crossover between to genotypes. A single point crossover is
    used.
    :param first_parent: genotype of the first parent (list)
    :param second_parent: genotype of the second parent (list)
    :return: a new genotype (list)
    """
    # Select two random points in the length of the parent and donor genome
    index_first_parent = random.randint(0, len(first_parent))
    index_second_parent = random.randint(0, len(second_parent))
    # Take all the genes from before the point from parent and all the genes
    # from behind the point from behind the point
    part_first_parent = first_parent[:index_first_parent]
    part_second_parent = second_parent[index_second_parent:]
    # Combine the parts
    child_genes = part_first_parent + part_second_parent
    # Create a set out of it to avoid duplicates
    # then turn it back to a list and return it
    child_genes = list(set(child_genes))
    return child_genes


def create(test=False):
    """
    Creates a genotype after given rules.
    
    Allows creation in such a way, that a connection to the outlet is 
    guaranteed. 
    :return: a genotype of a model
    """
    threshold = 1/3
    genes = []

    # Snow
    if random.random() < threshold or test:
        genes.append("snow")
        # Only add the snow parameter genes if there is a snow storage
        if random.random() < threshold or test:
            genes.append("snow_meltrate")
        if random.random() < threshold or test:
            genes.append("snow_melt_temp")

    # Canopy
    if random.random() < threshold or test:
        genes.append("canopy")
        if random.random() < threshold or test:
            genes.append("canopy_closure")
        if random.random() < threshold or test:
            genes.append("canopy_lai")

    # Layers
    if random.random() < threshold or test:
        genes.append("second")
        if random.random() < threshold or test:
            genes.append("third")

    if random.random() < threshold or test:
        genes.append("river")

    # Connections first layer
    if random.random() < threshold or test:
        genes.append("tr_first_second")
        if random.random() < threshold or test:
            genes.append("beta_first_second")
        if random.random() < threshold or test:
            genes.append("v0_first_second")

    if random.random() < threshold or test:
        genes.append("tr_first_river")
        if random.random() < threshold or test:
            genes.append("beta_first_river")
        if random.random() < threshold or test:
            genes.append("v0_first_river")

    if random.random() < threshold or test:
        genes.append("tr_first_out")
        if random.random() < threshold or test:
            genes.append("beta_first_out")
        if random.random() < threshold or test:
            genes.append("v0_first_out")

    # Connections second layer
    if "second" in genes:
        # loop through until second_layer has a connection so somewhere
        while "tr_second_third" not in genes or "tr_second_river" not in genes:
            if random.random() < threshold or test:
                genes.append("tr_second_third")
                if random.random() < threshold or test:
                    genes.append("beta_second_third")
            if random.random() < threshold or test:
                genes.append("tr_second_river")
                if random.random() < threshold or test:
                    genes.append("beta_second_river")

    # Connections third layer
    if "third" in genes:
        # always add a connection, otherwise third_layer would be a dead end
        genes.append("tr_third_river")
        if random.random() < threshold or test:
            genes.append("beta_third_river")

    # River
    if "river" in genes:
        if random.random() < threshold or test:
            genes.append("beta_river_out")

    # Check if a connection to the outlet exists
    check_for_connection(genes)
    return genes


def write_all_models():
    """
    Writes all the models to a file.

    :return: None
    """
    # Open the output file
    name = 'acme_results_' + str(time.time()) + '.csv'
    outfile = open(name, 'w')

    # Make the header
    header = "Like" + ", " + "Genes" + "\n"
    outfile.write(header)

    # Write the entries
    for genes, like in LumpedCMFGenerator.models_so_far.items():
        # Exclude the non active genes before writing it down
        genes_copy = genes.split()
        genes_copy = find_active_genes(genes_copy)
        genes_copy = ", ".join(genes_copy)
        line = str(like) + ", " + genes_copy + "\n"
        outfile.write(line)
    outfile.close()


def check_for_connection(genes):
    """
    Determines if a there is a connection to the outlet and if not creates one.

    :param genes:
    :return: None
    """
    to_outlet = False
    outgoing = []
    for connection in LumpedCMFGenerator.connections:
        if "out" in connection:
            outgoing.append(connection)
    for connection in outgoing:
        if connection in genes:
            to_outlet = True
            break
    if not to_outlet:
        genes.append("tr_first_out")
