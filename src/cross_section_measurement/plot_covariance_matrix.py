from optparse import OptionParser
from config import XSectionConfig
import numpy as np
from rootpy.plotting import Hist2D
from root_numpy import array2hist
from tools.Calculation import get_correlation_matrix





if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option("-p", "--path", dest="path", default='data/',
	              help="set path to JSON files")
	parser.add_option("-o", "--output_folder", dest="output_folder", default='tables/',
	              help="set path to save tables")
	parser.add_option("-v", "--variable", dest="variable", default='MET',
	              help="set variable to plot (MET, HT, ST, MT, WPT)")
	parser.add_option("-m", "--metType", dest="metType", default='type1',
	                  help="set MET type used in the analysis of MET-dependent variables")
	parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
	                  help="set the centre of mass energy for analysis. Default = 8 [TeV]")

	(options, args) = parser.parse_args()
	measurement_config = XSectionConfig(options.CoM)
	# caching of variables for shorter access
	translate_options = measurement_config.translate_options


	variable = options.variable
	output_folder = options.output_folder
	if not output_folder.endswith('/'):
	    output_folder += '/'

	met_type = translate_options[options.metType]
	path_to_JSON = options.path + '/' + str(measurement_config.centre_of_mass_energy) + 'TeV/'

	for channel in ['combined']:                        

		stat_covariance = np.loadtxt(path_to_JSON + '/' + variable + '/xsection_measurement_results/combined/central/covariance.txt',delimiter=',')
		syst_covariance = np.loadtxt(path_to_JSON + '/' + variable + '/xsection_measurement_results/combined/central/covariance_systematic.txt',delimiter=',')

		full_covariance = stat_covariance + syst_covariance
		# full_covariance = syst_covariance

		print full_covariance
		nBins = full_covariance.shape[0]

		uncertainties = [ np.sqrt(full_covariance[i,i]) for i in range(0,nBins) ]

		full_correlation = get_correlation_matrix( uncertainties, full_covariance )

		hist = Hist2D(nBins, 0, nBins, nBins, 0, nBins, type='F')
		array2hist(full_correlation, hist)

		hist.Draw('COLZ TEXT')
		raw_input('...')


# 1.
# madgraph 260.200698419 14 2.22235586282e-47
# madgraph_ptreweight 206.092857526 14 3.1199844713e-36
# mcatnlo 452.430154807 14 1.09007959737e-87
# powheg_v1_pythia 1136.08556935 14 9.45606334174e-234
# powheg_v1_herwig 767.50906492 14 9.80253562557e-155
# powheg_v2_pythia 172.213828364 14 2.4440527553e-29
# powheg_v2_herwig 2595.64265928 14 0.0

# 0.995
# madgraph 44.952092151 14 4.15303289684e-05
# madgraph_ptreweight 8.97303169932 14 0.832774277818
# mcatnlo 23.4724573835 14 0.0530032732625
# powheg_v1_pythia 39.072729903 14 0.000355412330874
# powheg_v1_herwig 25.1522914114 14 0.0330933635701
# powheg_v2_pythia 20.3633234788 14 0.119096482135
# powheg_v2_herwig 102.494382619 14 1.57464239767e-15

# 0.99
# madgraph 30.9649954797 14 0.0056063902049
# madgraph_ptreweight 6.52232220208 14 0.951563093841
# mcatnlo 16.1987455777 14 0.301388411893
# powheg_v1_pythia 29.7711155148 14 0.00820516299424
# powheg_v1_herwig 18.6963603902 14 0.176878931589
# powheg_v2_pythia 12.6196539729 14 0.556666472407
# powheg_v2_herwig 65.2314532301 14 1.39097221014e-08

# 0.9
# madgraph 10.7635419935 14 0.704503726933
# madgraph_ptreweight 2.51432745404 14 0.999668848356
# mcatnlo 5.15094707419 14 0.983599020582
# powheg_v1_pythia 13.1771312971 14 0.512626005209
# powheg_v1_herwig 7.06757553801 14 0.932075478849
# powheg_v2_pythia 2.9027501205 14 0.999233557149
# powheg_v2_herwig 21.0768834128 14 0.0996784514207

# 0
# madgraph 9.67054408874 14 0.785852080078
# madgraph_ptreweight 6.17360385996 14 0.961924159492
# mcatnlo 9.50466821867 14 0.797427986823
# powheg_v1_pythia 12.1628479675 14 0.593226598367
# powheg_v1_herwig 5.64351092282 14 0.974692894781
# powheg_v2_pythia 10.217000073 14 0.746152402623
# powheg_v2_herwig 53.3771850831 14 1.64091512776e-06
