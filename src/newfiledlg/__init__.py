'''
Created on Jan 2, 2016

@author: Jeff
'''
import os
import wx
from protoboard import ProtoBoard
from XMLDoc import XMLDoc

BDIM = (48, 48)

class NewFileDialog(wx.Dialog):
	def __init__(self, parent):
		self.parent = parent 
		self.settings = parent.settings
		self.images = parent.settings.images
		
		self.chosenTemplate = None
		
		self.pb = None
		
		title = "New Proto-board file"
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(100, 100))
		self.SetBackgroundColour("white")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer.AddSpacer((10, 10))
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		hsizer.AddSpacer((20, 10))
		
		box = wx.StaticBox(self, -1, "Choose an existing template")
		tmplSizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		
		self.templates = [x 
			for x in sorted(os.listdir(self.settings.templDir))
				if x.endswith(".pbt")]
		
		self.descText = {}
		for t in self.templates:
			self.descText[t] = self.getTemplateDesc(os.path.join(self.settings.templDir, t))
		
		self.chTempl = wx.Choice(self, wx.ID_ANY, choices = self.templates)
		self.chTempl.Bind(wx.EVT_CHOICE, self.onTemplChoice)
		if len(self.templates) > 0:
			self.chTempl.SetSelection(0)
			self.chosenTemplate = self.templates[0]
		tmplSizer.Add(self.chTempl, 0, wx.ALL, 10)
		
		self.tbTmplOk = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BDIM)
		self.setTemplateHelp()
		self.Bind(wx.EVT_BUTTON, self.onTmplOk, self.tbTmplOk)
		tmplSizer.Add(self.tbTmplOk, 0, wx.ALIGN_CENTER)
		
		hsizer.Add(tmplSizer, 0, wx.EXPAND)
		hsizer.AddSpacer((10, 10))
		
		box = wx.StaticBox(self, -1, "Choose proto board parameters")
		rightSizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		rightSizer.AddSpacer((20, 20))

		t1 = wx.StaticText(self, wx.ID_ANY, "Columns:")		
		self.scCols = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scCols.SetRange(5,100)
		self.scCols.SetValue(5)
		
		t2 = wx.StaticText(self, wx.ID_ANY, "Rows:")		
		self.scRows = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scRows.SetRange(5,100)
		self.scRows.SetValue(5)
		
		t3 = wx.StaticText(self, wx.ID_ANY, "Trace Length:")		
		self.scTraces = wx.SpinCtrl(self, wx.ID_ANY, size=(50, -1))
		self.scTraces.SetRange(1,20)
		self.scTraces.SetValue(1)
		
		t4 = wx.StaticText(self, wx.ID_ANY, "Full Length:")
		self.cbFull = wx.CheckBox(self, wx.ID_ANY, "")
		
		t5 = wx.StaticText(self, wx.ID_ANY, "Vertical Traces:")
		self.cbVert = wx.CheckBox(self, wx.ID_ANY, "")
		
		isizer = wx.FlexGridSizer(cols=4, hgap=6, vgap=6)
		isizer.AddMany([ t1, self.scCols, t2, self.scRows,
						 t3, self.scTraces, t4, self.cbFull,
						 t5, self.cbVert])
		
		rightSizer.Add(isizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT, 10)
		rightSizer.AddSpacer((10, 10))



		btnSizer=wx.BoxSizer(wx.HORIZONTAL)
		
		self.tbOk = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BDIM)
		self.tbOk.SetToolTipString("Create new proto-board file")
		self.Bind(wx.EVT_BUTTON, self.onOk, self.tbOk)
		btnSizer.Add(self.tbOk)
		
		btnSizer.AddSpacer((20, 20))
		
		self.tbCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BDIM)
		self.tbCancel.SetToolTipString("Exit without creating new file")
		self.Bind(wx.EVT_BUTTON, self.onClose, self.tbCancel)
		btnSizer.Add(self.tbCancel)
		
		rightSizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		hsizer.Add(rightSizer, 0, wx.EXPAND)
		hsizer.AddSpacer((20, 10))
		
		sizer.Add(hsizer)
		
		sizer.AddSpacer((20, 20))
		
		self.SetSizer(sizer)
		self.Fit()
		
	def getTemplateDesc(self, fnTmpl):
		try:
			with open(fnTmpl, "r") as x: xml = x.read()
		except:
			return None
		
		xmldoc = XMLDoc(xml, makelist=["trace", "cut", "removal", "wire", "component"])
		root = xmldoc.getRoot()
		try:
			return root.description
		except AttributeError:
			return None

	def onTemplChoice(self, evt):
		self.chosenTemplate = self.chTempl.GetStringSelection()
		self.setTemplateHelp()
		
	def setTemplateHelp(self):
		if self.chosenTemplate is None:
			self.tbTmplOk.SetToolTipString("Create based on a template")
		elif self.descText[self.chosenTemplate] is None:
			self.tbTmplOk.SetToolTipString("Create using template %s" % self.chosenTemplate)
		else:
			self.tbTmplOk.SetToolTipString("Create using %s" % self.descText[self.chosenTemplate])
		
	def getData(self):
		return self.pb
		
	def onTmplOk(self, evt):
		i = self.chTempl.GetSelection()
		fn = os.path.join(self.settings.templDir, self.chTempl.GetString(i))
		self.pb = self.parent.loadBoard(fn)
		self.EndModal(wx.ID_OK)
		
	def onOk(self, evt):
		r = self.scRows.GetValue()
		c = self.scCols.GetValue()
		vertical = self.cbVert.IsChecked()
		
		if self.cbFull.IsChecked():
			if vertical:
				tl = r
			else:
				tl = c
		else:
			tl = self.scTraces.GetValue()
		self.pb = ProtoBoard(c, r)

		if vertical:
			if tl > r:
				tl = r
			for i in range(c):
				for j in range(0, r-tl+1, tl):
					self.pb.addVTrace(i, j, j+tl-1)
			nl = r % tl
			if nl != 0:
				for i in range(c):
					self.pb.addVTrace(i, r-nl, r-1)
		else:		
			if tl > c:
				tl = c
			for i in range(r):
				for j in range(0, c-tl+1, tl):
					self.pb.addHTrace(j, j+tl-1, i)
			nl = c % tl
			if nl != 0:
				for i in range(r):
					self.pb.addHTrace(c-nl, c-1, i)
		
		self.EndModal(wx.ID_OK)
		
	def onClose(self, evt):
		self.EndModal(wx.ID_CANCEL)
