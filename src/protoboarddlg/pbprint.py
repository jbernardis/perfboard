'''
Created on Jan 5, 2016

@author: Jeff
'''
import wx

class PBPrint(wx.Printout):
    def __init__(self, canvas, filename):
        wx.Printout.__init__(self)
        self.canvas = canvas
        self.filename = filename

    def OnBeginDocument(self, start, end):
        return super(PBPrint, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(PBPrint, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(PBPrint, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(PBPrint, self).OnEndPrinting()

    def OnPreparePrinting(self):
        super(PBPrint, self).OnPreparePrinting()

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

        clX, clY = self.canvas.GetClientSize()
        maxX = clX
        maxY = clY

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Add the margin to the graphic size
        maxX = maxX + (2 * marginX)
        maxY = maxY + (2 * marginY)

        # Get the size of the DC in pixels
        (w, h) = dc.GetSizeTuple()

        # Calculate a suitable scaling factor
        scaleX = float(w) / maxX
        scaleY = float(h) / maxY

        # Use x or y scaling factor, whichever fits on the DC
        actualScale = min(scaleX, scaleY)
        
        if actualScale > 6:
            actualScale = 6

        # Calculate the position on the DC for centering the graphic
        posX = (w - (clX * actualScale)) / 2.0
        posY = (h - (clY * actualScale)) / 2.0

        # Set the scale and origin
        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        #-------------------------------------------

        self.canvas.drawGraph(dc)
        if self.filename is None:
            fn = "<untitled>"
        else:
            fn = self.filename
        dc.DrawText("File: %s" % fn, marginX/2, maxY-marginY)


        return True
 
