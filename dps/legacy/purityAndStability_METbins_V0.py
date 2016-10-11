'''
Created on Aug 1, 2012

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''

import FILES
import dps.utils.ROOTFileReader as FileReader
from ROOT import gROOT

fileTemplate = 'data/correctionFactors/correctionFactors_%s_%s_JSON.txt'
samples = [
        'TTJet',
        'POWHEG',
        'PYTHIA6',
        'MCatNLO',
        'TTJets-matchingdown',
        'TTJets-matchingup',
        'TTJets-scaledown',
        'TTJets-scaleup',
         ]

metbins = [
        '0-25',
        '25-45',
        '45-70',
        '70-100',
        '100-inf'
        ]

metTypes = ['PFMET', 'patType1CorrectedPFMet', 'patType1p2CorrectedPFMet' ]
metsystematics_sources = [
        "patType1p2CorrectedPFMetElectronEnUp",
        "patType1p2CorrectedPFMetElectronEnDown",
        "patType1p2CorrectedPFMetMuonEnUp",
        "patType1p2CorrectedPFMetMuonEnDown",
        "patType1p2CorrectedPFMetTauEnUp",
        "patType1p2CorrectedPFMetTauEnDown",
        "patType1p2CorrectedPFMetJetResUp",
        "patType1p2CorrectedPFMetJetResDown",
        "patType1p2CorrectedPFMetJetEnUp",
        "patType1p2CorrectedPFMetJetEnDown",
        "patType1p2CorrectedPFMetUnclusteredEnUp",
        "patType1p2CorrectedPFMetUnclusteredEnDown",
        "patType1CorrectedPFMetElectronEnUp",
        "patType1CorrectedPFMetElectronEnDown",
        "patType1CorrectedPFMetMuonEnUp",
        "patType1CorrectedPFMetMuonEnDown",
        "patType1CorrectedPFMetTauEnUp",
        "patType1CorrectedPFMetTauEnDown",
        "patType1CorrectedPFMetJetResUp",
        "patType1CorrectedPFMetJetResDown",
        "patType1CorrectedPFMetJetEnUp",
        "patType1CorrectedPFMetJetEnDown",
        "patType1CorrectedPFMetUnclusteredEnUp",
        "patType1CorrectedPFMetUnclusteredEnDown",
        "patPFMetElectronEnUp",
        "patPFMetElectronEnDown",
        "patPFMetMuonEnUp",
        "patPFMetMuonEnDown",
        "patPFMetTauEnUp",
        "patPFMetTauEnDown",
        "patPFMetJetResUp",
        "patPFMetJetResDown",
        "patPFMetJetEnUp",
        "patPFMetJetEnDown",
        "patPFMetUnclusteredEnUp",
        "patPFMetUnclusteredEnDown",
                      ]
metTypes.extend(metsystematics_sources)


def getMETVariables(analysisType, sample, metType, bjetbin):
    base = 'TTbarPlusMetAnalysis/' + analysisType + '/Ref selection/BinnedMETAnalysis/'
    analyser = 'Electron_%s_bin_%s/electron_AbsEta_%s'
    if 'Mu' in analysisType:
        analyser = 'Muon_%s_bin_%s/muon_AbsEta_%s'
    correctionFactors = {}
    purities = {}
    stabilities = {}
    numberOfGenEvents = {}
    numberOfRecoEvents = {}
    for metbin in metbins:
            genMET = base + analyser % ('GenMET', metbin, bjetbin)
            PFMET = base + analyser % (metType, metbin, bjetbin)
            genMETs = FileReader.getHistogramFromFile(genMET, FILES.files[sample])
            PFMETs = FileReader.getHistogramFromFile(PFMET, FILES.files[sample])
            N_gen = genMETs.Integral()
            N_reco = PFMETs.Integral()
            purity = (N_gen + N_reco) / N_reco
            stability = (N_gen + N_reco) / N_gen
            correctionFactor = N_gen / N_reco
            
            correctionFactors[metbin] = correctionFactor
            purities[metbin] = purity
            stabilities[metbin] = stability
            numberOfGenEvents[metbin] = N_gen
            numberOfRecoEvents[metbin] = N_reco
    result = {
              'correctionFactors': correctionFactors,
              'purities': purities,
              'stabilities': stabilities,
              'numberOfGenEvents': numberOfGenEvents,
              'numberOfRecoEvents':numberOfRecoEvents
              }
    return result

def saveToFile(correctionFactors, analysisType, bjetbin):
    stringForFile = ''
    fileName = fileTemplate % (analysisType, bjetbin)
    stringForFile += str(correctionFactors) + '\n'
    import json
    stringForFile =  json.dumps(correctionFactors, sort_keys=True, indent=4)
    outputFile = open(fileName, 'w')
    outputFile.write(stringForFile)
    outputFile.close()
        
    
if __name__ == "__main__":
    from optparse import OptionParser
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
   
    
    parser = OptionParser()
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-a", "--analysisType", dest="analysisType", default='EPlusJets',
                  help="set analysis type: EPlusJets or MuPlusJets")
    parser.add_option("-t", "--test",
                  action="store_true", dest="test", default=False,
                  help="Run test")
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
                        }
    
    (options, args) = parser.parse_args()
    bjetbin = translateOptions[options.bjetbin]
    analysisType = options.analysisType
#    base = 'TTbarPlusMetAnalysis/' + analysisType + '/Ref selection/BinnedMETAnalysis/'
    
#    bjetbin = '2orMoreBtags'
#    bjetbins = ['0orMoreBtags', '1orMoreBtags', '2orMoreBtags']
#    metType = 'PFMET'
    
    correctionFactors = {}
    for sample in samples:
        correctionFactors[sample] = {}
        for metType in metTypes:
            variables = getMETVariables(analysisType, sample, metType, bjetbin)
            correctionFactors[sample][metType] = variables['correctionFactors']
    saveToFile(correctionFactors, analysisType, bjetbin)
    
