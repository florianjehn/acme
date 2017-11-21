# -*- coding: utf-8 -*-
"""
Created on Aug 17 14:26 2017
@author(s): Florian U. Jehn
"""

from setuptools import setup
import acme
import io


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.md')


setup(
  name='acme',
  version=acme.__version__,
  description='Automated Construction of Model by Evolution',
  long_description=long_description,
  author='Florian Jehn, Tobias Houska, Philipp Kraft, Lutz Breuer',
  author_email='florian.u.jehn@umwelt.uni-giessen.de',
  url='https://github.com/zutn/ACME',
  license='Apache-2.0',
  packages=["acme", "acme.examples", "acme.genetics",
            "acme.cmf_model_generators", "acme.visualization", "acme.tests"],
  include_package_data=True,
  zip_save=False,
  keywords=['Evolution', 'lumped models', 'Genetic Algorithms', 'Hydrology',
            'Simulated Annealing', 'CMF', 'ROPE', 'Uncertainty',
            'Calibration', 'Model', 'Signatures', 'Validation'],
  classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache-2.0 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'],)
