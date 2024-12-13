#!/usr/bin/env python
"""Hysteresis.py: Hysteresis concrete implementation."""

# Import custom modules
from .SerialFilter import SerialFilter
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

class HysteresisFilter(SerialFilter):

    def __init__(self, hystValue, maxInterval):
        """ Class constructor. """

        # Parameters
        self._hystValue = hystValue
        self._maxInterval = maxInterval

        # Min and max values track the spread of points
        self._minValue = None
        self._maxValue = None
        self._firstTime = None

        # Last point received
        self._lastPoint = FilterPoint(0, 0)

        return

    def filterPoint(self, time, value) -> list:
        """ Applies compression to the time-series points. """
        results = list()

        # Initialise min and max values
        if(self._minValue is None):
            self._minValue = value
            self._maxValue = value
            self._firstTime = time
            results += [(time, value)]
        # Handle invalid conditions
        elif(time <= self._lastPoint.time)
            raise ValueError("Time-series data-point must be newer than previous points.")
        else:
            # If max interval value exceeded
            if((time - self._firstTime) > self._maxInterval):
                results += [(self._lastPoint.time, self._lastPoint.value)]
                self._firstTime = self._lastPoint.time
                self._minValue = self._lastPoint.value
                self._maxValue = self._lastPoint.value

            # Update min and max values
            if(value > self._maxValue):
                self._maxValue = value
            if(value < self._minValue):
                self._minValue = value

            # If hysteresis threshold value exceeded or max interval
            # still exceeded
            if((self._maxValue - self._minValue) > self._hystValue
                or (time - self._firstTime) > self._maxInterval):
                results += [(time, value)]
                self._minValue = value
                self._maxValue = value
                self._firstTime = time

        # Save the last point
        self._lastPoint = self._lastPoint._replace(time = time, value = value)

        return results

    def flush(self) -> list:
        """ Returns the last point if available. """
        results = []
        
        # The first point is always returned, so no need for a new point
        if(self._minValue):
            results += [(self._lastPoint.time, self._lastPoint.value)]
        
        return results    
             
