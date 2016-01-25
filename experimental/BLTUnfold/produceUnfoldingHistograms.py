from rootpy.tree import Tree
from rootpy.plotting import Hist, Hist2D, Canvas
from rootpy.io import root_open, File
#from rootpy.interactive import wait
from optparse import OptionParser
from config import XSectionConfig
from config.variable_binning import bin_edges, bin_edges_vis
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
        # channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon')
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
            
            for channel in channels:
                if options.debug and channel.channelName != 'muPlusJets' : continue
                
                print 'Channel : ',channel.channelName

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
                print "Number of entries in tree : ", nEntries

                if meWeight >= 0 :
                    tree.AddFriend('TTbar_plus_X_analysis/Unfolding/GeneratorSystematicWeights')
                    tree.SetBranchStatus('genWeight_*',0)
                    tree.SetBranchStatus('genWeight_%i' % meWeight, 1)

                # Keep record of generator weight
                if meWeight >= 0:
                    generatorWeight = '( genWeight_%i )' % meWeight
                    generatorWeightHist = Hist( 50, 0.4, 1.6, name='generatorWeights_'+channel.channelName )
                    if not options.donothing:
                        tree.Draw( generatorWeight, hist=generatorWeightHist)
                    outputDir = 0
                    if not ( out.FindObject('generatorWeights') ):
                        outputDir = out.mkdir('generatorWeights')
                    else :
                        outputDir = out.Get('generatorWeights')
                    outputDir.cd()
                    generatorWeightHist.Write()
                    pass

                # For variables where you want bins to be symmetric about 0, use abs(variable) (but also make plots for signed variable)
                allVariablesBins = bin_edges.copy()
                for variable in bin_edges:
                    if 'Rap' in variable:
                        allVariablesBins['abs_%s' % variable] = [0,bin_edges[variable][-1]]

                for variable in allVariablesBins:
                    if options.debug and variable != 'HT' : continue

                    if options.sample in measurement_config.met_systematics and variable not in ['MET', 'ST', 'WPT']:
                        continue

                    
                    print '--->Doing variable :',variable

                    # Output dir name                
                    metSuffix='_patType1CorrectedPFMet'
                    if variable is 'HT':
                        metSuffix=''
                        pass
                    # Make dir in output file
                    outputDir = out.mkdir('unfolding_'+variable+'_analyser_'+channel.outputDirName+'_channel'+metSuffix)

                    #
                    # Variable names
                    #
                    recoVariable = branchNames[variable]
                    if variable in ['MET', 'ST', 'WPT']:
                        if options.sample == "jesup":
                            recoVariable += '_METUncertainties[2]'
                        elif options.sample == "jesdown":
                            recoVariable += '_METUncertainties[3]'
                        elif options.sample == "jerup":
                            recoVariable += '_METUncertainties[0]'
                        elif options.sample == "jerdown":
                            recoVariable += '_METUncertainties[1]'
                        elif options.sample in measurement_config.met_systematics:
                            recoVariable += '_METUncertainties[%i]' % measurement_config.met_systematics[options.sample]

                    genVariable_particle = genBranchNames_particle[variable]
                    genVariable_parton = None
                    if variable in genBranchNames_parton:
                        genVariable_parton = genBranchNames_parton[variable]

                    #
                    # Weights and selection
                    #

                    pileupWeight = "PUWeight"
                    if options.sample == "pileupSystematic":
                        pileupWeight = "1"
                    # Generator level
                    genWeight = '( EventWeight * %.4f)' % ( measurement_config.luminosity_scale)
                    # genWeight = '( unfolding.puWeight )'
                    genSelection = ''
                    genSelectionVis = ''
                    if channel.channelName is 'muPlusJets' :
                        genSelection = '( isSemiLeptonicMuon == 1 )'
                        genSelectionVis = '( isSemiLeptonicMuon == 1 && passesGenEventSelection )'
                    elif channel.channelName is 'ePlusJets' :
                        genSelection = '( isSemiLeptonicElectron == 1 )'
                        genSelectionVis = '( isSemiLeptonicElectron == 1 && passesGenEventSelection )'

                    # Offline level
                    # offlineWeight = '( unfolding.bTagWeight * unfolding.puWeight )'
                    leptonWeight = 'LeptonEfficiencyCorrection'
                    if options.sample == 'leptonup':
                        leptonWeight = 'LeptonEfficiencyCorrectionUp'
                    elif options.sample == 'leptondown':
                        leptonWeight == 'LeptonEfficiencyCorrectionDown'

                    bjetWeight = "BJetWeight"
                    if options.sample == "bjetup":
                        bjetWeight = "BJetUpWeight"
                    elif options.sample == "bjetdown":
                        bjetWeight = "BJetDownWeight"

                    # lightjetWeight = "LightJetWeight"
                    # if options.sample == "lightjetup":
                    #     lightjetWeight = "LightJetUpWeight"
                    # elif options.sample == "lightjetdown":
                    #     lightjetWeight = "LightJetDownWeight"

                    # offlineWeight = '( EventWeight * %s * %s * %s * %s * %.4f)' % ( pileupWeight, bjetWeight, lightjetWeight, leptonWeight, measurement_config.luminosity_scale )
                    offlineWeight = '( EventWeight * %s * %s * %s * %.4f)' % ( pileupWeight, bjetWeight, leptonWeight, measurement_config.luminosity_scale )
                    offlineSelection = ''
                    if channel.channelName is 'muPlusJets' :
                        offlineSelection = '( passSelection == 1 )'
                    elif channel.channelName is 'ePlusJets' :               
                        offlineSelection = '( passSelection == 2 )'

                    # Fake selection
                    fakeSelection = '( ' + offlineSelection+"&&!"+genSelection +' ) '
                    fakeSelectionVis = '( ' + offlineSelection+"&&!"+genSelectionVis +' ) '

                    # Weights derived from variables in tree
                    if options.applyTopPtReweighting:
                        ptWeight = topPtWeight( int(options.centreOfMassEnergy) )
                        offlineWeight += ' * '+ptWeight
                        genWeight += ' * '+ptWeight
                        pass
                    
                    # Apply generator weight
                    if meWeight >= 0:
                        genWeight = '( EventWeight * %.4f * genWeight_%s )' %  (measurement_config.luminosity_scale, meWeight)
                        offlineWeight = '( EventWeight * %s * %s * %s * %.4f * genWeight_%s )' % ( pileupWeight, bjetWeight, leptonWeight, measurement_config.luminosity_scale, meWeight )
                        nEntries = 1000000
                        print 'Changing nEntries to ',nEntries, "<---- DOES NOT SEEM TO DO ANYTHING"
                        pass

                    # Scale factors
                    # scaleFactor = getScaleFactor( options.centreOfMassEnergy, channel.channelName )
                    # scaleFactor = '( unfolding.leptonWeight )'
                    # offlineWeight += ' * '+scaleFactor

                    #
                    # Histograms to fill
                    #
                    # 1D histograms
                    truth = Hist( allVariablesBins[variable], name='truth')
                    truthVis = Hist( bin_edges_vis[variable], name='truthVis')
                    truth_parton = Hist( allVariablesBins[variable], name='truth_parton')                
                    measured = Hist( allVariablesBins[variable], name='measured')
                    measuredVis = Hist( bin_edges_vis[variable], name='measuredVis')
                    fake = Hist( allVariablesBins[variable], name='fake')
                    fakeVis = Hist( allVariablesBins[variable], name='fakeVis')
                    # 2D histograms
                    response = Hist2D( allVariablesBins[variable], allVariablesBins[variable], name='response')
                    response_without_fakes = Hist2D( allVariablesBins[variable], allVariablesBins[variable], name='response_without_fakes')
                    response_only_fakes = Hist2D( allVariablesBins[variable], allVariablesBins[variable], name='response_only_fakes')

                    responseVis_without_fakes = Hist2D( bin_edges_vis[variable], bin_edges_vis[variable], name='responseVis_without_fakes')
                    responseVis_only_fakes = Hist2D( bin_edges_vis[variable], bin_edges_vis[variable], name='responseVis_only_fakes')

                    response_parton = Hist2D( allVariablesBins[variable], allVariablesBins[variable], name='response_parton')
                    response_without_fakes_parton = Hist2D( allVariablesBins[variable], allVariablesBins[variable], name='response_without_fakes_parton')
                    response_only_fakes_parton = Hist2D( allVariablesBins[variable], allVariablesBins[variable], name='response_only_fakes_parton')

                    if options.fineBinned:
                        minVar = trunc( allVariablesBins[variable][0] )
                        maxVar = trunc( max( tree.GetMaximum(genVariable_particle), tree.GetMaximum( recoVariable ) ) * 1.2 )
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
                            minVar = -0.5
                            nBins = 21

                        truth = Hist( nBins, minVar, maxVar, name='truth')
                        truthVis = Hist( nBins, minVar, maxVar, name='truthVis')
                        truth_parton = Hist( nBins, minVar, maxVar, name='truth_parton')
                        measured = Hist( nBins, minVar, maxVar, name='measured')
                        measuredVis = Hist( nBins, minVar, maxVar, name='measuredVis')
                        fake = Hist( nBins, minVar, maxVar, name='fake')
                        fakeVis = Hist( nBins, minVar, maxVar, name='fakeVis')
                        response = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response')
                        response_without_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes')
                        response_only_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_only_fakes')
                        responseVis_without_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='responseVis_without_fakes')
                        responseVis_only_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='responseVis_only_fakes')

                        response_parton = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_parton')
                        response_without_fakes_parton = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes_parton')
                        response_only_fakes_parton = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_only_fakes_parton')

                    # Some interesting histograms
                    puOffline = Hist( 20, 0, 2, name='puWeights_offline')
                    eventWeightHist = Hist( 100, -2, 2, name='eventWeightHist')                    
                    genWeightHist = Hist( 100, -2, 2, name='genWeightHist')
                    offlineWeightHist = Hist( 100, -2, 2, name='offlineWeightHist')

                    phaseSpaceInfoHist = Hist( 10, 0, 1, name='phaseSpaceInfoHist')
                    if not options.donothing:
                        nVis = ( tree.Draw( '1', genWeight+'*'+genSelectionVis ) ).Integral()
                        nVisNotOffline = ( tree.Draw( '1', genWeight+'* ( '+genSelectionVis+'&& !'+offlineSelection+')' ) ).Integral()
                        nOffline = ( tree.Draw( '1', offlineWeight+'*'+offlineSelection ) ).Integral()
                        nOfflineNotVis = ( tree.Draw( '1', offlineWeight+'* ( '+offlineSelection+'&& !'+genSelectionVis+')' ) ).Integral()
                        nFull = ( tree.Draw( '1', genWeight+'*'+genSelection ) ).Integral()
                        phaseSpaceInfoHist.SetBinContent(1, nVisNotOffline / nVis)
                        phaseSpaceInfoHist.SetBinContent(2, nOfflineNotVis / nOffline)
                        phaseSpaceInfoHist.SetBinContent(3, nVis / nFull)
                        
                        nOfflineSL = ( tree.Draw( '1', offlineWeight+'* ( '+offlineSelection+'&& '+genSelection+')' ) ).Integral()
                        nSL = ( tree.Draw( '1', offlineWeight+'* ( '+genSelection+')' ) ).Integral()
                        # Selection efficiency for SL ttbar
                        phaseSpaceInfoHist.SetBinContent(4, nOfflineSL / nSL)
                        # Fraction of offline that are SL
                        phaseSpaceInfoHist.SetBinContent(5, nOfflineSL / nOffline)


                    #
                    # Fill histograms
                    #
                    if not options.donothing:
                    #     # 1D

                        tree.Draw(genVariable_particle,genWeight+'*'+genSelection,hist=truth, nentries=nEntries)
                        tree.Draw(genVariable_particle,genWeight+'*'+genSelectionVis,hist=truthVis, nentries=nEntries)
                        # if genVariable_parton != None:
                            # tree.Draw(genVariable_parton,genWeight+'*'+genSelection,hist=truth_parton, nentries=nEntries)
                        tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measured, nentries=nEntries)
                        tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measuredVis, nentries=nEntries)
                        tree.Draw(recoVariable,offlineWeight+'*'+fakeSelection,hist=fake, nentries=nEntries)
                        tree.Draw(recoVariable,offlineWeight+'*'+fakeSelectionVis,hist=fakeVis, nentries=nEntries)
                        # 2D
                        tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'*'+offlineSelection,hist=response, nentries=nEntries)
                        tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes, nentries=nEntries)
                        tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'*'+fakeSelection,hist=response_only_fakes, nentries=nEntries)

                        tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'* ('+offlineSelection+'&&'+genSelectionVis +')',hist=responseVis_without_fakes, nentries=nEntries)
                        tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'*'+fakeSelectionVis,hist=responseVis_only_fakes, nentries=nEntries)

                        # if genVariable_parton != None:
                        #     tree.Draw(recoVariable+':'+genVariable_parton,offlineWeight+'*'+offlineSelection,hist=response_parton)
                        #     tree.Draw(recoVariable+':'+genVariable_parton,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes_parton, nentries=nEntries)
                        #     tree.Draw(recoVariable+':'+genVariable_parton,offlineWeight+'*'+fakeSelection,hist=response_only_fakes_parton, nentries=nEntries)

                        if options.extraHists:
                            tree.Draw('EventWeight',genSelection,hist=eventWeightHist)
                            tree.Draw(genWeight,genSelection,hist=genWeightHist)
                            tree.Draw( offlineWeight,offlineSelection,hist=offlineWeightHist)
                            pass
                    #
                    # Output histgorams to file
                    #
                    outputDir.cd()
                    truth.Write()
                    truthVis.Write()
                    truth_parton.Write()
                    measured.Write()
                    measuredVis.Write()
                    fake.Write()
                    fakeVis.Write()
                    response.Write()
                    response_without_fakes.Write()
                    response_only_fakes.Write()
                    response_parton.Write()
                    response_without_fakes_parton.Write()
                    response_only_fakes_parton.Write()
                    responseVis_without_fakes.Write()
                    responseVis_only_fakes.Write()

                    phaseSpaceInfoHist.Write()
                    genWeightHist.Write()
                    offlineWeightHist.Write()
                    eventWeightHist.Write()
                    if options.extraHists:
                        puOffline.Write()
                    pass
                pass
            pass
        pass

        with root_open( outputFileName, 'update') as out:
            # Done all channels, now combine the two channels, and output to the same file
            for path, dirs, objects in out.walk():
                if 'electron' in path:
                    outputDir = out.mkdir(path.replace('electron','COMBINED'))
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
