'''
Created on Dec 23, 2015

@author: Jeff
'''

CLASS_FIXED = 1
CLASS_STRETCH = 2
CLASS_GROW = 3
CLASS_WIRE = 4

class CompId:
    def __init__(self):
        self.inuse = []
        
    def reInit(self):
        self.inuse = []

    def generateID(self, prefix):
        nx = 0
        while True:       
            nx += 1
        
            nm = "%s%d" % (prefix, nx)
            if not nm in self.inuse:
                self.inuse.append(nm)
                return nm
            
    def returnID(self, nm):
        if nm in self.inuse:
            self.inuse.remove(nm)
            
    def reserveID(self, nm):
        if not nm in self.inuse:
            self.inuse.append(nm)
    

compID = CompId()

class Component:
    def setID(self, ID):
        self.ID = ID
        
    def getID(self):
        return self.ID
    
    def setName(self, n):
        self.name = n
        
    def getName(self):
        return self.name
    
    def setValue(self, v):
        self.value = v
        
    def getValue(self):
        return self.value
    
    def getClass(self):
        return self.classification
    
    def getInstructions(self):
        return "Instructions not yet implemented for this subtype"


class FixedComponent(Component):
    def __init__(self, ctype, cnx, cvr, image, offset):
        self.ctype = ctype
        self.name = ""
        self.value = ""
        self.pts = cnx
        self.covered = cvr
        self.image = image
        self.offset = offset
        self.view = 0
        self.anchor = None
        self.ID = None
        self.classification = CLASS_FIXED
        
    def getType(self):
        return self.ctype
        
    def setView(self, v):
        self.view = v
        
    def getView(self):
        return self.view
        
    def getXml(self):
        result = "<type>%s</type>" % self.ctype
        result += "<id>%s</id>" % self.ID
        result += "<view>%d</view>" % self.view
        result += "<name>%s</name>" % self.name
        result += "<value>%s</value>" % self.value
        result += "<anchor>%d,%d</anchor>" % (self.anchor[0], self.anchor[1])
        return result
    
    def getInstructions(self):
        inst = "Install %s %s" % (self.ctype, self.ID)
        if self.name.strip() != "":
            inst += " - %s" % self.name
        if self.value.strip() != "":
            inst += " (%s) " % self.value
            
        inst += " anchored at position %d,%d view number %d" % (self.anchor[0], self.anchor[1], self.view)
        return inst
       
    def setAnchor(self, pos):
        self.anchor = pos 
        
    def getAnchor(self):
        return self.anchor
    
    def getBitmap(self):
        return self.image
    
    def setBitmap(self, img):
        self.image = img
    
    def getConnections(self):
        return self.pts
    
    def setConnections(self, cnx):
        self.pts = cnx
    
    def getOffset(self):
        return self.offset
    
    def setOffset(self, o):
        self.offset = o
    
    def getCovered(self):
        return self.pts + self.covered
    
    def setCovered(self, cvr):
        self.covered = cvr
    
