import os
import wx
from protoboard import ProtoBoard
from pbpreview import ProtoBoardPreview

TBDIM = (48, 48)
STYPE_HTRACE = 1
STYPE_VTRACE = 2
STYPE_HSKIP = 3
STYPE_VSKIP = 4

wildcard = "Proto-board template file (*.pbt)|*.pbt"


class Segment:
	def __init__(self, stype, v1, v2, v3):
		self.stype = stype
		self.v1 = v1
		self.v2 = v2
		self.v3 = v3   
		
	def getValues(self):
		return [self.stype, self.v1, self.v2, self.v3]  
	
	def getFirstPos(self): 
		if self.stype == STYPE_HTRACE:
			return [self.v1, self.v3]
		elif self.stype == STYPE_VTRACE:
			return [self.v1, self.v2]
		elif self.stype == STYPE_HSKIP:
			return [self.v1, 0]
		elif self.stype == STYPE_VSKIP:
			return [self.v1, 0]
		else:
			return None
		
	def getStr(self):
		if self.stype == STYPE_HTRACE:
			return "Horizontal Trace %d,%d to %d,%d" % (self.v1, self.v3, self.v2, self.v3)
		elif self.stype == STYPE_VTRACE:
			return "Vertical Trace %d,%d to %d,%d" % (self.v1, self.v2, self.v1, self.v3)
		elif self.stype == STYPE_HSKIP:
			return "Row without holes %d" % self.v1
		elif self.stype == STYPE_VSKIP:
			return "Column without holes %d" % self.v1
		else:
			return "Unknown segment type"
		
	def addSegment(self, pb):
		if self.stype == STYPE_HTRACE:
			pb.addHTrace(self.v1, self.v2, self.v3)
		elif self.stype == STYPE_VTRACE:
			pb.addVTrace(self.v1, self.v2, self.v3)
		elif self.stype == STYPE_HSKIP:
			pb.addHSkip(self.v1)
		elif self.stype == STYPE_VSKIP:
			pb.addVSkip(self.v1)
		
	def limitValues(self, nc, nr):
		chg = False
		if self.stype == STYPE_HTRACE:
			if self.v1 >= nc:
				self.v1 = nc - 1
				chg = True
			if self.v2 >= nc:
				self.v2 = nc - 1
				chg = True
			if self.v3 >= nr:
				return True, chg
			else:
				return False, chg
			
		elif self.stype == STYPE_VTRACE:
			if self.v2 >= nr:
				self.v2 = nr - 1
				chg = True
			if self.v3 >= nr:
				self.v3 = nr - 1
				chg = True
			if self.v1 >= nc:
				return True, chg
			else:
				return False, chg
			
		elif self.stype == STYPE_HSKIP:
			if self.v1 >= nr:
				return True, False
			else:
				return False, False
			
		elif self.stype == STYPE_VSKIP:
			if self.v1 >= nc:
				return True, False
			else:
				return False, False
			
		else:
			return True, False

