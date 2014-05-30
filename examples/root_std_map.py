import rootpy.stl as stl
import ROOT
 
# Create a vector type
StrVector = stl.vector(stl.string)
# Instantiate
strvector = StrVector()
strvector.push_back("Hello")
# etc.
MapStrRoot = stl.map(stl.string, ROOT.TH1D)
MapStrRootPtr = stl.map(stl.string, "TH1D*")
StrHist = stl.pair(stl.string, "TH1*")
m = MapStrRootPtr()
a = ROOT.TH1D('t1', 't1', 10, 0, 1)
m.insert(StrHist("test", a))
print m
