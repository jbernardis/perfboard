import xml.parsers.expat
import keyword

class XMLNode:
    def __init__(self, doc, nm, a={}, v=None, silent=False, makelist=None):
        self.doc = doc
        self.silent = silent
        self.__name__ = self.legalize(nm)
        self.setValue(v)
        self.__xmlAttrs__ = a.copy()
        self.__attrs__ = []
        self.__makelist__ = makelist
        
    def legalize(self, n):
        nm = self.doc.translate(n)
        
        if nm in keyword.kwlist:
            if not self.silent:
                print "name (%s) is a reserved python keyword - using (_%s)" % (nm, nm)
            return "_" + nm
        
        onm = nm
        nm = ''.join(e for e in nm if e.isalnum())
        
        if nm[0].isdigit():
            nm = "_" + nm
            
        if onm != nm:
            if not self.silent:
                print "modified name (%s) to (%s)" % (onm, nm)
            
        return nm


    def isAForcedList(self, cn):
        if self.__makelist__ is None:
            return False
        if len(self.__makelist__) == 0:
            return True
        return cn in self.__makelist__
        
    def getName(self):
        return self.__name__
        
    def setValue(self, v):
        self.__value__ = v
        
    def __str__(self):
        if self.__value__ is None or isinstance(self.__value__, XMLNode):
            return "<" + self.__name__ + ">"
        else:
            return self.getValue()
        
    def getValue(self):
        return str(self.__value__)
    
    def getAttr(self, k):
        if k in self.__xmlAttrs__.keys():
            return self.__xmlAttrs__[k]
        else:
            return None
    
    def addChild(self, cn, v):
        n = self.legalize(cn)
        if n not in self.__attrs__:
            self.__attrs__.append(n)
            
        try:
            ov = getattr(self, n)
            if self.isAForcedList(cn):
                ov.append(v)
                setattr(self, n, ov)
            else:
                if isinstance(ov, list):
                    ov.append(v)
                    setattr(self, n, ov)
                else:
                    l = []
                    l.append(ov)
                    l.append(v)
                    setattr(self, n, l)
            
        except AttributeError:
            if self.isAForcedList(cn):
                setattr(self, n, [v])
            else:
                setattr(self, n, v)

            
    def hasChild(self, cn):
        n = self.legalize(cn)
        return (n in self.__attrs__)
            
    def delChild(self, cn):
        n = self.legalize(cn)
        try:
            self.__attrs__.remove(n)
            delattr(self, n)
            return True
        except:
            return False
           
    def getChild(self, cn):
        n = self.legalize(cn)
        if n in self.__attrs__:
            return getattr(self, n)
        else:
            return None
    
    def getChildrenNames(self):
        return self.__attrs__
            

class XMLDoc:
    def __init__(self, text, symtab={}, makelist=None):
        self.currentNode = None
        self.stack = []
        self.dataVal = None
        self.docRoot = None
        self.inhskips = False
        self.symtab = symtab
        self.makelist = makelist
        p = xml.parsers.expat.ParserCreate()

        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data

        p.Parse(text,  1)
        
    def translate(self, nm):
        if nm in self.symtab.keys():
            return self.symtab[nm]
        
        return nm
        
    def getRoot(self):
        return self.docRoot
    
    def start_element(self, name, attrs):
        c = XMLNode(self, name, attrs, self.currentNode, makelist=self.makelist)
        if self.currentNode is not None:
            self.currentNode.addChild(name, c)
            self.stack.append(self.currentNode)
        self.currentNode = c
        self.dataVal = None
        if self.docRoot is None:
            self.docRoot = c
  
    def end_element(self, name):
        if self.currentNode is None:
            print "Invalid XML end: ", name
            exit(1)
            
        if len(self.stack) == 0:
            self.currentNode = None
            return
            
        if self.dataVal is not None:
            self.currentNode.setValue(self.dataVal)
            self.dataVal = None
        else:
            self.currentNode.setValue("")

        self.currentNode = self.stack.pop()
 
    def char_data(self, data):
        d = data.strip()
        if d == "":
            if self.dataVal is None:
                self.dataVal = ""
            return
        
        if self.dataVal is None:
            self.dataVal = d
        else:
            self.dataVal += d


    
    


