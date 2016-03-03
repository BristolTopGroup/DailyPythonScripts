'''
    A basic script for manually playing around with the unfolding
    Useful for debugging e.g. with known inputs and outputs
    Currently set up to unfold measured MC and compare to truth MC
'''
from rootpy.io import File

from config.variable_binning import bin_edges_vis
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple, removeFakes
from config.cross_section_config import XSectionConfig
from tools.plotting import compare_measurements, Histogram_properties
from config import latex_labels
from tools.ROOT_utils import set_root_defaults
from rootpy import asrootpy

def main():

    config = XSectionConfig(13)
    method = 'TUnfold'

    # A few different files for testing different inputs
    file_for_unfolding = File(config.unfolding_central, 'read')
    madgraph_file = File(config.unfolding_madgraphMLM, 'read')

    for channel in ['combined']:

        # for variable in bin_edges_vis.keys():
        for variable in ['HT']:
        
            print variable

            # tau_value = get_tau_value(config, channel, variable)
            # tau_value = 0.000228338590921
            tau_value = 0.0

            # h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple(
            #     inputfile=file_for_unfolding,
            #     variable=variable,
            #     channel=channel,
            #     met_type=config.met_type,
            #     centre_of_mass=config.centre_of_mass_energy,
            #     ttbar_xsection=config.ttbar_xsection,
            #     luminosity=config.luminosity,
            #     load_fakes=False,
            #     visiblePS=True,
            # )

            # measured = asrootpy(h_response.ProjectionX('px',1))
            # print 'Measured from response :',list(measured.y())
            # truth = asrootpy(h_response.ProjectionY())
            # print 'Truth from response :',list(truth.y())

            h_truth_mad, h_measured_mad, h_response_mad, h_fakes_mad = get_unfold_histogram_tuple(
                inputfile=madgraph_file,
                variable=variable,
                channel=channel,
                met_type=config.met_type,
                centre_of_mass=config.centre_of_mass_energy,
                ttbar_xsection=config.ttbar_xsection,
                luminosity=config.luminosity,
                load_fakes=False,
                visiblePS=True,
            )

            measured = asrootpy(h_response_mad.ProjectionX('px',1))
            print 'Measured from response :',list(measured.y())
            truth = asrootpy(h_response_mad.ProjectionY())
            print 'Truth from response :',list(truth.y())

            # Unfold
            unfolding = Unfolding( measured,
                truth, measured, h_response_mad, None,
                method=method, k_value=-1, tau=tau_value)

            # unfolded_data = unfolding.closureTest()

            # print 'Measured :',list( h_measured.y() )
            # h_measured, _ = removeFakes( h_measured, None, h_response)

            # for binx in range(0,h_truth.GetNbinsX()+2):
            #     for biny in range(0,h_truth.GetNbinsX()+2):
            #         print binx, biny,h_response.GetBinContent(binx,biny)
                # print bin,h_truth.GetBinContent(bin)
            print 'Tau :',tau_value
            unfolded_results = unfolding.unfold()
            print 'Unfolded :',list( unfolded_results.y() )
            print unfolding.unfoldObject.GetTau()


def get_tau_value(config, channel, variable):
    if channel == 'electron':
        return config.tau_values_electron[variable]
    if channel == 'muon':
        return config.tau_values_muon[variable]
    if channel == 'combined':
        return config.tau_values_combined[variable]


if __name__ == '__main__':
    # set_root_defaults( msg_ignore_level = 3001 )
    main()
