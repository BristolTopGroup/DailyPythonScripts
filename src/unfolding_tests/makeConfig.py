import json
from config import XSectionConfig
from config.variable_binning import bin_edges

com = 13
fitVars = "M3_angle_bl"

config = XSectionConfig( com )

for channel in config.analysis_types.keys():
	for variable in bin_edges.keys():

		histogramTemplate = "unfolding_%s_analyser_%s_channel" % ( variable, channel )
		outputJson = {
		    "output_folder": "plots/%sTeV/unfolding_tests" % com, 
		    "output_format": ["png", "pdf"], 
		    "centre-of-mass energy" : com,
		    "channel": "%s" % channel,
		    "variable": "%s" % variable,
			"truth" : { 
				"file" : "%s" % config.unfolding_madgraph,
				"histogram": "%s/truth" % ( histogramTemplate ),
				},
			"gen_vs_reco" : { 
				"file" : "%s" % config.unfolding_madgraph,
				"histogram": "%s/response_without_fakes" % ( histogramTemplate ),
			},
			"measured" : {
				"file" : "%s" % config.unfolding_madgraph,
				"histogram": "%s/measured" % ( histogramTemplate ),
				},
			"data" : { 
				"file": "data/%s/%sTeV/%s/fit_results/central/fit_results_%s_patType1CorrectedPFMet.txt" % ( fitVars, com, variable, channel),
				"histogram": "TTJet"
				},
			}

		outputFile = 'config/unfolding/%s_%sTeV_%s_channel.json' % ( variable, com, channel)
		with open(outputFile, 'w') as outfile:
			# print outputJson
			outfile.write( json.dumps(outputJson , sort_keys=True, indent=4, separators=(',', ': ') ) )
