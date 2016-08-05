import wx
from protoboarddlg.pbframe import PBFrame

class ProtoBoardPreview(wx.Dialog):
	def __init__(self, parent, pb, position, settings):
		self.parent = parent 
		self.pb = pb
		self.settings = settings
		
		self.lastReport = None
		
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Preview", size=(400, 400), pos=position)
		self.SetBackgroundColour("white")
		
		self.SetClientSize((600, 300))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.dsp = PBFrame(self, self.pb, self.settings)
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.Add(self.dsp)
		
		sz.AddSpacer((3,3))
		
		self.statusLine = wx.StaticText(self, wx.ID_ANY, "")
		sz.Add(self.statusLine)
		
		sz.AddSpacer((3,3))

		self.SetSizer(sz)
		self.Fit()
		self.dsp.refresh()
		
	def holeDrag(self, p1, p2):
		pass
		
	def holeClick(self, p):
		pass
		
	def holeDoubleClick(self, p):
		pass
		
	def rightClick(self, p):
		pass
		
	def setHiLightedPos(self, pos):
		self.dsp.setHiLightedNet(pos)
		self.refresh()
		
	def refresh(self):
		self.dsp.refresh()
		
	def onClose(self, evt):
		self.Destroy()
		
	def reportCoordinate(self, pos):
		if pos == self.lastReport:
			return
		
		self.lastReport = pos
		text = "	 (%s,%d)" % (pos[0], pos[1])
		self.statusLine.SetLabel(text)
