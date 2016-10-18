from optparse import OptionParser

import ROOT 
from ROOT import gROOT, gPad, gStyle, TChain, TFile, TTree, TMath, TH1, TH1F, TH2F, TCanvas, TPad, TAxis, TLegend, TLatex, kRed, kBlue, kGreen, kMagenta
from array import array
import math
import os
from optparse import OptionParser
from dps.utils.file_utilities import make_folder_if_not_exists

ROOT.gROOT.SetBatch(True)
if __name__ == '__main__':
	########## 			SETUP 			##########
	gStyle.SetOptStat("")

	parser = OptionParser()
	parser.add_option("-t", "--test", dest="test", action = "store_true", 
		help="Run over a few events only")
	parser.add_option("-p", "--plots", dest="make_plots", action = "store_true", 
    	help="Print out files to .png")
	parser.add_option("-o", "--only_plots", dest="only_plots", action = "store_true", 
    	help="Print out files to .png")
	(options, args) = parser.parse_args()
	if options.test : print "RUNNING OVER TEST SAMPLE"

	basepath = "/hdfs/TopQuarkGroup/ec6821/0.0.10/atOutput/combined/"
	input_files = {
		0 : ["TTJets_PowhegPythia8_tree.root" , "PowhegPythia8"], 
		1 : ["TTJets_powhegHerwigpp_tree.root" , "PowhegHerwigpp"],
		2 : ["TTJets_amc_tree.root" , "aMCatNLOPythia8"],
		3 : ["TTJets_madgraph_tree.root" , "Madgraph"],
		4 : ["TTJets_PowhegPythia8_Moriond17_tree.root" , "PowhegPythia8_Moriond17"]
		# 4 : ["TTJets_amcatnloHerwigpp_tree.root" , "aMCatNLOHerwigpp"],
		}

	partonHists = [
		"bQuarkJets_Total_Hist",
		"cQuarkJets_Total_Hist",
		"udsgQuarkJets_Total_Hist"
	]

	bQuarkJets_Total_Hist = {}
	bQuarkJets_BTags_Hist = {}
	cQuarkJets_Total_Hist = {}
	cQuarkJets_BTags_Hist = {}
	udsgQuarkJets_Total_Hist = {}
	udsgQuarkJets_BTags_Hist = {}

	ratio_bQuarkJets_BTags_Hist = {}
	ratio_cQuarkJets_BTags_Hist = {}
	ratio_udsgQuarkJets_BTags_Hist = {}

	pt_binning = array ( 'f' , [30, 50, 70, 100, 140, 200, 300, 670] )
	eta_binning = array ( 'f', [-2.4, -2.1, -1.5, 0, 1.5, 2.1, 2.4] )
	nPtBins = len( pt_binning )	- 1
	nEtaBins = len( eta_binning ) - 1

	if not options.only_plots:
		out_file = TFile("BTagEfficiency.root", "RECREATE")

		for key in range (0, len(input_files)):
			in_file = input_files[key][0]
			sample = input_files[key][1]
			input_file = basepath+in_file
			if key == 4:
				input_file = "/hdfs/TopQuarkGroup/run2/atOutput/13TeV/2016/TTJets_PowhegPythia8_Moriond17_tree.root"

			print "Generator : ", sample

			directory = out_file.mkdir( sample )
			directory.cd()

			bQuarkJets_Total_Hist[sample] = TH2F("bQuarkJets_Total_Hist", "bQuarkJets_Total_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
			bQuarkJets_BTags_Hist[sample] = TH2F("bQuarkJets_BTags_Hist", "bQuarkJets_BTags_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
			cQuarkJets_Total_Hist[sample] = TH2F("cQuarkJets_Total_Hist", "cQuarkJets_Total_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
			cQuarkJets_BTags_Hist[sample] = TH2F("cQuarkJets_BTags_Hist", "cQuarkJets_BTags_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
			udsgQuarkJets_Total_Hist[sample] = TH2F("udsgQuarkJets_Total_Hist", "udsgQuarkJets_Total_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
			udsgQuarkJets_BTags_Hist[sample] = TH2F("udsgQuarkJets_BTags_Hist", "udsgQuarkJets_BTags_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)

			E_inputTree = "TTbar_plus_X_analysis/EPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
			E_Chain = TChain(E_inputTree)
			E_Chain.Add(input_file)
			Mu_inputTree = "TTbar_plus_X_analysis/MuPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
			Mu_Chain = TChain(Mu_inputTree)
			Mu_Chain.Add(input_file)
			Chain = {
			0 : E_Chain,
			1 : Mu_Chain,
			}

			########## 			FILL HISTOGRAMS 		##########

			for key, chain in Chain.iteritems():
				n=0
				if key == 0 : print "Doing Electron Channel"
				if key == 1 : print "Doing Muon Channel"
				for event in chain : 
					n=n+1
					if options.test :  
						if n == 10000 : break
						# if n == 10 : break
					NJets = event.__getattr__("NJets")
					pt = event.__getattr__("pt")
					eta = event.__getattr__("eta")
					CSV = event.__getattr__("CSV")
					hadronFlavour = event.__getattr__("hadronFlavour")
					isLoose = event.__getattr__("isLoose")
					isMedium = event.__getattr__("isMedium")
					isTight = event.__getattr__("isTight")

					eventWeight = event.__getattr__("EventWeight")
					puWeight = event.__getattr__("PUWeight")
					if key == 0 : leptonWeight = event.__getattr__("ElectronEfficiencyCorrection")
					else : leptonWeight = event.__getattr__("MuonEfficiencyCorrection")



					weight = eventWeight * puWeight * leptonWeight

					
					if (NJets <= 0): continue;

					for JetIndex in range (0,int(NJets)):
						if (pt[JetIndex] < 30): continue;
						if (abs(eta[JetIndex]) > 2.4): continue;
						# print "- "*10
						# print 'leptonweight chosen ' , leptonWeight
						# print 'electron wieght ' ,event.__getattr__("ElectronEfficiencyCorrection")
						# print 'muon weight ' ,event.__getattr__("MuonEfficiencyCorrection")
						# print "NJets ", NJets
						# print "Weight ", weight
						# print "eventWeight ", eventWeight
						# print "puWeight ", puWeight
						# print "lepWeight ", leptonWeight
						# print "HadronFlavour ", hadronFlavour[JetIndex]
						# print "is Med BTagged", isMedium[JetIndex]
						# print "Pt jet", pt[JetIndex]

						if (hadronFlavour[JetIndex] == 5):
							bQuarkJets_Total_Hist[sample].Fill(pt[JetIndex], eta[JetIndex], weight)
							if (isMedium[JetIndex] == 1):
								bQuarkJets_BTags_Hist[sample].Fill(pt[JetIndex], eta[JetIndex], weight)

						if (hadronFlavour[JetIndex] == 4):
							cQuarkJets_Total_Hist[sample].Fill(pt[JetIndex], eta[JetIndex], weight)
							if (isMedium[JetIndex] == 1):
								cQuarkJets_BTags_Hist[sample].Fill(pt[JetIndex], eta[JetIndex], weight)

						if (hadronFlavour[JetIndex] == 0):
							udsgQuarkJets_Total_Hist[sample].Fill(pt[JetIndex], eta[JetIndex], weight)
							if (isMedium[JetIndex] == 1):
								udsgQuarkJets_BTags_Hist[sample].Fill(pt[JetIndex], eta[JetIndex], weight)

			########## 			    B Quark 			##########

			bQuarkJets_BTags_Hist[sample].Sumw2()
			cQuarkJets_BTags_Hist[sample].Sumw2()
			udsgQuarkJets_BTags_Hist[sample].Sumw2()

			bQuarkJets_Total_Hist[sample].Sumw2()
			cQuarkJets_Total_Hist[sample].Sumw2()
			udsgQuarkJets_Total_Hist[sample].Sumw2()

			# Divide N by Ntot to get BTag Eff 1,1, are scalers for each hist but not used with "B" which calcs Binomial errors, updating Sumw2()
			bQuarkJets_BTags_Hist[sample].Divide(bQuarkJets_BTags_Hist[sample],bQuarkJets_Total_Hist[sample],  1, 1,  "B")
			cQuarkJets_BTags_Hist[sample].Divide(cQuarkJets_BTags_Hist[sample],cQuarkJets_Total_Hist[sample], 1, 1,   "B")
			udsgQuarkJets_BTags_Hist[sample].Divide(udsgQuarkJets_BTags_Hist[sample],udsgQuarkJets_Total_Hist[sample], 1, 1,   "B")

			bQuarkJets_BTags_Hist[sample].Write()
			cQuarkJets_BTags_Hist[sample].Write()
			udsgQuarkJets_BTags_Hist[sample].Write()
		
			ratio_bQuarkJets_BTags_Hist[sample] = bQuarkJets_BTags_Hist[sample].Clone("ratio_b_"+sample)
			ratio_cQuarkJets_BTags_Hist[sample] = cQuarkJets_BTags_Hist[sample].Clone("ratio_c_"+sample)
			ratio_udsgQuarkJets_BTags_Hist[sample] = udsgQuarkJets_BTags_Hist[sample].Clone("ratio_udsg_"+sample)
			ratio_bQuarkJets_BTags_Hist[sample].Divide( bQuarkJets_BTags_Hist["PowhegPythia8"], ratio_bQuarkJets_BTags_Hist[sample],  1, 1,  "B")
			ratio_cQuarkJets_BTags_Hist[sample].Divide( cQuarkJets_BTags_Hist["PowhegPythia8"], ratio_cQuarkJets_BTags_Hist[sample],  1, 1,  "B")
			ratio_udsgQuarkJets_BTags_Hist[sample].Divide( udsgQuarkJets_BTags_Hist["PowhegPythia8"], ratio_udsgQuarkJets_BTags_Hist[sample],  1, 1,  "B")

			ratio_bQuarkJets_BTags_Hist[sample].Write()
			ratio_cQuarkJets_BTags_Hist[sample].Write()
			ratio_udsgQuarkJets_BTags_Hist[sample].Write()

		out_file.Close()

	########## 				PLOTTING 			##########

	if options.make_plots:
		f = TFile("BTagEfficiency.root", "OPEN")
		make_folder_if_not_exists('plots/')
		for key in range (0, len(input_files)):
			generator = input_files[key][1]

			b_Hist = f.Get(generator+"/bQuarkJets_BTags_Hist")
			c_Hist = f.Get(generator+"/cQuarkJets_BTags_Hist")
			udsg_Hist = f.Get(generator+"/udsgQuarkJets_BTags_Hist")

			# Easy access to .pngs 
			b_Canvas = TCanvas("bQuarkJet","bQuarkJet", 0, 0, 800, 600)
			b_Hist.SetTitle("b quark b tagging efficiency ; pt; eta")
			b_Hist.Draw("colz")
			b_Canvas.Update()
			b_Canvas.SaveAs("plots/bQuarkJet_"+generator+"_BTagEfficiency.png")

			c_Canvas = TCanvas("cQuarkJet","cQuarkJet", 0, 0, 800, 600)
			c_Hist.SetTitle("c quark b tagging efficiency ; pt; eta")
			c_Hist.Draw("colz")
			c_Canvas.Update()
			c_Canvas.SaveAs("plots/cQuarkJet_"+generator+"_BTagEfficiency.png")
			
			udsg_Canvas = TCanvas("udsgQuarkJet","udsgQuarkJet", 0, 0, 800, 600)
			udsg_Hist.SetTitle("udsg quark b tagging efficiency ; pt; eta")
			udsg_Hist.Draw("colz")
			udsg_Canvas.Update()
			udsg_Canvas.SaveAs("plots/udsgQuarkJet_"+generator+"_BTagEfficiency.png")

		f.Close()


