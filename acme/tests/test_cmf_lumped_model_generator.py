# -*- coding: utf-8 -*-
"""
Created on Aug 17 14:17 2017
@author(s): Florian U. Jehn
"""
import unittest
from acme.model_generators import create_lumped_CMF_model as generator
from acme.model_generators import _lumped_CMF_model_template as template
import acme.genetics as genetics
import datetime
import copy
import math
import os
import acme.model_generators._lookup as lookup


# Only import cmf if the test is run on windows, so Travis does not try to
# import a non existing thing
if os.name == "nt":
    import cmf


class GeneratorsTests(unittest.TestCase):
    gene_set = generator.LumpedCMFGenerator.gene_set

    def test_solve(self):
        # # Only run when not on travis
        # if os.name == "nt":
        #     area_catchment = 2976.41
        #     discharge_file = "GrebenauQTagMittel__1979_1990.txt"
        #     temperature_file = "Temp_max_min_avg_1979_1988.txt"
        #     precipitation_file = "Prec_Grebenau_1979_1988.txt"
        #     P, T, Tmin, Tmax, Q = load_data(discharge_file, temperature_file,
        #                                   precipitation_file, area_catchment)
        #
        #     lumped_model_generator = generator.LumpedCMFGenerator(
        #         1980,
        #         1982,
        #         1,
        #         "nashsutcliffe",
        #         0.5,
        #         "Uniform",
        #         "dream",
        #         "Hargreave",
        #         P,
        #         Q,
        #         T,
        #         Tmin,
        #         Tmax,
        #         )
        #     lumped_model_generator.solve()
        # else:
        #     pass
        # Outcommented for now. Will be reinstalled once everything else works
        pass

    def test_get_fitness(self):
        """
        Calls the get_fitness function with a mockup model setup, which
        contains all possible genes. To test if it runs correctly.

        :return: None
        """
        # Exclude from Travis.
        if os.name == "nt":
            genes = generator.LumpedCMFGenerator.gene_set
            precipitation, temperature_avg, temperature_min, \
            temperature_max, discharge = load_data(
                "GrebenauQTagMittel__1979_1990.txt",
                "Temp_max_min_avg_1979_1988.txt",
                "Prec_Grebenau_1979_1988.txt",
                2976.41
            )
            data = {
                "prec": precipitation,
                "discharge": discharge,
                "t_mean": temperature_avg,
                "t_min": temperature_min,
                "t_max": temperature_max
            }
            obj_func = "nashsutcliffe"
            obj_func = lookup.get_obj_func(obj_func)
            algorithm = "dream"
            algorithm = lookup.get_algorithm(algorithm)
            distribution = "Uniform"
            distribution = lookup.get_distribution(distribution)
            fitness = generator.get_fitness(genes, data, obj_func, algorithm,
                                            distribution,
                                            # start and end dates for
                                            # calibration and validation
                                            datetime.datetime(1980, 1, 1),
                                            datetime.datetime(1981, 12, 31),
                                            datetime.datetime(1982, 1, 1),
                                            datetime.datetime(1983, 12, 31))
            self.assertTrue(fitness > 0)
        else:
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
        Calls the mutation function for 1000 times. After that ~ 3333 genotypes
        should have one gene more and ~ 3333 genotypes should have gen less
        and ~ 3333 genotypes should have one gene replaced by another one.
        :return:
        """
        genes = ["snow", "second_layer",
                 "third_layer", "river", "first_out", "first_river",
                 "first_third", "second_third", "second_river", "third_river"]
        len_before = len(genes)
        count_add = 0
        count_del = 0
        count_swap = 0
        repetitions = 10000
        fraction = repetitions / 3
        for i in range(repetitions):
            genes_copy = genes[:]
            generator.mutate(genes_copy, self.gene_set)
            if len(genes_copy) > len_before:
                count_add += 1
            elif len(genes_copy) < len_before:
                count_del += 1
            elif len(genes_copy) == len_before:
                count_swap += 1
        print("Added: {}\tDeleted:{}\tSwapped:{}\n\n".format(count_add,
                                                             count_del,
                                                             count_swap))
        self.assertTrue(math.isclose(count_add, fraction,
                                     abs_tol=repetitions * 0.05)
                        and
                        math.isclose(count_del, fraction,
                                     abs_tol=repetitions * 0.05)
                        and
                        math.isclose(count_swap, fraction,
                                     abs_tol=repetitions * 0.05)
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

    def test_create_returns_non_empty_list_most_of_time(self):
        """
        Tests if the create method returns a non empty list of genes most of
        the time. Sometimes is ok as  this represents the most simple model.

        :return: None
        """
        repetitions = 1000
        not_empty = 0
        for i in range(repetitions):
            genes = generator.create()
            if len(genes) > 0:
                not_empty += 1
        print("not_empty = {}".format(not_empty))
        self.assertTrue(isinstance(genes, list) and not_empty > 900)

    def test_create_params_from_genes(self):
        """
        Tests if the method create_params_from_genes from the CMF lumped
        model template creates the param list correctly.
        """
        genes = generator.LumpedCMFGenerator.gene_set
        params = (template.LumpedModelCMF.
                  create_params_from_genes(genes, lookup.get_distribution(
                                                                 "Uniform")))

        params_names = []
        for param in params:
            if param.name != "ETV1" and param.name != "fETV0":
                params_names.append(param.name)

        self.assertTrue(len(params) == len(genes)
                        and
                        # Check if the param is created as an
                        # distribution object
                        params[0].optguess is not None
                        and
                        # Both sets should be the same if all worked well
                        set(genes) == set(params_names))

    def test_create_all_possible_genes_present(self):
        """
        Calls create() with the test variable, which triggers all control
        flows to be true. Thus creating a model with all possible genes.
        This should equal the gene_set.

        :return: None
        """
        genes = generator.create(test=True)
        if set(genes) == set(self.gene_set):
            self.assertTrue(True)
        else:
            print("The following genes were in genes and not in "
                  "gene_set: {}".format(set(genes) - set(self.gene_set)))
            print("The following genes were in gene_set, but not in genes: "
                  "{}".format(set(self.gene_set) - set(genes)))
            self.assertTrue(False)

    def test_del_params_without_storage(self):
        """
        Tests if only the inactive genes are deleted.

        :return: None
        """
        genes = ["snow", "snow_meltrate", "tr_first_out", "first",
                 "tr_second_out"]
        genes_copy = generator.del_params_without_storage(genes)

        # From this test set tr_second_out should be deleted. All other
        # connections should remain.
        print("genes is {}".format(genes))
        print("genes_copy is {}".format(genes_copy))
        self.assertTrue("snow" in genes_copy
                        and
                        "snow_meltrate" in genes_copy
                        and
                        "tr_first_out" in genes_copy
                        and
                        "first" in genes_copy
                        and
                        "tr_second_out" not in genes_copy
                        )

    def test_write_all_models(self):
        """
        Tests if a file is written by calling the method write_all_models.

        :return: None
        """
        model_1 = ["snow", "second", "beta_second_river"]
        model_1_str = " ".join(model_1)
        model_1_like = 0.78
        model_2 = ["canopy", "third"]
        model_2_str = " ".join(model_2)
        model_2_like = 0.71
        models_so_far = generator.LumpedCMFGenerator.models_so_far
        models_so_far[model_1_str] = model_1_like
        models_so_far[model_2_str] = model_2_like
        generator.write_all_models()
        # Delete them again, to not cause trouble when the program itself runs
        del models_so_far[model_1_str]
        del models_so_far[model_2_str]


def load_data(discharge_file, temperature_file, precipitation_file,
              area_catchment):
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
