'''
Created on 28 Jul 2014

@author: phxlk
'''
import numpy as np
from rootpy.plotting import Hist

def hist_to_numpy(hist):
    edges = list(hist.xedges())
    np_hist, be = np.histogram(list(hist.y()), bins = hist.nbins(), range = (edges[0], edges[-1]))
    return np_hist, be


n_bins = 100
min_x = 0
max_x = 200
N_bkg1_ctl = 30000
N_signal_ctl = 2000
N_bkg1_obs = 30000
N_signal_obs = 2000
N_data = N_bkg1_obs + N_signal_obs
mu1, mu2, sigma1, sigma2 = 100, 140, 15, 5
mu3, mu4, sigma3, sigma4 = 80, 170, 14, 10

x1 = mu1 + sigma1 * np.random.randn( N_bkg1_ctl )
h1 = Hist( n_bins, 0, 200, title = 'data' )
map( h1.Fill, x1 )



