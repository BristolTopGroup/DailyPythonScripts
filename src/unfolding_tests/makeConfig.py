import json
from config import XSectionConfig
from config.variable_binning import bin_edges_full, bin_edges_vis
from tools.file_utilities import make_folder_if_not_exists

com = 13
fitVars = "M3_angle_bl"

config = XSectionConfig( com )

make_folder_if_not_exists('config/unfolding/FullPS/')
make_folder_if_not_exists('config/unfolding/VisiblePS/')

for channel in config.analysis_types.keys():
	for variable in config.variables:

		histogramTemplate = "%s_%s" % ( variable, channel )
		outputJson = {
		    "output_folder": "plots/unfolding/bestRegularisation/FullPS", 
		    "output_format": ["png", "pdf"], 
		    "centre-of-mass energy" : com,
		    "channel": "%s" % channel,
		    "variable": "%s" % variable,
		    "phaseSpace" : "FullPS",
			"truth" : { 
				"file" : "%s" % config.unfolding_central,
				# "histogram": "%s/truth" % ( histogramTemplate ),
				},
			"gen_vs_reco" : { 
				"file" : "%s" % config.unfolding_central,
				# "histogram": "%s/response_without_fakes" % ( histogramTemplate ),
			},
			"measured" : {
				"file" : "%s" % config.unfolding_central,
				# "histogram": "%s/measured" % ( histogramTemplate ),
				},
			"data" : { 
				"file": "data/normalisation/background_subtraction/%sTeV/%s/FullPS/central/normalisation_%s_patType1CorrectedPFMet.txt" % ( com, variable, channel),
				"histogram": "TTJet"
				},
			}
		outputFile = 'config/unfolding/FullPS/%s_%sTeV_%s_channel.json' % ( variable, com, channel)
		with open(outputFile, 'w') as outfile:
			# print outputJson
			outfile.write( json.dumps(outputJson , sort_keys=True, indent=4, separators=(',', ': ') ) )

	for variable in config.variables:

		histogramTemplate = "%s_%s" % ( variable, channel )
		outputJson = {
		    "output_folder": "plots/unfolding/bestRegularisation/VisiblePS", 
		    "output_format": ["png", "pdf"], 
		    "centre-of-mass energy" : com,
		    "channel": "%s" % channel,
		    "variable": "%s" % variable,
		    "phaseSpace" : "VisiblePS",
			"truth" : { 
				"file" : "%s" % config.unfolding_central,
				# "histogram": "%s/truthVis" % ( histogramTemplate ),
				},
			"gen_vs_reco" : { 
				"file" : "%s" % config.unfolding_central,
				# "histogram": "%s/responseVis_without_fakes" % ( histogramTemplate ),
			},
			"measured" : {
				"file" : "%s" % config.unfolding_central,
				# "histogram": "%s/measuredVis" % ( histogramTemplate ),
				},
			"data" : { 
				"file": "data/normalisation/background_subtraction/%sTeV/%s/VisiblePS/central/normalisation_%s_patType1CorrectedPFMet.txt" % ( com, variable, channel),
				"histogram": "TTJet"
				},
			}
		outputFile = 'config/unfolding/VisiblePS/%s_%sTeV_%s_channel.json' % ( variable, com, channel)
		with open(outputFile, 'w') as outfile:
			# print outputJson
			outfile.write( json.dumps(outputJson , sort_keys=True, indent=4, separators=(',', ': ') ) )