#!/usr/bin/env python
import os
import sys
import subprocess
import time

from tools.file_utilities import make_folder_if_not_exists
from tools.file_utilities import merge_ROOT_files
from optparse import OptionParser


parser = OptionParser("Merge histogram files on DICE")
parser.add_option("-n", dest="jobNumber", default=-1, type='int',
                  help="Specify which job number to run")
parser.add_option("-c", dest="com", type='int',
                  help="Specify centre of mass energy")
parser.add_option("-u", dest="user", type='string',
                  help="Specify username (for use in path to CRAB output files).")
parser.add_option("--listJobs", dest="listJobs", action='store_true', default=False,
                  help="Just list the jobs to run and the total number of jobs")
(options, _) = parser.parse_args()

if options.jobNumber < 0 and not options.listJobs:
    print "Choose a job number >=0."
    sys.exit()

if options.com != 7 and options.com != 8:
    print "Centre of mass must be 7 or 8 TeV"
    print "You've chosen",options.com
    sys.exit()
    

# first set up lists of jobs to be run

sample_to_BLT_filepath_dictionary_7TeV = {
                                "central":"TTJets_MSDecays_central_TuneZ2_7TeV-madgraph-tauola/crab_TTJets_central_7TeV_madgraph_BLTUnfold_NoSkim",
                                "scaleup": "TTJets_MSDecays_scaleup_TuneZ2star_7TeV-madgraph-tauola/crab_TTJets_scaleup_7TeV_madgraph_BLTUnfold_NoSkim",
                                "scaledown": "TTJets_MSDecays_scaledown_TuneZ2star_7TeV-madgraph-tauola/crab_TTJets_scaledown_7TeV_madgraph_BLTUnfold_NoSkim",
                                "matchingup": "TTJets_MSDecays_matchingup_7TeV-madgraph-tauola/crab_TTJets_matchingup_7TeV_madgraph_BLTUnfold_NoSkim",
                                "matchingdown": "TTJets_MSDecays_matchingdown_7TeV-madgraph-tauola/crab_TTJets_matchingdown_7TeV_madgraph_BLTUnfold_NoSkim",
                                "mass_173_5":"TTJets_MSDecays_mass173_5_7TeV-madgraph-tauola/crab_TTJets_mass_173_5_7TeV_madgraph_BLTUnfold_NoSkim",
                                "mass_169_5": "TTJets_MSDecays_mass169_5_7TeV-madgraph-tauola/crab_TTJets_mass_169_5_7TeV_madgraph_BLTUnfold_NoSkim",
                                 "powhegpythia": "TT_weights_CT10_TuneZ2_7TeV-powheg-pythia-tauola/crab_TT_CT10_TuneZ2_7TeV_powheg_pythia_tauola_BLTUnfold_NoSkim",
                                 "powhegherwig": "TT_weights_CT10_AUET2_7TeV-powheg-herwig/crab_TT_CT10_AUET2_7TeV_powheg_herwig_BLTUnfold_NoSkim_2"
                                }

sample_to_BLT_filepath_dictionary_8TeV = {
                                # "central":"TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/crab_TTJets_central_8TeV_madgraph_BLTUnfold_NoSkim",
                                # "scaleup": "TTJets_scaleup_TuneZ2star_8TeV-madgraph-tauola/crab_TTJets_scaleup_8TeV_madgraph_BLTUnfold_NoSkim",
                                # "scaledown": "TTJets_scaledown_TuneZ2star_8TeV-madgraph-tauola/crab_TTJets_scaledown_8TeV_madgraph_BLTUnfold_NoSkim",
                                # "matchingup": "TTJets_matchingup_TuneZ2star_8TeV-madgraph-tauola/crab_TTJets_matchingup_8TeV_madgraph_BLTUnfold_NoSkim",
                                # "matchingdown": "TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/crab_TTJets_matchingdown_8TeV_madgraph_BLTUnfold_NoSkim",
                                "mass_173_5":"TTJets_MSDecays_mass173_5_TuneZ2star_8TeV-madgraph-tauola/crab_TTJets_mass_173_5_8TeV_madgraph_BLTUnfold_NoSkim",
                                "mass_169_5": "TTJets_MSDecays_mass169_5_TuneZ2star_8TeV-madgraph-tauola/crab_TTJets_mass_169_5_8TeV_madgraph_BLTUnfold_NoSkim",
                                # "powhegpythia": "TT_CT10_TuneZ2star_8TeV-powheg-tauola/crab_TT_CT10_8TeV_powheg_tauola_BLTUnfold_NoSkim",
                                # "powhegherwig": "TT_CT10_AUET2_8TeV-powheg-herwig/crab_TT_CT10_AUET2_8TeV_powheg_herwig_BLTUnfold_NoSkim",
                                # "mcatnlo": "TT_8TeV-mcatnlo/crab_TT_8TeV_mcatnlo_BLTUnfold_NoSkim"
                                }

if options.com == 7:
    sample_names = sample_to_BLT_filepath_dictionary_7TeV
else:
    sample_names = sample_to_BLT_filepath_dictionary_8TeV

input_filepath_template = "/hdfs/dpm/phy.bris.ac.uk/home/cms/store/user/%s/%s/*/*/*.root"
output_filename_template = "unfolding_TTJets_%s_%sTeV.root"

#Make list of input filepaths and output filenames
allJobs = []

for sample_name in sample_names:
    input_filepath = input_filepath_template % (options.user, sample_names[sample_name])
    output_filename = output_filename_template % (sample_name, options.com)
    allJobs.append( [output_filename, [input_filepath]] )

if options.listJobs:
    print "[Output file: [Input files] ] : \n", allJobs
    print "Total number of jobs for centre of mass : ", len(allJobs)
    sys.exit()

if options.jobNumber > (len(allJobs)-1):
    print 'Job number',options.jobNumber,'too large'
    print 'Total number of possible jobs :',len(allJobs)
    print 'Largest possible job number : ',len(allJobs)-1
    sys.exit()
    
# setup for merging
jobNumber = options.jobNumber
job = allJobs[jobNumber]
input_files = job[1]
output_file = job[0]

# get current working directory
current_working_directory = os.getcwd()
# make_folder_if_not_exists(current_working_directory + "/mergeBLTUnfold/")

# if the output file doesn't already exist, merge!
print current_working_directory
#if not os.path.exists( current_working_directory + "/mergeBLTUnfold/" + output_file):
if not os.path.exists( current_working_directory + "/" + output_file):
    merge_ROOT_files(input_files, output_file, compression = 7, waitToFinish=True)
    print "Merging", output_file, "from", input_files
else:
    print "Not merging ", sample, "as", current_working_directory, "/", output_file, "already exists."
    
# HAVE NOT CHECKED IF THE FOLLOWING COMMENTED CODE WORKS.
# Now move output file to hdfs
# Check if file already exists on hdfs
output_file_hdfs = '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/temp/' + output_file
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
