
import ROOT 
from ROOT import gROOT, gPad, gStyle, TChain, TFile, TTree, TMath, TH1, TH1F, TH2F, TCanvas, TPad, TAxis, TLegend, TLatex, kRed, kBlue, kGreen, kMagenta
import math

if __name__ == '__main__':


	########## 			SETUP 			##########
	gStyle.SetOptStat("")
	input_file = "/storage/db0268/TopCrossSections/LocalAnalysis/CMSSW_7_5_0/src/BTagEfficiency/data/tree_TTJets_amcatnloFXFX_5000pb_PFElectron_PFMuon_PF2PATJets_MET.root"
	file = TFile("BTagEfficiency.root", "RECREATE")


	Channel = {
	1 : 'E',
	2 : 'Mu',
	}


	for x in Channel:	

		allQuarkJets_Total_Hist = TH2F("allQuarkJets_Total_"+Channel[x]+"_Hist", "allQuarkJets_Total_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)
		allQuarkJets_BTags_Hist = TH2F("allQuarkJets_BTags_"+Channel[x]+"_Hist", "allQuarkJets_BTags_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)

		bQuarkJets_Total_Hist = TH2F("bQuarkJets_Total_"+Channel[x]+"_Hist", "bQuarkJets_Total_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)
		bQuarkJets_BTags_Hist = TH2F("bQuarkJets_BTags_"+Channel[x]+"_Hist", "bQuarkJets_BTags_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)

		cQuarkJets_Total_Hist = TH2F("cQuarkJets_Total_"+Channel[x]+"_Hist", "cQuarkJets_Total_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)
		cQuarkJets_BTags_Hist = TH2F("cQuarkJets_BTags_"+Channel[x]+"_Hist", "cQuarkJets_BTags_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)

		udsQuarkJets_Total_Hist = TH2F("udsQuarkJets_Total_"+Channel[x]+"_Hist", "udsQuarkJets_Total_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)
		udsQuarkJets_BTags_Hist = TH2F("udsQuarkJets_BTags_"+Channel[x]+"_Hist", "udsQuarkJets_BTags_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)

		gluonQuarkJets_Total_Hist = TH2F("gluonQuarkJets_Total_"+Channel[x]+"_Hist", "gluonQuarkJets_Total_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)
		gluonQuarkJets_BTags_Hist = TH2F("gluonQuarkJets_BTags_"+Channel[x]+"_Hist", "gluonQuarkJets_BTags_"+Channel[x]+"_Hist", 100, 20, 200, 100, -2.4, 2.4)

		inputTree = "TTbar_plus_X_analysis/"+Channel[x]+"PlusJets/Ref selection/BTagEfficiencies/Jets"

		Chain = TChain(inputTree)
		Chain.Add(input_file)
		Chain.SetBranchStatus("*",1)


		########## 			FILL HISTOGRAMS 		##########

		for event in Chain:

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

				allQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
				if (isTight[JetIndex] == 1):
					allQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

				if (partonFlavour[JetIndex] == 5):
					bQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
					if (isTight[JetIndex] == 1):
						bQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

				if (partonFlavour[JetIndex] == 4):
					cQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
					if (isTight[JetIndex] == 1):
						cQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

				if (partonFlavour[JetIndex] == 3 or partonFlavour[JetIndex] == 2 or partonFlavour[JetIndex] == 1 or partonFlavour[JetIndex] == 0):
					udsQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
					if (isTight[JetIndex] == 1):
						udsQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])

				if (partonFlavour[JetIndex] == 21):
					gluonQuarkJets_Total_Hist.Fill(pt[JetIndex], eta[JetIndex])
					if (isTight[JetIndex] == 1):
						gluonQuarkJets_BTags_Hist.Fill(pt[JetIndex], eta[JetIndex])


		########## 				PLOTTING 			##########

		allQuarkJets_Total_Hist.Write()
		bQuarkJets_Total_Hist.Write()
		cQuarkJets_Total_Hist.Write()
		udsQuarkJets_Total_Hist.Write()
		gluonQuarkJets_Total_Hist.Write()

		allQuarkJets_BTags_Hist.Write()
		bQuarkJets_BTags_Hist.Write()
		cQuarkJets_BTags_Hist.Write()
		udsQuarkJets_BTags_Hist.Write()
		gluonQuarkJets_BTags_Hist.Write()

		########## 			    B Quark 			##########

		allQuarkJets_BTags_Hist.Divide(allQuarkJets_Total_Hist)
		bQuarkJets_BTags_Hist.Divide(bQuarkJets_Total_Hist)
		cQuarkJets_BTags_Hist.Divide(cQuarkJets_Total_Hist)
		udsQuarkJets_BTags_Hist.Divide(udsQuarkJets_Total_Hist)
		gluonQuarkJets_BTags_Hist.Divide(gluonQuarkJets_Total_Hist)

		allQuarkJetCanvas = TCanvas("allQuarkJet"+Channel[x],"allQuarkJet"+Channel[x], 0, 0, 800, 600)
		allQuarkJets_BTags_Hist.SetTitle("allQuarkJet "+Channel[x]+" BTag Efficiencies; pt; eta")
		allQuarkJets_BTags_Hist.Draw("colz")
		allQuarkJetCanvas.Update()
		allQuarkJetCanvas.SaveAs("plots/"+Channel[x]+"_allQuarkJet_BTagEfficiency.png")
		allQuarkJetCanvas.Write()

		bQuarkJetCanvas = TCanvas("bQuarkJet"+Channel[x],"bQuarkJet"+Channel[x], 0, 0, 800, 600)
		bQuarkJets_BTags_Hist.SetTitle("bQuarkJet "+Channel[x]+" BTag Efficiencies; pt; eta")
		bQuarkJets_BTags_Hist.Draw("colz")
		bQuarkJetCanvas.Update()
		bQuarkJetCanvas.SaveAs("plots/"+Channel[x]+"_bQuarkJet_BTagEfficiency.png")
		bQuarkJetCanvas.Write()

		cQuarkJetCanvas = TCanvas("cQuarkJet"+Channel[x],"cQuarkJet"+Channel[x], 0, 0, 800, 600)
		cQuarkJets_BTags_Hist.SetTitle("cQuarkJet "+Channel[x]+" BTag Efficiencies; pt; eta")
		cQuarkJets_BTags_Hist.Draw("colz")
		cQuarkJetCanvas.Update()
		cQuarkJetCanvas.SaveAs("plots/"+Channel[x]+"_cQuarkJet_BTagEfficiency.png")
		cQuarkJetCanvas.Write()
		
		udsQuarkJetCanvas = TCanvas("udsQuarkJet"+Channel[x],"udsQuarkJet"+Channel[x], 0, 0, 800, 600)
		udsQuarkJets_BTags_Hist.SetTitle("udsQuarkJet "+Channel[x]+" BTag Efficiencies; pt; eta")
		udsQuarkJets_BTags_Hist.Draw("colz")
		udsQuarkJetCanvas.Update()
		udsQuarkJetCanvas.SaveAs("plots/"+Channel[x]+"_udsQuarkJet_BTagEfficiency.png")
		udsQuarkJetCanvas.Write()

		gluonQuarkJetCanvas = TCanvas("gluonQuarkJet"+Channel[x],"gluonQuarkJet"+Channel[x], 0, 0, 800, 600)
		gluonQuarkJets_BTags_Hist.SetTitle("gluonQuarkJet "+Channel[x]+" BTag Efficiencies; pt; eta")
		gluonQuarkJets_BTags_Hist.Draw("colz")
		gluonQuarkJetCanvas.Update()
		gluonQuarkJetCanvas.SaveAs("plots/"+Channel[x]+"_gluonQuarkJet_BTagEfficiency.png")
		gluonQuarkJetCanvas.Write()
