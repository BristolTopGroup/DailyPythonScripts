from __future__ import division
from optparse import OptionParser
from math import sqrt
import sys
# rootpy                                                                                                                                                                                                                      
from rootpy.io import File
from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, RooHistPdf, RooArgSet, RooAddPdf
from ROOT import RooChi2Var, RooFormulaVar, RooMinuit, TCanvas, RooPlot, RooGaussian, RooProdPdf, RooLinkedList
from dps.config.variable_binning import variable_bins_ROOT
from dps.utils.Calculation import decombine_result
from uncertainties import ufloat
from dps.config.xsection import XSectionConfig
from dps.config.summations_common import b_tag_summations
        
# copied from 01_get_fit_results.py
def get_histogram(input_file, histogram_path, b_tag_bin=''):
    b_tag_bin_sum_rules = b_tag_summations
    histogram = None
    if b_tag_bin in b_tag_bin_sum_rules.keys():  # summing needed
        b_tag_bins_to_sum = b_tag_bin_sum_rules[b_tag_bin]
        histogram = input_file.Get(histogram_path + '_' + b_tag_bins_to_sum[0]).Clone()
        for bin_i in b_tag_bins_to_sum[1:]:
            histogram += input_file.Get(histogram_path + '_' + bin_i)
    else:
        if b_tag_bin == '':
            histogram = input_file.Get(histogram_path)
        else:
            histogram = input_file.Get(histogram_path + '_' + b_tag_bin)
    return histogram.Clone()

