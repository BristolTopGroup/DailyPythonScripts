#####################################
####################################/

from ROOT import RooRealVar, RooGaussian, RooPlot, gPad, TCanvas, RooFit, kRed, \
RooArgSet, RooCBShape, RooFFTConvPdf, kDashed, RooAddPdf, RooArgList, RooDataHist, \
kBlue, RooAbsData, kFALSE, RooBreitWigner, RooVoigtian, TChain, RooMsgService

from rootpy.io import root_open
from rootpy.plotting import Hist
from rootpy.tree import Tree
from ROOT import TH1D, TH2F, gROOT, TGraphErrors, TGraph2DErrors, TGraph2D
from array import array
from math import sqrt
gROOT.SetBatch(1);
from itertools import combinations_with_replacement
from collections import OrderedDict
import os.path
from optparse import OptionParser

RooMsgService.instance().setGlobalKillBelow(RooFit.WARNING)

from copy import deepcopy

inputFileName = {
# 'data' :'/hdfs/TopQuarkGroup/run2/atOutput/13TeV/pretendData_tree.root',
# 'allMC' : '/hdfs/TopQuarkGroup/run2/atOutput/13TeV/pretendData_tree.root'

'data' :'/storage/ec6821/AnalysisTools/CMSSW_7_4_0_pre7/src/atOutput/13TeV/pretendData_tree.root',
'allMC' : '/storage/ec6821/AnalysisTools/CMSSW_7_4_0_pre7/src/atOutput/13TeV/pretendData_tree.root'
}

channels = [ 'EPlusJets', 
'MuPlusJets'
]

puBins = OrderedDict( [ 	
			('0_15' , [0,15]),
			('15_17' , [15,17]),
			('17_20' , [17,20]),
			('20_25' , [20,25]),
			('25_inf' , [25,999]),
])

etaBins = OrderedDict( [
 				('-2.5_-1.3' , [-2.5,-1.3]),
 				('-1.3_-0.8' , [-1.3,-0.8]),
 				('-0.8_0' , [-0.8,0]),
 				('0_0.8' , [0.,0.8]),
 				('0.8_1.3' , [0.8,1.3]),
 				('1.3_2.5' , [1.3,2.5]),
])

ptBins = OrderedDict([
 				('30_40' , [30,40]),
 				('40_50' , [40,50]),
 				('50_70' , [50,70]),
 				('70_100' , [70,100]),
 				('100_inf' , [100,999999999]),
])

def fitHistogram( histToFit, channel, variable='', bin='', treeSuffix ='' ) :
	# Declare variables x,mean,sigma with associated name, title, initial value and allowed range
	x = RooRealVar("M(jj)","M(jj)",40,500)

	title = channel
	if variable != '' and bin != '' :
		title = '%s_%s_%s' % (channel, variable, bin)

	histToFit = RooDataHist('histToFit', 'histToFit', RooArgList( x ), RooFit.Import( histToFit ) )
	frame = x.frame(RooFit.Title( title )) 
	histToFit.plotOn( frame )

	# Setup fit function
	fitFunction = None

	# Stuff for gauss
	mg = RooRealVar("mean","mean of gaussian",86,50,120) 
	sg = RooRealVar("sigma","width of gaussian",10,2,50) 
	gauss = RooGaussian("gauss","gaussian PDF",x,mg,sg)   

	CBmean = RooRealVar("CBmean", "CBmean",110, 5, 500)
	CBsigma = RooRealVar("CBsigma", "CBsigma",40, 20, 150)
	CBalpha = RooRealVar("CBalpha", "CBalpha", -0.5, -20., 0.)
	# CBalpha = RooRealVar("CBalpha", "CBalpha", 10, 0., 20.)
	CBn = RooRealVar("CBn", "CBn", 1., 0., 20.)
	crystalBall = RooCBShape("crystalBall","Crystal Ball resolution model", x, CBmean, CBsigma, CBalpha, CBn)

	fracGauss = RooRealVar("fracGauss", "fracGauss", 0.4, 0, 1)
	gaussPlusCrystalBall = RooAddPdf("gaussPlusCrystalBall", "Gauss plus Crystal Ball", RooArgList(gauss, crystalBall), RooArgList( fracGauss ) )
	fitFunction = gaussPlusCrystalBall

	# # Fit pdf to data
	fitFunction.fitTo(histToFit, RooFit.PrintLevel(-1))

	# Plot histogram being fitted
	histToFit.plotOn(frame)

	# Plot fit functions and components
	fitFunction.plotOn(frame, RooFit.LineColor(kRed))

	toPlot = RooArgSet(crystalBall)
	fitFunction.plotOn(frame, RooFit.Components(toPlot), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed))

	toPlot = RooArgSet(gauss)
	fitFunction.plotOn(frame, RooFit.Components(toPlot), RooFit.LineStyle(kDashed), RooFit.LineColor(kBlue))

	fitFunction.paramOn(frame,RooFit.Layout(0.55, 0.9, 0.9)) ;

	# # Draw frame on a canvas
	c = TCanvas("WMass","WMass",800,400) 
	gPad.SetLeftMargin(0.15)
	frame.GetYaxis().SetTitleOffset(1.6)
	frame.Draw() 
	gPad.Update()

	if variable == '' and bin == '':
		c.Print( 'plots/WStudies/%s%s.pdf' % ( channel, treeSuffix ) )
	elif variable != '' and bin != '':
		outputDir = 'plots/WStudies/%s%s/%s' % (channel, treeSuffix, variable)
		if not os.path.exists( outputDir ):
			os.makedirs( outputDir )
		c.Print( '%s/%s.pdf' % (outputDir, bin) )
	# raw_input('Carry on')
	# mg.Print()
	return mg

