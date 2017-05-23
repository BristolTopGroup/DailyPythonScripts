from dps.utils.pandas_utilities import read_tuple_from_file
from dps.config.xsection import XSectionConfig
from dps.utils.ROOT_utils import set_root_defaults
import matplotlib.pyplot as plt
from dps.config.variable_binning import reco_bin_edges_vis
from dps.utils.hist_utilities import value_error_tuplelist_to_hist
from rootpy.plotting import Canvas, Pad
import ROOT as r

def getMaxDifference( h1, h2 ):
    return max( [abs((float(i)/float(j))) for i,j in zip(h1,h2)] )

def SetPlotStyle():
  # from ATLAS plot style macro
  # use plain black on white colors
  r.gStyle.SetFrameBorderMode(0)
  r.gStyle.SetFrameFillColor(0)
  r.gStyle.SetCanvasBorderMode(0)
  r.gStyle.SetCanvasColor(0)
  r.gStyle.SetPadBorderMode(0)
  r.gStyle.SetPadColor(0)
  r.gStyle.SetStatColor(0)
  r.gStyle.SetHistLineColor(1)

  r.gStyle.SetPalette(1)

  # set the paper & margin sizes
  r.gStyle.SetPaperSize(20,26)
  r.gStyle.SetPadTopMargin(0.05)
  r.gStyle.SetPadRightMargin(0.05)
  r.gStyle.SetPadBottomMargin(0.16)
  r.gStyle.SetPadLeftMargin(0.16)

  # set title offsets (for axis label)
  r.gStyle.SetTitleXOffset(1.4)
  r.gStyle.SetTitleYOffset(1.4)

  # use large fonts
  r.gStyle.SetTextFont(42)
  r.gStyle.SetTextSize(0.05)
  r.gStyle.SetLabelFont(42,"x")
  r.gStyle.SetTitleFont(42,"x")
  r.gStyle.SetLabelFont(42,"y")
  r.gStyle.SetTitleFont(42,"y")
  r.gStyle.SetLabelFont(42,"z")
  r.gStyle.SetTitleFont(42,"z")
  r.gStyle.SetLabelSize(0.05,"x")
  r.gStyle.SetTitleSize(0.05,"x")
  r.gStyle.SetLabelSize(0.05,"y")
  r.gStyle.SetTitleSize(0.05,"y")
  r.gStyle.SetLabelSize(0.05,"z")
  r.gStyle.SetTitleSize(0.05,"z")

  # use bold lines and markers
  r.gStyle.SetMarkerStyle(20)
  r.gStyle.SetMarkerSize(1.2)
  r.gStyle.SetHistLineWidth(2)
  r.gStyle.SetLineStyleString(2,"[12 12]")

  # get rid of error bar caps
  r.gStyle.SetEndErrorSize(0.)

  # do not display any of the standard histogram decorations
  r.gStyle.SetOptTitle(0)
  r.gStyle.SetOptStat(0)
  r.gStyle.SetOptFit(0)

  # put tick marks on top and RHS of plots
  r.gStyle.SetPadTickX(1)
  r.gStyle.SetPadTickY(1)

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
        minY = 99999999

        for f in files:
            normalisations[f] = read_tuple_from_file( files[f] )['QCD']
            hists[f] = value_error_tuplelist_to_hist( normalisations[f], reco_bin_edges_vis[variable] ).Rebin(2)
            maxY = max([maxY]+list(hists[f].y() ) )
            minY = min([minY]+list(hists[f].y() ) )

        if minY <= 0 : minY = 0.1

        can = Canvas()
        pad1 = Pad( 0, 0.3, 1, 1)
        pad2 = Pad( 0, 0, 1, 0.3)
        pad1.Draw()
        pad2.Draw()
        pad1.cd()

        # print normalisations
        hists['central'].SetLineColor(2)
        hists['central'].SetLineWidth(3)
        hists['central'].SetLineStyle(3)
        hists['central'].GetYaxis().SetRangeUser(minY*0.9,maxY*1.2)
        hists['central'].Draw('HIST E')


        hists['QCD_signal_MC'].SetLineColor(4)
        hists['QCD_signal_MC'].SetLineWidth(3)
        hists['QCD_signal_MC'].SetLineStyle(1)
        hists['QCD_signal_MC'].Draw('SAME HIST E')


        hists['QCD_shape'].SetLineColor(4)
        hists['QCD_shape'].SetLineWidth(3)
        hists['QCD_shape'].SetLineStyle(2)
        hists['QCD_shape'].Draw('SAME HIST E')

        hists['QCD_normalisation'].SetLineColor(8)
        hists['QCD_normalisation'].SetLineWidth(3)
        hists['QCD_normalisation'].SetLineStyle(2)
        hists['QCD_normalisation'].Draw('SAME HIST E')

        # hists['QCD_other_control_region'].SetLineColor(9)
        # hists['QCD_other_control_region'].SetLineWidth(3)
        # hists['QCD_other_control_region'].SetLineStyle(2)
        # hists['QCD_other_control_region'].Draw('SAME HIST E')

        # print hists['QCD_signal_MC'].Integral()
        # print hists['central'].Integral()
        # print hists['QCD_other_control_region'].Integral()
        # print hists['QCD_other_control_region'].Integral() / hists['central'].Integral()
        # print hists['QCD_normalisation'].Integral() / hists['central'].Integral()
        # print hists['QCD_shape'].Integral() / hists['central'].Integral()
        # print getMaxDifference( list(hists['QCD_other_control_region'].y()), list(hists['central'].y()))
        # print getMaxDifference( list(hists['QCD_shape'].y()), list(hists['central'].y()))
        # print getMaxDifference( list(hists['QCD_normalisation'].y()), list(hists['central'].y()))

        pad2.cd()
        # pad2.SetGridy()
        ratio1 = hists['QCD_shape'] / hists['central']
        ratio2 = hists['QCD_normalisation'] / hists['central']
        # ratio3 = hists['QCD_other_control_region'] / hists['QCD_signal_MC']

        print list( ratio1.y() )
        ratio1.GetYaxis().SetRangeUser(0,2)
        ratio1.GetXaxis().SetTitle('TEST')

        ratio1.Draw('HIST E')

        ratio2.Draw('HIST SAME E')

        # ratio3.Draw('HIST SAME E')


        raw_input('...')
