from dps.config.summations_7TeV import sample_summations
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import make_folder_if_not_exists

from dps.utils.file_utilities import merge_ROOT_files
import os
import subprocess
import time

new_files = []

config_7TeV = XSectionConfig(7)

#Can not output to DICE, and since we are now working with input files on /hdfs, need to find somewhere to output the merged files 
#this script creates
#So, create folders in working directory with structure: AN-XX-XXX_Xth_draft/XTeV/<central/BJet_up/Light_Jet_up/etc. for all categories>
#NOTE: YOU WILL THEN HAVE TO MOVE THESE MERGED FILES MANUALLY TO THE APPROPRIATE LOCATION IN /hdfs/TopQuarkGroup/results/histogramfiles/...

# first get current working directory
current_working_directory = os.getcwd()
path_to_AN_folder = config_7TeV.path_to_files
# change path from /hdfs to current working directory
path_to_AN_folder = path_to_AN_folder.replace("/hdfs/TopQuarkGroup/results/histogramfiles", current_working_directory)
#loop through all categories (e.g. central, BJet_up, LightJet_up, etc....) and make folder
for category in config_7TeV.categories_and_prefixes.keys():
    make_folder_if_not_exists( path_to_AN_folder + "/" + category)

# merge generator systematics histogram files
for sample, input_samples in sample_summations.iteritems():
    if not sample in ['WJets', 'VJets-matchingup',
                      'VJets-matchingdown', 'VJets-scaleup',
                      'VJets-scaledown']: # No 'DYJets' because there is only one inclusive DYJets dataset
        continue
    print "Merging"
    current_working_directory = os.getcwd()  #find current working directory
    output_file = config_7TeV.central_general_template % sample
    output_file = output_file.replace("/hdfs/TopQuarkGroup/results/histogramfiles", current_working_directory)
    input_files = [config_7TeV.central_general_template % input_sample for input_sample in input_samples]
    
    print output_file
    for input_file in input_files:
        print input_file
    
    if not os.path.exists( output_file ):
        merge_ROOT_files( input_files, output_file, compression = 7 )
        print "merging ", sample
        new_files.append( output_file )
    print '=' * 120
    
    # if 8 concurrent processes, wait until they are finished before starting the next set to avoid overloading the machine
    while ( int( subprocess.check_output( "ps ax | grep 'hadd' | wc -l", shell = True ) ) - 2 ) >= 8:
        time.sleep( 30 )  # sleep for 30 seconds

# merge all other histogram files
for category in config_7TeV.categories_and_prefixes.keys():
    for sample, input_samples in sample_summations.iteritems():
        if not sample in ['QCD_Electron', 'QCD_Muon', 'VJets', 
                          'SingleTop']: #
            continue
        print "Merging"
        current_working_directory = os.getcwd()  #find current working directory
        output_file = config_7TeV.general_category_templates[category] % sample
        output_file = output_file.replace("/hdfs/TopQuarkGroup/results/histogramfiles", current_working_directory)
        input_files = [config_7TeV.general_category_templates[category] % input_sample for input_sample in input_samples]

        print output_file
        for input_file in input_files:
            print input_file
        
        if not os.path.exists( output_file ):
            merge_ROOT_files( input_files, output_file, compression = 7 )
            print "merging ", category, " ", sample
            new_files.append( output_file )
        print '='*120
        
        # if 8 concurrent processes, wait until they are finished before starting the next set to avoid overloading the machine
        while ( int( subprocess.check_output( "ps ax | grep 'hadd' | wc -l", shell = True ) ) - 2 ) >= 8:
            time.sleep( 30 )  # sleep for 30 seconds
        
print '='*120
print 'Created:'
for f in new_files:
    print f
