'''
Created on Nov 23, 2011

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''
from ROOT import TLegend, TCanvas, TPaveText, gROOT
import Styles
import FileUtilities
qcd_samples = [ 'QCD_Pt-20to30_BCtoE',
                 'QCD_Pt-30to80_BCtoE',
                 'QCD_Pt-80to170_BCtoE',
                 'QCD_Pt-20to30_EMEnriched',
                 'QCD_Pt-30to80_EMEnriched',
                 'QCD_Pt-80to170_EMEnriched',
                 'GJets_HT-40To100',
                 'GJets_HT-100To200',
                 'GJets_HT-200']
singleTop_samples = [ 'T_tW-channel',
                 'T_t-channel',
                 'T_s-channel',
                 'Tbar_tW-channel',
                 'Tbar_t-channel',
                 'Tbar_s-channel']
wplusjets_samples = [ 'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets']
diboson_samples = [ 'WWtoAnything', 'WZtoAnything', 'ZZtoAnything']
signal_samples = [ 'TTJet', 'SingleTop']
allMC_samples = [ 'TTJet', 'DYJetsToLL', 'QCD', 'Di-Boson', 'W+Jets', 'SingleTop']

defaultCanvasWidth = 1600
defaultCanvasHeight = 1200

class Plot():
    '''
    Plot unites the tuning parameters for plot style
    '''
    def __init__(self):
        self.rebin = 1
        self.scale = 1
        self.UserRange = (0, 0)
        self.name = ""
        self.location = ""
        self.jetBins = []
        self.bJetBins = []
        self.qcdShapeFrom = ""
        self.qcdEstimate = 0 
        
def compareShapes(histograms=[], histogramlables=[], styles=[], maxfactor = 1.3):
    leg = TLegend(0.6, 0.7, 0.94, 0.92);
    leg.SetBorderSize(0);
    leg.SetLineStyle(0);
    leg.SetTextFont(42);
    leg.SetFillStyle(0);
    AddLegendEntry = leg.AddEntry 
    
    c = TCanvas("compareShapes", 'compareShapes', defaultCanvasWidth, defaultCanvasHeight)
    c.cd()

    for hist, label, style in zip(histograms,histogramlables,styles):
        hist.Sumw2()
        hist = normalise(hist)
        hist.SetLineColor(style['color'])
        hist.SetLineWidth(4)
        
        AddLegendEntry(hist, label, "f")
        
    index = 0
    maximum = getMax(histograms)
    for hist in histograms:
        if index == 0:
            hist.GetYaxis().SetRangeUser(0, maximum*maxfactor)
            hist.Draw('histe')
        else:
            hist.Draw('histe same')
        index += 1
    
    return c, leg

def create_cms_label(lumiInInvPb, njet="4orMoreJets", nbjet="0orMoreBtag", channel="e"):
    jetBinsLatex = {'0jet':'0 jet', '0orMoreJets':'#geq 0 jets', '1jet':'1 jet', '1orMoreJets':'#geq 1 jet',
                    '2jets':'2 jets', '2orMoreJets':'#geq 2 jets', '3jets':'3 jets', '3orMoreJets':'#geq 3 jets',
                    '4orMoreJets':'#geq 4 jets'}

    BjetBinsLatex = {'0btag':'0 b-tags', '0orMoreBtag':'#geq 0 b-tags', '1btag':'1 b-tags',
                    '1orMoreBtag':'#geq 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'#geq 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'#geq 3 b-tags',
                    '4orMoreBtags':'#geq 4 b-tags'}

    mytext = TPaveText(0.35, 0.7, 0.7, 0.93, "NDC")
    mytext.AddText("CMS Preliminary")
    mytext.AddText("%.2f fb^{-1} at #sqrt{s} = 7 TeV" % (lumiInInvPb / 1000))
    if njet != "":
        mytext.AddText(channel + ", %s, %s" % (jetBinsLatex[njet], BjetBinsLatex[nbjet]))   
             
    mytext.SetFillStyle(0);
    mytext.SetBorderSize(0);
    mytext.SetTextFont(42);
    mytext.SetTextAlign(13);
    
    return mytext

def create_legend(x0=0.696, y0 = 0.95, x1=0.94, y1=0.55):
#    legend = TLegend(0.6, 0.7, 0.94, 0.92);
    legend = TLegend(x0, y0, x1, y1)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    legend.SetFillStyle(0);
    return legend

def saveAs(canvas, name, outputFormats=['png'], outputFolder=''):
    canvas.RedrawAxis()
    if not outputFolder == '' and not outputFolder.endswith('/'):
        outputFolder += '/'
    for outputFormat in outputFormats:
        fullFileName = outputFolder + name + '.' + outputFormat
        if '/' in fullFileName:
            path = fullFileName[:fullFileName.rfind('/')]
            FileUtilities.createFolderIfDoesNotExist(path)
        
        canvas.SaveAs(fullFileName)
        
def normalise(histogram):
    if histogram and histogram.Integral() > 0:
        histogram.Scale(1 / histogram.Integral())
    return histogram

def rebin(hists, nbins, histname = ''):
    for sample in hists.keys():
        if isinstance(hists[sample], dict):
            if len(hists[sample].keys()) == 0 or 'Stack' in sample:
                continue
            if '*' in histname:
                nameToken = histname.replace('*', '')
                histlist = hists[sample]
                for name in histlist.keys():
                    if nameToken in name:
                        hists[sample][name].Rebin(nbins)
            elif hists[sample].has_key(histname):
                hists[sample][histname].Rebin(nbins)
        else:
            hists[sample].Rebin(nbins)
    return hists

def setXRange(hists, limits=(0, 5000), histname=''):
    for sample in hists.keys():
        if len(hists[sample].keys()) == 0 or 'Stack' in sample:
            continue
        if '*' in histname:
            nameToken = histname.replace('*', '')
            histlist = hists[sample]
            for name in histlist.keys():
                if nameToken in name:
                    if hists[sample][name] and hists[sample][name].GetXaxis():
                        hists[sample][name].GetXaxis().SetRangeUser(limits[0], limits[1])
                    else:
                        print "Can't find histogram", sample, name
        elif hists[sample].has_key(histname):
            if hists[sample][name]:
                hists[sample][histname].GetXaxis().SetRangeUser(limits[0], limits[1]);
            else:
                print "Can't find histogram", sample, name
    return hists

def setYRange(hists, limits=(0, 5000), histname=''):
    for sample in hists.keys():
        if len(hists[sample].keys()) == 0 or 'Stack' in sample:
            continue
        if '*' in histname:
            nameToken = histname.replace('*', '')
            histlist = hists[sample]
            for name in histlist.keys():
                if nameToken in name:
                    if hists[sample][name] and hists[sample][name].GetYaxis():
                        hists[sample][name].GetYaxis().SetRangeUser(limits[0], limits[1])
                    else:
                        print "Can't find histogram", sample, name
        elif hists[sample].has_key(histname):
            if hists[sample][name]:
                hists[sample][histname].GetYaxis().SetRangeUser(limits[0], limits[1]);
            else:
                print "Can't find histogram", sample, name
    return hists
    
def setXTitle(hists, title, histname=''):
    for sample in hists.keys():
        if isinstance(hists[sample], dict):
            if len(hists[sample].keys()) == 0 or 'Stack' in sample:
                continue
            if '*' in histname:
                nameToken = histname.replace('*', '')
                histlist = hists[sample]
                for name in histlist.keys():
                    if nameToken in name:
                        hists[sample][name].SetXTitle(title)
            elif hists[sample].has_key(histname):
                hists[sample][histname].SetXTitle(title);
        else:
            hists[sample].SetXTitle(title);
    return hists

def setYTitle(hists, title, histname=''):
    for sample in hists.keys():
        if isinstance(hists[sample], dict):
            if len(hists[sample].keys()) == 0 or 'Stack' in sample:
                continue
            if '*' in histname:
                nameToken = histname.replace('*', '')
                histlist = hists[sample]
                for name in histlist.keys():
                    if nameToken in name:
                        hists[sample][name].SetYTitle(title)
            elif hists[sample].has_key(histname):
                hists[sample][histname].SetYTitle(title);
        else:
            hists[sample].SetYTitle(title);
    return hists   

def setStyle():
    tdrStyle = Styles.tdrStyle.getStyle()

    #slight adaptation
    tdrStyle.SetPadRightMargin(0.05); #originally was 0.02, too narrow!
    tdrStyle.SetStatH(0.2);
    #tdrStyle.SetOptStat(1110);//off title
    tdrStyle.SetOptStat(0);#off title
    tdrStyle.SetOptFit(0);#off title
#    tdrStyle.SetTitleYOffset(1.6);
    tdrStyle.cd();
    gROOT.ForceStyle();     
    
def getMax(histograms):
    maximum = 0
    for hist in histograms:
        current_max = hist.GetMaximum()
        if current_max > maximum:
            maximum = current_max
    return maximum
#Usage:
#histograms['summedSample'] = sumSamples(histograms, ['sample1','sample2', 'sample3'])
def sumSamples(histograms = {}, samplesToSum = []):
    summedHists = {}
    summedHist = None
    doubleDictionary = False
    
    for sample in samplesToSum:
        hists = histograms[sample]
        if isinstance(hists, dict):
            doubleDictionary = True
            for histname, hist in hists.iteritems():
                if summedHists.has_key(histname):
                    summedHists[histname] += hist
                else:
                    summedHists[histname] = hist
        else:
            if summedHist:
                summedHist += hists
            else:
                summedHist = hists
    if doubleDictionary:        
        return summedHists
    else:
        return summedHist
            
        
def plot(histograms = [], data = 0, makeStack = True, outputFormats = ['png', 'pdf'], normalise = False, ratio = False ):
    pass