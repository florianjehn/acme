# -*- coding: utf-8 -*-
"""
Created on Nov 20 12:40 2017
@author(s): Florian U. Jehn
"""

import unittest
import acme.cmf_model_generators.cmf_descriptor as descriptor
import acme.tests.benchmark_model as benchmark_model
import spotpy


class DescriptorTest(unittest.TestCase):
    @staticmethod
    def test_descriptor_writing():
        """
        Tests if the cmf descriptor is able to write to a file.

        :return: None
        """
        # Create an instance of the model
        model = benchmark_model.LumpedModelCMF()

        # Create the spotpy parameters objects
        parameters = spotpy.parameter.generate(model.Params)
        # Fill the parameter vector with the randomly generated values for
        # the parameters
        param_vector = []
        for param in parameters:
            param_vector.append(param[0])
        paramdict = dict((pp.name, v) for pp, v in zip(model.Params,
                                                       param_vector))

        # Run setparameters, so the model is complete and can be descriped.
        model.setparameters(**paramdict)
        # model.runmodel(verbose=True)
        with open("description.txt", "w") as file:
            descriptor.describe(model.project, file)


    def test_descriptor_file_format(self):
        """
        Tests if the cmf descriptor is saves the model in the right format
        :return:
        """
        pass