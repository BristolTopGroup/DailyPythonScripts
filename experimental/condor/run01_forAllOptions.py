import os
from optparse import OptionParser

fit_var="M3,angle_bl"

vars = [
	'MET',
	'HT',
	'ST',
	'WPT',
	# 'hadTopRap',
	# 'lepTopPt',
	# 'hadTopPt',
	# 'ttbarPt',
	# 'ttbarM',
	# 'lepTopRap',
	# 'ttbarRap',
]

jobOptions = [ '-v %s --fit-variables \'%s\' ' % ( var, fit_var ) for var in vars ]

parser = OptionParser("Merge histogram files on DICE")
parser.add_option("-n", dest="jobNumber", default=-1, type='int',
                  help="Specify which job number to run")

(options, _) = parser.parse_args()

jobOption = jobOptions[options.jobNumber]
print 'Running with options : ',jobOption
os.system('python src/cross_section_measurement/01_get_fit_results.py %s' % jobOption )
