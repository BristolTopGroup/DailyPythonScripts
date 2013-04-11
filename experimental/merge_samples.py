from config.summations import sample_summations
import config.cross_section_measurement_7TeV as measurement_config

from tools.file_utilities import merge_ROOT_files
import os

new_files = []

for category in measurement_config.categories_and_prefixes.keys():
    for sample, input_samples in sample_summations.iteritems():
        if not sample in ['VJets', 'SingleTop']:
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