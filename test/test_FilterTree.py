#!/usr/bin/env python
"""test_FilterTree.py: unit tests for FilterTree class."""

# Import built-in modules
import sys

# Import custom modules
sys.path.append('../')
from pydbfilter import FilterTree, SdtFilter, BaseFilter

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

def test_walk():
    """Verify walk() method."""
    tree = FilterTree(SdtFilter,0.1,100)

    # Create tag associated filters
    filter1 = tree.walk([("location","italy")])
    filter2 = tree.walk([("location","japan")])

    # Retrieve previously defined filter
    filter3 = tree.walk([("location","italy")])

    # Check of correct type
    assert isinstance(filter1, BaseFilter)
    assert isinstance(filter2, BaseFilter)

    # Check expected instances
    assert filter1 == filter3
    assert filter2 != filter3

    return

def test_getallchildren():
    """ Verify getallchildren() method. """
    tree = FilterTree(SdtFilter, 0.1,100)

    # Create tag associated filters
    filter1 = tree.walk([("location","italy")])
    filter2 = tree.walk([("location","japan")])

    # Check method returns expected data structure
    children = tree.getAllChildren()
    assert children == [([("location","italy")], filter1),([("location","japan")], filter2)]

    # Create filter at depth of two tags
    filter3 = tree.walk([("category","a")])
    filter4 = tree.walk([("location","italy"),("category","a")])
    children = tree.getAllChildren()

    # Check method returns expected data structure
    assert children == [([("location","italy")], filter1),
                        ([("location","japan")], filter2),
                        ([("category","a")], filter3),
                        ([("category","a"),("location","italy")], filter4)]
    
    return

