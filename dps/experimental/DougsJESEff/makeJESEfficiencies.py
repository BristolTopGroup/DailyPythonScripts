import ROOT 
from ROOT import gPad, gROOT, gStyle, TFile, TTree, TH1F, TH2F, TCanvas, TPad, TLegend
from array import array
import math
import os
import os.path
import sys
import time
import glob

from argparse import ArgumentParser
from dps.utils.file_utilities import make_folder_if_not_exists

from rootpy.tree import Tree
from rootpy import asrootpy
from rootpy.io import root_open
from rootpy.plotting import Hist, Legend, Canvas
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from dps.config import CMS
from dps.config.xsection import XSectionConfig
from dps.utils.hist_utilities import value_tuplelist_to_hist
from matplotlib import rc
measurement_config = XSectionConfig( 13 )

ROOT.gROOT.SetBatch(True)
rc( 'font', **CMS.font )
rc( 'text', usetex = False )

def main():
	########## 			SETUP 			##########
	t = time.time()
	gStyle.SetOptStat("")

	#################################################################################################################################
	# READ THE OPTIONS
	#################################################################################################################################
	parser = ArgumentParser()
	parser.add_argument("-t", "--test", dest="test", action = "store_true", 
		help="Run over a few events only")
	parser.add_argument("-p", "--plots", dest="make_plots", action = "store_true", 
    	help="Print out files to .png")
	parser.add_argument("-o", "--only_plots", dest="only_plots", action = "store_true", 
    	help="Print out files to .png")
	parser.add_argument("-d", "--debug", dest="debug", action = "store_true", 
    	help="Run debugger")
	args = parser.parse_args()
	if args.test : print "RUNNING OVER TEST SAMPLE"
	debug = args.debug

	#################################################################################################################################
	# ADD THE GENERATOR INPUT FILES
	#################################################################################################################################
	samples = [
		"PowhegPythia8",
		"PowhegHerwigpp",
		"aMCatNLOPythia8",
		"Madgraph",
		"PowhegPythia8_fsrup", 
		"PowhegPythia8_fsrdown", 
		"PowhegPythia8_isrup", 
		"PowhegPythia8_isrdown", 
		# "PowhegPythia8_ueup", 
		# "PowhegPythia8_uedown", 
		# "PowhegPythia8_mtop1755", 
		# "PowhegPythia8_mtop1695", 
		# "PowhegPythia8_hdampup", 
		# "PowhegPythia8_hdampdown", 
		# "PowhegPythia8_erdOn", 
		# "PowhegPythia8_QCDbased_erdOn", 
		# "PowhegPythia8_GluonMove", 
	]
	if debug:
		print "Constructed Input Files and Read Arguments"
		t = get_time(t)

	#################################################################################################################################
	# INITIALISE THE BINNING AND WEIGHTS
	#################################################################################################################################
	pt_binning = [30, 50, 70, 100, 140, 200, 300, 600, 1000]
	# pt_binning = [30, 50, 70, 100, 140, 200]
	barrel_endcap_split = 1.3

	if debug:
		print "Initialised Pt and Eta binning"
		t = get_time(t)

	#################################################################################################################################
	# INITIALISE THE INPUT AND OUTPUT PATHS
	#################################################################################################################################
	file_path = 'dps/experimental/DougsJESEff/JESEfficiency.root'

	output_file = root_open(file_path, "recreate")
	make_folder_if_not_exists('plots/JetEfficiency/Summary/')


	#################################################################################################################################
	# CALCULATE THE JET PT / PSEUDOJET PT GAUSSIANS
	#################################################################################################################################
	r = {}
	for sample in samples:
		make_folder_if_not_exists('plots/JetEfficiency/'+sample)

		r[sample] = {}
		r[sample]['BarrelLightJet'] = {}
		r[sample]['BarrelBJet'] 	= {}
		r[sample]['EndcapLightJet'] = {}
		r[sample]['EndcapBJet'] 	= {}
		for i in range (1, len(pt_binning)):
			r[sample]['BarrelLightJet'][i] 	= Hist(50, 0, 2, name='Residuals_Bin_BarrelLightJet_'+sample+'_'+str(i))
			r[sample]['BarrelBJet'][i] 		= Hist(50, 0, 2, name='Residuals_Bin_BarrelBJet_'+sample+'_'+str(i))
			r[sample]['EndcapLightJet'][i] 	= Hist(50, 0, 2, name='Residuals_Bin_EndcapLightJet_'+sample+'_'+str(i))
			r[sample]['EndcapBJet'][i] 		= Hist(50, 0, 2, name='Residuals_Bin_EndcapBJet_'+sample+'_'+str(i))

		file_name = getFileName(sample, measurement_config)
		print "Calculating JES Efficiency For Generator : ",sample
		treeName = "TTbar_plus_X_analysis/JESAnalyser/JESAnalyser"
		file_name = getUnmergedDirectory(file_name)

		tree = ROOT.TChain(treeName);
		filenames = glob.glob( file_name )
		for f in filenames:
			tree.Add(f)

		nEntries = tree.GetEntries()
		print 'Number of entries:',nEntries
		n=0
		for event in tree:
			branch = event.__getattr__
			n+=1
			if not n%1000000: print 'Processing event %.0f Progress : %.2g %%' % ( n, float(n)/nEntries*100 )
			# if n > 1000: break

			jetPts = branch('jetPt')
			isBJets = branch('isB')
			isBarrels = branch('isBarrel')
			recoGenRatios = branch('recoGenRatio')

			for jpt, isBJet, isBarrel, recoGenRatio in zip(jetPts, isBJets, isBarrels, recoGenRatios):
				if jpt <= 30: continue
				# Find Jet Pt Bin to Fill
				for i, edge in enumerate(pt_binning):
					if jpt > edge: 
						continue
					else: 
						break

				# DEBUG PURPOSES
				# print "- "*30
				# print "Jet Pt : {}".format(jpt)
				# print "is a BJet : {}".format(isBJet)
				# print "is in Barrel : {}".format(isBarrel)
				# print "recoGen ratio : {}".format(recoGenRatio)
				# print "filled in Bin {}".format(i)
				# raw_input()

				if isBarrel:
					if isBJet:
						r[sample]['BarrelBJet'][i].Fill(recoGenRatio)
					else:
						r[sample]['BarrelLightJet'][i].Fill(recoGenRatio)
				else:
					if isBJet:
						r[sample]['EndcapBJet'][i].Fill(recoGenRatio)
					else:
						r[sample]['EndcapLightJet'][i].Fill(recoGenRatio)

	#################################################################################################################################
	# FIT THE GAUSSIANS AND CREATE AVERAGE JET PT / PSEUDOJET PT HISTOGRAMS
	#################################################################################################################################
	h_mean = {}
	for sample in samples:
		h_mean[sample] = {}
		for quadrant in ['BarrelLightJet', 'BarrelBJet', 'EndcapLightJet', 'EndcapBJet']:
			gaussian_fit = []
			for i, hist in r[sample][quadrant].iteritems():
				try:
					f = hist.Fit("gaus", "SMQ","", 0, 2)
					mean = f.Parameter(1)
				except:
					# Jet pt 20-30 not available
					mean = -1
					print "Cannot fit histogram"
				gaussian_fit.append(mean)

				# Plot individual pt bins
				canvas = TCanvas("c","c", 0, 0, 800, 600)
				hist.SetTitle(" ; pt; jet pT / pseudo jet pT")
				hist.Draw()
				canvas.Update()
				canvas.SaveAs('plots/JetEfficiency/'+sample+"/"+quadrant+"_"+str(i)+"_JetEfficiency.png")

			# Combine <pt ratio> into one hist
			h_mean[sample][quadrant] = value_tuplelist_to_hist(gaussian_fit, pt_binning)
			canvas = TCanvas("c","c", 0, 0, 800, 600)
			h_mean[sample][quadrant].SetTitle("JES efficiency ; pt; <jet over genjet>")
			h_mean[sample][quadrant].Draw()
			canvas.Update()
			canvas.SaveAs('plots/JetEfficiency/'+sample+"/"+quadrant+"_JetAveEfficiency.png")

	#################################################################################################################################
	# FIND THE CORRECTION, RATIO OF <Central Pt> / <Variation Pt>
	#################################################################################################################################
	h_jes = {}
	for sample in samples:
		h_jes[sample] = {}
		for quadrant in ['BarrelLightJet', 'BarrelBJet', 'EndcapLightJet', 'EndcapBJet']:

			h_jes[sample][quadrant] = h_mean['PowhegPythia8'][quadrant].Clone()
			h_jes[sample][quadrant].Divide(h_jes[sample][quadrant],h_mean[sample][quadrant],1,1,"B")

			canvas = TCanvas("c","c", 0, 0, 800, 600)
			h_jes[sample][quadrant].SetTitle("JES efficiency ; pt; <jet over genjet> over <jet over genjet>")
			h_jes[sample][quadrant].Draw()
			canvas.Update()
			canvas.SaveAs('plots/JetEfficiency/Summary/'+sample+"_"+quadrant+"_JetCorrection.png")



	colours = [
		'red', 'blue', 'green', 'chartreuse', 'indigo', 
		'magenta', 'darkmagenta', 'hotpink', 'cyan', 'darkred', 
		'darkgoldenrod', 'mediumvioletred', 'mediumspringgreen', 
		'gold', 'darkgoldenrod', 'slategray', 'dodgerblue', 
		'cadetblue', 'darkblue', 'seagreen', 'deeppink', 'deepskyblue' 
	]
	
	for quadrant in ['BarrelLightJet', 'BarrelBJet', 'EndcapLightJet', 'EndcapBJet']:
		i=0
		fig_eff = plt.figure( figsize = ( 20, 16 ), dpi = 400, facecolor = 'white' )
		ax_eff = fig_eff.add_subplot(1, 1, 1)
		ax_eff.minorticks_on()
		ax_eff.xaxis.labelpad = 12
		ax_eff.yaxis.labelpad = 12
		ax_eff.set_ylim( 0, 1 )
		plt.tick_params( **CMS.axis_label_major )
		plt.tick_params( **CMS.axis_label_minor )

		y_limits = [0.95,1.05]
		y_title = '<jet over genjet> / <jet over genjet>'
		x_title = 'Jet Pt [GeV]'
		plt.xlabel( x_title, CMS.x_axis_title )
		plt.ylabel( y_title, CMS.y_axis_title)

		template = '%.1f fb$^{-1}$ (%d TeV)'
		label = template % ( measurement_config.new_luminosity/1000., measurement_config.centre_of_mass_energy)
		plt.title( label,loc='right', **CMS.title )

		for sample, hists in h_jes.iteritems():
			hist = hists[quadrant]
			hist.linewidth = 4
			hist.color = 'black'
			l = sample
			if sample != 'PowhegPythia8':
				hist.linestyle = 'dashed'
				hist.linewidth = 2
				if 'aMCatNLOPythia8' in sample:
					hist.color = 'blue'
					hist.linestyle = 'solid'
				if 'PowhegHerwigpp' in sample:
					hist.color = 'red'
					hist.linestyle = 'solid'
				if 'Madgraph' in sample:
					hist.color = 'green'
					hist.linestyle = 'solid'
				if 'fsr' in sample:
					hist.color = 'hotpink'
					l = l.replace('down', '')
					if 'up' in sample: 	l = ''
				if 'isr' in sample:
					hist.color = 'cyan'
					l = l.replace('down', '')
					if 'up' in sample: 	l = ''

			rplt.hist( hist, stacked=False, label = l )
			i+=1

		# plot legend
		leg = plt.legend(loc='best',prop={'size':25},ncol=2)
		leg.draw_frame(False)	
		ax_eff.set_ylim( y_limits )

		# plt.text(0.05, 0.97, 
		#     r"{}".format(quadrant), 
		#     transform=ax_eff.transAxes, 
		#     fontsize=42,
		#     verticalalignment='top',
		#     horizontalalignment='left'
		# )

		plt.tight_layout()

		fig_eff.savefig('plots/JetEfficiency/Summary/'+quadrant+"_JetCorrections.pdf")


