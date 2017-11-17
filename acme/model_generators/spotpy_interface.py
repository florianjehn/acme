# -*- coding: utf-8 -*-
"""
Created on Nov 17 10:53 2017
@author(s): Florian U. Jehn

Contains a basic class with the functions, which spotpy needs to work properly.
Is separated to make the model template more readable
"""
import datetime
import numpy as np
import spotpy


class SpotpyInterface:
    def __init__(self):
        self.params = None
        self.setparameters = None
        self.run_model = None
        self.obs_discharge = None
        self.begin_calibration = None
        self.end_calibration = None

    def simulation(self, vector):
        """
        SpotPy expects a method simulation. This methods calls setparameters
        and runmodels, so SpotPy is satisfied.
        """
        param_dict = dict((pp.name, v) for pp, v in zip(self.params, vector))
        self.setparameters(param_dict)

        sim_discharge = self.run_model()
        return np.array(sim_discharge)

    def evaluation(self):
        """
        For Spotpy. Creates a numpy array from the evaluation timeseries.
        """
        return np.array(
            self.obs_discharge[self.begin_calibration:self.end_calibration +
                               datetime.timedelta(days=1)])

    def parameters(self):
        """
        For Spotpy. Tells Spotpy the parameter names and ranges.
        """
        return spotpy.parameter.generate(self.params)