class NewTempDialog(wx.Dialog):
	def __init__(self, parent):
		self.parent = parent 
		self.settings = parent.settings
		self.images = parent.settings.images
		
		self.stype = STYPE_HTRACE
		self.segments = []
		self.selectedSegment = wx.NOT_FOUND
		
		self.cols = 5
		self.rows = 5
		self.modified = False
		
		self.fileName = None
		
		self.pbPrev = None
		self.prevPosition = [-1, -1]
		
		wx.CallAfter(self.createProtoBoard)
		
		title = "New Proto-board template"
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(100, 100))
		self.SetBackgroundColour("white")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		t1 = wx.StaticText(self, wx.ID_ANY, "Columns:")		
		self.scCols = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scCols.SetRange(5,100)
		self.scCols.SetValue(self.cols)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinCol, self.scCols)
		
		t2 = wx.StaticText(self, wx.ID_ANY, "Rows:")		
		self.scRows = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scRows.SetRange(5,100)
		self.scRows.SetValue(self.rows)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinRow, self.scRows)
		
		isizer = wx.FlexGridSizer(cols=4, hgap=6, vgap=6)
		isizer.AddMany([ t1, self.scCols, t2, self.scRows ])
		
		box = wx.StaticBox(self, -1, "Item")
		szItems = wx.StaticBoxSizer(box, wx.VERTICAL)

		self.rbHTrace = wx.RadioButton(self, wx.ID_ANY, "Horizontal Trace", style = wx.RB_GROUP)
		self.rbVTrace = wx.RadioButton(self, wx.ID_ANY, "Vertical Trace")
		self.rbHSkip = wx.RadioButton(self, wx.ID_ANY, "Row without holes")
		self.rbVSkip = wx.RadioButton(self, wx.ID_ANY, "Column without holes")
		self.Bind(wx.EVT_RADIOBUTTON, self.onHTrace, self.rbHTrace )
		self.Bind(wx.EVT_RADIOBUTTON, self.onVTrace, self.rbVTrace )
		self.Bind(wx.EVT_RADIOBUTTON, self.onHSkip, self.rbHSkip )
		self.Bind(wx.EVT_RADIOBUTTON, self.onVSkip, self.rbVSkip )
		
		szItems.AddSpacer((10, 10))
		szItems.Add(self.rbHTrace)
		szItems.AddSpacer((10, 10))
		szItems.Add(self.rbVTrace)
		szItems.AddSpacer((10, 10))
		szItems.Add(self.rbHSkip)
		szItems.AddSpacer((10, 10))
		szItems.Add(self.rbVSkip)
		szItems.AddSpacer((10, 10))
		
		t1 = wx.StaticText(self, wx.ID_ANY, "Point A")		
		self.scAX = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scAX.SetRange(0,self.cols-1)
		self.scAX.SetValue(0)
		
		self.scAY = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scAY.SetRange(0,self.rows-1)
		self.scAY.SetValue(0)
		
		t2 = wx.StaticText(self, wx.ID_ANY, "Point B")		
		self.scBX = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scBX.SetRange(0,self.cols-1)
		self.scBX.SetValue(0)
		
		self.scBY = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scBY.SetRange(0,self.rows-1)
		self.scBY.SetValue(0)
		
		szData = wx.FlexGridSizer(cols=3, hgap=6, vgap=6)
		szData.AddMany([ t1, self.scAX, self.scAY, t2, self.scBX, self.scBY])
		
		box = wx.StaticBox(self, -1, "Positions")
		szDataBox = wx.StaticBoxSizer(box, wx.VERTICAL)
		szDataBox.Add(szData)
		
		szDataBox.AddSpacer((10, 10))
		self.cbRepeat = wx.CheckBox(self, wx.ID_ANY, "Repeat across row/column")
		szDataBox.Add(self.cbRepeat)
		self.cbRepeat.SetValue(False)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(szItems)
		hsz.AddSpacer((20, 20))
		hsz.Add(szDataBox)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.AddSpacer((20, 20))
		sizer.Add(isizer)
		sizer.AddSpacer((20, 20))
		sizer.Add(hsz)
		sizer.AddSpacer((20, 20))

		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer((20, 20))
		hsizer.Add(sizer)
		hsizer.AddSpacer((20, 20))
		
		self.lbSegments = wx.ListBox(self, wx.ID_ANY, size=(200, 200), choices=[])
		self.setSegmentList()
		self.lbSegments.Bind(wx.EVT_LISTBOX, self.onSegmentSelect)
	
		hsizer.Add(self.lbSegments, 1, wx.ALL, 20)
		hsizer.AddSpacer((20, 20))
		
		dbSizer = wx.BoxSizer(wx.VERTICAL)
		dbSizer.Add(hsizer)
		
		dscSizer = wx.BoxSizer(wx.HORIZONTAL)
		dscSizer.AddSpacer((20, 10))
		dscSizer.Add(wx.StaticText(self, wx.ID_ANY, "Description: "))
		dscSizer.AddSpacer((5,5))
		
		self.tcDesc = wx.TextCtrl(self, wx.ID_ANY, "", size=(500, -1))
		dscSizer.Add(self.tcDesc)
		dbSizer.Add(dscSizer)
		dbSizer.AddSpacer((10, 10))
		
		tbSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		tbSizer.AddSpacer((20, 20))
		
		self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngAdd, size=TBDIM)
		self.bAdd.SetToolTipString("Add a new item to the template")
		self.Bind(wx.EVT_BUTTON, self.onAdd, self.bAdd)
		tbSizer.Add(self.bAdd)
		tbSizer.AddSpacer((5, 5))
		
		self.bDel = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngDelete, size=TBDIM)
		self.bDel.SetToolTipString("Delete an item from the template")
		self.Bind(wx.EVT_BUTTON, self.onDel, self.bDel)
		tbSizer.Add(self.bDel)
		tbSizer.AddSpacer((20, 10))
		
		self.bPrev = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngView, size=TBDIM)
		self.bPrev.SetToolTipString("Display preview window")
		self.Bind(wx.EVT_BUTTON, self.onPreview, self.bPrev)
		tbSizer.Add(self.bPrev)
		tbSizer.AddSpacer((20, 20))
		
		self.bLoad = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngOpen, size=TBDIM)
		self.bLoad.SetToolTipString("Load a Template File")
		self.Bind(wx.EVT_BUTTON, self.onLoad, self.bLoad)
		tbSizer.Add(self.bLoad)
		tbSizer.AddSpacer((5, 5))
				
		self.bSave = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngSave, size=TBDIM)
		self.bSave.SetToolTipString("Save Template")
		self.Bind(wx.EVT_BUTTON, self.onSave, self.bSave)
		tbSizer.Add(self.bSave)
		tbSizer.AddSpacer((5, 5))
		
		self.bSaveAs = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngSaveas, size=TBDIM)
		self.bSaveAs.SetToolTipString("Save Template As A New File")
		self.Bind(wx.EVT_BUTTON, self.onSaveAs, self.bSaveAs)
		tbSizer.Add(self.bSaveAs)
		tbSizer.AddSpacer((50, 10))
		
		self.bExit = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngExit, size=TBDIM)
		self.bExit.SetToolTipString("Exit")
		self.Bind(wx.EVT_BUTTON, self.onClose, self.bExit)
		tbSizer.Add(self.bExit)
		tbSizer.AddSpacer((10, 10))
		
		dbSizer.Add(tbSizer)
		dbSizer.AddSpacer((20, 20))
		
		self.SetSizer(dbSizer)
		self.Fit()
		
		self.rbHTrace.SetValue(1)
		self.onHTrace(None)
		
	def onLoad(self, evt):
		if self.modified:
			if not self.abandonChanges():
				return
			
		dlg = wx.FileDialog(
			self, message="Choose a proto-board template...",
			defaultDir=self.settings.templDir, 
			defaultFile="",
			wildcard=wildcard,
			style=wx.OPEN
			)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		pb = self.parent.loadBoard(path)
		if pb is None:
			dlg = wx.MessageDialog(self, 'Error loading proto-board template file: ' + path,
				'Load Error', wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		self.fileName = path
		
		dsc = pb.getDescription()
		if dsc is None:
			self.tcDesc.SetValue("")
		else:
			self.tcDesc.SetValue(dsc)
			
		self.cols, self.rows = pb.getSize()
		self.scRows.SetValue(self.rows)
		self.scCols.SetValue(self.cols)

		self.scAX.SetRange(0, self.cols-1)
		self.scBX.SetRange(0, self.cols-1)
		self.scAY.SetRange(0, self.rows-1)
		self.scBY.SetRange(0, self.rows-1)
		self.segments = []

		ht = pb.getHTraces()
		for t in ht:		
			self.addSegment(Segment(STYPE_HTRACE, t[0], t[1], t[2]))

		vt = pb.getVTraces()
		for t in vt:		
			self.addSegment(Segment(STYPE_VTRACE, t[0], t[1], t[2]))
			
		hs, vs = pb.getSkips()
		for s in hs:
			self.addSegment(Segment(STYPE_HSKIP, s, None, None))
							
		for s in vs:
			self.addSegment(Segment(STYPE_VSKIP, s, None, None))
			
		self.setSegmentList()

		self.createProtoBoard()
		self.setModified(False)
		
	def setModified(self, flag=True):
		self.modified = flag
		
	def abandonChanges(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Are you sure you want to exit?\nPending changes will be lost',
				'Changes pending',
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
			rc = dlg.ShowModal()
			dlg.Destroy()
			
			if rc == wx.ID_NO:
				return False
			
		return True

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
			self, message="Save proto board template as ...", defaultDir=os.getcwd(), 
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
		pb = ProtoBoard(self.cols, self.rows)
		dsc = self.tcDesc.GetValue().strip()
		if dsc == "":
			pb.setDescription(None)
		else:
			pb.setDescription(dsc)
			
		pb.clearTraces()
		pb.clearSkips()
		for s in self.segments:
			s.addSegment(pb)

		try:
			fp = open(fn, "w")
			fp.write(pb.getXml(includeDescription=True))
			fp.write("\n")
			fp.close()
		except:
			dlg = wx.MessageDialog(self, 'Error writing to file ' + fn,
				'Save Error', wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return False

		self.setModified(False)
		dlg = wx.MessageDialog(self, 'Proto Board template saved to ' + fn,
			'Saved', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		return True
		
	def onPreview(self, evt):
		self.createProtoBoard()
		
	def createProtoBoard(self):
		self.pb = ProtoBoard(self.cols, self.rows)
		self.updateProtoBoard(False)
		if not self.pbPrev is None:
			try:
				self.prevPosition = self.pbPrev.GetPosition()
				self.pbPrev.Destroy()
			except wx.PyDeadObjectError:
				self.pbPrev = None
				self.prevPosition = [-1, -1]
			
		self.pbPrev = ProtoBoardPreview(self.parent, self.pb, self.prevPosition, self.settings)
		self.pbPrev.Show()
		
		if len(self.segments) > 0:
			s = self.segments[-1]
			self.hiLightPos(s.getFirstPos())
		
	def hiLightPos(self, pos):
		if self.pbPrev is None:
			return
		
		self.pbPrev.setHiLightedPos(pos)
		
	def updateProtoBoard(self, refresh=True):
		self.pb.clearTraces()
		self.pb.clearSkips()
		for s in self.segments:
			s.addSegment(self.pb)
			
		if refresh:
			if not self.pbPrev is None:
				try:
					self.pbPrev.refresh()
				except wx.PyDeadObjectError:
					self.pbPrev = None

		
	def onSpinRow(self, evt):
		self.setModified()
		nr = self.scRows.GetValue()
		self.scAY.SetRange(0, nr-1)
		self.scBY.SetRange(0, nr-1)
		self.rows = nr
		self.limitSegments()
		self.createProtoBoard()
		
	
	def onSpinCol(self, evt):
		self.setModified()
		nc = self.scCols.GetValue()
		self.scAX.SetRange(0, nc-1)
		self.scBX.SetRange(0, nc-1)
		self.cols = nc
		self.limitSegments()
		self.createProtoBoard()
		
	def setSegmentList(self):
		self.lbSegments.Set([s.getStr() for s in self.segments])
		
	def onSegmentSelect(self, evt):
		self.selectedSegment = self.lbSegments.GetSelection()
		if self.selectedSegment is None:
			self.hiLightPos(None)
			return
		if self.selectedSegment == wx.NOT_FOUND:
			self.hiLightPos(None)
			return
		if self.selectedSegment < 0 or self.selectedSegment >= len(self.segments):
			self.hiLightPos(None)
			return
		
		pos = self.segments[self.selectedSegment].getFirstPos()
		self.hiLightPos(pos)
			
	def limitSegments(self):
		delSeg = []
		for sx in range(len(self.segments)):
			deleteSeg, chg = self.segments[sx].limitValues(self.cols, self.rows)
			if deleteSeg:
				delSeg.append(sx)
			if deleteSeg or chg:
				self.setModified()
				
		for sx in delSeg[::-1]:
			del self.segments[sx]
			
		self.setSegmentList()
		
	def onAdd(self, evt):
		self.setModified()
		rpt = self.cbRepeat.GetValue()
		if self.stype == STYPE_HTRACE:
			ax = self.scAX.GetValue()
			ay = self.scAY.GetValue()
			bx = self.scBX.GetValue()
			by = self.scBY.GetValue()
			tlen = bx - ax + 1
			if ax > bx:
				t = ax
				ax = bx
				bx = t
			if ay > by:
				t = ay
				ay = by
				by = t
				
			if rpt:
				while True:
					for r in range(ay, by+1):
						self.addSegment(Segment(self.stype, ax, bx, r))
					ax += tlen
					bx += tlen
					if bx >= self.cols:
						break
			else:
				for r in range(ay, by+1):
					self.addSegment(Segment(self.stype, ax, bx, r))
				
		elif self.stype == STYPE_VTRACE:
			ax = self.scAX.GetValue()
			ay = self.scAY.GetValue()
			bx = self.scBX.GetValue()
			by = self.scBY.GetValue()
			tlen = by - ay + 1
			if ax > bx:
				t = ax
				ax = bx
				bx = t
			if ay > by:
				t = ay
				ay = by
				by = t
				
			if rpt:
				while True:
					for c in range(ax, bx+1):
						self.addSegment(Segment(self.stype, c, ay, by))
					ay += tlen
					by += tlen
					if by >= self.rows:
						break
			else:
				for c in range(ax, bx+1):
					self.addSegment(Segment(self.stype, c, ay, by))
				
		elif self.stype == STYPE_HSKIP:
			self.addSegment(Segment(self.stype, self.scAY.GetValue(), None, None))

		elif self.stype == STYPE_VSKIP:
			self.addSegment(Segment(self.stype, self.scAX.GetValue(), None, None))

		self.setSegmentList()
		self.selectedSegment = len(self.segments)-1
		self.lbSegments.SetSelection(self.selectedSegment)
		
		self.updateProtoBoard()
		
	def addSegment(self, seg):
		for s in self.segments:
			if s.getValues() == seg.getValues():
				return False
			
		self.segments.append(seg)
		return True
		
	def onDel(self, evt):
		if self.selectedSegment is None:
			return
		if self.selectedSegment == wx.NOT_FOUND:
			return
		if self.selectedSegment < 0:
			return
		if self.selectedSegment >= len(self.segments):
			return
		
		self.setModified()
		
		del self.segments[self.selectedSegment]
		self.setSegmentList()
		if self.selectedSegment >= len(self.segments):
			self.selectedSegment = len(self.segments) - 1
			if self.selectedSegment < 0:
				self.selectedSegment = wx.NOT_FOUND
			else:
				self.lbSegments.SetSelection(self.selectedSegment)
		else:
			self.lbSegments.SetSelection(self.selectedSegment)
			
		self.updateProtoBoard()

	def onHTrace(self, evt):
		self.stype = STYPE_HTRACE
		self.scAX.Enable(True)
		self.scAY.Enable(True)
		self.scBX.Enable(True)
		self.scBY.Enable(True)
		
	def onVTrace(self, evt):
		self.stype = STYPE_VTRACE
		self.scAX.Enable(True)
		self.scAY.Enable(True)
		self.scBX.Enable(True)
		self.scBY.Enable(True)
		
	def onHSkip(self, evt):
		self.stype = STYPE_HSKIP
		self.scAX.Enable(False)
		self.scAY.Enable(True)
		self.scBX.Enable(False)
		self.scBY.Enable(False)
		
	def onVSkip(self, evt):
		self.stype = STYPE_VSKIP
		self.scAX.Enable(True)
		self.scAY.Enable(False)
		self.scBX.Enable(False)
		self.scBY.Enable(False)
		
	def onClose(self, evt):
		if self.modified:
			if not self.abandonChanges():
				return
			
		if not self.pbPrev is None:
			try:
				self.pbPrev.Destroy()
			except wx.PyDeadObjectError:
				self.pbPrev = None

		self.EndModal(wx.ID_OK)
