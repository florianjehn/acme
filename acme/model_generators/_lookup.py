# -*- coding: utf-8 -*-
"""
Created on Aug 16 12:52 2017
@author(s): Florian U. Jehn

This delivers back the functions specified by user.
"""
import spotpy


def get_obj_func(obj_func):
    """
    Returns the objective function as specified by obj_func.

    :param obj_func: Name of objective function
    :return: spotpy objective function
    """
    if obj_func == "bias":
        return spotpy.objectivefunctions.bias
    elif obj_func == "pbias":
        return spotpy.objectivefunctions.pbias
    elif obj_func == "nashsutcliffe":
        return spotpy.objectivefunctions.nashsutcliffe
    elif obj_func == "lognashsutcliffe":
        return spotpy.objectivefunctions.lognashsutcliffe
    elif obj_func == "log_p":
        return spotpy.objectivefunctions.log_p
    elif obj_func == "correlationcoefficient":
        return spotpy.objectivefunctions.correlationcoefficient
    elif obj_func == "rsquared":
        return spotpy.objectivefunctions.rsquared
    elif obj_func == "mse":
        return spotpy.objectivefunctions.mse
    elif obj_func == "rmse":
        return spotpy.objectivefunctions.rmse
    elif obj_func == "mae":
        return spotpy.objectivefunctions.mae
    elif obj_func == "rrmse":
        return spotpy.objectivefunctions.rrmse
    elif obj_func == "agreementindex":
        return spotpy.objectivefunctions.agreementindex
    elif obj_func == "covariance":
        return spotpy.objectivefunctions.covariance
    elif obj_func == "decomposed_mse":
        return spotpy.objectivefunctions.decomposed_mse
    elif obj_func == "kge":
        return spotpy.objectivefunctions.kge
    else:
        raise NameError("No such objective function in spotpy")
    
    
def get_spotpy_algorithm(algorithm):
    """
    Returns the algorithm as specified by algorithm (variable)


    :param algorithm: 
    :return: 
    """
    if algorithm == "abc":
        return spotpy.algorithms.abc
    elif algorithm == "demcz":
        return spotpy.algorithms.demcz
    elif algorithm == "dream":
        return spotpy.algorithms.dream
