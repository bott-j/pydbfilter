#!/usr/bin/env python
"""test_HysteresisFilter.py: unit tests for HysteresisFilter class."""

# Import built-in modules
import sys

# Import third-party modules
from pandas import DataFrame, testing

# Import custom modules
sys.path.append('../')
from pydbfilter import HysteresisFilter

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
    """Verify filter() method deadband filter functionality."""
    filter = HysteresisFilter(10,100)

    assert filter.filterPoint(100, 20) == [(100, 20)]
    assert filter.filterPoint(110, 10) == []
    assert filter.filterPoint(120, 20) == []
    assert filter.filterPoint(140, 40) == [(140,40)]
    assert filter.filterPoint(150, 30) == []
    assert filter.filterPoint(160, 45) == [(160, 45)]
    assert filter.filterPoint(180, 5) == [(180, 5)]

    return

def test_filterpoints_list():
    """Verify filterpoints() method deadband filter functionality with list."""
    filter = HysteresisFilter(10,100)

    data = [(100, 20),(110, 10),(120, 20),(140, 40),(150, 30),(160, 45),(180, 5)]    
    assert filter.filterPoints(data) == [(100, 20),(140,40),(160, 45),(180,5)]   

    return

def test_filterpoints_df():
    """Verify filterpoints() method deadband filter functionality with dataframe."""
    filter = HysteresisFilter(10,100)

    data = DataFrame({
                    "t" : [100,110,120,140,150,160,180],
                    "v" : [20,10,20,40,30,45,5]
                    })
    expected = DataFrame({
                    "t" : [100, 140, 160, 180],
                    "v" : [20, 40, 45, 5]
                    })
    result = filter.filterPoints(data)
    testing.assert_frame_equal(result, expected, check_dtype=False)
    
    return

def test_timeout():
    """Verify filter() method timeout functionality."""
    filter = HysteresisFilter(10,100)

    assert filter.filterPoint(100, -20) == [(100, -20)]
    assert filter.filterPoint(200, -20) == []
    assert filter.filterPoint(301, -20) == [(200, -20),(301,-20)]

    return

def test_flush():
    """Verify flush() method."""
    filter = HysteresisFilter(10,100)

    assert filter.filterPoint(100, 5) == [(100, 5)]
    assert filter.filterPoint(110, 5) == []
    assert filter.filterPoint(120, 10) == []
    assert filter.flush() == [(120,10)]

    return
