# -*- coding: utf-8 -*-
"""
Created on Aug 15 13:28 2017
@author(s): Florian U. Jehn

This file is used to start the construction of a predefined CMF model. The
user only has to provide the forcing data and the kind of techniques (
crossover, mutation, objective function).

The structure is created in such a way, that there is always at least one
connection to the outlet.
"""
import acme.model_generators._lumped_CMF_model_template as template
import acme.model_generators._lookup as lookup
import acme.genetics.genetic as genetic
import datetime


class LumpedCMFGenerator:
    def __init__(self):
        pass

