# -*- coding: utf-8 -*-
"""
Created on Nov 17 12:58 2017
@author(s): Florian U. Jehn
"""
import unittest
from acme.cmf_model_generators import create_lumped_CMF_model as generator
import acme.cmf_model_generators.genome_arrange as genome_arrange


class GeneratorsTests(unittest.TestCase):
    def test_check_for_connection_outlet_present(self):
        """
        Tests if the the function check_for_connection can detect that an
        outlet is missing and then add it.
        :return: None
        """
        genes = ["snow", "river"]
        genome_arrange.check_for_connection(
            genes,
            generator.LumpedCMFGenerator.connections)
        self.assertTrue("tr_first_out" in genes and len(genes) == 3)

    def test_check_for_connection_outlet_not_present(self):
        """
        Tests if the the function check_for_connection can detect that an
        outlet is present and leave the genes unchanged.
        :return: None
        """
        genes = ["snow", "river", "tr_first_out"]
        genes_copy = genes[:]
        genome_arrange.check_for_connection(
            genes,
            generator.LumpedCMFGenerator.connections)
        self.assertTrue(genes == genes_copy)

    def test_del_inactive_params_1(self):
        """
        Tests if only the inactive genes are deleted.

        :return: None
        """
        genes = ["snow", "snow_meltrate", "tr_first_out", "first",
                 "tr_second_out"]
        genes_copy = genome_arrange.del_inactive_params(
            genes,
            generator.LumpedCMFGenerator.storages)

        # From this test set tr_second_out should be deleted. All other
        # connections should remain.
        print("\n test_del_inactive_params")
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

    def test_del_inactive_params_2(self):
        """
        Tests if inactive params are deleted correctly.

        :return: None
        """
        genes = ["tr_first_out", "tr_second_out", "beta_first_out"]
        genes = genome_arrange.del_inactive_params(
            genes,
            generator.LumpedCMFGenerator.storages)
        self.assertTrue(set(genes) == {"tr_first_out", "beta_first_out"})

    def test_del_inactive_storages(self):
        """
        Tests if incative storages are deleted correctly.

        :return: None
        """
        genes = ["tr_first_out", "tr_second_out", "beta_first_out", "third",
                 "second"]
        genes = genome_arrange.del_inactive_storages(
            genes,
            generator.LumpedCMFGenerator.storages)
        self.assertTrue(set(genes) == {"tr_first_out", "tr_second_out",
                                       "beta_first_out"})

    def test_find_active_genes(self):
        """
        Tests if the Method is correctly finding the active genes and return
        them.

        :return: None
        """
        genes = ["snow", "snow_meltrate", "canopy_closure", "second",
                 "tr_second_out", "tr_first_second", "third", "tr_third_river"]
        active_genes = genome_arrange.find_active_genes(
            genes, generator.LumpedCMFGenerator.storages)
        right_solution = ["snow", "snow_meltrate", "second",
                          "tr_second_out", "tr_first_second", "first"]

        print("\n test_active_genes")
        print("Start genes = " + str(genes))
        print("Active genes = " + str(active_genes))
        print("Right solution = " + str(right_solution))

        self.assertTrue(len(active_genes) < len(genes)
                        and
                        len(active_genes) == len(right_solution)
                        and
                        set(active_genes) == set(right_solution))

if __name__ == '__main__':
    unittest.main()
