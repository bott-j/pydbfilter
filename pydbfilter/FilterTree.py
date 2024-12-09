#!/usr/bin/env python
"""FilterTree.py: Implements BaseFilter derived classes as a tree data structure.\
"""

# Import custom modules
from . import SdtFilter, BaseFilter

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

# Decorator converts filter class into a tree data structure 
class FilterTree(BaseFilter):
    
    def __init__(self, className, *args, **kwargs):
        """ Class constructor. """
        self._children = dict()
        self._component = className(args, kwargs)
        self._className = className
        self._classArgs = args
        self._classKwargs = kwargs
        return

    def getAllChildren(self, parentTags = []):
        """ Method returns a list where each element is a tuple containing a 
            list of associated tags and a DeadbandFilter object instance.
        """ 
        result = list()

        for tagName, row in self._children.items():
            for tagValue, filter in row.items(): 
                # Add child record
                result += [(parentTags + [(tagName, tagValue)], filter)]
                # Add children of child record
                result += filter.getAllChildren(parentTags + [(tagName, tagValue)])

        return result

    def _addChild(self, tag, value, child):
        """ Adds a child to this tree node. """

        # If key already exists, update dict
        if tag in self._children.keys():
            self._children[tag][value] = child
        # If key doesn't exist, add dict
        else:
            self._children[tag] = {value : child}
        
        return

    def _getChild(self, tag, value):
        """ Retrieces a child from this tree node. """
        result = None

        # If tag name exists
        if(tag in self._children.keys()):
            # If tag value exists
            if(value in self._children[tag].keys()):
                result = self._children[tag][value]

        return result

    def walk(self, tags):
        """ Searches the tree for a node matching the tags specified. 
            Returns the DeadbandFilter object instance matching the tags.
            If one does not exist it is created.
        """
        result = None

        # Base case
        if(len(tags) == 0):
            result = self

        # Recursion case
        else:
            # Get the next tag to search sub tree for
            (tagKey, tagValue) = tags.pop()
            next = self._getChild(tagKey, tagValue)
            
            # If child has been found
            if(next is None):
                next = FilterTree(self._className, self._classArgs, self._classKwargs)
                self._addChild(tagKey, tagValue, next)

            # Recursively walk
            result = next.walk(tags)

        return result

    def filter(self, time: float, value: float) -> list:
        """ Pass filter calls to component. """
        return self._component.filter(time, value)

    def flush(self) -> list:
        """ Pass flush calls to component. """
        return self._component.flush()
