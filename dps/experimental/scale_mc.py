'''
Created on 15 Jan 2013

@author: kreczko

Scale the MC to the correct x-section.
Take the cross sections and processed events from config/dataset_info*
Assume that the first part of the name is the process in question (and implement exceptions)
'''
from argparse import ArgumentParser
from dps.utils.file_utilities import get_process_from_file
from dps.config.dataset_info_7TeV import dataset_info as dataset_info_7TeV
from dps.config.dataset_info_8TeV import dataset_info as dataset_info_8TeV

def scale_file(file_in_path):
    process_name = get_process_from_file(file_in_path)
    

if __name__ == "__main__":
    from rootpy.logger import logging
    parser = ArgumentParser(description='Scales all MC to a set luminosity')
    parser.add_argument('input_folder', metavar='input_folder', 
                        help="input folder for histogram files to be scaled")
    parser.add_argument('output_folder', metavar='output_folder', 
                        help="output folder for the scaled histogram files to be written to.",
                        default = '', nargs='?')
    parser.add_argument('--lumi', metavar='luminosity', 
                        help="Luminosity the histograms will be scaled to",
                        type=float)
    parser.add_argument('--centre-of-mass-energy', metavar='centre_of_mass_energy', 
                        help="Centre of mass energy the cross sections should be read for.",
                        type=float)
    parser.add_argument('--debug',
                        help="Turn on debug output",
                        action='store_true')
    args = parser.parse_args()
    
    dataset_info = None
    if args.debug:
        logging.basicConfig()#fancy logger for better error messages
    else:
        logging.basicConfig(level=logging.WARNING)#turn debug off
    if args.centre_of_mass_energy == 7:
        dataset_info = dataset_info_7TeV
    elif args.centre_of_mass_energy == 8:
        dataset_info = dataset_info_8TeV
