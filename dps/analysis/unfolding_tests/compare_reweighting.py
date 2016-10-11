
from dps.utils.file_utilities import read_data_from_JSON
from dps.utils.Unfolding import get_unfold_histogram_tuple, removeFakes
from rootpy.io import File
from rootpy import asrootpy
from dps.utils.hist_utilities import value_error_tuplelist_to_hist
from dps.config.xsection import XSectionConfig
from dps.config.variable_binning import reco_bin_edges_vis
from dps.utils.plotting import compare_measurements, Histogram_properties
from dps.config import latex_labels



def main():

	config = XSectionConfig(13)

	file_for_powhegPythia  = File(config.unfolding_central, 'read')
	file_for_ptReweight_up  = File(config.unfolding_ptreweight_up, 'read')
	file_for_ptReweight_down  = File(config.unfolding_ptreweight_down, 'read')
	file_for_etaReweight_up = File(config.unfolding_etareweight_up, 'read')
	file_for_etaReweight_down = File(config.unfolding_etareweight_down, 'read')
	file_for_data_template = 'data/normalisation/background_subtraction/13TeV/{variable}/VisiblePS/central/normalisation_combined_patType1CorrectedPFMet.txt'



	for channel in ['combined']:
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
			
			_, _, response_eta_reweighted_up, _ = get_unfold_histogram_tuple(
				inputfile=file_for_etaReweight_up,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=False,
				visiblePS=True
			)

			measured_eta_reweighted_up = asrootpy(response_eta_reweighted_up.ProjectionX('px',1))
			truth_eta_reweighted_up = asrootpy(response_eta_reweighted_up.ProjectionY())

			_, _, response_eta_reweighted_down, _ = get_unfold_histogram_tuple(
				inputfile=file_for_etaReweight_down,
				variable=variable,
				channel=channel,
				centre_of_mass=13,
				load_fakes=False,
				visiblePS=True
			)

			measured_eta_reweighted_down = asrootpy(response_eta_reweighted_down.ProjectionX('px',1))
			truth_eta_reweighted_down = asrootpy(response_eta_reweighted_down.ProjectionY())

			# Get the data input (data after background subtraction, and fake removal)
			file_for_data = file_for_data_template.format( variable = variable )
			data = read_data_from_JSON(file_for_data)['TTJet']
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
			hp.y_axis_title = 'Number of events'
			hp.title = 'Reweighting check for {variable}'.format(variable=v_latex)

			measured_central.Rebin(2)
			measured_pt_reweighted_up.Rebin(2)
			measured_pt_reweighted_down.Rebin(2)
			measured_eta_reweighted_up.Rebin(2)
			measured_eta_reweighted_down.Rebin(2)
			data.Rebin(2)

			measured_central.Scale( 1 / measured_central.Integral() )
			measured_pt_reweighted_up.Scale( 1 / measured_pt_reweighted_up.Integral() )
			measured_pt_reweighted_down.Scale( 1 / measured_pt_reweighted_down.Integral() )
			measured_eta_reweighted_up.Scale( 1 / measured_eta_reweighted_up.Integral() )
			measured_eta_reweighted_down.Scale( 1/ measured_eta_reweighted_down.Integral() )

			data.Scale( 1 / data.Integral() )

			compare_measurements(
					models = {'Central' : measured_central, 'PtReweighted Up' : measured_pt_reweighted_up, 'PtReweighted Down' : measured_pt_reweighted_down, 'EtaReweighted Up' : measured_eta_reweighted_up, 'EtaReweighted Down' : measured_eta_reweighted_down},
					measurements = {'Data' : data},
					show_measurement_errors=True,
					histogram_properties=hp,
					save_folder='plots/unfolding/reweighting_check',
					save_as=['pdf']
					)


if __name__ == '__main__':
    main()

