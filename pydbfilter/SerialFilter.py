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

class SerialFilter(BaseFilter):
    """ Define interface common to all concrete filter implementations. """
    
    def filterPoints(self, data : Union[DataFrame, list]) -> Union[DataFrame, list]:
        """ Implements filtering buffer as serial calls to filterPoint(). """
        # If type is data frame
        if(type(data) is DataFrame):
            
            # Must have two columns
            if(len(data.columns) != 2):
                raise ValueError("Input data frame must have two columns.")
            
            # Apply over each row
            times = list()
            values = list()
            for row in data.iterrows():
                for result in self.filterPoint(row[1][0], row[1][1]):
                    times += [result[0]]
                    values += [result[1]]
            results = DataFrame({data.columns[0] : times, data.columns[1] : values})
        # If type is list
        if(type(data) is list):
            
            # For each point
            results = list()
            for time, value in data:
                results += self.filterPoint(time, value)

        return results