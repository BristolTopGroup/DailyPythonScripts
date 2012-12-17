import os
import re
import time
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
	parser.add_option("-l", "--numberlumis", dest="total_number_of_lumis", default=-1,
			  help="specify total number of lumis to run over; default is -1.")
	parser.add_option("-j", "--numberjobs", dest="number_of_jobs", default=1000,
			  help="specify total number of jobs to be created; default is 1000.")
	parser.add_option("-f", "--lumi_mask", dest="lumi_mask", default=None,
			  help="specify lumi_mask if running on data; default is 'None'.")
	parser.add_option("-d", "--useData", dest="useData", default=0,
                	  help="specify 0 for monte carlo or 1 for data")
	parser.add_option("-t", "--dataType", dest="dataType", default='TTJets',
                	  help="specify dataType; default is 'TTJets'.") 
	parser.add_option("-s", "--skim", dest="skim", default='LeptonPlus3Jets',
                	  help="specify skim; default is 'LeptonPlus3Jets'.")

	parser.add_option("-m", "--mail", dest="email", default=None,
			  help="specify email address if notifications are desired; default is None.")
	
	parser.add_option("-w", "--whiteList", dest="whiteList", default=None,
			  help="specify sites to which you wish to submit jobs (if desired) separated by commas; default is None. If you wish to create a white list of only the sites where your data is present, enter the string '1'.")
	parser.add_option("-b", "--blackList", dest="blackList", default=None,
                	  help="specify sites to which you do not wish to submit jobs (if desired) separated by commas; default is None.")

	(options, args) = parser.parse_args()

	#make sure that a datasetpath has been entered.
	if options.datasetpath == None:
	    print 'Please enter a datasetPath.'

	#Use das_client.py to get nFiles and nEvents for the dataset in question by making a DAS query.
	dasData = commands.getstatusoutput("../tools/das_client.py --query=dataset=\"" + options.datasetpath + " | grep dataset.name, dataset.nfiles, dataset.nevents \" --verbose=1")
	dasData = dasData[1].split("\n")
	dasData = dasData[3].split(" ")
	nFiles=dasData[1]
	nEvents=dasData[2]

	#set up white list and black list arrays
	#whiteList
	if options.whiteList == '1':
		sites = commands.getstatusoutput("./das_client.py --query=\"site dataset=" + options.datasetpath + "\"")
		sites = sites[1].split("\n")
		sites = sites[3:]
	elif options.whiteList:
		sites = options.whiteList.split(",")
	elif whiteList == None:
		print "no whiteList."
	else:
		print "whiteList format error."
	#blackList
	if options.blackList:
		blackList = options.blackList.split(",")
	elif options.blackList == None:
		print "no blackList."
	else:
		print "blackList format error."

	#Set up configuration file to write to.
	if int(options.useData) == 1:
		filepath = "data2012/" + options.version
		if not os.path.exists(filepath):
			os.makedirs(filepath)
	if int(options.useData) == 0:
		filepath = "defaultMC_Summer12/" + options.version
		if not os.path.exists(filepath):
			os.makedirs(filepath)

	datasetPath = options.datasetpath.replace("/", "_")
	filename = datasetPath[1:]
	filename = filename + "_nTuple_" + options.version + "_" + options.skim + ".cfg"
	configFile = open(filepath + "/" + filename, "w")

	#Set up directory name both for local and remote		
	if int(options.useData) == 1:
		directory = datasetPath[1:] + "_nTuple_" + options.version + "_GoldenJSON_" + options.skim + "_final"
	elif int(options.useData) == 0:
	        directory = datasetPath[1:] + "_nTuple_" + options.version + "_" + options.skim + "_final"
	else:
		print "useData value entered is not 0 (monte carlo) or 1 (data). Current value: ", options.useData

	#Write to configuration file
	print "starting writing configuration file " + filename
	configFile.write("[CRAB]\n")
	configFile.write("jobtype = " + options.jobtype + "\n")
	configFile.write("scheduler = " + options.scheduler + "\n")
	configFile.write("use_server = " + options.use_server + "\n\n")

	configFile.write("[CMSSW]\n")
	configFile.write("#nEvents = " + nEvents + "\n")
	configFile.write("#nFiles = " + nFiles + "\n")
	configFile.write("datasetpath = " + options.datasetpath + "\n")
	configFile.write("pset = " + options.pset + "\n")
	if int(options.useData) == 1:
		configFile.write("total_number_of_lumis = " + str(options.total_number_of_lumis) + "\n")
	elif int(options.useData) == 0:
		configFile.write("total_number_of_events = " + str(options.total_number_of_events) + "\n")
	configFile.write("number_of_jobs = " + str(options.number_of_jobs) + "\n")
	configFile.write("get_edm_output = 1\n")
	if int(options.useData) == 1:
		if options.lumi_mask == None:
			print "Please specify a JSON file."
		else:
			configFile.write("lumi_mask = BristolAnalysis/NTupleTools/data/CertifiedJSONs/" + options.lumi_mask + "\n")	
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
	if options.whiteList != "None":
		configFile.write("se_white_list=")
		for i in range(len(sites)):
			configFile.write(sites[i])
			if i != len(sites)-1:
				configFile.write(", ")
			else:
				configFile.write("\n")
	if options.blackList !="None":
		configFile.write("se_black_list=")
		for i in range(len(blackList)):
			configFile.write(blackList[i])
			if i != len(blackList)-1:
				configFile.write(", ")
			else:
				configFile.write("\n")

	configFile.close()
	print filename, "saved."
#
# main
#
if __name__ == '__main__':
    main()
