#!/usr/bin/env python
"""SdtFilter.py: SDT filter concrete implementation."""

# Import built-in modules
from collections import deque

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

class SdtFilter(BaseFilter):

    def __init__(self, compressionDeviation, maxInterval):
        """ Class constructor. """

        # The compression deviation and maximum interval
        self._compressionDeviation = compressionDeviation
        self._maxInterval = maxInterval

        # Limits on sloping upper and sloping lower gradients
        self._slopingUpperMax = -float("inf")
        self._slopingLowerMin = float("inf")

        # Queu to hold up to two previous points
        self._lastPoints = deque(maxlen = 2)

        return

    def _updateWindow(self, thisPoint, newPoint):
        """ Initialises window for a new parallelogram. """
        
        # Update upper and lower pivot
        self._upperPivot = newPoint + FilterPoint(0, self._compressionDeviation)
        self._lowerPivot = newPoint + FilterPoint(0, -self._compressionDeviation)
        
        # Update the sloping upper and sloping lower gradients
        # Sloping upper is the gradient between the current point and the upper pivot
        slopingUpper = (thisPoint.value - self._upperPivot.value)/(thisPoint.time - self._upperPivot.time)
        # Sloping lower is the gradient between the current point and the lower pivot 
        slopingLower = (thisPoint.value - self._lowerPivot.value)/(thisPoint.time - self._lowerPivot.time)
        
        # Uppdate limits on sloping upper and sloping lower gradients
        self._slopingUpperMax = slopingUpper
        self._slopingLowerMax = slopingLower

        return

    def filter(self, time, value) -> list:
        """ Applies compression to the time-series points. """
        results = list()

        # Initialisation
        if(len(self._lastPoints) < 1):
            # Last point generated by the algorithm
            thisPoint = FilterPoint(time, value)

            # Upper and lower pivot points
            self._upperPivot = thisPoint + FilterPoint(0, self._compressionDeviation)
            self._lowerPivot = thisPoint + FilterPoint(0, -self._compressionDeviation)
            
            # First point received is generated by the algorithm
            results += [(thisPoint.time, thisPoint.value)]
        else:
            # Update last point and current point
            thisPoint = FilterPoint(time = time, value = value)

            # Update the sloping upper and sloping lower gradients
            # These are the gradients between the current point and upper/lower pivot points respectively
            slopingUpper = (thisPoint.value - self._upperPivot.value) / (thisPoint.time - self._upperPivot.time)
            slopingLower = (thisPoint.value - self._lowerPivot.value) / (thisPoint.time - self._lowerPivot.time)

            # If maximum interval reached
            if(thisPoint.time - self._lastPoints[0].time > self._maxInterval):
                results += [(thisPoint.time, thisPoint.value)]
                # Recalculate the window
                self._updateWindow(self._lastPoints[0], thisPoint)  

            # Otherwise evaluate if parallelogram envelope exceeded
            else:
                # If sloping upper gradient exceeded limit 
                if(slopingUpper > self._slopingUpperMax):
                    # Update sloping upper gradient limit
                    self._slopingUpperMax = slopingUpper

                    # If sloping upper gradient limit exceeds sloping lower gradient limit
                    if(self._slopingUpperMax > self._slopingLowerMin):
                                                
                        # L1 will be a line parallel to _slopingLowerMax, passing through the upper pivot
                        # Use slopping lower min as the gradient
                        m1 = self._slopingLowerMin
                        # Find intercept from equation of line passing through upper pivot: 
                        #   b1 = y - m1*x
                        b1 = self._upperPivot.value - m1*self._upperPivot.time 

                        # L2 will be the line between the last two points
                        # Find gradient betwen this point and last point
                        m2 = (thisPoint.value - self._lastPoints[0].value)/(thisPoint.time - self._lastPoints[0].time)
                        # Find intercept from equation of line passing through this point:
                        #   b2 = y - m2*x
                        b2 = thisPoint.value - m2 * thisPoint.time                    

                        # Find point of intersection between L1 and L2 
                        # which will be the lower boundary for the parallelogram 
                        newPoint = FilterPoint((b2 - b1)/(m1 - m2), m1*(b2 - b1)/(m1 - m2) + b1)
                        # Offset point to lie between the upper and lower boundaries of the parallelogram
                        newPoint -= FilterPoint(0, self._compressionDeviation/2)

                        # New point generated by compression algorithm
                        results += [(newPoint.time, newPoint.value)]
                        
                        # Recalculate the window
                        self._updateWindow(thisPoint, newPoint)

                # If sloping lower gradient exceeded limit
                if(slopingLower < self._slopingLowerMin):
                    
                    # Update sloping lower gradient minimum
                    self._slopingLowerMin = slopingLower
                    
                    # If sloping upper gradient limit exceeds sloping lower gradient limit
                    if(self._slopingUpperMax > self._slopingLowerMin):
                                                
                        # L1 will be a line parallel to _slopingUpperMax, passing through the lower pivot
                        # Use slopping upper max as the gradient
                        m1 = self._slopingUpperMax
                        # Find intercept from equation of line passing through lower pivot: 
                        #   b1 = y - m1*x
                        b1 = self._lowerPivot.value - m1*self._lowerPivot.time 

                        # L2 will be the line between the last two points
                        # Find gradient betwen this point and last point
                        m2 = (thisPoint.value - self._lastPoints[0].value)/(thisPoint.time - self._lastPoints[0].time)
                        # Find intercept from equation of line passing through this point:
                        #   b2 = y - m2*x
                        b2 = thisPoint.value - m2 * thisPoint.time
                        
                        # Find point of intersection between L1 and L2,
                        # which will be the lower boundary for the parallelogram 
                        newPoint = FilterPoint((b2 - b1)/(m1 - m2), m1*(b2 - b1)/(m1 - m2) + b1)
                        # Offset point to lie between the upper and lower boundaries of the parallelogram
                        newPoint += FilterPoint(0, self._compressionDeviation/2)

                        # New point generated by compression algorithm
                        results += [(newPoint.time, newPoint.value)]
                        
                        # Recalculate the window
                        self._updateWindow(thisPoint, newPoint)

        # Save the last point
        self._lastPoints.appendleft(thisPoint)

        return results

    def flush(self) -> list:
        """ Returns the last point if available. """
        results = []
        
        # The first point is always returned, so no need for a new point
        if(len(self._lastPoints) > 1):
            results += [(self._lastPoints[0].time, self._lastPoints[0].value)]
            self._updateWindow(self._lastPoints[-1], self._lastPoints[0]) 
        
        return results    
             
