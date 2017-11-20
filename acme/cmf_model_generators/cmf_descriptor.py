# -*- coding: utf-8 -*-
"""
Created on Nov 08 09:18 2017
@author(s): Florian U. Jehn, Philipp Kraft

Describes a cmf model with storages, connections, cells, forcing data,
outlets and so forth.
"""
import cmf


def describe(project: cmf.project, out):
    """
    Describes a cmf project in a file like object.

    :param project: cmf project
    :param out: filelike object
    :return: None
    """
    out.write('{}\n'.format(project))

    out.write("\nDescription of Cells\n")
    for cell in project:
        out.write('\t- {}:\n'.format(cell))
        for storage in cell.storages:
            out.write('\t\t- {}\n'.format(storage))
            for connection in storage.connections:
                out.write('\t\t\t- {}\n'.format(connection))

    out.write("\nDescription of Meteo Stations\n")

    # ### Is there a smarter way to do this?
    # Definition of all possible timeseries in meteo station
    variables = ["T", "Tmax", "Tmin", "Tground", "Windspeed", "rHmean",
                 "rHmin", "rHmax", "Tdew", "Sunshine", "Rs", "T_lapse"]

    for meteo in project.meteo_stations:
        out.write("\t- {}:\n".format(meteo))
        for timeseries in variables:
            timeseries_object = eval("meteo." + timeseries)
            out.write("\t\t- {}\n".format(timeseries_object))
            # Breaks if the timeseries does not exist. Therefore try; except
            try:
                mean_val = timeseries_object.mean()
                min_val = timeseries_object.min()
                max_val = timeseries_object.max()
            except IndexError:
                mean_val = "NA"
                min_val = "NA"
                max_val = "NA"

            out.write("\t\t\t- Mean: {}\tMin: {}\tMax: {}\n".format(
                mean_val, min_val, max_val
            ))

    out.write("\nDescription of Rain Stations\n")
    for rain in project.rainfall_stations:
        out.write("\t- {}:\n".format(rain))

    out.write("\nDescription of Outlets\n")
    for outlet in project.nodes:
        out.write("\t- {}:\n".format(outlet))


