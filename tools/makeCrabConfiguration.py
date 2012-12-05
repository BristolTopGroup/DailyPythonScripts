import os
import re
import time
import json
import urllib
import urllib2
import httplib
from optparse import OptionParser
import subprocess as subprocess
import commands

def main():
        "Main function."
        parser = OptionParser()

	parser.add_option("-T", "--jobtype", dest="jobtype", default='cmssw',
                	  help="specify jobtype")
	parser.add_option("-g", "--scheduler", dest="scheduler", default='glidein',
                	  help="specify scheduler; default is 'glidein'.")
	parser.add_option("-u", "--use_server", dest="use_server", default='1',
                	  help="specify use_server variable; default is '1'.")
	
	parser.add_option("-v", "--version", dest="version", default='v9a',
	                  help="specify nTuple version in the form 'vXx'; default is 'v9a'.")
	parser.add_option("-P", "--datasetpath", dest="datasetpath", default=None,
                	  help="specify datasetpath; default is 'None'.")
	parser.add_option("-p", "--pset", dest="pset", default='BristolAnalysis/nTupleTools/test/makeTuples_cfg.py',
                	  help="specify path to pset; default is 'BristolAnalysis/nTupleTools/test/makeTuples_cfg.py'.")
	parser.add_option("-e", "--numberevents", dest="total_number_of_events", default=-1,
			  help="specify total number of events to run over; default is -1.")
	parser.add_option("-j", "--numberjobs", dest="number_of_jobs", default=1000,
			  help="specify total number of jobs to be created; default is 1000.")
	parser.add_option("-d", "--useData", dest="useData", default=0,
                	  help="specify 0 for monte carlo or 1 for data")
	parser.add_option("-t", "--dataType", dest="dataType", default='TTJets',
                	  help="specify dataType; default is 'TTJets'.") 
	parser.add_option("-s", "--skim", dest="skim", default='LeptonPlus3Jets',
                	  help="specify skim; default is 'LeptonPlus3Jets'.")

	parser.add_option("-m", "--mail", dest="email", default=None,
			  help="specify email address if notifications are desired; default is None.")
	
	parser.add_option("-w", "--whiteList", dest="whiteList", default=None,
			  help="specify sites to which you wish to submit jobs (if desired) in the form of an array of strings; default is None. If you wish to create a white list of only the sites where your data is present, enter 1.")
	parser.add_option("-b", "--blacklist", dest="blackList", default=None,
                	  help="specify sites to which you do not wish to submit jobs (if desired) in the form of an array of strings; default is None.")


	#parser.add_option("-b", "--datasetpath", dest="datasetPath", default='None',
	#                  help="specify datasetPath; default is 'None'.")

	(options, args) = parser.parse_args()

	if options.datasetpath == None:
	    print 'Please enter a datasetPath.'

	#Use das_client.py to get nFiles and nEvents for the dataset in question by making a DAS query.
	dasData = commands.getstatusoutput("./das_client.py --query=dataset=\"" + options.datasetpath + " | grep dataset.name, dataset.nfiles, dataset.nevents \" --verbose=1")
	dasData = dasData[1].split("\n")
	dasData = dasData[3].split(" ")
#        print dasData
	nFiles=dasData[1]
	nEvents=dasData[2]

	print options.whiteList
	print type(options.whiteList)
	if options.whiteList == '1':
		sites = commands.getstatusoutput("./das_client.py --query=\"site dataset=" + options.datasetpath + "\"")
		sites = sites[1].split("\n")
		sites = sites[3:]
		print sites

	#Set up configuration file to write to.
	datasetPath = options.datasetpath.replace("/", "_")
	filename = datasetPath[1:]
	filename = filename + "_nTuple_" + options.version + "_" + options.skim + ".cfg"
	configFile = open(filename, "w")

	#Set up directory name both for local and remote 
	if options.useData == 1:
		directory = datasetPath[1:] + "_nTuple_" + options.version + "_GoldenJSON_" + options.skim + "_final"
	elif options.useData == 0:
	        directory = datasetPath[1:] + "_nTuple_" + options.version + "_" + options.skim + "_final"
	else:
		print "useData value entered is not 0 (monte carlo) or 1 (data). Corrent value: ", options.useData

	#Write to configuration file
	configFile.write("[CRAB]\n")
	configFile.write("jobtype = " + options.jobtype + "\n")
	configFile.write("scheduler = " + options.scheduler + "\n")
	configFile.write("use_server = " + options.use_server + "\n\n")

	configFile.write("[CMSSW]\n")
	configFile.write("#nEvents = " + nEvents + "\n")
	configFile.write("#nFiles = " + nFiles + "\n")
	configFile.write("datasetpath = " + options.datasetpath + "\n")
	configFile.write("pset = " + options.pset + "\n")
	configFile.write("total_number_of_events = " + str(options.total_number_of_events) + "\n")
	configFile.write("number_of_jobs = " + str(options.number_of_jobs) + "\n")
	configFile.write("get_edm_output = 1\n")
	configFile.write("pycfg_params = useData=" + str(options.useData) + " dataType=" + options.dataType + " skim=" + options.skim + "\n\n")

	configFile.write("[USER]\n")
	configFile.write("additional_input_files = BristolAnalysis/NTupleTools/data/PileUp/*.root\n")
	configFile.write("return_data = 0\n")
	configFile.write("copy_data = 1\n")
	configFile.write("storage_element = T2_UK_SGrid_Bristol\n")
	configFile.write("user_remote_dir = " + directory + "\n")
	configFile.write("check_user_remote_dir = 0\n")
        configFile.write("ui_working_dir = " + directory + "\n")
	if options.email:
	        configFile.write("email = " + options.email + "\n\n")
	else:
		configFile.write("\n\n")

        configFile.write("[GRID]\n")
	if options.whiteList:
		configFile.write("se_white_list=")
		for i in range(len(sites)):
			configFile.write(sites[i])
			if i != len(sites)-1:
				configFile.write(", ")
			else:
				configFile.write("\n")
	if options.blackList:
		configFile.write("se_black_list=")
		for i in range(len(options.blackList)):
			configFile.write(options.blackList[i])
			if i != len(options.blackList)-1:
				configFile.write(", ")
			else:
				configFile.write("\n")

	configFile.close()

#
# main
#
if __name__ == '__main__':
    main()
