import wx 
import math
from protoboard.component import LT_LED_BLUE, LT_LED_GREEN, LT_LED_ORANGE, LT_LED_RED, LT_LED_WHITE, LT_LED_YELLOW, LT_RESISTOR, LT_DIODE, LT_CAPACITOR, LT_WIRE
from protoboard import OV_OK

clrGrid = wx.Colour(160, 160, 160)
clrGridSelect = wx.Colour(255, 255, 255)
clrBoard = wx.Colour(170, 209, 80)
clrStripe = wx.Colour(218, 165, 64)
clrNetHiLight = wx.Colour(248, 195, 94)
clrLead = wx.Colour(0, 0, 0)
clrJumper = wx.Colour(192, 192, 192)

clrResistor = wx.Colour(61, 239, 221)
clrCapacitor = wx.Colour(196, 60, 26)
clrDiode = wx.Colour(120, 120, 120)

BORDER = 10

LED_List = [LT_LED_RED, LT_LED_GREEN, LT_LED_BLUE, LT_LED_YELLOW, LT_LED_ORANGE, LT_LED_WHITE]
clrLED = {
		LT_LED_RED: wx.Colour(255, 0, 0),
		LT_LED_GREEN: wx.Colour(0, 255, 0),
		LT_LED_BLUE: wx.Colour(0, 0, 255),
		LT_LED_YELLOW: wx.Colour(255, 255, 0),
		LT_LED_ORANGE: wx.Colour(255, 128, 0),
		LT_LED_WHITE: wx.Colour(255, 255, 255),
		}

GT_HEADER = 10

AT_STRETCH = 0
AT_GROW = 1

