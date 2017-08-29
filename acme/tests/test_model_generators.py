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
import math
import os

# Only import cmf if the test is run on windows, so Travis does not try to
# import a non existing thing
if os.name == "nt":
    import cmf


class GeneratorsTests(unittest.TestCase):
    gene_set = ["snow", "canopy", "second_layer",
                "third_layer", "river", "first_out", "first_river",
                "first_third", "second_third", "second_river",
                "third_river", "meltrate", "snow_melt_temp", "lai",
                "canopy_closure", "etv0", "fetv0", "beta_first_out",
                "beta_first_river", "beta_first_second",
                "beta_second_river", "beta_second_third",
                "beta_third_river", "beta_river_out"]

    def test_solve(self):
        # Only run when not on travis
        if os.name == "nt":
            area_catchment = 2976.41
            discharge_file = "GrebenauQTagMittel__1979_1990.txt"
            temperature_file = "Temp_max_min_avg_1979_1988.txt"
            precipitation_file = "Prec_Grebenau_1979_1988.txt"
            P, T, Tmin, Tmax, Q = load_data(discharge_file, temperature_file,
                                            precipitation_file, area_catchment)

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
        else:
            pass

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

    def test_crossover_list_properties(self):
        """
        Tests if the returned value of crossover is a non empty list.
        :return: None
        """
        first_parent = ["snow", "second_layer", "canopy"]
        second_parent = ["snow", "canopy", "third_layer", "second_layer"]
        child = generator.crossover(first_parent, second_parent)
        self.assertTrue(len(child) > 0 and isinstance(child, list))

    def test_crossover_no_duplicates(self):
        """
        Tests that the crossover method does not allow duplicates in the
        genotype.
        :return: None
        """
        first_parent = ["snow", "second_layer", "canopy"]
        second_parent = ["snow", "canopy", "third_layer", "second_layer"]
        child = generator.crossover(first_parent, second_parent)
        self.assertTrue(len(child) == len(set(child)))

    def test_create(self):
        pass

    def test_write_best_model(self):
        pass


def load_data(discharge_file, temperature_file, precipitation_file, area_catchment):
    """
    Loads climata and discharge data from the corresponding files
    discharge_file, temperature_file and precipitation_file
    """
    # Only run when not on Travis
    if os.name == "nt":
        # Fixed model starting point
        begin = datetime.datetime(1979, 1, 1)
        step = datetime.timedelta(days=1)
        # empty time series
        precipitation = cmf.timeseries(begin, step)
        with open(precipitation_file) as precipitation_file_file:
            precipitation.extend(float(precipitation_str) for
                                 precipitation_str in
                                 precipitation_file_file)
        discharge = cmf.timeseries(begin, step)
        with open(discharge_file) as discharge_file_file:
            discharge.extend(float(discharge_str) for discharge_str in
                             discharge_file_file)
        # Convert m3/s to mm/day
        discharge *= 86400 * 1e3 / (area_catchment * 1e6)
        temperature_avg = cmf.timeseries(begin, step)
        temperature_min = cmf.timeseries(begin, step)
        temperature_max = cmf.timeseries(begin, step)

        # Go through all lines in the file
        with open(temperature_file) as temperature_file_file:
            for line in temperature_file_file:
                columns = line.split('\t')
                if len(columns) == 3:
                    temperature_max.add(float(columns[0]))
                    temperature_min.add(float(columns[1]))
                    temperature_avg.add(float(columns[2]))

        return precipitation, temperature_avg, temperature_min,\
            temperature_max, discharge
    else:
        pass



if __name__ == '__main__':
    unittest.main()