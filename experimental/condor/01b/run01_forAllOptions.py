import os
from optparse import OptionParser

vars = [
	# 'MET',
	# 'HT',
	# 'ST',
	# 'WPT',
	# 'NJets',
	# 'lepton_pt',
	# 'abs_lepton_eta',

	'MET --visiblePS',
	'HT --visiblePS',
	'ST --visiblePS',
	'WPT --visiblePS',
	'NJets --visiblePS',
	'lepton_pt --visiblePS',
	'abs_lepton_eta --visiblePS',

	# 'hadTopRap',
	# 'lepTopPt',
	# 'hadTopPt',
	# 'ttbarPt',
	# 'ttbarM',
	# 'lepTopRap',
	# 'ttbarRap',
]

jobOptions = ['-v %s -i config/measurements/background_subtraction' % ( var ) for var in vars ]

parser = OptionParser("Merge histogram files on DICE")
parser.add_option("-n", dest="jobNumber", default=-1, type='int',
                  help="Specify which job number to run")

(options, _) = parser.parse_args()

jobOption = jobOptions[options.jobNumber]
print 'Running with options : ',jobOption
os.system('python src/cross_section_measurement/01_get_ttjet_normalisation.py %s' % jobOption )
