import numpy as np
from numpy import array 
from rootpy.plotting import Hist
from iminuit import Minuit
from probfit import BinnedLH, Extended, AddPdf, draw_blh
from probfit.pdf import HistogramPdf
from probfit.plotting import draw_pdf
from root_numpy import root2array

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

def main():
    data, data_ctl = get_data()
    signal, bkg, signal_ctl, bkg_ctl = get_templates()
    edges = list( data.xedges() )
#     print list(data.y())
#     data, be = hist_to_numpy(data)
#     print data
#     data_ctl, _ = hist_to_numpy(data_ctl)
#     signal, _ = hist_to_numpy(signal)
#     signal_ctl, _ = hist_to_numpy(signal_ctl)
#     bkg, _ = hist_to_numpy(bkg)
#     bkg_ctl, _ = hist_to_numpy(bkg_ctl)
    sig_pdf = hist_to_pdf( signal )
    bkg_pdf = hist_to_pdf( bkg )
    epsig = Extended( sig_pdf, extname = 'N1' )
    epbkg = Extended( bkg_pdf, extname = 'N2' )
    pdf = AddPdf( epbkg, epsig )
    fitdata = array( list( data.y() ) )
    blh = BinnedLH( pdf, fitdata, bins = n_bins, bound = ( min_x, max_x ), extended = True )
    m = Minuit( blh, N1 = 2000, N2 = 30000, error_N1 = 44, error_N2 = 200 )
    m.migrad()
    blh.draw( m, parts = True )


def get_data():
    # start with data that has the same statistics
    
    # randomise it
    x1_ctl = mu1 + sigma1 * np.random.randn( N_bkg1_ctl )
    x2_ctl = mu2 + sigma2 * np.random.randn( N_signal_ctl )
    x1_obs = mu3 + sigma3 * np.random.randn( N_bkg1_obs )
    x2_obs = mu4 + sigma4 * np.random.randn( N_signal_obs )
    
    h1 = Hist( n_bins, 0, 200, title = 'data' )
    h2 = Hist( n_bins, 0, 200, title = 'data_ctl' )
    
    # fill the histograms with our distributions
    map( h1.Fill, x1_obs )
    map( h1.Fill, x2_obs )
    map( h2.Fill, x1_ctl )
    map( h2.Fill, x2_ctl )
    return h1, h2

def get_templates():
    x1_ctl = mu1 + sigma1 * np.random.randn( N_bkg1_ctl )
    x2_ctl = mu2 + sigma2 * np.random.randn( N_signal_ctl )
    x1_obs = mu3 + sigma3 * np.random.randn( N_bkg1_obs * 2 )
    x2_obs = mu4 + sigma4 * np.random.randn( N_signal_obs * 2 )
    
    signal_1 = Hist( n_bins, 0, 200, title = 'signal_1' )
    bkg_1 = Hist( n_bins, 0, 200, title = 'bkg_1' )
    
    signal_2 = Hist( n_bins, 0, 200, title = 'signal_1' )
    bkg_2 = Hist( n_bins, 0, 200, title = 'bkg_1' )
    
    # fill the histograms with our distributions
    map( bkg_1.Fill, x1_obs )
    map( signal_1.Fill, x2_obs )
    map( bkg_2.Fill, x1_ctl )
    map( signal_2.Fill, x2_ctl )
    
    
    return signal_1, bkg_1, signal_2, bkg_2

def hist_to_numpy( hist ):
    edges = list( hist.xedges() )
    np_hist, be = np.histogram( list( hist.y() ), bins = hist.nbins(), range = ( edges[0], edges[-1] ) )
    return np_hist, be

def hist_to_pdf( hist ):
    edges = array( list( hist.xedges() ) )
    y_values = array( list( hist.y() ) )
    return HistogramPdf( y_values, edges )
    
if __name__ == "__main__":
    main()
    
