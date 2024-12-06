#!/usr/bin/env python
"""FilterPoint.py: Named tuple for time series point."""

# Import built-in modules
import collections

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

# Named tupple holds a time-series point
FilterPoint = collections.namedtuple('FilterPoint',
                            ['time',
                             'value'])
# Define addition operator for named tuple
def add(self: FilterPoint, other: FilterPoint) -> FilterPoint:
    return FilterPoint(self.time + other.time, self.value + other.value)
# Define subtraction operator for named tuple
def sub(self: FilterPoint, other: FilterPoint) -> FilterPoint:
    return FilterPoint(self.time - other.time, self.value - other.value)
# Overload operators on named tupple
FilterPoint.__add__ = add
FilterPoint.__sub__ = sub    