class FixedComponentList:
    def __init__(self, images):
        self.componentTypes = {}
        self.componentList = {}
 
        self.componentList["DIP4"] = [
            [[0, 0], [0, 1], [3, 1], [3, 0]],
            [[1, 0], [2, 0], [1, 1], [2, 1]],
            images.pngDip4,
            [-2, -2], "IC"]
        self.componentList["DIP4r1"] = [
            [[0, 0], [1, 0], [0, -3], [1, -3]],
            [[0, -1], [1, -1], [0, -2], [1, -2]],
            images.pngDip4r1,
            [-2, -47], "IC"]
        self.componentList["DIP4r2"] = [
            [[0, 0], [0, -1], [-3, -1], [-3, 0]],
            [[-1, 0], [-2, 0], [-1, -1], [-2, -1]],
            images.pngDip4r2,
            [-47, -17], "IC"]
        self.componentList["DIP4r3"] = [
            [[0, 0], [-1, 0], [0, 3], [-1, 3]],
            [[0, 1], [-1, 1], [0, 2], [-1, 2]],
            images.pngDip4r3,
            [-17, -2], "IC"]
        self.componentTypes["DIP4"] = ["DIP4", "DIP4r1", "DIP4r2", "DIP4r3"]

        self.componentList["DIP8"] = [
            [[0, i] for i in range(4)] + [[3, i] for i in range(4)],
            [[1, i] for i in range(4)] + [[2, i] for i in range(4)],
            images.pngDip8, [-2, -2], "IC"] 
        self.componentList["DIP8r1"] = [
            [[i, 0] for i in range(4)] + [[i, -3] for i in range(4)],
            [[i, -1] for i in range(4)] + [[i, -2] for i in range(4)],
            images.pngDip8r1, [-2, -47], "IC"]
        self.componentList["DIP8r2"] = [
            [[0, i-3] for i in range(4)] + [[-3, i-3] for i in range(4)],
            [[-1, i-3] for i in range(4)] + [[-2, i-3] for i in range(4)],
            images.pngDip8r2, [-47, -47], "IC"]
        self.componentList["DIP8r3"] = [
            [[i-3, 0] for i in range(4)] + [[i-3, 3] for i in range(4)],
            [[i-3, 1] for i in range(4)] + [[i-3, 2] for i in range(4)],
            images.pngDip8r3, [-47, -2], "IC"]
        self.componentTypes["DIP8"] = ["DIP8", "DIP8r1", "DIP8r2", "DIP8r3"]
 
        self.componentList["DIP14"] = [
            [[0, i] for i in range(7)] + [[3, i] for i in range(7)],
            [[1, i] for i in range(7)] + [[2, i] for i in range(7)],
            images.pngDip14, [-2, -2], "IC"]
        self.componentList["DIP14r1"] = [
            [[i, 0] for i in range(7)] + [[i, -3] for i in range(7)],
            [[i, -1] for i in range(7)] + [[i, -2] for i in range(7)],
            images.pngDip14r1, [-2, -47], "IC"]
        self.componentList["DIP14r2"] = [
            [[0, i-6] for i in range(7)] + [[-3, i-6] for i in range(7)],
            [[-1, i-6] for i in range(7)] + [[-2, i-6] for i in range(7)],
            images.pngDip14r2, [-47, -92], "IC"]
        self.componentList["DIP14r3"] = [
            [[i-6, 0] for i in range(7)] + [[i-6, 3] for i in range(7)],
            [[i-6, 1] for i in range(7)] + [[i-6, 2] for i in range(7)],
            images.pngDip14r3, [-92, -2], "IC"]
        self.componentTypes["DIP14"] = ["DIP14", "DIP14r1", "DIP14r2", "DIP14r3"]
 
        self.componentList["DIP16"] = [
            [[0, i] for i in range(8)] + [[3, i] for i in range(8)],
            [[1, i] for i in range(8)] + [[2, i] for i in range(8)],
            images.pngDip16, [-2, -2], "IC"]
        self.componentList["DIP16r1"] = [
            [[i, 0] for i in range(8)] + [[i, -3] for i in range(8)],
            [[i, -1] for i in range(8)] + [[i, -2] for i in range(8)],
            images.pngDip16r1, [-2, -47], "IC"]
        self.componentList["DIP16r2"] = [
            [[0, i-7] for i in range(8)] + [[-3, i-7] for i in range(8)],
            [[-1, i-7] for i in range(8)] + [[-2, i-7] for i in range(8)],
            images.pngDip16r2, [-47, -107], "IC"]
        self.componentList["DIP16r3"] = [
            [[i-7, 0] for i in range(8)] + [[i-7, 3] for i in range(8)],
            [[i-7, 1] for i in range(8)] + [[i-7, 2] for i in range(8)],
            images.pngDip16r3, [-107, -2], "IC"]
        self.componentTypes["DIP16"] = ["DIP16", "DIP16r1", "DIP16r2", "DIP16r3"]

        self.componentList["DIP28"] = [
            [[0, i] for i in range(14)] + [[3, i] for i in range(14)],
            [[1, i] for i in range(14)] + [[2, i] for i in range(14)],
            images.pngDip28,
            [-2, -2], "IC"]
        self.componentList["DIP28r1"] = [
            [[i, 0] for i in range(14)] + [[i, -3] for i in range(14)],
            [[i, -1] for i in range(14)] + [[i, -2] for i in range(14)],
            images.pngDip28r1,
            [-2, -47], "IC"]
        self.componentList["DIP28r2"] = [
            [[0, i-13] for i in range(14)] + [[-3, i-13] for i in range(14)],
            [[-1, i-13] for i in range(14)] + [[-2, i-13] for i in range(14)],
            images.pngDip28r2,
            [-47, -197], "IC"]
        self.componentList["DIP28r3"] = [
            [[i-13, 0] for i in range(14)] + [[i-13, 3] for i in range(14)],
            [[i-13, 1] for i in range(14)] + [[i-13, 2] for i in range(14)],
            images.pngDip28r3,
            [-197, -2], "IC"]
        self.componentTypes["DIP28"] = ["DIP28", "DIP28r1", "DIP28r2", "DIP28r3"]
        
        self.componentList["Electrolytic Cap - small"] = [[[0, 0], [0, 1]],  [], images.pngCapsmall, [-17, -9], "C"]
        self.componentList["Electrolytic Cap - smallr1"] = [[[0, 0], [1, 0]],  [], images.pngCapsmallr1, [-9, -17], "C"]
        self.componentTypes["Electrolytic Cap - small"] = ["Electrolytic Cap - small", "Electrolytic Cap - smallr1"]
                
        self.componentList["Electrolytic Cap - medium"] = [[[0, 0], [0, 1]],  [[-1, 0], [1, 0], [-1, 1], [1, 1]], images.pngCapmedium, [-24, -17], "C"]
        self.componentList["Electrolytic Cap - mediumr1"] = [[[0, 0], [1, 0]],  [[0, -1], [0, 1], [1, -1], [1, 1]], images.pngCapmediumr1, [-17, -24], "C"]
        self.componentTypes["Electrolytic Cap - medium"] = ["Electrolytic Cap - medium", "Electrolytic Cap - mediumr1"]
        
        self.componentList["Electrolytic Cap - large"] = [[[0, 0], [0, 2]],  [[-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1], [-1, 2], [1, 2]], images.pngCaplarge, [-32, -17], "C"]
        self.componentList["Electrolytic Cap - larger1"] = [[[0, 0], [2, 0]],  [[1, 0], [0, -1], [1, -1], [2, -1], [0, 1], [1, 1], [2, 1]], images.pngCaplarger1, [-17, -32], "C"]
        self.componentTypes["Electrolytic Cap - large"] = ["Electrolytic Cap - large", "Electrolytic Cap - larger1"]
        
        self.componentList["Voltage Regulator"] = [[[0, 0], [0, 1], [0, 2]],  [], images.pngTo220, [-2, -5], "VR"]
        self.componentList["Voltage Regulatorr1"] = [[[0, 0], [1, 0], [2, 0]],  [], images.pngTo220r1, [-5, -12], "VR"]
        self.componentList["Voltage Regulatorr2"] = [[[0, 0], [0, -1], [0, -2]],  [], images.pngTo220r2, [-12, -35], "VR"]
        self.componentList["Voltage Regulatorr3"] = [[[0, 0], [-1, 0], [-2, 0]],  [], images.pngTo220r3, [-35, -2], "VR"]
        self.componentTypes["Voltage Regulator"] = ["Voltage Regulator", "Voltage Regulatorr1", "Voltage Regulatorr2", "Voltage Regulatorr3"]
        
        self.componentList["MOSFET"] = [[[0, 0], [0, 1], [0, 2]],  [], images.pngTo220, [-2, -5], "Q"]
        self.componentList["MOSFETr1"] = [[[0, 0], [1, 0], [2, 0]],  [], images.pngTo220r1, [-5, -12], "Q"]
        self.componentList["MOSFETr2"] = [[[0, 0], [0, -1], [0, -2]],  [], images.pngTo220r2, [-12, -35], "Q"]
        self.componentList["MOSFETr3"] = [[[0, 0], [-1, 0], [-2, 0]],  [], images.pngTo220r3, [-35, -2], "Q"]
        self.componentTypes["MOSFET"] = ["MOSFET", "MOSFETr1", "MOSFETr2", "MOSFETr3"]
        
        self.componentList["trimpot vertical"] = [[[0, 0], [0, 1], [0, 2]],  [], images.pngTrimpotv, [-10, -8], "R"]
        self.componentList["trimpot verticalr1"] = [[[0, 0], [1, 0], [2, 0]],  [], images.pngTrimpotvr1, [-8, -10], "R"]
        self.componentList["trimpot verticalr2"] = [[[0, 0], [0, -1], [0, -2]],  [], images.pngTrimpotvr2, [-10, -38], "R"]
        self.componentList["trimpot verticalr3"] = [[[0, 0], [-1, 0], [-2, 0]],  [], images.pngTrimpotvr3, [-38, -10], "R"]
        self.componentTypes["trimpot vertical"] = ["trimpot vertical", "trimpot verticalr1", "trimpot verticalr2", "trimpot verticalr3"]
        
        self.componentList["trimpot horizontal"] = [[[0, 0], [0, 1], [0, 2]],  [[x,y] for x in [1,2] for y in [0,1,2]], images.pngTrimpoth, [-7, -7], "R"]
        self.componentList["trimpot horizontalr1"] = [[[0, 0], [1, 0], [2, 0]],  [[x,y] for x in [0,1,2] for y in [-1,-2]], images.pngTrimpothr1, [-7, -37], "R"]
        self.componentList["trimpot horizontalr2"] = [[[0, 0], [0, -1], [0, -2]],  [[x,y] for x in [-1,-2] for y in [0,-1,-2]], images.pngTrimpothr2, [-37, -37], "R"]
        self.componentList["trimpot horizontalr3"] = [[[0, 0], [-1, 0], [-2, 0]],  [[x,y] for x in [0,-1,-2] for y in [1,2]], images.pngTrimpothr3, [-37, -7], "R"]
        self.componentTypes["trimpot horizontal"] = ["trimpot horizontal", "trimpot horizontalr1", "trimpot horizontalr2", "trimpot horizontalr3"]

        self.componentList["tac switch"] = [[[0, 0], [3, 0], [0, 2], [3, 2]],  [[0, 1], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2], [3, 1]], images.pngTacswitch, [-2, -5], "S"]
        self.componentList["tac switchr1"] = [[[0, 0], [2, 0], [0, -3], [2, -3]],  [[0, -1], [0, -2], [1, 0], [1, -1], [1, -2], [1, -3], [2, -1], [2, -2]], images.pngTacswitchr1, [-5, -47], "S"]
        self.componentTypes["tac switch"] = ["tac switch", "tac switchr1"]
 
        self.componentList["tac switch - lg"] = [
            [[0, 0], [0, 2], [5, 0], [5, 2]],
            [[x,y] for x in [0, 1, 2, 3, 4, 5] for y in [-1, 1, 3]] + [[x,y] for x in [1, 2, 3, 4] for y in [0, 2]],
            images.pngTacswitchlg, [-2, -24], "S"]
        self.componentList["tac switch - lgr1"] = [
            [[0, 0], [2, 0], [0, -5], [2, -5]],
            [[x,y] for y in [0, -1, -2, -3, -4, -5] for x in [-1, 1, 3]] + [[x,y] for y in [-1, -2, -3, -4] for x in [0, 2]],
            images.pngTacswitchlgr1, [-24, -76], "S"]
        self.componentTypes["tac Switch - large"] = ["tac switch - lg", "tac switch - lgr1"]
        
        self.componentList["SPDT slide switch"] = [[[0, 0], [0, 1], [0, 2]],  [], images.pngSwspdtslide, [-11, -12], "S"]
        self.componentList["SPDT slide switchr1"] = [[[0, 0], [1, 0], [2, 0]],  [], images.pngSwspdtslider1, [-12, -11], "S"]
        self.componentTypes["SPDT slide switch"] = ["SPDT slide switch", "SPDT slide switchr1"]
        
        self.componentList["Transistor"] = [[[0, 0], [0, 1], [0, 2]],  [], images.pngTransistor, [-7, -2], "Q"]
        self.componentList["Transistorr1"] = [[[0, 0], [1, 0], [2, 0]],  [], images.pngTransistorr1, [-2, -7], "Q"]
        self.componentTypes["Transistor"] = ["Transistor", "Transistorr1"]
        
        self.componentList["RGB LED"] = [[[0, 0], [0, 1], [0, 2], [0, 3]],  [], images.pngRgbled, [-7, -2], "LED"]
        self.componentList["RGB LEDr1"] = [[[0, 0], [1, 0], [2, 0], [3, 0]],  [], images.pngRgbledr1, [-2, -7], "LED"]
        self.componentTypes["RGB LED"] = ["RGB LED", "RGB LEDr1"]
    
    def getComponent(self, ctype):
        if not ctype in self.componentTypes.keys():
            return None
        
        cv = self.componentTypes[ctype][0]
 
        c = self.componentList[cv]       
        return FixedComponent(ctype, c[0], c[1], c[2], c[3]), c[4]

    def getComponentTypes(self):
        return sorted(self.componentTypes.keys())
    
    def nextView(self, comp):
        ct = comp.getType()
        if len(self.componentTypes[ct]) == 1:
            return
        
        cv = comp.getView()
        cv += 1
        if cv >= len(self.componentTypes[ct]):
            cv = 0
            
        self.setView(comp, cv)

    def setView(self, comp, cv):            
        ct = comp.getType()
        comp.setView(cv)
        vt = self.componentTypes[ct][cv]
        c = self.componentList[vt]
        
        comp.setConnections(c[0])
        comp.setCovered(c[1])
        comp.setBitmap(c[2])
        comp.setOffset(c[3])
        
        


