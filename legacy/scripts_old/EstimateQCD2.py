from __future__ import division

import HistGetter
import HistPlotter
from tdrStyle import *
from ROOT import *
from math import pow, exp, sqrt
from copy import deepcopy
from array import array
import inputFiles

class QCDEstimator:
    luminosity = 1091.45#349.007#pb-1
    mc_luminosity = 1091.45#pb-1
    luminosity_unit = 'pb-1'
    scale = luminosity / mc_luminosity
    jetBins = ['0jet', '0orMoreJets', '1jet', '1orMoreJets', '2jets', '2orMoreJets', '3jets', '3orMoreJets', '4orMoreJets']
    jetBins = HistPlotter.allBjetBins
    jetBinsLatex = {'0jet':'0 jet', '0orMoreJets':'#geq 0 jets', '1jet':'1 jet', '1orMoreJets':'#geq 1 jet',
                    '2jets':'2 jets', '2orMoreJets':'#geq 2 jets', '3jets':'3 jets', '3orMoreJets':'#geq 3 jets',
                    '4orMoreJets':'#geq 4 jets'}
    jetBinsLatex = HistPlotter.BjetBinsLatex
    binWidth = 0.01
    rebin = 1
    fitRangesClosureTest = [ ( 0.1, 0.9 ), ( 0.1, 1.0 ), ( 0.1, 1.1 ),
                  ( 0.2, 0.9 ), ( 0.2, 1.0 ), ( 0.2, 1.1 ),
                  ( 0.3, 0.9 ), ( 0.3, 1.0 ), ( 0.3, 1.1 )]

    fitRangesEstimation = [# ( 0.1, 1.1 ), 
                           ( 0.2, 1.6 ), 
                           ( 0.3, 1.6 ),
                           ( 0.4, 1.6 )]
    signalRegion = ( 0, 0.1 )
    maxValue = 1.6
    pfIsoHistogramPrefix = 'QCDStudy/QCDest_PFIsolation_WithMETCutAndAsymJetCuts_'
    pfIsoHistogramPrefix = 'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_'
    pfIsoControlRegionHistogramPrefix = 'QCDStudy/QCDest_PFIsolation_controlRegion2_WithMETCutAndAsymJetCuts_'
    relIsoHistogramPrefix = 'QCDStudy/QCDest_CombRelIso_'
    pfIsoResults = {}
    relIsoResults = {}
    allPfIsoResults = {}
    allRelIsoResults = {}

    useEntryAsData = 'data'
    constrainFit = False
    numberOfFreeParameters = 0

    currentFitRange = ( 0.1, 1.6 )
    currentFitFuntion = 'gaus'
    currentJetBin = jetBins[-1]

    outputFormat = 'pdf'
    outputFolder = ''

    def __init__( self, files ):
        self.files = files
#        HistGetter.samplefiles = files
        self.histograms = {}
#        self.histGetter = HistGetter()
        HistPlotter.setStyle()
        self.getHistograms()
        self.applyStyleAndCreateStack()

        for bin in self.jetBins:
            self.pfIsoResults[bin] = {'actualNumberOfQCDEvents': 0, 'estimatedNumberOfQCDEvents':0,
                                      'fitFunction': None, 'fitParameters': {}, 'numberOfAllDataEvents':0,
                                      'numberOfAllMCEvents':0}
            self.relIsoResults[bin] = {'actualNumberOfQCDEvents': 0, 'estimatedNumberOfQCDEvents':0,
                                       'fitFunction': None, 'fitParameters': {}, 'numberOfAllDataEvents':0,
                                       'numberOfAllMCEvents':0}

    def getHistograms( self ):
#        relIsoHists = [self.relIsoHistogramPrefix + jetbin for jetbin in self.jetBins]
        pfIsoHists = [self.pfIsoHistogramPrefix + jetbin for jetbin in self.jetBins]
#        pfIsoControlHists = [self.pfIsoControlRegionHistogramPrefix + jetbin for jetbin in self.jetBins]
#        allHists = relIsoHists
        allHists = []
        allHists.extend( pfIsoHists )
#        allHists.extend( pfIsoControlHists )
        #print allHists
#        HistGetter.hists = allHists

        self.histograms = HistGetter.getHistsFromFiles(allHists, self.files);
        self.histograms = HistGetter.addSampleSum( self.histograms )

    def applyStyleAndCreateStack( self ):
