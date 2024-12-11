#!/usr/bin/env python
"""SerialFilter.py: Implements filterPoints() as calls to filterPoint()."""

# Import built-in modules
from typing import Union

# Import third-party modules
from pandas import DataFrame

# Import custom modules
from .BaseFilter import BaseFilter

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

class SerialFilter():
    """ Define interface common to all concrete filter implementations. """
    
    def filterPoints(self, data : Union[DataFrame, list]) -> Union[DataFrame, list]:

        # If type is data frame
        if(type(data) == DataFrame):
            
            # Must have two columns
            if(len(df.columns) != 2):
                raise ValueError("Input data frame must have two columns.")
        
            # Apply map to series
            results = data.copy()
            results.iloc[:,1] = data.apply(lambda d: self.filterPoint(d[0], d[1]), axis=1)

        # If type is list
        if(type(data) == list):
            
            # For each point
            results = list()
            for time, value in data:
                results += [[time, self.filterPoint(time, value)]]

        return results