LT_WIRE = 0
LT_RESISTOR = 1
LT_CAPACITOR = 2
LT_DIODE = 3

LT_LED_RED = 10
LT_LED_GREEN = 11
LT_LED_BLUE = 12
LT_LED_YELLOW = 13
LT_LED_ORANGE = 14
LT_LED_WHITE = 15
    
class StretchComponent(Component):
    def __init__(self, ctype, p1, p2, ltype):
        self.ctype = ctype
        self.ID = None
        self.p1 = p1
        self.p2 = p2
        self.ltype = ltype
        self.name = ""
        self.value = ""
        self.classification = CLASS_STRETCH

    def getXml(self):
        result = ""
        result += "<type>%s</type>" % self.ctype
        result += "<id>%s</id>" % self.ID
        result += "<pointa>%d,%d</pointa>" % (self.p1[0], self.p1[1])
        result += "<pointb>%d,%d</pointb>" % (self.p2[0], self.p2[1])
        result += "<ltype>%d</ltype>" % self.ltype
        result += "<name>%s</name>" % self.name
        result += "<value>%s</value>" % self.value
        return result
    
    def getInstructions(self):
        inst = "Install %s %s" % (self.ctype, self.ID)
        if self.name.strip() != "":
            inst += " - %s" % self.name
        if self.value.strip() != "":
            inst += " (%s) " % self.value
            
        inst += " between positions %d,%d and %d,%d" % (self.p1[0], self.p1[1], self.p2[0], self.p2[1])
        return inst
       
    def getP1(self):
        return self.p1
                
    def getP2(self):
        return self.p2
        
    def setP1(self, np1):
        self.p1 = np1
                
    def setP2(self, np2):
        self.p2 = np2
    
    def getLType(self):
        return self.ltype