#        self.histograms = HistPlotter.applyDefaultStylesAndColors(self.histograms)
        samplesOfInterest = ['data', 'qcd', 'zjets', 'wjets', 'singleTop', 'ttbar', 'allMC']
        colors = {'ttbar' :  kRed + 1,
                  'wjets' :  kGreen - 3,
                  'zjets' :  kAzure - 2,
                  'qcd' :  kYellow,
                  'singleTop' :  kMagenta}
#
        mcStack = {}
        for sample in samplesOfInterest:#sample
            for histname in self.histograms[sample].keys():
                self.histograms[sample][histname].Rebin( self.rebin )
                if not sample in ['data', 'allMC']:
                    self.histograms[sample][histname].Scale( self.scale )
                    self.histograms[sample][histname].SetFillStyle( 1001 )
                    self.histograms[sample][histname].SetFillColor( colors[sample] )
##                    if sample == 'ttbar':
##                        self.histograms[sample][histname].Scale( 1.15 )
                    if not mcStack.has_key( histname ):
                        mcStack[histname] = THStack( "MC_" + histname, "MC_" + histname );
                    mcStack[histname].Add( self.histograms[sample][histname] )
                if sample == 'allMC':
                    self.histograms[sample][histname].Scale( self.scale )
#                else:
#                    self.histograms[sample][histname].SetMarkerStyle( 8 );
#
#
        self.histograms['MCStack'] = mcStack
#        HistPlotter.setStyle()
        self.setStyle()
        print "=" * 40
        print "data integrated luminosity:", self.luminosity, self.luminosity_unit
        print "MC integrated luminosity:", self.mc_luminosity, self.luminosity_unit
        print "MC scale factor: ", self.scale
        print '=' * 40


    def setStyle( self ):
        tdrstyle = setTDRStyle();
        tdrstyle.SetPadRightMargin( 0.05 )#originally was 0.02, too narrow!
        tdrStyle.SetStatH( 0.2 );
        tdrStyle.SetOptStat( 0 );#off title
        tdrStyle.SetOptFit( 0 );#off title
        tdrStyle.cd();
        gROOT.ForceStyle();
        gStyle.SetTitleH( 0.1 );
        gStyle.SetStatH( 0.22 ); #0.24);
        gStyle.SetStatW( 0.22 ); #0.26);
        gStyle.SetOptStat( 1 ); #on stat
        gStyle.SetLineScalePS( 2 ); #D=3
        gStyle.SetOptFit( 112 );


    def doClosureTests( self, function = 'gaus' ):
        self.useEntryAsData = 'allMC'
        self.currentFitFuntion = function

        for fitRange in self.fitRangesClosureTest:
            self.currentFitRange = fitRange
            for bin in self.jetBins:
                self.currentJetBin = bin
                self.EstimateJetBin( bin )
                self.plot( self.pfIsoHistogramPrefix + bin, self.pfIsoResults[bin] )
#                self.plot( self.relIsoHistogramPrefix + bin, self.relIsoResults[bin] )
                self.allPfIsoResults['%1.1f-%1.1f' % fitRange] = deepcopy( self.pfIsoResults )
#                self.allRelIsoResults['%1.1f-%1.1f' % fitRange] = deepcopy( self.relIsoResults )
        self.plotClosureTest( self.pfIsoHistogramPrefix, self.allPfIsoResults )
#        self.plotClosureTest( self.relIsoHistogramPrefix, self.allRelIsoResults )


    def doEstimate( self, function = 'gaus' ):
        self.useEntryAsData = 'data'
        self.currentFitFuntion = function

        for fitRange in self.fitRangesEstimation:
            self.currentFitRange = fitRange
            for bin in self.jetBins:
                self.currentJetBin = bin
                self.EstimateJetBin( bin )
                self.plot( self.pfIsoHistogramPrefix + bin, self.pfIsoResults[bin] )
#                self.plot( self.relIsoHistogramPrefix + bin, self.relIsoResults[bin] )
                self.allPfIsoResults['%1.1f-%1.1f' % fitRange] = deepcopy( self.pfIsoResults )
#                self.allRelIsoResults['%1.1f-%1.1f' % fitRange] = deepcopy( self.relIsoResults )

    def EstimateJetBin( self, jetbin ):
