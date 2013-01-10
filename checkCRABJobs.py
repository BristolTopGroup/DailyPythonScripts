import os as os
import sys as sys
import re as re
import ROOT as ROOT
from optparse import OptionParser
import commands as commands
import fnmatch as fnmatch

"Main function."
def main():
	parser = OptionParser("Script to check progress of CRAB jobs in creating nTuples. Run as: python checkCRABJobs.py -p projectFolder -n numberOfJobs >&check.log &")
        parser.add_option("-p", "--projectFolder", dest="projectFolder",
                help="specify project")
	parser.add_option("-n", "--numberOfJobs", dest="numberOfJobs",
		help="specify project")

        (options, args) = parser.parse_args()

	#make sure the project option has been specified
	if not options.projectFolder:
		parser.error('Please enter a project as an option (-p) e.g. /gpfs_phys/storm/user/...')

	#list the items in the CRAB output folder on the Bristol Storage Element.
	try:
		storageElementList=os.listdir(str(options.projectFolder))
	except OSError:
		print "Location Error: Specified project folder does not exist on the Bristol Storage Element, signifying that the CRAB job has probably not started running yet."
		sys.exit()

	#The following section has been commented out because if it is the first time this script is being run in a session, a grid password will be needed which will cause the script
	#to not be able to finish. Since the only purpose of this CRAB command is to obtain the number of jobs, for the time being the number of jobs has been entered as an option to
	#be manually entered by the user.

	#get the status of the crab jobs and extract the number of output files expected on the Bristol Storage Element.
#	projectFolder = options.projectFolder.split("/")[6]
#	status = commands.getstatusoutput("crab -status -c " + projectFolder)
#	statusFormatted = status[1].split("\n")
#	for line in statusFormatted:
#		if "crab:" in line and "Total Jobs" in line:
#			words = line.split()
#			numberOfJobs = int(words[1])

	#check that all job root files are present in Bristol Storage Element folder.
	missingOrBroken = []	
	jobs = range(1,int(options.numberOfJobs)+1)
	for job in jobs:
		for file in storageElementList:
			count = storageElementList.index(file)
			filenameSplit = re.split('[\W+,_]',file)
			if job == int(filenameSplit[-4]):
				#check that the file is openable and not corrupted.				
				try:
					rootFile = ROOT.TFile(options.projectFolder + "/" + file)					
					rootFileList = rootFile.ls()
					break
				except:
					print "Adding Job Number ", job, "to missing list."
					missingOrBroken.append(job)
			if count == len(storageElementList)-1:
				print "Adding Job Number ", job, "to missing list."
				missingOrBroken.append(job)

	print "The following", len(missingOrBroken), "job numbers could not be found in the Bristol Storage Element folder:"
	print missingOrBroken

if __name__ == '__main__':
	main()
