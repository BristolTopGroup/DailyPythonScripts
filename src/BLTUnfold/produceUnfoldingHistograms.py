from rootpy.tree import Tree
from rootpy.plotting import Hist, Hist2D, Canvas
from rootpy.io import root_open, File
#from rootpy.interactive import wait
from optparse import OptionParser
from config import XSectionConfig
from config.variable_binning import bin_edges_vis, reco_bin_edges_vis
from config.variableBranchNames import branchNames, genBranchNames_particle, genBranchNames_parton
from tools.file_utilities import make_folder_if_not_exists
from math import trunc

from scaleFactors import *

import ROOT as ROOT
ROOT.gROOT.SetBatch(True)

class channel:
    def __init__(self, channelName, treeName, outputDirName):
        self.channelName = channelName
        self.treeName = treeName
        self.outputDirName = outputDirName
        pass
    pass

def calculateTopPtWeight( lepTopPt, hadTopPt ):
    return max ( ( 1 + ( branch('lepTopPt_parton') - 100 ) / 500 ) * ( 1 + ( branch('hadTopPt_parton') - 100 ) / 500 ) , 0.1 )

def getFileName( com, sample, measurementConfig ) :

    fileNames = {
                 '13TeV' : {
                        'central' : measurementConfig.ttbar_category_templates_trees['central'],
                        'amcatnlo' : measurementConfig.ttbar_amc_category_templates_trees,
                        'madgraph' : measurementConfig.ttbar_madgraph_category_templates_trees,
                        'herwigpp' : measurementConfig.ttbar_herwigpp_category_templates_trees,
                        'scaleup' : measurementConfig.ttbar_scaleup_category_templates_trees,
                        'scaledown' : measurementConfig.ttbar_scaledown_category_templates_trees,
                        'massdown' : measurementConfig.ttbar_mtop1695_category_templates_trees,
                        'massup' : measurementConfig.ttbar_mtop1755_category_templates_trees,
                        'jesdown' : measurementConfig.ttbar_jesdown_category_templates_trees,
                        'jesup' : measurementConfig.ttbar_jesup_category_templates_trees,
                        'jerdown' : measurementConfig.ttbar_jerdown_category_templates_trees,
                        'jerup' : measurementConfig.ttbar_jerup_category_templates_trees,
                        'bjetdown' : measurementConfig.ttbar_category_templates_trees['central'],
                        'bjetup' : measurementConfig.ttbar_category_templates_trees['central'],
                        # 'lightjetdown' : measurementConfig.ttbar_category_templates_trees['central'],
                        # 'lightjetup' : measurementConfig.ttbar_category_templates_trees['central'],
                        'leptondown' : measurementConfig.ttbar_category_templates_trees['central'],
                        'leptonup' : measurementConfig.ttbar_category_templates_trees['central'],
                        'pileupSystematic' : measurementConfig.ttbar_category_templates_trees['central'],

                        'ElectronEnUp' : measurementConfig.ttbar_category_templates_trees['central'],
                        'ElectronEnDown' : measurementConfig.ttbar_category_templates_trees['central'],
                        'MuonEnUp' : measurementConfig.ttbar_category_templates_trees['central'],
                        'MuonEnDown' : measurementConfig.ttbar_category_templates_trees['central'],
                        'TauEnUp' : measurementConfig.ttbar_category_templates_trees['central'],
                        'TauEnDown' : measurementConfig.ttbar_category_templates_trees['central'],
                        'UnclusteredEnUp' : measurementConfig.ttbar_category_templates_trees['central'],
                        'UnclusteredEnDown' : measurementConfig.ttbar_category_templates_trees['central'],
                    },
                 }

    return fileNames[com][sample]

channels = [
        channel( 'ePlusJets', 'rootTupleTreeEPlusJets', 'electron'),
        channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon')
        ]

