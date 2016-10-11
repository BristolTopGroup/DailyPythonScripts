from optparse import OptionParser
from .read_BLT_ntuple import Particle, read_lepton_collections, match_four_momenta, get_parameters, set_parameter_limits, get_fitted_function_str
from ROOT import TGraphAsymmErrors, TF1
from dps.utils.ROOT_utils import set_root_defaults
from dps.utils.file_utilities import make_folder_if_not_exists
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from rootpy.io import File
from rootpy import asrootpy, ROOTError
from rootpy.plotting import Hist, Efficiency
from copy import deepcopy

import pickle
import numpy
from numpy import frompyfunc
from pylab import plot

from dps.config import CMS
from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

jet_pt_bins = [30, 40, 50, 100]

histograms_1st = {
                  'reco_jet_pt' : Hist(20, 0, 150, name='reco_jet_pt'),
                  'reco_jet_eta' : Hist(30, -3, 3, name='reco_jet_eta'),
                  'reco_jet_multiplicity' : Hist(5, 0, 5, name='N reco jets'),

                  'hlt_jet_pt' : Hist(20, 0, 150, name='hlt_jet_pt'),
                  'hlt_jet_eta' : Hist(30, -3, 3, name='hlt_jet_eta'),
                  'hlt_jet_multiplicity' : Hist(5, 0, 5, name='N hlt jets'),

                  'reco_4th_jet_pt_passed' : Hist(jet_pt_bins, name='reco_4th_jet_pt_passed'),
                  'reco_4th_jet_pt_total' : Hist(jet_pt_bins, name='reco_4th_jet_pt_total'),
                  'reco_4th_jet_eta_passed' : Hist(15, -3, 3, name='reco_4th_jet_eta_passed'),
                  'reco_4th_jet_eta_total' : Hist(15, -3, 3, name='reco_4th_jet_eta_total'),
}

# histograms sets for 3 versions of 2011 ele+jets trigger
histograms_2nd = deepcopy(histograms_1st)
histograms_3rd = deepcopy(histograms_1st)

def make_single_efficiency_plot(hist_passed, hist_total, efficiency, channel = 'electron'):
    global output_folder, output_formats

    x_limits, x_title, y_title, fit_function, fit_range = get_parameters(efficiency)

    plot_efficiency = asrootpy(TGraphAsymmErrors())
    plot_efficiency.Divide(hist_passed, hist_total, "cl=0.683 b(1,1) mode")

    fit_data = TF1("fit_data", fit_function, fit_range[0], fit_range[1])
    set_parameter_limits(efficiency, fit_data)
    try:
        plot_efficiency.Fit(fit_data, 'FECQ')
    except ROOTError, e:
        print e.msg
        pass
    plot_efficiency.SetMarkerSize(2)

    save_as_name = efficiency

    # plot with matplotlib
    plt.figure(figsize=(20, 16), dpi=200, facecolor='white')

    ax0 = plt.axes()
    ax0.minorticks_on()
    ax0.grid(True, 'major', linewidth=2)
    ax0.grid(True, 'minor')
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    
    ax0.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax0.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax0.xaxis.labelpad = 11
    #ax0.yaxis.labelpad = 20
    
    rplt.errorbar(plot_efficiency, xerr=True, emptybins=True, axes=ax0, marker = 'o', ms = 15, mew=3, lw = 2)
    
    ax0.set_xlim(x_limits)
    ax0.set_ylim([0.0,1.1])
    
    #add fits
    x = numpy.linspace(fit_data.GetXmin(), fit_data.GetXmax(), fit_data.GetNpx())
    function_data = frompyfunc(fit_data.Eval, 1, 1)
    plot(x, function_data(x), axes=ax0, color = 'red', linewidth = 2)
    
    
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    plt.xlabel(x_title, CMS.x_axis_title)
    plt.ylabel(y_title, CMS.y_axis_title)
    plt.title(r'e+jets, CMS Preliminary, $\sqrt{s}$ = 7 TeV', CMS.title)
    plt.legend(['data', 'fit'], numpoints=1, loc='lower right', prop=CMS.legend_properties)

    
    #add fit formulas
    ax0.text(0.2, 0.15, '$\epsilon$ = ' + get_fitted_function_str(fit_data, fit_function),
        verticalalignment='bottom', horizontalalignment='left',
        transform=ax0.transAxes,
        color='red', fontsize=60, bbox = dict(facecolor = 'white', edgecolor = 'none', alpha = 0.5))

    plt.tight_layout()
    
    for output_format in output_formats:
        plt.savefig(output_folder + save_as_name + '.' + output_format)  

