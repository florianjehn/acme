# -*- coding: utf-8 -*-
"""
Created on Nov 08 09:18 2017
@author(s): Florian U. Jehn

Describes a cmf model with storages, connections, cells, forcing data,
outlets and so forth.
"""
import io
import cmf


def describe(project: cmf.project, out):
    """
    Describes a cmf project in a file like object.

    :param project: cmf project
    :param out: filelike object
    :return: None
    """
    out.write('{}\n'.format(project))
    # Meteo & Rain station beschreiben - für jede Timeseries start, anzahl,
    # mittelwert
    # Outlets for o in project.nodes
    for c in project:
        out.write(f'{c}:\n')
        for stor in c.storages:
            out.write(f' - {stor}\n')
            for con in stor.connections:
                out.write(f'     - {con}\n')