def study1DVariable( tree, variable, channel, bins, variableName = '', treeSuffix = '' ):
	# Storage for histograms and fitted m(W)
	binnedHists = {}
	binned_mw = {}

	variableLabel = variable
	if variableName:
		variableLabel = variableName

	# Loop over all bins
	for bin in bins:

		# Get bin limits
		downBinLimit = bins[bin][0]
		upBinLimit = bins[bin][1]

		# Make histogram for this bin
		binnedHists[bin] = Hist(80,40,500)
		# Work out selection
		cut = '%s >= %f && %s < %f' % ( variable, downBinLimit, variable, upBinLimit )

		# Draw histgoram
		tree.Draw('mjj', cut, hist=binnedHists[bin] )
		# Perform fit and store fitted m(W)
		binned_mw[bin] = fitHistogram( binnedHists[bin], channel, variableLabel, bin, treeSuffix = treeSuffix )
	# Return histograms and fitted m(W)
	return binnedHists, binned_mw

def study2DVariable( tree, variable, channel, bins ):
	# Storage for histograms and fitted m(W)
	binnedHists = {}
	binned_mw = {}

	# Loop over each combination of bins
	# e.g. if the possible bins are A,B, consider AA, BB, (AB || BA)
	for bin in combinations_with_replacement(bins, 2):

		# Get bin limits
		jet1_downBinLimit = bins[bin[0]][0]
		jet1_upBinLimit = bins[bin[0]][1]
		jet2_downBinLimit = bins[bin[1]][0]
		jet2_upBinLimit = bins[bin[1]][1]

		# Make label for this bin
		binLabel = bin[0]+'_'+bin[1]

		# Make histogram for this bin
		binnedHists[binLabel] = Hist(80,40,500)

		cut = ''
		# Selection if the two jets are in the same bin
		if ( bin[0] == bin[1] ) :
			jet1 = 'fabs(%s[0]) >= %f && fabs(%s[0]) < %f' % ( variable, jet1_downBinLimit, variable, jet1_upBinLimit )
			jet2 = 'fabs(%s[1]) >= %f && fabs(%s[1]) < %f' % ( variable, jet2_downBinLimit, variable, jet2_upBinLimit )
			cut = jet1 + ' && ' + jet2
		# Selection if the jets are in difference bins
		else :
			jet1 = 'fabs(%s[0]) >= %f && fabs(%s[0]) < %f' % (  variable, jet1_downBinLimit,  variable, jet1_upBinLimit )
			jet2 = 'fabs(%s[1]) >= %f && fabs(%s[1]) < %f' % (  variable, jet2_downBinLimit,  variable, jet2_upBinLimit )
			jet1_otherBin = 'fabs(%s[0]) >= %f && fabs(%s[0]) < %f' % (  variable, jet2_downBinLimit,  variable, jet2_upBinLimit )
			jet2_otherBin = 'fabs(%s[1]) >= %f && fabs(%s[1]) < %f' % (  variable, jet1_downBinLimit,  variable, jet1_upBinLimit )
			cut = '( (' + jet1 + ' && ' + jet2 + ' ) || ( '+ jet1_otherBin + ' && ' + jet2_otherBin + ' ) )'
		# Draw histogram
		tree.Draw('mjj', cut, hist=binnedHists[binLabel] )
		# Perform fit and store fitted value of m(W)
		binned_mw[binLabel] = fitHistogram( binnedHists[binLabel], channel, variable, binLabel )
	# Return histograms and fitted m(W)
	return binnedHists,binned_mw

