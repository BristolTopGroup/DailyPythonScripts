from iminuit import describe
from tools.Fitting import IMinuit, FitData, FitDataCollection
from rootpy.plotting import Hist
import numpy as np

N_bkg1 = 9000
N_signal = 1000
N_bkg1_obs = 10000
N_signal_obs = 2000
N_data = N_bkg1_obs + N_signal_obs
mu1, mu2, sigma1, sigma2 = 100, 140, 15, 5
x1 = mu1 + sigma1 * np.random.randn( N_bkg1 )
x2 = mu2 + sigma2 * np.random.randn( N_signal )
x1_obs = mu1 + sigma1 * np.random.randn( N_bkg1_obs )
x2_obs = mu2 + sigma2 * np.random.randn( N_signal_obs )

x3 = mu2 + sigma1 * np.random.randn( N_bkg1 )
x4 = mu1 + sigma2 * np.random.randn( N_signal )
x3_obs = mu2 + sigma1 * np.random.randn( N_bkg1_obs )
x4_obs = mu1 + sigma2 * np.random.randn( N_signal_obs )

data_scale = 1.2
N_data = N_data * data_scale

h_bkg1_1 = Hist( 100, 40, 200, title = 'Background' )
h_signal_1 = h_bkg1_1.Clone( title = 'Signal' )
h_data_1 = h_bkg1_1.Clone( title = 'Data' )
h_bkg1_2 = h_bkg1_1.Clone( title = 'Background' )
h_signal_2 = h_bkg1_1.Clone( title = 'Signal' )
h_data_2 = h_bkg1_1.Clone( title = 'Data' )

# fill the histograms with our distributions
map( h_bkg1_1.Fill, x1 )
map( h_signal_1.Fill, x2 )
map( h_data_1.Fill, x1_obs )
map( h_data_1.Fill, x2_obs )

map( h_bkg1_2.Fill, x3 )
map( h_signal_2.Fill, x4 )
map( h_data_2.Fill, x3_obs )
map( h_data_2.Fill, x4_obs )

h_data_1.Scale( data_scale )
h_data_2.Scale( data_scale )

histograms_1 = {'signal': h_signal_1,
                'bkg1': h_bkg1_1}

histograms_2 = {'signal': h_signal_2,
                'bkg1': h_bkg1_2}

fit_data_1 = FitData( h_data_1, histograms_1, fit_boundaries = ( 40, 200 ) )
fit_data_2 = FitData( h_data_2, histograms_2, fit_boundaries = ( 40, 200 ) )

single_fit_collection = FitDataCollection()
single_fit_collection.add( fit_data_1 )

m = IMinuit(single_fit_collection)
print describe(m.likelihood_3_samples, verbose=True)
print describe(m.likelihood_4_samples, verbose=True)