def read_jet_collections( event, reco_jet_collection, trigger_jet_collection, histograms, channel = 'electron' ):
    reco_jets = []
    hlt_jets = []
    getVar = event.__getattr__
    reco_jets_px = getVar(reco_jet_collection + '.Px')
    reco_jets_py = getVar(reco_jet_collection + '.Py')
    reco_jets_pz = getVar(reco_jet_collection + '.Pz')
    reco_jets_E  = getVar(reco_jet_collection + '.Energy')
    assert reco_jets_px.size() == reco_jets_py.size() == reco_jets_pz.size() == reco_jets_E.size()
    for index in range(reco_jets_E.size()):
        reco_jet = Particle(reco_jets_px[index], reco_jets_py[index], reco_jets_pz[index], reco_jets_E[index])
        histograms['reco_jet_pt'].Fill(reco_jet.Pt())
        histograms['reco_jet_eta'].Fill(reco_jet.Eta())
        reco_jets.append(reco_jet)

    histograms['reco_jet_multiplicity'].Fill(len(reco_jets))

    hlt_jets_px = getVar(trigger_jet_collection + '.Px')
    hlt_jets_py = getVar(trigger_jet_collection + '.Py')
    hlt_jets_pz = getVar(trigger_jet_collection + '.Pz')
    hlt_jets_E  = getVar(trigger_jet_collection + '.Energy')
    assert hlt_jets_px.size() == hlt_jets_py.size() == hlt_jets_pz.size() == hlt_jets_E.size()
    for index in range(hlt_jets_E.size()):
        hlt_jet = Particle(hlt_jets_px[index], hlt_jets_py[index], hlt_jets_pz[index], hlt_jets_E[index])
        histograms['hlt_jet_pt'].Fill(hlt_jet.Pt())
        histograms['hlt_jet_eta'].Fill(hlt_jet.Eta())
        hlt_jets.append(hlt_jet)
    
    histograms['hlt_jet_multiplicity'].Fill(len(hlt_jets))
    
    return reco_jets, hlt_jets

def produce_pickle_file(hist_passed_data, hist_total_data, file_name):
    output_pickle = open( file_name, 'wb' )
    dictionary = {}

    number_of_pt_bin_edges = len( jet_pt_bins )
    
    data_efficiency = Efficiency(hist_passed_data, hist_total_data)

    for i in range( number_of_pt_bin_edges - 1 ):
        lower_edge_pt = jet_pt_bins[i]
        upper_edge_pt = jet_pt_bins[i+1]
        pt_bin_range = 'pt_' + str(lower_edge_pt) + '_' + str(upper_edge_pt)
        dictionary[pt_bin_range] = {}

        data_efficiency_in_bin = data_efficiency.GetEfficiency( i+1 )
        data_efficiency_in_bin_error_up = data_efficiency.GetEfficiencyErrorUp( i+1 )
        data_efficiency_in_bin_error_down = data_efficiency.GetEfficiencyErrorLow( i+1 )
        dictionary[pt_bin_range]['data'] = { 'efficiency' : data_efficiency_in_bin,
                                                  'err_up' : data_efficiency_in_bin_error_up,
                                                  'err_down' : data_efficiency_in_bin_error_down,
                                                }

    pickle.dump( dictionary, output_pickle )

