#!/usr/bin/env python
"""test_SdtFilter.py: unit tests for SdtFilter class."""

# Import built-in modules
import sys

# Import custom modules
sys.path.append('../')
from pydbfilter import SdtFilter

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

def test_sdt():
    """Verify filter() method deadband filter functionality."""
    filter = SdtFilter(10,100)

    assert filter.filter(100, 20) == [(100, 20)]
    assert filter.filter(110, 10) == []
    assert filter.filter(120, 20) == []
    assert filter.filter(140, 40) == [(130,25)]
    assert filter.filter(150, 30) == []
    assert filter.filter(160, 45) == []
    assert filter.filter(180, 5) == [(166, 38)]

    return

def test_timeout():
    """Verify filter() method timeout functionality."""
    filter = SdtFilter(10,100)

    assert filter.filter(100, -20) == [(100, -20)]
    assert filter.filter(200, -20) == []
    assert filter.filter(301, -20) == [(200, -20),(301,-20)]
    
    return

def test_flush():
    """Verify flush() method."""
    filter = SdtFilter(10,100)

    assert filter.filter(100, 5) == [(100, 5)]
    assert filter.filter(110, 5) == []
    assert filter.filter(120, 10) == []
    assert filter.flush() == [(120,10)]

    return
