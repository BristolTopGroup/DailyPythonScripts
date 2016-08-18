# imports
from config.variable_binning import bin_edges
from rootpy.io import root_open, File
from rootpy.plotting import Canvas, Pad, Legend
from config.latex_labels import variables_latex
from ROOT import gStyle, gROOT
gStyle.SetOptStat(0)
gROOT.SetBatch()

def normaliseHistogramToOne( histogram ):
	normalisationFactor = histogram.Integral()
	if normalisationFactor > 0:
		histogram.Scale( 1 / normalisationFactor)

def setHistogramColour( histogram, colour ):
	histogram.linecolor = colour
	histogram.markercolor = colour

def getRatioOfFirstToSecond( first_histogram, second_histogram ):
	return first_histogram / second_histogram

def setupPads():
	canvas = Canvas(width=700,height=500)
	plot_pad = Pad( xlow = 0., ylow = 0.3, xup = 1., yup = 1.)
	plot_pad.SetBottomMargin(0.01)
	ratio_pad = Pad( xlow = 0., ylow = 0., xup = 1., yup = 0.3)
	ratio_pad.SetTopMargin(0.04)
	ratio_pad.SetBottomMargin(0.2)

	return canvas, plot_pad, ratio_pad

# files
seven_tev_file_name = '/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_8th_draft/7TeV/unfolding/unfolding_TTJets_7TeV_asymmetric.root'
eight_tev_file_name = '/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_8th_draft/8TeV/unfolding/unfolding_TTJets_8TeV_asymmetric.root'
reweighted_eight_tev_file_name = '/storage/ec6821/DailyPythonScripts/legacy/CMSSW_7_4_7/src/DailyPythonScripts/unfolding/unfolding_TTJets_8TeV_8To7_asymmetric.root'
output_file_directory = 'plots/compareCOMReweight/'
# channels
channels = ['electron', 'muon']

with root_open( seven_tev_file_name, 'read' ) as seven_tev_file, \
	root_open( eight_tev_file_name, 'read' ) as eight_tev_file, \
	root_open( reweighted_eight_tev_file_name, 'read' ) as reweighted_eight_tev_file:

	for channel in channels:
		for variable in bin_edges:
			if variable == 'MT' : continue
			print variable

			directory_template = 'unfolding_{variable}_analyser_{channel}_channel'
			if variable != 'HT':
				directory_template += '_patType1CorrectedPFMet'

			directory_name = directory_template.format(
														variable = variable,
														channel = channel,
														)

			for distribution in ['truth', 'measured']:

				truth_seven_tev = seven_tev_file.Get( directory_name + '/' + distribution )
				truth_eight_tev = eight_tev_file.Get( directory_name + '/' + distribution )
				truth_reweighted_eight_tev = reweighted_eight_tev_file.Get( directory_name + '/' + distribution )

				normaliseHistogramToOne( truth_seven_tev )
				normaliseHistogramToOne( truth_eight_tev )
				normaliseHistogramToOne( truth_reweighted_eight_tev )

				ratio_reweighted_eight_to_seven = getRatioOfFirstToSecond( truth_reweighted_eight_tev, truth_seven_tev )
				ratio_eight_to_seven = getRatioOfFirstToSecond( truth_eight_tev, truth_seven_tev )

				canvas, plot_pad, ratio_pad = setupPads()
				plot_pad.Draw()
				ratio_pad.Draw()
				setHistogramColour( truth_seven_tev, 'red' )
				setHistogramColour( truth_eight_tev, 'green' )
				setHistogramColour( truth_reweighted_eight_tev, 'blue' )

				plot_pad.cd()
				truth_seven_tev.Draw()
				truth_seven_tev.yaxis.SetTitle('Arbitrary Units')
				truth_seven_tev.xaxis.SetLabelSize(0)
				truth_eight_tev.Draw('SAME')
				truth_reweighted_eight_tev.Draw('SAME')

				setHistogramColour( ratio_reweighted_eight_to_seven, 'blue')
				setHistogramColour( ratio_eight_to_seven, 'green')

				legend = Legend(3)
				legend.AddEntry(truth_seven_tev, label='7 TeV', style='LEP')
				legend.AddEntry(truth_eight_tev, label='8 TeV', style='LEP')
				legend.AddEntry(truth_reweighted_eight_tev, label='Reweighted 8 TeV', style='LEP')
				legend.SetBorderSize(0)
				legend.Draw()

				ratio_pad.cd()			
				ratio_reweighted_eight_to_seven.SetLabelSize(0.1,'X')
				ratio_reweighted_eight_to_seven.SetTitleSize(0.1, 'X')
				ratio_reweighted_eight_to_seven.SetTitleOffset(0, 'X')
				ratio_reweighted_eight_to_seven.xaxis.SetTitle(variables_latex[variable] + '/[GeV]')

				ratio_reweighted_eight_to_seven.yaxis.SetRangeUser(0.9,1.1)
				# ratio_reweighted_eight_to_seven.yaxis.SetNdivisions(400,1)
				ratio_reweighted_eight_to_seven.SetLabelSize(0.1,'Y')
				ratio_reweighted_eight_to_seven.yaxis.SetNdivisions(402);
				ratio_reweighted_eight_to_seven.yaxis.SetTitleSize(20);
				ratio_pad.SetGridy()
				ratio_reweighted_eight_to_seven.Draw()
				ratio_eight_to_seven.Draw('SAME')
				# plot_pad.Update()
				# ratio_pad.Update()
				# canvas.Update()
				output_pdf_template = '{directory}/{variable}_{channel}_{distribution}.pdf'
				output_pdf_filename = output_pdf_template.format( directory = output_file_directory, variable = variable, channel = channel, distribution = distribution)
				canvas.Update()
				canvas.SaveAs(output_pdf_filename)
				# raw_input('...')


