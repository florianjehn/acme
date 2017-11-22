# -*- coding: utf-8 -*-
"""
Created on Nov 22 13:13 2017
@author(s): Florian U. Jehn

Creates and returns the weather stations and everything neccessary around them
"""


def make_stations(project, prec, temp, temp_min, temp_max):
    """
    Creates the cmf weather stations
    """
    # Rain
    rainstation = project.rainfall_stations.add("Rainfall Station",
                                                prec, (0, 0, 0))
    project.use_nearest_rainfall()

    # All other meteorological data
    meteo = project.meteo_stations.add_station('Meteo Station',
                                               (0, 0, 0))
    meteo.T = temp
    meteo.Tmin = temp_min
    meteo.Tmax = temp_max
    project.use_nearest_meteo()
    return rainstation
