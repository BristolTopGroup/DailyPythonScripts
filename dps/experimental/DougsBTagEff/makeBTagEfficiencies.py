from optparse import OptionParser

import ROOT 
from ROOT import gPad, gROOT, gStyle, TFile, TTree, TH1F, TH2F, TCanvas, TPad, TLegend
from array import array
import math
import os
import time

from optparse import OptionParser
from dps.utils.file_utilities import make_folder_if_not_exists

from rootpy.tree import Tree
from rootpy import asrootpy
from rootpy.io import root_open
from rootpy.plotting import Hist, Legend, Canvas
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from dps.config import CMS
from dps.config.xsection import XSectionConfig
from matplotlib import rc
measurement_config = XSectionConfig( 13 )

ROOT.gROOT.SetBatch(True)
rc( 'font', **CMS.font )
# rc( 'text', usetex = False )

def main():
	########## 			SETUP 			##########
	t = time.time()
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
	parser.add_option("-d", "--debug", dest="debug", action = "store_true", 
    	help="Run debugger")
	(options, args) = parser.parse_args()
	if options.test : print "RUNNING OVER TEST SAMPLE"
	debug = options.debug

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

		"TTJets_PowhegPythia8_plusJES_tree.root" 	: "PowhegPythia8_plusJES", 
		"TTJets_PowhegPythia8_minusJES_tree.root" 	: "PowhegPythia8_minusJES", 
		"TTJets_PowhegPythia8_plusJER_tree.root" 	: "PowhegPythia8_plusJER", 
		"TTJets_PowhegPythia8_minusJER_tree.root" 	: "PowhegPythia8_minusJER", 

		# "TTJets_amcatnloHerwigpp_tree.root" : "aMCatNLOHerwigpp",
	}
	if debug:
		print "Constructed Input Files and Read Arguments"
		t = get_time(t)

	#################################################################################################################################
	# INITIALISE THE BINNING AND WEIGHTS
	#################################################################################################################################
	pt_binning = array ( 'f' , [20, 30, 50, 70, 100, 140, 200, 300, 600, 1000] )
	eta_binning = array ( 'f', [-2.4, -2.1, -1.5, 0, 1.5, 2.1, 2.4] )
	nPtBins = len( pt_binning )	- 1
	nEtaBins = len( eta_binning ) - 1

	eWeight="EventWeight*PUWeight*ElectronEfficiencyCorrection"
	eSelection=eWeight+"*({flav}{b})"
	muWeight="EventWeight*PUWeight*MuonEfficiencyCorrection"
	muSelection=muWeight+"*({flav}{b})"

	if debug:
		print "Initialised Pt and Eta binning"
		t = get_time(t)

	#################################################################################################################################
	# INITIALISE THE INPUT AND OUTPUT PATHS
	#################################################################################################################################
	basepath = "/hdfs/TopQuarkGroup/ec6821/1.0.3/atOutput/combined/"
	file_path = 'dps/experimental/DougsBTagEff/BTagEfficiency.root'

	if options.only_plots:
	 	make_eff_plots(input_files, file_path)
		# make_eff_plots(input_files, file_path, split='generator')
		# make_eff_plots(input_files, file_path, split='Shape')
		# make_eff_plots(input_files, file_path, split='Tune')
	 	return

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
		eTreeName = "TTbar_plus_X_analysis/EPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
		muTreeName = "TTbar_plus_X_analysis/MuPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"

		if "plusJES" in sample:
			eTreeName += "_JESUp"
			muTreeName += "_JESUp"
		if "minusJES" in sample:
			eTreeName += "_JESDown"
			muTreeName += "_JESDown"
		if "plusJER" in sample:
			eTreeName += "_JERUp"
			muTreeName += "_JERUp"
		if "minusJER" in sample:
			eTreeName += "_JERDown"
			muTreeName += "_JERDown"

		if debug:
			print "Opened File : {}".format(input_file)
			t = get_time(t)

		eTree = f.Get(eTreeName)
		muTree = f.Get(muTreeName)

		if debug:
			print "Retrieved E Tree : {}".format(eTreeName)
			print "Retrieved Mu Tree : {}".format(muTreeName)
			t = get_time(t)

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

		if debug:
			print "Initialised Histograms"
			t = get_time(t)

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

		if debug:
			print "Set Sum of Weight Sq"
			t = get_time(t)

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

		if debug:
			print "Draw Trees and Combined Channels"
			t = get_time(t)

		#################################################################################################################################
		# 2D Efficiencies
		#################################################################################################################################
		bQuarkJets_Ratio_Hist = bQuarkJets_BTags_Hist.Clone("bQuarkJets_Ratio_Hist")
		bQuarkJets_Ratio_Hist.Divide(bQuarkJets_Ratio_Hist,bQuarkJets_Total_Hist,1,1,"B")
		cQuarkJets_Ratio_Hist = cQuarkJets_BTags_Hist.Clone("cQuarkJets_Ratio_Hist")
		cQuarkJets_Ratio_Hist.Divide(cQuarkJets_Ratio_Hist,cQuarkJets_Total_Hist,1,1,"B")
		udsgQuarkJets_Ratio_Hist = udsgQuarkJets_BTags_Hist.Clone("udsgQuarkJets_Ratio_Hist")
		udsgQuarkJets_Ratio_Hist.Divide(udsgQuarkJets_Ratio_Hist,udsgQuarkJets_Total_Hist,1,1,"B")

		if debug:
			print "Found the 2D Efficiencies"
			t = get_time(t)

		#################################################################################################################################
		# 1D Efficiencies
		#################################################################################################################################
		bQuarkJets_BTags_Pt_Hist = bQuarkJets_BTags_Hist.ProjectionX("bQuarkJets_Btags_Pt_Hist")
		bQuarkJets_Total_Pt_Hist = bQuarkJets_Total_Hist.ProjectionX("bQuarkJets_Total_Pt_Hist")
		bQuarkJets_Ratio_Pt_Hist = bQuarkJets_BTags_Pt_Hist.Clone("bQuarkJets_Ratio_Pt_Hist")
		bQuarkJets_Ratio_Pt_Hist.Divide(bQuarkJets_Ratio_Pt_Hist,bQuarkJets_Total_Pt_Hist,1,1,"B")
		bQuarkJets_BTags_Eta_Hist = bQuarkJets_BTags_Hist.ProjectionY("bQuarkJets_Btags_Eta_Hist")
		bQuarkJets_Total_Eta_Hist = bQuarkJets_Total_Hist.ProjectionY("bQuarkJets_Total_Eta_Hist")
		bQuarkJets_Ratio_Eta_Hist = bQuarkJets_BTags_Eta_Hist.Clone("bQuarkJets_Ratio_Eta_Hist")
		bQuarkJets_Ratio_Eta_Hist.Divide(bQuarkJets_Ratio_Eta_Hist,bQuarkJets_Total_Eta_Hist,1,1,"B")

		cQuarkJets_BTags_Pt_Hist = cQuarkJets_BTags_Hist.ProjectionX("cQuarkJets_Btags_Pt_Hist")
		cQuarkJets_Total_Pt_Hist = cQuarkJets_Total_Hist.ProjectionX("cQuarkJets_Total_Pt_Hist")
		cQuarkJets_Ratio_Pt_Hist = cQuarkJets_BTags_Pt_Hist.Clone("cQuarkJets_Ratio_Pt_Hist")
		cQuarkJets_Ratio_Pt_Hist.Divide(cQuarkJets_Ratio_Pt_Hist,cQuarkJets_Total_Pt_Hist,1,1,"B")
		cQuarkJets_BTags_Eta_Hist = cQuarkJets_BTags_Hist.ProjectionY("cQuarkJets_Btags_Eta_Hist")
		cQuarkJets_Total_Eta_Hist = cQuarkJets_Total_Hist.ProjectionY("cQuarkJets_Total_Eta_Hist")
		cQuarkJets_Ratio_Eta_Hist = cQuarkJets_BTags_Eta_Hist.Clone("cQuarkJets_Ratio_Eta_Hist")
		cQuarkJets_Ratio_Eta_Hist.Divide(cQuarkJets_Ratio_Eta_Hist,cQuarkJets_Total_Eta_Hist,1,1,"B")

		udsgQuarkJets_BTags_Pt_Hist = udsgQuarkJets_BTags_Hist.ProjectionX("udsgQuarkJets_Btags_Pt_Hist")
		udsgQuarkJets_Total_Pt_Hist = udsgQuarkJets_Total_Hist.ProjectionX("udsgQuarkJets_Total_Pt_Hist")
		udsgQuarkJets_Ratio_Pt_Hist = udsgQuarkJets_BTags_Pt_Hist.Clone("udsgQuarkJets_Ratio_Pt_Hist")
		udsgQuarkJets_Ratio_Pt_Hist.Divide(udsgQuarkJets_Ratio_Pt_Hist,udsgQuarkJets_Total_Pt_Hist,1,1,"B")
		udsgQuarkJets_BTags_Eta_Hist = udsgQuarkJets_BTags_Hist.ProjectionY("udsgQuarkJets_Btags_Eta_Hist")
		udsgQuarkJets_Total_Eta_Hist = udsgQuarkJets_Total_Hist.ProjectionY("udsgQuarkJets_Total_Eta_Hist")
		udsgQuarkJets_Ratio_Eta_Hist = udsgQuarkJets_BTags_Eta_Hist.Clone("udsgQuarkJets_Ratio_Eta_Hist")
		udsgQuarkJets_Ratio_Eta_Hist.Divide(udsgQuarkJets_Ratio_Eta_Hist,udsgQuarkJets_Total_Eta_Hist,1,1,"B")

		if debug:
			print "Found the 1D Efficiencies (Projections)"
			t = get_time(t)

		#################################################################################################################################
		# WRITE EFFICIENCY TO FILE
		#################################################################################################################################
		# Directory should be here so no other histograms are associated ad written
		directory = output_file.mkdir( sample )
		directory.cd()

		bQuarkJets_Ratio_Hist.Write()
		bQuarkJets_Ratio_Pt_Hist.Write()
		bQuarkJets_Ratio_Eta_Hist.Write()
		cQuarkJets_Ratio_Hist.Write()
		cQuarkJets_Ratio_Pt_Hist.Write()
		cQuarkJets_Ratio_Eta_Hist.Write()
		udsgQuarkJets_Ratio_Hist.Write()
		udsgQuarkJets_Ratio_Pt_Hist.Write()
		udsgQuarkJets_Ratio_Eta_Hist.Write()

		if debug:
			print "Written to File"
			t = get_time(t)

		f.close()
	output_file.close()
	if debug:
		print "Output File Closed - End of Calculator"
		t = get_time(t)

	if options.make_plots:
		make_eff_plots(input_files, file_path)
	return


