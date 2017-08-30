# -*- coding: utf-8 -*-
"""
Created on Aug 30 11:18 2017
@author(s): Florian U. Jehn


This datawriter is needed to stop Spotpy from writing large amounts of .csv
with simulation data, which are not needed for the progress of ACME.
"""

import spotpy
import datetime
import os

class DataWriter(spotpy.database.database):
    """
    Class to write the data in csv-files
    """
    def __init__(self, genes):
        self.genes = genes
        # open the file
        try:
            task_id = int(os.environ.get('SGE_TASK_ID',0))
        except:
            task_id = 0
        postfix = '.%04i' % task_id if task_id else ''



