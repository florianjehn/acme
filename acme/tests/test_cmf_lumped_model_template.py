# -*- coding: utf-8 -*-
"""
Created on Nov 17 13:00 2017
@author(s): Florian U. Jehn
"""
import unittest
from acme.cmf_model_generators import create_lumped_CMF_model as generator
from acme.cmf_model_generators import lumped_CMF_model_template as template
import copy
import utilities_for_tests as utils
import datetime
import spotpy
import acme.cmf_model_generators.cmf_descriptor as descriptor


class GeneratorsTemplate(unittest.TestCase):
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

    @staticmethod
    def test_model_parametrization():
        """
        Tests whether the maximal model can be initialized.

        :return: parametrized model, ready to run
        """
        print("\n test_template_parametrization")

        # Initialize data and genome
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
        begin_calibration = datetime.datetime(1980, 1, 1)
        end_calibration = datetime.datetime(1981, 12, 31)
        begin_validation = datetime.datetime(1982, 1, 1)
        end_validation = datetime.datetime(1983, 12, 31)

        # Initialize model
        model = template.LumpedModelCMF(genes, data, begin_calibration,
                                        end_calibration, begin_validation,
                                        end_validation)

        # Initialize parameter values
        params = template.LumpedModelCMF.create_params_from_genes(genes)
        parameters = spotpy.parameter.generate(params)
        param_vector = []
        for param in parameters:
            param_vector.append(param[0])
        paramdict = dict((pp.name, v) for pp, v in zip(params,
                                                       param_vector))
        # Initialize model with parameter values
        model.setparameters(paramdict)
        return model

    def test_template_equal_to_benchmark(self):
        """
        Tests if the hashes created from the cmf description of the
        benchmark model equals the one created by.

        :return: None
        """
        print("\n Test equal description")
        # Create readily parametrized models
        benchmark = utils.model_setup()
        acme_model = GeneratorsTemplate.test_model_parametrization()

        # Open files
        benchmark_file = open("bench_file.txt", "w")
        acme_file = open("acme_file.txt", "w")

        # Give all things to the descriptor
        descriptor.describe(benchmark.project, benchmark_file)
        descriptor.describe(acme_model.project, acme_file)

        # Create hashes
        acme_hash = utils.hashing("acme_file.txt")
        bench_hash = utils.hashing("bench_file.txt")

        # Compare, should be equal
        self.assertTrue(acme_hash == bench_hash)


if __name__ == '__main__':
    unittest.main()