#        fitRange = self.currentFitRange
        function = self.currentFitFuntion

        QCD = self.histograms['qcd']
        data = self.histograms[self.useEntryAsData]
        allMC = self.histograms['allMC']
        pfIsoHist = self.pfIsoHistogramPrefix + jetbin
        relIsoHist = self.relIsoHistogramPrefix + jetbin

        self.pfIsoResults[jetbin]['actualNumberOfQCDEvents'] = QCD[pfIsoHist].GetBinContent(1)
        self.pfIsoResults[jetbin]['numberOfAllDataEvents'] = data[pfIsoHist].GetBinContent(1)
        self.pfIsoResults[jetbin]['numberOfAllMCEvents'] = allMC[pfIsoHist].GetBinContent(1)

        pfIsoFit = self.doFit( data[pfIsoHist] )
        self.pfIsoResults[jetbin]['fitFunction'] = pfIsoFit
        self.pfIsoResults[jetbin]['fitParameters'] = self.getFitParameters( pfIsoFit )
        estimate = 0
        if pfIsoFit:
            estimate = pfIsoFit.Integral( self.signalRegion[0], self.signalRegion[1] ) / ( self.binWidth * self.rebin )

        self.pfIsoResults[jetbin]['estimatedNumberOfQCDEvents'] = estimate

#---------------------------------------------------------------------------------------------------------------------- 
#        self.relIsoResults[jetbin]['actualNumberOfQCDEvents'] = QCD[relIsoHist].GetBinContent(1)
#        self.relIsoResults[jetbin]['numberOfAllDataEvents'] = data[relIsoHist].GetBinContent(1)
#        self.relIsoResults[jetbin]['numberOfAllMCEvents'] = allMC[relIsoHist].GetBinContent(1)
#
#        relIsoFit = self.doFit( data[relIsoHist] )
#        self.relIsoResults[jetbin]['fitFunction'] = relIsoFit
#        self.relIsoResults[jetbin]['fitParameters'] = self.getFitParameters( relIsoFit )
#
#        estimate = relIsoFit.Integral( self.signalRegion[0], self.signalRegion[1] ) / ( self.binWidth * self.rebin )
#        self.relIsoResults[jetbin]['estimatedNumberOfQCDEvents'] = estimate



    def doFit( self, histogram ):
        function = self.currentFitFuntion
        fitRange = self.currentFitRange

        if not self.constrainFit:
            histogram.Fit( function, "Q0", "ah", fitRange[0], fitRange[1] )

        else:
             ff = TF1( function, function, 0, 1 );
             self.numberOfFreeParameters = ff.GetNumberFreeParameters();

        return histogram.GetFunction( function )

    def plot( self, histname, results ):
        data = self.histograms[self.useEntryAsData][histname]
        mcStack = self.histograms['MCStack'][histname]
        fitFunction = results['fitFunction']
        if not fitFunction:
            print 'no fitfunction found'
            return;

        data.GetXaxis().SetRangeUser( 0, self.maxValue - 0.01 );
        fitFunction.SetLineColor( kRed );
        fitFunction.SetLineWidth( 2 )

        fitFunction2 = fitFunction.Clone()
        fitFunction2.SetLineColor( kBlue );
        fitFunction2.SetRange( self.signalRegion[0], self.signalRegion[1] );

        fitFunction3 = fitFunction.Clone()
        fitFunction3.SetLineColor( kBlue );
        fitFunction3.SetLineStyle( kDashed );
        fitFunction3.SetRange( self.signalRegion[1], self.currentFitRange[0] );

        canvas = TCanvas( "c1", "Iso fit", 1200, 900 )
        data.Draw();

        max = 0
        if mcStack.GetMaximum() > data.GetBinContent( 1 ):
            max = mcStack.GetMaximum()*1.1
        else:
            max = data.GetBinContent( 1 ) * 1.1

        data.GetYaxis().SetRangeUser( 0, max );
        data.SetXTitle( "Relative Isolation" );
        data.SetYTitle( "Events/0.1" );
        # draw mc
        mcStack.Draw( "hist same" );
        data.Draw( "ae same" );

        fitFunction.Draw( "same" );
        fitFunction2.Draw( "same" );
        fitFunction3.Draw( "same" );

        label = self.add_cms_label( self.currentJetBin )
        label.Draw()

        legend = self.add_legend( histname )
#        legend.Draw()

        if self.currentFitFuntion == "pol1":
            out = "%s_fit_linear_from_0%.0f_%s" % ( histname, self.currentFitRange[0] * 10.0, self.useEntryAsData );
        else:
            out = "%s_fit_%s_from_%1.1f_to_%1.1f_%s" % ( histname, self.currentFitFuntion, self.currentFitRange[0],
                                            self.currentFitRange[1], self.useEntryAsData );
