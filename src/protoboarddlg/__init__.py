'''
Created on Dec 21, 2015

@author: ejefber 
'''
import os
import re
import wx 
import copy
from protoboarddlg.pbframe import PBFrame
from protoboard.component import compID, WIRENAME, CLASS_WIRE, CLASS_FIXED, CLASS_STRETCH, CLASS_GROW
from protoboard import OV_OVERLAP, OV_SKIPPED_HOLE
from protoboarddlg.infodlg import InfoDialog
from pbprint import PBPrint
from pbview import ProtoBoardView
from pbinstrprint import PBInstructionsPrint
from protoboarddlg.movedlg import MoveDlg
from protoboarddlg.trimdlg import TrimDlg

TBDIM = (48, 48)

TOOL_CUT = 10
TOOL_EXAMINE = 20
TOOL_NAME = 30
TOOL_WIRE = 40
TOOL_COMPONENT = 50
TOOL_STRETCH = 60
TOOL_GROW = 70
TOOL_GRAB = 80
TOOL_MOVE = 85
TOOL_TRIM = 90
TOOL_TRASH = 99

rePrefix = re.compile("[a-zA-Z]+")

toolHintText = {
	TOOL_CUT : ["Double click on the board to remove or replace trace", "Drag to cut/uncut between holes or to jumper between adjacent traces"],
	TOOL_EXAMINE : ["Double click on the board to see inter-connected traces",""],
	TOOL_NAME : ["Double click on a component to change its name and/or value",""],
	TOOL_WIRE : ["Add a wire - double click start and end points, right click to re-anchor", "right click tool for colors"],
	TOOL_COMPONENT : ["Add a fixed-shape component.  Double click for placement, right click to rotate", "right click tool for component choices"],
	TOOL_STRETCH : ["Add a stretchable component.  Double click each end for placement, right click to re-anchor", "right click tool for component choices"],
	TOOL_GROW: ["Add a growable component.  Double click each end for placement, right click to re-anchor", "right click tool for component choices"],
	TOOL_GRAB: ["Double click a component to select it for editing",""],
	TOOL_MOVE: ["Double click a component to to move it",""],
	TOOL_TRIM: ["Resize board by adding/trimming rows and columns",""],
	TOOL_TRASH : ["Delete - double click an item to delete it",""]
	}

wildcard = "Proto-board file (*.pb)|*.pb"
TITLETEXT = "Proto-Board Layout Editor"
	
