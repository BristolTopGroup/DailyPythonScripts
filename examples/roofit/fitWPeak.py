#####################################
#
# 'BASIC FUNCTIONALITY' RooFit tutorial macro #101
# 
# Fitting, plotting, toy data generation on one-dimensional p.d.f
#
# pdf = gauss(x,m,s) 
#
#
# 07/2008 - Wouter Verkerke 
# 
####################################/

from ROOT import RooRealVar, RooGaussian, RooPlot, gPad, TCanvas, RooFit, kRed, \
RooArgSet, RooCBShape, RooFFTConvPdf, kDashed, RooAddPdf, RooArgList, RooDataHist, \
kBlue, RooAbsData, kFALSE, RooBreitWigner, RooVoigtian

from rootpy.io import root_open
from ROOT import TH1D, gROOT

from copy import deepcopy

# inputFile = '/storage/ec6821/DailyPythonScripts/CMSSW_7_3_0/src/DailyPythonScripts/plots/control_plots/13TeV/EPlusJets_WMass_2orMoreBtags_with_ratio.root'
# inputHistogram = 'MC'

# inputFile = '/storage/ec6821/AnalysisTools/CMSSW_7_3_0/src/atOutput/TTJet_5000pb_PFElectron_PFMuon_PF2PATJets_MET.root'
# inputHistogram = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/W Bosons/hadronicWMass_partons'

inputFile = '/storage/ec6821/AnalysisTools/CMSSW_7_3_0/src/atOutput/TTJet_5000pb_PFElectron_PFMuon_PF2PATJets_MET.root'
# inputHistogram = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/W Bosons/hadronicWMass_partonsGenJets'
# inputHistogram = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/W Bosons/hadronicWMass_genJets'
# inputHistogram = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/W Bosons/hadronicWMass_recoMatchedToPartons'
# inputHistogram = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/W Bosons/hadronicWMass_cleanedReco'
# inputHistogram = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/W Bosons/hadronicWMass'
inputHistogram = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/W Bosons/hadronicWMass_newJEC'

whatToFit = 'realLife'
# whatToFit = 'partons'
# whatToFit = 'genJetsFromPartons'


def fitWPeak():

	# Get histograms from file
	mcHist = 0
	with root_open( inputFile, 'read' ) as file:
		gROOT.cd()
		mcHist = file.Get(inputHistogram).Clone('histToFit')
		# mcHist = file.Get(inputHistogram).GetStack().Last().Clone('histToFit')

	# Data hist gone out of scope?
	print mcHist

	# Import the data to fit

	# Declare variables x,mean,sigma with associated name, title, initial value and allowed range
	x = RooRealVar("M(jj)","M(jj)",40,180)

	histToFit = RooDataHist('histToFit', 'histToFit', RooArgList( x ), RooFit.Import( mcHist ) )
	frame = x.frame(RooFit.Title("E Plus Jets")) 
	histToFit.plotOn( frame )

	# Setup fit function
	fitFunction = None
	print fitFunction
	if whatToFit == 'realLife':
		# Stuff for gauss
		mg = RooRealVar("mean","mean of gaussian",86,50,120) 
		sg = RooRealVar("sigma","width of gaussian",10,0,50) 
		gauss = RooGaussian("gauss","gaussian PDF",x,mg,sg)   

		CBmean = RooRealVar("CBmean", "CBmean",110, 60, 200)
		CBsigma = RooRealVar("CBsigma", "CBsigma",40, 20, 100)
		CBalpha = RooRealVar("CBalpha", "CBalpha", -0.5, -20., 0.)
		# CBalpha = RooRealVar("CBalpha", "CBalpha", 10, 0., 20.)
		CBn = RooRealVar("CBn", "CBn", 1., 0., 20.)
		crystalBall = RooCBShape("crystalBall","Crystal Ball resolution model", x, CBmean, CBsigma, CBalpha, CBn)

		fracGauss = RooRealVar("fracGauss", "fracGauss", 0.4, 0, 1)
		gaussPlusCrystalBall = RooAddPdf("gaussPlusCrystalBall", "Gauss plus Crystal Ball", RooArgList(gauss, crystalBall), RooArgList( fracGauss ) )
		fitFunction = gaussPlusCrystalBall
	elif whatToFit == 'partons':
		mg = RooRealVar("mean","mean of gaussian",86,50,120) 
		sg = RooRealVar("sigma","width of gaussian",10,0,50) 
		breitWigner = RooBreitWigner('bw', 'bw', x, mg, sg)
		fitFunction = breitWigner
	elif whatToFit == 'genJetsFromPartons':
		# mg = RooRealVar("mean","mean of gaussian",86,50,120) 
		# sg = RooRealVar("sigma","width of gaussian",10,0,50) 
		# breitWigner = RooBreitWigner('bw', 'bw', x, mg, sg)
		# fitFunction = breitWigner
		# mg = RooRealVar("mean","mean of gaussian",86,50,120)
		# sg = RooRealVar("sigma","width of gaussian",1,0,20)
		# width = RooRealVar("width","width of gaussian",5,0,50)
		# voigtian = RooVoigtian("voigt","voigt",x,mg,sg,width);
		# fitFunction = voigtian
		mg = RooRealVar("mean","mean of gaussian",86,50,120) 
		sg = RooRealVar("sigma","width of gaussian",10,0,50) 
		gauss = RooGaussian("gauss","gaussian PDF",x,mg,sg)
		fitFunction = gauss


	print fitFunction
	
	# # Fit pdf to data
	fitFunction.fitTo(histToFit)

	# Plot histogram being fitted
	histToFit.plotOn(frame)

	# Plot fit functions and components
	fitFunction.plotOn(frame, RooFit.LineColor(kRed))
	print 'Chi square with 7 : ',frame.chiSquare(7)
	print frame.chiSquare()
	print fitFunction.getParameters(histToFit).selectByAttrib('Constant', kFALSE).getSize()

	toPlot = RooArgSet(crystalBall)
	fitFunction.plotOn(frame, RooFit.Components(toPlot), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed))

	toPlot = RooArgSet(gauss)
	fitFunction.plotOn(frame, RooFit.Components(toPlot), RooFit.LineStyle(kDashed), RooFit.LineColor(kBlue))

	fitFunction.paramOn(frame,RooFit.Layout(0.55, 0.9, 0.9)) ;


	# Print values of mean and sigma (that now reflect fitted values and errors)
	mg.Print()
	sg.Print()
	# CBmean.Print() 
	# CBsigma.Print() 
	# CBalpha.Print() 
	# CBn.Print()
	# fracGauss.Print()

	# # Draw frame on a canvas
	c = TCanvas("WMass","WMass",800,400) 
	gPad.SetLeftMargin(0.15)
	frame.GetYaxis().SetTitleOffset(1.6)
	frame.Draw() 
	gPad.Update()
	c.Print('EPlusJets_mjj_fit.pdf')
	raw_input()
    
if __name__ == '__main__':
    fitWPeak()
