#!/usr/bin/env python
"""test_DeadbandFilter.py: unit tests for DeadbandFilter class."""

# Import built-in modules
import sys

# Import third-party modules
from pandas import DataFrame, testing

# Import custom modules
sys.path.append('../')
from pydbfilter import DeadbandFilter

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

def test_filterpoint():
    """Verify filterpoint() method deadband filter functionality."""
    filter = DeadbandFilter(0.1,100)

    assert filter.filterPoint(100, 1) == [(100, 1)]
    assert filter.filterPoint(120, 1.1) == []
    assert filter.filterPoint(140, 0.9) == []
    assert filter.filterPoint(150, 1.2) == [(150, 1.2)]   
    assert filter.filterPoint(160, 1.3) == []   
    assert filter.filterPoint(170, 1.1) == []   
    assert filter.filterPoint(180, 1) == [(180, 1)]   
    return

def test_filterpoints_list():
    """Verify filterpoints() method deadband filter functionality with list."""
    filter = DeadbandFilter(0.1,100)

    data = [(100, 1),(120, 1.1),(140, 0.9),(150, 1.2),(160, 1.3),(170, 1.1),(180, 1)]    
    assert filter.filterPoints(data) == [(100, 1),(150, 1.2),(180, 1)]   

    return

def test_filterpoints_df():
    """Verify filterpoints() method deadband filter functionality with dataframe."""
    filter = DeadbandFilter(0.1,100)

    data = DataFrame({
                    "t" : [100,120,140,150,160,170,180],
                    "v" : [1,1.1,0.9,1.2,1.3,1.1,1]
                    })
    expected = DataFrame({
                    "t" : [100, 150, 180],
                    "v" : [1, 1.2, 1]
                    })
    result = filter.filterPoints(data)
    testing.assert_frame_equal(result, expected, check_dtype=False)
    
    return

def test_timeout():
    """Verify filter() method timeout functionality."""
    filter = DeadbandFilter(0.1,100)

    assert filter.filterPoint(100, 1) == [(100, 1)]
    assert filter.filterPoint(160, 1) == []
    assert filter.filterPoint(220, 1) == [(160, 1)]  
    assert filter.filterPoint(240, 1) == [] 
    assert filter.filterPoint(360, 1) == [(240, 1),(360, 1)] 

    return

def test_flush():
    """Verify flush() method."""
    filter = DeadbandFilter(0.1,100)

    assert filter.filterPoint(100, 1) == [(100, 1)]
    assert filter.filterPoint(120, 1) == []
    assert filter.flush() == [(120,1)]

    return