def make1DSummaryPlot( binned_mw, bins, channel, variable, treeSuffix ) :
	nBins = len(bins)

	xValues, yValues = array('d'), array( 'd' )
	xErrors, yErrors = array('d'), array( 'd' )
	for bin in bins:
		mW = binned_mw[bin]
		lowBinEdge = bins[bin][0]
		highBinEdge = bins[bin][1]
		binWidth = ( bins[bin][1] - bins[bin][0] ) / 2
		binCentre = bins[bin][1] - binWidth
		if bin.split('_')[-1] == 'inf' :
			binCentre = lowBinEdge*1.1
			binWidth = lowBinEdge*0.1
		# print binCentre
		# print bin,bins[bin],mW.getVal(),mW.getError()
		xValues.append( binCentre )
		yValues.append( mW.getVal() )
		xErrors.append( binWidth )
		yErrors.append( mW.getError() )

	c = TCanvas( 'c1', 'A Simple Graph Example', 200, 10, 700, 500 )
	gr = TGraphErrors( nBins, xValues, yValues, xErrors, yErrors )
	gr.SetMarkerColor( 4 )
	gr.SetMarkerStyle( 3 )
	gr.GetXaxis().SetTitle( 'X title' )
	gr.GetYaxis().SetTitle( 'Y title' )
	gr.SetMinimum(75)
	gr.SetMaximum(85)
	gr.Draw( 'AP' )
	c.Update()

	outputDir = 'plots/WStudies/%s%s/%s' % (channel, treeSuffix, variable)
	c.Print( '%s/Summary.pdf' % outputDir )

	# raw_input('...')

def make2DSummaryPlot( binned_mw, bins, channel, variable, treeSuffix ) :
	nBins = len(bins)

	xValues, yValues, zValues = array('d'), array( 'd' ), array( 'd' )
	xErrors, yErrors, zErrors = array('d'), array( 'd' ), array( 'd' )

	binsForHist = array( 'd' )
	for binLimits in bins:
		for bin in bins[binLimits]:
			if bin not in binsForHist:
				if binLimits.find('inf') >= 0 and str(bin) != binLimits.split('_')[0]:
					binsForHist.append( binsForHist[-1]*1.5 )
				else:
					binsForHist.append( bin )
	
	hist = TH2F('blah','blah', len(binsForHist)-1, binsForHist, len(binsForHist)-1, binsForHist)

	for bin in combinations_with_replacement(bins, 2):
		mW = binned_mw[bin[0]+'_'+bin[1]]

		x_downBinLimit = bins[bin[0]][0]
		x_upBinLimit = bins[bin[0]][1]
		y_downBinLimit = bins[bin[1]][0]
		y_upBinLimit = bins[bin[1]][1]

		xbinWidth = ( x_upBinLimit - x_downBinLimit ) / 2
		xbinCentre = x_upBinLimit - xbinWidth
		if bin[0].split('_')[-1] == 'inf' :
			xbinCentre = x_downBinLimit*1.1
			xbinWidth = x_downBinLimit*0.1

		ybinWidth = ( y_upBinLimit - y_downBinLimit ) / 2
		ybinCentre = y_upBinLimit - ybinWidth
		if bin[1].split('_')[-1] == 'inf' :
			ybinCentre = y_downBinLimit*1.1
			ybinWidth = y_downBinLimit*0.1

		bin = hist.FindBin( xbinCentre, ybinCentre)

		hist.SetBinContent( bin, mW.getVal() )
		hist.SetBinError( bin, mW.getError() )

	# 	if xbinCentre not in xValues:
	# 		xValues.append( xbinCentre )
	# 	if ybinCentre not in yValues:
	# 		yValues.append( ybinCentre )		
	# 	zValues.append( mW.getVal() )
	# 	# xErrors.append( xbinWidth )
	# 	# yErrors.append( ybinWidth )
	# 	# zErrors.append( mW.getError() )


	c = TCanvas( 'c1', 'A Simple Graph Example', 200, 10, 700, 500 )
	# # # gr = TGraph2DErrors( nBins, xValues, yValues, zValues, xErrors, yErrors, zErrors )
	# # # gr = TGraph2D( nBins, xValues, yValues, zValues)

	hist.GetXaxis().SetTitle( 'X title' )
	hist.GetYaxis().SetTitle( 'Y title' )
	hist.SetMinimum(78)
	hist.SetMaximum(83)
	hist.Draw('COLZ TEXTE')
	c.Update()

	outputDir = 'plots/WStudies/%s%s/%s' % (channel, treeSuffix, variable)
	c.Print( '%s/Summary.pdf' % outputDir )
	# raw_input('...')

