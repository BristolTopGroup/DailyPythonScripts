from __future__ import division
from argparse import ArgumentParser
from dps.utils.logger import log
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import write_data_to_JSON, get_files_in_path, make_folder_if_not_exists, read_data_from_JSON
from dps.utils.hist_utilities import clean_control_region, hist_to_value_error_tuplelist, fix_overflow
from dps.utils.Calculation import combine_complex_results
from dps.utils.measurement2 import Measurement
from dps.utils.ROOT_utils import set_root_defaults

# define logger for this module
mylog = log["01b_get_ttjet_normalisation"]

def main():
    '''
    1 - Create config file reading in templates
    2 - Create 'jobs' for each config
    3 - Read in config
    4 - Differentiate between Syst and Central
    5 - Work in QCD from data
    '''
    results = {}

    # config file template
    input_template = 'TESTING/config/measurements/background_subtraction/{com}TeV/{ch}/{var}/{ps}/'

    if args.visiblePS:
        ps = 'VisiblePS'
    else:
        ps = 'FullPS'

    for ch in ['electron', 'muon']:
        for var in measurement_config.variables:
            if args.variable not in var: continue

            # Create measurement_filepath
            measurement_filepath = input_template.format(
                com = args.CoM,
                ch = ch,
                var = var,
                ps = ps,
            )
            
            # Get all config files in measurement_filepath
            measurement_files = get_files_in_path(measurement_filepath, file_ending='.json')

            for f in sorted(measurement_files):
                print('Processing file ' + f)
                # Read in Measurement JSON
                config = read_data_from_JSON(f)

                # Create Measurement Class using JSON
                measurement = Measurement(config)
                measurement.calculate_normalisation()
                measurement.save(ps)
                # break
    return

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument("-v", "--variable", dest="variable", default='HT',
                            help="set the variable to analyse (MET, HT, ST, MT, WPT). Default is MET.")
    parser.add_argument("-c", "--centre-of-mass-energy", dest="CoM", default=13, type=int,
                            help="set the centre of mass energy for analysis. Default = 13 [TeV]")
    parser.add_argument('--visiblePS', dest="visiblePS", action="store_true",
                            help="Unfold to visible phase space")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    set_root_defaults()
    args = parse_arguments()
    measurement_config = XSectionConfig(args.CoM)
    main()



