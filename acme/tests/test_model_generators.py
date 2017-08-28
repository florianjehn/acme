# -*- coding: utf-8 -*-
"""
Created on Aug 17 14:17 2017
@author(s): Florian U. Jehn
"""
import unittest
from acme.model_generators import create_lumped_CMF_model as generator
import acme.genetics as genetics
import datetime
import copy
import cmf
import math


class generators_tests(unittest.TestCase):

    gene_set = ["snow", "canopy", "first_layer", "second_layer",
                     "third_layer", "river", "first_out", "first_river",
                     "first_third", "second_third", "second_river",
                     "third_river", "meltrate", "snow_melt_temp", "lai",
                     "canopy_closure", "etv0", "fetv0", "beta_first_out",
                     "beta_first_river", "beta_first_second",
                     "beta_second_river", "beta_second_third",
                     "beta_third_river", "beta_river_out"]

    def test_solve(self):
        area_catchment = 2976.41
        fnQ = "GrebenauQTagMittel__1979_1990.txt"
        fnT = "Temp_max_min_avg_1979_1988.txt"
        fnP = "Prec_Grebenau_1979_1988.txt"
        P, T, Tmin, Tmax, Q = load_data(fnQ, fnT, fnP, area_catchment)

        lumped_model_generator = generator.LumpedCMFGenerator(
            1980,
            1982,
            1,
            "nashsutcliffe",
            0.5,
            "Uniform",
            "lhs",
            "Hargreave",
            P,
            Q,
            T,
            Tmin,
            Tmax,
            )
        lumped_model_generator.solve()

    def test_get_fitness(self):
        pass

    def test_display(self):
        """
        Calls the display function with one test set to determine if it works
        at all. Cannot determine if the output is as expected.
        This has to checked manually.
        """
        start_time = datetime.datetime.now() - datetime.timedelta(0, 3)
        candidate = genetics.genetic.Chromosome(
            ["snow", "first_layer"], 0.8, genetics.genetic.Strategies.create)
        generator.display(candidate, start_time)

    def test_mutation(self):
        """
        Calls the mutation function for 1000 times. After that ~ 333 genotypes
        should have one gene more and ~ 333 genotypes should have gen less
        and ~ 333 genotypes should have one gene replaced by another one.
        :return:
        """
        genes = ["snow", "second_layer",
                 "third_layer", "river", "first_out", "first_river",
                 "first_third", "second_third", "second_river", "third_river"]
        len_before = len(genes)
        count_add = 0
        count_del = 0
        count_swap = 0
        reputations = 1000
        for i in range(reputations):
            genes_copy = copy.deepcopy(genes)
            genes_copy = generator.mutate(genes_copy, self.gene_set,
                                          generator.get_fitness)
            if len(genes_copy) > len_before + 1:
                count_add += 1
            elif len(genes_copy) < len_before - 1:
                count_del += 1
            elif len(genes_copy) == len_before:
                count_swap += 1
        print("Added: {}\tDeleted:{}\tSwapped:{}\n\n".format(count_add,
                                                         count_del,
                                                         count_swap))
        self.assertTrue(math.isclose(count_add, len_before,
                                     abs_tol=reputations * 0.05)
                        and
                        math.isclose(count_del, len_before,
                                     abs_tol=reputations * 0.05)
                        and
                        math.isclose(count_swap, len_before,
                                     abs_tol=reputations * 0.05)
                        )


    def test_check_for_connection_outlet_present(self):
        """
        Tests if the the function check_for_connection can detect that an
        outlet is missing and then add it.
        :return: None
        """
        genes = ["snow", "river"]
        generator.check_for_connection(genes)
        self.assertTrue("tr_first_out" in genes and len(genes) == 3)

    def test_check_for_connection_outlet_not_present(self):
        """
        Tests if the the function check_for_connection can detect that an
        outlet is present and leave the genes unchanged.
        :return: None
        """
        genes = ["snow", "river", "tr_first_out"]
        genes_copy = genes[:]
        generator.check_for_connection(genes)
        self.assertTrue(genes == genes_copy)

    def test_crossover(self):
        pass

    def test_create(self):
        pass

    def test_write_best_model(self):
        pass




def load_data(fnQ, fnT, fnP, area_catchment):
    """
    Loads climata and discharge data from the corresponding files fnQ, fnT and
    fnP
    """
    # Fixed model starting point
    begin = datetime.datetime(1979, 1, 1)
    step = datetime.timedelta(days=1)
    # empty time series
    P = cmf.timeseries(begin, step)
    with open(fnP) as fnP_file:
        P.extend(float(Pstr) for Pstr in fnP_file)
    Q = cmf.timeseries(begin, step)
    with open(fnQ) as fnQ_file:
        Q.extend(float(Qstr) for Qstr in fnQ_file)
    # Convert m3/s to mm/day
    Q *= 86400 * 1e3 / (area_catchment * 1e6)
    T = cmf.timeseries(begin, step)
    Tmin = cmf.timeseries(begin, step)
    Tmax = cmf.timeseries(begin, step)

    # Go through all lines in the file
    with open(fnT) as fnT_file:
        for line in fnT_file:
            columns = line.split('\t')
            if len(columns) == 3:
                Tmax.add(float(columns[0]))
                Tmin.add(float(columns[1]))
                T.add(float(columns[2]))

    return P, T, Tmin, Tmax, Q
