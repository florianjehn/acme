# -*- coding: utf-8 -*-
"""
Created on Aug 17 09:04 2017
@author(s): Florian U. Jehn

This template is called from the generator to be used as basis for all
models which are generated during the evolutionary process. Also the class is
the interface to spotpy.
"""

import datetime
import os
import spotpy
import numpy as np
# Exclude CMF to allow Travis testing
if os.name == "nt":
    import cmf


class LumpedModelCMF:
    def __init__(self, genes, data, obj_func, distribution,
                 begin_calibration, end_calibration,
                 begin_validation, end_validation):
        """
        Sets up the base model in regard to the genes provided.

        :param genes:
        :param data:
        :param obj_func:
        :param distribution:
        :param begin_calibration:
        :param end_calibration:
        :param begin_validation:
        :param end_validation:
        :param possible_params: A dictionary with all possible different
        params for this model and what storage they are related too
        """
        # Main things
        self.obj_func = obj_func
        self.genes = genes
        self.data = data
        self.distribution = distribution

        # Date stuff
        self.begin_calibration = begin_calibration
        self.end_calibration = end_calibration
        self.begin_validation = begin_validation
        self.end_validation = end_validation

        # Create params list
        self.params = self.create_params_from_genes(self.genes,
                                                    self.distribution)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Basic Layout, same for all possible models
        prec = data["prec"]
        discharge = data["discharge"]
        t_mean = data["t_mean"]
        t_min = data["t_min"]
        t_max = data["t_max"]
        self.discharge = discharge

        # Use only one core (quicker for smaller models)
        cmf.set_parallel_threads(1)

        # Generate a project with one cell for a lumped model
        self.project = cmf.project()
        p = self.project

        # Add one cell, which will include all other parts. The area is set
        # to 1000 m², so the units are easier to understand
        c = p.NewCell(0, 0, 0, 1000)

        # Add a first layer, this one is always present, as a model with no
        # layers makes no sense
        first_layer = c.add_layer(2.0)

        # Add an evapotranspiration
        cmf.HargreaveET(first_layer, c.transpiration)

        # Create the CMF meteo and rain stations
        self.make_stations(prec, t_mean, t_min, t_max)

        # Create an outlet
        self.outlet = p.NewOutlet("outlet", 10, 0, 0)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Now create all storages which are depended on the genes provided
        if "snow" in self.genes:
            c.add_storage("snow", "s")
            cmf.Snowfall(c.snow, c)

        if "canopy" in self.genes:
            c.add_storage("canopy", "c")

        if "second_layer" in self.genes:
            c.add_layer(5.0)

        if "third_layer" in self.genes:
            c.add_layer(10.0)

        if "river" in self.genes:
            c.add_storage("river", "r")

    @staticmethod
    def create_params_from_genes(genes, distribution):
        """
        Creates the param list, which is needed for SPOTPY. It is static
        so it can be tested without creating an template instance.
        :return: params list
        """
        params = []
        # ET Params always included
        # ETV1 = Under this volume the potential ET is reduced by the factor
        # fETV0
        params.append(distribution("ETV1", 0., 200.))
        params.append(distribution("fETV0", 0., 0.5))

        # Determine which storages exists:
        river = "river" in genes
        second_layer = "second_layer" in genes
        third_layer = "third_layer" in genes

        # Allow the creation of the different parameters depending on the
        # existence of the different storages

        # All layers and the river exist
        if second_layer and third_layer and river:
            # Add transition times
            if "tr_first_out" in genes:
                params.append(distribution("tr_first_out", 0., 300.))

            if "tr_first_river" in genes and "river" in genes:
                params.append(distribution("tr_first_river", 0., 300.))

            if "tr_first_second" in genes and "second_layer" in genes:
                params.append(distribution("tr_first_second", 0., 300.))

            if "tr_second_third" in genes:
                params.append(distribution("tr_second_third", 0., 300.))

            if "tr_second_river" in genes:
                params.append(distribution("tr_second_river", 0., 300.))

            if "tr_third_river" in genes:
                params.append(distribution("tr_third_river", 0., 300.))

            # The river tr is added by default.
            params.append(distribution("tr_river_out", 0., 300.))

            # Add betas
            if "beta_first_out" in genes:
                params.append(distribution("beta_first_out", 0., 4.))

            if "beta_first_river" in genes:
                params.append(distribution("beta_first_river", 0., 4.))

            if "beta_first_second" in genes:
                params.append(distribution("beta_first_second", 0., 4.))

            if "beta_second_river" in genes:
                params.append(distribution("beta_second_river", 0., 4.))

            if "beta_second_third" in genes:
                params.append(distribution("beta_second_third", 0., 4.))

            if "beta_third_river" in genes:
                params.append(distribution("beta_third_river", 0., 4.))

            if "beta_river_out" in genes:
                params.append(distribution("beta_river_out", 0., 4.))



        # All layers, but not the river exis
        elif second_layer and third_layer and not river:
            pass
        # The second or third layer exist (which one does not matter,
        # as it will result in a two storage model either way)
        # and the river exists too
        elif (second_layer or third_layer) and river:
            pass
        # The second or the third layer exist but not the river
        elif (second_layer or third_layer) and not river:
            pass
        # Only one layer and the river exist
        elif not second_layer and not third_layer and river:
            pass
        # Only one layer exists
        elif not second_layer and not third_layer and not river:
            pass






        # Add Snow paramters
        if "meltrate" in genes:
            params.append(distribution("meltrate", 0., 15.))

        if "snow_melt_temp" in genes:
            params.append(distribution("snow_melt_temp", -5.0, 5.0))

        # Add


        return params


    def setparameters(self, **kwargs):
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

    def run_model(self):
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

    def simulation(self, vector):
        """
        SpotPy expects a method simulation. This methods calls setparameters
        and runmodels, so SpotPy is satisfied.
        """
        paramdict = dict((pp.name, v) for pp, v in zip(self.params, vector))
        self.setparameters(**paramdict)
        sim_discharge = self.run_model()
        return np.array(sim_discharge)

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
