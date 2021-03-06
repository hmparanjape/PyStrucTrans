from __future__ import absolute_import, print_function, division, generators

from sys import version as SYS_VERSION
if SYS_VERSION > '3':
    long = int
    xrange = range

import logging
from warnings import warn

import numpy as np
import numpy.linalg as la

SMALL = 1.0E-12