import ROOT as r
from rootpy.io import File
from rootpy.tree import Tree
from rootpy.plotting import Canvas, Hist
import json

# inputFile = File('/users/ec6821/tnpEle50ns/root/fit_mc_ele27_pt_med.root')
# canvasName = 'GsfElectronHLTMedium/HLT/fit_eff_plots/probe_pt_PLOT'

inputFile = File('~/Electron_ID_Iso_Ali_30072015.root ')
canvasName = 'c0'


canvas = inputFile.Get(canvasName)
print canvas.find_all_primitives()

# hist = canvas.GetPrimitive("hxy_fit_eff")
# print hist.Integral()
# print hist.GetN()

# binning = []
# xValues = []
# yValues = []
# yErrors = []
# for bin in range(0, hist.GetN()):
# 	x = r.Double(0)
# 	xErrorLow = hist.GetErrorXlow(bin)
# 	xErrorHigh = hist.GetErrorXhigh(bin)
# 	y = r.Double(0)
# 	hist.GetPoint(bin,x,y)

# 	binning.append( x - xErrorLow )
# 	xValues.append(x)
# 	yValues.append(y)
# 	yErrors.append(max(hist.GetErrorYlow(bin), hist.GetErrorYhigh(bin)))

# binning.append( x + hist.GetErrorXhigh(hist.GetN()-1))

# newFile = File('ElectronTriggerEfficiencies.root','recreate')
# newHist = Hist( binning, name='eff', title='eff' )
# for bin in range (1,newHist.GetNbinsX()+1):
# 	newHist.SetBinContent(bin,yValues[bin-1])
# 	newHist.SetBinError(bin,yErrors[bin-1])

# newHist.Write('eff')
# newFile.Close()