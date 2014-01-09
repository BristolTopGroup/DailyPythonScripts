from __future__ import division
from tdrStyle import *
from ROOT import gROOT, kRed, kGreen, kAzure, kBlue, kYellow, kMagenta, kTeal, kCyan, kOrange, TPaveText, TCanvas
import os


inclusiveJetBins = [
        "0orMoreJets",
        "1orMoreJets",
        "2orMoreJets",
        "3orMoreJets" , 
        "4orMoreJets"]

exclusiveJetBins = [
        "0jet",
        "1jet",
        "2jets",
        "3jets"]

inclusiveBjetBins = [
        "0orMoreBtag",
        "1orMoreBtag",
        "2orMoreBtags",
        "3orMoreBtags",
        '4orMoreBtags' ]

exclusiveBjetBins = [
        '0btag',
        "1btag",
        "2btags",
        "3btags"]

allJetBins = []
allJetBins.extend(inclusiveJetBins)
allJetBins.extend(exclusiveJetBins)

allBjetBins = []
allBjetBins.extend(inclusiveBjetBins)
allBjetBins.extend(exclusiveBjetBins)

jetBinsLatex = {'0jet':'0 jet', '0orMoreJets':'#geq 0 jets', '1jet':'1 jet', '1orMoreJets':'#geq 1 jet',
                    '2jets':'2 jets', '2orMoreJets':'#geq 2 jets', '3jets':'3 jets', '3orMoreJets':'#geq 3 jets',
                    '4orMoreJets':'#geq 4 jets'}

BjetBinsLatex = {'0btag':'0 b-tags', '0orMoreBtag':'#geq 0 b-tags', '1btag':'1 b-tags', 
                    '1orMoreBtag':'#geq 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'#geq 2 b-tags', 
                    '3btags':'3 b-tags', '3orMoreBtags':'#geq 3 b-tags',
                    '4orMoreBtags':'#geq 4 b-tags'}

def setStyle():
        tdrStyle = setTDRStyle();

        #slight adaptation
        tdrStyle.SetPadRightMargin( 0.05 ); #originally was 0.02, too narrow!
        tdrStyle.SetStatH( 0.2 );
        #tdrStyle.SetOptStat(1110);//off title
        tdrStyle.SetOptStat( 0 );#off title
        tdrStyle.SetOptFit( 0 );#off title
        tdrStyle.cd();
        gROOT.ForceStyle();


def rebin( hists, nbins, histname ):
    for sample in hists.keys():
        if len( hists[sample].keys() ) == 0 or 'Stack' in sample:
            continue
        if '*' in histname:
            nameToken = histname.replace('*', '')
            histlist = hists[sample]
            for name in histlist.keys():
                if nameToken in name:
                    hists[sample][name].Rebin( nbins )
        elif hists[sample].has_key( histname ):
            hists[sample][histname].Rebin( nbins )
    return hists

def setXRange( hists, limits = ( 0, 5000 ), histname = '' ):
    for sample in hists.keys():
        if len( hists[sample].keys() ) == 0 or 'Stack' in sample:
            continue
        if '*' in histname:
            nameToken = histname.replace('*', '')
            histlist = hists[sample]
            for name in histlist.keys():
                if nameToken in name:
                    if hists[sample][name] and hists[sample][name].GetXaxis():
                        hists[sample][name].GetXaxis().SetRangeUser( limits[0], limits[1] )
                    else:
                        print "Can't find histogram", sample, name
        elif hists[sample].has_key( histname ):
            if hists[sample][name]:
                hists[sample][histname].GetXaxis().SetRangeUser( limits[0], limits[1] );
            else:
                print "Can't find histogram", sample, name
    return hists


def setXTitle( hists, title, histname = '' ):
    for sample in hists.keys():
        if len( hists[sample].keys() ) == 0 or 'Stack' in sample:
            continue
        if '*' in histname:
            nameToken = histname.replace('*', '')
            histlist = hists[sample]
            for name in histlist.keys():
                if nameToken in name:
                    hists[sample][name].SetXTitle( title )
        elif hists[sample].has_key( histname ):
            hists[sample][histname].SetXTitle( title );
    return hists

def setYTitle( hists, title, histname = '' ):
    for sample in hists.keys():
        if len( hists[sample].keys() ) == 0 or 'Stack' in sample:
            continue
        if '*' in histname:
            nameToken = histname.replace('*', '')
            histlist = hists[sample]
            for name in histlist.keys():
                if nameToken in name:
                    hists[sample][name].SetYTitle( title )
        elif hists[sample].has_key( histname ):
            hists[sample][histname].SetYTitle( title );
    return hists

