from dps.analysis.xsection.lib import read_normalisation, read_fit_templates, read_initial_normalisation, closure_tests
from rootpy.plotting import Hist
from dps.utils.plotting import make_data_mc_comparison_plot, Histogram_properties


fit_variable_properties = {
                       'M3': {'min':0, 'max':1000, 'rebin':5, 'x-title': 'M3 [GeV]', 'y-title': 'Events/25 GeV'},
                       'angle_bl': {'min':0, 'max':3.5, 'rebin':2, 'x-title': 'angle(b,l)', 'y-title': 'Events/(0.2)'},
                       'absolute_eta': {'min':0, 'max':2.6, 'rebin':2, 'x-title': '$\left|\eta(e)\\right|$', 'y-title': 'Events/(0.2)'},
                       }


variables = [ 'MET', 'HT', 'ST', 'WPT', 'MT' ]


for test in closure_tests:
    if test != 'qcd_only' : continue;
    for variable in variables:
        
        fit_results_ = read_normalisation( 'data/closure_test/'+test+'/absolute_eta_M3_angle_bl/8TeV/',
                                    variable,
                                    'central',
                                    'electron',
                                     'patType1CorrectedPFMet' )
    
        fit_templates_ = read_fit_templates( 'data/closure_test/'+test+'/absolute_eta_M3_angle_bl/8TeV/',
                                        variable,
                                        'central',
                                        'electron',
                                         'patType1CorrectedPFMet' )
        
        initial_values_ = read_initial_normalisation( 'data/closure_test/'+test+'/absolute_eta_M3_angle_bl/8TeV/',
                                        variable,
                                        'central',
                                        'electron',
                                         'patType1CorrectedPFMet' )
    
        for whichBin in range (0,len(fit_results_['TTJet'])):
            for fitVariable in fit_variable_properties:
                fitTemplates = fit_templates_[fitVariable]
                
                histograms = {}
                for template in fitTemplates:
                    nBins = len(fitTemplates[template][whichBin])
                    
                    histograms[template] = Hist(nBins,fit_variable_properties[fitVariable]['min'],fit_variable_properties[fitVariable]['max'],name=template)
                    
                    for bin in range(0,nBins):
                        histograms[template].SetBinContent( bin, fitTemplates[template][whichBin][bin] )
                        pass
                    
                    if template !='data':
                        histograms[template].Scale( fit_results_[template][whichBin][0])
                        pass
                    elif template == 'data':
                        histograms[template].Scale( initial_values_[template][whichBin][0])
                    
                    pass
                
                histogramsToDraw = [    histograms['data'],
                                        histograms['QCD'],
                                        histograms['V+Jets'],
                                        histograms['SingleTop'],
                                        histograms['TTJet']
                                    ]
                
                histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', 'TTJet']
                histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
                histogram_properties = Histogram_properties()
                
                histogram_properties.name = 'Closure_'+'simple'+'_'+fitVariable+'_'+variable+'_'+str(whichBin)
                histogram_properties.x_axis_title = fit_variable_properties[fitVariable]['x-title']
                histogram_properties.y_axis_title = fit_variable_properties[fitVariable]['y-title']
                
                make_data_mc_comparison_plot( histogramsToDraw, histogram_lables, histogram_colors,
                                             histogram_properties,
                                             save_folder = 'data/closure_test/'+test+'/absolute_eta_M3_angle_bl/8TeV/',
                                             show_ratio = False,
                                             save_as = ['pdf'],
                                             )
                pass
            pass
        pass
    pass
