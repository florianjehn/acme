# -*- coding: utf-8 -*-
"""
Created on Okt 17 14:25 2017
@author(s): Florian U. Jehn


Model which mimics the maximal layout of the ACME Template, to test wether this model works.
"""
import datetime
import spotpy
import numpy as np
import cmf
from spotpy.parameter import Uniform as param
import os


class LumpedModelCMF:
    def __init__(self):
        self.params = [param("tr_first_out", 0.,300),
                       param("tr_first_river", 0., 300),
                       param("tr_first_second", 0., 300),
                       param("tr_second_third", 0., 300),
                       param("tr_second_river", 0., 300),
                       param("tr_third_river", 0., 300),
                       param("tr_river_out", 0., 300),
                       param("beta_first_out", 0., 4),
                       param("beta_first_river", 0., 4),
                       param("beta_first_second", 0., 4),
                       param("beta_second_river", 0., 4),
                       param("beta_second_third", 0., 4),
                       param("beta_third_river", 0., 4),
                       param("beta_river_out", 0., 4),
                       param("canopy_lai", 1., 14),
                       param("canopy_closure", 0., 1.0),
                       param("snow_meltrate", 0.1, 15.),
                       param("snow_melt_temp", -5.0, 5.0),
                       param("V0_first_out", 0., 200),
                       param("V0_first_river", 0., 200),
                       param("V0_first_second", 0., 200),
                       param("ETV0", 0, 200),
                       param("fETV0", 0., 0.85)
                       ]

        P, T, Tmin, Tmax, Q = load_data("observed_discharge.txt", "temperature_max_min_avg.txt", "precipitation.txt", 2976.41)
        self.Q = Q
        cmf.set_parallel_threads(1)
        self.project = cmf.project()
        project = self.project
        cell = project.NewCell(0,0,0, 1000)

        cell.add_storage("Snow", "S")
        cmf.Snowfall(cell.snow, cell)

        cell.add_layer(2.0)
        cell.add_layer(5.0)
        cell.add_layer(10.0)

        cmf.HargreaveET(cell.layers[0], cell.transpiration)

        self.outlet = project.NewOutlet("outlet", 10,0,0)

        self.make_stations(P, T, Tmin, Tmax)

        self.river = cell.add_storage("River", "R")
        self.canopy = cell.add_storage("Canopy", "C")

        self.begin = datetime.datetime(1979, 1,1)
        self.end = datetime.datetime(1986,12, 31)

    def setparameters(self,tr_first_out,
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
        sets the parameters, all parameterized connections will be created anew
        """
        # Get all definitions from init method
        p = self.project
        cell = p[0]
        first = cell.layers[0]
        second = cell.layers[1]
        third = cell.layers[2]

        river = self.river

        canopy = self.canopy

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

        cmf.kinematic_wave(second, third, tr_second_third, exponent=beta_second_third)

        cmf.kinematic_wave(third, river, tr_third_river, exponent=beta_third_river)

        cmf.kinematic_wave(river, out, tr_river_out, exponent=beta_river_out)

        # set snowmelt temperature
        cmf.Weather.set_snow_threshold(snow_melt_temp)
        # Snowmelt at the surfaces
        snowmelt_surf = cmf.SimpleTindexSnowMelt(cell.snow,
                                                 cell.surfacewater, cell,
                                                 rate=snow_meltrate)

        # Splits the rainfall in interzeption and throughfall
        cmf.Rainfall(cell.canopy, cell, False, True)
        cmf.Rainfall(cell.surfacewater, cell, True, False)
        # Makes a overflow for the interception storage
        cmf.RutterInterception(cell.canopy, cell.surfacewater, cell)
        # Transpiration on the plants is added
        cmf.CanopyStorageEvaporation(cell.canopy, cell.evaporation, cell)
        # Sets the parameters for the interception
        cell.vegetation.LAI = canopy_lai
        # Defines how much throughfall there is (in %)
        cell.vegetation.CanopyClosure = canopy_closure


    def make_stations(self, P, T, Tmin, Tmax):
        """
        Creates the rainfall and the climate stations
        P = time series precipitation
        T, Tmin, Tmax = time series of mean temperatur, min and max
        """
        rainstation = self.project.rainfall_stations.add('Grebenau avg', P,
                                                         (0, 0, 0))
        self.project.use_nearest_rainfall()

        # Temperature data
        meteo = self.project.meteo_stations.add_station('Grebenau avg',
                                                        (0, 0, 0))
        meteo.T = T
        meteo.Tmin = Tmin
        meteo.Tmax = Tmax
        self.project.use_nearest_meteo()

        return rainstation

    def runmodel(self, verbose=False):
        """
        starts the model
        if verboose = True --> give something out for every day
        """
        try:
            # Creates a solver for the differential equations
            # solver = cmf.ImplicitEuler(self.project,1e-8)
            solver = cmf.CVodeIntegrator(self.project, 1e-8)
            # usually the CVodeIntegrator computes the jakobi matrix only
            # partially to save computation time. But in models with low spatial
            # complexity this leads to a longer computational time
            # therefore the jakob matrix is computed completely to speed things up
            # this is done by LinearSolver = 0
            solver.LinearSolver = 0
            c = self.project[0]
            solver.max_step = cmf.h

            # New time series for model results (res - result)
            resQ = cmf.timeseries(self.begin, cmf.day)
            # starts the solver and calculates the daily time steps
            end = self.end


            for t in solver.run(self.project.meteo_stations[0].T.begin, end,
                                cmf.day):
                # Fill the results
                if t >= self.begin:
                    resQ.add(self.outlet.waterbalance(t))


            # Return the filled result time series
            return resQ
        except RuntimeError:
            return np.array(self.Q[self.begin:self.end + datetime.timedelta(
                days=1)]) * np.nan

    def simulation(self, vector):
        """
        SpotPy expects a method simulation. This methods calls setparameters
        and runmodels, so SpotPy is satisfied
        """

        paramdict = dict((pp.name, v) for pp, v in zip(self.params, vector))
        self.setparameters(**paramdict)
        resQ = self.runmodel()
        return np.array(resQ)

    def evaluation(self):
        """
        For Spotpy
        """
        return np.array(
            self.Q[self.begin:self.end + datetime.timedelta(days=1)])

    def parameters(self):
        """
        For Spotpy
        """
        return spotpy.parameter.generate(self.params)

    def objectivefunction(self, simulation, evaluation):
        """
        For Spotpy
        """
        return spotpy.objectivefunctions.nashsutcliffe(evaluation, simulation)


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
    from spotpy.algorithms import dream as Sampler

    parallel = 'mpi' if 'OMPI_COMM_WORLD_SIZE' in os.environ else 'seq'


    model = LumpedModelCMF()
    sampler = Sampler(model, parallel=parallel)
    sampler.sample(500)
