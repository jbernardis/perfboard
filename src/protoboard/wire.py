'''
Created on Dec 22, 2015

@author: Jeff
'''

class Wire(object):
    def __init__(self, p1, p2, color):
        self.p1 = p1
        self.p2 = p2
        self.color = color
        
    def getXml(self):
        result =  "<pointa>%d,%d</pointa>" % (self.p1[0], self.p1[1])
        result += "<pointb>%d,%d</pointb>" % (self.p2[0], self.p2[1])
        result += "<color>%d,%d,%d</color>" % (self.color.red, self.color.green, self.color.blue)
        return result
    
    def getInstructions(self):
        return "Install wire color (%d,%d,%d) between positions %d,%d and %d,%d" % \
            (self.color.red, self.color.green, self.color.blue, self.p1[0], self.p1[1], self.p2[0], self.p2[1])
        
    def getP1(self):
        return self.p1
    
    def getP2(self):
        return self.p2
    
    def getColor(self):
        return self.color
