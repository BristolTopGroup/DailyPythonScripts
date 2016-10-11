'''
Run this script with 2015 Data datasets to merge the cutflows from the ntuples.
'''




import ROOT 
from ROOT import gROOT, TFile, TH1F, TCanvas, TChain
import math

import os
import glob

if __name__ == '__main__':
	basepath = '/hdfs/TopQuarkGroup/run2/atOutput/13TeV/25ns/'
	outpath = 'plots/CutFlows/'

	e_consec = TH1F('eConsecCut', 'EPlusJets Consectutive Cutflow', 10, -0.500000, 9.500000)
	e_indiv = TH1F('eIndivCut', 'EPlusJets Individual Cutflow', 10, -0.500000, 9.500000)
	mu_consec = TH1F('muConsecCut', 'MuPlusJets Consectutive Cutflow', 9, -0.500000, 8.500000)
	mu_indiv = TH1F('muIndivCut', 'MuPlusJets Individual Cutflow', 9, -0.500000, 8.500000)
	e_consec_mc = TH1F('eConsecCut_mc', 'MC EPlusJets Consectutive Cutflow', 10, -0.500000, 9.500000)
	e_indiv_mc = TH1F('eIndivCut_mc', 'MC EPlusJets Individual Cutflow', 10, -0.500000, 9.500000)
	mu_consec_mc = TH1F('muConsecCut_mc', 'MC MuPlusJets Consectutive Cutflow', 9, -0.500000, 8.500000)
	mu_indiv_mc = TH1F('muIndivCut_mc', 'MC MuPlusJets Individual Cutflow', 9, -0.500000, 8.500000)

	plotlist = [e_indiv, e_consec, mu_indiv, mu_consec, e_indiv_mc, e_consec_mc, mu_indiv_mc, mu_consec_mc]

	dataTypes = {
	'MC'   : ['TTJets_PowhegPythia8_tree.root'],
	'Data' : ['data_electron_tree.root', 'data_muon_tree.root'],
	}

	channel = {
	'E'  : [[e_indiv, e_consec],[e_indiv_mc, e_consec_mc]],
	'Mu' : [[mu_indiv, mu_consec],[mu_indiv_mc, mu_consec_mc]],
	}

	Cuts = {
	0 : "All Events",
	1 : "Trigger Selection",
	2 : "MET Selection",
	3 : "Lepton Selection",
	4 : "Electron Veto",	
	5 : "Muon Veto",	
	6 : "Conversion Veto",
	7 : "Jet Selection",
	8 : "BJet Selection",
	9 : "Pass All",
	}

	for dataType, dataFile, in dataTypes.iteritems():
		for ch, hists in channel.iteritems():

			filepath='' # Find appropriate file path
			if dataType == 'MC': filepath = basepath+dataFile[0]
			elif dataType == 'Data' and ch == 'E' : filepath = basepath+dataFile[0]
			elif dataType == 'Data' and ch == 'Mu' : filepath = basepath+dataFile[1]
			print dataType
			print ch
			print filepath

			treepath = 'TTbar_plus_X_analysis/'+ch+'PlusJets/Cutflow/Cutflow' # Find appropriate tree
			chain = TChain(treepath)
			chain.Add(filepath)
			nevent=0
			for event in chain:
				nevent=nevent+1
				if nevent==10000 : break


				tag = event.__getattr__("Cutflow") # Get list of cuts in bool form

				passLastCut=True
				for i, cut in enumerate(tag) : # Loop over list of cuts

					if dataType == 'Data' : hist = hists[0] # Choose between MC and Data Histograms
					elif dataType == 'MC' : hist = hists[1]

					if (ch == 'Mu' and i >= 6) : cutName = Cuts[i+1] # Skip Conversion Label
					else : cutName = Cuts[i]

					hist[0].Fill(cutName, cut) # Individual Cuts

					if not cut : passLastCut=False
					if passLastCut : hist[1].Fill(cutName, cut) # Consecutive Cuts

	for plot in plotlist:
		canvas = TCanvas("CanvasRef", "CanvasTitle", 800,600)
		# canvas.SetLogy()
		# canvas.SetGridy()
		plot.SetMinimum(0)
		plot.Draw("text")
		canvas.Update()
		canvas.SaveAs(outpath+plot.GetTitle()+'.pdf')	
		canvas.Close()	