def get_histograms(channel, input_files, variable, met_type, variable_bin, b_tag_bin, rebin=1):
    global b_tag_bin_VJets
    global electron_control_region, muon_control_region

    histograms = {}
    if not variable in measurement_config.histogram_path_templates.keys():
        print 'Fatal Error: unknown variable ', variable
        sys.exit()
    
    abs_eta = ''
    abs_eta_data = ''
    abs_eta_template = measurement_config.histogram_path_templates[variable] 
    if variable == 'HT':
        abs_eta = abs_eta_template % (analysis_type[channel], variable_bin, channel)
        abs_eta_data = abs_eta
    else:
        if measurement_config.centre_of_mass == 8:
            abs_eta = abs_eta_template % (analysis_type[channel], met_type, variable_bin, channel)
        else:  # hot fix for 2011 data. Needs reprocessing for nicer paths
            lepton = channel.title()
            abs_eta = abs_eta_template % (analysis_type[channel], lepton, met_type, variable_bin, channel)
        if 'JetRes' in met_type:
            abs_eta_data = abs_eta.replace('JetResDown', '')
            abs_eta_data = abs_eta_data.replace('JetResUp', '')
            if 'patPFMet' in met_type:
                abs_eta = abs_eta.replace('patPFMet', 'PFMET')
        else:
            abs_eta_data = abs_eta
    
    for sample, file_name in input_files.iteritems():
        h_abs_eta = None
        if sample == 'data':
            h_abs_eta = get_histogram(file_name, abs_eta_data, b_tag_bin)
        elif sample == 'V+Jets':
            # extracting the V+Jets template from its specific b-tag bin (>=0 by default) and scaling it to analysis b-tag bin
            h_abs_eta = get_histogram(file_name, abs_eta, b_tag_bin)
            h_abs_eta_VJets_specific_b_tag_bin = get_histogram(file_name, abs_eta, b_tag_bin_VJets)
            try:
                h_abs_eta_VJets_specific_b_tag_bin.Scale(h_abs_eta.Integral() / h_abs_eta_VJets_specific_b_tag_bin.Integral())
                h_abs_eta = h_abs_eta_VJets_specific_b_tag_bin
            except:
                print 'WARNING: V+Jets template from ' + str(file_name) + ', histogram ' + abs_eta + ' in ' + b_tag_bin_VJets + \
                    ' b-tag bin is empty. Using central bin (' + b_tag_bin + '), integral = ' + str(h_abs_eta.Integral())
        else:
            h_abs_eta = get_histogram(file_name, abs_eta, b_tag_bin)
        h_abs_eta.Rebin(rebin)
        histograms[sample] = h_abs_eta
    
    if channel == 'electron':
        global electron_QCD_MC_file
        h_abs_eta_mc = get_histogram(electron_QCD_MC_file, abs_eta, b_tag_bin)
        h_abs_eta_mc.Rebin(rebin)
        # data-driven QCD template extracted from all-inclusive eta distributions
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Electron/electron_AbsEta' % (analysis_type[channel])
        abs_eta = abs_eta.replace('Ref selection', electron_control_region)
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['V+Jets'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['TTJet'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['SingleTop'], abs_eta, '0btag')
        electron_QCD_normalisation_factor = 1
        h_abs_eta.Rebin(20)
        if measurement_config.centre_of_mass == 8:
            electron_QCD_normalisation_factor = h_abs_eta_mc.Integral() / h_abs_eta.Integral()
            if electron_QCD_normalisation_factor == 0:
                electron_QCD_normalisation_factor = 1 / h_abs_eta.Integral()
        if measurement_config.centre_of_mass == 7:
            # scaling to 10% of data
            electron_QCD_normalisation_factor = 0.1 * histograms['data'].Integral() / h_abs_eta.Integral()

        h_abs_eta.Scale(electron_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
        
    if channel == 'muon':
        # data-driven QCD template extracted from all-inclusive eta distributions
        global muon_QCD_file, muon_QCD_MC_file
        h_abs_eta_mc = get_histogram(muon_QCD_MC_file, abs_eta, b_tag_bin)
        h_abs_eta_mc.Rebin(rebin)
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Muon/muon_AbsEta' % (analysis_type[channel])
        abs_eta = abs_eta.replace('Ref selection', muon_control_region)
#        abs_eta = measurement_config.special_muon_histogram
#        h_abs_eta = get_histogram(muon_QCD_file, abs_eta, '')
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['TTJet'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['V+Jets'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['SingleTop'], abs_eta, '0btag')
        muon_QCD_normalisation_factor = 1
        h_abs_eta.Rebin(20)
        if measurement_config.centre_of_mass == 8:
            muon_QCD_normalisation_factor = h_abs_eta_mc.Integral() / h_abs_eta.Integral()
            if muon_QCD_normalisation_factor == 0:
                muon_QCD_normalisation_factor = 1 / h_abs_eta.Integral()
        if measurement_config.centre_of_mass == 7:
            muon_QCD_normalisation_factor = 0.05 * histograms['data'].Integral() / h_abs_eta.Integral()
        
        h_abs_eta.Scale(muon_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
        
    return histograms

def get_fitted_normalisation_from_ROOT(channel, input_files, variable, met_type, b_tag_bin):
    results = {}
    initial_values = {}
    templates = {}

    for variable_bin in variable_bins_ROOT[variable]:
        histograms = get_histograms(channel,
                                    input_files,
                                    variable=variable,
                                    met_type=met_type,
                                    variable_bin=variable_bin,
                                    b_tag_bin=b_tag_bin,
                                    rebin=measurement_config.rebin
                                    )
        # create signal histograms
        h_eta_signal = histograms['TTJet'] + histograms['SingleTop']
        
        N_ttbar_before_fit = histograms['TTJet'].Integral()
        N_SingleTop_before_fit = histograms['SingleTop'].Integral()
        N_vjets_before_fit = histograms['V+Jets'].Integral()
        N_qcd_before_fit = histograms['QCD'].Integral()
        N_signal_before_fit = N_ttbar_before_fit + N_SingleTop_before_fit
        
        N_ttbar_error_before_fit = sum(histograms['TTJet'].errors())
        N_SingleTop_error_before_fit = sum(histograms['SingleTop'].errors())
        N_vjets_error_before_fit = sum(histograms['V+Jets'].errors())
        N_QCD_error_before_fit = sum(histograms['QCD'].errors())
        
        if (N_SingleTop_before_fit != 0):
            TTJet_SingleTop_ratio = N_ttbar_before_fit / N_SingleTop_before_fit
        else:
            print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for %s channel! Setting to 0.' % channel
            TTJet_SingleTop_ratio = 0
            
        
        leptonAbsEta = RooRealVar("leptonAbsEta", "leptonAbsEta", 0., 2.4)
        # this has to move to dps.utils.Fitting.py
        vars = RooArgList()
        vars.add(leptonAbsEta)
        vars_set = RooArgSet()
        vars_set.add(leptonAbsEta)
        n_event_obs = histograms['data'].Integral()
        
        lowerBound = 0. 
        upperBound = n_event_obs + 10 * sqrt(n_event_obs)
        n_init = n_event_obs / 2.
        
        data = RooDataHist("data", "dataset with leptonAbsEta", vars, histograms['data'])
        rh_vj = RooDataHist("rh_vj", "vj", vars, histograms['V+Jets'])
        rh_qcd = RooDataHist("rh_qcd", "qcd", vars, histograms['QCD'])
        rh_signal = RooDataHist("rh_signal", "signal", vars, h_eta_signal)
        
        pdf_vj = RooHistPdf ("pdf_vj", "V+Jets pdf", vars_set, rh_vj, 0)
        pdf_qcd = RooHistPdf("pdf_qcd", "QCD pdf ", vars_set, rh_qcd, 0)
        pdf_signal = RooHistPdf("pdf_signal", "single top pdf", vars_set, rh_signal, 0)
        
        # RooRealVar(const char *name, const char *title, Double_t value, Double_t minValue, Double_t maxValue, const char *unit) :
        nSignal = RooRealVar("nSignal", "number of single top + ttbar events", N_signal_before_fit, lowerBound, upperBound, "event")
        nvj = RooRealVar  ("nvj", "number of V+Jets bgnd events", N_vjets_before_fit, lowerBound, upperBound, "event")
        nqcd = RooRealVar("nqcd", "number of QCD bgnd events", N_QCD_error_before_fit, lowerBound, upperBound, "event")
        
        model = RooAddPdf("model", "sig+vj+qcd",
                          RooArgList(pdf_signal, pdf_vj, pdf_qcd),
                          RooArgList(nSignal, nvj, nqcd)
                          )
        vj_constraint = RooGaussian("nvj_constraint", "nvj_constraint", nvj, RooFit.RooConst(N_vjets_before_fit), RooFit.RooConst(0.5 * N_vjets_before_fit))
        qcd_constraint = RooGaussian("nqcd_constraint", "nqcd_constraint", nqcd, RooFit.RooConst(N_qcd_before_fit), RooFit.RooConst(2 * N_qcd_before_fit))  
        model_with_constraints = RooProdPdf("model_with_constraints", "model with gaussian constraints",
                                            RooArgSet(model, vj_constraint, qcd_constraint), RooLinkedList())
        model_with_constraints.fitTo(data, RooFit.Minimizer("Minuit2", "Migrad"))  #WARNING: number of cores changes the results!!!
#         nll = model.createNLL(data, RooFit.NumCPU(2))
#         RooMinuit(nll).migrad()
#         frame1 = nSignal.frame(RooFit.Bins(100), RooFit.Range(lowerBound, n_event_obs), RooFit.Title("LL and profileLL in nSignal")) 
#         nll.plotOn(frame1, RooFit.ShiftToZero())
#         frame2 = nvj.frame(RooFit.Bins(100), RooFit.Range(lowerBound, n_event_obs), RooFit.Title("LL and profileLL in nvj"))
#         nll.plotOn(frame2, RooFit.ShiftToZero())
#         frame3 = nqcd.frame(RooFit.Bins(100), RooFit.Range(lowerBound, n_event_obs), RooFit.Title("LL and profileLL in nqcd"))
#         nll.plotOn(frame3, RooFit.ShiftToZero())  
#         
#         pll_nSignal = nll.createProfile(nSignal)
#         pll_nSignal.plotOn(frame1, RooFit.LineColor(2)) 
#         frame1.SetMinimum(0)
#         frame1.SetMaximum(3)
#         
#         pll_nvj = nll.createProfile(nvj)
#         pll_nvj.plotOn(frame2, RooFit.LineColor(2)) 
#         frame2.SetMinimum(0)
#         frame2.SetMaximum(3)
#         
#         pll_nqcd = nll.createProfile(nqcd)
#         pll_nqcd.plotOn(frame3, RooFit.LineColor(2)) 
#         frame3.SetMinimum(0)
#         frame3.SetMaximum(3)
#         c = TCanvas("profilell","profilell",1200, 400)
#         c.Divide(3)
#         c.cd(1)
#         frame1.Draw()
#         c.cd(2)
#         frame2.Draw()
#         c.cd(3)
#         frame3.Draw()
#         c.SaveAs('profileLL.png')
#         model.fitTo(data, RooFit.Minimizer("Minuit2", "Migrad"), RooFit.NumCPU(1))#WARNING: number of cores changes the results!!!
        fit_results = {}
        fit_results['signal'] = (nSignal.getVal(), nSignal.getError())
        fit_results['QCD'] = ufloat(nqcd.getVal(), nqcd.getError())
        fit_results['V+Jets'] = ufloat(nvj.getVal(), nvj.getError())
        
        N_ttbar, N_SingleTop = decombine_result(fit_results['signal'], TTJet_SingleTop_ratio)
        fit_results['signal'] = ufloat(nSignal.getVal(), nSignal.getError())
        fit_results['TTJet'] = ufloat(N_ttbar)
        fit_results['SingleTop'] = ufloat(N_SingleTop)
        
        if results == {}:  # empty
            for sample in fit_results.keys():
                results[sample] = [fit_results[sample]]
        else:
            for sample in fit_results.keys():
                results[sample].append(fit_results[sample])
        
    return results, None, None

if __name__ == '__main__':
    # setup
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data',
                  help="set output path for JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                      help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("--bjetbin-vjets", dest="bjetbin_VJets", default='0m',
                      help="set b-jet multiplicity for V+Jets samples. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")

    (options, args) = parser.parse_args()
    measurement_config = XSectionConfig(options.CoM)
    # caching of variables for shorter access
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    generator_systematics = measurement_config.generator_systematics
    categories_and_prefixes = measurement_config.categories_and_prefixes
    met_systematics_suffixes = measurement_config.met_systematics_suffixes
    analysis_types = measurement_config.analysis_types
    translate_options = measurement_config.translate_options
        
    generator_systematics = measurement_config.generator_systematics
    categories_and_prefixes = measurement_config.categories_and_prefixes
    met_systematics_suffixes = met_systematics_suffixes
    analysis_type = analysis_types
    
    variable = options.variable
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    b_tag_bin_VJets = translate_options[options.bjetbin_VJets]
    path_to_files = measurement_config.path_to_files
    output_path = options.path
    
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    # data and muon_QCD file with SFs are the same for central measurement and all systematics 
    data_file_electron = File(measurement_config.data_file_electron)
    data_file_muon = File(measurement_config.data_file_muon)
    muon_QCD_file = File(measurement_config.muon_QCD_file)
    
    SingleTop_file = File(measurement_config.SingleTop_file)
    muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_file)
    electron_QCD_MC_file = File(measurement_config.electron_QCD_MC_file)
    TTJet_file = File(measurement_config.ttbar_category_templates['central'])
    VJets_file = File(measurement_config.VJets_category_templates['central'])
    electron_control_region = measurement_config.electron_control_region
    muon_control_region = measurement_config.muon_control_region
    
    input_files = {
                   'TTJet': TTJet_file,
                   'SingleTop': SingleTop_file,
                   'V+Jets': VJets_file,
                   'data': data_file_electron,
                   }
    fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   },
                      variable=variable,
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
    
    print 'TTJet:', fit_results_electron['TTJet'] 
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['TTJet']))
    print
    print 'SingleTop:', fit_results_electron['SingleTop']
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['SingleTop']))
    print
    print 'V+Jets:', fit_results_electron['V+Jets']
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['V+Jets']))
    print
    print 'QCD:', fit_results_electron['QCD']
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['QCD']))
