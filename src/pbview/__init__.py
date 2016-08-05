import wx
from protoboarddlg.pbframe import PBFrame

class ProtoBoardView(wx.Dialog):
	def __init__(self, parent, pb, position, settings):
		self.parent = parent 
		self.pb = pb
		self.settings = settings
		
		self.lastReport = None
		
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "PCB", size=(400, 400), pos=position)
		self.SetBackgroundColour("white")
		
		self.SetClientSize((600, 600))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Show()
		
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
		self.parent.holeDrag(p1, p2)
		
	def holeClick(self, p):
		self.parent.holeClick(p)
		
	def holeDoubleClick(self, p):
		self.parent.holeDoubleClick(p)
		
	def rightClick(self, p):
		self.parent.rightClick(p)
		
	def setHiLightedPos(self, pos):
		self.dsp.setHiLightedNet(pos)
		self.refresh()
		
	def refresh(self):
		self.dsp.refresh()
		
	def onClose(self, evt):
		evt.Veto()
		
	def getPBFrame(self):
		return self.dsp
		
	def reportCoordinate(self, pos):
		if pos == self.lastReport:
			return
		
		self.lastReport = pos
		text = "  (%d,%d)" % (pos[0], pos[1])
		self.statusLine.SetLabel(text)
		self.parent.reportCoordinate(pos)
