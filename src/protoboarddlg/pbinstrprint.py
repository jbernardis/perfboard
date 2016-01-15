'''
Created on Jan 5, 2016

@author: Jeff
'''
import wx

class PBInstructionsPrint(wx.Printout):
    def __init__(self, pb):
        wx.Printout.__init__(self)
        self.pb = pb
        self.instructions = self.pb.getInstructions()

    def OnBeginDocument(self, start, end):
        return super(PBInstructionsPrint, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(PBInstructionsPrint, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(PBInstructionsPrint, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(PBInstructionsPrint, self).OnEndPrinting()

    def OnPreparePrinting(self):
        super(PBInstructionsPrint, self).OnPreparePrinting()

    def HasPage(self, page):
        if page < 2:
            return True
        else:
            return False

    def GetPageInfo(self):
        # minpage, maxpage, pagefrom, pageto
        return (1, 1, 1, 1)

    def OnPrintPage(self, page):
        if page != 1:
            return False
        
        dc = self.GetDC()

        text = 'XXXXXXXXXX'

        # (width, height) in pixels
        otw, oth = dc.GetTextExtent(text)
        
        font = wx.Font (12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(font)

        # (width, height) in pixels
        tw, th = dc.GetTextExtent(text)
        sfw = int(otw/tw)
        sfh = int(oth/th)
        scale = min(sfw, sfh)
        
        lineHt = th + 0

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Get the size of the DC in pixels
        h = dc.GetSizeTuple()[1]
        lpp = int(h/scale/lineHt)


        #-------------------------------------------

        dc.SetUserScale(scale, scale)
        ln = 0
        for i in self.instructions:
            dc.DrawText(i, marginX, marginY + ln)
            ln += lineHt
        return True
 