#        if self.outputFormat == 'pdf':
#            canvas.SaveAs( '%s.eps' % out );
#            gROOT.ProcessLine( ".!ps2pdf -dEPSCrop %s.eps" % out );
#            gROOT.ProcessLine( ".!rm -f %s.eps" % out );
#        else:
        canvas.SaveAs( '%s/%s.%s' % ( self.outputFolder, out, self.outputFormat ) )

        canvas.Close(); #crucial!
        
    def plotSpecial( self, histname, results, fitRanges ):
        data = self.histograms[self.useEntryAsData][histname]
        mcStack = self.histograms['MCStack'][histname]
        bjetBin = HistPlotter.getBjetBin(histname)
        fitStart = 0.2
        fitfunctions = []
        for fitRange in fitRanges:
            fitStart = float(fitRange[:3])
            fitFunction = results[fitRange][bjetBin]['fitFunction']
        
            if not fitFunction:
                print 'no fitfunction found'
                return;
            fitFunction.SetLineColor( kRed );
            fitFunction.SetLineWidth( 2 )

            fitFunction2 = fitFunction.Clone()
            fitFunction2.SetLineColor( kBlue );
            fitFunction2.SetRange( self.signalRegion[0], self.signalRegion[1] );

            fitFunction3 = fitFunction.Clone()
            fitFunction3.SetLineColor( kBlue );
            fitFunction3.SetLineStyle( kDashed );
            fitFunction3.SetRange( self.signalRegion[1], fitStart );
            fitfunctions.append(fitFunction)
            fitfunctions.append(fitFunction2)
            fitfunctions.append(fitFunction3)

        data.GetXaxis().SetRangeUser( 0, self.maxValue - 0.01 );

        canvas = TCanvas( "c1", "Iso fit", 1200, 900 )
        data.Draw();

        max = 0
        if mcStack.GetMaximum() > data.GetBinContent( 1 ):
            max = mcStack.GetMaximum()*1.1
        else:
            max = data.GetBinContent( 1 ) * 1.1

        data.GetYaxis().SetRangeUser( 0, max );
        data.SetXTitle( "Relative Isolation" );
        data.SetYTitle( "Events/0.1" );
        # draw mc
        mcStack.Draw( "hist same" );
        data.Draw( "ae same" );
#        data.GetYaxis().Draw('same')
        
        for fitFunction in fitfunctions:
            fitFunction.Draw( "same" );
        
        label = self.add_cms_label( bjetBin )
        label.Draw()

        legend = self.add_legend( histname )
#        legend.Draw()

        if self.currentFitFuntion == "pol1":
            out = "%s_fit_linear_%s" % ( histname, self.useEntryAsData );
        else:
            out = "%s_fit_%s_%s" % ( histname, self.currentFitFuntion, self.useEntryAsData );
#        if self.outputFormat == 'pdf':
#            canvas.SaveAs( '%s.eps' % out );
#            gROOT.ProcessLine( ".!ps2pdf -dEPSCrop %s.eps" % out );
#            gROOT.ProcessLine( ".!rm -f %s.eps" % out );
#        else:
        
        HistPlotter.saveAs(canvas, '%s/%s' % (self.outputFolder, out), ['png', 'pdf'] )
#        canvas.SaveAs( '%s/%s.%s' % ( self.outputFolder, out, self.outputFormat ) )

        canvas.Close(); #crucial!


    def plotClosureTest( self, histname, results ):
        c2 = TCanvas( "c2", "QCD estimates", 1080, 1080 );
        x = array( 'd', [1, 2, 3] )
#        jetBinsOfInterest = [#'1jet', 
#                             '2jets', '3jets', '4orMoreJets']
        
        jetBinsOfInterest = HistPlotter.exclusiveBjetBins
        function = self.currentFitFuntion

        gStyle.SetMarkerSize( 1.7 );
        gStyle.SetMarkerStyle( 20 );
        c2.SetTopMargin( 0.1 );
        c2.SetLeftMargin( 0.12 );
        c2.SetRightMargin( 0.35 );

        y = {}
        for fitRange in self.fitRangesClosureTest:
            range = '%1.1f-%1.1f' % fitRange
            y[range] = []
            for bin in jetBinsOfInterest:

                est = results[range][bin]['estimatedNumberOfQCDEvents']
                true = results[range][bin]['actualNumberOfQCDEvents']
                variation = 0
                if not true == 0:
                    variation = ( est - true ) / true
                y[range].append( variation )