WIRENAME = "Wire"
   
class StretchComponentList:
    def __init__(self):
        self.stretchNames = {}
        self.stretchNames[WIRENAME] = ["W", LT_WIRE]
        self.stretchNames["Resistor"] = ["R", LT_RESISTOR]
        self.stretchNames["Capacitor"] = ["C", LT_CAPACITOR]
        self.stretchNames["Diode"] = ["D", LT_DIODE]
        self.stretchNames["LED - Blue"] = ["LED", LT_LED_BLUE]
        self.stretchNames["LED - Green"] = ["LED", LT_LED_GREEN]
        self.stretchNames["LED - Red"] = ["LED", LT_LED_RED]
        self.stretchNames["LED - Yellow"] = ["LED", LT_LED_YELLOW]
        self.stretchNames["LED - Orange"] = ["LED", LT_LED_ORANGE]
        self.stretchNames["LED - White"] = ["LED", LT_LED_WHITE]
        
    def getWireName(self):
        return WIRENAME
        
    def getComponent(self, ctype):
        if not ctype in self.stretchNames.keys():
            return None
        
        return StretchComponent(ctype, None, None, self.stretchNames[ctype][1]), self.stretchNames[ctype][0]
    
    def getComponentNames(self):
        return self.stretchNames.keys()

    
