import os as os
import sys as sys
import re as re
import ROOT as ROOT
from optparse import OptionParser
import commands as commands
import fnmatch as fnmatch
import glob as glob

"Main function."
def main():
	"Main Function"
	ROOT.gROOT.SetBatch(True)

	parser = OptionParser("Script to check progress of CRAB jobs in creating nTuples. Run as: python check_CRAB_jobs.py -p projectFolder -n numberOfJobs >&check.log &")
        parser.add_option("-p", "--projectFolder", dest="projectFolder",
                help="specify project")
	parser.add_option("-n", "--numberOfJobs", dest="numberOfJobs",
		help="specify project")

        (options, args) = parser.parse_args()

	#make sure the project option has been specified
	if not options.projectFolder:
		parser.error('Please enter a project folder as the -p option: /gpfs_phys/storm/cms/user/...')

	#normalise the projectFolder filepath and add a "/" at the end
	projectFolder = os.path.normpath(options.projectFolder) + os.sep

	#list the items in the CRAB output folder on the Bristol Storage Element.
	storageElementList=glob.glob(projectFolder + "*.root")
	if storageElementList:
		pass
	else:
		print "Location Error: Specified project folder does not exist on the Bristol Storage Element, signifying that the CRAB job has probably not started running yet or you forgot to include the full path /gpfs_storm/cms/user/..."
		sys.exit()

	#The following section has been commented out because if it is the first time this script is being run in a session, a grid password will be needed which will cause the script
	#to not be able to finish. Since the only purpose of this following CRAB command is to obtain the number of jobs, for the time being the number of jobs has been entered as an option to
	#the script which should be manually entered by the user.

	#get the status of the crab jobs and extract the number of output files expected on the Bristol Storage Element.
#	projectFolder = options.projectFolder.split("/")[6]
#	status = commands.getstatusoutput("crab -status -c " + projectFolder)
#	statusFormatted = status[1].split("\n")
#	for line in statusFormatted:
#		if "crab:" in line and "Total Jobs" in line:
#			words = line.split()
#			numberOfJobs = int(words[1])


	#Now, check that all job root files are present in Bristol Storage Element folder:

	missingOrBroken = []
	presentJobList = []

	#make list of all the job numbers which should be present.
	jobList = range(1,int(options.numberOfJobs)+1)

	#try opening all files in Bristol Storage Element folder and add to missing list if they cannot be opened.
	for file in storageElementList:
		#make list of all jobs numbers in the Bristol Storage Element folder
		jobNumber = int((re.split('[\W+,_]',file))[-4])
		presentJobList.append(jobNumber)
		try:
			rootFile = ROOT.TFile.Open(file)
			rootFile.Close()
		except:
			print "Adding Job Number", jobNumber, "to missingOrBroken list."
			missingOrBroken.append(jobNumber)
	
	#now add any absent files to the missing list:
	for job in jobList:
		if job not in presentJobList:
			print "Adding Job Number", job, "to missingOrBroken list."
			missingOrBroken.append(job)

	print "\n The following", len(missingOrBroken), "job numbers could not be found in the Bristol Storage Element folder:"
	print str(missingOrBroken).replace(" ", "")

if __name__ == '__main__':
	main()
