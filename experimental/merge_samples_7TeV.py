from config.summations_7TeV import sample_summations
import config.cross_section_measurement_7TeV as measurement_config

from tools.file_utilities import merge_ROOT_files
import os
import subprocess
import time

new_files = []

#merge generator systematics histogram files and unfolding ntuples
for sample, input_samples in sample_summations.iteritems():
    if not sample in ['WJets', 'VJets_matchingup', 'VJets_matchingdown', 'VJets_scaleup', 'VJets_scaledown', 'unfolding_merged', 'unfolding_TTJets_7TeV_mcatnlo', 'unfolding_TTJets_7TeV_powheg', 'unfolding_TTJets_7TeV_matchingup', 'unfolding_TTJets_7TeV_matchingdown', 'unfolding_TTJets_7TeV_scaleup', 'unfolding_TTJets_7TeV_scaledown']: # No 'DYJets' because there is only one inclusive DYJets dataset
        continue
    print "Merging"
    if 'unfolding' in sample:
        output_file = measurement_config.unfolding_output_general_template % sample
        input_files = [measurement_config.unfolding_input_templates[sample] % input_sample for input_sample in input_samples]
    else:
        output_file = measurement_config.central_general_template % sample
        input_files = [measurement_config.central_general_template % input_sample for input_sample in input_samples]
    
    print output_file
    for input_file in input_files:
        print input_file
    
    if not os.path.exists(output_file):
        merge_ROOT_files(input_files, output_file, compression = 7)
        new_files.append(output_file)
    print '='*120
    
    #if 8 concurrent processes, wait until they are finished before starting the next set to avoid overloading the machine
    number_of_running_hadds = int(subprocess.check_output("ps ax | grep 'hadd' | wc -l", shell=True))
    while number_of_running_hadds >= 10:
        time.sleep(30) #sleep for 30 seconds
        number_of_running_hadds = int(subprocess.check_output("ps ax | grep 'hadd' | wc -l", shell=True))


#merge all other histogram files
for category in measurement_config.categories_and_prefixes.keys():
    for sample, input_samples in sample_summations.iteritems():
        if not sample in ['VJets', 'SingleTop', 'QCD_Electron']: # No QCD_Muon because there is only one MuEnriched QCD dataset
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
        number_of_running_hadds = int(subprocess.check_output("ps ax | grep 'hadd' | wc -l", shell=True))
        while number_of_running_hadds >= 10:
            time.sleep(30) #sleep for 30 seconds
            number_of_running_hadds = int(subprocess.check_output("ps ax | grep 'hadd' | wc -l", shell=True))
        
print '='*120
print 'Created:'
for f in new_files:
    print f
