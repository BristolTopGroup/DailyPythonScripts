from math import sqrt
from tools.ROOT_utililities import get_histograms_from_files

cuts = None
cuts_electrons = [
        "Skim", #
        "Event cleaning and HLT", #
        "Electron", #
        "Muon Veto", #
        "Electron veto", #
        "Conversion veto", #
        "$\geq 3$ jets", #
        "$\geq 4$ jets", #
        "$\geq 1$ CSV b-tag", #
        "$\geq 2$ CSV b-tag" #
        ]

cuts_muons = [
        "Skim", #
        "Event cleaning and HLT", #
        "Muon", #
        "Electron veto", #
        "Muon Veto", #
        "$\geq 3$ jets", #
        "$\geq 4$ jets", #
        "$\geq 1$ CSV b-tag", #
        "$\geq 2$ CSV b-tag" #
        ]

def printCutFlow(histograms, selection, outputFormat='Latex'):
    global cuts
    header = " | Step | TTJet | W+jets | DY + Jets | single top | QCD | Sum MC | Data |"
    row = " | %s  |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d | "
    if outputFormat == 'Latex':
        header = "Selection step & \\ttbar & W + Jets & Z + Jets & Single-top & QCD~  & Sum MC & Data\\\\"
        row = " %s  &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  %d \\\\ "
    print header
    
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
    from config.latex_labels import b_tag_bins_latex, samples_latex
    
    path_to_data = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6/central/'
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6/central/'
    suffix = ''
    lumi = 19584
    data = 'SingleElectron'
    pfmuon = 'PFMuon_'
    histogram_files = {
            'data' : path_to_data + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon),
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
    printCutFlow(histograms, electron_selection)

    data = 'SingleMu'
    histogram_files['data'] = path_to_data + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon)
    histogram_files['QCD'] = path_to_files + 'QCD_Muon_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix)
    histograms = get_histograms_from_files([muon_selection], histogram_files)

    cuts = cuts_muons
    print '='*50
    printCutFlow(histograms, muon_selection)



