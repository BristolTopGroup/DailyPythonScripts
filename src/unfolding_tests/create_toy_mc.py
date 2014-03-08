'''
Created on 11 Dec 2012

@author: kreczko
1) get template
2) generate N events with gaussian distribution
'''
from optparse import OptionParser
from tools.toy_mc import generate_toy_MC_from_distribution
from tools.Unfolding import get_unfold_histogram_tuple
from tools.file_utilities import make_folder_if_not_exists
from tools.hist_utilities import hist_to_value_error_tuplelist
from config.cross_section_measurement_common import translate_options
from rootpy.io import File
from rootpy import asrootpy
from array import array
import ROOT

def get_new_set_of_histograms(h_truth, h_measured, h_response_AsymBins, h_fakes):
    global nbins
    h_truth_new = generate_toy_MC_from_distribution(h_truth)
    h_measured_new = generate_toy_MC_from_distribution(h_measured)
    h_fakes_new = generate_toy_MC_from_distribution(h_fakes)
    h_reco_truth_new = h_measured_new - h_fakes_new
    h_reco_truth = asrootpy(h_response_AsymBins.ProjectionX())
    h_truth_selected = asrootpy(h_response_AsymBins.ProjectionY())
    
    h_truth_new.SetName('truth')
    h_measured_new.SetName('measured')
    h_fakes_new.SetName('fake')
    h_reco_truth_new.SetName('reco_truth')
    
    # get acceptance scale factor
    acceptance = h_truth_selected / h_truth
    # assume identical acceptance (no reason this should change)
    h_truth_selected_new = h_truth_new.Clone('truth_selected')
    h_truth_selected_new *= acceptance
    h_truth_selected_new.SetName('truth_selected')
    
    scaling_truth_selected = h_truth_selected_new / h_truth_selected
    scaling_reco_truth = h_reco_truth_new / h_reco_truth

    h_response_AsymBins_new = h_response_AsymBins.Clone('response_AsymBins_new')
    h_response_AsymBins_new.SetName('response_without_fakes_AsymBins')

    for y in range(1, nbins+1):
        for x in range(1, nbins+1):
            entry = h_response_AsymBins.GetBinContent(x, y)
            # this weight is only approximate due to the correlation of both results!
            weight = scaling_truth_selected.GetBinContent(y) * scaling_reco_truth.GetBinContent(x)
            h_response_AsymBins_new.SetBinContent(x, y, entry * weight)
    return h_truth_new, h_measured_new, h_fakes_new, h_response_AsymBins_new, h_reco_truth_new, h_truth_selected_new


if __name__ == '__main__':
    # prevent directory ownership of ROOT histograms (python does the garbage collection)
    ROOT.TH1F.AddDirectory(False)
    parser = OptionParser()
    parser.add_option("-n", "--n_toy_mc",
                      dest="n_toy_mc", default=100,
                      help="number of toy MC to create", type=int)
    parser.add_option("-o", "--output",
                      dest="output_folder", default='../data/toy_mc/',
                      help="output folder for toy MC")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]", type=int)

    (options, args) = parser.parse_args()

    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_edges
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit( 'Unknown centre of mass energy' )

    centre_of_mass = options.CoM
    ttbar_xsection = measurement_config.ttbar_xsection
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    variable = options.variable
    met_type = translate_options[options.metType]
    make_folder_if_not_exists(options.output_folder)

    input_file = File( measurement_config.path_to_unfolding_histograms + 'unfolding_merged.root' )

    variable = options.variable

    # define bins
    bins = array('d', bin_edges[variable])
    nbins = len(bins) - 1

    # define output file
    output = File(options.output_folder + '/toy_mc_' + variable + '_N_' + str(options.n_toy_mc) + '.root', 'recreate')
    for channel in ['electron', 'muon']:
        # get histograms
        h_truth, h_measured, h_response_AsymBins, h_fakes = get_unfold_histogram_tuple(input_file,
                                                                                       variable,
                                                                                       channel,
                                                                                       met_type,
                                                                                       centre_of_mass,
                                                                                       ttbar_xsection,
                                                                                       luminosity,
                                                                                       load_fakes = True )
        directory = output.mkdir(channel)
        directory.cd()
        mkdir = directory.mkdir
        cd = directory.cd
        # generate toy MC
        for i in range(1, options.n_toy_mc + 1):
            mkdir('toy_%d' % i)
            cd('toy_%d' % i)  # should the numbering be transferred to the histograms?
            if i % 100 == 0:
                print 'Done %d toy MC' % i
            new_histograms = get_new_set_of_histograms(h_truth, h_measured, h_response_AsymBins, h_fakes)
            for hist in new_histograms:
                hist.Write()
    output.Write()
    output.Close()
