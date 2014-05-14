from config.summations_7TeV import sample_summations
import config.cross_section_measurement_7TeV as measurement_config

from tools.file_utilities import merge_ROOT_files
import os
import subprocess
import time

new_files = []

#merge generator systematics histogram files
for sample, input_samples in sample_summations.iteritems():
    if not sample in ['WJets', 'VJets-matchingup', 'VJets-matchingdown', 'VJets-scaleup', 'VJets-scaledown']: # No 'DYJets' because there is only one inclusive DYJets dataset
        continue
    print "Merging"
    output_file = measurement_config.central_general_template % sample
    input_files = [measurement_config.central_general_template % input_sample for input_sample in input_samples]
    
    print output_file
    for input_file in input_files:
        print input_file
    
    if not os.path.exists(output_file):
        merge_ROOT_files(input_files, output_file, compression = 7)
        new_files.append(output_file)
    print '='*120
    
    # if 8 concurrent processes, wait until they are finished before starting the next set to avoid overloading the machine
    while ( int( subprocess.check_output( "ps ax | grep 'hadd' | wc -l", shell = True ) ) - 2 ) >= 8:
        time.sleep( 30 )  # sleep for 30 seconds


#merge all other histogram files
for category in measurement_config.categories_and_prefixes.keys():
    for sample, input_samples in sample_summations.iteritems():
        if not sample in ['VJets', 'SingleTop', 'QCD-Electron']: # No QCD_Muon because there is only one MuEnriched QCD dataset
            continue
        print "Merging"
        output_file = measurement_config.general_category_templates[category] % sample
        input_files = [measurement_config.general_category_templates[category] % input_sample for input_sample in input_samples]

        print output_file
        for input_file in input_files:
            print input_file
        
        if not os.path.exists(output_file):
            merge_ROOT_files(input_files, output_file, compression = 7)
            new_files.append(output_file)
        print '='*120
        
        #if 8 concurrent processes, wait until they are finished before starting the next set to avoid overloading the machine
        while ( int( subprocess.check_output( "ps ax | grep 'hadd' | wc -l", shell = True ) ) - 2 ) >= 8:
            time.sleep( 30 )  # sleep for 30 seconds
        
print '='*120
print 'Created:'
for f in new_files:
    print f