def main():
    
    parser = OptionParser()
    parser.add_option('--topPtReweighting', action='store_true', dest='applyTopPtReweighting', default=False )
    parser.add_option('-c', '--centreOfMassEnergy', dest='centreOfMassEnergy', type='int', default=13 )
    parser.add_option('--generatorWeight', type='int', dest='generatorWeight', default=-1 )
    parser.add_option('--nGeneratorWeights', type='int', dest='nGeneratorWeights', default=1 )
    parser.add_option('-s', '--sample', dest='sample', default='central')
    parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False)
    parser.add_option('-n', action='store_true', dest='donothing', default=False)
    parser.add_option('-e', action='store_true', dest='extraHists', default=False)
    parser.add_option('-f',action='store_true', dest='fineBinned', default=False)

    (options, _) = parser.parse_args()

    measurement_config = XSectionConfig( options.centreOfMassEnergy )

    # Input file name
    file_name = 'crap.root'
    if int(options.centreOfMassEnergy) == 13:
        # file_name = fileNames['13TeV'][options.sample]
        file_name = getFileName('13TeV', options.sample, measurement_config)
        # if options.generatorWeight >= 0:
        #     file_name = 'localInputFile.root'
    else:
        print "Error: Unrecognised centre of mass energy."

    generatorWeightsToRun = []
    if options.nGeneratorWeights > 1 :
        for i in range (0, options.nGeneratorWeights):
            generatorWeightsToRun.append( options.generatorWeight + i )
    elif options.generatorWeight >= 0 :
        generatorWeightsToRun.append(options.generatorWeight)
    else: generatorWeightsToRun.append( -1 )

    # Output file name
    outputFileName = 'crap.root'
    outputFileDir = 'unfolding/%sTeV/' % options.centreOfMassEnergy
    make_folder_if_not_exists(outputFileDir)
   
    energySuffix = '%sTeV' % ( options.centreOfMassEnergy )

    for meWeight in generatorWeightsToRun :
        if options.applyTopPtReweighting:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopPtReweighting.root' % energySuffix
        elif meWeight == 4:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_scaleUpWeight.root' % ( energySuffix )
        elif meWeight == 8:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_scaleDownWeight.root' % ( energySuffix )
        elif meWeight >= 9 and meWeight <= 108:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_generatorWeight_%i.root' % ( energySuffix, meWeight )
        elif options.sample != 'central':
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_%s_asymmetric.root' % ( energySuffix, options.sample  )
        elif options.fineBinned :
            outputFileName = outputFileDir+'/unfolding_TTJets_%s.root' % ( energySuffix  )
        else:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric.root' % energySuffix

        with root_open( file_name, 'read' ) as f, root_open( outputFileName, 'recreate') as out:
            
                # Get the tree
                treeName = "TTbar_plus_X_analysis/Unfolding/Unfolding"
                if options.sample == "jesup":
                    treeName += "_JESUp"
                elif options.sample == "jesdown":
                    treeName += "_JESDown"
                elif options.sample == "jerup":
                    treeName += "_JERUp"
                elif options.sample == "jerdown":
                    treeName += "_JERDown"

                tree = f.Get(treeName)
                nEntries = tree.GetEntries()
    
                # weightTree = f.Get('TTbar_plus_X_analysis/Unfolding/GeneratorSystematicWeights')
                # if meWeight >= 0 :
                #     tree.AddFriend('TTbar_plus_X_analysis/Unfolding/GeneratorSystematicWeights')
                #     tree.SetBranchStatus('genWeight_*',1)
                #     tree.SetBranchStatus('genWeight_%i' % meWeight, 1)

                # For variables where you want bins to be symmetric about 0, use abs(variable) (but also make plots for signed variable)
                allVariablesBins = bin_edges_vis.copy()
                for variable in bin_edges_vis:
                    if 'Rap' in variable:
                        allVariablesBins['abs_%s' % variable] = [0,bin_edges_vis[variable][-1]]


                recoVariableNames = {}
                genVariable_particle_names = {}
                genVariable_parton_names = {}
                histograms = {}
                outputDirs = {}
                for variable in allVariablesBins:
                    if options.debug and variable != 'HT' : continue

                    if options.sample in measurement_config.met_systematics and variable not in ['MET', 'ST', 'WPT']:
                        continue

                    outputDirs[variable] = {}
                    histograms[variable] = {}

                    #
                    # Variable names
                    #
                    recoVariableName = branchNames[variable]
                    sysIndex = None
                    if variable in ['MET', 'ST', 'WPT']:
                        if options.sample == "jesup":
                            recoVariableName += '_METUncertainties'
                            sysIndex = 2
                        elif options.sample == "jesdown":
                            recoVariableName += '_METUncertainties'
                            sysIndex = 3
                        elif options.sample == "jerup":
                            recoVariableName += '_METUncertainties'
                            sysIndex = 0
                        elif options.sample == "jerdown":
                            recoVariableName+= '_METUncertainties'
                            sysIndex = 1
                        elif options.sample in measurement_config.met_systematics:
                            recoVariableName += '_METUncertainties'
                            sysIndex = measurement_config.met_systematics[options.sample]

                    genVariable_particle_name = genBranchNames_particle[variable]
                    genVariable_parton = None
                    if variable in genBranchNames_parton:
                        genVariable_parton = genBranchNames_parton[variable]

                    recoVariableNames[variable] = recoVariableName
                    genVariable_particle_names[variable] = genVariable_particle_name
                    genVariable_parton_names[variable] = genVariable_parton

                    for channel in channels:
                        # Make dir in output file
                        outputDirName = variable+'_'+channel.outputDirName
                        outputDir = out.mkdir(outputDirName)
                        outputDirs[variable][channel.channelName] = outputDir

                        #
                        # Book histograms
                        #
                        # 1D histograms
                        histograms[variable][channel.channelName] = {}
                        h = histograms[variable][channel.channelName]
                        h['truth'] = Hist( allVariablesBins[variable], name='truth')
                        h['truthVis'] = Hist( allVariablesBins[variable], name='truthVis')
                        h['truth_parton'] = Hist( allVariablesBins[variable], name='truth_parton')                
                        h['measured'] = Hist( reco_bin_edges_vis[variable], name='measured')
                        h['measuredVis'] = Hist( reco_bin_edges_vis[variable], name='measuredVis')
                        h['measured_without_fakes'] = Hist( reco_bin_edges_vis[variable], name='measured_without_fakes')
                        h['measuredVis_without_fakes'] = Hist( reco_bin_edges_vis[variable], name='measuredVis_without_fakes')
                        h['fake'] = Hist( reco_bin_edges_vis[variable], name='fake')
                        h['fakeVis'] = Hist( reco_bin_edges_vis[variable], name='fakeVis')
                        # 2D histograms
                        h['response'] = Hist2D( reco_bin_edges_vis[variable], allVariablesBins[variable], name='response')
                        h['response_without_fakes'] = Hist2D( reco_bin_edges_vis[variable], allVariablesBins[variable], name='response_without_fakes')

                        h['responseVis_without_fakes'] = Hist2D( reco_bin_edges_vis[variable], allVariablesBins[variable], name='responseVis_without_fakes')

                        h['response_parton'] = Hist2D( reco_bin_edges_vis[variable], allVariablesBins[variable], name='response_parton')
                        h['response_without_fakes_parton'] = Hist2D( reco_bin_edges_vis[variable], allVariablesBins[variable], name='response_without_fakes_parton')

                        if options.fineBinned:
                            minVar = trunc( allVariablesBins[variable][0] )
                            maxVar = trunc( max( tree.GetMaximum(genVariable_particle_names[variable]), tree.GetMaximum( recoVariableNames[variable] ) ) * 1.2 )
                            nBins = int(maxVar - minVar)
                            if variable is 'lepton_eta' or variable is 'bjets_eta':
                                maxVar = 2.5
                                minVar = -2.5
                                nBins = 1000
                            elif 'abs' in variable and 'eta' in variable:
                                maxVar = 3.0
                                minVar = 0.
                                nBins = 1000
                            elif 'Rap' in variable:
                                maxVar = 3.0
                                minVar = -3.0
                                nBins = 1000
                            elif 'NJets' in variable:
                                maxVar = 20.5
                                minVar = 3.5
                                nBins = 17

                            h['truth'] = Hist( nBins, minVar, maxVar, name='truth')
                            h['truthVis'] = Hist( nBins, minVar, maxVar, name='truthVis')
                            h['truth_parton'] = Hist( nBins, minVar, maxVar, name='truth_parton')
                            h['measured'] = Hist( nBins, minVar, maxVar, name='measured')
                            h['measuredVis'] = Hist( nBins, minVar, maxVar, name='measuredVis')
                            h['measured_without_fakes'] = Hist( nBins, minVar, maxVar, name='measured_without_fakes')
                            h['measuredVis_without_fakes'] = Hist( nBins, minVar, maxVar, name='measuredVis_without_fakes')
                            h['fake'] = Hist( nBins, minVar, maxVar, name='fake')
                            h['fakeVis'] = Hist( nBins, minVar, maxVar, name='fakeVis')
                            h['response'] = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response')
                            h['response_without_fakes'] = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes')
                            h['responseVis_without_fakes'] = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='responseVis_without_fakes')

                            h['response_parton'] = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_parton')
                            h['response_without_fakes_parton'] = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes_parton')

                        # Some interesting histograms
                        h['puOffline'] = Hist( 20, 0, 2, name='puWeights_offline')
                        h['eventWeightHist'] = Hist( 100, -2, 2, name='eventWeightHist')                    
                        h['genWeightHist'] = Hist( 100, -2, 2, name='genWeightHist')
                        h['offlineWeightHist'] = Hist( 100, -2, 2, name='offlineWeightHist')
     
                        h['phaseSpaceInfoHist'] = Hist( 10, 0, 1, name='phaseSpaceInfoHist')


                # Counters for studying phase space
                nVis = {c.channelName : 0 for c in channels}
                nVisNotOffline = {c.channelName : 0 for c in channels}
                nOffline = {c.channelName : 0 for c in channels}
                nOfflineNotVis = {c.channelName : 0 for c in channels}
                nFull = {c.channelName : 0 for c in channels}
                nOfflineSL = {c.channelName : 0 for c in channels}

                n=0
                # Event Loop
                # for event, weight in zip(tree,weightTree):
                for event in tree:
                    branch = event.__getattr__
                    n+=1
                    if not n%100000: print 'Processing event %.0f Progress : %.2g %%' % ( n, float(n)/nEntries*100 )
                    # # #
                    # # # Weights and selection
                    # # #

                    # Pileup weight
                    # Don't apply if calculating systematic
                    pileupWeight = event.PUWeight
                    if options.sample == "pileupSystematic":
                        pileupWeight = 1

                    # Generator level weight
                    genWeight = event.EventWeight * measurement_config.luminosity_scale

                    # Offline level weights
                    offlineWeight = pileupWeight

                    # Lepton weight
                    leptonWeight = event.LeptonEfficiencyCorrection
                    if options.sample == 'leptonup':
                        leptonWeight = event.LeptonEfficiencyCorrectionUp
                    elif options.sample == 'leptondown':
                        leptonWeight == event.LeptonEfficiencyCorrectionDown

                    # B Jet Weight
                    bjetWeight = event.BJetWeight
                    if options.sample == "bjetup":
                        bjetWeight = event.BJetUpWeight
                    elif options.sample == "bjetdown":
                        bjetWeight = event.BJetDownWeight

                    # # lightjetWeight = "LightJetWeight"
                    # # if options.sample == "lightjetup":
                    # #     lightjetWeight = "LightJetUpWeight"
                    # # elif options.sample == "lightjetdown":
                    # #     lightjetWeight = "LightJetDownWeight"

                    offlineWeight = event.EventWeight * measurement_config.luminosity_scale
                    offlineWeight *= pileupWeight
                    offlineWeight *= bjetWeight
                    offlineWeight *= leptonWeight

                    # Generator weight
                    # Scale up/down, pdf
                    if meWeight >= 0:
                        genWeight *= branch('genWeight_%i' % meWeight)
                        offlineWeight *= branch('genWeight_%i' % meWeight)
                        pass

                    if options.applyTopPtReweighting:
                        ptWeight = calculateTopPtWeight( branch('lepTopPt_parton'), branch('hadTopPt_parton'))
                        offlineWeight *= ptWeight
                        genWeight *= ptWeight

                    for channel in channels:
                        # Generator level selection
                        genSelection = ''
                        genSelectionVis = ''
                        if channel.channelName is 'muPlusJets' :
                            genSelection = event.isSemiLeptonicMuon == 1
                            genSelectionVis = event.isSemiLeptonicMuon == 1 and event.passesGenEventSelection == 1
                        elif channel.channelName is 'ePlusJets' :
                            genSelection = event.isSemiLeptonicElectron == 1
                            genSelectionVis = event.isSemiLeptonicElectron == 1 and event.passesGenEventSelection == 1

                        # Offline level selection
                        offlineSelection = 0
                        if channel.channelName is 'muPlusJets' :
                            offlineSelection = event.passSelection == 1
                        elif channel.channelName is 'ePlusJets' :               
                            offlineSelection = event.passSelection == 2

                        # Fake selection
                        fakeSelection = offlineSelection and not genSelection
                        fakeSelectionVis = offlineSelection and not genSelectionVis

                        # Phase space info
                        if genSelection:
                            nFull[channel.channelName] += genWeight
                            if offlineSelection:
                                nOfflineSL[channel.channelName] += genWeight
                        if genSelectionVis:
                            nVis[channel.channelName] += genWeight
                            if not offlineSelection:
                                nVisNotOffline[channel.channelName] += genWeight
                        if offlineSelection:
                            nOffline[channel.channelName] += offlineWeight
                            if not genSelectionVis:
                                nOfflineNotVis[channel.channelName] += offlineWeight

                        for variable in allVariablesBins:
                            if options.sample in measurement_config.met_systematics and variable not in ['MET', 'ST', 'WPT']:
                                continue
                            # # #
                            # # # Variable to plot
                            # # #
                            recoVariable = branch(recoVariableNames[variable])
                            if variable in ['MET', 'ST', 'WPT'] and \
                            sysIndex != None and ( offlineSelection or fakeSelection or fakeSelectionVis ) :
                                recoVariable = recoVariable[sysIndex]
                            
                            if 'abs' in variable:
                                recoVariable = abs(recoVariable)

                            # With TUnfold, reco variable never goes in the overflow (or underflow)
                            # if recoVariable > allVariablesBins[variable][-1]:
                            #     print 'Big reco variable : ',recoVariable
                            #     print 'Setting to :',min( recoVariable, allVariablesBins[variable][-1] - 0.000001 )
                            if not options.fineBinned:
                                recoVariable = min( recoVariable, allVariablesBins[variable][-1] - 0.000001 )

                            genVariable_particle = branch(genVariable_particle_names[variable])
                            if 'abs' in variable:
                                genVariable_particle = abs(genVariable_particle)
                            # #
                            # # Fill histograms
                            # #
                            histogramsToFill = histograms[variable][channel.channelName]
                            if not options.donothing:

                                if genSelection:
                                    histogramsToFill['truth'].Fill( genVariable_particle, genWeight)

                                if genSelectionVis:
                                    histogramsToFill['truthVis'].Fill( genVariable_particle, genWeight)

                                if offlineSelection:
                                    histogramsToFill['measured'].Fill( recoVariable, offlineWeight)
                                    histogramsToFill['measuredVis'].Fill( recoVariable, offlineWeight)
                                    if genSelectionVis :
                                        histogramsToFill['measuredVis_without_fakes'].Fill( recoVariable, offlineWeight)
                                    if genSelection:
                                        histogramsToFill['measured_without_fakes'].Fill( recoVariable, offlineWeight)
                                    histogramsToFill['response'].Fill( recoVariable, genVariable_particle, offlineWeight )

                                if offlineSelection and genSelection:
                                    histogramsToFill['response_without_fakes'].Fill( recoVariable, genVariable_particle, offlineWeight )
                                elif genSelection:
                                    histogramsToFill['response_without_fakes'].Fill( allVariablesBins[variable][0]-1, genVariable_particle, genWeight )

                                if offlineSelection and genSelectionVis:
                                    histogramsToFill['responseVis_without_fakes'].Fill( recoVariable, genVariable_particle, offlineWeight )
                                elif genSelectionVis:
                                    histogramsToFill['responseVis_without_fakes'].Fill( allVariablesBins[variable][0]-1, genVariable_particle, genWeight )

                                if fakeSelection:
                                    histogramsToFill['fake'].Fill( recoVariable, offlineWeight)

                                if fakeSelectionVis:
                                    histogramsToFill['fakeVis'].Fill( recoVariable, offlineWeight)

                                if options.extraHists:
                                    if genSelection:
                                        histogramsToFill['eventWeightHist'].Fill(event.EventWeight)
                                        histogramsToFill['genWeightHist'].Fill(genWeight)
                                        histogramsToFill['offlineWeightHist'].Fill(offlineWeight)




                #
                # Output histgorams to file
                #
                for variable in allVariablesBins:
                    if options.sample in measurement_config.met_systematics and variable not in ['MET', 'ST', 'WPT']:
                        continue
                    for channel in channels:

                        
                        # Fill phase space info
                        h = histograms[variable][channel.channelName]['phaseSpaceInfoHist']
                        h.SetBinContent(1, nVisNotOffline[channel.channelName] / nVis[channel.channelName])
                        h.SetBinContent(2, nOfflineNotVis[channel.channelName] / nOffline[channel.channelName])
                        h.SetBinContent(3, nVis[channel.channelName] / nFull[channel.channelName])
                        # Selection efficiency for SL ttbar
                        h.SetBinContent(4, nOfflineSL[channel.channelName] / nFull[channel.channelName])
                        # Fraction of offline that are SL
                        h.SetBinContent(5, nOfflineSL[channel.channelName] / nOffline[channel.channelName])

                        outputDirs[variable][channel.channelName].cd()
                        for h in histograms[variable][channel.channelName]:
                            histograms[variable][channel.channelName][h].Write()


        with root_open( outputFileName, 'update') as out:
            # Done all channels, now combine the two channels, and output to the same file
            for path, dirs, objects in out.walk():
                if 'electron' in path:
                    outputDir = out.mkdir(path.replace('electron','combined'))
                    outputDir.cd()
                    for h in objects:
                        h_e = out.Get(path+'/'+h)
                        h_mu = out.Get(path.replace('electron','muon')+'/'+h)
                        h_comb = (h_e + h_mu).Clone(h)
                        h_comb.Write()
                    pass
                pass
            pass

if __name__ == '__main__':
    main()
