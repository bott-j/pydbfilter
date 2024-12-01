#!/usr/bin/env python
"""dbfilterTree.py: Implements DeadbandFilter class as a tree data structure.\
"""

# Import custom modules
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

# Decorator converts filter class into a tree data structure 
class DeadbandFilterTree(DeadbandFilter):

    def __init__(self, deadbandvalue, maximuminterval):
        self._children = dict()
        self._deadbandvalue = deadbandvalue
        self._maximuminterval = maximuminterval
        return super().__init__(deadbandvalue, maximuminterval)

    def getAllChildren(self, parentTags = []):
        result = list()

        for tagName, row in self._children.items():
            for tagValue, filter in row.items(): 
                # Add child record
                result += [(parentTags + [(tagName, tagValue)], filter)]
                # Add children of child record
                result += filter.getAllChildren(parentTags + [(tagName, tagValue)])

        return result

    def addChild(self, tag, value, child):
        self._children.update({tag : {value : child}}) 
        return

    def getChild(self, tag, value):
        result = None
        if(tag in self._children.keys()):
            if(value in self._children[tag].keys()):
                result = self._children[tag][value]
        return result

    def walk(self, tags):
        result = None

        # Base case
        if(len(tags) == 0):
            result = self

        # Recursion case
        else:
            # Get the next tag to search sub tree for
            (tagKey, tagValue) = tags.pop()
            next = self.getChild(tagKey, tagValue)
            
            # If child has been found
            if(next is None):
                next = DeadbandFilterTree(self._deadbandvalue, self._maximuminterval)
                self.addChild(tagKey, tagValue, next)

            # Recursively walk
            result = next.walk(tags)

        return result