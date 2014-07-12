# please fill in with multi-dimensional fit of all differential cross section measurement variables
# THANKS!

import numpy as np
from rootpy.plotting import Hist
from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, RooHistPdf, \
RooArgSet, RooAddPdf, RooMsgService, RooProdPdf, RooGaussian, RooLinkedList, \
RooCategory, RooSimultaneous, RooDataSet
from copy import deepcopy

def main ():
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
    
    h1 = Hist( 100, 40, 200, title = 'Background' )
    h2 = h1.Clone( title = 'Signal' )
    h3 = h1.Clone( title = 'Data' )
    h3.markersize = 1.2
    
    # fill the histograms with our distributions
    map( h1.Fill, x1 )
    map( h2.Fill, x2 )
    map( h3.Fill, x1_obs )
    map( h3.Fill, x2_obs )
    
    histograms_1 = {'signal': h2,
                  'bkg1': h1,
                  'data': h3}
    
    histograms_2 = {'signal': h2,
                  'bkg1': h1,
                  'data': h3}
    
    # roofit_histograms contains RooDataHist
    # model = RooAddPdf
    model1, roofit_histograms_1,fit_variable_1 = get_roofit_model( histograms_1, fit_boundaries = ( 40, 200 ), name = 'm1' )
    model2, roofit_histograms_2, fit_variable_2 = get_roofit_model( histograms_2, fit_boundaries = ( 40, 200 ), name = 'm2' )
    sample = RooCategory( 'sample', 'sample' )
    sample.defineType( 'm1', 1 )
    sample.defineType( 'm2', 2 )
    combined_data = deepcopy( roofit_histograms_1['data'] )
    combined_data.add( roofit_histograms_2['data'] )
    # RooDataHist(const char* name, const char* title, const RooArgList& vars, RooCategory& indexCat, map<std::string,TH1*> histMap, Double_t initWgt = 1.0)
    sim_pdf = RooSimultaneous( "simPdf", "simultaneous pdf", sample )
    sim_pdf.addPdf( model1, 'm1' )
    sim_pdf.addPdf( model2, 'm2' )
    variables = RooArgList()
    variables.add(fit_variable_1)
    variables.add(fit_variable_2)
#     combined_data = RooDataHist('combined_data', 'combined_data',
#                                 variables, RooFit.Index(sample),
#                                 RooFit.Import('m1', roofit_histograms_1['data']),
#                                 RooFit.Import('m2', roofit_histograms_2['data']))
    fitResult = sim_pdf.fitTo( combined_data,
#                    RooFit.Minimizer( "Minuit2", "Migrad" ),
#                    RooFit.NumCPU( 1 ),
#                    RooFit.Extended(),
                    RooFit.Save(), 
                   )
    
def get_roofit_model( histograms, fit_boundaries, name = 'model' ):
    data_label = 'data'
    samples = sorted( histograms.keys() )
    samples.remove( data_label )
    roofit_histograms = {}
    roofit_pdfs = {}
    roofit_variables = {}
    variables = RooArgList()
    variable_set = RooArgSet()

    fit_variable = RooRealVar( name , name, fit_boundaries[0], fit_boundaries[1] )
    variables.add( fit_variable )
    variable_set.add( fit_variable )
    
    roofit_histograms[data_label] = RooDataHist( data_label,
                                                     data_label,
                                                     variables,
                                                     histograms[data_label] )
    
    pdf_arglist = RooArgList()
    variable_arglist = RooArgList()
    N_total = histograms[data_label].Integral() * 2
    N_min = 0
    for sample in samples:
        roofit_histogram = RooDataHist( sample, sample, variables, histograms[sample] )
        roofit_histograms[sample] = roofit_histogram
        roofit_pdf = RooHistPdf ( 'pdf' + sample, 'pdf' + sample, variable_set, roofit_histogram, 0 )
        roofit_pdfs[sample] = roofit_pdf
        roofit_variable = RooRealVar( sample, "number of " + sample + " events", histograms[sample].Integral(), N_min, N_total, "event" )
        roofit_variables[sample] = roofit_variable
        pdf_arglist.add( roofit_pdf )
        variable_arglist.add( roofit_variable )
        
    model = RooAddPdf( name, name, pdf_arglist, variable_arglist )
    return model, roofit_histograms, fit_variable

if __name__ == '__main__':
    main()
