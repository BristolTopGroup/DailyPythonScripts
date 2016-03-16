from config import CMS
from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex
from config.variable_binning import bin_edges_vis, variable_bins_ROOT
from config import XSectionConfig
from tools.ROOT_utils import get_histograms_from_files
from tools.file_utilities import read_data_from_JSON
from tools.plotting import Histogram_properties, make_control_region_comparison
from tools.hist_utilities import value_error_tuplelist_to_hist, rebin_asymmetric
from ROOT import Double
from uncertainties import ufloat

def get_fit_results(variable, channel):
    global path_to_JSON, category, met_type
    fit_results = read_data_from_JSON(path_to_JSON + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
    return fit_results

def get_fit_inputs(template, variable, channel):
    
    inputs = {}
    for var_bin in variable_bins_ROOT[variable]:
        print var_bin
        histogram = template % var_bin
        histograms = get_histograms_from_files([histogram], histogram_files)
        for sample in [channel, 'TTJet', 'V+Jets', 'SingleTop']:
            n_bins = histograms[sample][histogram].GetNbinsX()
            error = Double(0)
            integral = histograms[sample][histogram].IntegralAndError(1, n_bins, error)
            if inputs.has_key(sample):
                inputs[sample].append((integral, error))
            else:
                inputs[sample] = [(integral, error)]
    
    inputs['QCD'] = []
    for data,ttjet, vjets, singletop in zip(inputs[channel], inputs['TTJet'], inputs['V+Jets'], inputs['SingleTop']):
        qcd = ufloat(data) - ufloat(ttjet) - ufloat(vjets) - ufloat(singletop)
        inputs['QCD'].append((qcd.nominal_value, qcd.std_dev))
    print inputs
    return inputs
            

def do_shape_check(channel, control_region_1, control_region_2, variable, normalisation, title, x_title, y_title, x_limits, y_limits,
                   name_region_1='conversions' , name_region_2='non-isolated electrons', name_region_3='fit results', rebin=1):
    global b_tag_bin
    # QCD shape comparison
    if channel == 'electron':
        histograms = get_histograms_from_files([control_region_1, control_region_2], histogram_files)
        
        region_1 = histograms[channel][control_region_1].Clone() - histograms['TTJet'][control_region_1].Clone() - histograms['V+Jets'][control_region_1].Clone() - histograms['SingleTop'][control_region_1].Clone()
        region_2 = histograms[channel][control_region_2].Clone() - histograms['TTJet'][control_region_2].Clone() - histograms['V+Jets'][control_region_2].Clone() - histograms['SingleTop'][control_region_2].Clone()
        
        region_1.Rebin(rebin)
        region_2.Rebin(rebin)
        
        histogram_properties = Histogram_properties()
        histogram_properties.name = 'QCD_control_region_comparison_' + channel + '_' + variable + '_' + b_tag_bin
        histogram_properties.title = title + ', ' + b_tag_bins_latex[b_tag_bin]
        histogram_properties.x_axis_title = x_title
        histogram_properties.y_axis_title = 'arbitrary units/(0.1)'
        histogram_properties.x_limits = x_limits
        histogram_properties.y_limits = y_limits[0]
        histogram_properties.mc_error = 0.0
        histogram_properties.legend_location = 'upper right'
        make_control_region_comparison(region_1, region_2,
                                       name_region_1=name_region_1, name_region_2=name_region_2,
                                       histogram_properties=histogram_properties, save_folder=output_folder)
        
        # QCD shape comparison to fit results
        histograms = get_histograms_from_files([control_region_1], histogram_files)
        
        region_1_tmp = histograms[channel][control_region_1].Clone() - histograms['TTJet'][control_region_1].Clone() - histograms['V+Jets'][control_region_1].Clone() - histograms['SingleTop'][control_region_1].Clone()
        region_1 = rebin_asymmetric(region_1_tmp, bin_edges[variable])
        
        fit_results_QCD = normalisation[variable]['QCD']
        region_2 = value_error_tuplelist_to_hist(fit_results_QCD, bin_edges_vis[variable])
        
        histogram_properties = Histogram_properties()
        histogram_properties.name = 'QCD_control_region_comparison_' + channel + '_' + variable + '_fits_with_conversions_' + b_tag_bin
        histogram_properties.title = title + ', ' + b_tag_bins_latex[b_tag_bin]
        histogram_properties.x_axis_title = x_title
        histogram_properties.y_axis_title = 'arbitrary units/(0.1)'
        histogram_properties.x_limits = x_limits
        histogram_properties.y_limits = y_limits[1]
        histogram_properties.mc_error = 0.0
        histogram_properties.legend_location = 'upper right'
        make_control_region_comparison(region_1, region_2,
                                       name_region_1=name_region_1, name_region_2=name_region_3,
                                       histogram_properties=histogram_properties, save_folder=output_folder)
    
    histograms = get_histograms_from_files([control_region_2], histogram_files)
    
    region_1_tmp = histograms[channel][control_region_2].Clone() - histograms['TTJet'][control_region_2].Clone() - histograms['V+Jets'][control_region_2].Clone() - histograms['SingleTop'][control_region_2].Clone()
    region_1 = rebin_asymmetric(region_1_tmp, bin_edges_vis[variable])    
    
    fit_results_QCD = normalisation[variable]['QCD']
    region_2 = value_error_tuplelist_to_hist(fit_results_QCD, bin_edges[variable])
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_control_region_comparison_' + channel + '_' + variable + '_fits_with_noniso_' + b_tag_bin
    histogram_properties.title = title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = x_title
    histogram_properties.y_axis_title = 'arbitrary units/(0.1)'
    histogram_properties.x_limits = x_limits
    histogram_properties.y_limits = y_limits[1]
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = 'upper right'
    make_control_region_comparison(region_1, region_2,
                                   name_region_1=name_region_2, name_region_2=name_region_3,
                                   histogram_properties=histogram_properties, save_folder=output_folder)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/absolute_eta_M3_angle_bl/',
                  help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='plots/',
                  help="set path to save plots")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")
    parser.add_option("-c", "--category", dest="category", default='central',
                      help="set the category to take the fit results from (default: central)")
    parser.add_option("-n", "--normalise_to_fit", dest="normalise_to_fit", action="store_true",
                  help="normalise the MC to fit results")
    parser.add_option("-i", "--use_inputs", dest="use_inputs", action="store_true",
                  help="use fit inputs instead of fit results")
    parser.add_option("-e", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                  help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    
    (options, args) = parser.parse_args()
    measurement_config = XSectionConfig(options.CoM)
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    lumi = measurement_config.luminosity
    come = measurement_config.centre_of_mass_energy
    electron_histogram_title = 'CMS Preliminary, $\mathcal{L}$ = %.1f fb$^{-1}$ at $\sqrt{s}$ = %d TeV \n e+jets, $\geq$4 jets' % (lumi, come)
    muon_histogram_title = 'CMS Preliminary, $\mathcal{L}$ = %.1f fb$^{-1}$ at $\sqrt{s}$ = %d TeV \n $\mu$+jets, $\geq$4 jets' % (lumi, come)

    path_to_JSON = options.path + '/' + str(measurement_config.centre_of_mass_energy) + 'TeV/'
    output_folder = options.output_folder
    normalise_to_fit = options.normalise_to_fit
    category = options.category
    met_type = translate_options[options.metType]

    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    histogram_files = {
            'electron' : measurement_config.data_file_electron,
            'muon' : measurement_config.data_file_muon,
            'TTJet': measurement_config.ttbar_category_templates[category],
            'V+Jets': measurement_config.VJets_category_templates[category],
            'QCD': measurement_config.electron_QCD_MC_file,  # this should also be category-dependent, but unimportant and not available atm
            'SingleTop': measurement_config.SingleTop_category_templates[category]
    }
    
    normalisations_electron, normalisations_muon = {}, {}
    # getting normalisations
    if not options.use_inputs:
        fit_results_electron = {
                'MET':get_fit_results('MET', 'electron'),
                'HT':get_fit_results('HT', 'electron'),
                'ST':get_fit_results('ST', 'electron'),
                'MT':get_fit_results('MT', 'electron'),
                'WPT':get_fit_results('WPT', 'electron')
                }
        fit_results_muon = {
                'MET':get_fit_results('MET', 'muon'),
                'HT':get_fit_results('HT', 'muon'),
                'ST':get_fit_results('ST', 'muon'),
                'MT':get_fit_results('MT', 'muon'),
                'WPT':get_fit_results('WPT', 'muon')
                }
        normalisations_electron, normalisations_muon = fit_results_electron, fit_results_muon
    else:
        inputs_electron = {
                           'MET': get_fit_inputs('TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_MET_Analysis/patType1CorrectedPFMet_bin_%s/electron_absolute_eta_0btag', 'MET', 'electron'),
                           'HT': get_fit_inputs('TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_HT_Analysis/HT_bin_%s/electron_absolute_eta_0btag', 'HT', 'electron'),
                           'ST': get_fit_inputs('TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_%s/electron_absolute_eta_0btag', 'ST', 'electron'),
                           'MT': get_fit_inputs('TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_%s/electron_absolute_eta_0btag', 'MT', 'electron'),
                           'WPT': get_fit_inputs('TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_%s/electron_absolute_eta_0btag', 'WPT', 'electron'),
                           }
        
        inputs_muon = {
                           'MET': get_fit_inputs('TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_MET_Analysis/patType1CorrectedPFMet_bin_%s/muon_absolute_eta_0btag', 'MET', 'muon'),
                           'HT': get_fit_inputs('TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_HT_Analysis/HT_bin_%s/muon_absolute_eta_0btag', 'HT', 'muon'),
                           'ST': get_fit_inputs('TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_%s/muon_absolute_eta_0btag', 'ST', 'muon'),
                           'MT': get_fit_inputs('TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_%s/muon_absolute_eta_0btag', 'MT', 'muon'),
                           'WPT': get_fit_inputs('TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_%s/muon_absolute_eta_0btag', 'WPT', 'muon'),
                           }
        normalisations_electron, normalisations_muon = inputs_electron, inputs_muon

    # electrons
    histogram_title = 'CMS Preliminary, $\mathcal{L}$ = 19.6 fb$^{-1}$ at $\sqrt{s}$ = 8 TeV \n e+jets, $\geq$4 jets'
    b_tag_bin = '0btag'
    name_region_1, name_region_2, name_region_3 = 'conversions', 'non-isolated electrons', 'fit results'
    if options.use_inputs:
        name_region_3 = 'fit inputs'
    do_shape_check(channel='electron',
                   control_region_1='TTbar_plus_X_analysis/EPlusJets/QCDConversions/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                   variable='MET',
                   normalisation=normalisations_electron,
                   title=electron_histogram_title,
                   x_title='$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]',
                   y_title='arbitrary units/(5 GeV)',
                   x_limits=[0, 250],
                   y_limits=([0, 0.18], [0, 0.65]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=1)
    
    do_shape_check(channel='electron',
                   control_region_1='TTbar_plus_X_analysis/EPlusJets/QCDConversions/MET/HT_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/MET/HT_' + b_tag_bin,
                   variable='HT',
                   normalisation=normalisations_electron,
                   title=electron_histogram_title,
                   x_title='$H_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(20 GeV)',
                   x_limits=[80, 1000],
                   y_limits=([0, 0.12], [0, 0.45]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=4)
      
    do_shape_check(channel='electron',
                   control_region_1='TTbar_plus_X_analysis/EPlusJets/QCDConversions/MET/patType1CorrectedPFMet/ST_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/MET/patType1CorrectedPFMet/ST_' + b_tag_bin,
                   variable='ST',
                   normalisation=normalisations_electron,
                   title=electron_histogram_title,
                   x_title='$S_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(20 GeV)',
                   x_limits=[106, 1000],
                   y_limits=([0, 0.12], [0, 0.65]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=4)
     
    do_shape_check(channel='electron',
                   control_region_1='TTbar_plus_X_analysis/EPlusJets/QCDConversions/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin,
                   variable='MT',
                   normalisation=normalisations_electron,
                   title=electron_histogram_title,
                   x_title='$M^\mathrm{W}_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(10 GeV)',
                   x_limits=[0, 200],
                   y_limits=([0, 0.18], [0, 0.45]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=10)
     
    do_shape_check(channel='electron',
                   control_region_1='TTbar_plus_X_analysis/EPlusJets/QCDConversions/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin,
                   variable='WPT',
                   normalisation=normalisations_electron,
                   title=electron_histogram_title,
                   x_title='$p^\mathrm{W}_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(5 GeV)',
                   x_limits=[0, 250],
                   y_limits=([0, 0.10], [0, 0.45]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=5)

    # muons
    b_tag_bin = '0btag'
    name_region_1, name_region_2, name_region_3 = 'non-isolated muons', 'non-isolated muons', 'fit results'
    if options.use_inputs:
        name_region_3 = 'fit inputs'
    
    do_shape_check(channel='muon',
                   control_region_1='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                   variable='MET',
                   normalisation=normalisations_muon,
                   title=muon_histogram_title,
                   x_title='$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]',
                   y_title='arbitrary units/(5 GeV)',
                   x_limits=[0, 250],
                   y_limits=([0, 0.18], [0, 1]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=1)
    
    do_shape_check(channel='muon',
                   control_region_1='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/HT_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/HT_' + b_tag_bin,
                   variable='HT',
                   normalisation=normalisations_muon,
                   title=muon_histogram_title,
                   x_title='$H_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(20 GeV)',
                   x_limits=[80, 1000],
                   y_limits=([0, 0.12], [0, 1]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=4)
     
    do_shape_check(channel='muon',
                   control_region_1='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/ST_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/ST_' + b_tag_bin,
                   variable='ST',
                   normalisation=normalisations_muon,
                   title=muon_histogram_title,
                   x_title='$S_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(20 GeV)',
                   x_limits=[106, 1000],
                   y_limits=([0, 0.12], [0, 1]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=4)
     
    do_shape_check(channel='muon',
                   control_region_1='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin,
                   variable='MT',
                   normalisation=normalisations_muon,
                   title=muon_histogram_title,
                   x_title='$M^\mathrm{W}_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(10 GeV)',
                   x_limits=[0, 200],
                   y_limits=([0, 0.18], [0, 1]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=10)
     
    do_shape_check(channel='muon',
                   control_region_1='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin,
                   control_region_2='TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin,
                   variable='WPT',
                   normalisation=normalisations_muon,
                   title=muon_histogram_title,
                   x_title='$p^\mathrm{W}_\mathrm{T}$ [GeV]',
                   y_title='arbitrary units/(5 GeV)',
                   x_limits=[0, 250],
                   y_limits=([0, 0.10], [0, 1]),
                   name_region_1=name_region_1,
                   name_region_2=name_region_2,
                   name_region_3=name_region_3,
                   rebin=5)
