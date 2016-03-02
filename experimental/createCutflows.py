'''
Run this script with 2015 Data datasets to merge the cutflows from the ntuples.
'''

import ROOT 
from ROOT import gROOT, TFile, TH1F, TCanvas, TChain
import math

import os
import glob

if __name__ == '__main__':

	basepath = '/storage/db0268/TopCrossSections/AnalysisSoftware/CMSSW_7_6_3_patch2/src/tree_TTJets_PowhegPythia8_2215.18pb_PFElectron_PFMuon_PF2PATJets_MET.root'
	outpath = '../plots/CutFlows/'
	treepath = 'TTbar_plus_X_analysis/EPlusJets/Cutflow/Cutflow/'
	# if not os.path.exists(outpath): 
	# 	os.makedirs(outpath)
	Tree = "TTbar_plus_X_analysis/EPlusJets/Cutflow/Cutflow"
	Chain = TChain(Tree)
	Chain.Add(basepath)
	# e_consec = TH1F('eConsecCut', 'EPlusJets Consectutive Cutflow', 12, -0.500000, 11.500000)
	e_indiv = TH1F('eIndivCut', 'EPlusJets Individual Cutflow', 6, -0.500000, 5.500000)

	Cuts = {
	0 : "All Events",
	1 : "Trigger Selection",
	2 : "MET Selection",
	3 : "Lepton Selection",
	4 : "Jet Selection",
	5 : "Pass All",
	}

	# rootfile = TFile(basepath)
	# hist_indiv = rootfile.Get(treepath)
	for event in Chain:
		tag = event.__getattr__("Cutflow")

		for i in range (0, len(tag)):
			e_indiv.Fill(Cuts[i], tag[i])


	# rootfile.Close()


	canvas = TCanvas("CanvasRef", "CanvasTitle", 800,600)
	canvas.SetLogy()
	canvas.SetGridy()
	e_indiv.Draw("text")
	canvas.Update()
	canvas.SaveAs(outpath+e_indiv.GetTitle()+'.pdf')	
	canvas.Close()	


	# basepath = '/hdfs/TopQuarkGroup/run2/ntuples/25ns/v7/'
	# outpath = '../plots/CutFlows/'

	# # if not os.path.exists(outpath): 
	# # 	os.makedirs(outpath)

	# mu_consec = TH1F('muConsecCut', 'MuPlusJets Consectutive Cutflow', 11, -0.500000, 10.500000)
	# mu_indiv = TH1F('muIndivCut', 'MuPlusJets Individual Cutflow', 11, -0.500000, 10.500000)
	# e_consec = TH1F('eConsecCut', 'EPlusJets Consectutive Cutflow', 12, -0.500000, 11.500000)
	# e_indiv = TH1F('eIndivCut', 'EPlusJets Individual Cutflow', 12, -0.500000, 11.500000)

	# tt_mu_consec = TH1F('tt_muConsecCut', 'MC MuPlusJets Consectutive Cutflow', 11, -0.500000, 10.500000)
	# tt_mu_indiv = TH1F('tt_muIndivCut', 'MC MuPlusJets Individual Cutflow', 11, -0.500000, 10.500000)
	# tt_e_consec = TH1F('tt_eConsecCut', 'MC EPlusJets Consectutive Cutflow', 12, -0.500000, 11.500000)
	# tt_e_indiv = TH1F('tt_eIndivCut', 'MC EPlusJets Individual Cutflow', 12, -0.500000, 11.500000)

	# electron_datasets = []
	# muon_datasets = []
	# tt_datasets = []

	# muon_plots = [ mu_consec , mu_indiv , tt_mu_consec, tt_mu_indiv ]
	# electron_plots = [ e_consec , e_indiv , tt_e_consec, tt_e_indiv ]

	# for dirs in os.listdir(basepath):
	# 	if "Electron" in dirs : electron_datasets.append(dirs)
	# 	if "Muon" in dirs : muon_datasets.append(dirs)
	# 	if dirs == "TTJets_PowhegPythia8" : tt_datasets.append(dirs)

	# for dataset in muon_datasets:
	# 	datasetpath = basepath+dataset+'/'
	# 	print datasetpath	

	# 	rootfiles = []
	# 	for files in os.listdir(datasetpath):
	# 		rootfiles.append(files)

	# 	for f in rootfiles:
	# 		rootfile = datasetpath+f
	# 		if not os.path.exists(rootfile): 
	# 			print 'File Does Not exist'
	# 			break
	# 		else: print 'Adding File : ', rootfile

	# 		rootfile = TFile(rootfile)
	# 		hist_consec = rootfile.Get("topPairMuPlusJetsSelectionAnalyser/consecutiveCuts")
	# 		hist_indiv = rootfile.Get("topPairMuPlusJetsSelectionAnalyser/individualCuts")

	# 		clone_consec = hist_consec.Clone()
	# 		clone_consec.SetDirectory(0)
	# 		clone_indiv = hist_indiv.Clone()
	# 		clone_indiv.SetDirectory(0)

	# 		rootfile.Close()

	# 		mu_consec.Add(clone_consec)
	# 		mu_consec.SetDirectory(0)
	# 		mu_indiv.Add(clone_indiv)
	# 		mu_indiv.SetDirectory(0)

	# for dataset in electron_datasets:
	# 	datasetpath = basepath+dataset+'/'
	# 	print datasetpath	

	# 	rootfiles = []
	# 	for files in os.listdir(datasetpath):
	# 		rootfiles.append(files)

	# 	for f in rootfiles:
	# 		rootfile = datasetpath+f
	# 		if not os.path.exists(rootfile): 
	# 			print 'File Does Not exist'
	# 			break
	# 		else: print 'Adding File : ', rootfile

	# 		rootfile = TFile(rootfile)
	# 		hist_consec = rootfile.Get("topPairEPlusJetsSelectionAnalyser/consecutiveCuts")
	# 		hist_indiv = rootfile.Get("topPairEPlusJetsSelectionAnalyser/individualCuts")

	# 		clone_consec = hist_consec.Clone()
	# 		clone_consec.SetDirectory(0)
	# 		clone_indiv = hist_indiv.Clone()
	# 		clone_indiv.SetDirectory(0)

	# 		rootfile.Close()

	# 		e_consec.Add(clone_consec)
	# 		e_consec.SetDirectory(0)
	# 		e_indiv.Add(clone_indiv)
	# 		e_indiv.SetDirectory(0)



	# for dataset in tt_datasets:
	# 	datasetpath = basepath+dataset+'/'
	# 	print datasetpath	

	# 	rootfiles = []
	# 	for files in os.listdir(datasetpath):
	# 		rootfiles.append(files)

	# 	for f in rootfiles:
	# 		rootfile = datasetpath+f			
	# 		if not os.path.exists(rootfile): 
	# 			print 'File Does Not exist'
	# 			break
	# 		else: print 'Adding File : ', rootfile

	# 		rootfile = TFile(rootfile)

	# 		hist_consec_mu = rootfile.Get("topPairMuPlusJetsSelectionAnalyser/consecutiveCuts")
	# 		hist_indiv_mu = rootfile.Get("topPairMuPlusJetsSelectionAnalyser/individualCuts")
	# 		hist_consec_e = rootfile.Get("topPairEPlusJetsSelectionAnalyser/consecutiveCuts")
	# 		hist_indiv_e = rootfile.Get("topPairEPlusJetsSelectionAnalyser/individualCuts")

	# 		clone_consec_mu = hist_consec_mu.Clone()
	# 		clone_consec_mu.SetDirectory(0)
	# 		clone_indiv_mu = hist_indiv_mu.Clone()
	# 		clone_indiv_mu.SetDirectory(0)
	# 		clone_consec_e = hist_consec_e.Clone()
	# 		clone_consec_e.SetDirectory(0)
	# 		clone_indiv_e = hist_indiv_e.Clone()
	# 		clone_indiv_e.SetDirectory(0)

	# 		rootfile.Close()

	# 		tt_mu_consec.Add(clone_consec_mu)
	# 		tt_mu_indiv.Add(clone_indiv_mu)
	# 		tt_e_consec.Add(clone_consec_e)
	# 		tt_e_indiv.Add(clone_indiv_e)

	# for plot in muon_plots :
	# 	plot.GetXaxis().SetBinLabel(1, "Total Events");
	# 	plot.GetXaxis().SetBinLabel(2, "Event Cleaning and Trigger");
	# 	plot.GetXaxis().SetBinLabel(3, "ExactlyOneSignalMuon");
	# 	plot.GetXaxis().SetBinLabel(4, "LooseMuonVeto");
	# 	plot.GetXaxis().SetBinLabel(5, "LooseElectronVeto");
	# 	plot.GetXaxis().SetBinLabel(6, "AtLeastOneGoodJet");
	# 	plot.GetXaxis().SetBinLabel(7, "AtLeastTwoGoodJets");
	# 	plot.GetXaxis().SetBinLabel(8, "AtLeastThreeGoodJets");
	# 	plot.GetXaxis().SetBinLabel(9, "AtLeastFourGoodJets");
	# 	plot.GetXaxis().SetBinLabel(10, "AtLeastOneBTag");
	# 	plot.GetXaxis().SetBinLabel(11, "AtLeastTwoBTags");
	# 	plot.GetYaxis().SetTitle("Number of Events");

	# for plot in electron_plots :
	# 	plot.GetXaxis().SetBinLabel(1, "Total Events");
	# 	plot.GetXaxis().SetBinLabel(2, "Event Cleaning and Trigger");
	# 	plot.GetXaxis().SetBinLabel(3, "ExactlyOneSignalElectron");
	# 	plot.GetXaxis().SetBinLabel(4, "LooseMuonVeto");
	# 	plot.GetXaxis().SetBinLabel(5, "LooseElectronVeto");
	# 	plot.GetXaxis().SetBinLabel(6, "ConversionVeto");
	# 	plot.GetXaxis().SetBinLabel(7, "AtLeastOneGoodJet");
	# 	plot.GetXaxis().SetBinLabel(8, "AtLeastTwoGoodJets");
	# 	plot.GetXaxis().SetBinLabel(9, "AtLeastThreeGoodJets");
	# 	plot.GetXaxis().SetBinLabel(10, "AtLeastFourGoodJets");
	# 	plot.GetXaxis().SetBinLabel(11, "AtLeastOneBTag");
	# 	plot.GetXaxis().SetBinLabel(12, "AtLeastTwoBTags");
	# 	plot.GetYaxis().SetTitle("Number of Events");

	# for plot in electron_plots :
	# 	canvas = TCanvas("CanvasRef", "CanvasTitle", 800,600)
	# 	canvas.SetLogy()
	# 	canvas.SetGridy()
	# 	plot.Draw()
	# 	canvas.Update()
	# 	canvas.SaveAs(outpath+plot.GetTitle()+'.pdf')	
	# 	canvas.Close()	

	# for plot in muon_plots :
	# 	canvas = TCanvas("CanvasRef", "CanvasTitle", 800,600)
	# 	canvas.SetLogy()
	# 	canvas.SetGridy()
	# 	plot.Draw()
	# 	canvas.Update()
	# 	canvas.SaveAs(outpath+plot.GetTitle()+'.pdf')	
	# 	canvas.Close()	

