#!/usr/bin/env python
"""pydbfilter.py: Deadband filter class."""

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

class DeadbandFilter(SerialFilter):    
    
    def __init__(self, deadbandValue, maximumInterval):        
        """ Class constructor. """
        self._deadbandValue = deadbandValue
        self._maximumInterval = maximumInterval
        self._base = None
        self._lastPoint = FilterPoint(0, 0)

        return

    def isOutsideBounds(self, time, value):
        """ Tests if a time/value point is outside of deadband."""
        result = False
        
        # Test against limits
        if(value > (self._base.value + self._deadbandValue)
            or value < (self._base.value - self._deadbandValue)):
            result = True

        return result

    def isTimeout(self, time):
        """ Checks if time for point exceeds maximum interval. """
        return (time - self._base.time) > self._maximumInterval  

    def filterPoint(self, time, value) -> list:
        """ Applies compression to the time-series points. """
        results = list()

        # Initialise min and max values
        if(self._base is None):
            self._base = FilterPoint(time, value)
            results += [(time, value)]
        # Handle invalid conditions
        elif(time <= self._lastPoint.time):
            raise ValueError("Time-series data-point must be newer than previous points.")
        else:
            # If max interval value exceeded
            if(self.isTimeout(time)):
                results += [(self._lastPoint.time, self._lastPoint.value)]
                self._base = self._base._replace(time = self._lastPoint.time, value = self._lastPoint.value)

            # If hysteresis threshold value exceeded or max interval
            # still exceeded
            if(self.isOutsideBounds(time, value)
                or self.isTimeout(time)):
                results += [(time, value)]
                self._base = self._base._replace(time = time, value = value)

        # Save the last point
        self._lastPoint = self._lastPoint._replace(time = time, value = value)

        return results

    def flush(self) -> list:
        """ Returns the last point if available. """
        results = []
        
        # The first point is always returned, so no need for a new point
        if(self._base):
            results += [(self._lastPoint.time, self._lastPoint.value)]
            self._base = self._base._replace(time = self._lastPoint.time, value = self._lastPoint.value)
        
        return results    
             
