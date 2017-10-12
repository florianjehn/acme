# ACME

**A**utomated **C**onstruction of **M**odels by **E**volution
---

[![Build Status][travis-image]][travis-link]
[![License][license-image]][license-link]

[travis-image]: https://travis-ci.org/zutn/ACME.svg?branch=master
[travis-link]: https://travis-ci.org/zutn/ACME
[license-image]: https://img.shields.io/hexpm/l/plug.svg
[license-link]: https://opensource.org/licenses/Apache-2.0


## Purpose
ACME is used to automatically construct a lumped, hydrological model for a given discharge, climate and precipitation timeseries. The model will itself will be constructed using the Catchment Modelling Framework [CMF](http://fb09-pasig.umwelt.uni-giessen.de/cmf).

## Features
Using different crossover and mutation techniques in combination with different evaluation schemes from [SPOTPY](http://fb09-pasig.umwelt.uni-giessen.de/spotpy/).

## Install
Installing ACME is straightforward (though not yet working). Just use:

	pip install acme

To be able to use it properly you need SPOTPY and CMF as well:

	pip install spotpy
	pip install cmf
## Support
- Feel free to contact the authors of this tool for any support questions.
- Please contact the authors in case of any bug.
- If you use ACME please cite: [Here will be a paper someday]().
- Patches and enhancements and any other contribution to ACME are very welcome!

## Getting started (and beyond)
You can either use only the genetic engine itself to define the way you want your CMF model to be created or you can use one of the predefined CMF-model-generators.

[Klick me to go to the examples](https://github.com/zutn/ACME/tree/master/acme/examples)

Or if you are up to a bit larger challenge it is also possible to rewrite the code provided here to work with different model frameworks (e.g. [FUSE](http://onlinelibrary.wiley.com/doi/10.1029/2007WR006735/abstract)). This might be a bit of work especially if the framework is not written in Python, but well worth a try. Feel free to contact me if you want to undertake this journey. 

## Important Dependencies
This program assumes you have an up to date [SPOTPY](http://fb09-pasig.umwelt.uni-giessen.de/spotpy/) package installed. If you want to create [CMF](http://fb09-pasig.umwelt.uni-giessen.de/cmf) models you also need an up to date CMF version. SPOTPY can be installed with pip. To get CMF you have to follow the instructions [here](http://fb09-pasig.umwelt.uni-giessen.de/cmf/wiki/CmfInstall).

## License
This project is released unter the Apache 2 license. If you are wondering what this means, here is a short explanation:

"The Apache license says “do whatever you want with this, just don’t sue me” but does so with many more words, which lawyers like because it adds specificity. It also contains a patent license and retaliation clause which is designed to prevent patents (including patent trolls) from encumbering the software project." 

(Taken from [here](https://exygy.com/which-license-should-i-use-mit-vs-apache-vs-gpl/))
