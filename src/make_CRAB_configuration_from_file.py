#A script for using CRABConfigs.py to write CRAB configuration filesfor datasets specified in datasetInput.txt.
#Best to run this script in the configurations folder of NTupleTools, so that the created CRAB configuration files go into the correct locations/folders.
#With current filepaths (as commited), make_CRAB_configuration.py should be in the same folder as this 
#make_CRAB_configuration_from_file.py script, dataset_input.py should be in the data folder and das_client should be in the ../tools folder relative to 
#this script.
#Simply run with: python make_CRAB_configuration_from_file.py
import commands as commands

#open datasetInput.txt for reading
filename = 'data/dataset_input.txt'
file=open(filename, 'rU')

#loop through lines and create configuration file for each line
x = file.readlines()

for line in x[1:]:
	line = line.strip()
	line = line.split()
	if len(line) == 16:
#		print len(line)
#		print line
		commands.getstatusoutput("python make_CRAB_configuration.py --jobtype=" + line[0] + " --scheduler=" + line[1] + " --use_server=" + line[2] + " --version=" + line[3] + " --datasetpath=" + line[4] + " --pset=" + line[5] + " --numberevents=" + line[6] + " --numberlumis=" + line[7] + " --numberjobs=" + line[8] + " --lumi_mask=" + line[9] + " --useData=" + line[10] + " --dataType=" + line[11] + " --skim=" + line[12] + " --mail=" + line[13] + " --whiteList=" + line[14] + " --blackList=" + line[15])
