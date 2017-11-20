# -*- coding: utf-8 -*-
"""
Created on Nov 17 13:00 2017
@author(s): Florian U. Jehn
"""
import unittest
from acme.cmf_model_generators import create_lumped_CMF_model as generator
from acme.cmf_model_generators import lumped_CMF_model_template as template
import copy


class GeneratorsTests(unittest.TestCase):
    def test_create_params_from_genes(self):
        """
        Tests if the method create_params_from_genes from the CMF lumped
        model template creates the param list correctly.
        """
        genes = copy.deepcopy(generator.LumpedCMFGenerator.gene_set)
        params = (template.LumpedModelCMF.
                  create_params_from_genes(genes))

        params_names = []
        for param in params:
            if param.name != "ETV1" and param.name != "fETV0":
                params_names.append(param.name)

        # Exclude the storages and add the ET parameters
        genes = set(genes).difference(set(copy.deepcopy(
            generator.LumpedCMFGenerator.storages)))

        print("\n test_create_params_from_genes")
        print("Genes = " + str(genes) + " \nLaenge = " + str(len(genes)))
        print("Parameter Names = " + str(params_names) + " \nLaenge = " + str(
            len(params_names)))

        self.assertTrue(len(params_names) == len(genes)
                        and
                        # Check if the param is created as an
                        # distribution object
                        params[0].optguess is not None
                        and
                        # Both sets should be the same if all worked well
                        genes == set(params_names))

if __name__ == '__main__':
    unittest.main()
