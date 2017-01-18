import os as os
import sys as sys
import re as re
from dps.utils.ROOT_utils import set_root_defaults
from optparse import OptionParser
import glob as glob
from rootpy.io import File

"Main function."
def main():
	"Main Function"
	set_root_defaults()

	parser = OptionParser("Script to check progress of CRAB jobs in creating nTuples. Run as: python check_CRAB_jobs.py -p projectFolder -n numberOfJobs >&check.log &")
	parser.add_option("-p", "--projectFolder", dest="projectFolder", help="specify project")
	parser.add_option("-n", "--numberOfJobs", dest="numberOfJobs",
		help="specify project")

	(options, _) = parser.parse_args()

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

	missingOrBrokenTemp = []
	missingOrBroken = []
	goodFilesTemp = []
	goodFiles = []
	presentJobList = []
	duplicatesToDelete = []

	#make list of all the job numbers which should be present.
	jobList = range(1,int(options.numberOfJobs)+1)

	#try opening all files in Bristol Storage Element folder and add to missing list if they cannot be opened.
	for f in storageElementList:
		#make list of all jobs numbers in the Bristol Storage Element folder
		jobNumber = int((re.split('[\W+,_]',f))[-4])
		presentJobList.append(jobNumber)

		#check if files are corrupt or not
		try:
			rootFile = File(f)
			rootFile.Close()
		except:
			print "Adding Job Number", jobNumber, "to missingOrBroken list because file is corrupted."
			missingOrBrokenTemp.append(jobNumber)
		else:
			goodFilesTemp.append(jobNumber)

	#now add any absent files to the missing list:
	for job in jobList:
		if job not in presentJobList:
			print "Adding Job Number", job, "to missingOrBroken list because it doesn't exist on the Storage Element."
			missingOrBrokenTemp.append(job)

	#Remove any job numbers from missingOrBroken which appear in both goodFiles and missingOrBroken lists
	for job in missingOrBrokenTemp:
		if job not in goodFilesTemp:
			missingOrBroken.append(job)
		else:
			print "Removing", job, "from missingOrBroken list because there is at least one duplicate good output file."

	#Remove any job numbers from goodFiles which appear more than once in goodFiles
	for job in goodFilesTemp:
		if job not in goodFiles:
			goodFiles.append(job)
		else:
			duplicatesToDelete.append(job)

	print "\n The following", len(goodFiles), "good output files were found in the Bristol Storage Element folder:"
	print str(goodFiles).replace(" ", "")  
	print "\n The following", len(duplicatesToDelete), "job numbers have multiple good files on the Bristol Storage Element folder which can be deleted:"
	print str(duplicatesToDelete).replace(" ", "")
	print "\n The following", len(missingOrBroken), "job numbers could not be found in the Bristol Storage Element folder:"
	print str(missingOrBroken).replace(" ", "")

if __name__ == '__main__':
	main()
