# -*- coding: utf-8 -*-
"""
Created on Nov 21 13:17 2017
@author(s): Florian U. Jehn

Contains all functions which are used for tests but do not test themselve
"""

import hashlib
import acme.tests.benchmark_model as benchmark_model
import spotpy
import cmf
import os
import datetime


def hashing(file):
    """

    :param file: filelike object
    :return: Hash of the filelike object
    """
    curfile = open(file, "rb")
    hasher = hashlib.md5()
    buf = curfile.read()
    hasher.update(buf)
    hash = hasher.hexdigest()
    print(hash)
    return hash


def model_setup():
    """
    Sets up the benchmark model and returns it.

    :return: Benchmark model with setparameters already invoked
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

    # Run setparameters, so the model is complete and can be described.
    model.setparameters(**paramdict)
    return model


def load_data(discharge_file, temperature_file, precipitation_file,
              area_catchment):
    """
    Loads climata and discharge data from the corresponding files
    discharge_file, temperature_file and precipitation_file
    """

    # Fixed model starting point
    begin = datetime.datetime(1979, 1, 1)
    step = datetime.timedelta(days=1)
    # empty time series
    precipitation = cmf.timeseries(begin, step)
    if os.name == "nt":
        cwd = os.getcwd() + os.sep
    else:
        cwd = os.getcwd() + os.sep + "acme" + os.sep + "tests" + os.sep
    print("Current Working Directory = " + cwd)
    with open(cwd + precipitation_file) as precipitation_file_file:
        precipitation.extend(float(precipitation_str) for
                             precipitation_str in
                             precipitation_file_file)
    discharge = cmf.timeseries(begin, step)
    with open(cwd + discharge_file) as discharge_file_file:
        discharge.extend(float(discharge_str) for discharge_str in
                         discharge_file_file)
    # Convert m3/s to mm/day
    discharge *= 86400 * 1e3 / (area_catchment * 1e6)
    temperature_avg = cmf.timeseries(begin, step)
    temperature_min = cmf.timeseries(begin, step)
    temperature_max = cmf.timeseries(begin, step)

    # Go through all lines in the file
    with open(cwd + temperature_file) as temperature_file_file:
        for line in temperature_file_file:
            columns = line.split('\t')
            if len(columns) == 3:
                temperature_max.add(float(columns[0]))
                temperature_min.add(float(columns[1]))
                temperature_avg.add(float(columns[2]))

    return precipitation, temperature_avg, temperature_min,\
        temperature_max, discharge


if __name__ == '__main__':
    hashing("description.txt")
