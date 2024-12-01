from pydbfilter import DeadbandFilter

# Decorator converts filter class into a tree data structure 
class DeadbandFilterTree(DeadbandFilter):

    def __init__(self, deadbandvalue, maximuminterval):
        self._children = dict()
        self._deadbandvalue = deadbandvalue
        self._maximuminterval = maximuminterval
        return super().__init__(deadbandvalue, maximuminterval)

    def addChild(self, tag, value, child):
        self._children.update({tag : {value : child}}) 
        return

    def getChild(self, tag, value):
        result = None
        if(tag in self._children.keys()):
            if(value in self._children[tag].keys()):
                result = self._children[tag][value]
        return result

    def walk(tags):
        result = None

        # Base case
        if(len(tags) == 0):
            result = self
        else:
            (tagKey, tagValue) = tags.pop()
            next = self.getChild(tagKey, tagValue)
            if(next is None):
                next = self.addChild(tagKey, tagValue, dbfilterTree(self._deadbandvalue, self._maximuminterval))
            result = next.walk(tags)

        return result
