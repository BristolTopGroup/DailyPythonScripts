from __future__ import division
from argparse import ArgumentParser
from dps.utils.logger import log
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import get_files_in_path, read_data_from_JSON, make_folder_if_not_exists, get_filename_without_extension
from dps.utils.measurement import Measurement
from dps.utils.ROOT_utils import set_root_defaults
from dps.utils.pandas_utilities import file_to_df, dict_to_df, df_to_file

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
    input_template          = 'config/measurements/background_subtraction/{com}TeV/{ch}/{var}/{ps}/'
    output_folder_template  = 'data/normalisation/background_subtraction/{com}TeV/{var}/{ps}/{cat}/'

    ps = 'FullPS'
    if args.visiblePS:
        ps = 'VisiblePS'

    channels = [
        'electron', 
        'muon',
    ]

    for ch in channels:
        for var in measurement_config.variables:
            if not args.variable == var: continue
            qcd_transfer_factor = {}

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
                sample = get_filename_without_extension(f)

                # Read in Measurement JSON
                config = read_data_from_JSON(f)

                if 'electron' in ch:
                    # Create Measurement Class using JSON
                    electron_measurement = Measurement(config)
                    electron_measurement.calculate_normalisation()
                    electron_measurement.save(ps)
                    qcd_transfer_factor[sample] = [electron_measurement.t_factor]

                elif 'muon' in ch:
                    # Create Measurement Class using JSON
                    muon_measurement = Measurement(config)
                    muon_measurement.calculate_normalisation()
                    muon_measurement.save(ps)
                    qcd_transfer_factor[sample] = [muon_measurement.t_factor]

            output_folder = output_folder_template.format(
                com = args.CoM,  var = var,
                ps  = ps,   cat = 'central',
            )
            store_transfer_factor(qcd_transfer_factor, output_folder, ch)
    return

def store_transfer_factor(tf, output_file, channel):
    make_folder_if_not_exists(output_file)
    f = output_file+'table_of_transfer_factors_'+channel+'.txt'
    df = dict_to_df(tf)
    df_to_file(f, df)
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




