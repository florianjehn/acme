# -*- coding: utf-8 -*-
"""
Created on Nov 20 12:40 2017
@author(s): Florian U. Jehn
"""

import unittest
import acme.cmf_model_generators.cmf_descriptor as descriptor
import utilities_for_tests as utils
import os


class DescriptorTest(unittest.TestCase):
    filename = "description.txt"

    def test_descriptor_file_format(self):
        """
        Tests if the cmf descriptor is saves the model in the right format
        by comparing the hash values.

        :return: None
        """
        benchmark_model_hash = "e81aa320023afc769c4f2dbd707cbc32"
        self.test_descriptor_writing(delete=False)
        current_hash = utils.hashing(DescriptorTest.filename)
        print(current_hash)
        # Find the directory of the file to be able to delete it
        filepath = os.path.abspath(__file__)
        directoy_name = os.path.dirname(filepath)
        os.chdir(directoy_name)
        os.remove(DescriptorTest.filename)
        print("Hash to compare to is     " + benchmark_model_hash)
        print("Currently created hash is " + current_hash)
        self.assertTrue(benchmark_model_hash == current_hash)

    @staticmethod
    def test_descriptor_writing(delete=True):
        """
        Tests if the cmf descriptor is able to write to a file without an
        error message.

        :param: delete: if True delete file after test
        :return: None
        """
        model = utils.model_setup()
        # model.runmodel(verbose=True)
        with open(DescriptorTest.filename, "w") as file:
            descriptor.describe(model.project, file)
            print("Finished writing file")

        if delete:
            filepath = os.path.abspath(__file__)
            directoy_name = os.path.dirname(filepath)
            os.chdir(directoy_name)
            os.remove(DescriptorTest.filename)


if __name__ == '__main__':
    unittest.main()
