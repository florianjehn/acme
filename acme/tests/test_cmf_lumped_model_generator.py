# -*- coding: utf-8 -*-
"""
Created on Aug 17 14:17 2017
@author(s): Florian U. Jehn
"""
import unittest
from acme.cmf_model_generators import create_lumped_CMF_model as generator
import acme.genetics as genetics
import datetime
import math
import acme.tests.utilities_for_tests as utils



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
        print("\n test_get_fitness")
        genes = generator.LumpedCMFGenerator.gene_set
        precipitation, temperature_avg, temperature_min, \
            temperature_max, discharge = utils.load_data(
                "observed_discharge.txt",
                "temperature_max_min_avg.txt",
                "precipitation.txt",
                2976.41
            )
        data = {
            "prec": precipitation,
            "discharge": discharge,
            "t_mean": temperature_avg,
            "t_min": temperature_min,
            "t_max": temperature_max
        }

        fitness = generator.get_fitness(genes, data,
                                        # start and end dates for
                                        # calibration and validation
                                        datetime.datetime(1980, 1, 1),
                                        datetime.datetime(1981, 12, 31),
                                        datetime.datetime(1982, 1, 1),
                                        datetime.datetime(1983, 12, 31))
        # Todo: Enter the right fitness value here for DREAM
        self.assertTrue(fitness > -1)

    @staticmethod
    def test_display():
        """
        Calls the display function with one test set to determine if it works
        at all. Cannot determine if the output is as expected.
        This has to checked manually.
        """
        start_time = datetime.datetime.now() - datetime.timedelta(0, 3)
        candidate = genetics.genetic.Chromosome(
            ["snow", "second", "tr_first_out"], 0.8,
            genetics.genetic.Strategies.create)
        print("\n test_display")
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
        print("\n test_mutation")
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
        genes = None
        for i in range(repetitions):
            genes = generator.create()
            if len(genes) > 0:
                not_empty += 1
        print("\n test_create_returns_not_empty_list_most_of_time")
        print("not_empty = {}".format(not_empty))
        self.assertTrue(isinstance(genes, list) and not_empty > 900)

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
            print("\n test_create_all_possible_genes")
            print("The following genes were in genes and not in "
                  "gene_set: {}".format(set(genes) - set(self.gene_set)))
            print("The following genes were in gene_set, but not in genes: "
                  "{}".format(set(self.gene_set) - set(genes)))
            self.assertTrue(False)

    @staticmethod
    def test_write_all_models():
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
        generator.write_all_models(test=True)
        # Delete them again, to not cause trouble when the program itself runs
        del models_so_far[model_1_str]
        del models_so_far[model_2_str]


if __name__ == '__main__':
    unittest.main()
