# -*- coding: utf-8 -*-
"""
Created on Aug 17 14:17 2017
@author(s): Florian U. Jehn
"""
import unittest
from acme.model_generators import create_lumped_CMF_model as generator
import acme.genetics as genetics
import cmf
import datetime

class generators_tests(unittest.TestCase):
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
        Calls the display function with one test set to determine if it works at all. Cannot determine if the output is as expected. This has to checked manually.
        """
        start_time = datetime.datetime.now() - datetime.timedelta(0,3)
        candidate = genetics.genetic.Chromosome(["snow", "first_layer"], 0.8, genetics.genetic.Strategies.create)
        generator.display(candidate, start_time)

    def test_mutation(self):
        pass

    def test_crossover(self):
        pass

    def test_create(self):
        pass

    def test_write_best_model(self):
        pass




def load_data(fnQ, fnT, fnP, area_catchment):
    """
    Loads climata and discharge data from the corresponding files fnQ, fnT and fnP
    """
    # Fixed model starting point
    begin = datetime.datetime(1979, 1, 1)
    step = datetime.timedelta(days=1)
    # empty time series
    P = cmf.timeseries(begin, step)
    P.extend(float(Pstr) for Pstr in open(fnP))

    Q = cmf.timeseries(begin, step)
    Q.extend(float(Qstr) for Qstr in open(fnQ))
    # Convert m3/s to mm/day
    Q *= 86400 * 1e3 / (area_catchment * 1e6)
    T = cmf.timeseries(begin, step)
    Tmin = cmf.timeseries(begin, step)
    Tmax = cmf.timeseries(begin, step)

    # Go through all lines in the file
    for line in open(fnT):
        columns = line.split('\t')
        if len(columns) == 3:
            Tmax.add(float(columns[0]))
            Tmin.add(float(columns[1]))
            T.add(float(columns[2]))

    return P, T, Tmin, Tmax, Q