class ProtoBoardDialog(wx.Dialog):
	def __init__(self, parent, pb, fn, settings):
		self.parent = parent 
		
		title = TITLETEXT
		if not fn is None:
			title += " - %s" % fn	   
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(400, 400))
		self.SetBackgroundColour("white")
		
		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_LETTER)
		self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

		self.pb = pb
		self.pbView = None
		self.prevPosition = [-1, -1]
		self.fileName = fn
		self.SetClientSize((600, 300))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.dx = 0
		self.dy = 0
		
		self.settings = settings
		self.images = settings.images
		self.compImages = settings.compImages
		self.fixedComponentList = settings.fixedComponentList
		self.stretchComponentList = settings.stretchComponentList
		self.growComponentList = settings.growComponentList
		
		self.fixedComponentTypes = self.fixedComponentList.getComponentTypes()
		self.currentFixedComponentChoice = self.fixedComponentTypes[0]

		self.stretchComponentNames = self.stretchComponentList.getComponentNames()
		if WIRENAME in self.stretchComponentNames:
			self.stretchComponentNames.remove(WIRENAME)
		self.currentStretchName = self.stretchComponentNames[0]

		self.growComponentNames = self.growComponentList.getComponentNames()
		self.currentGrowComponentChoice = self.growComponentNames[0]

		self.currentComponentPrefix = ""
		self.currentFixedComponent = None
		self.currentStretchComponent = None
		self.currentGrowComponent = None
		
		self.wireColor = wx.Colour(0, 255, 0)
		self.lastReport = []
				
		self.tb = wx.BoxSizer(wx.HORIZONTAL)
		self.tb.AddSpacer((20, 20))

		self.tbExamine = wx.BitmapButton(self, wx.ID_ANY, self.images.pngView, size=TBDIM)
		self.tbExamine.SetToolTipString("Examine the trace/wire network")
		self.Bind(wx.EVT_BUTTON, self.onExamine, self.tbExamine)
		self.tb.Add(self.tbExamine)

		self.tbName = wx.BitmapButton(self, wx.ID_ANY, self.images.pngProperties, size=TBDIM)
		self.tbName.SetToolTipString("Assign name and/or value to a component")
		self.Bind(wx.EVT_BUTTON, self.onName, self.tbName)
		self.tb.Add(self.tbName)
		
		self.tb.AddSpacer((20, 20))
		
		self.tbCut = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCut, size=TBDIM)
		self.tbCut.SetToolTipString("Cut/replace traces and/or jumpers")
		self.Bind(wx.EVT_BUTTON, self.onCut, self.tbCut)
		self.tb.Add(self.tbCut)
		
		self.tbWire = wx.BitmapButton(self, wx.ID_ANY, self.images.pngWire, size=TBDIM)
		self.tbWire.SetToolTipString("Add a wire to the circuit")
		self.Bind(wx.EVT_BUTTON, self.onWire, self.tbWire)
		self.tbWire.Bind(wx.EVT_RIGHT_DOWN, self.onColor)
		self.tb.Add(self.tbWire)
		
		self.tbComponent = wx.BitmapButton(self, wx.ID_ANY, self.images.pngComponent, size=TBDIM)
		self.tbComponent.SetToolTipString("Add a fixed-shape component")
		self.Bind(wx.EVT_BUTTON, self.onComponent, self.tbComponent)
		self.tbComponent.Bind(wx.EVT_RIGHT_DOWN, self.onChooseComponent)
		self.tb.Add(self.tbComponent)
		
		self.tbStretch = wx.BitmapButton(self, wx.ID_ANY, self.images.pngStretch, size=TBDIM)
		self.tbStretch.SetToolTipString("Add a stretchable component")
		self.Bind(wx.EVT_BUTTON, self.onStretch, self.tbStretch)
		self.tbStretch.Bind(wx.EVT_RIGHT_DOWN, self.onChooseStretch)
		self.tb.Add(self.tbStretch)
		
		self.tbGrow = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGrow, size=TBDIM)
		self.tbGrow.SetToolTipString("Add a growable component")
		self.Bind(wx.EVT_BUTTON, self.onGrow, self.tbGrow)
		self.tbGrow.Bind(wx.EVT_RIGHT_DOWN, self.onChooseGrow)
		self.tb.Add(self.tbGrow)
		
		self.tb.AddSpacer((50, 20))

		self.tbGrab = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGrab, size=TBDIM)
		self.tbGrab.SetToolTipString("Select item")
		self.Bind(wx.EVT_BUTTON, self.onGrab, self.tbGrab)
		self.tb.Add(self.tbGrab)
		
		self.tbMove = wx.BitmapButton(self, wx.ID_ANY, self.images.pngMove, size=TBDIM)
		self.tbMove.SetToolTipString("Move item")
		self.Bind(wx.EVT_BUTTON, self.onMove, self.tbMove)
		self.tb.Add(self.tbMove)
		
		self.tbTrim = wx.BitmapButton(self, wx.ID_ANY, self.images.pngResize, size=TBDIM)
		self.tbTrim.SetToolTipString("Resize PCB")
		self.Bind(wx.EVT_BUTTON, self.onTrim, self.tbTrim)
		self.tb.Add(self.tbTrim)
		
		self.tb.AddSpacer((30, 20))
		
		self.tbTrash = wx.BitmapButton(self, wx.ID_ANY, self.images.pngTrash, size=TBDIM)
		self.tbTrash.SetToolTipString("Delete item")
		self.Bind(wx.EVT_BUTTON, self.onTrash, self.tbTrash)
		self.tb.Add(self.tbTrash)
		
		self.tb.AddSpacer((40, 20))
		
		self.bSave = wx.BitmapButton(self, wx.ID_ANY, self.images.pngSave, size=TBDIM)
		self.bSave.SetToolTipString("Save")
		self.Bind(wx.EVT_BUTTON, self.onSave, self.bSave)
		self.tb.Add(self.bSave)
		
		self.bSaveAs = wx.BitmapButton(self, wx.ID_ANY, self.images.pngSaveas, size=TBDIM)
		self.bSaveAs.SetToolTipString("Save As")
		self.Bind(wx.EVT_BUTTON, self.onSaveAs, self.bSaveAs)
		self.tb.Add(self.bSaveAs)
		
		self.bPrint = wx.BitmapButton(self, wx.ID_ANY, self.images.pngPrint, size=TBDIM)
		self.bPrint.SetToolTipString("Print - right click for preview")
		self.Bind(wx.EVT_BUTTON, self.onPrint, self.bPrint)
		self.bPrint.Bind(wx.EVT_RIGHT_DOWN, self.onPrintPreview)
		self.tb.Add(self.bPrint)
		
		self.bPrintInstr = wx.BitmapButton(self, wx.ID_ANY, self.images.pngInstructions, size=TBDIM)
		self.bPrintInstr.SetToolTipString("Print Instructions")
		self.Bind(wx.EVT_BUTTON, self.onPrintInstr, self.bPrintInstr)
		self.tb.Add(self.bPrintInstr)
		
		self.bExit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngExit, size=TBDIM)
		self.bExit.SetToolTipString("Exit")
		self.Bind(wx.EVT_BUTTON, self.onClose, self.bExit)
		self.tb.Add(self.bExit)
		
		self.tb.AddSpacer((20, 20))

		self.pbSizer = wx.BoxSizer()
		#self.dsp = PBFrame(self, self.pb, self.settings)
		#self.pbSizer.Add(self.dsp)
		
		self.statusSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.statusSizer.AddSpacer((5,5))
		
		self.bitmapStatus = wx.StaticBitmap(self, wx.ID_ANY, self.images.pngCut)
		self.statusSizer.Add(self.bitmapStatus)
		self.statusSizer.AddSpacer((5,5))
	
		statusMsgSizer = wx.BoxSizer(wx.VERTICAL)
		
		self.hintLine1 = wx.StaticText(self, wx.ID_ANY, "")
		statusMsgSizer.Add(self.hintLine1)
		
		self.hintLine2 = wx.StaticText(self, wx.ID_ANY, "")
		statusMsgSizer.Add(self.hintLine2)
		statusMsgSizer.AddSpacer((5,5))

		self.statusLine = wx.StaticText(self, wx.ID_ANY, "")
		statusMsgSizer.Add(self.statusLine)
		
		self.statusSizer.Add(statusMsgSizer)
		
		self.buildSizer()
		wx.CallAfter(self.createPBView)
		wx.CallAfter(self.setInitialTool)
		
	def createPBView(self):
		#self.updateProtoBoard(False)
		if not self.pbView is None:
			try:
				self.prevPosition = self.pbView.GetPosition()
				self.pbView.Destroy()
			except wx.PyDeadObjectError:
				self.pbView = None
				self.prevPosition = [-1, -1]
			
		self.pbView = ProtoBoardView(self, self.pb, self.prevPosition, self.settings)
		self.dsp = self.pbView.getPBFrame()
		self.pbView.Show()
		
	def buildSizer(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.AddSpacer((10, 10))
		sizer.Add(self.tb)
		sizer.AddSpacer((10, 10))
		sizer.Add(self.pbSizer, 1, wx.LEFT+wx.RIGHT, 10)
		sizer.AddSpacer((10, 10))
		sizer.Add(self.statusSizer)
		sizer.AddSpacer((10, 10))
		self.SetSizer(sizer)
		self.mySizer = sizer
		self.Fit()
		
	def updateTitle(self):
		title = TITLETEXT
		if not self.fileName is None:
			title += " - %s" % self.fileName
		self.SetTitle(title)
		
	def setInitialTool(self):
		self.selectTool(TOOL_CUT)
		
	def setStatusText(self, msg):
		self.statusLine.SetLabel(msg)
		
	def setStatusBitmap(self, tid):
		if tid == TOOL_CUT:
			self.bitmapStatus.SetBitmap(self.images.pngCut)
		elif tid == TOOL_EXAMINE:
			self.bitmapStatus.SetBitmap(self.images.pngView)
		elif tid == TOOL_NAME:
			self.bitmapStatus.SetBitmap(self.images.pngProperties)
		elif tid == TOOL_WIRE:
			self.bitmapStatus.SetBitmap(self.images.pngWire)
		elif tid == TOOL_COMPONENT:
			self.bitmapStatus.SetBitmap(self.images.pngComponent)
		elif tid == TOOL_STRETCH:
			self.bitmapStatus.SetBitmap(self.images.pngStretch)
		elif tid == TOOL_GROW:
			self.bitmapStatus.SetBitmap(self.images.pngGrow)
		elif tid == TOOL_GRAB:
			self.bitmapStatus.SetBitmap(self.images.pngGrab)
		elif tid == TOOL_MOVE:
			self.bitmapStatus.SetBitmap(self.images.pngMove)
		elif tid == TOOL_TRIM:
			self.bitmapStatus.SetBitmap(self.images.pngTrim)
		elif tid == TOOL_TRASH:
			self.bitmapStatus.SetBitmap(self.images.pngTrash)
		
	def setHintText(self, tid):
		if tid is None:
			self.hintLine1.SetLabel("")
			self.hintLine2.SetLabel("")
			
		elif tid in toolHintText.keys():
			self.hintLine1.SetLabel(toolHintText[tid][0])
			self.hintLine2.SetLabel(toolHintText[tid][1])
		
	def onCut(self, evt):
		self.clearAllComponents()
		self.selectTool(TOOL_CUT)
		
	def onExamine(self, evt):
		self.clearAllComponents()
		self.selectTool(TOOL_EXAMINE)
		
	def onName(self, evt):
		self.clearAllComponents()
		self.selectTool(TOOL_NAME)
		
	def onWire(self, evt):
		self.dsp.setFixedComponent(None)
		self.currentFixedComponent = None
		self.dsp.setGrowComponent(None)
		self.currentGrowComponent = None
		self.selectTool(TOOL_WIRE)
		
	def onComponent(self, evt):
		self.dsp.setStretchComponent(None)
		self.currentStretchComponent = None
		self.dsp.setGrowComponent(None)
		self.currentGrowComponent = None
		self.selectTool(TOOL_COMPONENT)
		
	def onStretch(self, evt):
		self.dsp.setFixedComponent(None)
		self.currentFixedComponent = None
		self.dsp.setGrowComponent(None)
		self.currentGrowComponent = None
		self.selectTool(TOOL_STRETCH)
		
	def onGrow(self, evt):
		self.dsp.setStretchComponent(None)
		self.currentStretchComponent = None
		self.dsp.setFixedComponent(None)
		self.currentFixedComponent = None
		self.selectTool(TOOL_GROW)
		
	def onGrab(self, evt):
		self.clearAllComponents()
		self.selectTool(TOOL_GRAB) 
		
	def onMove(self, evt):
		dlg = MoveDlg(self, self.pb.getSize(), self.settings)
		rc = dlg.ShowModal()
		failedMoves = []
		if rc == wx.ID_OK:
			self.dx, self.dy = dlg.getValues()
			self.clearAllComponents()
			self.selectTool(TOOL_MOVE) 
		elif rc == wx.ID_EXECUTE:
			self.dx, self.dy = dlg.getValues()
			failedMoves = self.moveAllComponents([self.dx, self.dy])
			
		dlg.Destroy()
		
		if len(failedMoves) != 0:
			print "%d failed moves" % len(failedMoves)
			for f in failedMoves:
				print "  %s" % f
		
	def onTrim(self, evt):
		dlg = TrimDlg(self, self.settings)
		dlg.ShowModal()
		dlg.Destroy()
		
	def trimRight(self):
		if self.pb.trimRight():
			self.dsp.reSize()
			self.createPBView()
		
	def growRight(self):
		if self.pb.growRight():
			self.dsp.reSize()
			self.createPBView()
		
	def trimBottom(self):
		if self.pb.trimBottom():
			self.dsp.reSize()
			self.createPBView()
		
	def growBottom(self):
		if self.pb.growBottom():
			self.dsp.reSize()
			self.createPBView()
		
	def trimLeft(self):
		if self.pb.trimLeft():
			self.moveAllComponents([-1, 0])
			self.dsp.reSize()
			self.createPBView()
		
	def growLeft(self):
		if self.pb.growLeft():
			self.moveAllComponents([1, 0])
			self.dsp.reSize()
			self.createPBView()
			
	def trimTop(self):
		if self.pb.trimTop():
			self.moveAllComponents([0, -1])
			self.dsp.reSize()
			self.createPBView()
			
	def growTop(self):
		if self.pb.growTop():
			self.moveAllComponents([0, 1])
			self.dsp.reSize()
			self.createPBView()
		
	def onTrash(self, evt):
		self.clearAllComponents()
		self.selectTool(TOOL_TRASH) 
		
	def clearAllComponents(self):	 
		self.dsp.setStretchComponent(None)
		self.currentStretchComponent = None
		self.dsp.setFixedComponent(None)
		self.currentFixedComponent = None
		self.dsp.setGrowComponent(None)
		self.currentGrowComponent = None
		
	def selectTool(self, tid, newComponent=True):
		self.selectedTool = tid
		self.setHintText(tid)
		self.setStatusBitmap(tid)
		self.dsp.setHiLightedNet(None)
		self.dsp.refresh()

		if newComponent:	   
			if tid == TOOL_COMPONENT:
				self.currentFixedComponent = self.newFixedComponent()
				self.dsp.setFixedComponent(self.currentFixedComponent)
			elif tid == TOOL_STRETCH:
				self.currentStretchComponent = self.newStretchComponent()
				self.dsp.setStretchComponent(self.currentStretchComponent)
			elif tid == TOOL_WIRE:
				self.currentStretchComponent = self.newStretchComponent(WIRENAME)
				self.dsp.setWireColor(self.wireColor)
				self.dsp.setStretchComponent(self.currentStretchComponent)
			elif tid == TOOL_GROW:
				self.currentGrowComponent = self.newGrowComponent()
				self.dsp.setGrowComponent(self.currentGrowComponent)

	def onColor(self, evt):
		self.chooseColor(evt)
		self.onWire(None)
		
	def onChooseComponent(self, evt):
		dlg = wx.SingleChoiceDialog(
				self, 'Choose component to add to circuit', 'Component Type',
				self.fixedComponentTypes, 
				wx.CHOICEDLG_STYLE
				)

		if dlg.ShowModal() == wx.ID_OK:
			self.currentFixedComponentChoice = dlg.GetStringSelection()
			if not self.currentFixedComponent is None:
				self.currentFixedComponent = self.newFixedComponent()
				self.dsp.setFixedComponent(self.currentFixedComponent)

		dlg.Destroy()
		self.onComponent(None)
		
	def onChooseStretch(self, evt):
		dlg = wx.SingleChoiceDialog(
				self, 'Choose component to add to circuit', 'Component Type',
				sorted(self.stretchComponentNames), 
				wx.CHOICEDLG_STYLE
				)

		if dlg.ShowModal() == wx.ID_OK:
			self.currentStretchName = dlg.GetStringSelection()
			self.currentStretchComponent = self.newStretchComponent()
			self.dsp.setStretchComponent(self.currentStretchComponent)

		dlg.Destroy()
		self.onStretch(None)
		
	def onChooseGrow(self, evt):
		dlg = wx.SingleChoiceDialog(
				self, 'Choose component to add to circuit', 'Component Type',
				sorted(self.growComponentNames), 
				wx.CHOICEDLG_STYLE
				)
		
		if dlg.ShowModal() == wx.ID_OK:
			self.currentGrowComponentChoice = dlg.GetStringSelection()
			self.currentGrowComponent = self.newGrowComponent()
			self.dsp.setGrowComponent(self.currentGrowComponent)
			
		dlg.Destroy()
		self.onGrow(None)

	def newFixedComponent(self):
		c, self.currentComponentPrefix = self.fixedComponentList.getComponent(self.currentFixedComponentChoice)
		return c

	def newStretchComponent(self, nm = None):
		if nm is None:
			nm = self.currentStretchName
		c, self.currentComponentPrefix = self.stretchComponentList.getComponent(nm)
		return c
	
	def newGrowComponent(self):
		c, self.currentComponentPrefix = self.growComponentList.getComponent(self.currentGrowComponentChoice)
		return c

	def holeClick(self, pos):
		self.dsp.selectHole(pos[0], pos[1])
		
	def rightClick(self, pos):
		if self.selectedTool == TOOL_COMPONENT:
			self.fixedComponentList.nextView(self.currentFixedComponent)
			self.dsp.refresh()
		elif self.selectedTool in [TOOL_STRETCH, TOOL_WIRE]:
			self.currentStretchComponent.setP1(pos)
			self.currentStretchComponent.setP2(pos)
			self.dsp.refresh()
		elif self.selectedTool == TOOL_GROW:
			self.currentGrowComponent.setP1(pos)
			self.currentGrowComponent.setP2(pos)
			self.dsp.refresh()


		
	def holeDrag(self, p1, p2):
		if self.selectedTool == TOOL_CUT:
			dx = p2[0] - p1[0]
			dy = p2[1] - p1[1]
			dcut = None
			if dx == 0 and (dy == 1 or dy == -1):
				dcut = 'v'
			elif dy == 0 and (dx == 1 or dx == -1):
				dcut = 'h'
				
			if not dcut is None:
				if self.pb.sameTrace(p1, p2):
					if dcut == 'v':
						self.pb.addVCut(p1[0], p1[1], p2[1])
					else:
						self.pb.addHCut(p1[0], p2[0], p1[1])
					self.dsp.refresh()
				else:
					if dcut == 'v':
						rc = self.pb.delVCut(p1[0], p1[1], p2[1])
					else:
						rc = self.pb.delHCut(p1[0], p2[0], p1[1])
					if not rc:
						if not self.pb.addJumper(p1, p2):
							self.pb.delJumper(p1, p2)
					self.dsp.refresh()
		

	def holeDoubleClick(self, pos):
		if self.selectedTool == TOOL_CUT:
			self.doBreak(pos)
		elif self.selectedTool == TOOL_EXAMINE:
			self.doExamine(pos)
		elif self.selectedTool == TOOL_NAME:
			self.doName(pos)
		elif self.selectedTool == TOOL_WIRE:
			self.doStretchComponent(pos, WIRENAME)
		elif self.selectedTool == TOOL_COMPONENT:
			self.doFixedComponent(pos)
		elif self.selectedTool == TOOL_STRETCH:
			self.doStretchComponent(pos)
		elif self.selectedTool == TOOL_GROW:
			self.doGrowComponent(pos)
		elif self.selectedTool == TOOL_GRAB:
			self.doGrab(pos)
		elif self.selectedTool == TOOL_MOVE:
			self.doMove(pos)
		elif self.selectedTool == TOOL_TRASH:
			self.doTrash(pos)
			
	def doStretchComponent(self, pos, nm=None):
		if self.pb.occupied(pos):
			self.setStatusText("Position is already occupied")
			return
		
		if self.pb.noTrace(pos):
			self.setStatusText("No trace at that position")
			return

		if nm == WIRENAME:
			self.dsp.setWireColor(self.wireColor)

		pt = self.currentStretchComponent.getP1()
		if pt is None:
			self.currentStretchComponent.setP1(pos)
			self.currentStretchComponent.setP2(pos)

		else:
			if pos[0] == pt[0] and pos[1] == pt[1]:
				self.setStatusText("Cannot start and end on the same position")
				return
			
			if self.pb.sameTrace(pos, pt):
				# re-anchor
				self.currentStretchComponent.setP1(pos)
				self.currentStretchComponent.setP2(pos)

			elif nm == WIRENAME:
				self.currentStretchComponent.setP2(pos)
				wid = compID.generateID(self.currentComponentPrefix) 
				self.currentStretchComponent.setID(wid)
				self.pb.addWire(self.currentStretchComponent, self.wireColor)
				self.currentStretchComponent = self.newStretchComponent(WIRENAME)
				self.dsp.setStretchComponent(self.currentStretchComponent)
				
			else:
				self.currentStretchComponent.setP2(pos)
				nm = compID.generateID(self.currentComponentPrefix) 
				self.currentStretchComponent.setID(nm)
				self.pb.addStretchComponent(self.currentStretchComponent)
				self.currentStretchComponent = self.newStretchComponent()
				self.dsp.setStretchComponent(self.currentStretchComponent)
		self.dsp.refresh()
			
	def doGrowComponent(self, pos):
		if self.pb.occupied(pos):
			self.setStatusText("Position is already occupied")
			return
		
		if self.pb.noTrace(pos):
			self.setStatusText("no Trace at that position")
			return

		pt = self.currentGrowComponent.getP1()
		if pt is None:
			self.currentGrowComponent.setP1(pos)
			self.currentGrowComponent.setP2(pos)

		else:
			self.dsp.checkGrowEnd(pos)
			nm = compID.generateID(self.currentComponentPrefix) 
			self.currentGrowComponent.setID(nm)
			self.pb.addGrowComponent(self.currentGrowComponent)
			self.currentGrowComponent = self.newGrowComponent()
			self.dsp.setGrowComponent(self.currentGrowComponent)
		self.dsp.refresh()
			
	def doFixedComponent(self, pos):
		if self.currentFixedComponent is None:
			return
		
		cx = self.currentFixedComponent.getConnections()
		ncols, nrows = self.pb.getSize()
		for p in cx:
			if (pos[0]+p[0] >= ncols or pos[1]+p[1] >= nrows or
					pos[0]+p[0] < 0 or pos[1]+p[1] < 0):
				self.setStatusText("Component goes beyond board edge")
				return
			if self.pb.occupied([pos[0]+p[0], pos[1]+p[1]]):
				self.setStatusText("Position(s) already occupied")
				return
			if self.pb.noTrace([pos[0]+p[0], pos[1]+p[1]]):
				self.setStatusText("no Trace at that position")
				return

		self.currentFixedComponent.setAnchor(pos)

		nm = compID.generateID(self.currentComponentPrefix) 
		self.currentFixedComponent.setID(nm)  
		cv = self.currentFixedComponent.getView()		
		self.pb.addComponent(self.currentFixedComponent)
		self.currentFixedComponent = self.newFixedComponent()
		self.currentFixedComponent.setAnchor(pos)
		self.fixedComponentList.setView(self.currentFixedComponent, cv)
		self.dsp.setFixedComponent(self.currentFixedComponent)

	def doExamine(self, pos):
		if self.pb.noTrace(pos):
			self.setStatusText("No trace at that position")
			return
		
		self.dsp.setHiLightedNet(pos)
		self.dsp.refresh()
		
	def doName(self, pos):
		c, cclass = self.pb.findByPosition(pos)
		if c is None:
			return
		
		if cclass == CLASS_WIRE:
			return
		
		dlg = InfoDialog(self, c.getID(), c.getName(), c.getValue())
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			n,v = dlg.getData()
			
			c.setName(n)
			c.setValue(v)
			self.pb.setModified()
			
		dlg.Destroy()
	
	def doBreak(self, pos):
		if self.pb.occupied(pos, covered=False):
			self.setStatusText("Position is occupied")
			return
		
		if not self.pb.traceRemovable(pos):
			self.setStatusText("Cannot remove/replace trace at this location")
			return
		
		if self.pb.traceRemoved(pos):
			self.pb.traceReplace(pos)
		else:
			self.pb.traceRemove(pos)
		
		self.dsp.refresh()
		
	def doGrab(self, pos):
		c, cclass = self.pb.findByPosition(pos, True)
		if c is None:
			return
		
		if cclass == CLASS_WIRE:
			self.dsp.setFixedComponent(None)
			self.currentFixedComponent = None
			self.dsp.setGrowComponent(None)
			self.currentGrowComponent = None

			p1 = c.getP1()
			p2 = c.getP2()
			self.wireColor = c.getColor()
			c = self.newStretchComponent(WIRENAME)
			if p2 == pos:
				c.setP1(p1)
				c.setP2(p2)
			else:
				c.setP1(p2)
				c.setP2(p1)
			
			self.currentStretchComponent = c
			self.dsp.setWireColor(self.wireColor)
			self.dsp.setStretchComponent(self.currentStretchComponent)

			self.selectTool(TOOL_WIRE, False)

		elif cclass == CLASS_FIXED:
			self.dsp.setStretchComponent(None)
			self.currentStretchComponent = None
			self.dsp.setGrowComponent(None)
			self.currentGrowComponent = None
			self.getIDPrefix(c)
			compID.returnID(c.getID())
			c.setID(None)
			self.currentFixedComponent = c
			self.dsp.setFixedComponent(self.currentFixedComponent)
			self.selectTool(TOOL_COMPONENT, False)

		elif cclass == CLASS_STRETCH:
			self.dsp.setFixedComponent(None)
			self.currentFixedComponent = None
			self.dsp.setGrowComponent(None)
			self.currentGrowComponent = None
			p2 = c.getP2()
			if p2 != pos:
				# reanchor from the other end
				p1 = c.getP1()
				c.setP2(p1)
				c.setP1(p2)
				
			self.getIDPrefix(c)
			compID.returnID(c.getID())
			c.setID(None)
			self.currentStretchComponent = c
			self.dsp.setStretchComponent(self.currentStretchComponent)
			self.selectTool(TOOL_STRETCH, False)
			
		elif cclass == CLASS_GROW:
			self.dsp.setStretchComponent(None)
			self.currentStretchComponent = None
			self.dsp.setFixedComponent(None)
			self.currentFixedComponent = None
			
			# calculate new anchor based on where within the component the click occurred
			p1 = c.getP1()
			p2 = c.getP2()
			minx = p1[0]
			maxx = p2[0]
			if maxx < minx:
				minx = p2[0]
				maxx = p1[0]
			midx = (maxx - minx)/2 + minx
			
			miny = p1[1]
			maxy = p2[1]
			if maxy < miny:
				miny = p2[1]
				maxy = p1[1]
			midy = (maxy - miny)/2 + miny
			
			#anchor should be on the opposite side from where we selected
			if pos[0] < midx:
				xa = maxx
				xb = minx
			else:
				xa = minx
				xb = maxx
			if pos[1] < midy:
				ya = maxy
				yb = miny
			else:
				ya = miny
				yb = maxy
				
			c.setP1([xa, ya])
			c.setP2([xb, yb])

			self.getIDPrefix(c)
			compID.returnID(c.getID())
			c.setID(None)
			self.currentGrowComponent = c
			self.dsp.setGrowComponent(self.currentGrowComponent)
			self.selectTool(TOOL_GROW, False)
			
		else:
			print "unknown component class"
			return
		
	def doMove(self, pos):
		c, cclass = self.pb.findByPosition(pos, False)
		self.moveComponent(c, cclass, [self.dx, self.dy])
		
	def moveAllComponents(self, delta):
		failedMoves = []
		for c in self.pb.getComponentList():
			if not self.moveComponent(c, CLASS_FIXED, delta, True):
				failedMoves.append(c.getID())
			
		for c in self.pb.getStretchComponentList():
			if not self.moveComponent(c, CLASS_STRETCH, delta, True):
				failedMoves.append(c.getID())
			
		for c in self.pb.getWireList():
			if not self.moveComponent(c, CLASS_WIRE, delta, True):
				failedMoves.append(c.getID())
			
		for c in self.pb.getGrowComponentList():
			if not self.moveComponent(c, CLASS_GROW, delta, True):
				failedMoves.append(c.getID())
			
		return failedMoves


		
	def moveComponent(self, c, cclass, delta, silent=False):
		if c is None:
			return
		
		dx = delta[0]
		dy = delta[1]

		if cclass in [CLASS_WIRE, CLASS_STRETCH]:
			self.dsp.setFixedComponent(None)
			self.currentFixedComponent = None
			self.dsp.setGrowComponent(None)
			self.currentGrowComponent = None
			
			p1 = c.getP1()
			p2 = c.getP2()
			
			np1 = [p1[0]+dx, p1[1]+dy]
			np2 = [p2[0]+dx, p2[1]+dy]

			if self.pb.outOfBounds(np1):
				if not silent:
					self.setStatusText("New position A is off of the board")
				return False
			
			if self.pb.occupied(np1, comp=c):
				if not silent:
					self.setStatusText("New position A is already occupied")
				return False
			
			if self.pb.noTrace(np1):
				if not silent:
					self.setStatusText("No trace at new position A")
				return False

			if self.pb.outOfBounds(np2):
				if not silent:
					self.setStatusText("New position B is off of the board")
				return False

			if self.pb.occupied(np2, comp=c):
				if not silent:
					self.setStatusText("New position B is already occupied")
				return False
			
			if self.pb.noTrace(np2):
				if not silent:
					self.setStatusText("No trace at new position B")
				return False

			c.setP1(np1)
			c.setP2(np2)

			self.dsp.refresh()
			return True
			
		elif cclass == CLASS_FIXED:
			self.dsp.setStretchComponent(None)
			self.currentStretchComponent = None
			self.dsp.setGrowComponent(None)
			self.currentGrowComponent = None
			
			ap = c.getAnchor()
			
			for p in c.getCovered():
				np = [p[0] + ap[0] + dx, p[1]+ap[1] + dy]
				if self.pb.outOfBounds(np):
					if not silent:
						self.setStatusText("Component will be off of the board")
					return False

				if self.pb.occupied(np, comp=c):
					if not silent:
						self.setStatusText("New position is already occupied")
					return False
			
				if self.pb.noTrace(np):
					if not silent:
						self.setStatusText("No trace at new position")
					return False
				
			c.setAnchor([ap[0]+dx, ap[1]+dy])
			
			self.dsp.refresh()
			return True

		elif cclass == CLASS_GROW:
			self.dsp.setStretchComponent(None)
			self.currentStretchComponent = None
			self.dsp.setFixedComponent(None)
			self.currentFixedComponent = None

			p1 = c.getP1()
			p2 = c.getP2()
			
			minx = min(p1[0], p2[0])
			maxx = max(p1[0], p2[0])
			miny = min(p1[1], p2[1])
			maxy = max(p1[1], p2[1])
			
			for px in range(minx, maxx+1):
				for py in range(miny, maxy+1):
					np = [px + dx, py + dy]
					if self.pb.outOfBounds(np):
						if not silent:
							self.setStatusText("Component will be off of the board")
						return False
	
					if self.pb.occupied(np, comp=c):
						if not silent:
							self.setStatusText("New position is already occupied")
						return False
				
					if self.pb.noTrace(np):
						if not silent:
							self.setStatusText("No trace at new position")
						return False
					
			c.setP1([p1[0]+dx, p1[1]+dy])
			c.setP2([p2[0]+dx, p2[1]+dy])
			
			self.dsp.refresh();
			return True
			
		
	def getIDPrefix(self, c):
		try:
			cid = c.getID()
		except:
			self.currentComponentPrefix = "?"
			return
		self.currentComponentPrefix = rePrefix.match(cid).group()
		
	def doTrash(self, pos):
		if not self.pb.deleteByPosition(pos):
			self.setStatusText("Nothing at that position")
			return
		
		self.dsp.refresh()
		
	def reportCoordinate(self, pos):
		if pos == self.lastReport:
			return
		
		self.lastReport = pos
		
		
		c, ct = self.pb.findByPosition(pos)
		
		text = "(%s,%d)" % (pos[0], pos[1])
		if (not c is None) and (ct != CLASS_WIRE):
			text += "   " + c.getID()
			s = c.getName().strip()
			if s != "":
				text += "  " + s

			s = c.getValue().strip()
			if s != "":
				text += " (" + s + ")"   

		self.setStatusText(text)
		
		if not self.currentStretchComponent is None:
			self.dsp.checkStretchEnd(pos)
			
		if not self.currentGrowComponent is None:
			rc = self.dsp.checkGrowEnd(pos)
			if rc == OV_OVERLAP:
				self.setStatusText("Components would overlap")
			elif rc == OV_SKIPPED_HOLE:
				self.setStatusText("Component would extend over region with no holes")

		if not self.currentFixedComponent is None:
			self.currentFixedComponent.setAnchor(pos)
			self.dsp.refresh()
			
	def chooseColor(self, evt):
		dlg = wx.ColourDialog(self)
		dlg.GetColourData().SetChooseFull(True)

		if dlg.ShowModal() == wx.ID_OK:
			rgb = dlg.GetColourData().GetColour().Get()
			self.wireColor = wx.Colour(rgb[0], rgb[1], rgb[2])
			self.dsp.setWireColor(self.wireColor)

		dlg.Destroy()
		
	def onSave(self, evt):
		if self.fileName is None:
			self.onSaveAs(None)
			return
		self.saveToFile(self.fileName)
		
	def onSaveAs(self, evt):
		dfn = ""
		if not self.fileName is None:
			dfn = self.fileName
			
		dlg = wx.FileDialog(
			self, message="Save proto board as ...", defaultDir=os.getcwd(), 
			defaultFile=dfn, wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
			)
		
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if not path.lower().endswith(".pb"):
			path += ".pb"
			
		if self.saveToFile(path):
			self.fileName = path
			self.updateTitle()
		
	def saveToFile(self, fn):
		try:
			fp = open(fn, "w")
			fp.write(self.pb.getXml())
			fp.write("\n")
			fp.close()
		except:
			dlg = wx.MessageDialog(self, 'Error writing to file ' + fn,
				'Save Error', wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return False

		self.pb.setModified(False)
		dlg = wx.MessageDialog(self, 'Proto Board saved to ' + fn,
			'Saved', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		return True

	def onClose(self, evt):
		if self.pb.isModified():
			dlg = wx.MessageDialog(self, 'Are you sure you want to exit?\nPending changes will be lost',
				'Changes pending',
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
			rc = dlg.ShowModal()
			dlg.Destroy()
			
			if rc == wx.ID_NO:
				return
			
		self.parent.onEditorClose()
		
	def onPrint(self, evt):
		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_LETTER)
		self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

		pdd = wx.PrintDialogData(self.printData)
		pdd.SetToPage(2)
		printer = wx.Printer(pdd)
		printout = PBPrint(self.dsp, self.fileName)

		if not printer.Print(self, printout, True):
			rc = printer.GetLastError()
			if rc == wx.PRINTER_ERROR:
				wx.MessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
		printout.Destroy()
		
	def onPrintPreview(self, evt):
		data = wx.PrintDialogData(self.printData)
		printout = PBPrint(self.dsp, self.fileName)
		printout2 = PBPrint(self.dsp, self.fileName)
		self.preview = wx.PrintPreview(printout, printout2, data)

		if not self.preview.Ok():
			rc = self.preview.GetLastError()
			if rc == wx.PRINTER_ERROR:
				wx.MessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)
				return

		title = "Print Preview: "
		if self.fileName is None:
			title += "<untitled>"
		else:
			title += self.fileName
		pfrm = wx.PreviewFrame(self.preview, self.parent, title)

		pfrm.Initialize()
		pfrm.SetPosition(self.GetPosition())
		pfrm.SetSize(self.GetSize())
		pfrm.Show(True)

		
	def onPrintInstr(self, evt):
		pdd = wx.PrintDialogData(self.printData)
		pdd.SetToPage(2)
		printer = wx.Printer(pdd)
		printout = PBInstructionsPrint(self.pb)

		if not printer.Print(self, printout, True):
			rc = printer.GetLastError()
			if rc == wx.PRINTER_ERROR:
				wx.MessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
		printout.Destroy()