#    for sample in hists.keys():
#        if len( hists[sample].keys() ) == 0 or not hists[sample].has_key( histname ) or not len( limits ) == 2:
#            continue
#        hists[sample][histname].GetXaxis().SetRangeUser( limits[0], limits[1] );
#    return hists

def applyDefaultStylesAndColors( hists ):
    defaultColors = {'data':0,
    'ttbar' : kRed + 1,
    'wjets' : kGreen - 3,
    'zjets' : kAzure - 2,
    'bce1' : kRed-7,
    'bce2' : kRed-8,
    'bce3' : kRed-9,
    'enri1' : kBlue-7,
    'enri2' : kBlue-8,
    'enri3' : kBlue-9,
    'pj1' : kYellow-7,
    'pj2' : kYellow-8,
    'pj3' : kYellow-9,
    'qcd': kYellow,
    'singleTop': kMagenta,
    'Zprime500': kTeal - 9,
    'Zprime750': kBlue - 6,
    'Zprime1000': 28,
    'Zprime1250': kCyan - 5,
    'Zprime1500': kOrange + 1, }

    for sample, histlist in hists.iteritems():
        if not sample in defaultColors.keys():
            continue
        for histname, hist in histlist.iteritems():
            hists[sample][histname].SetFillColor( defaultColors[sample] )
            if histname == 'data':
                hists[sample][histname].SetMarkerStyle( 8 )
            elif 'Zprime' in histname:
                hists[sample][histname].SetFillStyle( 0 )
                hists[sample][histname].SetLineColor( defaultColors[sample] )
            else:
                hists[sample][histname].SetFillStyle( 1001 );
                hists[sample][histname].SetFillColor( defaultColors[sample] )

    return hists

def get_cms_label( lumiInInvPb, njet = "4orMoreJets", nbjet = "0orMoreBtag", channel = "e" ):
    mytext = TPaveText( 0.5, 0.97, 1, 1.01, "NDC" )
    channelLabel = TPaveText( 0.15, 0.965, 0.4, 1.01, "NDC" )
    channelLabel.AddText(channel + ", %s, %s" % (jetBinsLatex[njet], BjetBinsLatex[nbjet] ))
    mytext.AddText( "CMS Preliminary, L = %.1f fb^{-1} at #sqrt{s} = 8 TeV" % (lumiInInvPb/1000.));
#    if njet != "":
#        mytext.AddText( channel + ", %s, %s" % (jetBinsLatex[njet], BjetBinsLatex[nbjet] ))   
             
    mytext.SetFillStyle( 0 );
    mytext.SetBorderSize( 0 );
    mytext.SetTextFont( 42 );
    mytext.SetTextAlign( 13 );
    
    channelLabel.SetFillStyle( 0 );
    channelLabel.SetBorderSize( 0 );
    channelLabel.SetTextFont( 42 );
    channelLabel.SetTextAlign( 13 );
    
    return mytext, channelLabel

def getJetBin(histname):
    for bin in allJetBins:
        if bin in histname:
            return bin
    if 'ThreeJet' in histname:
        return '3jets'
    #default
    return '4orMoreJets'

def getBjetBin(histname):
    for bin in allBjetBins:
        if bin in histname:
            return bin
    #default
    return '0orMoreBtag'

def getChannel(histname):
    if 'Muon' in histname or 'MuPlusJets' in histname:
        return '#mu'
    else:
        return 'e'
    
def normalise(histogram):
    if histogram and histogram.Integral() > 0:
        histogram.Scale(1/histogram.Integral())
    return histogram

def saveAs(canvas, name, outputFormats= ['png'], outputFolder = ''):
    canvas.RedrawAxis()
    if not outputFolder == '' and not outputFolder.endswith('/'):
        outputFolder += '/'
    for outputFormat in outputFormats:
        fullFileName = outputFolder + name + '.' + outputFormat
        if '/' in fullFileName:
            path = fullFileName[:fullFileName.rfind('/')]
            createFolderIfDoesNotExist(path)
        
        canvas.SaveAs(fullFileName)
    
def createFolderIfDoesNotExist(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
def plotHistAndFits(data, mcStack, fits):
    canvas = TCanvas( "c1", "plot with fits", 1920, 1080 )
    
    

