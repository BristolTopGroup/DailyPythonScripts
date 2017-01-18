'''
    A basic script for manually playing around with the unfolding
    Useful for debugging e.g. with known inputs and outputs
    Currently set up to unfold measured MC and compare to truth MC
'''
from rootpy.io import File

from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
from dps.config.xsection import XSectionConfig
from rootpy import asrootpy

def main():

    config = XSectionConfig(13)
    method = 'TUnfold'

    # A few different files for testing different inputs
    file_for_unfolding = File(config.unfolding_central, 'read')
    powheg_herwig_file = File(config.unfolding_powheg_herwig, 'read')

    for channel in ['combined', 'muon', 'electron']:

        # for variable in config.variables:
        for variable in config.variables:
        # for variable in ['MET']:

            print variable

            # tau_value = get_tau_value(config, channel, variable)
            # tau_value = 0.000228338590921
            tau_value = 0.000

            h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple(
                inputfile=file_for_unfolding,
                variable=variable,
                channel=channel,
                centre_of_mass=config.centre_of_mass_energy,
                ttbar_xsection=config.ttbar_xsection,
                luminosity=config.luminosity,
                load_fakes=False,
                visiblePS=True,
            )

            # measured = asrootpy(h_response.ProjectionX('px',1))
            # print 'Measured from response :',list(measured.y())
            # truth = asrootpy(h_response.ProjectionY())
            # print 'Truth from response :',list(truth.y())

            h_truth_ph, h_measured_ph, h_response_ph, h_fakes_ph = get_unfold_histogram_tuple(
                inputfile=powheg_herwig_file,
                variable=variable,
                channel=channel,
                met_type=config.met_type,
                centre_of_mass=config.centre_of_mass_energy,
                ttbar_xsection=config.ttbar_xsection,
                luminosity=config.luminosity,
                load_fakes=False,
                visiblePS=True,
            )

            measured = asrootpy(h_response_ph.ProjectionX('px',1))
            # print 'Measured from response :',list(measured.y())
            measured.SetBinContent(0,0)
            truth = asrootpy(h_response_ph.ProjectionY())
            # print 'Truth from response :',list(truth.y())
            # print 'Truth underflow :',truth.GetBinContent(0),truth.GetBinContent(truth.GetNbinsX()+1)

            # Unfold
            unfolding = Unfolding( measured,
                truth, measured, h_response, None,
                method=method, k_value=-1, tau=tau_value)

            # unfolded_data = unfolding.closureTest()

            # print 'Measured :',list( h_measured.y() )
            # h_measured, _ = removeFakes( h_measured, None, h_response)

            # for binx in range(0,h_truth.GetNbinsX()+2):
            #     for biny in range(0,h_truth.GetNbinsX()+2):
            #         print binx, biny,h_response.GetBinContent(binx,biny)
                # print bin,h_truth.GetBinContent(bin)
            # print 'Tau :',tau_value
            unfolded_results = unfolding.unfold()
            # print 'Unfolded :',list( unfolded_results.y() )
            # print unfolding.unfoldObject.GetTau()

            # print 'Unfolded :',list( unfolded_results.y() )
            refolded_results = unfolding.refold()
            refolded_results.rebin(2)
            measured.rebin(2)
            print 'Refolded :',list( refolded_results.y() )
            print 'Measured :',list( measured.y() )

            # for i in range(1,refolded_results.GetNbinsX()):
            #     print i,measured.GetBinContent(i),measured.GetBinError(i),abs( measured.GetBinContent(i) - refolded_results.GetBinContent(i) )

            pValue = measured.Chi2Test(refolded_results)
            print pValue,1-pValue
            # print unfolding.unfoldObject.GetTau()

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
