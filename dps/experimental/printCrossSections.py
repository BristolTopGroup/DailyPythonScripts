import ROOT
from optparse import OptionParser
# @BROKEN
from dps.config.variable_binning_8TeV import variable_bins_ROOT, variable_bins_latex
from dps.config.met_systematics import metsystematics_sources, metsystematics_sources_latex
from dps.utils.Calculation import getRelativeError, symmetriseErrors, calculateTotalUncertainty
from dps.utils.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from math import sqrt

categories = [ 'central', 'matchingup', 'matchingdown', 'scaleup', 'scaledown', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up', 'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up' ]
doSymmetricErrors = True

def read_unfolded_xsections(channel):
    global path_to_JSON, variable, k_value, met_type, b_tag_bin
    TTJet_xsection_unfolded = {}
    for category in categories:
        normalised_xsections = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
        TTJet_xsection_unfolded[category] = normalised_xsections['TTJet_unfolded']
    return TTJet_xsection_unfolded

def setMETSystematics(metType):
    prefix = ''
    if metType == 'patMETsPFlow':
        prefix = 'patPFMet'
    elif metType == 'patType1CorrectedPFMet':
        prefix = 'patType1CorrectedPFMet'
    else:
        prefix = 'patType1p2CorrectedPFMet'
    metsystematics_sources = [
        prefix + "ElectronEnUp",
        prefix + "ElectronEnDown",
        prefix + "MuonEnUp",
        prefix + "MuonEnDown",
        prefix + "TauEnUp",
        prefix + "TauEnDown",
        prefix + "JetResUp",
        prefix + "JetResDown",
        prefix + "JetEnUp",
        prefix + "JetEnDown",
        prefix + "UnclusteredEnUp",
        prefix + "UnclusteredEnDown"
                      ]

    metsystematics_sources_latex = {
                prefix + "ElectronEnUp":'Electron energy $+1\sigma$',
                prefix + "ElectronEnDown":'Electron energy $-1\sigma$',
                prefix + "MuonEnUp":'Muon energy $+1\sigma$',
                prefix + "MuonEnDown":'Muon energy $-1\sigma$',
                prefix + "TauEnUp":'Tau energy $+1\sigma$',
                prefix + "TauEnDown":'Tau energy $-1\sigma$',
                prefix + "JetResUp":'Jet resolution $+1\sigma$',
                prefix + "JetResDown":'Jet resolution $-1\sigma$',
                prefix + "JetEnUp":'Jet energy $+1\sigma$',
                prefix + "JetEnDown":'Jet energy $-1\sigma$',
                prefix + "UnclusteredEnUp":'Unclustered energy $+1\sigma$',
                prefix + "UnclusteredEnDown":'Unclustered energy $-1\sigma$'
                      }

def print_xsections(xsections, channel, toFile = True):
    global savePath, variable, k_value, met_type, b_tag_bin
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, k_value, met_type, b_tag_bin)
    printout += '=' * 60
    printout += '\n'
    rows = {}
    header = 'Measurement'
    scale = 100
    
    bins = variable_bins_ROOT[variable]
    assert(len(bins) == len(xsections['central']))
    
    for bin_i, variable_bin in enumerate(bins):
        header += '& $\sigma_{meas}$ %s bin %s~\GeV' % (variable, variable_bin)
        for source in categories:
            value, error = xsections[source][bin_i]
            relativeError = getRelativeError(value, error)
            text = ' $(%.2f \pm %.2f) \cdot 10^{-2}$ ' % (value * scale, error * scale) + '(%.2f' % (relativeError * 100) + '\%)'
            if rows.has_key(source):
                rows[source].append(text)
            else:
                rows[source] = [translateOptions[source], text]
        
    header += '\\\\ \n'
    printout += header
    printout += '\hline\n'
    for item in rows['central']:
        printout += item + '&'
    printout = printout.rstrip('&')
    printout += '\\\\ \n'

    for source in sorted(rows.keys()):
        if source == 'central':
            continue
        for item in rows[source]:
            printout += item + '&'
        printout = printout.rstrip('&')
        printout += '\\\\ \n'
    printout += '\hline \n\n'
    
    make_folder_if_not_exists(savePath + '/' + variable)
    if toFile:
        output_file = open(savePath + '/' + variable + '/normalised_xsection_result_' + channel + '_' + met_type + '_kv' + str(k_value) + '.tex', 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

def print_xsections_with_uncertainties(xsections, channel, toFile = True):
    global savePath, variable, k_value, met_type, b_tag_bin
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, k_value, met_type, b_tag_bin)
    printout += '=' * 60
    printout += '\n'