def fitWPeak( sample = 'data', JESVar = 0, allPlots = False, useAlphaCorr=False ):
	
	fittedMass = { channel : -1 for channel in channels	}
	with root_open(inputFileName[sample], 'read') as inputFile:
		for channel in channels :

			print '------ ',channel,' ------'

			treeSuffix = ''
			if JESVar == 1 :
				treeSuffix = '_JESUp'
			elif JESVar == -1 :
				treeSuffix = '_JESDown'

			if useAlphaCorr:
				treeSuffix += '_alphaCorr'

			inputTree = 'TTbar_plus_X_analysis/%s/Ref selection/W Bosons/W Bosons%s' % ( channel, treeSuffix )
			tree = inputFile.Get(inputTree);
			tree.SetBranchStatus("*", 0);
			# now enable the one we are interested in:
			tree.SetBranchStatus("mjj", 1);
			tree.SetBranchStatus("NPU", 1);
			tree.SetBranchStatus("jetEta", 1);
			tree.SetBranchStatus("jetPt", 1);

			# Loop over tree and get the distributions to fit
			histToFit_fromFile = Hist(80,40,500)

			# # Inclusive
			print '--- Inclusive'
			tree.Draw('mjj',hist=histToFit_fromFile)
			fittedMass[channel] = fitHistogram( histToFit_fromFile, '%s' % channel, treeSuffix=treeSuffix )

			if allPlots:
				# PU bins
				print '--- PU Binned'
				puBinnedHists, puBinned_mw = study1DVariable( tree, 'NPU', channel, puBins, treeSuffix=treeSuffix )
				# Make summary plot
				make1DSummaryPlot( puBinned_mw, puBins, channel, 'NPU', treeSuffix )

				# # Leading jet
				# # print '--- Leading jet pt'
				# # leadingJetPtBinned, leadingJetPtBinned_mw = study1DVariable( tree, 'max(jetPt[0],jetPt[1])', channel, ptBins, 'LeadingJetPt' )
				# # # Make summary plot
				# # make1DSummaryPlot( leadingJetPtBinned_mw, ptBins, channel, 'LeadingJetPt' )
				print '--- Leading jet eta'
				leadingJetEtaBinned, leadingJetEtaBinned_mw = study1DVariable( tree, '( (max(jetPt[0],jetPt[1]) == jetPt[0]) * jetEta[0] + (max(jetPt[0],jetPt[1]) == jetPt[1]) * jetEta[1] )', channel, etaBins, 'LeadingJetEta', treeSuffix=treeSuffix )
				# Make summary plot
				make1DSummaryPlot( leadingJetEtaBinned_mw, etaBins, channel, 'LeadingJetEta', treeSuffix )

				# # Sub leading jet
				# # print '--- Sub Leading jet pt'
				# # subleadingJetPtBinned, subleadingJetPtBinned_mw = study1DVariable( tree, 'min(jetPt[0],jetPt[1])', channel, ptBins, 'SubleadingJetPt' )
				# # # Make summary plot
				# # make1DSummaryPlot( subleadingJetPtBinned_mw, ptBins, channel, 'SubleadingJetPt' )
				print '--- Sub leading jet eta'
				subleadingJetEtaBinned, subleadingJetEtaBinned_mw = study1DVariable( tree, '( (min(jetPt[0],jetPt[1]) == jetPt[0]) * jetEta[0] + (min(jetPt[0],jetPt[1]) == jetPt[1]) * jetEta[1] )', channel, etaBins, 'SubeadingJetEta', treeSuffix=treeSuffix )
				# Make summary plot
				make1DSummaryPlot( subleadingJetEtaBinned_mw, etaBins, channel, 'SubeadingJetEta', treeSuffix )

				# # # # Eta Bins
				# print '--- Eta Binned'
				# etaBinnedHists, etaBinned_mw = study2DVariable( tree, 'jetEta', channel, etaBins )
				# make2DSummaryPlot( etaBinned_mw, etaBins, channel, 'jetEta' )

				# # # Pt Bins
				# print '--- Pt Binned'
				# ptBinnedHists, ptBinned_mw = study2DVariable( tree, 'jetPt', channel, ptBins )
				# make2DSummaryPlot( ptBinned_mw, ptBins, channel, 'jetPt' )
	return fittedMass

