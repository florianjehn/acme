# -*- coding: utf-8 -*-
"""
Created on Aug 17 09:04 2017
@author(s): Florian U. Jehn

This template is called from the generator to be used as basis for all
models which are generated during the evolutionary process. Also the class is
the interface to spotpy.
"""
import datetime
import cmf
import spotpy
import os
import numpy as np
from dateutil.relativedelta import relativedelta


class LumpedModelCMF:
    def __init__(self, genotype, area_catchment, obj_func=None):
        """

        :param genotype:
        """
        if obj_func is None:
            obj_func = _lookup.get_obj_func("nashsutcliffe")
        self.genotype_to_structure(genotype)
        self.objective_function = obj_func
        self.area_catchment = area_catchment

        def basic_layout():
            pass

        def set_storages():
            pass






    def setparameters(self, tr, Vr=0.0, V0=1000., beta=1.0, ETV1=500.,
                      fETV0=0.0, initVol=100.):
        """
        Creates all connections with the parameter values produced by the
        sampling algorithm.
        """
        # Import all
        c = self.project[0]
        outlet = self.outlet

        def all_layers():
            pass

        def second_and_third_layer():
            pass

        def first_and_third_layer():
            pass

        def first_and_second_layer():
            pass

        def only_first_layer():
            pass

        def only_second_layer():
            pass

        def only_third_layer():
            pass

        # Setze den Water-Uptakestress
        c.set_uptakestress(cmf.VolumeStress(ETV1, ETV1 * fETV0))
        cmf.kinematic_wave(c.layers[0], outlet, tr / V0, exponent=beta,
                           residual=Vr, V0=V0)
        c.layers[0].volume = initVol
        # TODO: Anpassen an ACME


    def loadPETQ(self):
        """
        Loads climata and discharge data from the corresponding files fnQ,
        fnT and fnP
        """
        # Fixed model starting point
        # Change this if you want a warm up period other than a year
        begin = self.begin - relativedelta(years=1)
        step = datetime.timedelta(days=1)
        # empty time series
        prec = cmf.timeseries(begin, step)
        prec.extend(float(Pstr.strip("\n")) for Pstr in open(fnP))

        discharge = cmf.timeseries(begin, step)
        discharge.extend(float(Qstr.strip("\n")) for Qstr in open(fnQ))
        # Convert m3/s to mm/day
        area_catchment = 562.41  # Change this when catchment changes!!!
        discharge *= 86400 * 1e3 / (area_catchment * 1e6)
        temp = cmf.timeseries(begin, step)
        temp_min = cmf.timeseries(begin, step)
        temp_max = cmf.timeseries(begin, step)

        # Go through all lines in the file
        for line in open(fnT):
            columns = line.strip("\n").split('\t')
            if len(columns) == 3:
                temp_max.add(float(columns[0]))
                temp_min.add(float(columns[1]))
                temp.add(float(columns[2]))

        return prec, temp, temp_min, temp_max, discharge


    def make_stations(self, prec, temp, temp_min, temp_max):
        """
        Creates the cmf weather stations
        """
        rainstation = self.project.rainfall_stations.add("Rainfall Station",
                                                         prec, (0, 0, 0))
        self.project.use_nearest_rainfall()

        # Temperature data
        meteo = self.project.meteo_stations.add_station('Meteo Station', (0,
                                                                          0,
                                                                          0))
        meteo.T = temp
        meteo.Tmin = temp_min
        meteo.Tmax = temp_max
        self.project.use_nearest_meteo()
        return rainstation

        return rainstation
    # TODO: Anpassen an ACME


    def runmodel(self):
        """
        Starts the model. Used by spotpy
        """

        try:
            # Create a solver for differential equations
            solver = cmf.CVodeIntegrator(self.project, 1e-8)

            # New time series for model results
            resQ = cmf.timeseries(self.begin, cmf.day)
            # starts the solver and calculates the daily time steps
            end = self.end
            for t in solver.run(self.project.meteo_stations[0].T.begin, end,
                                cmf.day):
                # Fill the results (first year is included but not used to
                # calculate the NS)
                if t >= self.begin:
                    resQ.add(self.outlet.waterbalance(t))
            return resQ
        # Return an nan - array when a runtime error occurs
        except RuntimeError:
            return np.array(self.Q[
                            self.begin:self.end + datetime.timedelta(
                                days=1)])*np.nan

    def test_run(self):
        """
        Stars the model one time to determine if there is a connection to
        the outlet, by recursively cycling through all nodes.
        :return:
        """
        pass


    def evaluation(self):
        """
        For Spotpy. Creates a numpy array from the evaluation timeseries.
        """
        return np.array(
            self.Q[self.begin:self.end + datetime.timedelta(days=1)])

    def parameters(self):
        """
        For Spotpy. Tells Spotpy the parameter names and ranges.
        """
        return spotpy.parameter.generate(self.params)

    def objectivefunction(self, simulation, evaluation):
        """
        For Spotpy. Tells Spotpy how the model is to be evaluated.
        """
        return self.objective_function(evaluation, simulation)
