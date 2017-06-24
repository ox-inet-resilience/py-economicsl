# python-destilledESL

[![DOI](https://zenodo.org/badge/95235014.svg)](https://zenodo.org/badge/latestdoi/95235014)
[![Build Status](https://travis-ci.org/rht/py-destilledESL.svg?branch=master)](https://travis-ci.org/rht/py-destilledESL)

This is a python port of the entirety of
https://github.com/EconomicSL/destilledESL, further trimmed to its essence.
`destilledESL` is a rewrite of Core-ESL, a reference implementation of Economic
Simulation Library. I anticipate that the spec for the EconomicSL library will
be cross-language, just like in the case of a spec of an IETF RFC.

Currently it has a feature and implementation parity with:
https://github.com/EconomicSL/destilledESL/commit/1ef2d0a9fed490990f2a600b2916391de50bdea8 (May 10 2017)

The goal of this repo is to become a catalyst for a convergent evolution between the
API designs in Core-ESL / destilled-ESL / ABCE. Ideas can be tested much more
easily here.

## Installation

To install, run
```
$ pip install git+https://github.com/rht/py-destilledESL
```

or from this repo
```
$ pip install .
```
