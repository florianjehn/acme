# -*- coding: utf-8 -*-
"""
Created on Aug 16 12:52 2017
@author(s): Florian U. Jehn

This delivers back the functions specified by user.
"""
import spotpy
import cmf


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
    elif obj_func == "rsr":
        return spotpy.objectivefunctions.rsr
    else:
        raise NameError("No such objective function in spotpy")
    
    
def get_algorithm(algorithm):
    """
    Returns the algorithm as specified by algorithm (variable)

    :param algorithm: Name of the algorithm
    :return: spotpy algorithm
    """
    if algorithm == "abc":
        return spotpy.algorithms.abc
    elif algorithm == "demcz":
        return spotpy.algorithms.demcz
    elif algorithm == "dream":
        return spotpy.algorithms.dream
    elif algorithm == "fast":
        return spotpy.algorithms.fast
    elif algorithm == "fscabc":
        return spotpy.algorithms.fscabc
    elif algorithm == "lhs":
        return spotpy.algorithms.lhs
    elif algorithm == "mc":
        return spotpy.algorithms.mc
    elif algorithm == "mcmc":
        return spotpy.algorithms.mcmc
    elif algorithm == "mle":
        return spotpy.algorithms.mle
    elif algorithm == "rope":
        return spotpy.algorithms.rope
    elif algorithm == "sa":
        return spotpy.algorithms.sa
    elif algorithm == "sceua":
        return spotpy.algorithms.sceua
    else:
        raise NameError("No such algorithm in spotpy")


def get_distribution(distribution):
    """
    Returns the distribution as specified by distribution (variable)

    :param distribution: Name of the distribution
    :return: spotpy distribution
    """
    if distribution == "Uniform":
        return spotpy.parameter.Uniform
    elif distribution == "Normal":
        return spotpy.parameter.Normal
    elif distribution == "logNormal":
        return spotpy.parameter.logNormal
    elif distribution == "Chisquare":
        return spotpy.parameter.Chisquare
    elif distribution == "Exponential":
        return spotpy.parameter.Exponential
    elif distribution == "Gamma":
        return spotpy.parameter.Gamma
    elif distribution == "Wald":
        return spotpy.parameter.Wald
    elif distribution == "Weibull":
        return spotpy.parameter.Weibull
    else:
        raise NameError("No such distribution in spotpy")


def get_evapotranspiration(et):
    """
    Returns the method of calculation of the evapotranspiration as specified
    in "et".

    :param et: name of the evapotranspiration method
    :return: cmf evapotranspiration method
    """
    if et == "Hargreave":
        return cmf.HargreaveET
    elif et == "PenmanMonteith":
        return cmf.PenmanMonteithET
    elif et == "PriestleyTaylor":
        return cmf.PriestleyTaylorET
    elif et == "Turc":
        return cmf.TurcET
    else:
        raise NameError("No such evapotranspiration in CMF")