#                if bin == '1btag':
#                    print bin, fitRange
#                    print est, true, variation
        nbins = 3
        gr1 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[0]] ) )
        gr2 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[1]] ) )
        gr3 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[2]] ) )
        gr4 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[3]] ) )
        gr5 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[4]] ) )
        gr6 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[5]] ) )
        gr7 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[6]] ) )
        gr8 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[7]] ) )
        gr9 = TGraph( nbins, x, array( 'd', y['%1.1f-%1.1f' % self.fitRangesClosureTest[8]] ) )

        gr1.SetMarkerColor( kGreen + 1 );
        gr2.SetMarkerColor( kGreen + 2 );
        gr3.SetMarkerColor( kGreen + 3 );
        gr4.SetMarkerColor( kAzure + 7 );
        gr5.SetMarkerColor( kAzure - 3 );
        gr6.SetMarkerColor( kBlue );
        gr7.SetMarkerColor( kOrange );
        gr8.SetMarkerColor( kOrange - 1 );
        gr9.SetMarkerColor( kOrange - 6 );

        gStyle.SetTitleW( 0.9 );
        gStyle.SetTitleH( 0.05 )

        h = None
        if function == "gaus":
            h = TH1D( "h", "Variation of QCD estimates with fit range (Gaussian)", 4, 0.5, 4.5 );
        elif function == "pol3":
            h = TH1D( "h", "Variation of QCD estimates with fit range (Pol3)", 4, 0.5, 4.5 );
        elif function == "pol1":
            h = TH1D( "h", "Variation of QCD estimates with fit range (Pol1)", 4, 0.5, 4.5 );
        elif function == "landau":
            h = TH1D( "h", "Variation of QCD estimates with fit range (Landau)", 4, 0.5, 4.5 );

        h.SetStats( kFALSE ); # no statistics
        h.Draw();
        h.SetYTitle( "Deviation = (N_{QCD,est}-N_{QCD,true})/N_{QCD,true}" );
        h.GetYaxis().SetRangeUser( -1, 1 );
        h.GetXaxis().SetRangeUser( 0.5, 2.5 );
        h.GetXaxis().SetBinLabel( 1, "0btags" );
        h.GetXaxis().SetBinLabel( 2, "1btags" );
        h.GetXaxis().SetBinLabel( 3, "2btags" );