def get_time(t):
	'''
	How long does each step take?
	'''
	now_time = time.time()
	print "\t in {}s".format(now_time-t)
	return now_time

def getFileName( sample, measurementConfig ) :
    fileNames = {
        'PowhegPythia8'           			: measurementConfig.ttbar_trees,

        'aMCatNLOPythia8'          			: measurementConfig.ttbar_amc_trees,
        'Madgraph'          				: measurementConfig.ttbar_madgraph_trees,
        'PowhegHerwigpp'    				: measurementConfig.ttbar_powhegherwigpp_trees,

        'PowhegPythia8_ueup'              	: measurementConfig.ttbar_ueup_trees,
        'PowhegPythia8_uedown'            	: measurementConfig.ttbar_uedown_trees,
        'PowhegPythia8_isrup'             	: measurementConfig.ttbar_isrup_trees,
        'PowhegPythia8_isrdown'           	: measurementConfig.ttbar_isrdown_trees,
        'PowhegPythia8_fsrup'             	: measurementConfig.ttbar_fsrup_trees,
        'PowhegPythia8_fsrdown'           	: measurementConfig.ttbar_fsrdown_trees,

        'PowhegPythia8_hdampup'             : measurementConfig.ttbar_hdampup_trees,
        'PowhegPythia8_hdampdown'           : measurementConfig.ttbar_hdampdown_trees,

        'PowhegPythia8_erdOn'           	: measurementConfig.ttbar_erdOn_trees,
        'PowhegPythia8_QCDbased_erdOn'      : measurementConfig.ttbar_QCDbased_erdOn_trees,
        'PowhegPythia8_GluonMove'           : measurementConfig.ttbar_GluonMove_trees,
        'PowhegPythia8_GluonMove_erdOn'     : measurementConfig.ttbar_GluonMove_trees,

        'PowhegPythia8_mtop1695'          	: measurementConfig.ttbar_mtop1695_trees,
        'PowhegPythia8_mtop1755'            : measurementConfig.ttbar_mtop1755_trees,
    }

    return fileNames[sample]

def getUnmergedDirectory( f ) :
    baseDir = f.split('combined')[0]
    sampleName = f.split('combined')[-1].strip('/').split('_tree.root')[0]

    if 'TTJets_amc' in sampleName:
        sampleName = 'TTJets_amcatnloFXFX'
    elif 'TTJets_madgraph' in sampleName:
        sampleName = 'TTJets_madgraphMLM'
    new_f = None
    if 'plusJES' in f:
        new_f = baseDir + '/' + sampleName.strip('_plusJES') + '/analysis_JES_up_job_*/*root'
    elif 'minusJES' in f:
        new_f = baseDir + '/' + sampleName.strip('_minusJES') + '/analysis_JES_down_job_*/*root'
    elif 'plusJER' in f:
        new_f = baseDir + '/' + sampleName.strip('_plusJER') + '/analysis_JetSmearing_up_job_*/*root'
    elif 'minusJER' in f:
        new_f = baseDir + '/' + sampleName.strip('_minusJER') + '/analysis_JetSmearing_down_job_*/*root'
    else:
        new_f = baseDir + '/' + sampleName + '/analysis_central_job_*/*root'
    return new_f

if __name__ == '__main__':
	main()
