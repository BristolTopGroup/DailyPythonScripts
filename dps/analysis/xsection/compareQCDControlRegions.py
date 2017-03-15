from dps.utils.pandas_utilities import read_tuple_from_file
from dps.config.xsection import XSectionConfig
from dps.utils.ROOT_utils import set_root_defaults
import matplotlib.pyplot as plt
from dps.config.variable_binning import reco_bin_edges_vis
from dps.utils.hist_utilities import value_error_tuplelist_to_hist

if __name__ == '__main__':
    # set_root_defaults( msg_ignore_level = 3001 )

    measurement_config  = XSectionConfig( 13 )

    channel =  'electron'

    for variable in measurement_config.variables:
        print variable
        path_to_DF = 'data/normalisation/background_subtraction/13TeV/{variable}/VisiblePS/'.format( 
            variable = variable
        )

        # read normalisation results from JSON
        files = {
            'central' : '{path}/central/normalisation_{channel}.txt'.format( path=path_to_DF,channel=channel ),
            'QCD_shape' : '{path}/QCD_shape/normalisation_{channel}.txt'.format( path=path_to_DF,channel=channel ),
            'QCD_normalisation' : '{path}/QCD_cross_section/normalisation_{channel}.txt'.format( path=path_to_DF,channel=channel ),
            'QCD_other_control_region' : '{path}/QCD_other_control_region/normalisation_{channel}.txt'.format( path=path_to_DF,channel=channel ),
            'QCD_signal_MC' : '{path}/QCD_signal_MC/normalisation_{channel}.txt'.format( path=path_to_DF,channel=channel )
        }

        normalisations = { 
        }
        hists = {
        }
        maxY = 0
        for f in files:
            normalisations[f] = read_tuple_from_file( files[f] )['QCD']
            hists[f] = value_error_tuplelist_to_hist( normalisations[f], reco_bin_edges_vis[variable] ).Rebin(2)
            maxY = max([maxY]+list(hists[f].y() ) )

        # print normalisations
        hists['central'].SetLineColor(2)
        hists['central'].SetLineWidth(3)
        hists['central'].SetLineStyle(3)
        hists['central'].GetYaxis().SetRangeUser(0.01,maxY*1.2)
        hists['central'].Draw('HIST')

        hists['QCD_signal_MC'].SetLineColor(4)
        hists['QCD_signal_MC'].SetLineWidth(3)
        hists['QCD_signal_MC'].SetLineStyle(1)
        hists['QCD_signal_MC'].Draw('SAME HIST')

        # hists['QCD_shape'].SetLineColor(4)
        # hists['QCD_shape'].SetLineWidth(3)
        # hists['QCD_shape'].SetLineStyle(2)
        # hists['QCD_shape'].Draw('SAME HIST')

        # hists['QCD_normalisation'].SetLineColor(8)
        # hists['QCD_normalisation'].SetLineWidth(3)
        # hists['QCD_normalisation'].SetLineStyle(2)
        # hists['QCD_normalisation'].Draw('SAME HIST')

        hists['QCD_other_control_region'].SetLineColor(8)
        hists['QCD_other_control_region'].SetLineWidth(3)
        hists['QCD_other_control_region'].SetLineStyle(2)
        hists['QCD_other_control_region'].Draw('SAME HIST')


        raw_input('...')
