#!/usr/bin/env python
from config import XSectionConfig
from tools.file_utilities import make_folder_if_not_exists
from optparse import OptionParser

import os
import sys
import subprocess

parser = OptionParser("Move BAT output files to hdfs")
parser.add_option("-c", "--centreOfMassEnergy", type='int', 
				help="Specify centre of mass energy")
parser.add_option("--doNothing", dest="doNothing", action='store_true', default=False,
				help="Don't actually move anything, just show the files to be moved and the location")
parser.add_option("-p", "--pathToBATOutputFiles", dest="pathToBATOutputFiles", default=None,
				help="Specify the path where the BAT output files you want to move to hdfs are located.\
				Format should be e.g /storage/<username>/<folder>/<cmssw_folder>/src/")
(options, _) = parser.parse_args()

if not options.pathToBATOutputFiles:
	print "No path to files to be moved. Exiting."
	sys.exit()
	
if options.centreOfMassEnergy != 7 and options.centreOfMassEnergy != 8:
	print "Centre of mass energy must be 7 or 8 TeV"
	print "You've chosen", options.centreOfMassEnergy
	sys.exit()

#set up the config according to the centre of mass energy
config = XSectionConfig(options.centreOfMassEnergy)

#Get the luminosity for the centre of mass energy
luminosity = config.luminosities[options.centreOfMassEnergy]

#Get current working directory
current_working_directory = os.getcwd()

#Get folder to move files to
path_to_AN_folder = config.path_to_files

#move log files separately first, since there is no "logs" category in categories_and_prefixes
make_folder_if_not_exists(path_to_AN_folder + '/logs/')
command = 'mv ' + options.pathToBATOutputFiles + '/*' + str(options.centreOfMassEnergy) + 'TeV*.log ' + path_to_AN_folder + '/logs/'
if options.doNothing:
	print "command = ", command
	print "path to folder = ", path_to_AN_folder + '/logs/'
elif not options.doNothing:
	make_folder_if_not_exists( path_to_AN_folder + "/logs" )

	p = subprocess.Popen(command, shell=True)
	p.wait()

#Now move all other BAT output files.

for category in config.categories_and_prefixes.keys():
	make_folder_if_not_exists(path_to_AN_folder + "/" + category)
	command = 'mv ' + options.pathToBATOutputFiles + '/*' + str(luminosity) + 'pb*' + config.categories_and_prefixes[category] + '.root ' + path_to_AN_folder + "/" + category
	#make sure if category is central, only the central root files are selected by making sure the filename ending is correct for central files.
	if category == 'central':
		command.replace('.root', 'PFMET.root')
		
	if options.doNothing:
		print "command = ", command
		print "path to folder = ", path_to_AN_folder + "/" + category
	elif not options.doNothing:
		# Now move output file to hdfs
		make_folder_if_not_exists( path_to_AN_folder + "/" + category )
		
		#check if folder is empty and exit if not
		if len(os.listdir( path_to_AN_folder + category )) != 0:
			print "Folder " + path_to_AN_folder + "/" + category + " on hdfs is not empty.  Exiting because histogram files with same names will be overwritten."
			sys.exit()

		print "running command: ", command
		p = subprocess.Popen(command, shell=True)
		p.wait()

print "All done!"


# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/logs
# mv *7TeV*log /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/logs
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Electron_up
# mv *7TeV*plusElectron.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Electron_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Electron_down
# mv *7TeV*minusElectron.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Electron_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Muon_up
# mv *7TeV*plusMuon.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Muon_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Muon_down
# mv *7TeV*minusMuon.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/Muon_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/PU_up
# mv *7TeV*PU_71400mb.root  /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/PU_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/PU_down
# mv *7TeV*PU_64600mb.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/PU_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/BJet_up
# mv *7TeV*plusBjet.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/BJet_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/BJet_down
# mv *7TeV**minusBJet.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/BJet_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/LightJet_up
# mv *7TeV*plusLightJet.root /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/LightJet_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/LightJet_down
# 
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/JES_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/JES_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/JER_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/JER_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/PDFWeights
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV/central
# 
# 
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/logs
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/Electron_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/Electron_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/Muon_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/Muon_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/PU_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/PU_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/BJet_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/BJet_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/LightJet_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/LightJet_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/JES_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/JES_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/JER_up
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/JER_down
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/PDFWeights
# 
# mkdir /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/8TeV/central