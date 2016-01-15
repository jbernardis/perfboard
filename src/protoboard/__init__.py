'''
Created on Dec 21, 2015

@author: ejefber
'''
class ProtoBoardPositionError(Exception):
    pass 

from protoboard.wire import Wire
from protoboard.jumper import Jumper
from protoboard.component import CLASS_FIXED, CLASS_STRETCH, CLASS_WIRE, CLASS_GROW

OV_OK = 0
OV_SKIPPED_HOLE = 1
OV_OVERLAP = 2

class ProtoBoard(object):
    def __init__(self, cols, rows):
        self.hTraces = []
        self.vTraces = []
        self.vSkips = []
        self.hSkips = []
        self.hCuts = []
        self.vCuts = []
        self.removals = []
        self.jumpers = []
        self.nrows = rows
        self.ncols = cols
        self.wires = []
        self.components = []
        self.stretchComponents = []
        self.growComponents = []
        self.modified = False
        
    def clearTraces(self):
        self.hTraces = []
        self.vTraces = []
        
    def clearSkips(self):
        self.vSkips = []
        self.hSkips = []
        
    def getXml(self):
        result = "<stripboard>\n"
        result += "<size>%d,%d</size>\n" % (self.ncols, self.nrows)
        
        result += "<htraces>\n"
        for t in self.hTraces:
            result += "<trace>%d,%d,%d</trace>\n" % (t[0], t[1], t[2])
        result += "</htraces>\n"
        
        result += "<vtraces>\n"
        for t in self.vTraces:
            result += "<trace>%d,%d,%d</trace>\n" % (t[0], t[1], t[2])
        result += "</vtraces>\n"
        
        result += "<hskips>" + ",".join(["%d" % x for x in self.hSkips]) + "</hskips>\n"
        
        result += "<vskips>" + ",".join(["%d" % x for x in self.vSkips]) + "</vskips>\n"
        
        result += "<hcuts>\n"
        for c in self.hCuts:
            result += "<cut>%d,%d,%d</cut>\n" % (c[0], c[1], c[2])
        result += "</hcuts>\n"
        
        result += "<vcuts>\n"
        for c in self.vCuts:
            result += "<cut>%d,%d,%d</cut>\n" % (c[0], c[1], c[2])
        result += "</vcuts>\n"
        
        result += "<removals>\n"
        for r in self.removals:
            result += "<removal>%d,%d</removal>\n" % (r[0], r[1])
        result += "</removals>\n"
        
        result += "<jumpers>\n"
        for j in self.jumpers:
            result += "<jumper>" + j.getXml() + "</jumper>\n"
        result += "</jumpers>\n"
        
        result += "<wires>\n"
        for w in self.wires:
            result += "<wire>" + w.getXml() + "</wire>\n"
        result += "</wires>\n"

        result += "<components>\n"
        for c in self.components:
            result += "<component>" + c.getXml() + "</component>\n"
        result += "</components>\n"
        
        result += "<stretchcomponents>\n"
        for c in self.stretchComponents:
            result += "<component>" + c.getXml() + "</component>\n"
        result += "</stretchcomponents>\n"
        
        result += "<growcomponents>\n"
        for c in self.growComponents:
            result += "<component>" + c.getXml() + "</component>\n"
        result += "</growcomponents>\n"
        
        result += "</stripboard>"
        
        return result
    
    def getInstructions(self):
        instr = []
        for c in self.hCuts:
            instr.append("Cut horizontal trace row %d between columns %s and %d" % (c[2], c[0], c[1]))
        
        for c in self.vCuts:
            instr.append("Cut Vertical trace column %d between rows %s and %d" % (c[0], c[1], c[2]))
        
        for r in self.removals:
            instr.append("Remove trace surrounding position %d,%d" % (r[0], r[1]))

        for j in self.jumpers:
            instr.append(j.getInstructions())

        for w in self.wires:
            instr.append(w.getInstructions())
            
        for c in self.components:
            instr.append(c.getInstructions())
            
        for c in self.stretchComponents:
            instr.append(c.getInstructions())
            
        for c in self.growComponents:
            instr.append(c.getInstructions())
        
        return instr
        
    def setModified(self, flag=True):
        self.modified = flag
        
    def isModified(self):
        return self.modified
        
    def deleteByPosition(self, pos):
        for wx in range(len(self.wires)):
            if pos == self.wires[wx].getP1():
                del self.wires[wx]
                self.setModified()
                return True
            if pos == self.wires[wx].getP2():
                del self.wires[wx]
                self.setModified()
                return True
            
        for wx in range(len(self.stretchComponents)):
            if pos == self.stretchComponents[wx].getP1():
                del self.stretchComponents[wx]
                self.setModified()
                return True
            if pos == self.stretchComponents[wx].getP2():
                del self.stretchComponents[wx]
                self.setModified()
                return True
            
        for cx in range(len(self.components)):
            c = self.components[cx]
            a = c.getAnchor()
            for p in c.getConnections():
                if pos[0] == p[0]+a[0] and pos[1] == p[1]+a[1]:
                    del self.components[cx]
                    self.setModified()
                    return True
             
        for cx in range(len(self.growComponents)):
            c = self.growComponents[cx]
            p1 = c.getP1()
            p2 = c.getP2()
            
            minx = p1[0]
            maxx = p2[0]
            if maxx < minx:
                minx = p2[0]
                maxx = p1[0]
                
            miny = p1[1]
            maxy = p2[1]
            if maxy < miny:
                miny = p2[1]
                maxy = p1[1]
                
            if minx <= pos[0] and pos[0] <= maxx and miny <= pos[1] and pos[1] <= maxy:
                del(self.growComponents[cx])
                self.setModified()
                return True
          
        return False
        
    def findByPosition(self, pos, delete=False):
        for wx in range(len(self.wires)):
            w = self.wires[wx]
            if pos == w.getP1() or pos == w.getP2():
                if delete:
                    del(self.wires[wx])
                    self.setModified()
                return w, CLASS_WIRE
            
        for cx in range(len(self.stretchComponents)):
            c = self.stretchComponents[cx]
            if pos == c.getP1() or pos == c.getP2():
                if delete:
                    del(self.stretchComponents[cx])
                    self.setModified()
                return c, CLASS_STRETCH
            
        for cx in range(len(self.components)):
            c = self.components[cx]
            a = c.getAnchor()
            for p in c.getConnections():
                if pos[0] == p[0]+a[0] and pos[1] == p[1]+a[1]:
                    if delete:
                        del(self.components[cx])
                        self.setModified()
                    return c, CLASS_FIXED
             
        for cx in range(len(self.growComponents)):
            c = self.growComponents[cx]
            p1 = c.getP1()
            p2 = c.getP2()
            
            minx = p1[0]
            maxx = p2[0]
            if maxx < minx:
                minx = p2[0]
                maxx = p1[0]
                
            miny = p1[1]
            maxy = p2[1]
            if maxy < miny:
                miny = p2[1]
                maxy = p1[1]
                
            if minx <= pos[0] and pos[0] <= maxx and miny <= pos[1] and pos[1] <= maxy:
                if delete:
                    del(self.growComponents[cx])
                    self.setModified()
                return c, CLASS_GROW
          
        return None, None
    
    def isConnected(self, p1, p2):
        if self.sameTrace(p1, p2):
            return True
        
        for w in self.wires:
            w.followed = False
        for j in self.jumpers:
            j.followed = False
            
        return self.followWires(p1, p2)
 
    def sameTrace(self, p1, p2):
        if p1[0] != p2[0] and p1[1] != p2[1]:
            return False
        
        if p1[0] == p2[0] and p1[1] == p2[1]:
            return True
        
        if p1[0] == p2[0]: # same X - look in vTraces
            for t in self.vTraces:
                if t[0] != p1[0]:
                    continue
                if t[1] <= p1[1] and t[1] <= p2[1] and t[2] >= p1[1] and t[2] >= p2[1]:
                    return self.checkVTraceBreaks(t, p1, p2)
            return False
        
        elif p1[1] == p2[1]: # same y - look in hTraces
            for t in self.hTraces:
                if t[2] != p1[1]:
                    continue
                if t[0] <= p1[0] and t[0] <= p2[0] and t[1] >= p1[0] and t[1] >= p2[0]:
                    return self.checkHTraceBreaks(t, p1, p2)
            return False
        
        return False
        
    def checkVTraceBreaks(self, t, p1, p2):
        for r in self.removals:
            if r[0] != t[0]:
                continue
            if p1[1] < r[1] and r[1] < p2[1]:
                return False
            if p2[1] < r[1] and r[1] < p1[1]:
                return False
            
        for c in self.vCuts:
            if c[0] != t[0]:
                continue
            
            if p1[1] <= c[1] and c[2] <= p2[1]:
                return False
            if p2[1] <= c[1] and c[2] <= p1[1]:
                return False
            
        return True
        
    def checkHTraceBreaks(self, t, p1, p2):
        for r in self.removals:
            if r[1] != t[2]:
                continue
            if p1[0] < r[0] and r[0] < p2[0]:
                return False
            if p2[0] < r[0] and r[0] < p1[0]:
                return False
            
        for c in self.hCuts:
            if c[2] != t[2]:
                continue
            
            if p1[0] <= c[0] and c[1] <= p2[0]:
                return False
            if p2[0] <= c[0] and c[1] <= p1[0]:
                return False
 
        return True
    
    def followWires(self, p1, p2):
        for w in self.wires:
            if w.followed:
                continue
            
            if self.sameTrace(p1, w.getP1()):
                pw = w.getP2()
            elif self.sameTrace(p1, w.getP2()):
                pw = w.getP1()
            else:
                pw = None
                
            if not pw is None:
                w.followed = True
                if self.sameTrace(p2, pw):
                    return True
                
                if self.followWires(pw, p2):
                    return True
                w.followed = False
                
        for j in self.jumpers:
            if j.followed:
                continue
            
            if self.sameTrace(p1, j.getP1()):
                pw = j.getP2()
            elif self.sameTrace(p1, j.getP2()):
                pw = j.getP1()
            else:
                pw = None
                
            if not pw is None:
                j.followed = True
                if self.sameTrace(p2, pw):
                    return True
                
                if self.followWires(pw, p2):
                    return True
                j.followed = False
                
        return False
    
    def checkOverlap(self, p1, p2):
        xa = p1[0]
        xb = p2[0]
        if xb < xa:
            xa = p2[0]
            xb = p1[0]
            
        ya = p1[1]
        yb = p2[1]
        if yb < ya:
            ya = p2[1]
            yb = p1[1]
            
        region = [[x,y] for x in range(xa,xb+1) for y in range(ya,yb+1)]
       
        for s in self.vSkips:
            for y in range(self.nrows):
                if [s, y] in region:
                    return OV_SKIPPED_HOLE
        
        for s in self.hSkips:
            for x in range(self.ncols):
                if [x, s] in region:
                    return OV_OVERLAP
        
        for w in self.wires:
            if w.getP1() in region or w.getP2() in region:
                return OV_OVERLAP
            
        for c in self.components:
            a = c.getAnchor()
            pts = c.getCovered()
            for p in pts:
                if [p[0]+a[0], p[1]+a[1]] in region:
                    return OV_OVERLAP

        for c in self.stretchComponents:
            if c.getP1() in region or c.getP2() in region:
                return OV_OVERLAP
            
        for c in self.growComponents:
            p1 = c.getP1()
            p2 = c.getP2()
            
            x1 = p1[0]
            x2 = p2[0]
            if x2 < x1:
                x1 = p2[0]
                x2 = p1[0]
                
            y1 = p1[1]
            y2 = p2[1]
            if y2 < y1:
                y1 = p2[1]
                y2 = p1[1]
                
            for x in range(x1, x2+1):
                for y in range(y1, y2+1):
                    if [x,y] in region:
                        return OV_OVERLAP
            
        return OV_OK
        
    def occupied(self, pos, covered=True):
        for w in self.wires:
            p = w.getP1()
            if pos[0] == p[0] and pos[1] == p[1]:
                return True
            p = w.getP2()
            if pos[0] == p[0] and pos[1] == p[1]:
                return True
            
        for c in self.components:
            a = c.getAnchor()
            if covered:
                pts = c.getCovered()
            else:
                pts = c.getConnections()
            for p in pts:
                if pos[0] == p[0]+a[0] and pos[1] == p[1]+a[1]:
                    return True
             
        for w in self.stretchComponents:
            p = w.getP1()
            if pos[0] == p[0] and pos[1] == p[1]:
                return True
            p = w.getP2()
            if pos[0] == p[0] and pos[1] == p[1]:
                return True
            
        for w in self.growComponents:
            p1 = w.getP1()
            p2 = w.getP2()
            
            minx = p1[0]
            maxx = p2[0]
            if maxx < minx:
                minx = p2[0]
                maxx = p1[0]
                
            miny = p1[1]
            maxy = p2[1]
            if maxy < miny:
                miny = p2[1]
                maxy = p1[1]
                
            if minx <= pos[0] and pos[0] <= maxx and miny <= pos[1] and pos[1] <= maxy:
                return True
             
        return False
         
    def addWire(self, comp, color):
        self.setModified()
        self.wires.append(Wire(comp.getP1(), comp.getP2(), color))
        
    def getWireList(self):
        return self.wires
        
    def addComponent(self, comp):
        self.setModified()
        if comp.getAnchor() is None:
            comp.setAnchor([0,0])
        self.components.append(comp)
        
    def getComponentList(self):
        return self.components
    
    def addStretchComponent(self, comp):
        self.setModified()
        self.stretchComponents.append(comp)
        
    def getStretchComponentList(self):
        return self.stretchComponents
    
    def addGrowComponent(self, comp):
        self.setModified()
        self.growComponents.append(comp)
        
    def getGrowComponentList(self):
        return self.growComponents

    def getSize(self):
        return [self.ncols, self.nrows]
    
    def noTrace(self, pos):
        if pos[0] < 0 or pos[0] >= self.ncols:
            raise ProtoBoardPositionError
        
        if pos[1] < 0 or pos[1] >= self.nrows:
            raise ProtoBoardPositionError
        
        if pos[0] in self.vSkips or pos[1] in self.hSkips:
            return True
        
        if pos in self.removals:
            return True
        
        return False
    
    def traceRemoved(self, pos):
        if pos[0] < 0 or pos[0] >= self.ncols:
            raise ProtoBoardPositionError
        
        if pos[1] < 0 or pos[1] >= self.nrows:
            raise ProtoBoardPositionError
        
        return pos in self.removals
    
    def traceRemovable(self, pos):
        if pos[0] < 0 or pos[0] >= self.ncols:
            raise ProtoBoardPositionError
        
        if pos[1] < 0 or pos[1] >= self.nrows:
            raise ProtoBoardPositionError
        
        if pos[0] in self.vSkips or pos[1] in self.hSkips:
            return False
        
        return True
    
    def addHCut(self, col1, col2, row):
        if col1 < 0 or col1 >= self.ncols:
            raise ProtoBoardPositionError
         
        if col2 < 0 or col2 >= self.ncols:
            raise ProtoBoardPositionError
        
        if row < 0 or row >= self.nrows:
            raise ProtoBoardPositionError
        
        if col1 < col2:
            self.hCuts.append([col1, col2, row])
        else:
            self.hCuts.append([col2, col1, row])
            
    def delHCut(self, col1, col2, row):
        if col1 < 0 or col1 >= self.ncols:
            raise ProtoBoardPositionError
         
        if col2 < 0 or col2 >= self.ncols:
            raise ProtoBoardPositionError
        
        if row < 0 or row >= self.nrows:
            raise ProtoBoardPositionError
        
        if col1 < col2:
            t = [col1, col2, row]
        else:
            t = [col2, col1, row]
            
        if t in self.hCuts:
            self.hCuts.remove(t)
            self.pruneWires()
            return True
        
        return False
        
    def addVCut(self, col, row1, row2):
        if col < 0 or col >= self.ncols:
            raise ProtoBoardPositionError
        
        if row1 < 0 or row1 >= self.nrows:
            raise ProtoBoardPositionError
        
        if row2 < 0 or row2 >= self.nrows:
            raise ProtoBoardPositionError
        
        if row1 < row2:
            self.vCuts.append([col, row1, row2])
        else:
            self.vCuts.append([col, row2, row1])
        
    def delVCut(self, col, row1, row2):
        if col < 0 or col >= self.ncols:
            raise ProtoBoardPositionError
        
        if row1 < 0 or row1 >= self.nrows:
            raise ProtoBoardPositionError
        
        if row2 < 0 or row2 >= self.nrows:
            raise ProtoBoardPositionError
        
        if row1 < row2:
            t = [col, row1, row2]
        else:
            t = [col, row2, row1]
            
        if t in self.vCuts:
            self.vCuts.remove(t)
            self.pruneWires()
            return True
        
        return False
 
    def addJumper(self, pos1, pos2):
        if pos1[1] < 0 or pos1[1] >= self.nrows:
            raise ProtoBoardPositionError
        
        if pos1[0] < 0 or pos1[0] >= self.ncols:
            raise ProtoBoardPositionError
        
        if pos2[1] < 0 or pos2[1] >= self.nrows:
            raise ProtoBoardPositionError
        
        if pos2[0] < 0 or pos2[0] >= self.ncols:
            raise ProtoBoardPositionError
        
        if pos1[0] in self.vSkips or pos1[1] in self.hSkips:
            return
            raise ProtoBoardPositionError
        
        if pos2[0] in self.vSkips or pos2[1] in self.hSkips:
            return False
        
        j = self.orderJumper(pos1, pos2)       
        
        for jmp in self.jumpers:
            if j == jmp.getP1P2():
                return False
        
        self.jumpers.append(Jumper([j[0], j[1]], [j[2], j[3]]))
        self.setModified()
        return True
        
    def delJumper(self, pos1, pos2):
        j = self.orderJumper(pos1, pos2)
        
        for jx in range(len(self.jumpers)):
            jmp = self.jumpers[jx]
            if j == jmp.getP1P2():
                del self.jumpers[jx]
                self.setModified()
                return
            
    def orderJumper(self, pos1, pos2):
        if pos1[0] < pos2[0]:
            ax = pos1[0]
            ay = pos1[1]
            bx = pos2[0]
            by = pos2[1]
        elif pos1[0] == pos2[0]:
            if pos1[1] <= pos2[1]:
                ax = pos1[0]
                ay = pos1[1]
                bx = pos2[0]
                by = pos2[1]
            else:
                ax = pos2[0]
                ay = pos2[1]
                bx = pos1[0]
                by = pos1[1]
        else:
            ax = pos2[0]
            ay = pos2[1]
            bx = pos1[0]
            by = pos1[1]
        return [ax, ay, bx, by]

            
    def getJumpers(self):
        return self.jumpers
               
    def traceRemove(self, pos):
        if pos[1] < 0 or pos[1] >= self.nrows:
            raise ProtoBoardPositionError
        
        if pos[0] < 0 or pos[0] >= self.ncols:
            raise ProtoBoardPositionError
        
        if pos[0] in self.vSkips or pos[1] in self.hSkips:
            return
        
        if pos in self.removals:
            return
        
        self.setModified()
        self.removals.append(pos)
        
    def traceReplace(self, pos):
        if pos in self.removals:
            self.removals.remove(pos)
            self.pruneWires()
            self.setModified()
            
    def pruneWires(self):
        nw = []
        pruned = False
        for w in self.wires:
            if not self.sameTrace(w.getP1(), w.getP2()):
                nw.append(w)
            else:
                pruned = True
                
        if pruned:
            self.wires = nw
        
    def addHTrace(self, col1, col2, row):
        if col1 < 0 or col1 >= self.ncols:
            raise ProtoBoardPositionError
         
        if col2 < 0 or col2 >= self.ncols:
            raise ProtoBoardPositionError
        
        if row < 0 or row >= self.nrows:
            raise ProtoBoardPositionError
        
        self.hTraces.append([col1, col2, row])
        
    def addVTrace(self, col, row1, row2):
        if col < 0 or col >= self.ncols:
            raise ProtoBoardPositionError
        
        if row1 < 0 or row1 >= self.nrows:
            raise ProtoBoardPositionError
        
        if row2 < 0 or row2 >= self.nrows:
            raise ProtoBoardPositionError
        
        self.vTraces.append([col, row1, row2])
                 
    def getTraces(self):
        result = []
        for t in self.hTraces:
            result.extend(self.splitHTrace(t))
        for t in self.vTraces:
            result.extend(self.splitVTrace(t))
            
        return result
    
    def getHTraces(self):
        return self.hTraces
    
    def getVTraces(self):
        return self.vTraces
    
    def splitHTrace(self, t):
        result = []
        x1 = t[0]
        x2 = t[1]
        y = t[2]
        
        brks = []
        for r in self.removals:
            if r[1] == y and (r[0] >= x1 and r[0] <= x2):
                brks.append((r[0], None))
                
        for c in self.hCuts:
            if c[2] == y and (c[0] >= x1 and c[0] <= x2) and (c[1] >= x1 and c[1] <= x2):
                brks.append((c[0], c[1]))
 
        sx = x1               
        for b in sorted(brks):
            if b[1] is None:
                ex = b[0] - 1;
            else:
                ex = b[0]
                
            if sx <= ex:
                result.append([sx, y, ex, y])
                
            if b[1] is None:
                sx = b[0] + 1;
            else:
                sx = b[1]
        
        if sx <= x2:
            result.append([sx, y, x2, y])
        
        return result
    
    def splitVTrace(self, t):
        result = []
        x = t[0]
        y1 = t[1]
        y2 = t[2]

        brks = []
        for r in self.removals:
            if r[0] == x and (r[1] >= y1 and r[1] <= y2):
                brks.append((r[1], None))
                
        for c in self.vCuts:
            if c[0] == x and (c[1] >= y1 and c[1] <= y2) and (c[2] >= y1 and c[2] <= y2):
                brks.append((c[1], c[2]))

        sy = y1               
        for b in sorted(brks):
            if b[1] is None:
                ey = b[0] - 1;
            else:
                ey = b[0]
                
            if sy <= ey:
                result.append([x, sy, x, ey])
                
            if b[1] is None:
                sy = b[0] + 1;
            else:
                sy = b[1]
        
        if sy <= y2:
            result.append([x, sy, x, y2])
            
        return result
    
    def addHSkip(self, row):
        if row < 0 or row >= self.nrows:
            raise ProtoBoardPositionError

        self.hSkips.append(row)
    
    def addVSkip(self, col):
        if col < 0 or col >= self.ncols:
            raise ProtoBoardPositionError

        self.vSkips.append(col)
    
    def getSkips(self):
        return self.hSkips, self.vSkips
         