if __name__ == '__main__':
    set_root_defaults( msg_ignore_level = 3001 )
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='/hdfs/TopQuarkGroup/trigger_BLT_ntuples/',
                  help="set path to input BLT ntuples")
    parser.add_option("-o", "--output_folder", dest="output_plots_folder", default='plots/2011/hadron_leg/',
                  help="set path to save tables")

    (options, args) = parser.parse_args()
    input_path = options.path
    output_folder = options.output_plots_folder
    output_pickle_folder = './pickle_files/'
    channel = 'electron'
    centre_of_mass = 7

    make_folder_if_not_exists(output_folder)
    make_folder_if_not_exists(output_pickle_folder)
    output_formats = ['pdf']

    data_histFile = input_path + '/2011/SingleElectron_2011_RunAB_had_leg.root'
    data_input_file = File(data_histFile)
    data_tree = data_input_file.Get('rootTupleTreeEPlusJets/ePlusJetsTree')

    reco_leptons_collection = 'selectedPatElectronsLoosePFlow'
    reco_jet_collection = 'cleanedJetsPFlowEPlusJets'
    trigger_object_lepton = 'TriggerObjectElectronIsoLeg'
    trigger_jet_collection = 'TriggerObjectHadronPFIsoLeg'

    print 'Number of events in data tree: ', data_tree.GetEntries()

    n_lepton_leg_events = 0

    for event in data_tree:
        run_number = event.__getattr__('Event.Run')

        if run_number >= 160404 and run_number <= 165633:
            trigger_name = 'HLT_Ele25_CaloIdVT_TrkIdT_CentralTriJet30'
            alternative_trigger_name = 'HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30'
            trigger_object_lepton = 'TriggerObjectElectronLeg'
            trigger_jet_collection = 'TriggerObjectHadronLeg'
            histograms = histograms_1st
        elif run_number >= 165970 and run_number <= 178380:
            trigger_name = 'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30'
            alternative_trigger_name = trigger_name
            trigger_object_lepton = 'TriggerObjectElectronIsoLeg'
            trigger_jet_collection = 'TriggerObjectHadronIsoLeg'
            histograms = histograms_2nd
        elif run_number >= 178420 and run_number <= 180252:
            trigger_name = 'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFJet30'
            alternative_trigger_name = trigger_name
            trigger_object_lepton = 'TriggerObjectElectronIsoLeg'
            trigger_jet_collection = 'TriggerObjectHadronPFIsoLeg'
            histograms = histograms_3rd

        reco_leptons, hlt_leptons, _ = read_lepton_collections( event, reco_leptons_collection, \
        							'dummy_mc_collection', trigger_object_lepton, 'data', channel, doTrigger = True )
        
        # check passing the lepton leg of the trigger
        passes_lepton_leg = False
        for reco_lepton in reco_leptons:
            matched_delta_R = 99
            best_index, matched_delta_R = match_four_momenta(reco_lepton, hlt_leptons)
            if matched_delta_R < 0.3:
                passes_lepton_leg = True
                continue

        if passes_lepton_leg:
            n_lepton_leg_events += 1
            reco_jets, hlt_jets = read_jet_collections( event, reco_jet_collection, trigger_jet_collection, histograms, channel )

            third_reco_jet = reco_jets[2]
            fourth_reco_jet = reco_jets[3]
            histograms['reco_4th_jet_pt_total'].Fill(fourth_reco_jet.Pt())
            histograms['reco_4th_jet_eta_total'].Fill(fourth_reco_jet.Eta())

            trigger_list = event.__getattr__('Trigger.HLTNames')
            trigger_results = event.__getattr__('Trigger.HLTResults')
            assert trigger_list.size() == trigger_results.size()
            for index in range(trigger_list.size()):
                if trigger_name in trigger_list[index] and not 'not found' in trigger_list[index]:
                    if trigger_results[index]:
                        histograms['reco_4th_jet_pt_passed'].Fill(fourth_reco_jet.Pt())
                        histograms['reco_4th_jet_eta_passed'].Fill(fourth_reco_jet.Eta())
                        continue
                elif alternative_trigger_name in trigger_list[index] and not 'not found' in trigger_list[index]:
                    if trigger_results[index]:
                        histograms['reco_4th_jet_pt_passed'].Fill(fourth_reco_jet.Pt())
                        histograms['reco_4th_jet_eta_passed'].Fill(fourth_reco_jet.Eta())
                        continue


    print 'Events passing lepton leg:', n_lepton_leg_events

    # first version of ele+jets trigger (runs 160404-165633)
    make_single_efficiency_plot(histograms_1st['reco_4th_jet_pt_passed'], histograms_1st['reco_4th_jet_pt_total'], 'efficiency_4th_jet_pt_1st', channel)
    make_single_efficiency_plot(histograms_1st['reco_4th_jet_eta_passed'], histograms_1st['reco_4th_jet_eta_total'], 'efficiency_4th_jet_eta_1st', channel)
    produce_pickle_file(histograms_1st['reco_4th_jet_pt_passed'], histograms_1st['reco_4th_jet_pt_total'], output_pickle_folder + '/2011_had_leg_eff_1st.pkl')

    # second version of ele+jets trigger (runs 165970-178380)
    make_single_efficiency_plot(histograms_2nd['reco_4th_jet_pt_passed'], histograms_2nd['reco_4th_jet_pt_total'], 'efficiency_4th_jet_pt_2nd', channel)
    make_single_efficiency_plot(histograms_2nd['reco_4th_jet_eta_passed'], histograms_2nd['reco_4th_jet_eta_total'], 'efficiency_4th_jet_eta_2nd', channel)
    produce_pickle_file(histograms_2nd['reco_4th_jet_pt_passed'], histograms_2nd['reco_4th_jet_pt_total'], output_pickle_folder + '/2011_had_leg_eff_2nd.pkl')

    # third version of ele+jets trigger (runs 178420-180252)
    make_single_efficiency_plot(histograms_3rd['reco_4th_jet_pt_passed'], histograms_3rd['reco_4th_jet_pt_total'], 'efficiency_4th_jet_pt_3rd', channel)
    make_single_efficiency_plot(histograms_3rd['reco_4th_jet_eta_passed'], histograms_3rd['reco_4th_jet_eta_total'], 'efficiency_4th_jet_eta_3rd', channel)
    produce_pickle_file(histograms_3rd['reco_4th_jet_pt_passed'], histograms_3rd['reco_4th_jet_pt_total'], output_pickle_folder + '/2011_had_leg_eff_3rd.pkl')

