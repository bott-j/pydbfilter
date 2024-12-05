#!/usr/bin/env python
"""pydbfilter.py: Deadband filter class."""

# Import built-in modules
import collections

# Import third party modules
import numpy as np

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

# Named tupple holds line between last two points, also used to recalculate         
DeadbandFilterBoundary = collections.namedtuple('DeadbandFilterBoundary', 
                            ['m',   # Gradient from two accepted points
                             'b',   # Offset is height of last accepted point
                             'time',
                             'value'])  # Time of last accepted point

class DeadbandFilter(BaseFilter):    
    
    def __init__(self, deadbandValue, maximumInterval):        
        """ Class constructor. """
        self._deadbandValue = np.float64(deadbandValue)
        self._maximumInterval = np.float64(maximumInterval)
        self._bounds = None
        self._lastUnacceptedPoint = None

        return

    def isOutsideBounds(self, time, value):
        """ Tests if a time/value point is outside of deadband."""
        result = False
        
        # Calculate the lower and upper thresholds at this point in time
        upperLimit = self._bounds.m * time \
                        + self._bounds.b \
                        + self._deadbandValue / 2.0 
        lowerLimit = self._bounds.m * time \
                        + self._bounds.b \
                        - self._deadbandValue / 2.0

        # Test against limits
        if(value > upperLimit
            or value < lowerLimit):
            result = True

        return result

    def isTimeout(self, time):
        """ Checks if time for point exceeds maximum interval. """
        return (time - self._bounds.time) > self._maximumInterval  

    def updateBounds(self, newTime, newValue):
        """ Updates the linear deadband center line. """
        # If boundary line exists
        if(self._bounds):
            previousOffset = self._bounds.value
            previousTime = self._bounds.time
            self._bounds = self._bounds._replace(
                m = (newValue - previousOffset)/(newTime - previousTime),
                b = newValue - self._bounds.m * newTime)
        
        # Otherwise intialize it as a straight line
        else:
            self._bounds = DeadbandFilterBoundary(np.float64(0), newValue, newTime, newValue)

        self._bounds = self._bounds._replace(time = newTime, value = newValue)

        return    

    def filter(self, time, value):
        """ Filters a supplied time/value point. """
        result = []
        time = np.float64(time)
        value = np.float64(value)

        # Test conditions for filtering point
        # Test if this is the initial point
        if(not self._bounds):
            self.updateBounds(time, value)
            result += [(time, value)]
        elif(self.isTimeout(time)):
            # If the last point was not accepted accept it now
            if(self._lastUnacceptedPoint):
                result += [(self._lastUnacceptedPoint.time, self._lastUnacceptedPoint.value)]
                self.updateBounds(self._lastUnacceptedPoint.time, self._lastUnacceptedPoint.value)
                self._lastUnacceptedPoint = None
            # Retest if the new point exceeds bounds or timeout
            if(self.isOutsideBounds(time, value)
                or self.isTimeout(time)):
                result += [(time, value)]
                self.updateBounds(time, value)
            else:
                self._lastUnacceptedPoint = FilterPoint(time, value)    
        # If this point otherwise exceeds bounds
        elif(self.isOutsideBounds(time, value)):
            result += [(time, value)]
            self.updateBounds(time, value)
            self._lastUnacceptedPoint = None
        # Else this point becomes the last unaccepted point
        else:
            self._lastUnacceptedPoint = FilterPoint(time, value)
            
        return result

    def flush(self):
        """ Return any pending unaccepted point. """
        result = []
        if(self._lastUnacceptedPoint):
            result += [(self._lastUnacceptedPoint.time, self._lastUnacceptedPoint.value)]

        return result