#        h.GetXaxis().SetBinLabel( 4, "3btags" );
        h.GetXaxis().SetLabelSize( 0.07 );
        h.GetYaxis().SetTitleOffset( 1.3 );

        gr1.Draw( "P" );
        gr2.Draw( "P" ); #to superimpose graphs, do not re-draw axis
        gr3.Draw( "P" );
        gr4.Draw( "P" );
        gr5.Draw( "P" );
        gr6.Draw( "P" );
        gr7.Draw( "P" );
        gr8.Draw( "P" );
        gr9.Draw( "P" );

        c2.SetGrid( 1, 1 );

        leg = TLegend( 0.65, 0.1, 0.98, 0.9 );
        leg.SetFillColor( 0 );
        leg.AddEntry( gr1, "Free: 0.1-0.9", "p" );
        leg.AddEntry( gr2, "Free: 0.1-1.0", "p" );
        leg.AddEntry( gr3, "Free: 0.1-1.1", "p" );
        leg.AddEntry( gr4, "Free: 0.2-0.9", "p" );
        leg.AddEntry( gr5, "Free: 0.2-1.0", "p" );
        leg.AddEntry( gr6, "Free: 0.2-1.1", "p" );
        leg.AddEntry( gr7, "Free: 0.3-0.9", "p" );
        leg.AddEntry( gr8, "Free: 0.3-1.0", "p" );
        leg.AddEntry( gr9, "Free: 0.3-1.1", "p" );

        leg.Draw();

        c2.SaveAs( "%s/%s_qcd_estimate_%s.%s" % ( self.outputFolder, histname, function, self.outputFormat ) )

        setRange = h.GetYaxis().SetRangeUser
        saveAs = c2.SaveAs
        for limit in [1, 2, 3, 6, 8]:
            setRange( -limit, limit );
            saveAs( "%s/%s_qcd_estimate_%s_zoom_%d.%s" % ( self.outputFolder, histname, function, limit, self.outputFormat ) );

    def getFitParameters( self, fitFunction ):
        fitParameters = {'chi2':-1, 'numberOfdegreesOfFreedom': 0, 'constrain1': 0, 'constrain2': 0,
                         'constrain3': 0, 'constrain4': 0}
        if fitFunction:
            fitParameters['chi2'] = fitFunction.GetChisquare()
            fitParameters['numberOfdegreesOfFreedom'] = fitFunction.GetNDF()
        return fitParameters

    def doConstrainedFit( self, histogram, function = 'gaus', limits = ( 0.1, 1.6 ) ):
        fitFunction = None
        if function == 'gaus':
            fitFunction = TF1( "gaus", "gaus", 0, 2 );
        elif function == 'pol3':
            fitFunction = TF1( "pol3", "[0] * ( 1 + [1]*x + [2]*x^2 + [3]*x^3 )", 0, 2 );
        elif function == 'landau':
            fitFunction = TF1( "landau", "landau", 0, 2 )


        myFitResult = data.Fit( function, "Q0", "ah", limits[0], limits[1] );

    def add_cms_label( self, njet = "" ):

        mytext = TPaveText( 0.3, 0.8, 0.6, 0.93, "NDC" );
        mytext.AddText( "CMS Preliminary" );
        mytext.AddText( "%.1f pb^{-1} at  #sqrt{s} = 7 TeV" % self.luminosity );
        if njet != "":
            mytext.AddText( "e+jets, %s" % self.jetBinsLatex[njet] )
        mytext.SetFillStyle( 0 );
        mytext.SetBorderSize( 0 );
        mytext.SetTextFont( 42 );
        mytext.SetTextAlign( 13 );
        return mytext

    def add_legend( self, histname ):
        function = self.currentFitFuntion

        tt = self.histograms['ttbar'][histname]
        wj = self.histograms['wjets'][histname]
        zj = self.histograms['zjets'][histname]
        data = self.histograms['data'][histname]
        QCD = self.histograms['qcd'][histname]
        stop = self.histograms['singleTop'][histname]

        leg = TLegend( 0.64, 0.4, 0.9, 0.9 );
        leg.SetFillStyle( 0 );
        leg.SetBorderSize( 0 );
        leg.SetTextFont( 42 );

        # Here I define coloured lines for use in the legend
        blue = TF1( "blue", "pol0", 0, 1 );
        red = TF1( "red", "pol0", 0, 1 );

        blue.SetLineColor( kBlue );
        red.SetLineColor( kRed );

        red.SetLineWidth( 2 );
        blue.SetLineWidth( 2 );

        blue.SetLineStyle( kDashed );

        # Add entry to legend
        if self.useEntryAsData == 'data':
            leg.AddEntry( data, "Data", "LP" );
        else:
            leg.AddEntry( data, "All MC events", "LP" );
        if function == "pol1":
            leg.AddEntry( red, "Linear Fit", "l" );
        elif function == "expo":
            leg.AddEntry( red, "Exponenetial Fit", "l" );
        elif function == "gaus":
            leg.AddEntry( red, "Gaussian Fit", "l" );

        leg.AddEntry( blue, "Extrapolation", "l" );
        leg.AddEntry( tt, "t#bar{t}", "F" );
        leg.AddEntry( stop, "Single-Top", "F" );
        leg.AddEntry( wj, "W#rightarrowl#nu", "F" );
        leg.AddEntry( zj, "Z/#gamma*#rightarrowl^{+}l^{-}", "F" );
        leg.AddEntry( QCD, "QCD & #gamma+jets", "F" );
        leg.Draw()
        return ( leg, red, blue )

    def printResults( self, results ):
        self.printJetBinResults( results, '0btag' )
        print '=' * 60
        self.printJetBinResults( results, '1btag' )
        print '=' * 60
        self.printJetBinResults( results, '2btags' )
        print '=' * 60
        self.printJetBinResults( results, '3btags' )
        print '=' * 60
        
        self.printJetBinResults( results, '0orMoreBtag' )
        print '=' * 60
        self.printJetBinResults( results, '1orMoreBtag' )
        print '=' * 60
        self.printJetBinResults( results, '2orMoreBtags' )
        print '=' * 60
        self.printJetBinResults( results, '3orMoreBtags' )
        print '=' * 60
        self.printJetBinResults( results, '4orMoreBtags' )
        print '=' * 60
        
    def printTwikiTable(self, results):
        
        summary = self.getSummeryOfAllResults(results)
        
        estimates = (summary['0btag'][0], summary['0btag'][1], 
                     summary['1btag'][0], summary['1btag'][1],
                     summary['2btags'][0], summary['2btags'][1],
                     summary['3btags'][0], summary['3btags'][1],
                     summary['4orMoreBtags'][0], summary['4orMoreBtags'][1])
        predictions = (summary['0btag'][2], 
                       summary['1btag'][2],
                       summary['2btags'][2],
                       summary['3btags'][2],
                       summary['4orMoreBtags'][2])
        print '| * * | *0 b-tag* | *1 b-tag* | *2 b-tags* | *3 b-tags* | *4 b-tags* |'
        print '| estimate | %.2f +- %.2f | %.2f +- %.2f | %.2f +- %.2f | %.2f +- %.2f | %.2f +- %.2f|' %estimates
        print '| expected | %.2f | %.2f | %.2f | %.2f | %.2f |' % predictions
        
        
        estimates = (summary['0orMoreBtag'][0], summary['0orMoreBtag'][1], 
                     summary['1orMoreBtag'][0], summary['1orMoreBtag'][1],
                     summary['2orMoreBtags'][0], summary['2orMoreBtags'][1],
                     summary['3orMoreBtags'][0], summary['3orMoreBtags'][1],
                     summary['4orMoreBtags'][0], summary['4orMoreBtags'][1])
        predictions = (summary['0orMoreBtag'][2], 
                       summary['1orMoreBtag'][2],
                       summary['2orMoreBtags'][2],
                       summary['3orMoreBtags'][2],
                       summary['4orMoreBtags'][2])
        print '| * * | *>=0 b-tag* | *>= 1 b-tag* | *>=2 b-tags* | *>=3 b-tags* | *>=4 b-tags* |'
        print '| estimate | %.2f +- %.2f | %.2f +- %.2f | %.2f +- %.2f | %.2f +- %.2f | %.2f +- %.2f|' %estimates
        print '| expected | %.2f | %.2f | %.2f | %.2f | %.2f |' % predictions


    def getSummeryOfAllResults(self, results):
        summary = {}
        summary['0btag'] = self.getSummaryOfResult(results, '0btag')
        summary['1btag'] = self.getSummaryOfResult(results, '1btag')
        summary['2btags'] = self.getSummaryOfResult(results, '2btags')
        summary['3btags'] = self.getSummaryOfResult(results, '3btags')
        
        summary['0orMoreBtag'] = self.getSummaryOfResult(results, '0orMoreBtag')
        summary['1orMoreBtag'] = self.getSummaryOfResult(results, '1orMoreBtag')
        summary['2orMoreBtags'] = self.getSummaryOfResult(results, '2orMoreBtags')
        summary['3orMoreBtags'] = self.getSummaryOfResult(results, '3orMoreBtags')
        summary['4orMoreBtags'] = self.getSummaryOfResult(results, '4orMoreBtags')
        return summary
        
    def getSummaryOfResult(self, results, bin):
        estimate = 0
        estimate2 = 0
        predicted = results[results.keys()[0]][bin]['actualNumberOfQCDEvents']
        allData = results[results.keys()[0]][bin]['numberOfAllDataEvents']
        allMC = results[results.keys()[0]][bin]['numberOfAllMCEvents']

        for fitRange in self.fitRangesEstimation:
            range = '%1.1f-%1.1f' % fitRange
            est = results[range][bin]['estimatedNumberOfQCDEvents']
            true = results[range][bin]['actualNumberOfQCDEvents']
            variation = est
            if not true == 0:
                variation = ( est - true ) / true
            estimate += est
            estimate2 += est * est

        mean = estimate / len( self.fitRangesEstimation )
        mean2 = estimate2 / len( self.fitRangesEstimation )
        error = sqrt( ( mean2 - mean * mean ) / len( self.fitRangesEstimation ) )
        weight = 0
        if not predicted == 0:
            weight = estimate / len( self.fitRangesEstimation ) / predicted
        
        return (mean, error, predicted)
        
    def printJetBinResults( self, results, jetBin ):
        estimate = 0
        estimate2 = 0
        predicted = results[results.keys()[0]][jetBin]['actualNumberOfQCDEvents']
        allData = results[results.keys()[0]][jetBin]['numberOfAllDataEvents']
        allMC = results[results.keys()[0]][jetBin]['numberOfAllMCEvents']
        print jetBin
        if jetBin == '4orMoreJets':
            print 'Estimation for >= 4 jets'
        elif jetBin == '3orMoreJets':
            print 'Estimation for >= 3 jets'
        elif jetBin == '3jets':
            print 'Estimation for == 3 jets'
        print 'predicted number of QCD events', predicted
        for fitRange in self.fitRangesEstimation:
            range = '%1.1f-%1.1f' % fitRange
            est = results[range][jetBin]['estimatedNumberOfQCDEvents']
            true = results[range][jetBin]['actualNumberOfQCDEvents']
            variation = est
            if not true == 0:
                variation = ( est - true ) / true
            estimate += est
            estimate2 += est * est


            print
            print 'estimated number of QCD events'
            print 'for range', range, ': ',
            print est
        print
        mean = estimate / len( self.fitRangesEstimation )
        mean2 = estimate2 / len( self.fitRangesEstimation )
        error = sqrt( ( mean2 - mean * mean ) / len( self.fitRangesEstimation ) )
        print 'average estimate', mean, '+-', error
        weight = 0
        if not predicted == 0:
            weight = estimate / len( self.fitRangesEstimation ) / predicted
        print 'average weight factor', weight
        print 'Total number of data in signal bin(<0.1)', allData
        print 'Total number of MC in signal bin(<0.1) before reweighting QCD', allMC
        print 'Total number of MC in signal bin(<0.1) after reweighting QCD', ( allMC - predicted ) + predicted * weight

    def plotControlRegionComparison( self ):
        for bin in self.jetBins:
            hist = self.pfIsoHistogramPrefix + bin
            histControl = self.pfIsoControlRegionHistogramPrefix + bin
            QCD_control = self.histograms['qcd'][histControl]
            QCD = self.histograms['qcd'][hist]
            nQCD_Control = QCD_control.Integral()
            nQCD = QCD.Integral()
            if nQCD_Control > 0:
                QCD_control.Scale( 1 / nQCD_Control )
            if nQCD > 0:
                QCD.Scale( 1 / nQCD )
            QCD_control.SetFillStyle( 3004 )
            QCD.GetXaxis().SetRangeUser( 0., self.maxValue - 0.01 )

            max = 0
            if QCD.GetMaximum() > QCD_control.GetMaximum():
                max = QCD.GetMaximum()*1.1
            else:
                max = QCD_control.GetMaximum()*1.1

            QCD.GetYaxis().SetRangeUser( 0., max )

            canvas = TCanvas( "c1", "Shape comparision", 1200, 900 )
            QCD.Draw()
            QCD_control.Draw( 'same' )
            label = self.add_cms_label( bin )
            label.Draw()

            leg = TLegend( 0.64, 0.4, 0.9, 0.9 );
            leg.SetFillStyle( 0 );
            leg.SetBorderSize( 0 );
            leg.SetTextFont( 42 );
            leg.AddEntry( QCD_control, 'QCD control region' )
            leg.AddEntry( QCD, 'QCD standard selection' )
            leg.Draw()

            canvas.SaveAs( '%s/%s_shapeComparison.%s' % ( self.outputFolder, hist, self.outputFormat ) )


if __name__ == '__main__':
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = 3001;' )

    path = '/storage/results/2011/'
    
    q = QCDEstimator( inputFiles.files )
    QCDEstimator.outputFolder = '/storage/results/plots/ElectronHad/'
    QCDEstimator.outputFormat = 'png'
    function = 'expo'

    q.doEstimate( function )
    print '=' * 60
    print 'ParticleFlowIsolation results'
    q.printTwikiTable(q.allPfIsoResults)
#    q.printResults( q.allPfIsoResults )
    fitRanges = ['0.2-1.6','0.3-1.6','0.4-1.6']
    q.plotSpecial('QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_0btag', q.allPfIsoResults, fitRanges)
    q.plotSpecial('QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_1btag', q.allPfIsoResults, fitRanges)
    q.plotSpecial('QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_2btags', q.allPfIsoResults, fitRanges)
#    q.plot('QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_3orMoreBtags', q.allPfIsoResults['0.2-1.1']['3orMoreBtags'])
    #q.pfIsoHistogramPrefix = 'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts'
#    print 'Relative isolation results'
#    q.printResults( q.allRelIsoResults )
#    print '=' * 60


#    print 'Starting closure tests'
    q.doClosureTests( function)
#    q.plotControlRegionComparison()

