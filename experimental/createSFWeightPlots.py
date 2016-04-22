
import ROOT 
from ROOT import gROOT, TFile, TH1F, TCanvas
import math

import os
import glob
ROOT.gROOT.SetBatch(True)

if __name__ == '__main__':

	basepath = '/hdfs/TopQuarkGroup/run2/atOutput/13TeV/25ns/'
	outpath = '../plots/SFWeights/'

	# if not os.path.exists(outpath): 
	# 	os.makedirs(outpath)

	datasets = []

	SF = [ 
	'BJetWeight', 
	'BJetUpWeight', 
	'BJetDownWeight', 
	'LightJetUpWeight', 
	'LightJetDownWeight', 
	'EventWeight', 
	'PUWeight', 
	'PUWeight_up', 
	'PUWeight_down',
	 ]

	for dirs in os.listdir(basepath):
		if ".root" in dirs : datasets.append(dirs)

	for f in datasets:

		# if not f == 'TTJets_PowhegPythia8_tree.root' : continue
		
		print ""
		print "New File ________________________________________________________________________________________________________________________"
		print 'Current File : ', f
		print "Current File Path", basepath
		filename = os.path.splitext(f)[0]
		if not os.path.exists(outpath+filename+'/'): 
			os.makedirs(outpath+filename+'/')

		for weight in SF : 
			print 'Current Weight : ', weight
			tree = "TTbar_plus_X_analysis/Unfolding/Unfolding"

			if "JER" in filename :
				if "minus" in filename : tree = tree+"_JERDown"
				if "plus" in filename : tree = tree+"_JERUp"
			elif "JES" in filename :
				if "minus" in filename : tree = tree+"_JESDown"
				if "plus" in filename : tree = tree+"_JESUp"

			# tree = tree+weight
			print "Current Tree Path : ", tree

			rootfile = basepath+f

			if not os.path.exists(rootfile): 
				print 'File Does Not exist'
				break
			else: print 'Adding File : ', rootfile

			rtfile = TFile(rootfile)
			if "PUWeight" in weight : tmp = TH1F('tmp', weight+' Unfolding; SF; Number of Events', 50, 0, 5)
			else : tmp = TH1F('tmp', weight+' Unfolding; SF; Number of Events', 50, 0, 2)
			hist = rtfile.Get(tree)
			canvas = TCanvas("CanvasRef", "CanvasTitle", 800,600)
			canvas.SetGridy()
			drawparams = weight+">>tmp"
			hist.Draw(drawparams)
			canvas.Update()
			canvas.SaveAs(outpath+filename+'/'+weight+' '+hist.GetTitle()+'.pdf')	
			canvas.Close()	

			rtfile.Close()

			print "Canvas Created __________________________________________________________________________________________________________________"
			print ""

