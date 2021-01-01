# python-distilledESL

[![DOI](https://zenodo.org/badge/95235014.svg)](https://zenodo.org/badge/latestdoi/95235014)
[![Build Status](https://github.com/ox-inet-resilience/py-economicsl/workflows/build/badge.svg)](https://github.com/ox-inet-resilience/py-economicsl/actions?query=workflow%3Abuild)

This is a python port of the entirety of
https://github.com/EconomicSL/distilledESL, further trimmed to its essence.
`distilledESL` is a rewrite of Core-ESL, a reference implementation of Economic
Simulation Library. I anticipate that the spec for the EconomicSL library will
be cross-language, just like in the case of a spec of an IETF RFC.

Currently it has a feature and implementation parity with:
https://github.com/EconomicSL/distilledESL/commit/1ef2d0a9fed490990f2a600b2916391de50bdea8 (May 10 2017)

The goal of this repo is to become a catalyst for a convergent evolution between the
API designs in Core-ESL / distilled-ESL / ABCE. Ideas can be tested much more
easily here.

## Installation

This library uses Python >=3.5 type system, so it runs only on python>=3.5.

To install, run
```
$ pip install git+https://github.com/ox-inet-resilience/py-economicsl
```

or from this repo
```
$ pip install .
```
