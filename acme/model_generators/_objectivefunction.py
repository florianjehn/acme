# -*- coding: utf-8 -*-
"""
Created on Aug 16 12:52 2017
@author(s): Florian U. Jehn

This delivers back the spotpy objective function as specified by user
"""
import spotpy


def get_obj_func(name):
    """
    Returns the objective function as specified by name.

    :param name: Name of objective function
    :return: spotpy objective function
    """
    if name == "bias":
        return spotpy.objectivefunctions.bias
    elif name == "pbias":
        return spotpy.objectivefunctions.pbias
    elif name == "nashsutcliffe":
        return spotpy.objectivefunctions.nashsutcliffe
    elif name == "lognashsutcliffe":
        return spotpy.objectivefunctions.lognashsutcliffe
    elif name == "log_p":
        return spotpy.objectivefunctions.log_p
    elif name == "correlationcoefficient":
        return spotpy.objectivefunctions.correlationcoefficient
    elif name == "rsquared":
        return spotpy.objectivefunctions.rsquared
    elif name == "mse":
        return spotpy.objectivefunctions.mse
    elif name == "rmse":
        return spotpy.objectivefunctions.rmse
    elif name == "mae":
        return spotpy.objectivefunctions.mae
    elif name == "rrmse":
        return spotpy.objectivefunctions.rrmse
    elif name == "agreementindex":
        return spotpy.objectivefunctions.agreementindex
    elif name == "covariance":
        return spotpy.objectivefunctions.covariance
    elif name == "decomposed_mse":
        return spotpy.objectivefunctions.decomposed_mse
    elif name == "kge":
        return spotpy.objectivefunctions.kge
    else:
        raise NameError("No such objective function in spotpy")
