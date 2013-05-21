from config.summations_8TeV import sample_summations
import config.cross_section_measurement_8TeV as measurement_config

from tools.file_utilities import merge_ROOT_files
import os

new_files = []

#merge generator systematics histogram files and unfolding ntuples
for sample, input_samples in sample_summations.iteritems():
    if not sample in ['QCD_Electron', 'WJets', 'DYJets', 'VJets_matchingup', 'VJets_matchingdown', 'VJets_scaleup', 'VJets_scaledown', 'unfolding_merged', 'unfolding_TTJets_8TeV_mcatnlo', 'unfolding_TTJets_8TeV_powheg', 'unfolding_TTJets_8TeV_matchingup', 'unfolding_TTJets_8TeV_matchingdown', 'unfolding_TTJets_8TeV_scaleup', 'unfolding_TTJets_8TeV_scaledown']: #
        continue
    print "Merging"
    if 'unfolding' in sample:
#	print 'unfolding in sample'
        output_file = measurement_config.unfolding_output_general_template % sample
	input_files = [measurement_config.unfolding_input_templates[sample] % input_sample for input_sample in input_samples]
    else: #if any (generator_systematic in sample for generator_systematic in measurement_config.generator_systematics):
#        print 'generator systematic in sample'
	output_file = measurement_config.central_general_template % sample
        input_files = [measurement_config.central_general_template % input_sample for input_sample in input_samples]

    print output_file
    for input_file in input_files:
        print input_file
    if not os.path.exists(output_file):
        merge_ROOT_files(input_files, output_file, compression = 7)
        new_files.append(output_file)
    print '='*120

#merge all other histogram files
for category in measurement_config.categories_and_prefixes.keys():
    for sample, input_samples in sample_summations.iteritems():
        if not sample in ['VJets', 'QCD_Muon', 'SingleTop']: #
            continue
        print "Merging"
        output_file = measurement_config.general_category_templates[category] % sample
        print output_file
        input_files = [measurement_config.general_category_templates[category] % input_sample for input_sample in input_samples]
        for input_file in input_files:
            print input_file
        if not os.path.exists(output_file):
            merge_ROOT_files(input_files, output_file, compression = 7)
            new_files.append(output_file)
        print '='*120

print '='*120
print 'Created:'
for f in new_files:
    print f
