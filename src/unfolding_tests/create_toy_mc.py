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
from tools.toy_mc import generate_toy_MC_from_values
from tools.Unfolding import get_unfold_histogram_tuple
from tools.file_utilities import make_folder_if_not_exists
from rootpy.io import File
from rootpy.plotting import Hist
from ROOT import TH1F
from config.variable_binning import bin_edges
from config import XSectionConfig
from tools.ROOT_utililities import set_root_defaults
from rootpy.tree import TreeChain
from rootpy.plotting.hist import Hist2D
from tools.Calculation import which_variable_bin

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
    parser.add_option( "-l", "--limit", dest = "limit", default = 7000000,
                      help = "set the number of (input) events to run over." +
                      "all == -1. Default = 7000000", type = int )
    parser.add_option( '-V', '--verbose', dest = "verbose", action = "store_true",
                      help = "Print the event number, reco and gen variable value" )

    ( options, _ ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )

    centre_of_mass = options.CoM
    ttbar_xsection = measurement_config.ttbar_xsection
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    variable = options.variable
    met_type = measurement_config.translate_options[options.metType]
    verbose = options.verbose
    n_toy_mc = options.n_toy_mc
    make_folder_if_not_exists( options.output_folder )
    limit = options.limit
    
    # the input is a BLT unfolding ntuple of the format
    # EventFilter
    #     - EventCounter
    # topPairEPlusJetsSelectionAnalyser 
    #     - consecutiveCuts             
    #     - individualCuts           
    #     - consecutiveCuts_unweighted
    #     - individualCuts_unweighted
    # topPairMuPlusJetsSelectionAnalyser (as topPairEPlusJetsSelectionAnalyser)
    # rootTupleTreeEPlusJets/ePlusJetsTree
    # rootTupleTreeMuPlusJets/muPlusJetsTree
    # ttbarDecayAnalyser (as topPairEPlusJetsSelectionAnalyser)
    input_files = {7: '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_MSDecays_central_TuneZ2_7TeV-madgraph-tauola/TTJets_nTuple_53X_mc_merged.root',
                   8: '/hdfs/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/BLT/TTJets_MassiveBinDECAY_TuneZ2star_8TeV/TTJets_nTuple_53X_mc_merged.root'}
    input_file_BLT = input_files[centre_of_mass]
    # get histograms
    input_file_hists = File( measurement_config.path_to_unfolding_histograms + 'unfolding_merged_asymmetric.root' )
    # define output file
    out_file_template = '%s/toy_mc_%s_N_%d_%dTeV.root'
    out_file_name = out_file_template % (options.output_folder, variable, n_toy_mc, centre_of_mass)
    output = File( out_file_name, 'recreate' )
    
    
    trees = {'electron' : 'rootTupleTreeEPlusJets/ePlusJetsTree',
             'muon' : 'rootTupleTreeMuPlusJets/muPlusJetsTree'}
    
    gen_var_name = 'unfolding.gen' + variable
    reco_var_name = 'unfolding.reco' + variable
    for channel in ['electron', 'muon']:
        # first get the weights
        h_truth, h_measured, _, _ = get_unfold_histogram_tuple( input_file_hists,
                                                                                       variable,
                                                                                       channel,
                                                                                       met_type,
                                                                                       centre_of_mass,
                                                                                       ttbar_xsection,
                                                                                       luminosity,
                                                                                       load_fakes = True )
        # just store the y-values
        truth_y_values = list( h_truth.y() )
        measured_y_values = list( h_measured.y() )
        # next read in the chain
        chain = TreeChain( trees[channel], [input_file_BLT],
                          branches = ['unfolding.GenSelection',
                                      'unfolding.OfflineSelection',
                                      gen_var_name,
                                      reco_var_name,
                                      ] )
                                      
        # create directories
        directory = output.mkdir( channel )
        mkdir = directory.mkdir
        cd = directory.cd
        cd()
        # generate toy MC
        truth_scale_factors = [None] * options.n_toy_mc
        measured_scale_factors = [None] * options.n_toy_mc
        histograms = [None] * options.n_toy_mc
        
        for i in range( 1, n_toy_mc + 1 ):
            mkdir( 'toy_%d' % i )
            # get scale factors for MC generation
            truth_SFs, measure_SFs = get_scale_factors( truth_y_values, measured_y_values )
            truth_scale_factors[i -1] = truth_SFs
            measured_scale_factors[i -1] = measure_SFs
            cd( 'toy_%d' % i )
            # create histograms
            # add tuples (truth, measured, response) of histograms
            truth = Hist( bin_edges[variable], type = 'D', name = 'truth', 
                          title = 'generated ' + variable )
            measured = Hist( bin_edges[variable], type = 'D', name = 'measured', 
                             title = 'generated ' + variable  )
            response = Hist2D( bin_edges[variable], bin_edges[variable], 
                               type = 'D', name = 'response', 
                               title = 'generated vs. reconstructed' + variable  )
            
            histograms[i - 1] = truth, measured, response
            
            
        # loop over all events
        for counter, event in enumerate(chain):
            # read variables
            get_var = event.__getattr__
            passes_gen_sel = get_var( 'unfolding.GenSelection' )
            passes_offline_sel = get_var( 'unfolding.OfflineSelection' )
            if not passes_gen_sel and not passes_offline_sel:
                # we are not interested in events that pass neither the gen
                # selection nor the offline selection
                continue
            gen_var = get_var( gen_var_name )
            reco_var = get_var( reco_var_name )
            # generate toy MC
            
            if counter % 10000 == 0 and verbose:
                print 'Event number', counter
                print variable, 'gen=', gen_var, '| reco=', reco_var
            
            # find out which variable bin we are in
            gen_var_bin = which_variable_bin(variable, gen_var)
            reco_var_bin = which_variable_bin(variable, reco_var)
                
            for i in range( 1, options.n_toy_mc + 1 ):
                truth_sf = truth_scale_factors[i -1]
                measured_sf = measured_scale_factors[i -1]
                new_gen = gen_var * truth_sf[gen_var_bin]
                new_reco = reco_var * measured_sf[reco_var_bin]
                truth, measured, response = histograms[i - 1]
                if passes_gen_sel:
                    truth.Fill(new_gen)
                if passes_offline_sel:
                    measured.Fill(new_reco)
                if passes_gen_sel and passes_offline_sel:
                    response.Fill(new_reco, new_gen)
            if limit > 0 and counter >= limit:
                break
        print 'Processed', counter, 'events in channel "', channel, '"'
        # write histograms to file
        for i in range( 1, options.n_toy_mc + 1 ):
            cd( 'toy_%d' % i )  # should the numbering be transferred to the histograms?
            for hist in histograms[i - 1]:
                hist.Write()
    output.Write()
    output.Close()


def get_scale_factors( old_truth_y_values, old_measured_y_value ):
    # truth
    new_y_values, _ = generate_toy_MC_from_values( old_truth_y_values )
    truth_scale_factors = [new / old for new, old in zip( new_y_values, old_truth_y_values )]
    # measured
    new_y_values, _ = generate_toy_MC_from_values( old_measured_y_value )
    measured_scale_factors = [new / old for new, old in zip( new_y_values, old_measured_y_value )]
    
    return truth_scale_factors, measured_scale_factors

if __name__ == '__main__':
    main()
