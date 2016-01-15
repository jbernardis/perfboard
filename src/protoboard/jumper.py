'''
Created on Dec 22, 2015

@author: Jeff
'''

class Jumper(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
    def getXml(self):
        result =  "<pointa>%d,%d</pointa>" % (self.p1[0], self.p1[1])
        result += "<pointb>%d,%d</pointb>" % (self.p2[0], self.p2[1])
        return result
    
    def getInstructions(self):
        return "Install jumper between positions %d,%d and %d,%d" % (self.p1[0], self.p1[1], self.p2[0], self.p2[1])
        
    def getP1(self):
        return self.p1
    
    def getP2(self):
        return self.p2
    
    def getP1P2(self):
        return [self.p1[0], self.p1[1], self.p2[0], self.p2[1]]