# -*- coding: utf-8 -*-
"""
Created on Nov 08 09:18 2017
@author(s): Florian U. Jehn, Philipp Kraft
Describes a cmf model with storages, connections, cells, forcing data,
outlets and so forth.
"""
import cmf

def _describe_timeseries(ts: cmf.timeseries):
    """
    Describes a cmf timeseries with its start, end, step, min, mean and max.
    
    :param: ts: a cmf.timeseries
    :return: None
    """
    if ts:
        return ('{count} values from {start:%Y-%m-%d} to {end:%Y-%m-%d} step {step}, min/mean/max  {min:0.5g} / {mean:0.5g} / {max:0.5g}'
                .format(count=len(ts),
                        start=ts.begin.AsPython(),
                        end=ts.end.AsPython(),
                        step=ts.step,
                        min=ts.min(),
                        mean=ts.mean(),
                        max=ts.max()
                        )
                )
    else:
        return '~' # With no data in the timeseries return the YAML-NULL symbol
    

def _describe_node(indentlevel, node, write):
    write(indentlevel, '- {}'.format(node))
    for connection in node.connections:
        write(indentlevel + 1, '- {}'.format(connection))


def _describe_cell(cell, write):
    write(1, '- {}:'.format(cell))
    for storage in cell.storages:
        _describe_node(2, storage, write)


def _describe_meteo(meteo, write):
    write(1, '- {}:'.format(meteo))
    for var_name, timeseries in meteo.TimeseriesDictionary().items():
        write(2, '{}: {}'.format(var_name, _describe_timeseries(timeseries)))

def _describe_rain(rainstation, write):
    write(1, '- {} ({:0.2f}mm/year)'.format(rainstation.name, rainstation.data.mean()*365))
    

  
def describe(project: cmf.project, out):
    """
    Describes a cmf project in a file like object.
    :param project: cmf project
    :param out: filelike object
    :return: None
    """
    def write(indentlevel=0, text=''):
        """
        Helper function to write output to the out stream with identation
        """
        out.write('    ' * indentlevel + text + '\n')
    
    write(0, '{}'.format(project))
    write()

    write(0, 'Project nodes:')
    for node in project.nodes:
        _describe_node(1, node, write)
    write()

    write(0, 'Cells:')
    for cell in project:
        _describe_cell(cell, write)
    write()

    write(0, 'Meteo Stations:')
    for meteo in project.meteo_stations:
        _describe_meteo(meteo, write)
    write()

    write(0, 'Rain Stations:')
    for rain in project.rainfall_stations:
        _describe_rain(rain, write)
