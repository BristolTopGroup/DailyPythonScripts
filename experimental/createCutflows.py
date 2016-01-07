'''
Run this script with 2015 Data datasets to merge the cutflows from the ntuples.
'''

import ROOT 
from ROOT import gROOT, TFile, TH1F, TCanvas
import math

import os
import glob

if __name__ == '__main__':

	basepath = '/hdfs/TopQuarkGroup/run2/ntuples/25ns/v6/'
	outpath = '/plots/CutFlows/'
	if not os.path.exists(outpath):
		os.makedirs(outpath)



	mu_consec = TH1F('muConsecCut', 'MuPlusJets Consectutive Cutflow', 11, -0.500000, 10.500000)
	mu_indiv = TH1F('muIndivCut', 'MuPlusJets Individual Cutflow', 11, -0.500000, 10.500000)
	e_consec = TH1F('eConsecCut', 'EPlusJets Consectutive Cutflow', 12, -0.500000, 11.500000)
	e_indiv = TH1F('eIndivCut', 'EPlusJets Individual Cutflow', 12, -0.500000, 11.500000)

	electron_datasets = []
	muon_datasets = []
	for dirs in os.listdir(basepath):
		if "Electron" in dirs : electron_datasets.append(dirs)
		if "Muon" in dirs : muon_datasets.append(dirs)

	for dataset in muon_datasets:
		datasetpath = basepath+dataset+'/'
		print datasetpath	

		rootfiles = []
		for files in os.listdir(datasetpath):
			rootfiles.append(files)

		for f in rootfiles:
			rootfile = datasetpath+f
			if not os.path.exists(rootfile): 
				print 'File Does Not exist'
				break
			else: print 'Adding File : ', rootfile

			rootfile = TFile(rootfile)
			hist_consec = rootfile.Get("topPairMuPlusJetsSelectionAnalyser/consecutiveCuts")
			hist_indiv = rootfile.Get("topPairMuPlusJetsSelectionAnalyser/individualCuts")

			clone_consec = hist_consec.Clone()
			clone_consec.SetDirectory(0)
			clone_indiv = hist_indiv.Clone()
			clone_indiv.SetDirectory(0)

			rootfile.Close()

			mu_consec.Add(clone_consec)
			mu_consec.SetDirectory(0)
			mu_indiv.Add(clone_indiv)
			mu_indiv.SetDirectory(0)

	for dataset in electron_datasets:
		datasetpath = basepath+dataset+'/'
		print datasetpath	

		rootfiles = []
		for files in os.listdir(datasetpath):
			rootfiles.append(files)

		for f in rootfiles:
			rootfile = datasetpath+f
			if not os.path.exists(rootfile): 
				print 'File Does Not exist'
				break
			else: print 'Adding File : ', rootfile

			rootfile = TFile(rootfile)
			hist_consec = rootfile.Get("topPairEPlusJetsSelectionAnalyser/consecutiveCuts")
			hist_indiv = rootfile.Get("topPairEPlusJetsSelectionAnalyser/individualCuts")

			clone_consec = hist_consec.Clone()
			clone_consec.SetDirectory(0)
			clone_indiv = hist_indiv.Clone()
			clone_indiv.SetDirectory(0)

			rootfile.Close()

			e_consec.Add(clone_consec)
			e_consec.SetDirectory(0)
			e_indiv.Add(clone_indiv)
			e_indiv.SetDirectory(0)



	mu_consec.GetXaxis().SetBinLabel(1, "Total Events");
	mu_consec.GetXaxis().SetBinLabel(2, "Event Cleaning and Trigger");
	mu_consec.GetXaxis().SetBinLabel(3, "ExactlyOneSignalMuon");
	mu_consec.GetXaxis().SetBinLabel(4, "LooseMuonVeto");
	mu_consec.GetXaxis().SetBinLabel(5, "LooseElectronVeto");
	mu_consec.GetXaxis().SetBinLabel(6, "AtLeastOneGoodJet");
	mu_consec.GetXaxis().SetBinLabel(7, "AtLeastTwoGoodJets");
	mu_consec.GetXaxis().SetBinLabel(8, "AtLeastThreeGoodJets");
	mu_consec.GetXaxis().SetBinLabel(9, "AtLeastFourGoodJets");
	mu_consec.GetXaxis().SetBinLabel(10, "AtLeastOneBTag");
	mu_consec.GetXaxis().SetBinLabel(11, "AtLeastTwoBTags");
	mu_consec.GetYaxis().SetTitle("Number of Events");

	e_consec.GetXaxis().SetBinLabel(1, "Total Events");
	e_consec.GetXaxis().SetBinLabel(2, "Event Cleaning and Trigger");
	e_consec.GetXaxis().SetBinLabel(3, "ExactlyOneSignalElectron");
	e_consec.GetXaxis().SetBinLabel(4, "LooseMuonVeto");
	e_consec.GetXaxis().SetBinLabel(5, "LooseElectronVeto");
	e_consec.GetXaxis().SetBinLabel(6, "ConversionVeto");
	e_consec.GetXaxis().SetBinLabel(7, "AtLeastOneGoodJet");
	e_consec.GetXaxis().SetBinLabel(8, "AtLeastTwoGoodJets");
	e_consec.GetXaxis().SetBinLabel(9, "AtLeastThreeGoodJets");
	e_consec.GetXaxis().SetBinLabel(10, "AtLeastFourGoodJets");
	e_consec.GetXaxis().SetBinLabel(11, "AtLeastOneBTag");
	e_consec.GetXaxis().SetBinLabel(12, "AtLeastTwoBTags");
	e_consec.GetYaxis().SetTitle("Number of Events");

	mu_indiv.GetXaxis().SetBinLabel(1, "Total Events");
	mu_indiv.GetXaxis().SetBinLabel(2, "Event Cleaning and Trigger");
	mu_indiv.GetXaxis().SetBinLabel(3, "ExactlyOneSignalMuon");
	mu_indiv.GetXaxis().SetBinLabel(4, "LooseMuonVeto");
	mu_indiv.GetXaxis().SetBinLabel(5, "LooseElectronVeto");
	mu_indiv.GetXaxis().SetBinLabel(6, "AtLeastOneGoodJet");
	mu_indiv.GetXaxis().SetBinLabel(7, "AtLeastTwoGoodJets");
	mu_indiv.GetXaxis().SetBinLabel(8, "AtLeastThreeGoodJets");
	mu_indiv.GetXaxis().SetBinLabel(9, "AtLeastFourGoodJets");
	mu_indiv.GetXaxis().SetBinLabel(10, "AtLeastOneBTag");
	mu_indiv.GetXaxis().SetBinLabel(11, "AtLeastTwoBTags");
	mu_indiv.GetYaxis().SetTitle("Number of Events");

	e_indiv.GetXaxis().SetBinLabel(1, "Total Events");
	e_indiv.GetXaxis().SetBinLabel(2, "Event Cleaning and Trigger");
	e_indiv.GetXaxis().SetBinLabel(3, "ExactlyOneSignalElectron");
	e_indiv.GetXaxis().SetBinLabel(4, "LooseMuonVeto");
	e_indiv.GetXaxis().SetBinLabel(5, "LooseElectronVeto");
	e_indiv.GetXaxis().SetBinLabel(6, "ConversionVeto");
	e_indiv.GetXaxis().SetBinLabel(7, "AtLeastOneGoodJet");
	e_indiv.GetXaxis().SetBinLabel(8, "AtLeastTwoGoodJets");
	e_indiv.GetXaxis().SetBinLabel(9, "AtLeastThreeGoodJets");
	e_indiv.GetXaxis().SetBinLabel(10, "AtLeastFourGoodJets");
	e_indiv.GetXaxis().SetBinLabel(11, "AtLeastOneBTag");
	e_indiv.GetXaxis().SetBinLabel(12, "AtLeastTwoBTags");
	e_indiv.GetYaxis().SetTitle("Number of Events");


	mu_Canvas_consec = TCanvas("muCutFlow_consec","MuCutFlow", 0, 0, 800, 600)
	mu_Canvas_consec.SetLogy()
	mu_Canvas_consec.SetGridy()
	mu_consec.Draw()
	mu_Canvas_consec.Update()
	mu_Canvas_consec.SaveAs(outpath+'MuPlusJets_CutFlow_Consecutive.pdf')

	e_Canvas_consec = TCanvas("eCutFlow_consec","ECutFlow", 0, 0, 800, 600)
	e_Canvas_consec.SetLogy()
	e_Canvas_consec.SetGridy()
	e_consec.Draw()
	e_Canvas_consec.Update()
	e_Canvas_consec.SaveAs(outpath+'EPlusJets_CutFlow_Consecutive.pdf')

	mu_Canvas_indiv = TCanvas("muCutFlow_indiv","MuCutFlow", 0, 0, 800, 600)
	mu_Canvas_indiv.SetLogy()
	mu_Canvas_indiv.SetGridy()
	mu_indiv.Draw()
	mu_Canvas_indiv.Update()
	mu_Canvas_indiv.SaveAs(outpath+'MuPlusJets_CutFlow_Individual.pdf')

	e_Canvas_indiv = TCanvas("eCutFlow_indiv","ECutFlow", 0, 0, 800, 600)
	e_Canvas_indiv.SetLogy()
	e_Canvas_indiv.SetGridy()
	e_indiv.Draw()
	e_Canvas_indiv.Update()
	e_Canvas_indiv.SaveAs(outpath+'EPlusJets_CutFlow_Individual.pdf')



