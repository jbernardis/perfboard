import wx
TBDIM = (48, 48)

class TrimDlg(wx.Dialog):
	def __init__(self, parent, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Trim/Grow PCB edges")
		
		self.parent = parent
		self.images = settings.images

		
		sizer = wx.BoxSizer(wx.VERTICAL)
		kpdsizer = wx.GridSizer(rows=5, cols=5)
		btnsizer = wx.StdDialogButtonSizer()
		
		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))
		
		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngUp, size=TBDIM)
		btn.SetToolTipString("Trim top edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onTopEdge, btn)
		
		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))
		
		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))
		
		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGup, size=TBDIM)
		btn.SetToolTipString("Grow top edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onTopEdgeGrow, btn)
		
		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))

		
		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngLeft, size=TBDIM)
		btn.SetToolTipString("Trim left edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onLeftEdge, btn)
		
		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGleft, size=TBDIM)
		btn.SetToolTipString("Grow left edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onLeftEdgeGrow, btn)
		
		kpdsizer.Add((20,20))
	
		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGright, size=TBDIM)
		btn.SetToolTipString("Grow right edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onRightEdgeGrow, btn)

		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngRight, size=TBDIM)
		btn.SetToolTipString("Trim right edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onRightEdge, btn)

		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))
		
		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGdown, size=TBDIM)
		btn.SetToolTipString("Grow bottom edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onBottomEdgeGrow, btn)
		
		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))

		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))
		
		btn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDown, size=TBDIM)
		btn.SetToolTipString("Trim bottom edge of PCB")
		kpdsizer.Add(btn)
		self.Bind(wx.EVT_BUTTON, self.onBottomEdge, btn)
		
		kpdsizer.Add((20,20))
		kpdsizer.Add((20,20))

		btn = wx.BitmapButton(self, wx.ID_OK, self.images.pngOk, size=TBDIM)
		btn.SetToolTipString("Close dialog")
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btnsizer.Realize()

		sizer.Add(kpdsizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		
	def onTopEdge(self, evt):
		self.parent.trimTop()
				
	def onTopEdgeGrow(self, evt):
		self.parent.growTop()
				
	def onBottomEdge(self, evt):
		self.parent.trimBottom()   
			
	def onBottomEdgeGrow(self, evt):
		self.parent.growBottom()  
			
	def onLeftEdge(self, evt):
		self.parent.trimLeft()
					
	def onLeftEdgeGrow(self, evt):
		self.parent.growLeft()
					
	def onRightEdge(self, evt):
		self.parent.trimRight()	
						
	def onRightEdgeGrow(self, evt):
		self.parent.growRight()