'''
Created on Dec 28, 2015

@author: Jeff
'''
import os
import sys, inspect
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
    
from XMLDoc import XMLDoc

import wx
from protoboard import ProtoBoard
from protoboarddlg import ProtoBoardDialog
from newfiledlg import NewFileDialog
from newtempdlg import NewTempDialog
from images import Images

from protoboard.component import StretchComponent, StretchComponentList, LT_WIRE, WIRENAME, FixedComponentList, GrowComponentList, compID

wildcard = "Proto-board file (*.pb)|*.pb"

class Settings:
    def __init__(self):
        self.cmdfolder = cmd_folder
        self.usebuffereddc = True

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Proto-board layout editor")
        
        self.settings = Settings()
	self.editDlg = None
	self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.settings.images = Images(os.path.join(self.settings.cmdfolder, "images"))
        self.settings.compImages = Images(os.path.join(self.settings.cmdfolder, "components"))

        self.settings.fixedComponentList = FixedComponentList(self.settings.compImages)
        self.settings.stretchComponentList = StretchComponentList()
        self.settings.growComponentList = GrowComponentList(self.settings.compImages)
        self.settings.cmdFolder = cmd_folder
        self.settings.templDir = os.path.join(self.settings.cmdFolder, "templates")

        
        self.fileName = None
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer((50, 20))
        
        self.bNewTemp = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngNewtemp, size=(64, 64))
        self.bNewTemp.SetToolTipString("Create a new Strip-Board template")
        self.Bind(wx.EVT_BUTTON, self.onNewTemp, self.bNewTemp)
        sizer.Add(self.bNewTemp, 1, wx.ALL, 10)
        
        self.bNew = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngNew, size=(64, 64))
        self.bNew.SetToolTipString("Create a new Strip-Board")
        self.Bind(wx.EVT_BUTTON, self.onNew, self.bNew)
        sizer.Add(self.bNew, 1, wx.ALL, 10)
        
        self.bOpen = wx.BitmapButton(self, wx.ID_ANY, self.settings.images.pngOpen, size=(64, 64))
        self.bOpen.SetToolTipString("Open an existing Strip-Board file")
        self.Bind(wx.EVT_BUTTON, self.onOpen, self.bOpen)
        sizer.Add(self.bOpen, 1, wx.ALL, 10)
        
        sizer.AddSpacer((50, 20))
        self.SetSizer(sizer)
        self.Fit()

    def onClose(self, evt):
        if self.editDlg is not None:
		return

	self.Destroy()

    def onNewTemp(self, evt):
        dlg = NewTempDialog(self)
        rc = dlg.ShowModal()
        
    def onNew(self, evt): 
        compID.reInit()       
        dlg = NewFileDialog(self)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            pb = dlg.getData()
            
        dlg.Destroy()
        if rc != wx.ID_OK:
            return
        
        if pb is None:
            return
        
        self.fileName = None
        self.presentEditor(pb)
        
    def onOpen(self, evt):
        dlg = wx.FileDialog(
            self, message="Choose a proto-board file...",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )

        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            path = dlg.GetPath()
        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        sb = self.loadBoard(path)
        if sb is None:
            dlg = wx.MessageDialog(self, 'Error loading proto-board file: ' + path,
                'Load Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.fileName = path
            self.presentEditor(sb)
     
    def presentEditor(self, pb):       
        self.editDlg = ProtoBoardDialog(self, pb, self.fileName, self.settings)
	self.editDlg.Show()
	self.bOpen.Enable(False)
	self.bNew.Enable(False)
	self.bNewTemp.Enable(False)
        #dlg.ShowModal()
        #dlg.Destroy()

    def onEditorClose(self):
        self.editDlg.Destroy()
        self.editDlg = None
	self.bOpen.Enable(True)
	self.bNew.Enable(True)
	self.bNewTemp.Enable(True)
  
        
    def loadBoard(self, fn):
        try:
            with open(fn, "r") as x: xml = x.read()
        except:
            return None
        
        xmldoc = XMLDoc(xml, makelist=["trace", "cut", "removal", "wire", "component"])
        
        compID.reInit()
        
        root = xmldoc.getRoot()
        sz = [int(x) for x in str(root.size).split(',')]
        
        pb = ProtoBoard(sz[0], sz[1])
        
        try:
            tl = root.htraces.trace
        except AttributeError:
            tl = []
            
        for t in tl:
            trc = [int(x) for x in str(t).split(',')]
            pb.addHTrace(trc[0], trc[1], trc[2])
        
        try:
            tl = root.vtraces.trace
        except AttributeError:
            tl = []
            
        for t in tl:
            trc = [int(x) for x in str(t).split(',')]
            pb.addVTrace(trc[0], trc[1], trc[2])
        
        try:
            s = str(root.hskips).strip()
        except AttributeError:
            s = ""
 
        if len(s) > 0:
            for sk in s.split(','):
                pb.addHSkip(int(sk))
        
        try:
            s = str(root.vskips).strip()
        except AttributeError:
            s = ""
 
        if len(s) > 0:
            for sk in s.split(','):
                pb.addVSkip(int(sk))
        
        try:
            cl = root.hcuts.cut
        except AttributeError:
            cl = []
            
        for c in cl:
            cut = [int(x) for x in str(c).split(',')]
            pb.addHCut(cut[0], cut[1], cut[2])
        
        try:
            cl = root.vcuts.cut
        except AttributeError:
            cl = []
            
        for c in cl:
            cut = [int(x) for x in str(c).split(',')]
            pb.addVCut(cut[0], cut[1], cut[2])
        
        try:
            rl = root.removals.removal
        except AttributeError:
            rl = []
            
        for r in rl:
            rmv = [int(x) for x in str(r).split(',')]
            pb.traceRemove([rmv[0], rmv[1]])

        try:
            wirelist = root.wires.wire
        except AttributeError:
            wirelist = []
             
        for w in wirelist:
            s = str(w.pointa)
            pta = [int(x) for x in s.split(',')]
            s = str(w.pointb)
            ptb = [int(x) for x in s.split(',')]
            s = str(w.color)
            clr = [int(x) for x in s.split(',')]
             
            c = StretchComponent(WIRENAME, pta, ptb, LT_WIRE)
            pb.addWire(c, wx.Colour(clr[0], clr[1], clr[2]))
             
        try:
            complist = root.components.component
        except AttributeError:
            complist = []
 
        cl = self.settings.fixedComponentList
        for c in complist:
            tp = str(c.type)
            cid = str(c.id)
            nm = str(c.name)
            value = str(c.value)
            s = str(c.anchor)
            vw = int(str(c.view))
            
            anchor = [int(x) for x in s.split(',')]
            comp = cl.getComponent(tp)[0]
            comp.setID(cid)
            comp.setName(nm)
            comp.setValue(value)
            comp.setAnchor(anchor)
            cl.setView(comp, vw)
            pb.addComponent(comp)
            compID.reserveID(cid)
 
        try:
            complist = root.stretchcomponents.component
        except AttributeError:
            complist = []
 
        cl = self.settings.stretchComponentList
        for c in complist:
            tp = str(c.type)
            cid = str(c.id)
            nm = str(c.name)
            value = str(c.value)
            s = str(c.pointa)
            pta = [int(x) for x in s.split(',')]
            s = str(c.pointb)
            ptb = [int(x) for x in s.split(',')]
             
            comp = cl.getComponent(tp)[0]
            comp.setID(cid)
            comp.setP1(pta)
            comp.setP2(ptb)
            comp.setName(nm)
            comp.setValue(value)
            pb.addStretchComponent(comp)
            compID.reserveID(cid) 
 
        try:
            complist = root.growcomponents.component
        except AttributeError:
            complist = []
 
        cl = self.settings.growComponentList
        for c in complist:
            tp = str(c.type)
            cid = str(c.id)
            nm = str(c.name)
            value = str(c.value)
            s = str(c.pointa)
            pta = [int(x) for x in s.split(',')]
            s = str(c.pointb)
            ptb = [int(x) for x in s.split(',')]
             
            comp = cl.getComponent(tp)[0]
            comp.setID(cid)
            comp.setP1(pta)
            comp.setP2(ptb)
            comp.setName(nm)
            comp.setValue(value)
            pb.addGrowComponent(comp)
            compID.reserveID(cid)

            
        pb.setModified(False)
        return pb
            
 
app = wx.App(False)
frame = MyFrame()
frame.Show(True)
app.MainLoop()