class GrowComponent(Component):
    def __init__(self, ctype, p1, p2, pitch, image, offset):
        self.ctype = ctype
        self.p1 = p1
        self.p2 = p2
        self.pitch = pitch
        self.image = image
        self.offset = offset
        self.value = ""
        self.name = ""
        self.classification = CLASS_GROW
        
    def getPitch(self):
        return self.pitch
        
    def getXml(self):
        result = "<type>%s</type>" % self.ctype
        result += "<id>%s</id>" % self.ID
        result += "<pointa>%d,%d</pointa>" % (self.p1[0], self.p1[1])
        result += "<pointb>%d,%d</pointb>" % (self.p2[0], self.p2[1])
        result += "<name>%s</name>" % self.name
        result += "<value>%s</value>" % self.value
        return result
    
    def getInstructions(self):
        inst = "Install %s %s" % (self.ctype, self.ID)
        if self.name.strip() != "":
            inst += " - %s" % self.name
        if self.value.strip() != "":
            inst += " (%s) " % self.value
            
        inst += " between positions %d,%d and %d,%d" % (self.p1[0], self.p1[1], self.p2[0], self.p2[1])
        return inst
        
    def getP1(self):
        return self.p1
                
    def getP2(self):
        return self.p2
    
    def setP1(self, np1):
        self.p1 = np1
                
    def setP2(self, np2):
        self.p2 = np2
    
    def getImage(self):
        return self.image
    
    def getOffset(self):
        return self.offset
    
