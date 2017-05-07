from dps.utils.file_utilities import get_files_in_path, read_data_from_JSON
from dps.utils.measurement import Measurement
from dps.utils.ROOT_utils import set_root_defaults
from dps.utils.hist_utilities import clean_control_region
from dps.config.xsection import XSectionConfig
from rootpy.plotting import Canvas, Pad
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.config.latex_labels import variables_latex
from uncertainties import ufloat
import ROOT as r

def getControlRegionHistogramsFromFile(file):
	config = read_data_from_JSON(file)
	measurement = Measurement( config )
	return measurement.cr_histograms

def rebinHists( hists ):
	for h in hists:
		hists[h].Rebin(2)

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

SetPlotStyle()
set_root_defaults( set_batch=True)

measurement_config  = XSectionConfig( 13 )

channel =  'electron'

for variable in measurement_config.variables:
	print variable
	measurement_filepath = 'config/measurements/background_subtraction/13TeV/{channel}/{var}/VisiblePS/'.format(var=variable, channel=channel)

	# Get all config files in measurement_filepath
	central_file = measurement_filepath + 'central.json' 
	other_qcd_control_file = measurement_filepath + 'QCD_other_control_region.json' 

	central_control_histograms = getControlRegionHistogramsFromFile(central_file)
	other_control_histograms = getControlRegionHistogramsFromFile(other_qcd_control_file)

	rebinHists( central_control_histograms )
	rebinHists( other_control_histograms )
	qcd_from_data_in_central = clean_control_region(
	    central_control_histograms,
	    subtract=['TTBar', 'V+Jets', 'SingleTop']
		)

	qcd_mc_integral_in_central, u_central = central_control_histograms['QCD'].integral(overflow=True, error=True)
	qcd_mc_integral_in_central = ufloat( qcd_mc_integral_in_central, u_central )

	qcd_from_data_in_other = clean_control_region(
	    other_control_histograms,
	    subtract=['TTBar', 'V+Jets', 'SingleTop']
		)

	qcd_mc_integral_in_other, u_other = other_control_histograms['QCD'].integral(overflow=True, error=True)
	qcd_mc_integral_in_other = ufloat( qcd_mc_integral_in_other, u_other)

	transfer_from_central_to_other = qcd_mc_integral_in_other / qcd_mc_integral_in_central

	print 'Transfer factor :', transfer_from_central_to_other

	qcd_estimate_from_central = qcd_from_data_in_central.Clone('estimate')

	# transferFactorHist = qcd_estimate_from_central.Clone('transferFactor')
	# for i in range(0,transferFactorHist.GetNbinsX()+1):
	# 	transferFactorHist.SetBinContent(i,transfer_from_central_to_other.nominal_value)
	# 	transferFactorHist.SetBinError(i, transfer_from_central_to_other.std_dev)

	qcd_estimate_from_central.Scale(transfer_from_central_to_other.nominal_value)
	# qcd_estimate_from_central.Multiply( transferFactorHist )

	can = Canvas()
	pad1 = Pad( 0, 0.3, 1, 1)
	pad2 = Pad( 0, 0, 1, 0.3)
	pad1.Draw()
	pad2.Draw()
	pad1.cd()

	leg = r.TLegend(0.45,0.5,0.85,0.8)

	qcd_from_data_in_other.SetLineColor(4)
	qcd_from_data_in_other.SetLineWidth(3)
	qcd_from_data_in_other.SetLineStyle(1)

	# qcd_from_data_in_other.Scale( 1 / qcd_from_data_in_other.integral(overflow=True))

	qcd_from_data_in_other.GetYaxis().SetTitle('Events')
	qcd_from_data_in_other.GetXaxis().SetTitle(variables_latex[variable])

	qcd_from_data_in_other.Draw('HIST E')

	maxValue = max( [ qcd_from_data_in_other.GetMaximum(), qcd_estimate_from_central.GetMaximum(), other_control_histograms['QCD'].GetMaximum() ] )

	qcd_from_data_in_other.GetYaxis().SetRangeUser(0, maxValue * 1.5)
	leg.AddEntry( qcd_from_data_in_other, "Data in alternative control region", 'l')

	qcd_estimate_from_central.SetLineColor(2)
	qcd_estimate_from_central.SetLineWidth(3)
	qcd_estimate_from_central.SetLineStyle(3)

	# qcd_estimate_from_central.Scale( 1 / qcd_estimate_from_central.integral(overflow=True))

	qcd_estimate_from_central.Draw('HIST E SAME')
	leg.AddEntry( qcd_estimate_from_central, "QCD estimate from nominal control region", 'l')

	other_control_histograms['QCD'].SetLineColor(8)
	other_control_histograms['QCD'].SetLineWidth(3)
	other_control_histograms['QCD'].SetLineStyle(2)

	# other_control_histograms['QCD'].Scale( 1 / other_control_histograms['QCD'].integral(overflow=True))

	other_control_histograms['QCD'].Draw('HIST E SAME')
	leg.AddEntry( other_control_histograms['QCD'], "QCD MC in alternative control region", 'l')
	leg.Draw()

	pad2.cd()
	pad2.SetGridy()
	ratio = qcd_from_data_in_other / qcd_estimate_from_central
	ratio.GetYaxis().SetRangeUser(0,2)
	ratio.GetXaxis().SetTitle( variables_latex[variable] )
	# ratio.GetYaxis().SetTitle( '#frac{QCD estimate}{Data}')
	ratio.GetYaxis().SetTitle( 'Ratio')
	ratio.GetYaxis().SetTitleSize(0.08)
	ratio.GetYaxis().SetTitleSize(0.1)
	ratio.GetYaxis().SetTitleOffset(0.7)
	ratio.GetYaxis().SetLabelSize(0.09)
	ratio.Draw('HIST E')

	make_folder_if_not_exists('plots/QCDvalidation/')
	outputFileName = 'plots/QCDvalidation/{var}_{channel}.pdf'.format( var=variable, channel=channel )
	can.Update()
	can.Print(outputFileName)
	# raw_input('...')
