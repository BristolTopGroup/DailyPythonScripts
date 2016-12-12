from __future__ import division
from argparse import ArgumentParser
from dps.utils.logger import log
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import get_files_in_path, read_data_from_JSON
from dps.utils.measurement2 import Measurement
from dps.utils.ROOT_utils import set_root_defaults

# define logger for this module
mylog = log["01b_get_ttjet_normalisation"]

def main():
    '''
    1 - Read Config file for normalisation measurement
    2 - Run measurement
    3 - Combine measurement before unfolding
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
                if args.test:
                    if 'central' not in f: continue
                print('Processing file ' + f)
                # Read in Measurement JSON
                config = read_data_from_JSON(f)

                if 'electron' in ch:
                    # Create Measurement Class using JSON
                    electron_measurement = Measurement(config)
                    electron_measurement.calculate_normalisation()
                    electron_measurement.save(ps)
                elif 'muon' in ch:
                    # Create Measurement Class using JSON
                    muon_measurement = Measurement(config)
                    muon_measurement.calculate_normalisation()
                    muon_measurement.save(ps)
                # break

    # Combining the channels before unfolding
    combined_measurement = electron_measurement
    combined_measurement.combine(muon_measurement)
    combined_measurement.save(ps)
    return

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument("-v", "--variable", dest="variable", default='HT',
                            help="set the variable to analyse (MET, HT, ST, MT, WPT). Default is MET.")
    parser.add_argument("-c", "--centre-of-mass-energy", dest="CoM", default=13, type=int,
                            help="set the centre of mass energy for analysis. Default = 13 [TeV]")
    parser.add_argument('--visiblePS', dest="visiblePS", action="store_true",
                            help="Unfold to visible phase space")
    parser.add_argument('--test', dest="test", action="store_true",
                            help="Unfold to visible phase space")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    set_root_defaults()
    args = parse_arguments()
    measurement_config = XSectionConfig(args.CoM)
    main()