class GrowComponentList:
    def __init__(self, images):
        self.growNames = {}
        self.growNames["header"] = ["J", images.pngHeader, [-7, -7], [1,1]]
        self.growNames["term strip 2.54 vertical left"] = ["J", images.pngVertterm254l, [-9, -7], [0,1]]
        self.growNames["term strip 2.54 vertical right"] = ["J", images.pngVertterm254r, [-9, -7], [0,1]]
        self.growNames["term strip 2.54 horizontal up"] = ["J", images.pngHorterm254u, [-7, -9], [1, 0]]
        self.growNames["term strip 2.54 horizontal down"] = ["J", images.pngHorterm254d, [-7, -9], [1,0]]
        self.growNames["term strip 5.08 vertical left"] = ["J", images.pngVertterm508l, [-12, -15], [0,2]]
        self.growNames["term strip 5.08 vertical right"] = ["J", images.pngVertterm508r, [-12, -15], [0,2]]
        self.growNames["term strip 5.08 horizontal up"] = ["J", images.pngHorterm508u, [-15, -12], [2,0]]
        self.growNames["term strip 5.08 horizontal down"] = ["J", images.pngHorterm508d, [-15, -12], [2,0]]
        
    def getComponent(self, ctype):
        if not ctype in self.growNames.keys():
            return None
        
        c = self.growNames[ctype]
        return GrowComponent(ctype, None, None, c[3], c[1], c[2]), c[0]
    
    def getComponentNames(self):
        return self.growNames.keys()
