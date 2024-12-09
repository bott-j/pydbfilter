#!/usr/bin/env python
"""Hysteresis.py: Hysteresis concrete implementation."""

# Import custom modules
from .BaseFilter import BaseFilter
from .FilterPoint import FilterPoint

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

class HysteresisFilter(BaseFilter):

    def __init__(self, compressionDeviation, maxInterval):
        """ Class constructor. """

        # Min and max values track the spread of points
        self._minValue = None
        self._maxValue = None

        # Last point received
        self._lastPoint = FilterPoint(0, 0)

        return

    def filter(self, time, value) -> list:
        """ Applies compression to the time-series points. """
        results = list()

        # Initialise min and max values
        if(self._minValue = None):
            self._minValue = value
            self._maxValue = value
            results += [(time, value)]
        # Update min and max values
        else:
            if(value > self._maxValue):
                self._maxValue = value
            if(value < self._minValue):
                self._minValue = value

        # If hysteresis threshold value exceeded
        if(self._maxValue - self._minValue > self._hystValue):
            results += [(time, value)]
            self._minValue = value
            self._maxValue = value

        # Save the last point
        self._lastPoint = self._lastPoint.update(time = time, value = value)

        return results

    def flush(self) -> list:
        """ Returns the last point if available. """
        results = []
        
        # The first point is always returned, so no need for a new point
        if(self._minValue):
            results += [(self._lastPoint.time, self._lastPoint.value)]
        
        return results    
             
