from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
from dps.config.xsection import XSectionConfig
from rootpy import asrootpy
from rootpy.io import File, Directory
from rootpy.plotting import Hist, Hist2D, Canvas, Legend
from dps.utils.ROOT_utils import set_root_defaults
from dps.config import latex_labels
import ROOT as r
import numpy as np
from dps.utils.file_utilities import make_folder_if_not_exists
from argparse import ArgumentParser

def get_tau_value(config, channel, variable):
    if channel == 'electron':
        return config.tau_values_electron[variable]
    if channel == 'muon':
        return config.tau_values_muon[variable]
    if channel == 'combined':
        return config.tau_values_combined[variable]

def makeToyResponse( response ):
	for binx in range(0,response.GetNbinsX() + 2 ):
		for biny in range(0,response.GetNbinsY() + 2 ):
			binContent = response.GetBinContent( binx, biny )
			binError = response.GetBinError( binx, biny )
			if binContent <= 0:
				newBinContent = 0
			else:
				newBinContent = np.random.poisson(binContent)
			if newBinContent < 0: newBinContent = 0

			newBinError = binError

			newBinError = np.sqrt( newBinContent )
			response.SetBinContent( binx, biny, newBinContent )
			response.SetBinError( binx, biny, newBinError)
	return response

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

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument( "-v", "--variable", dest = "variable", default = 'MET',
                      help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_argument( "--channel", dest = "channel", default = 'muon',
                      help = "set the channel (electron, muon, combined)" )

    args = parser.parse_args()
    return args


def main():
	args = parse_arguments()
	channel = args.channel
	variable = args.variable

	SetPlotStyle()
	config = XSectionConfig(13)
	method = 'TUnfold'

	files_for_response = [
		File(config.unfolding_central, 'read')
	]

	files_for_toys = [
		File(config.unfolding_central, 'read')
	]

	print variable
	tau_value = get_tau_value(config, channel, variable)
	print tau_value
	pullHistogram = None

	for file_for_response in files_for_response:

		_, _, h_response, _ = get_unfold_histogram_tuple(
		    inputfile=file_for_response,
		    variable=variable,
		    channel=channel,
		    centre_of_mass=config.centre_of_mass_energy,
		    ttbar_xsection=config.ttbar_xsection,
		    luminosity=config.luminosity,
		    load_fakes=False,
		    visiblePS=True,
		)

		if pullHistogram is None:
			pullHistogram = Hist2D( h_response.GetNbinsY(), 1, h_response.GetNbinsY()+1, 1000, -10, 10 )
			pullHistogram.SetDirectory(0)

		for file_for_toys in files_for_toys:

			_, _, h_response_for_toys, _ = get_unfold_histogram_tuple(
			    inputfile=file_for_toys,
			    variable=variable,
			    channel=channel,
			    centre_of_mass=config.centre_of_mass_energy,
			    ttbar_xsection=config.ttbar_xsection,
			    luminosity=config.luminosity,
			    load_fakes=False,
			    visiblePS=True,
			)

			for i in range(0,5000):

				if i % 100 == 0: print 'Toy number :',i

				toy_response = makeToyResponse( h_response_for_toys.Clone() )
				toy_measured = asrootpy(toy_response.ProjectionX('px',1))
				toy_truth = asrootpy(h_response_for_toys.ProjectionY())

				toy_response_unfolding = makeToyResponse( h_response.Clone() )
				toy_response_unfolding.Scale( toy_response.integral(overflow=True) / toy_response_unfolding.integral(overflow=True) )

				# Unfold toy data with independent toy response
				unfolding = Unfolding( toy_measured,
					toy_truth, toy_measured, toy_response_unfolding, None,
					method='TUnfold', tau=tau_value)

				unfolded_results = unfolding.unfold()

				cov, cor, mc_cov = unfolding.get_covariance_matrix()
				total_statistical_covariance = cov + mc_cov
				for i in range(0,total_statistical_covariance.shape[0] ):
					unfolded_results.SetBinError(i+1, np.sqrt( total_statistical_covariance[i,i] ) )


				for bin in range(1,unfolded_results.GetNbinsX() + 1 ):
					diff = unfolded_results.GetBinContent(bin) - toy_truth.GetBinContent(bin)
					pull = diff / unfolded_results.GetBinError( bin )
					pullHistogram.Fill( bin, pull )

	c = Canvas()
	pullHistogram.Draw('COLZ')
	plots = r.TObjArray()

	# for bin in range(1,pullHistogram.GetNbinsX()):
	# 	slice = pullHistogram.ProjectionY('slice',bin,bin)
	# 	slice.Draw('HIST')
	# 	c.Update()
	# 	slice.Fit('gaus')
	# 	raw_input(bin)

	pullHistogram.FitSlicesY(0,0,-1,0,'QNR',plots)
	means = None
	widths = None
	for p in plots:
		if p.GetName()[-2:] == '_1':
			means = p
		elif p.GetName()[-2:] == '_2':
			widths = p

	means.GetYaxis().SetRangeUser(-2,2)
	means.SetMarkerColor(2)
	means.SetLineColor(2)
	means.GetXaxis().SetTitle(latex_labels.variables_NonLatex[variable])
	means.Draw()

	widths.SetMarkerColor(4)
	widths.SetLineColor(4)
	widths.GetXaxis().SetTitle(latex_labels.variables_NonLatex[variable])
	widths.Draw('SAME')

	l = Legend([], leftmargin=0.45, margin=0.3, topmargin=0.7, entryheight=0.7, entrysep = 0.2)
	l.AddEntry( means, 'Pull mean', 'P')
	l.AddEntry( widths, 'Pull width', 'P')
	l.Draw()
	c.Update()

	truth_response = asrootpy( h_response.ProjectionY() )
	truth_toys = asrootpy( h_response_for_toys.ProjectionY() )
	diff_truth = truth_response - truth_toys

	outputDir = 'plots/unfolding/pulls/new/'
	outputName = '{dir}/{variable}_{channel}.pdf'.format( dir = outputDir, variable = variable, channel = channel)
	make_folder_if_not_exists(outputDir)
	c.SaveAs(outputName)


if __name__ == '__main__':
    set_root_defaults( set_batch = True, msg_ignore_level = 3001 )
    main()