#!/usr/bin/env python
from dps.config.summations_7TeV import sample_summations as sample_summations_7TeV
from dps.config.summations_8TeV import sample_summations as sample_summations_8TeV
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import make_folder_if_not_exists
from optparse import OptionParser

from dps.utils.file_utilities import merge_ROOT_files
import os
import sys
import subprocess

parser = OptionParser("Merge histogram files on DICE")
parser.add_option("-n", dest="jobNumber", default=-1, type='int',
                  help="Specify which job number to run")
parser.add_option("-c", dest="com", type='int',
                  help="Specify centre of mass energy")
parser.add_option("--listJobs", dest="listJobs", action='store_true', default=False,
                  help="Just list the jobs to run and the total number of jobs")
(options, _) = parser.parse_args()

if options.jobNumber < 0:
    print "Choose a job number >= 0"
    sys.exit()

if options.com != 7 and options.com != 8:
    print "Centre of mass must be 7 or 8 TeV"
    print "You've chosen",options.com
    sys.exit()


config = XSectionConfig(options.com)
sample_summations = None
if options.com == 7:
    sample_summations = sample_summations_7TeV 
elif options.com == 8:
    sample_summations = sample_summations_8TeV

#Can not output to DICE, and since we are now working with input files on /hdfs, need to find somewhere to output the merged files 
#this script creates

# first get current working directory
current_working_directory = os.getcwd()
path_to_AN_folder = config.path_to_files
# Where you want files to end up on hdfs
# Because you can't merge directly to hdfs at the moment,
# have to merge somewhere else then cp/mv/rsync file to hdfs
path_to_AN_folder_hdfs = path_to_AN_folder
# change path from /hdfs to current working directory
path_to_AN_folder = path_to_AN_folder.replace("/hdfs/TopQuarkGroup/results/histogramfiles", current_working_directory)

print path_to_AN_folder
print path_to_AN_folder_hdfs

# Make list of all samples to be merged
allJobs = []
for category in config.categories_and_prefixes.keys():
    for sample, input_samples in sample_summations.iteritems():
        # Only consider these samples
        if not sample in ['WJets', 'DYJets', 'VJets-matchingup',
                          'VJets-matchingdown', 'VJets-scaleup',
                          'VJets-scaledown','QCD_Electron', 
                          'QCD_Muon', 'VJets',
                          'SingleTop']: #
            continue
        # Only consider these samples for central
        if sample in ['WJets', 'DYJets', 'VJets-matchingup',
                      'VJets-matchingdown', 'VJets-scaleup',
                      'VJets-scaledown']:
                      if category is not 'central':
                        continue
        allJobs.append( [category, sample, input_samples])


if options.listJobs:
  print allJobs
  print 'Total number of jobs for centre of mass ',options.com,':',len(allJobs)
  sys.exit()
  
if options.jobNumber > (len(allJobs)-1):
    print 'Job number',options.jobNumber,'too large'
    print 'Total number of possible jobs :',len(allJobs)
    print 'Largest possible job number : ',len(allJobs)-1
    sys.exit()

jobNumber = options.jobNumber
job = allJobs[jobNumber]
category = job[0]
sample = job[1]
input_samples = job[2]

# print 'Test with :',sample, category, input_samples

# Make folder
make_folder_if_not_exists( path_to_AN_folder + "/" + category)

current_working_directory = os.getcwd()  #find current working directory
output_file_hdfs = config.general_category_templates[category] % sample
output_file = output_file_hdfs.replace("/hdfs/TopQuarkGroup/results/histogramfiles", current_working_directory)
input_files = [config.general_category_templates[category] % input_sample for input_sample in input_samples]

if not os.path.exists( output_file ):
    merge_ROOT_files( input_files, output_file, compression = 7, waitToFinish=True )
    print "merging ", sample
else :
    print 'Not merging ',sample,'as',output_file,'already exists'

# Now move output file to hdfs
# Check if file already exists on hdfs
if os.path.exists( output_file_hdfs ):
  print "Output file on hdfs already exists.  Removing and replacing with new version."
  command = 'hadoop fs -rm -skipTrash ' + output_file_hdfs.split('/hdfs')[-1]
  p = subprocess.Popen(command, shell=True)
  p.wait()

print '\nStarting rsync'
output_log_file = output_file.replace(".root", ".log")
command = 'rsync --verbose  --progress --stats --compress --recursive --times --update %s %s >> %s' % (output_file,output_file_hdfs,output_log_file)
print command
p = subprocess.Popen(command, shell=True)
p.wait()

print 'ALL DONE!'
