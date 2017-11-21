# -*- coding: utf-8 -*-
"""
Created on Aug 17 09:04 2017
@author(s): Florian U. Jehn

This template is called from the generator to be used as basis for all
models which are generated during the evolutionary process. Also the class is
the interface to spotpy.
"""

import datetime
import spotpy
import numpy as np
import cmf
import acme.tests.get_storages_fluxes as get_storages_and_fluxes
import acme.cmf_model_generators.spotpy_interface as spotpy_interface


class LumpedModelCMF(spotpy_interface.SpotpyInterface):
    def __init__(self, genes, data,
                 begin_calibration, end_calibration,
                 begin_validation, end_validation):
        """
        Sets up the base model in regard to the genes provided.

        :param genes: active genome that is to be tested
        :param data: dictionary of all data needed for a run
        :param begin_calibration: start date of the calibration period
        :param end_calibration: end date of the calibration period
        :param begin_validation: start date of the validation period
        :param end_validation: end date of the validation period
        """
        # Main things
        self.genes = genes
        self.data = data

        # Date stuff
        self.begin_calibration = begin_calibration
        self.end_calibration = end_calibration
        self.begin_validation = begin_validation
        self.end_validation = end_validation

        # Create params list
        self.params = self.create_params_from_genes(self.genes)

        def basic_model_setup():
            """
            Creates the basic layout needed for every model structure.

            :return: None
            """
            # Basic Layout, same for all possible models
            prec = data["prec"]
            obs_discharge = data["discharge"]
            t_mean = data["t_mean"]
            t_min = data["t_min"]
            t_max = data["t_max"]
            self.obs_discharge = obs_discharge

            # Use only one core (quicker for smaller models)
            cmf.set_parallel_threads(1)

            # Generate a project with one cell for a lumped model
            self.project = cmf.project()
            project = self.project

            # Add one cell, which will include all other parts. The area is set
            # to 1000 m², so the units are easier to understand
            cell = project.NewCell(0, 0, 0, 1000)

            # Add a first layer, this one is always present, as a model with no
            # layers makes no sense
            first_layer = cell.add_layer(2.0)

            # Add an evapotranspiration
            cmf.HargreaveET(first_layer, cell.transpiration)

            # Create the CMF meteo and rain stations
            self.make_stations(prec, t_mean, t_min, t_max)

            # Create an outlet
            self.outlet = project.NewOutlet("outlet", 10, 0, 0)

        basic_model_setup()

        def create_storages():
            """
            Creates all storages that are present in the genome.

            :return: None
            """
            cell = self.project[0]
            # Make a dictionary to lookup the different storages
            self.storages = {"first": cell.layers[0], "out": self.outlet}

            # Now create all storages which are depended on the genes provided
            if "snow" in self.genes:
                self.snow = cell.add_storage("Snow", "S")
                cmf.Snowfall(cell.snow, cell)
                self.storages["snow"] = self.snow

            if "canopy" in self.genes:
                self.canopy = cell.add_storage("Canopy", "C")
                self.storages["canopy"] = self.canopy

            if "second" in self.genes:
                self.storages["second"] = cell.add_layer(5.0)

            if "third" in self.genes:
                self.storages["third"] = cell.add_layer(10.0)

            # Always create the river, but connect it later with a waterbalance
            # connection to the outlet if it does not exist in the genes. This
            # makes an easier connection with the other
            self.river = cell.add_storage("River", "R")
            self.storages["river"] = self.river

        create_storages()

    @staticmethod
    def create_params_from_genes(genes):
        """
        Creates the param list, which is needed for SPOTPY. It is static
        so it can be tested without creating an template instance.
        :return: params list
        """
        params = []
        distribution = spotpy.parameter.Uniform
        # ET Params always included
        # ETV1 = Under this volume the potential ET is reduced by the factor
        # fETV0
        params.append(distribution("ETV1", 0., 200.))
        params.append(distribution("fETV0", 0., 0.5))

        # Create all the other parameters if they exist.
        for gene in genes:
            # tr = transition time
            if "tr_" in gene:
                params.append(distribution(gene, 0., 300.))
            # Exponent to scale the kinematic wave
            elif "beta" in gene:
                params.append(distribution(gene, 0., 4.))
            # Rate in which the snow melts
            elif "snow_meltrate" in gene:
                params.append(distribution(gene, 0.1, 15.))
            # Temperature at which the snow melts
            elif "snow_melt_temp" in gene:
                params.append(distribution(gene, -5.0, 5.0))
            # Field capacity like feature
            elif "v0" in gene:
                params.append(distribution(gene, 0., 200))
            # Closure of the canopy
            elif "canopy_closure" in gene:
                params.append(distribution(gene, 0., 1.0))
            # Leaf area index
            elif "canopy_lai" in gene:
                params.append(distribution(gene, 1., 14.))

        return params

    def setparameters(self, param_dict: dict):
        """
        Creates all connections with the parameter values produced by the
        sampling algorithm.

        :param param_dict: Dictionary of all the parameters and their values.
        :return None
        """
        cell = self.project[0]
        storages = self.storages

        def find_active_connections():
            active_connections = []
            for param in param_dict.keys():
                if "tr_" in param:
                    active_connections.append(param)
            return active_connections

        def create_connections(active_connections):
            """
            Createas an kinematic wave conncetion and pulls the right
            parameters values from the param_dict
            :return:
            """
            # Go through all active connections
            for connection in active_connections:
                temp, source_tr, target_tr = connection.split("_")

                # Save the parameter values to be able to create the connection
                connection_params = {"tr": param_dict[connection],
                                     # Include the default values for beta and
                                     # V0, so a kinematic wave can always be
                                     # created.
                                     "beta": 1.0,
                                     "V0": 1.0}

                # Find all other parameter which belong to that connection
                for param in param_dict.keys():
                    try:
                        name, source_param, target_param = param.split("_")
                        # Save the values
                        if ((name == "beta" or name == "V0")
                            and
                                source_tr == source_param
                            and
                                target_tr == target_param):

                            connection_params[name] = param_dict[param]

                    except ValueError:
                        # ValueError is raised because the not all genes can be
                        # split in three parts. But as all genes that are of
                        # interest now can be, the error can pass.
                        pass

                # Create the connection
                cmf.kinematic_wave(storages[source_tr],
                                   storages[target_tr],
                                   param_dict[connection],
                                   V0=connection_params["V0"],
                                   exponent=connection_params["beta"])

        def create_snow():
            # Fill in the snow parameters when they exist. If not
            # leave them at CMFs default value.
            if "snow" in self.genes:
                cmf.SimpleTindexSnowMelt(cell.snow, cell.surfacewater, cell,
                                         rate=param_dict.get("snow_meltrate",
                                                             7))
                cmf.Weather.set_snow_threshold(param_dict.get("snow_melt_temp",
                                                              0.5))

        def create_canopy():
            # Fill in the canopy parameters when they exist
            if "canopy" in self.genes:
                # Splits the rainfall in interception and throughfall
                cmf.Rainfall(cell.canopy, cell, False, True)
                cmf.Rainfall(cell.surfacewater, cell, True, False)
                # Makes a overflow for the interception storage
                cmf.RutterInterception(cell.canopy, cell.surfacewater, cell)
                # Transpiration on the plants is added
                cmf.CanopyStorageEvaporation(cell.canopy, cell.evaporation,
                                             cell)

                # Set LAI and Canopy Closure if they exist in the dict. If not
                # leave them at CMFs default value.
                cell.vegetation.LAI = param_dict.get("canopy_lai", 2.88)
                cell.vegetation.CanopyClosure = param_dict.get(
                    "canopy_closure", 1.0)

        def shortcircuit_river():
            """
            Establish a waterbalance_connection if the river does not exist as
            a separate storage, so the model treats it as if it would not
            exist.

            :return: None
            """
            if "river" not in self.genes:
                cmf.waterbalance_connection(self.storages["river"],
                                            self.storages["out"])

        create_connections(find_active_connections())
        create_snow()
        create_canopy()
        shortcircuit_river()

    def make_stations(self, prec, temp, temp_min, temp_max):
        """
        Creates the cmf weather stations
        """
        rainstation = self.project.rainfall_stations.add("Rainfall Station",
                                                         prec, (0, 0, 0))
        self.project.use_nearest_rainfall()

        # Temperature data
        meteo = self.project.meteo_stations.add_station('Meteo Station',
                                                        (0, 0, 0))
        meteo.T = temp
        meteo.Tmin = temp_min
        meteo.Tmax = temp_max
        self.project.use_nearest_meteo()
        return rainstation

    def run_model(self, verbose = True):
        """
        Starts the model. Used by spotpy
        """
        cell = self.project[0]
        try:
            # Create a solver for differential equations
            solver = cmf.CVodeIntegrator(self.project, 1e-8)

            # New time series for model results
            resQ = cmf.timeseries(self.begin_calibration, cmf.day)
            # starts the solver and calculates the daily time steps
            end = self.end_validation
            for t in solver.run(self.project.meteo_stations[0].T.begin, end,
                                cmf.day):
                # Fill the results (first year is included but not used to
                # calculate the NS)
                if verbose:
                    print(t)
                    print("storages")
                    storages = get_storages_and_fluxes.storages_of_cell(
                        cell.rain_source, cell)
                    fluxes = get_storages_and_fluxes.flux_of_all_nodes_of_cell(
                        cell.rain_source, cell, t)
                    fluxes = \
                        get_storages_and_fluxes.convert_fluxes_for_fluxogram(
                            fluxes)
                    print(storages)
                    print("Fluxes")
                    print(fluxes)
                    print("\n")
                if t >= self.begin_calibration:
                    resQ.add(self.outlet.waterbalance(t))
            return resQ
        # Return an nan - array when a runtime error occurs
        except RuntimeError:
            print("Runtime Error")
            return np.array(self.obs_discharge[
                            self.begin_calibration:self.end_validation +
                            datetime.timedelta(days=1)])*np.nan

    def objectivefunction(self, simulation, evaluation):
        """
        For Spotpy. Tells Spotpy how the model is to be evaluated.
        """
        simulation_calib = simulation[
                           self.begin_validation: self.end_validation]
        # Todo: Hier noch hydrological signatures?
        return spotpy.objectivefunctions.nashsutcliffe(evaluation,
                                                       simulation_calib)
