'''
Created on 11 Dec 2012
@author: kreczko

This script creates toy MC for the unfolding tests.
It:
    1) reads the existing unfolding histograms
    2) creates a new set by changing the number of events in each bin according
         to a Possoinian
    3) creates scale factors for each bin
    4) reads the BLT unfolding ntuple (unbinned unfolding data)
    5) creates a new set (truth, response, measured) based on 3) and 4)
This script uses around 300 MB RAM per instance for n=10000
'''
from optparse import OptionParser
from tools.toy_mc import generate_toy_MC_from_distribution,\
 generate_toy_MC_from_2Ddistribution
from tools.Unfolding import get_unfold_histogram_tuple
from tools.file_utilities import make_folder_if_not_exists
from rootpy.io import File
from ROOT import TH1F
from config import XSectionConfig
from tools.ROOT_utililities import set_root_defaults

def main():
    set_root_defaults()
    # prevent directory ownership of ROOT histograms (python does the garbage collection)
    TH1F.AddDirectory( False )
    parser = OptionParser()
    parser.add_option( "-n", "--n_toy_mc",
                      dest = "n_toy_mc", default = 300,
                      help = "number of toy MC to create", type = int )
    parser.add_option( "-o", "--output",
                      dest = "output_folder", default = 'data/toy_mc/',
                      help = "output folder for toy MC" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                      help = "set the variable to analyse (MET, HT, ST, MT, WPT)" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type for analysis of MET, ST or MT" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]", type = int )
    parser.add_option( '-V', '--verbose', dest = "verbose", action = "store_true",
                      help = "Print the event number, reco and gen variable value" )

    ( options, _ ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )

    centre_of_mass = options.CoM
    ttbar_xsection = measurement_config.ttbar_xsection
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    variable = options.variable
    met_type = measurement_config.translate_options[options.metType]
    n_toy_mc = options.n_toy_mc
    make_folder_if_not_exists( options.output_folder )
    
    # get histograms
    input_file_hists = File( measurement_config.path_to_unfolding_histograms + 'unfolding_merged_asymmetric.root' )
    # define output file
    out_file_template = '%s/toy_mc_%s_N_%d_%dTeV.root'
    out_file_name = out_file_template % (options.output_folder, variable, n_toy_mc, centre_of_mass)
    output = File( out_file_name, 'recreate' )
    
    for channel in ['electron', 'muon']:
        # first get the weights
        h_truth, h_measured, h_response, _ = get_unfold_histogram_tuple( input_file_hists,
                                                                                       variable,
                                                                                       channel,
                                                                                       met_type,
                                                                                       centre_of_mass,
                                                                                       ttbar_xsection,
                                                                                       luminosity,
                                                                                       load_fakes = False )
        # create directories
        directory = output.mkdir( channel )
        mkdir = directory.mkdir
        cd = directory.cd
        cd()
        # generate toy MC
        for i in range( 1, n_toy_mc + 1 ):
            mkdir( 'toy_%d' % i )
            cd( 'toy_%d' % i )
            # create histograms
            # add tuples (truth, measured, response) of histograms
            truth = generate_toy_MC_from_distribution(h_truth)
            measured = generate_toy_MC_from_distribution(h_measured)
            response = generate_toy_MC_from_2Ddistribution(h_response)
            
            truth.SetName('truth')
            measured.SetName('measured')
            response.SetName('response')
            
            truth.Write()
            measured.Write()
            response.Write()
    output.Write()
    output.Close()

if __name__ == '__main__':
    main()
