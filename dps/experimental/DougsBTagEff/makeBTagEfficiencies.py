from optparse import OptionParser

import ROOT 
from ROOT import gROOT, gStyle, TFile, TTree, TH1F, TH2F, TCanvas
from array import array
import math
import os
from optparse import OptionParser
from dps.utils.file_utilities import make_folder_if_not_exists

from rootpy.tree import Tree
from rootpy import asrootpy
from rootpy.io import root_open


ROOT.gROOT.SetBatch(True)
if __name__ == '__main__':
	########## 			SETUP 			##########
	gStyle.SetOptStat("")

	#################################################################################################################################
	# READ THE OPTIONS
	#################################################################################################################################
	parser = OptionParser()
	parser.add_option("-t", "--test", dest="test", action = "store_true", 
		help="Run over a few events only")
	parser.add_option("-p", "--plots", dest="make_plots", action = "store_true", 
    	help="Print out files to .png")
	parser.add_option("-o", "--only_plots", dest="only_plots", action = "store_true", 
    	help="Print out files to .png")
	(options, args) = parser.parse_args()
	if options.test : print "RUNNING OVER TEST SAMPLE"

	#################################################################################################################################
	# ADD THE GENERATOR INPUT FILES
	#################################################################################################################################
	input_files = {
		"TTJets_PowhegPythia8_tree.root" 			: "PowhegPythia8", 
		"TTJets_PowhegHerwigpp_tree.root" 			: "PowhegHerwigpp",
		"TTJets_amc_tree.root" 						: "aMCatNLOPythia8",
		"TTJets_madgraph_tree.root" 				: "Madgraph",

		"TTJets_PowhegPythia8_fsrup_tree.root" 		: "PowhegPythia8_fsrup", 
		"TTJets_PowhegPythia8_fsrdown_tree.root" 	: "PowhegPythia8_fsrdown", 
		"TTJets_PowhegPythia8_isrup_tree.root" 		: "PowhegPythia8_isrup", 
		"TTJets_PowhegPythia8_isrdown_tree.root" 	: "PowhegPythia8_isrdown", 
		"TTJets_PowhegPythia8_up_tree.root" 		: "PowhegPythia8_up", 
		"TTJets_PowhegPythia8_down_tree.root" 		: "PowhegPythia8_down", 
		"TTJets_PowhegPythia8_mtop1755_tree.root" 	: "PowhegPythia8_mtop1755", 
		"TTJets_PowhegPythia8_mtop1695_tree.root" 	: "PowhegPythia8_mtop1695", 

		# "TTJets_amcatnloHerwigpp_tree.root" : "aMCatNLOHerwigpp",
	}

	#################################################################################################################################
	# INITIALISE THE BINNING AND WEIGHTS
	#################################################################################################################################
	pt_binning = array ( 'f' , [30, 50, 70, 100, 140, 200, 300, 670] )
	eta_binning = array ( 'f', [-2.4, -2.1, -1.5, 0, 1.5, 2.1, 2.4] )
	nPtBins = len( pt_binning )	- 1
	nEtaBins = len( eta_binning ) - 1

	eWeight="EventWeight*PUWeight*ElectronEfficiencyCorrection"
	eSelection=eWeight+"*({flav}{b})"
	muWeight="EventWeight*PUWeight*MuonEfficiencyCorrection"
	muSelection=muWeight+"*({flav}{b})"

	#################################################################################################################################
	# INITIALISE THE INPUT AND OUTPUT PATHS
	#################################################################################################################################
	basepath = "/hdfs/TopQuarkGroup/ec6821/1.0.2/atOutput/combined/"
	file_path = 'dps/experimental/DougsBTagEff/BTagEfficiency.root'
	output_file = root_open(file_path, "recreate")

	#################################################################################################################################
	# RUN THE EFFICINIECY CALCULATOR
	#################################################################################################################################
	for in_file, sample in input_files.iteritems():
		print "Calculating BTag Efficiency For Generator : ",sample

		#################################################################################################################################
		# GET THE INPUT FILE AND TREES
		#################################################################################################################################
		input_file = basepath+in_file
		f = root_open(input_file, "read")
		eTree = f.Get("TTbar_plus_X_analysis/EPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets")
		muTree = f.Get("TTbar_plus_X_analysis/MuPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets")

		#################################################################################################################################
		# INITIALISE THE HISTOGRAMS
		#################################################################################################################################
		bQuarkJets_BTags_eHist = TH2F("bQuarkJets_BTags_eHist", "bQuarkJets_BTags_eHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		bQuarkJets_Total_eHist = TH2F("bQuarkJets_Total_eHist", "bQuarkJets_Total_eHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		cQuarkJets_BTags_eHist = TH2F("cQuarkJets_BTags_eHist", "cQuarkJets_Total_eHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		cQuarkJets_Total_eHist = TH2F("cQuarkJets_Total_eHist", "cQuarkJets_Total_eHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		udsgQuarkJets_BTags_eHist = TH2F("udsgQuarkJets_BTags_eHist", "udsgQuarkJets_Total_eHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		udsgQuarkJets_Total_eHist = TH2F("udsgQuarkJets_Total_eHist", "udsgQuarkJets_Total_eHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		
		bQuarkJets_BTags_muHist = TH2F("bQuarkJets_BTags_muHist", "bQuarkJets_BTags_muHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		bQuarkJets_Total_muHist = TH2F("bQuarkJets_Total_muHist", "bQuarkJets_Total_muHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		cQuarkJets_BTags_muHist = TH2F("cQuarkJets_BTags_muHist", "cQuarkJets_Total_muHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		cQuarkJets_Total_muHist = TH2F("cQuarkJets_Total_muHist", "cQuarkJets_Total_muHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		udsgQuarkJets_BTags_muHist = TH2F("udsgQuarkJets_BTags_muHist", "udsgQuarkJets_Total_muHist", nPtBins, pt_binning, nEtaBins, eta_binning)
		udsgQuarkJets_Total_muHist = TH2F("udsgQuarkJets_Total_muHist", "udsgQuarkJets_Total_muHist", nPtBins, pt_binning, nEtaBins, eta_binning)

		#################################################################################################################################
		# SET TO STORE SUM OF WEIGHTS SQ
		#################################################################################################################################
		bQuarkJets_BTags_eHist.Sumw2()
		bQuarkJets_Total_eHist.Sumw2()
		cQuarkJets_BTags_eHist.Sumw2()
		cQuarkJets_Total_eHist.Sumw2()
		udsgQuarkJets_BTags_eHist.Sumw2()
		udsgQuarkJets_Total_eHist.Sumw2()

		bQuarkJets_BTags_muHist.Sumw2()
		bQuarkJets_Total_muHist.Sumw2()
		cQuarkJets_BTags_muHist.Sumw2()
		cQuarkJets_Total_muHist.Sumw2()
		udsgQuarkJets_BTags_muHist.Sumw2()
		udsgQuarkJets_Total_muHist.Sumw2()

		#################################################################################################################################
		# FILL THE HISTOGRAMS
		#################################################################################################################################
		weight = eSelection.format(flav='hadronFlavour==5', b = '')
		weightB = eSelection.format(flav='hadronFlavour==5', b = '&&isMedium')
		eTree.Draw("pt:eta",selection=weightB, hist=bQuarkJets_BTags_eHist)
		eTree.Draw("pt:eta",selection=weight, hist=bQuarkJets_Total_eHist)
		weight = eSelection.format(flav='hadronFlavour==4', b = '')
		weightB = eSelection.format(flav='hadronFlavour==4', b = '&&isMedium')
		eTree.Draw("pt:eta",selection=weightB, hist=cQuarkJets_BTags_eHist)
		eTree.Draw("pt:eta",selection=weight, hist=cQuarkJets_Total_eHist)
		weight = eSelection.format(flav='hadronFlavour==0', b = '')
		weightB = eSelection.format(flav='hadronFlavour==0', b = '&&isMedium')
		eTree.Draw("pt:eta",selection=weightB, hist=udsgQuarkJets_BTags_eHist)
		eTree.Draw("pt:eta",selection=weight, hist=udsgQuarkJets_Total_eHist)

		weight = muSelection.format(flav='hadronFlavour==5', b = '')
		weightB = muSelection.format(flav='hadronFlavour==5', b = '&&isMedium')
		muTree.Draw("pt:eta",selection=weightB, hist=bQuarkJets_BTags_muHist)
		muTree.Draw("pt:eta",selection=weight, hist=bQuarkJets_Total_muHist)
		weight = muSelection.format(flav='hadronFlavour==4', b = '')
		weightB = muSelection.format(flav='hadronFlavour==4', b = '&&isMedium')
		muTree.Draw("pt:eta",selection=weightB, hist=cQuarkJets_BTags_muHist)
		muTree.Draw("pt:eta",selection=weight, hist=cQuarkJets_Total_muHist)
		weight = muSelection.format(flav='hadronFlavour==0', b = '')
		weightB = muSelection.format(flav='hadronFlavour==0', b = '&&isMedium')
		muTree.Draw("pt:eta",selection=weightB, hist=udsgQuarkJets_BTags_muHist)
		muTree.Draw("pt:eta",selection=weight, hist=udsgQuarkJets_Total_muHist)

		bQuarkJets_BTags_Hist = bQuarkJets_BTags_eHist.Clone("bQuarkJets_BTags_Hist")
		bQuarkJets_BTags_Hist.Add(bQuarkJets_BTags_muHist)
		bQuarkJets_Total_Hist = bQuarkJets_Total_eHist.Clone("bQuarkJets_Total_Hist")
		bQuarkJets_Total_Hist.Add(bQuarkJets_Total_muHist)
		cQuarkJets_BTags_Hist = cQuarkJets_BTags_eHist.Clone("cQuarkJets_BTags_Hist")
		cQuarkJets_BTags_Hist.Add(cQuarkJets_BTags_muHist)
		cQuarkJets_Total_Hist = cQuarkJets_Total_eHist.Clone("cQuarkJets_Total_Hist")
		cQuarkJets_Total_Hist.Add(cQuarkJets_Total_muHist)
		udsgQuarkJets_BTags_Hist = udsgQuarkJets_BTags_eHist.Clone("udsgQuarkJets_BTags_Hist")
		udsgQuarkJets_BTags_Hist.Add(udsgQuarkJets_BTags_muHist)
		udsgQuarkJets_Total_Hist = udsgQuarkJets_Total_eHist.Clone("udsgQuarkJets_Total_Hist")
		udsgQuarkJets_Total_Hist.Add(udsgQuarkJets_Total_muHist)

		#################################################################################################################################
		# FIND THE RATIO
		#################################################################################################################################
		bQuarkJets_Ratio_Hist = bQuarkJets_BTags_Hist.Clone("bQuarkJets_Ratio_Hist")
		bQuarkJets_Ratio_Hist.Divide(bQuarkJets_Ratio_Hist,bQuarkJets_Total_Hist,1,1,"B")
		cQuarkJets_Ratio_Hist = cQuarkJets_BTags_Hist.Clone("cQuarkJets_Ratio_Hist")
		cQuarkJets_Ratio_Hist.Divide(cQuarkJets_Ratio_Hist,cQuarkJets_Total_Hist,1,1,"B")
		udsgQuarkJets_Ratio_Hist = udsgQuarkJets_BTags_Hist.Clone("udsgQuarkJets_Ratio_Hist")
		udsgQuarkJets_Ratio_Hist.Divide(udsgQuarkJets_Ratio_Hist,udsgQuarkJets_Total_Hist,1,1,"B")

		#################################################################################################################################
		# WRITE EFFICIENCY TO FILE
		#################################################################################################################################
		# Directory should be here so no other histograms are associated ad written
		directory = output_file.mkdir( sample )
		directory.cd()

		bQuarkJets_Ratio_Hist.Write()
		cQuarkJets_Ratio_Hist.Write()
		udsgQuarkJets_Ratio_Hist.Write()

		f.close()

	output_file.close()

	#################################################################################################################################
	# PLOT EFFICIENCY
	#################################################################################################################################
	if options.make_plots:
		f = TFile(file_path, "OPEN")
		make_folder_if_not_exists('plots/BTagEfficiency/')
		for generator in input_files.values():
			b_Hist = f.Get(generator+"/bQuarkJets_Ratio_Hist")
			c_Hist = f.Get(generator+"/cQuarkJets_Ratio_Hist")
			udsg_Hist = f.Get(generator+"/udsgQuarkJets_Ratio_Hist")

			# Easy access to .pngs 
			b_Canvas = TCanvas("bQuarkJet","bQuarkJet", 0, 0, 800, 600)
			b_Hist.SetTitle("b quark b tagging efficiency ; pt; eta")
			b_Hist.Draw("colz")
			b_Canvas.Update()
			b_Canvas.SaveAs("plots/BTagEfficiency/bQuarkJet_"+generator+"_BTagEfficiency.png")

			c_Canvas = TCanvas("cQuarkJet","cQuarkJet", 0, 0, 800, 600)
			c_Hist.SetTitle("c quark b tagging efficiency ; pt; eta")
			c_Hist.Draw("colz")
			c_Canvas.Update()
			c_Canvas.SaveAs("plots/BTagEfficiency/cQuarkJet_"+generator+"_BTagEfficiency.png")
			
			udsg_Canvas = TCanvas("udsgQuarkJet","udsgQuarkJet", 0, 0, 800, 600)
			udsg_Hist.SetTitle("udsg quark b tagging efficiency ; pt; eta")
			udsg_Hist.Draw("colz")
			udsg_Canvas.Update()
			udsg_Canvas.SaveAs("plots/BTagEfficiency/udsgQuarkJet_"+generator+"_BTagEfficiency.png")
		f.Close()