def make_eff_plots(input_files, file_path, split=''):
	'''
	1D and 2D efficiency plotter
	'''
	#################################################################################################################################
	# PLOT EFFICIENCY
	#################################################################################################################################
	f = TFile(file_path, "OPEN")
	make_folder_if_not_exists('plots/BTagEfficiency/')

	# #################################################################################################################################
	# # PLOT 2D EFFICIENCY
	# #################################################################################################################################
	for generator in input_files.values():
		b_Hist = f.Get(generator+"/bQuarkJets_Ratio_Hist")
		c_Hist = f.Get(generator+"/cQuarkJets_Ratio_Hist")
		udsg_Hist = f.Get(generator+"/udsgQuarkJets_Ratio_Hist")

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

	#################################################################################################################################
	# PLOT 1D EFFICIENCY
	#################################################################################################################################

	b_pt 		= {}
	b_eta 		= {}
	c_pt 		= {}
	c_eta 		= {}
	udsg_pt 	= {}
	udsg_eta 	= {}

	for generator in input_files.values():
		# Only get generators if they exist in the file
		if not f.GetListOfKeys().Contains(generator): continue

		# Split into categories
		if split == 'generator':
			if generator not in [
				'PowhegPythia8', 
				'PowhegHerwigpp', 
				'aMCatNLOPythia8', 
				'Madgraph'
				]: continue
		if split == 'Shape':
			if generator not in [
				'PowhegPythia8', 
				'PowhegPythia8_plusJES', 
				'PowhegPythia8_minusJES', 
				'PowhegPythia8_plusJER', 
				'PowhegPythia8_minusJER',  
				'PowhegPythia8_mtop1695', 
				'PowhegPythia8_mtop1755'
				]: continue
		if split == 'Tune':
			if generator not in [
				'PowhegPythia8', 
				'PowhegPythia8_fsrup', 
				'PowhegPythia8_fsrdown', 
				'PowhegPythia8_isrup', 
				'PowhegPythia8_isrdown',
				'PowhegPythia8_up', 
				'PowhegPythia8_down'
				]: continue

		b_pt[generator] 	= asrootpy( f.Get(generator+"/bQuarkJets_Ratio_Pt_Hist") )
		b_eta[generator] 	= asrootpy( f.Get(generator+"/bQuarkJets_Ratio_Eta_Hist") )
		c_pt[generator] 	= asrootpy( f.Get(generator+"/cQuarkJets_Ratio_Pt_Hist") )
		c_eta[generator] 	= asrootpy( f.Get(generator+"/cQuarkJets_Ratio_Eta_Hist") )
		udsg_pt[generator] 	= asrootpy( f.Get(generator+"/udsgQuarkJets_Ratio_Pt_Hist") )
		udsg_eta[generator] = asrootpy( f.Get(generator+"/udsgQuarkJets_Ratio_Eta_Hist") )

	eff_to_plot = {
		"b parton tagging effienciency (pt)" : b_pt,
		"b parton tagging effienciency (eta)" : b_eta,
		"c parton tagging effienciency (pt)" : c_pt,
		"c parton tagging effienciency (eta)" : c_eta,
		"udsg parton tagging effienciency (pt)" : udsg_pt,
		"udsg parton tagging effienciency (eta)" : udsg_eta,
	}

	print b_pt

	colours = [
		'red', 'blue', 'green', 'chartreuse', 'indigo', 
		'magenta', 'darkmagenta', 'hotpink', 'cyan', 'darkred', 
		'darkgoldenrod', 'mediumvioletred', 'mediumspringgreen', 
		'gold', 'darkgoldenrod', 'slategray', 'dodgerblue', 
		'cadetblue', 'darkblue', 'seagreen', 'deeppink', 'deepskyblue' 
	]

	for title, efficiencies in eff_to_plot.iteritems():

		# create figure
		fig_eff = plt.figure( figsize = ( 20, 16 ), dpi = 400, facecolor = 'white' )
		ax_eff = fig_eff.add_subplot(1, 1, 1)
		ax_eff.minorticks_on()
		ax_eff.xaxis.labelpad = 12
		ax_eff.yaxis.labelpad = 12
		ax_eff.set_ylim( 0, 1 )
		plt.tick_params( **CMS.axis_label_major )
		plt.tick_params( **CMS.axis_label_minor )

		# plot specifics
		var = 'pt'
		if 'eta' in title:
			var = 'eta'
		parton = 'b'
		if "c parton" in title: parton = 'c'
		if "udsg parton" in title: parton = 'udsg'

		ylimits=[]
		if parton == 'b':
			if var == 'pt':
				y_limits = [0.480,0.75]
			if var == 'eta':
				y_limits = [0.510,0.75]
		if parton == 'c':
			if var == 'pt':
				y_limits = [0.150,0.200]
			if var == 'eta':
				y_limits = [0.125,0.21]
		if parton == 'udsg':
			if var == 'pt':
				y_limits = [0.015,0.050]
			if var == 'eta':
				y_limits = [0.014,0.034]
		# labels
		x_title = var
		if var == 'pt':
			x_title+=' [GeV]'
		plt.xlabel( x_title, CMS.x_axis_title )
		plt.ylabel( 'Efficiency', CMS.y_axis_title)
		template = '%.1f fb$^{-1}$ (%d TeV)'
		label = template % ( measurement_config.new_luminosity/1000, measurement_config.centre_of_mass_energy)
		plt.title( label,loc='right', **CMS.title )

		# plot histograms
		i=0
		for label, h in efficiencies.iteritems():
			hist = asrootpy( h )
			h.linewidth = 4
			h.color = 'black'
			if label != 'PowhegPythia8':
				hist.linestyle = 'dashed'
				# hist.alpha = 0.8	
				hist.linewidth = 2
				h.color = colours[i]

			rplt.hist( h, stacked=False, label = label )
			i+=1

		# plot legend
		leg = plt.legend(loc='best',prop={'size':25},ncol=2)
		leg.draw_frame(False)	

		ax_eff.set_ylim( y_limits )

		# additional text 
		# logo_location = (0.05, 0.95)
		# plt.text(logo_location[0], logo_location[1], 
		# 	"CMS", 
		# 	transform=ax_eff.transAxes, 
		# 	fontsize=42,
		# 	verticalalignment='top',
		# 	horizontalalignment='left'
		# )
		# title_location = (0.05, 0.90)
		# plt.text(title_location[0], title_location[1], 
		# 	title,
		# 	transform=ax_eff.transAxes, 
		# 	fontsize=42,
		# 	verticalalignment='top',
		# 	horizontalalignment='left'
		# )

		# filename and saving
		name_template = '{parton}_{var}_{split}efficiency.pdf'
		s=''
		if split: s = split+'_' 
		name = name_template.format(
			parton=parton,
			var=var,
			split=s,
		)
		plt.tight_layout()
		fig_eff.savefig('plots/BTagEfficiency/'+name)
		fig_eff.close()

	f.Close()
	return


def get_time(t):
	'''
	How long does each step take?
	'''
	now_time = time.time()
	print "\t in {}s".format(now_time-t)
	return now_time


if __name__ == '__main__':
	main()
