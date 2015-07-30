
import ROOT 
from ROOT import gROOT, gPad, gStyle, TChain, TFile, TTree, TMath, TH1, TH1F, TH2F, TCanvas, TPad, TAxis, TLegend, TLatex, kRed, kBlue, kGreen, kMagenta
from array import array
import math

if __name__ == '__main__':


	########## 			SETUP 			##########
	gStyle.SetOptStat("")
	input_file = "/storage/db0268/TopCrossSections/AnalysisSoftware/CMSSW_7_5_0/src/tree_TTJets_amcatnloFXFX_1000pb_PFElectron_PFMuon_PF2PATJets_MET.root"
	file = TFile("BTagEfficiency.root", "RECREATE")

	# pt_binning = array ( 'f' , [25., 30., 40., 50., 60., 70., 80., 100., 120., 160., 210., 260., 320., 400., 500., 600., 800.] )
	# eta_binning = array ( 'f', [ -2.4, 2.4 ] )
	pt_binning = array ( 'f' , [25, 30, 40, 50, 100] )
	eta_binning = array ( 'f', [-2.5, -1.478, -0.8, 0, 0.8, 1.478, 2.5] )

	bQuarkJets_Total_Hist = TH2F("bQuarkJets_Total_Hist", "bQuarkJets_Total_Hist", 4, pt_binning, 6, eta_binning)
	bQuarkJets_BTags_Hist = TH2F("bQuarkJets_BTags_Hist", "bQuarkJets_BTags_Hist", 4, pt_binning, 6, eta_binning)

	cQuarkJets_Total_Hist = TH2F("cQuarkJets_Total_Hist", "cQuarkJets_Total_Hist", 4, pt_binning, 6, eta_binning)
	cQuarkJets_BTags_Hist = TH2F("cQuarkJets_BTags_Hist", "cQuarkJets_BTags_Hist", 4, pt_binning, 6, eta_binning)

	udsQuarkJets_Total_Hist = TH2F("udsQuarkJets_Total_Hist", "udsQuarkJets_Total_Hist", 4, pt_binning, 6, eta_binning)
	udsQuarkJets_BTags_Hist = TH2F("udsQuarkJets_BTags_Hist", "udsQuarkJets_BTags_Hist", 4, pt_binning, 6, eta_binning)

	gluonQuarkJets_Total_Hist = TH2F("gluonQuarkJets_Total_Hist", "gluonQuarkJets_Total_Hist", 4, pt_binning, 6, eta_binning)
	gluonQuarkJets_BTags_Hist = TH2F("gluonQuarkJets_BTags_Hist", "gluonQuarkJets_BTags_Hist", 4, pt_binning, 6, eta_binning)



	E_inputTree = "TTbar_plus_X_analysis/EPlusJets/Ref selection/BTagEfficiencies/Jets"
	E_Chain = TChain(E_inputTree)
	E_Chain.Add(input_file)

	Mu_inputTree = "TTbar_plus_X_analysis/MuPlusJets/Ref selection/BTagEfficiencies/Jets"
	Mu_Chain = TChain(Mu_inputTree)
	Mu_Chain.Add(input_file)

	E_Chain.SetBranchStatus("*",1)
	Mu_Chain.SetBranchStatus("*",1)

	# n=0

	########## 			FILL HISTOGRAMS 		##########
	for event in E_Chain:
		# n=n+1
		# if n==1000: break
		NJets = event.__getattr__("NJets")
		if (NJets <= 0): continue;

		for JetIndex in range (0,int(NJets)):

			pt = event.__getattr__("pt")
			eta = event.__getattr__("eta")
			CSV = event.__getattr__("CSV")
			partonFlavour = event.__getattr__("partonFlavour")
			isLoose = event.__getattr__("isLoose")
			isMedium = event.__getattr__("isMedium")
			isTight = event.__getattr__("isTight")

			# print pt[JetIndex]
			# print eta[JetIndex]
			# print partonFlavour[JetIndex]
			# print isTight[JetIndex]
			if (pt[JetIndex] < 25): continue;

			if (partonFlavour[JetIndex] == 5):
				bQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					bQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

			if (partonFlavour[JetIndex] == 4):
				cQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					cQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

			if (partonFlavour[JetIndex] == 3 or partonFlavour[JetIndex] == 2 or partonFlavour[JetIndex] == 1 or partonFlavour[JetIndex] == 0):
				udsQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					udsQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

			if (partonFlavour[JetIndex] == 21):
				gluonQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					gluonQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

	for event in Mu_Chain:
		# if n==1000: break

		NJets = event.__getattr__("NJets")
		if (NJets <= 0): continue;

		for JetIndex in range (0,int(NJets)):

			pt = event.__getattr__("pt")
			eta = event.__getattr__("eta")
			CSV = event.__getattr__("CSV")
			partonFlavour = event.__getattr__("partonFlavour")
			isLoose = event.__getattr__("isLoose")
			isMedium = event.__getattr__("isMedium")
			isTight = event.__getattr__("isTight")

			# print pt[JetIndex]
			# print eta[JetIndex]
			# print partonFlavour[JetIndex]
			# print isTight[JetIndex]
			if (pt[JetIndex] < 25): continue;

			if (partonFlavour[JetIndex] == 5):
				bQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					bQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

			if (partonFlavour[JetIndex] == 4):
				cQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					cQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

			if (partonFlavour[JetIndex] == 3 or partonFlavour[JetIndex] == 2 or partonFlavour[JetIndex] == 1 or partonFlavour[JetIndex] == 0):
				udsQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					udsQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

			if (partonFlavour[JetIndex] == 21):
				gluonQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isMedium[JetIndex] == 1):
					gluonQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])


	########## 			    B Quark 			##########

	bQuarkJets_BTags_Hist.Sumw2()
	cQuarkJets_BTags_Hist.Sumw2()
	udsQuarkJets_BTags_Hist.Sumw2()
	gluonQuarkJets_BTags_Hist.Sumw2()

	bQuarkJets_Total_Hist.Sumw2()
	cQuarkJets_Total_Hist.Sumw2()
	udsQuarkJets_Total_Hist.Sumw2()
	gluonQuarkJets_Total_Hist.Sumw2()

	# Divide N by Ntot to get BTag Eff 1,1, are scalers for each hist but not used with "B" which calcs Binomial errors, updating Sumw2()
	bQuarkJets_BTags_Hist.Divide(bQuarkJets_BTags_Hist,bQuarkJets_Total_Hist,  1, 1,  "B")
	cQuarkJets_BTags_Hist.Divide(cQuarkJets_BTags_Hist,cQuarkJets_Total_Hist, 1, 1,   "B")
	udsQuarkJets_BTags_Hist.Divide(udsQuarkJets_BTags_Hist,udsQuarkJets_Total_Hist, 1, 1,   "B")
	gluonQuarkJets_BTags_Hist.Divide(gluonQuarkJets_BTags_Hist,gluonQuarkJets_Total_Hist, 1, 1,   "B")

	bQuarkJets_BTags_Hist.Write()
	cQuarkJets_BTags_Hist.Write()
	udsQuarkJets_BTags_Hist.Write()
	gluonQuarkJets_BTags_Hist.Write()

	########## 				PLOTTING 			##########

	# Easy access to .pngs 
	bQuarkJetCanvas = TCanvas("bQuarkJet","bQuarkJet", 0, 0, 800, 600)
	bQuarkJets_BTags_Hist.SetTitle("bQuarkJet BTag Efficiencies; pt; eta")
	bQuarkJets_BTags_Hist.Draw("col text e")
	bQuarkJetCanvas.Update()
	bQuarkJetCanvas.SaveAs("plots/bQuarkJet_BTagEfficiency.png")

	cQuarkJetCanvas = TCanvas("cQuarkJet","cQuarkJet", 0, 0, 800, 600)
	cQuarkJets_BTags_Hist.SetTitle("cQuarkJet BTag Efficiencies; pt; eta")
	cQuarkJets_BTags_Hist.Draw("col text e")
	cQuarkJetCanvas.Update()
	cQuarkJetCanvas.SaveAs("plots/cQuarkJet_BTagEfficiency.png")
	
	udsQuarkJetCanvas = TCanvas("udsQuarkJet","udsQuarkJet", 0, 0, 800, 600)
	udsQuarkJets_BTags_Hist.SetTitle("udsQuarkJet BTag Efficiencies; pt; eta")
	udsQuarkJets_BTags_Hist.Draw("col text e")
	udsQuarkJetCanvas.Update()
	udsQuarkJetCanvas.SaveAs("plots/udsQuarkJet_BTagEfficiency.png")

	gluonQuarkJetCanvas = TCanvas("gluonQuarkJet","gluonQuarkJet", 0, 0, 800, 600)
	gluonQuarkJets_BTags_Hist.SetTitle("gluonQuarkJet BTag Efficiencies; pt; eta")
	gluonQuarkJets_BTags_Hist.Draw("col text e")
	gluonQuarkJetCanvas.Update()
	gluonQuarkJetCanvas.SaveAs("plots/gluonQuarkJet_BTagEfficiency.png")



