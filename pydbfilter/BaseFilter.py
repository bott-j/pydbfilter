#!/usr/bin/env python
"""BaseFilter.py: Filter class interface."""

# Import built-in modules
from abc import abstractmethod
from typing import Union

# Import third-party modules
from pandas import DataFrame

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

class BaseFilter():
    """ Define interface common to all concrete filter implementations. """
    
    @abstractmethod
    def filterPoint(self, time: float, value: float) -> list:
        pass

    @abstractmethod
    def filterPoints(self, data : Union[DataFrame, list]) -> Union[DataFrame, list]:
        pass

    @abstractmethod
    def flush(self) -> list:
        pass 
