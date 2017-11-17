# -*- coding: utf-8 -*-
"""
Created on Okt 17 14:25 2017
@author(s): Florian U. Jehn


Model which mimics the maximal layout of the ACME Template, to test whether 
this model works.
"""
import datetime
import spotpy
import numpy as np
import cmf
from spotpy.parameter import Uniform as Param
import os


class LumpedModelCMF:
    def __init__(self):
        self.Params = [Param("tr_first_out", 0., 300),
                       Param("tr_first_river", 0., 300),
                       Param("tr_first_second", 0., 300),
                       Param("tr_second_third", 0., 300),
                       Param("tr_second_river", 0., 300),
                       Param("tr_third_river", 0., 300),
                       Param("tr_river_out", 0., 300),
                       Param("beta_first_out", 0., 4),
                       Param("beta_first_river", 0., 4),
                       Param("beta_first_second", 0., 4),
                       Param("beta_second_river", 0., 4),
                       Param("beta_second_third", 0., 4),
                       Param("beta_third_river", 0., 4),
                       Param("beta_river_out", 0., 4),
                       Param("canopy_lai", 1., 14),
                       Param("canopy_closure", 0., 1.0),
                       Param("snow_meltrate", 0.1, 15.),
                       Param("snow_melt_temp", -5.0, 5.0),
                       Param("V0_first_out", 0., 200),
                       Param("V0_first_river", 0., 200),
                       Param("V0_first_second", 0., 200),
                       Param("ETV0", 0, 200),
                       Param("fETV0", 0., 0.85)
                       ]

        prec, temp, temp_min, temp_max, q = load_data(
            "observed_discharge.txt", "temperature_max_min_avg.txt", 
            "precipitation.txt", 2976.41)
        self.Q = q
        cmf.set_parallel_threads(1)
        self.project = cmf.project()
        project = self.project
        cell = project.NewCell(0, 0, 0, 1000)

        cell.add_storage("Snow", "S")
        cmf.Snowfall(cell.snow, cell)

        cell.add_layer(2.0)
        cell.add_layer(5.0)
        cell.add_layer(10.0)

        cmf.HargreaveET(cell.layers[0], cell.transpiration)

        self.outlet = project.NewOutlet("outlet", 10, 0, 0)

        self.make_stations(prec, temp, temp_min, temp_max)

        self.river = cell.add_storage("River", "R")
        self.canopy = cell.add_storage("Canopy", "C")

        self.begin = datetime.datetime(1979, 1, 1)
        self.end = datetime.datetime(1986, 12, 31)

    def setparameters(self,
                      tr_first_out,
                      tr_first_river,
                      tr_first_second,
                      tr_second_third,
                      tr_second_river,
                      tr_third_river,
                      tr_river_out,
                      beta_first_out,
                      beta_first_river,
                      beta_first_second,
                      beta_second_river,
                      beta_second_third,
                      beta_third_river,
                      beta_river_out,
                      canopy_lai,
                      canopy_closure,
                      snow_meltrate,
                      snow_melt_temp,
                      V0_first_out,
                      V0_first_river,
                      V0_first_second,
                      ETV0,
                      fETV0):
        """
        sets the Parameters, all Parametrized connections will be created anew
        """
        # Get all definitions from init method
        p = self.project
        cell = p[0]
        first = cell.layers[0]
        second = cell.layers[1]
        third = cell.layers[2]

        river = self.river

        out = self.outlet

        # Adjustment of the evapotranspiration
        cell.set_uptakestress(cmf.VolumeStress(ETV0, ETV0 * fETV0))

        # Kinematic waves
        cmf.kinematic_wave(first, second, tr_first_second,
                           exponent=beta_first_second, V0=V0_first_second)
        cmf.kinematic_wave(first, out, tr_first_out,
                           exponent=beta_first_out, V0=V0_first_out)
        cmf.kinematic_wave(first, river, tr_first_river,
                           exponent=beta_first_river, V0=V0_first_river)

        cmf.kinematic_wave(second, river, tr_second_river,
                           exponent=beta_second_river)

        cmf.kinematic_wave(second, third, tr_second_third, 
                           exponent=beta_second_third)

        cmf.kinematic_wave(third, river, tr_third_river, 
                           exponent=beta_third_river)

        cmf.kinematic_wave(river, out, tr_river_out, 
                           exponent=beta_river_out)

        # set snowmelt temperature
        cmf.Weather.set_snow_threshold(snow_melt_temp)
        # Snowmelt at the surfaces
        cmf.SimpleTindexSnowMelt(cell.snow,
                                 cell.surfacewater, cell,
                                 rate=snow_meltrate)

        # Splits the rainfall in interception and throughfall
        cmf.Rainfall(cell.canopy, cell, False, True)
        cmf.Rainfall(cell.surfacewater, cell, True, False)
        # Makes a overflow for the interception storage
        cmf.RutterInterception(cell.canopy, cell.surfacewater, cell)
        # Transpiration on the plants is added
        cmf.CanopyStorageEvaporation(cell.canopy, cell.evaporation, cell)
        # Sets the Parameters for the interception
        cell.vegetation.LAI = canopy_lai
        # Defines how much throughfall there is (in %)
        cell.vegetation.CanopyClosure = canopy_closure

    def make_stations(self, prec, temp_avg, temp_min, temp_max):
        """
        Creates the rainfall and the climate stations
        P = time series precipitation
        T, Tmin, Tmax = time series of mean temperatur, min and max
        """
        rainstation = self.project.rainfall_stations.add('Grebenau avg', prec,
                                                         (0, 0, 0))
        self.project.use_nearest_rainfall()

        # Temperature data
        meteo = self.project.meteo_stations.add_station('Grebenau avg',
                                                        (0, 0, 0))
        meteo.T = temp_avg
        meteo.Tmin = temp_min
        meteo.Tmax = temp_max
        self.project.use_nearest_meteo()

        return rainstation

    def runmodel(self, verbose=False):
        """
        starts the model
        if verboose = True --> give something out for every day
        """
        try:
            # Creates a solver for the differential equations
            solver = cmf.CVodeIntegrator(self.project, 1e-8)
            solver.LinearSolver = 0
            solver.max_step = cmf.h

            # New time series for model results (res - result)
            sim_dis = cmf.timeseries(self.begin, cmf.day)
            # starts the solver and calculates the daily time steps
            end = self.end

            for t in solver.run(self.project.meteo_stations[0].T.begin, end,
                                cmf.day):
                # Fill the results
                if t >= self.begin:
                    sim_dis.add(self.outlet.waterbalance(t))

            # Return the filled result time series
            return sim_dis
        except RuntimeError:
            return np.array(self.Q[self.begin:self.end + datetime.timedelta(
                days=1)]) * np.nan

    def simulation(self, vector):
        """
        SpotPy expects a method simulation. This methods calls setParameters
        and runmodel, so SpotPy is satisfied
        """

        paramdict = dict((pp.name, v) for pp, v in zip(self.Params, vector))
        self.setparameters(**paramdict)
        sim_dis = self.runmodel()
        return np.array(sim_dis)

    def evaluation(self):
        """
        For Spotpy
        """
        return np.array(
            self.Q[self.begin:self.end])

    def parameters(self):
        """
        For Spotpy
        """
        return spotpy.parameter.generate(self.Params)
    
    @staticmethod
    def objectivefunction(simulation, evaluation):
        """
        For Spotpy
        """
        print(len(evaluation))
        print(len(simulation))
        return spotpy.objectivefunctions.nashsutcliffe(evaluation,
                                                       simulation)


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
    from spotpy.algorithms import dream as sampler

    parallel = 'mpi' if 'OMPI_COMM_WORLD_SIZE' in os.environ else 'seq'

    model = LumpedModelCMF()

    # par = model.parameters()['optguess']
    # sim = model.simulation(par)
    # evalu = model.evaluation()
    # like = model.objectivefunction(sim, evalu)
    # print(like)
    # print(evalu)
    # print(sim)
    sampler = sampler(model, parallel=parallel, dbname="bench.csv",
                      dbformat="csv")
    sampler.sample(300)
