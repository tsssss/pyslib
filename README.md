# pyslib
My library `slib` written in python. NOTE: it's still under development.

## Geopack and Tsyganenko models
All modules in `geopack` has been coverted to python from the original Fortran code, including the recalc routine, tracing routines, the coordinate conversion routines.

Tsyganenko models have been added are T89, T96, T01. I'm working on T04 and T08.

## I/O modules
So far, I've only written routines to read CDF. These routines are based on the `cdflib`.

## The data processing system
The core of the system is the `sdata` class (a better name?).
`sdata` can be fed by "drivers" per spacecraft per instrument. Once the data are loaded into `sdata`, they can be processed, plotted, saved, etc.
