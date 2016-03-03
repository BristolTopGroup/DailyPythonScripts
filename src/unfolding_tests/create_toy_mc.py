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
from rootpy.io import File
from config import XSectionConfig
from tools.ROOT_utils import set_root_defaults
from rootpy.io.file import root_open
from config.variable_binning import bin_edges_vis
from rootpy import asrootpy


def main():
    set_root_defaults()
    # prevent directory ownership of ROOT histograms (python does the garbage
    # collection)
    parser = OptionParser()
    parser.add_option("-n", "--n_toy_mc",
                      dest="n_toy_mc", default=300,
                      help="number of toy MC to create", type=int)
    parser.add_option("-o", "--output",
                      dest="output_folder", default='data/toy_mc/',
                      help="output folder for toy MC")
    parser.add_option("-s", dest="sample", default='madgraph',
                        help='set underlying sample for creating the toy MC')
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=13,
                      help="set the centre of mass energy for analysis. Default = 13 [TeV]", type=int)
    parser.add_option('-V', '--verbose', dest="verbose", action="store_true",
                      help="Print the event number, reco and gen variable value")

    (options, _) = parser.parse_args()

    measurement_config = XSectionConfig(options.CoM)
#     variable = options.variable
    met_type = measurement_config.translate_options[options.metType]

    input_file = None
    if options.sample == 'madgraph':
        input_file = measurement_config.unfolding_madgraphMLM
    elif options.sample == 'powhegPythia':
        input_file = measurement_config.unfolding_central
    elif options.sample == 'amcatnlo':
        input_file = measurement_config.unfolding_amcatnlo


    create_toy_mc(input_file=input_file,
                  sample=options.sample,
                  output_folder=options.output_folder,
#                   variable=variable,
                  n_toy=options.n_toy_mc,
                  centre_of_mass=options.CoM,
                  ttbar_xsection=measurement_config.ttbar_xsection,
                  met_type=met_type)


def create_toy_mc(input_file, sample, output_folder, n_toy, centre_of_mass, ttbar_xsection, met_type):
    from tools.file_utilities import make_folder_if_not_exists
    from tools.toy_mc import generate_toy_MC_from_distribution, generate_toy_MC_from_2Ddistribution
    from tools.Unfolding import get_unfold_histogram_tuple
    make_folder_if_not_exists(output_folder)
    input_file_hists = File(input_file)
    output_file_name = get_output_file_name(output_folder, sample, n_toy, centre_of_mass)
    variable_bins = bin_edges_vis.copy()
    with root_open(output_file_name, 'recreate') as f_out:
        for channel in ['combined']:
            for variable in variable_bins:
                output_dir = f_out.mkdir(channel + '/' + variable, recurse=True)
                cd = output_dir.cd
                mkdir = output_dir.mkdir
                h_truth, h_measured, h_response, _ = get_unfold_histogram_tuple(input_file_hists,
                                                                        variable,
                                                                        channel,
                                                                        met_type,
                                                                        centre_of_mass,
                                                                        ttbar_xsection,
                                                                        visiblePS = True,
                                                                        load_fakes=False)

                cd()

                mkdir('Original')
                cd ('Original')
                h_truth.Write('truth')
                h_measured.Write('measured')
                h_response.Write('response')

                for i in range(1, n_toy+1):
                    toy_id = 'toy_{0}'.format(i)
                    mkdir(toy_id)
                    cd(toy_id)
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

def get_output_file_name(output_folder, sample, n_toy, centre_of_mass):
    # define output file
    out_file_template = '{0}/toy_mc_{1}_N_{2}_{3}TeV.root'
    output_file_name = out_file_template.format(
        output_folder, sample, n_toy, centre_of_mass)
    return output_file_name

if __name__ == '__main__':
    main()