def getAlphaOnly():
	print 'Fitting W'
	dataResults = {}
	dataResults['central'] = fitWPeak( sample = 'data', JESVar = 0 );
	dataResults['JESUp'] = fitWPeak( sample = 'data', JESVar = 1 );
	dataResults['JESDown'] = fitWPeak( sample = 'data', JESVar = -1 );
	mcResults = {}
	mcResults['central'] = fitWPeak( sample = 'allMC', JESVar = 0 );
	mcResults['JESUp'] = fitWPeak( sample = 'allMC', JESVar = 1 );
	mcResults['JESDown'] = fitWPeak( sample = 'allMC', JESVar = -1 );

	alphaResults = { channel : {'data' : { 'central' : -1, 'JESUp' : -1, 'JESDown' : -1 },
						'mc' : { 'central' : -1, 'JESUp' : -1, 'JESDown' : -1 } } for channel in channels }

	for channel in channels:
		# Correct to this W mass
		referenceWMass = dataResults['central'][channel]
		for results in ['data','mc']:
			for variation in ['central','JESUp','JESDown']:
				print 'Variation :',variation
				result = None
				if results is 'data' : 
					print 'Correcting data'
					result = dataResults
				elif results is 'mc' :
					print 'Correcting MC'
					result = mcResults
				print 'Reference W mass : ',referenceWMass.getVal(),'+/-', referenceWMass.getError()
				print 'This W mass :',result[variation][channel].getVal(),'+/-', result[variation][channel].getError()
				alpha = referenceWMass.getVal()/result[variation][channel].getVal()
				alphaErr = alpha * sqrt( ( referenceWMass.getError() / ( referenceWMass.getVal() ) ) ** 2 + ( result[variation][channel].getError() / ( result[variation][channel].getVal() ) ) ** 2 )
				print 'Alpha : ',alpha
				print 'Alpha error : ',alphaErr
				print 'Relative alpha error : ',alphaErr/alpha*100

				alphaResults[channel][results][variation] = alpha

	print alphaResults

if __name__ == '__main__':

	parser = OptionParser()
	parser.add_option('-a',dest='getAlphaOnly', action="store_true", default=False)
	parser.add_option('-j', type='int', dest='JESVar', default = 0)
	parser.add_option('-c',dest='useAlphaCorr',action='store_true',default=False)
	parser.add_option('-s', dest='sample', default = 'data')
	(options, _) = parser.parse_args()

	if options.getAlphaOnly:
		getAlphaOnly()
	else :
	    fitWPeak( JESVar = options.JESVar, allPlots = False, useAlphaCorr=options.useAlphaCorr )
