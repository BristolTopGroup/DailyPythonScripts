from math import sqrt
from dps.utils.ROOT_utils import get_histograms_from_files
from dps.config.xsection import XSectionConfig

cuts = None
cuts_electrons = [
        "Preselection", #
        "Event cleaning/HLT", #
        "One isolated electron", #
        "Muon veto", #
        "Dilepton veto", #
        "Conversion veto", #
        "$\geq 1$ jets", #
        "$\geq 2$ jets", # 
        "$\geq 3$ jets", #
        "$\geq 4$ jets", #
        "$\geq 1$ b-tagged jets", #
        "$\geq 2$ b-tagged jets" #
        ]

cuts_muons = [
        "Preselection", #
        "Event cleaning/HLT", #
        "One isolated muon", #
        "Second muon veto", #
        "Electron veto", #
        "$\geq 1$ jets", #
        "$\geq 2$ jets", # 
        "$\geq 3$ jets", #
        "$\geq 4$ jets", #
        "$\geq 1$ b-tagged jets", #
        "$\geq 2$ b-tagged jets" #
        ]

def printCutFlow(histograms, selection, luminosity_scale = 1.0, outputFormat='Latex'):
    global cuts
    header = " | Step | TTJet | W+jets | DY + Jets | single top | QCD | Sum MC | Data |"
    row = " | %s  |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d | "
    if outputFormat == 'Latex':
        header = "Selection step & \\ttbar + jets & W + jets & Z + jets & Single-Top & QCD & Sum MC & Data \\\\"
        row = "%s  &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  %d \\\\ "
    print header

    # scale the luminosity
    if luminosity_scale != 1.0:
        for sample, histogram in histograms.iteritems():
            if sample == 'data':
                continue
            histogram[selection].Scale(luminosity_scale)
    
    numbers, errors = getEventNumbers(histograms, selection)
    for step in range(len(cuts)):
        nums = numbers[step]
        errs = errors[step]
        sumMC = nums['TTJet'] + nums['WJets'] + nums['ZJets'] + nums['QCD'] + nums['SingleTop']
        sumMC_err = sqrt(errs['TTJet'] ** 2 + errs['WJets'] ** 2 + errs['ZJets'] ** 2 + errs['SingleTop'] ** 2 + errs['QCD'] ** 2)
        print row % (cuts[step], nums['TTJet'], errs['TTJet'], nums['WJets'], errs['WJets'], nums['ZJets'], errs['ZJets'],
                     nums['SingleTop'], errs['SingleTop'], nums['QCD'], errs['QCD'], sumMC, sumMC_err, nums['data'])

def getEventNumbers(hists, selection):
    global cuts
    eventNumbers = []
    errorValues = []
    for step in range(len(cuts)):
        events = {}
        errors = {}
        for sample in hists.keys():
            events[sample] = hists[sample][selection].GetBinContent(step + 1)
            errors[sample] = hists[sample][selection].GetBinError(step + 1)
        eventNumbers.append(events)
        errorValues.append(errors)
    return eventNumbers, errorValues

if __name__ == '__main__':
    measurement_config = XSectionConfig(8)
    path_to_files = measurement_config.path_to_files + '/central/'
    suffix = ''
    lumi = measurement_config.luminosity
    luminosity_scale = measurement_config.luminosity_scale
    
    data = 'SingleElectron'
    pfmuon = 'PFMuon_'
    histogram_files = {
            'data' : path_to_files + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon),
            'TTJet': path_to_files + 'TTJet_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'WJets': path_to_files + 'WJets_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'ZJets': path_to_files + 'DYJetsToLL_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'QCD': path_to_files + 'QCD_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'SingleTop': path_to_files + 'SingleTop_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix)
    }

    electron_selection = 'EventCount/TTbarEplusJetsRefSelection'
    muon_selection = 'EventCount/TTbarMuPlusJetsRefSelection'

    cuts = cuts_electrons
    histograms = get_histograms_from_files([electron_selection], histogram_files)
    print '='*50
    printCutFlow(histograms, electron_selection, luminosity_scale)

    data = 'SingleMu'
    histogram_files['data'] = path_to_files + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon)
    histogram_files['QCD'] = path_to_files + 'QCD_Muon_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix)
    histograms = get_histograms_from_files([muon_selection], histogram_files)

    cuts = cuts_muons
    print '='*50
    printCutFlow(histograms, muon_selection, luminosity_scale)



