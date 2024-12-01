#!/usr/bin/env python
"""test_DeadbandFilter.py: unit tests for DeadbandFilter class."""

# Import built-in modules
import sys

# Import third-party modules
import pytest

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

def test_deadband():
    """Verify filter() method deadband filter functionality."""
    filter = DeadbandFilter(0.1,100)

    assert filter.filter(100, 1) == [(100, 1)]
    assert filter.filter(120, 1) == []
    assert filter.filter(140, 1.1) == [(140, 1.1)]   
    return

def test_timeout():
    """Verify filter() method timeout functionality."""
    filter = DeadbandFilter(0.1,100)

    assert filter.filter(100, 1) == [(100, 1)]
    assert filter.filter(160, 1) == []
    assert filter.filter(220, 1) == [(160, 1)]  
    assert filter.filter(240, 1) == [] 
    assert filter.filter(360, 1) == [(240, 1),(360, 1)] 

    return

def test_flush():
    """Verify flush() method."""
    filter = DeadbandFilter(0.1,100)

    assert filter.filter(100, 1) == [(100, 1)]
    assert filter.filter(120, 1) == []
    assert filter.flush() == [(120,1)]

    return
