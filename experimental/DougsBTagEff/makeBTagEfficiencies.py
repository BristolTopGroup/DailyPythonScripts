
import ROOT 
from ROOT import gROOT, gPad, gStyle, TChain, TFile, TTree, TMath, TH1, TH1F, TH2F, TCanvas, TPad, TAxis, TLegend, TLatex, kRed, kBlue, kGreen, kMagenta
from array import array
import math
import os
ROOT.gROOT.SetBatch(True)
if __name__ == '__main__':


	########## 			SETUP 			##########
	gStyle.SetOptStat("")
	input_file = "/hdfs/TopQuarkGroup/run2/atOutput/13TeV/25ns/TTJets_PowhegPythia8_tree.root"
	file = TFile("BTagEfficiency.root", "RECREATE")

	if not os.path.exists('plots'):
		os.makedirs('plots')

	pt_binning = array ( 'f' , [30, 50, 70, 100, 140, 200, 300, 670] )
	eta_binning = array ( 'f', [-2.4, -2.1, -1.5, 0, 1.5, 2.1, 2.4] )


	nPtBins = len( pt_binning )	- 1
	nEtaBins = len( eta_binning )	- 1
	bQuarkJets_Total_Hist = TH2F("bQuarkJets_Total_Hist", "bQuarkJets_Total_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
	bQuarkJets_BTags_Hist = TH2F("bQuarkJets_BTags_Hist", "bQuarkJets_BTags_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)

	cQuarkJets_Total_Hist = TH2F("cQuarkJets_Total_Hist", "cQuarkJets_Total_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
	cQuarkJets_BTags_Hist = TH2F("cQuarkJets_BTags_Hist", "cQuarkJets_BTags_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)

	udsgQuarkJets_Total_Hist = TH2F("udsgQuarkJets_Total_Hist", "udsgQuarkJets_Total_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)
	udsgQuarkJets_BTags_Hist = TH2F("udsgQuarkJets_BTags_Hist", "udsgQuarkJets_BTags_Hist", nPtBins, pt_binning, nEtaBins, eta_binning)

	E_inputTree = "TTbar_plus_X_analysis/EPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
	E_Chain = TChain(E_inputTree)
	E_Chain.Add(input_file)

	Mu_inputTree = "TTbar_plus_X_analysis/MuPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
	Mu_Chain = TChain(Mu_inputTree)
	Mu_Chain.Add(input_file)

	for chain in [E_Chain, Mu_Chain]:
		chain.SetBranchStatus("*",0)
		chain.SetBranchStatus("pt",1)
		chain.SetBranchStatus("eta",1)
		chain.SetBranchStatus("CSV",1)
		chain.SetBranchStatus("partonFlavour",1)
		chain.SetBranchStatus("isLoose",1)
		chain.SetBranchStatus("isMedium",1)
		chain.SetBranchStatus("isTight",1)
		chain.SetBranchStatus("NJets",1)
		chain.SetBranchStatus("EventWeight",1)
		chain.SetBranchStatus("PUWeight",1)
		chain.SetBranchStatus("ElectronEfficiencyCorrection",1)
		chain.SetBranchStatus("MuonEfficiencyCorrection",1)

	########## 			FILL HISTOGRAMS 		##########
	print 'Electron channel'
	n=0
	for event in E_Chain:
		n=n+1
		if n==100000: print n, "th Event"

		NJets = event.__getattr__("NJets")
		if (NJets <= 0): continue;

		pt = event.__getattr__("pt")
		eta = event.__getattr__("eta")
		CSV = event.__getattr__("CSV")
		partonFlavour = event.__getattr__("partonFlavour")
		isLoose = event.__getattr__("isLoose")
		isMedium = event.__getattr__("isMedium")
		isTight = event.__getattr__("isTight")

		eventWeight = event.__getattr__("EventWeight")
		puWeight = event.__getattr__("PUWeight")
		electronWeight = event.__getattr__("ElectronEfficiencyCorrection")
		weight = eventWeight * puWeight * electronWeight

		for JetIndex in range (0,int(NJets)):

			if (pt[JetIndex] < 25): continue;

			if (partonFlavour[JetIndex] == 5):
				bQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)
				if (isMedium[JetIndex] == 1):
					bQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)

			if (partonFlavour[JetIndex] == 4):
				cQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)
				if (isMedium[JetIndex] == 1):
					cQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)

			if (partonFlavour[JetIndex] == 3 or partonFlavour[JetIndex] == 2 or partonFlavour[JetIndex] == 1 or partonFlavour[JetIndex] == 0 or partonFlavour[JetIndex] == 21):
				udsgQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)
				if (isMedium[JetIndex] == 1):
					udsgQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)

			# if (partonFlavour[JetIndex] == 21):
			# 	gluonQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)
			# 	if (isMedium[JetIndex] == 1):
			# 		gluonQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)

	print 'Muon channel'
	n=0
	for event in Mu_Chain:
		n=n+1
		if n==100000: print n, "th Event"

		NJets = event.__getattr__("NJets")
		if (NJets <= 0): continue;

		pt = event.__getattr__("pt")
		eta = event.__getattr__("eta")
		CSV = event.__getattr__("CSV")
		partonFlavour = event.__getattr__("partonFlavour")
		isLoose = event.__getattr__("isLoose")
		isMedium = event.__getattr__("isMedium")
		isTight = event.__getattr__("isTight")

		eventWeight = event.__getattr__("EventWeight")
		puWeight = event.__getattr__("PUWeight")
		muonWeight = event.__getattr__("MuonEfficiencyCorrection")
		weight = eventWeight * puWeight * muonWeight

		for JetIndex in range (0,int(NJets)):

			if (pt[JetIndex] < 25): continue;

			if (partonFlavour[JetIndex] == 5):
				bQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)
				if (isMedium[JetIndex] == 1):
					bQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)

			if (partonFlavour[JetIndex] == 4):
				cQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)
				if (isMedium[JetIndex] == 1):
					cQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)

			if (partonFlavour[JetIndex] == 3 or partonFlavour[JetIndex] == 2 or partonFlavour[JetIndex] == 1 or partonFlavour[JetIndex] == 0 or partonFlavour[JetIndex] == 21):
				udsgQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)
				if (isMedium[JetIndex] == 1):
					udsgQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex], weight)

	########## 			    B Quark 			##########

	bQuarkJets_BTags_Hist.Sumw2()
	cQuarkJets_BTags_Hist.Sumw2()
	udsgQuarkJets_BTags_Hist.Sumw2()

	bQuarkJets_Total_Hist.Sumw2()
	cQuarkJets_Total_Hist.Sumw2()
	udsgQuarkJets_Total_Hist.Sumw2()

	# Divide N by Ntot to get BTag Eff 1,1, are scalers for each hist but not used with "B" which calcs Binomial errors, updating Sumw2()
	bQuarkJets_BTags_Hist.Divide(bQuarkJets_BTags_Hist,bQuarkJets_Total_Hist,  1, 1,  "B")
	cQuarkJets_BTags_Hist.Divide(cQuarkJets_BTags_Hist,cQuarkJets_Total_Hist, 1, 1,   "B")
	udsgQuarkJets_BTags_Hist.Divide(udsgQuarkJets_BTags_Hist,udsgQuarkJets_Total_Hist, 1, 1,   "B")

	bQuarkJets_BTags_Hist.Write()
	cQuarkJets_BTags_Hist.Write()
	udsgQuarkJets_BTags_Hist.Write()

	########## 				PLOTTING 			##########

	# Easy access to .pngs 
	bQuarkJetCanvas = TCanvas("bQuarkJet","bQuarkJet", 0, 0, 800, 600)
	bQuarkJets_BTags_Hist.SetTitle("bQuarkJet BTag Efficiencies; pt; eta")
	bQuarkJets_BTags_Hist.Draw("colz text e")
	bQuarkJetCanvas.Update()
	bQuarkJetCanvas.SaveAs("plots/bQuarkJet_BTagEfficiency.png")

	cQuarkJetCanvas = TCanvas("cQuarkJet","cQuarkJet", 0, 0, 800, 600)
	cQuarkJets_BTags_Hist.SetTitle("cQuarkJet BTag Efficiencies; pt; eta")
	cQuarkJets_BTags_Hist.Draw("colz text e")
	cQuarkJetCanvas.Update()
	cQuarkJetCanvas.SaveAs("plots/cQuarkJet_BTagEfficiency.png")
	
	udsgQuarkJetCanvas = TCanvas("udsgQuarkJet","udsgQuarkJet", 0, 0, 800, 600)
	udsgQuarkJets_BTags_Hist.SetTitle("udsgQuarkJet BTag Efficiencies; pt; eta")
	udsgQuarkJets_BTags_Hist.Draw("colz text e")
	udsgQuarkJetCanvas.Update()
	udsgQuarkJetCanvas.SaveAs("plots/udsgQuarkJet_BTagEfficiency.png")


