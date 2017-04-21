
from dps.utils.file_utilities import read_data_from_JSON
from dps.utils.Unfolding import get_unfold_histogram_tuple, removeFakes
from rootpy.io import File
from rootpy import asrootpy
from dps.utils.hist_utilities import value_error_tuplelist_to_hist
from dps.config.xsection import XSectionConfig
from dps.config.variable_binning import reco_bin_edges_vis
from dps.utils.plotting import compare_measurements, Histogram_properties
from dps.config import latex_labels
from dps.utils.pandas_utilities import read_tuple_from_file
from collections import OrderedDict
def main():

	config = XSectionConfig(13)

	file_for_powhegPythia  		= File(config.unfolding_central_firstHalf, 'read')
	file_for_ptReweight_up 		= File(config.unfolding_ptreweight_up_firstHalf, 'read')
	file_for_ptReweight_down 	= File(config.unfolding_ptreweight_down_firstHalf, 'read')
	file_for_amcatnlo 			= File(config.unfolding_amcatnlo, 'read')
	file_for_powhegHerwig 		= File(config.unfolding_powheg_herwig, 'read')
	file_for_madgraphMLM 		= File(config.unfolding_madgraphMLM, 'read')
	file_for_etaReweight_up 	= File(config.unfolding_etareweight_up, 'read')
	file_for_etaReweight_down 	= File(config.unfolding_etareweight_down, 'read')
	file_for_data_template 		= 'data/normalisation/background_subtraction/13TeV/{variable}/VisiblePS/central/normalisation_{channel}.txt'

	for channel in config.analysis_types.keys():
		if channel is 'combined':continue
		print channel
		for variable in config.variables:
			print variable
		# for variable in ['HT']:
			# Get the central powheg pythia distributions
			_, _, response_central, fakes_central = get_unfold_histogram_tuple(
				inputfile=file_for_powhegPythia,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=True,
				visiblePS=True
			)

			measured_central = asrootpy(response_central.ProjectionX('px',1))
			truth_central = asrootpy(response_central.ProjectionY())


			# Get the reweighted powheg pythia distributions
			_, _, response_pt_reweighted_up, _ = get_unfold_histogram_tuple(
				inputfile=file_for_ptReweight_up,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=False,
				visiblePS=True
			)

			measured_pt_reweighted_up = asrootpy(response_pt_reweighted_up.ProjectionX('px',1))
			truth_pt_reweighted_up = asrootpy(response_pt_reweighted_up.ProjectionY())

			_, _, response_pt_reweighted_down, _ = get_unfold_histogram_tuple(
				inputfile=file_for_ptReweight_down,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=False,
				visiblePS=True
			)

			measured_pt_reweighted_down = asrootpy(response_pt_reweighted_down.ProjectionX('px',1))
			truth_pt_reweighted_down = asrootpy(response_pt_reweighted_down.ProjectionY())

			# _, _, response_eta_reweighted_up, _ = get_unfold_histogram_tuple(
			# 	inputfile=file_for_etaReweight_up,
			# 	variable=variable,
			# 	channel=channel,
			# 	centre_of_mass=13,
			# 	load_fakes=False,
			# 	visiblePS=True
			# )

			# measured_eta_reweighted_up = asrootpy(response_eta_reweighted_up.ProjectionX('px',1))
			# truth_eta_reweighted_up = asrootpy(response_eta_reweighted_up.ProjectionY())

			# _, _, response_eta_reweighted_down, _ = get_unfold_histogram_tuple(
			# 	inputfile=file_for_etaReweight_down,
			# 	variable=variable,
			# 	channel=channel,
			# 	centre_of_mass=13,
			# 	load_fakes=False,
			# 	visiblePS=True
			# )

			# measured_eta_reweighted_down = asrootpy(response_eta_reweighted_down.ProjectionX('px',1))
			# truth_eta_reweighted_down = asrootpy(response_eta_reweighted_down.ProjectionY())

			# Get the distributions for other MC models
			_, _, response_amcatnlo, _ = get_unfold_histogram_tuple(
				inputfile=file_for_amcatnlo,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=False,
				visiblePS=True
			)

			measured_amcatnlo = asrootpy(response_amcatnlo.ProjectionX('px',1))
			truth_amcatnlo = asrootpy(response_amcatnlo.ProjectionY())

			_, _, response_powhegHerwig, _ = get_unfold_histogram_tuple(
				inputfile=file_for_powhegHerwig,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=False,
				visiblePS=True
			)

			measured_powhegHerwig = asrootpy(response_powhegHerwig.ProjectionX('px',1))
			truth_powhegHerwig = asrootpy(response_powhegHerwig.ProjectionY())

			_, _, response_madgraphMLM, _ = get_unfold_histogram_tuple(
				inputfile=file_for_madgraphMLM,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=False,
				visiblePS=True
			)

			measured_madgraphMLM = asrootpy(response_madgraphMLM.ProjectionX('px',1))
			truth_madgraphMLM = asrootpy(response_madgraphMLM.ProjectionY())

			# Get the data input (data after background subtraction, and fake removal)
			file_for_data = file_for_data_template.format( variable = variable, channel = channel )
			data = read_tuple_from_file(file_for_data)['TTJet']
			data = value_error_tuplelist_to_hist( data, reco_bin_edges_vis[variable] )
			data = removeFakes( measured_central, fakes_central, data )

			# Plot all three

			hp = Histogram_properties()
			hp.name = 'Reweighting_check_{channel}_{variable}_at_{com}TeV'.format(
				channel=channel,
				variable=variable,
				com='13',
			)

			v_latex = latex_labels.variables_latex[variable]
			unit = ''
			if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
			    unit = ' [GeV]'
			hp.x_axis_title = v_latex + unit
			hp.x_limits = [ reco_bin_edges_vis[variable][0], reco_bin_edges_vis[variable][-1]]
			hp.ratio_y_limits = [0.1,1.9]
			hp.ratio_y_title = 'Reweighted / Central'
			hp.y_axis_title = 'Number of events'
			hp.title = 'Reweighting check for {variable}'.format(variable=v_latex)

			measured_central.Rebin(2)
			measured_pt_reweighted_up.Rebin(2)
			measured_pt_reweighted_down.Rebin(2)
			# measured_eta_reweighted_up.Rebin(2)
			# measured_eta_reweighted_down.Rebin(2)
			measured_amcatnlo.Rebin(2)
			measured_powhegHerwig.Rebin(2)
			measured_madgraphMLM.Rebin(2)
			data.Rebin(2)

			measured_central.Scale( 1 / measured_central.Integral() )
			measured_pt_reweighted_up.Scale( 1 / measured_pt_reweighted_up.Integral() )
			measured_pt_reweighted_down.Scale( 1 / measured_pt_reweighted_down.Integral() )
			measured_amcatnlo.Scale( 1 / measured_amcatnlo.Integral() )
			measured_powhegHerwig.Scale( 1 / measured_powhegHerwig.Integral() )
			measured_madgraphMLM.Scale( 1 / measured_madgraphMLM.Integral() )

			# measured_eta_reweighted_up.Scale( 1 / measured_eta_reweighted_up.Integral() )
			# measured_eta_reweighted_down.Scale( 1/ measured_eta_reweighted_down.Integral() )

			data.Scale( 1 / data.Integral() )

			compare_measurements(
				# models = {'Central' : measured_central, 'PtReweighted Up' : measured_pt_reweighted_up, 'PtReweighted Down' : measured_pt_reweighted_down, 'EtaReweighted Up' : measured_eta_reweighted_up, 'EtaReweighted Down' : measured_eta_reweighted_down},
				models = OrderedDict([('Central' , measured_central), ('PtReweighted Up' , measured_pt_reweighted_up), ('PtReweighted Down' , measured_pt_reweighted_down), ('amc@nlo' , measured_amcatnlo), ('powhegHerwig' , measured_powhegHerwig), ('madgraphMLM', measured_madgraphMLM) ] ),
				measurements = {'Data' : data},
				show_measurement_errors=True,
				histogram_properties=hp,
				save_folder='plots/unfolding/reweighting_check',
				save_as=['pdf'],
                line_styles_for_models = ['solid','solid','solid','dashed','dashed','dashed'],
				show_ratio_for_pairs = OrderedDict( [ 
					('PtUpVsCentral' , [ measured_pt_reweighted_up, measured_central ] ),
					('PtDownVsCentral' , [ measured_pt_reweighted_down, measured_central ] ),
					('amcatnloVsCentral' , [ measured_amcatnlo, measured_central ] ),
					('powhegHerwigVsCentral' , [ measured_powhegHerwig, measured_central ] ),
					('madgraphMLMVsCentral' , [ measured_madgraphMLM, measured_central ] ),
					('DataVsCentral' , [data, measured_central] ) 
					]),
			)


if __name__ == '__main__':
    main()