class PBFrame (wx.Window):
	def __init__(self, parent, pb, settings):
		
		self.scale = 15
		self.transX = lambda x: x*self.scale+BORDER
		self.transY = lambda y: y*self.scale+BORDER
		self.unTransX = lambda x: float((x-BORDER))/float(self.scale)
		self.unTransY = lambda y: float((y-BORDER))/float(self.scale)
		
		self.parent = parent
		self.settings = settings
		
		self.buildarea = pb.getSize()
		self.board = pb
		
		self.selectedHole = [-1,-1]
		self.lastReport = (0,0)
		self.insideWindow = False
		self.startDrag = (0, 0)
		
		self.fixedComponent = None
		self.stretchComponent = None
		self.growComponent = None
		
		self.wireClr = wx.Colour(255, 255, 255)
		self.clrLED = wx.Colour(255, 0, 0)
		self.hiLightedNet = None
		
		self.penStripe = wx.Pen(clrStripe, self.scale-2)
		self.penJumper = wx.Pen(clrJumper, self.scale/2)
		self.penNetHiLight = wx.Pen(clrNetHiLight, self.scale-2)
		self.penGrid = wx.Pen(clrGrid, self.scale/2)
		self.penGridSelected = wx.Pen(clrGridSelect, self.scale/2)
		
		self.brushBoard = wx.Brush(clrBoard)
		
		sz = [(x-1) * self.scale + BORDER*2 for x in self.buildarea]
		
		wx.Window.__init__(self,parent,size=sz)
		self.SetClientSize(sz)
		
		self.initBuffer()
		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
		self.Bind(wx.EVT_RIGHT_DOWN, self.onRightDown)
		self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
		self.Bind(wx.EVT_LEFT_DCLICK, self.onLeftDoubleClick)
		self.Bind(wx.EVT_MOTION, self.onMotion)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.onLeaveWindow)
		self.Bind(wx.EVT_ENTER_WINDOW, self.onEnterWindow)
		
		self.Show()
		
	def selectHole(self, x, y):
		if x < 0 or x >= self.buildarea[0] or y < 0 or y >= self.buildarea[1]:
			return
		
		self.selectedHole = [x,y]
		self.refresh()
		
	def setHiLightedNet(self, pos):
		self.hiLightedNet = pos
		
	def setWireColor(self, clr):
		self.wireClr = clr
		
	def checkStretchEnd(self, pos):
		if self.stretchComponent is None:
			return
		ap = self.stretchComponent.getP1()
		if ap is None:
			return
		
		ep = self.stretchComponent.getP1()
		if ep[0] == pos[0] and ep[1] == pos[1]:
			return
		
		self.stretchComponent.setP2(pos)
		self.refresh()
	
	def checkGrowEnd(self, pos):
		if self.growComponent is None:
			return OV_OK
		
		ap = self.growComponent.getP1()
		if ap is None:
			return OV_OK
		
		ep = self.growComponent.getP1()
		if ep[0] == pos[0] and ep[1] == pos[1]:
			return OV_OK
	
		rc = self.board.checkOverlap(ap, pos)
		if rc != OV_OK:
			return rc
		
		self.growComponent.setP2(pos)
		self.refresh()
		
		return OV_OK
		
	def setFixedComponent(self, comp):
		self.fixedComponent = comp
		self.stretchComponent = None
		self.growComponent = None
		self.refresh()
		
	def setStretchComponent(self, comp):
		self.stretchComponent = comp
		self.fixedComponent = None
		self.growComponent = None
		
	def setGrowComponent(self, comp):
		self.growComponent = comp
		self.fixedComponent = None
		self.stretchComponent = None
		
	def refresh(self):
		self.redrawBoard()
		
	def onSize(self, evt):
		self.initBuffer()
		
	def onPaint(self, evt):
		if self.settings.usebuffereddc:
			dc = wx.BufferedPaintDC(self, self.buffer)
		else:
			dc = wx.PaintDC(self)
			self.drawGraph(dc, self.currentlayer)
		
	def onLeftDown(self, evt):
		pos = evt.GetPositionTuple()
		
		n = self.getHoleCoordinate(pos)
		if n is None:
			return
		
		hskp, vskp = self.board.getSkips()
		if n[0] in vskp or n[1] in hskp:
			return
		
		self.startDrag = n
		self.CaptureMouse()
		self.SetFocus()
		
		self.parent.holeClick(n)
		
	def onRightDown(self, evt):
		pos = evt.GetPositionTuple()
		
		n = self.getHoleCoordinate(pos)
		if n is None:
			return
		
		hskp, vskp = self.board.getSkips()
		if n[0] in vskp or n[1] in hskp:
			return
		
		self.parent.rightClick(n)
		
	def onLeftUp(self, evt):
		if self.HasCapture():
			self.ReleaseMouse()
		pos = evt.GetPositionTuple()
		n = self.getHoleCoordinate(pos)
		if n is None: 
			return
		
		self.parent.holeDrag(self.startDrag, n)
		
	def getHoleCoordinate(self, pos):
		x = int(self.unTransX(pos[0])+0.5)
		y = int(self.unTransY(pos[1])+0.5)
		
		if x < 0 or x >= self.buildarea[0] or y < 0 or y >= self.buildarea[1]:
			return None
		
		return [x, y]
		
	def onLeftDoubleClick(self, evt):
		pos = evt.GetPositionTuple()
		
		n = self.getHoleCoordinate(pos)
		if n is None:
			return
		
		self.parent.holeDoubleClick(n)
		
			
	def onMotion(self, evt):
		x, y = evt.GetPositionTuple()
		
		n = self.getHoleCoordinate((x,y))
		if n is None:
			return

		self.parent.reportCoordinate(n)
		self.lastReport = n

		evt.Skip()
		
	def onEnterWindow(self, evt):
		self.insideWindow = True
		self.refresh()
		
	def onLeaveWindow(self, evt):
		self.insideWindow = False
		self.refresh()
		
	def initBuffer(self):
		w, h = self.GetClientSize();
		self.buffer = wx.EmptyBitmap(w, h)
		self.redrawBoard()
		
	def redrawBoard(self):
		if self.settings.usebuffereddc:
			dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
		else:
			dc = wx.ClientDC(self)

		self.drawGraph(dc)

		if self.settings.usebuffereddc:
			del dc
			self.Refresh()
			self.Update()
			
	def eraseGraph(self):
		if self.settings.usebuffereddc:
			dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
		else:
			dc = wx.ClientDC(self)
			
		self.clearGraph(dc)
		
	def clearGraph(self, dc):
		dc.SetBackground(self.brushBoard)
		dc.Clear()
		
	def drawGraph(self, dc):
		self.clearGraph(dc)
		self.drawTraces(dc)
		self.drawJumpers(dc)
		self.drawGrid(dc)
		self.drawWires(dc)
		self.drawFixedComponents(dc)
		self.drawStretchComponents(dc)
		self.drawGrowComponents(dc)
		
		if not self.stretchComponent is None:
			ap = self.stretchComponent.getP1()
			if not ap is None:
				self.drawStretchComponent(dc, self.stretchComponent)
			
		elif not self.growComponent is None:
			ap = self.growComponent.getP1()
			if not ap is None:
				self.drawGrowComponent(dc, self.growComponent)
			
		elif not self.fixedComponent is None and self.insideWindow:
			self.drawFixedComponent(dc, self.fixedComponent)

	def drawGrid(self, dc):
		col, row = self.board.getSize()
		hskp, vskp = self.board.getSkips()
		dc.SetPen(self.penGrid)
		for x in range(0, col):
			if x in vskp:
				continue
			
			px = self.transX(x)
			for y in range(0, row):
				if y in hskp:
					continue
				
				py = self.transY(y)
				if x == self.selectedHole[0] and y == self.selectedHole[1]:
					dc.SetPen(self.penGridSelected)
					dc.DrawLine(px, py, px, py)
					dc.SetPen(self.penGrid)
				else:
					dc.DrawLine(px, py, px, py)
					
	def drawTraces(self, dc):
		for trc in self.board.getTraces():
			x1 = self.transX(trc[0])
			x2 = self.transX(trc[2])
			y1 = self.transY(trc[1])
			y2 = self.transY(trc[3])
			if not self.hiLightedNet is None:
				if self.board.isConnected(self.hiLightedNet, [trc[0], trc[1]]):
					dc.SetPen(self.penNetHiLight)
				else:
					dc.SetPen(self.penStripe)
			else:
				dc.SetPen(self.penStripe)
			dc.DrawLine(x1, y1, x2, y2)
					
	def drawJumpers(self, dc):
		for jmp in self.board.getJumpers():
			jv = jmp.getP1P2()
			x1 = self.transX(jv[0])
			x2 = self.transX(jv[2])
			y1 = self.transY(jv[1])
			y2 = self.transY(jv[3])
			dc.SetPen(self.penJumper)
			dc.DrawLine(x1, y1, x2, y2)
				
	def drawWires(self, dc):
		for w in self.board.getWireList():
			p1 = w.getP1()
			p2 = w.getP2()
			clr = w.getColor()
			
			x1 = self.transX(p1[0])
			y1 = self.transY(p1[1])
			x2 = self.transX(p2[0])
			y2 = self.transY(p2[1])
			
			pen = wx.Pen(clr, self.scale/2)
			dc.SetPen(pen)
			dc.DrawLine(x1, y1, x2, y2)
			
	def drawStretchComponents(self, dc):
		for c in self.board.getStretchComponentList():
			self.drawStretchComponent(dc, c)
		
	def drawStretchComponent(self, dc, c):
		p1 = c.getP1()
		p2 = c.getP2()
		lt = c.getLType()
		x1 = self.transX(p1[0])
		y1 = self.transY(p1[1])
		
		x2 = self.transX(p2[0])
		y2 = self.transY(p2[1])
		
		if lt in [LT_RESISTOR, LT_CAPACITOR]:
			compLength = 10
		elif lt in LED_List:
			compLength = 1
		elif lt == LT_DIODE:
			compLength = 8
		else:
			compLength = 0
		
		xd = x2 - x1
		yd = y2 - y1
		llen = math.hypot(xd, yd)
		
		if compLength*2 >= llen and lt in [LT_RESISTOR, LT_CAPACITOR, LT_DIODE]:
			drawVert = True
		else:
			drawVert = False

		if drawVert:
			if lt == LT_RESISTOR:
				cpen = wx.Pen(clrResistor, 12)
				cpen.SetCap(wx.CAP_ROUND)
			elif lt == LT_CAPACITOR:
				cpen = wx.Pen(clrCapacitor, 12)
				cpen.SetCap(wx.CAP_ROUND)
			elif lt == LT_DIODE:
				cpen = wx.Pen(clrDiode, 12)
				cpen.SetCap(wx.CAP_ROUND)
				
			dc.SetPen(cpen)
			dc.DrawLine(x1, y1, x1, y1)
				
		if lt == LT_WIRE:
			pen = wx.Pen(self.wireClr, self.scale/2)
		else:
			pen = wx.Pen(clrLead, 2)
			
		dc.SetPen(pen)
		dc.DrawLine(x1, y1, x2, y2)
			
		if drawVert or lt == LT_WIRE:
			return
			
		rise = float(y2 - y1)
		run = float(x2 - x1)
		xmid = (x1 + x2)/2
		ymid = (y1 + y2)/2

		try:
			theta = math.atan(rise/run)
			rise = compLength*math.sin(theta)
			run = compLength*math.cos(theta)
		except ZeroDivisionError:
			run = 0
			rise = compLength
		
		if lt == LT_RESISTOR:
			cpen = wx.Pen(clrResistor, 8)
			cpen.SetCap(wx.CAP_BUTT)
		elif lt == LT_CAPACITOR:
			cpen = wx.Pen(clrCapacitor, 8)
			cpen.SetCap(wx.CAP_BUTT)
		elif lt == LT_DIODE:
			cpen = wx.Pen(clrDiode, 8)
			cpen.SetCap(wx.CAP_BUTT)
		elif lt in LED_List:
			cpen = wx.Pen(clrLED[lt], 12)
			cpen.SetCap(wx.CAP_ROUND)
			
		dc.SetPen(cpen)
		dc.DrawLine(xmid+run, ymid+rise, xmid-run, ymid-rise)

	def drawGrowComponents(self, dc):
		for c in self.board.getGrowComponentList():
			self.drawGrowComponent(dc, c)
		
	def drawGrowComponent(self, dc, c):
		p1 = c.getP1()
		p2 = c.getP2()
		image = c.getImage()
		offset = c.getOffset()
		pitch = c.getPitch()
		
		sx = p1[0]
		ex = p2[0]
		if ex < sx:
			dirx = -1
			ex -= 1
		else:
			dirx = 1
			ex += 1

		sy = p1[1]
		ey = p2[1]
		if ey < sy:
			diry = -1
			ey -= 1
		else:
			diry = 1
			ey += 1

		if pitch[0] == 0:
			incx = 1
			dirx = 1
			ex = sx+1
		else:
			incx = pitch[0]
			
		if pitch[1] == 0:
			incy = 1
			diry = 1
			ey = sy+1
		else:
			incy = pitch[1]

		for x in range(sx, ex, incx*dirx):
			cx = self.transX(x)
			for y in range(sy, ey, incy*diry):
				cy = self.transY(y)
				dc.DrawBitmap(image, cx+offset[0], cy+offset[1])

	def drawFixedComponents(self, dc):
		for c in self.board.getComponentList():
			self.drawFixedComponent(dc, c)

	def drawFixedComponent(self, dc, c):
		offset = c.getOffset()
		pos = c.getAnchor()
		if pos is None:
			pos = self.lastReport
		ax = self.transX(pos[0])+offset[0]
		ay = self.transY(pos[1])+offset[1]
		dc.DrawBitmap(c.getBitmap(), ax, ay)

	def drawComponent(self, dc, c, anchor):
		pts = c.getDrawingPoints()
		
		prev = None
		
		pen = wx.Pen(wx.Colour(0,0,0), self.scale/4)
		dc.SetPen(pen)
		cx = anchor[0]
		cy = anchor[1]
		
		for pt in pts:
			if not prev is None:
				x1 = self.transX(prev[0]+cx)
				y1 = self.transY(prev[1]+cy)
				x2 = self.transX(pt[0]+cx)
				y2 = self.transY(pt[1]+cy)
				dc.DrawLine(x1, y1, x2, y2)
			prev = pt