#    rows = {}
    printout += '%s bin & $\sigma_{meas}$ \\\\ \n' % variable
    printout += '\hline\n'
    uncertainties = {}
    header = 'Uncertainty'
    
    bins = variable_bins_ROOT[variable]
    assert(len(bins) == len(xsections['central']))
    
    for bin_i, variable_bin in enumerate(bins):
        header += '& %s bin %s' % (variable, variable_bin)
        centralresult = xsections['central'][bin_i]
        uncertainty = calculateTotalUncertainty(xsections, bin_i)
        uncertainty_total_plus = uncertainty['Total+'][0]
        uncertainty_total_minus = uncertainty['Total-'][0]
        uncertainty_total_plus, uncertainty_total_minus = symmetriseErrors(uncertainty_total_plus, uncertainty_total_minus)
        scale = 100
        central_measurement = centralresult[0]
        fit_error = centralresult[1]
        
        formatting = (variable_bins_latex[variable_bin], central_measurement * scale,
                      fit_error * scale, uncertainty_total_plus * scale,
                      uncertainty_total_minus * scale)
        text = '%s & $%.2f \pm %.2f (fit)^{+%.2f}_{-%.2f} (sys) \cdot 10^{-2}$\\\\ \n' % formatting
        if doSymmetricErrors:
            relativeError = getRelativeError(central_measurement, fit_error+uncertainty_total_plus)
            formatting = (variable_bins_latex[variable_bin], central_measurement * scale,
                      fit_error * scale, uncertainty_total_plus * scale)
            text = '%s & $\\left(%.2f \\pm %.2f \\text{ (fit)} \pm %.2f \\text{ (syst.)}\\right)' % formatting + '(%.2f' % (relativeError * 100) + '\%) \\times 10^{-2}\, \\GeV^{-1}$\\\\ \n'  
        printout += text
        for source in uncertainty.keys():
            unc_result = uncertainty[source]
            if not uncertainties.has_key(source):
                if source in metsystematics_sources:
                    uncertainties[source] = metsystematics_sources_latex[source] + ' & '
                else:
                    uncertainties[source] = source + ' & '
            relativeError = getRelativeError(centralresult[0], unc_result[0])
#            text = ' $(%.2f \pm %.2f) \cdot 10^{-2} $ ' % (unc_result[0]*scale,unc_result[1]*scale) + '(%.2f' % (relativeError * 100) + '\%) &'
            text = '%.2f' % (relativeError * 100) + '\% &'
#            text = ' $%.2f \pm %.2f $ ' % (unc_result[0]*scale,unc_result[1]*scale) + '(%.2f' % (relativeError * 100) + '\%) &'
            uncertainties[source] += text
    
    printout += '\\\\ \n'
    for source in sorted(uncertainties.keys()):
        value = uncertainties[source]
        value = value.rstrip('&')
        value += '\\\\ \n'
        printout += value
    
    make_folder_if_not_exists(savePath + '/' + variable)
    if toFile:
        output_file = open(savePath + '/' + variable + '/normalised_xsection_main_result_' + channel + '_' + met_type + '_kv' + str(k_value) + '.tex', 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-s", "--savePath", dest="savePath", default='tables/',
                  help="set path to save results")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to take care of (MET, HT, ST, MT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET, ST or MT")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=3,
                      help="k-value for SVD unfolding, used in histogram names")
    translateOptions = {
                        '0':'0btag',
                        '1':'1btag',
                        '2':'2btags',
                        '3':'3btags',
                        '0m':'0orMoreBtag',
                        '1m':'1orMoreBtag',
                        '2m':'2orMoreBtags',
                        '3m':'3orMoreBtags',
                        '4m':'4orMoreBtags',
                        #mettype:
                        'pf':'patMETsPFlow',
                        'type1':'patType1CorrectedPFMet',
                        #histnames:
                        'unfolded': 'unfolded',
                        'measured': 'measured',
                        'MADGRAPH': 't#bar{t} (MADGRAPH)',
                        'MCATNLO': 't#bar{t} (MC@NLO)',
                        'POWHEG': 't#bar{t} (POWHEG)',
                        'matchingdown': 't#bar{t} (matching down)',
                        'matchingup': 't#bar{t} (matching up)',
                        'scaledown': 't#bar{t} (Q^{2} down)',
                        'scaleup': 't#bar{t} (Q^{2} up)',
                        #variable names
                        'MET': 'E_{T}^{miss}',
                        'HT': 'HT',
                        'ST': 'ST',
                        'MT': 'MT',
                        #systematic sources names
                        'central':'central',
                        'matchingup':'TTJet matching+',
                        'matchingdown':'TTJet matching-',
                        'scaleup':'TTJet scale+',
                        'scaledown':'TTJet scale-',
                        'BJet_down':'BJets-',
                        'BJet_up':'BJets+',
                        'JES_down':'JES+',
                        'JES_up':'JES-',
                        'LightJet_down':'LightJet-',
                        'LightJet_up':'LightJet+',
                        'PU_down':'PileUp+',
                        'PU_up':'PileUp-'
                        }
    (options, args) = parser.parse_args()
    path_to_JSON = options.path
    savePath = options.savePath
    variable = options.variable
    met_type = translateOptions[options.metType]
    k_value = options.k_value
    b_tag_bin = translateOptions[options.bjetbin]
    
    setMETSystematics(met_type)
    
    electron_unfolded_xsections = read_unfolded_xsections('electron')
    muon_unfolded_xsections = read_unfolded_xsections('muon')
    
    print_xsections(electron_unfolded_xsections, 'electron')
    print_xsections(muon_unfolded_xsections, 'muon')
    print_xsections_with_uncertainties(electron_unfolded_xsections, 'electron')
    print_xsections_with_uncertainties(muon_unfolded_xsections, 'muon')

    