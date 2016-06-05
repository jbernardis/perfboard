import wx
TBDIM = (48, 48)

class MoveDlg(wx.Dialog):
	def __init__(self, parent, sz, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Specify movement amount")
		
		self.parent = parent
		self.images = settings.images

		
		self.shiftx = 0
		self.shifty = 0
		
		self.minx = -sz[0]+1
		self.maxx = sz[0]-1
		self.miny = -sz[1]+1
		self.maxy = sz[1]-1
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		slidesizer = wx.GridSizer(rows=1, cols=2)
		btnsizer = wx.StdDialogButtonSizer()

		self.slideX = wx.Slider(
			self, wx.ID_ANY, 0, self.minx, self.maxx, size=(150, -1),
			style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
		self.slideX.Bind(wx.EVT_SCROLL_CHANGED, self.onSpinX)
		self.slideX.Bind(wx.EVT_MOUSEWHEEL, self.onMouseX)
		self.slideX.SetPageSize(1);

		b = wx.StaticBox(self, wx.ID_ANY, "Horizontally")
		sbox = wx.StaticBoxSizer(b, wx.VERTICAL)
		sbox.Add(self.slideX, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
		slidesizer.Add(sbox, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
		
		self.slideY = wx.Slider(
			self, wx.ID_ANY, 0, self.miny, self.maxy, size=(-1, 150),
			style = wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS | wx.SL_INVERSE)
		self.slideY.Bind(wx.EVT_SCROLL_CHANGED, self.onSpinY)
		self.slideY.Bind(wx.EVT_MOUSEWHEEL, self.onMouseY)
		self.slideY.SetPageSize(1);

		b = wx.StaticBox(self, wx.ID_ANY, "Vertically")
		sbox = wx.StaticBoxSizer(b, wx.VERTICAL)
		sbox.Add(self.slideY, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5)
		slidesizer.Add(sbox, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5)
		
		btn = wx.BitmapButton(self, wx.ID_OK, self.images.pngOk, size=TBDIM)
		btn.SetToolTipString("Close dialog box to move components")
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.BitmapButton(self, wx.ID_CANCEL, self.images.pngCancel, size=TBDIM)
		btn.SetToolTipString("Cancel Move operation")
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		sizer.Add(slidesizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		
	def getValues(self):
		return self.shiftx, -self.shifty
		
	def onSpinX(self, evt):
		self.shiftx = evt.EventObject.GetValue()
	
	def onSpinY(self, evt):
		self.shifty = evt.EventObject.GetValue()
	
	def onMouseX(self, evt):
		l = self.slideX.GetValue()
		if evt.GetWheelRotation() < 0:
			l -= 1
		else:
			l += 1
		if l >= self.minx and l <= self.maxx:
			self.shiftx = l
			self.slideX.SetValue(l)
	
	def onMouseY(self, evt):
		l = self.slideY.GetValue()
		if evt.GetWheelRotation() < 0:
			l -= 1
		else:
			l += 1
		if l >= self.miny and l <= self.maxy:
			self.shifty = l
			self.slideY.SetValue(l)

