# -*- coding: utf-8 -*-
"""
Created on Aug 17 14:26 2017
@author(s): Florian U. Jehn
"""

from setuptools import setup

setup(
  name='acme',
  version='0.0.1',
  description='Automated Construction of Model by Evolution',

  author='Florian Jehn, Tobias Houska, Philipp Kraft, Alejandro '
          'Chamorro-Chavez and Lutz Breuer',
  author_email='florian.u.jehn@umwelt.uni-giessen.de',
  url='https://github.com/zutn/ACME',
  license='Apache-2.0',
  packages=["acme", "acme.examples", "acme.genetics",
            "acme.model_generators", "acme.visualization"],
  include_package_data=True,
  keywords=['Evolution', 'lumped models', 'Genetic Algorithms', 'Hydrology',
            'Simulated Annealing', 'CMF', 'ROPE', 'Uncertainty',
            'Calibration', 'Model', 'Signatures'],
  classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache-2.0 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'],)
