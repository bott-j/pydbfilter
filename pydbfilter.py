#!/usr/bin/env python
"""pydbfilter.py: Deadband filter class."""

# Import built-in modules
import collections

# Import third party modules
import numpy as np

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

# Named tupple holds a time-series point
DeadbandFilterPoint = collections.namedtuple('DeadbandFilterPoint',
                            ['time',
                             'value'])

class DeadbandFilter:    
    
    def __init__(self, deadbandValue, maximumInterval):        
        
        self._deadbandValue = np.int64(deadbandValue)
        self._maximumInterval = np.int64(maximumInterval)
        self._bounds = None
        self._lastUnacceptedPoint = None

        return

    def isOutsideBounds(self, time, value):
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
        return (time - self._bounds.time) > self._maximumInterval  

    def updateBounds(self, time, value):
        
        # If boundary line exists
        if(self._bounds):
            previousOffset = self._bounds.value
            previousTime = self._bounds.time
            self._bounds._replace(
                m = (value - previousOffset)/(time - previousTime),
                b = value - self._bounds.m * time)
        
        # Otherwise intialize it as a straight line
        else:
            self._bounds = DeadbandFilterBoundary(np.int64(0), value, time, value)

        self._bounds._replace(time = time, value = value)

        return    

    def filter(self, time, value):
        result = []
        time = np.int64(time)
        value = np.int64(value)

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
                self._lastUnacceptedPoint = DeadbandFilterPoint(time, value)    
        # If this point otherwise exceeds bounds
        elif(self.isOutsideBounds(time, value)):
            result += [(time, value)]
            self.updateBounds(time, value)
            self._lastUnacceptedPoint = None
        # Else this point becomes the last unaccepted point
        else:
            self._lastUnacceptedPoint = DeadbandFilterPoint(time, value)
            
        return result

    def flush(self):
        result = []
        if(self._lastUnacceptedPoint):
            result += [(self._lastUnacceptedPoint.time, self._lastUnacceptedPoint.value)]

        return result