'''
Created on Jan 2, 2016

@author: Jeff
'''
import wx

BDIM = (48, 48)
       
class InfoDialog(wx.Dialog):
    def __init__(self, parent, cid, sname, svalue):
        self.parent = parent 
        self.settings = parent.settings
        self.images = parent.images
        self.startName = sname
        self.startValue = svalue
        
        title = "View/Edit Component %s Name and Value" % cid
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(100, 100))
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.AddSpacer((20, 20))
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        t1 = wx.StaticText(self, wx.ID_ANY, "Component Name:")
        i1 = wx.TextCtrl(self, wx.ID_ANY, self.startName)
        t2 = wx.StaticText(self, wx.ID_ANY, "Component Value:")
        i2 = wx.TextCtrl(self, wx.ID_ANY, self.startValue)
        isizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        isizer.AddMany([ t1, i1, t2, i2])
        self.tcName = i1
        self.tcValue = i2

        hsizer.AddSpacer((50, 10))
        hsizer.Add(isizer)
        sizer.Add(hsizer)
        
        sizer.AddSpacer((20, 20))

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btnSizer.AddSpacer((100, 20))
        
        self.tbOk = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BDIM)
        self.tbOk.SetToolTipString("Save name and value")
        self.Bind(wx.EVT_BUTTON, self.onOk, self.tbOk)
        btnSizer.Add(self.tbOk)
        
        btnSizer.AddSpacer((20, 20))
        
        self.tbCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BDIM)
        self.tbCancel.SetToolTipString("Exit without saving name or value")
        self.Bind(wx.EVT_BUTTON, self.onClose, self.tbCancel)
        btnSizer.Add(self.tbCancel)
        
        btnSizer.AddSpacer((100, 20))

        sizer.Add(btnSizer)
        sizer.AddSpacer((20, 20))
        
        self.SetSizer(sizer)
        self.Fit()
        
    def getData(self):
        n = self.tcName.GetValue()
        v = self.tcValue.GetValue()
        
        return n,v
        
    def onOk(self, evt):
        self.EndModal(wx.ID_OK)
        
    def onClose(self, evt):
        self.EndModal(wx.ID_CANCEL)

