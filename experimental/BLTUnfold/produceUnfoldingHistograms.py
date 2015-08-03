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

class channel:
    def __init__(self, channelName, treeName, outputDirName):
        self.channelName = channelName
        self.treeName = treeName
        self.outputDirName = outputDirName
        pass
    pass

# For debug
def setup_canvas():
    canvas = Canvas(width=700, height=500)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.10)
    canvas.SetRightMargin(0.05)
    return canvas

# Top pt weight
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting
def topPtWeight( centreOfMassEnergy ):
    
    if centreOfMassEnergy == 7:
        return 'sqrt( exp(0.174-0.00137*unfolding.hadronicTopPt) * exp(0.174-0.00137*unfolding.leptonicTopPt) )'
    elif centreOfMassEnergy == 8:
        return 'sqrt( exp(0.159-0.00141*unfolding.hadronicTopPt) * exp(0.159-0.00141*unfolding.leptonicTopPt) )'
    else:
        print "Error: unrecognised centre of mass energy."

# Get the lepton scale factors
def getScaleFactor( centreOfMassEnergy, channelName ):
    if centreOfMassEnergy == 7:
        if channelName is 'ePlusJets':
            return '(1)'
        else:
            return convertScaleFactorsToString(muon7TeVScaleFactors)
    elif centreOfMassEnergy == 8:
        if channelName is 'ePlusJets':
            return convertScaleFactorsToString(electron8TeVScaleFactors)
        else:
            return convertScaleFactorsToString(muon8TeVScaleFactors)
    pass

# Convert the scale factors into a string for Tree::Draw
def convertScaleFactorsToString( scaleFactors ):
    firstScaleFactor = True
    sfString = '( '
    for scaleFactor in scaleFactors:
        if ( firstScaleFactor ):
            sfString += '( ( ( abs( unfolding.leptonEta ) > '+scaleFactor.etaLowEdge+') && ( abs( unfolding.leptonEta ) < '+scaleFactor.etaHighEdge+') && ( unfolding.leptonPt > '+scaleFactor.ptLowEdge+') && ( unfolding.leptonPt < '+scaleFactor.ptHighEdge+') ) * '+scaleFactor.factor+') '
            firstScaleFactor = False
        else :
            sfString += '+ ( ( ( abs( unfolding.leptonEta ) > '+scaleFactor.etaLowEdge+') && ( abs( unfolding.leptonEta ) < '+scaleFactor.etaHighEdge+') && ( unfolding.leptonPt > '+scaleFactor.ptLowEdge+') && ( unfolding.leptonPt < '+scaleFactor.ptHighEdge+') ) * '+scaleFactor.factor+') '

    sfString += ')'
    return sfString

def getgenVariable_particle( recoVariable ):
    if recoVariable is 'leptonEta':
        return 'pseudoLepton_eta'
    elif recoVariable is ('leptonPt'):
        return 'pseudoLepton_pT'
    elif recoVariable is 'bEta':
        return 'pseudoB_eta'
    elif recoVariable is 'bPt':
        return 'pseudoB_pT'
    else : return 'pseudo'+recoVariable

def getFileName( com, sample, measurementConfig ) :

    fileNames = {
                 '13TeV' : {
                        'central' : measurementConfig.ttbar_category_templates_trees['central'],
                        'amcatnlo' : measurementConfig.ttbar_amc_category_templates_trees,
                        'madgraph' : measurementConfig.ttbar_madgraph_category_templates_trees,
                        'scaleup' : measurementConfig.ttbar_scaleup_category_templates_trees,
                        'scaledown' : measurementConfig.ttbar_scaledown_category_templates_trees,
                        'massdown' : measurementConfig.ttbar_mtop1695_category_templates_trees,
                        'massup' : measurementConfig.ttbar_mtop1755_category_templates_trees,
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
        print getFileName('13TeV', options.sample, measurement_config)
    else:
        print "Error: Unrecognised centre of mass energy."

    # Output file name
    outputFileName = 'crap.root'
    outputFileDir = 'unfolding/%sTeV/' % options.centreOfMassEnergy
    make_folder_if_not_exists(outputFileDir)
   
    energySuffix = '%sTeV' % ( options.centreOfMassEnergy )
        
    if options.applyTopPtReweighting:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopPtReweighting.root' % energySuffix
    elif options.generatorWeight >= 0:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_generatorWeight_%i.root' % ( energySuffix, options.generatorWeight )
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
            tree = f.Get("TTbar_plus_X_analysis/Unfolding/Unfolding")

            print "Number of entries in tree : ", tree.GetEntries()

            # Keep record of generator weight
            # if options.generatorWeight >= 0:
            #     generatorWeight = '( generatorSystematicWeight[%i] )' % options.generatorWeight
            #     generatorWeightHist = Hist( 10, 0.8, 1.2, name='generatorWeights_'+channel.channelName )
            #     if not options.donothing:
            #         tree.Draw( generatorWeight, hist=generatorWeightHist)
            #     outputDir = 0
            #     if not ( out.FindObject('generatorWeights') ):
            #         outputDir = out.mkdir('generatorWeights')
            #     else :
            #         outputDir = out.Get('generatorWeights')
            #     outputDir.cd()
            #     generatorWeightHist.Write()
            #     pass

            # For variables where you want bins to be symmetric about 0, use abs(variable) (but also make plots for signed variable)
            allVariablesBins = bin_edges.copy()
            for variable in bin_edges:
                if 'Rap' in variable or 'eta' in variable:
                    allVariablesBins['abs_%s' % variable] = [0,bin_edges[variable][-1]]

            for variable in allVariablesBins:
                if options.debug and variable != 'HT' : continue
                
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
                genVariable_particle = genBranchNames_particle[variable]
                genVariable_parton = None
                if variable in genBranchNames_parton:
                    genVariable_parton = genBranchNames_parton[variable]

                #
                # Weights and selection
                #
                
                # Generator level
                genWeight = '( EventWeight * %.4f)' % measurement_config.luminosity_scale
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
                leptonWeight = '1'

                offlineWeight = '( EventWeight * %s * %.4f)' % ( leptonWeight, measurement_config.luminosity_scale )
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
                if options.generatorWeight >= 0:
                    generatorWeight = '( generatorSystematicWeight[%i] )' % options.generatorWeight
                    offlineWeight += ' * '+generatorWeight
                    genWeight += ' * '+generatorWeight
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
                eventWeight = Hist( 100, -2, 2, name='EventWeight')
                 
                #
                # Fill histograms
                #
                if not options.donothing:
                    tree.Draw('(EventWeight * %.4f)' % measurement_config.luminosity_scale,'1',hist=eventWeight)
                    # 1D
                    tree.Draw(genVariable_particle,genWeight+'*'+genSelection,hist=truth)
                    tree.Draw(genVariable_particle,genWeight+'*'+genSelectionVis,hist=truthVis)
                    if genVariable_parton != None:
                        tree.Draw(genVariable_parton,genWeight+'*'+genSelection,hist=truth_parton)
                    tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measured)
                    tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measuredVis)
                    tree.Draw(recoVariable,offlineWeight+'*'+fakeSelection,hist=fake)
                    # 2D
                    tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'*'+offlineSelection,hist=response)
                    tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes)
                    tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'*'+fakeSelection,hist=response_only_fakes)

                    tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'* ('+offlineSelection+'&&'+genSelectionVis +')',hist=responseVis_without_fakes)
                    tree.Draw(recoVariable+':'+genVariable_particle,offlineWeight+'*'+fakeSelection,hist=responseVis_only_fakes)

                    if genVariable_parton != None:
                        tree.Draw(recoVariable+':'+genVariable_parton,offlineWeight+'*'+offlineSelection,hist=response_parton)
                        tree.Draw(recoVariable+':'+genVariable_parton,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes_parton)
                        tree.Draw(recoVariable+':'+genVariable_parton,offlineWeight+'*'+fakeSelection,hist=response_only_fakes_parton)

                    if options.extraHists:
                        tree.Draw( 'unfolding.puWeight','unfolding.OfflineSelection',hist=puOffline)
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
                response.Write()
                response_without_fakes.Write()
                response_only_fakes.Write()
                response_parton.Write()
                response_without_fakes_parton.Write()
                response_only_fakes_parton.Write()
                responseVis_without_fakes.Write()
                responseVis_only_fakes.Write()

                eventWeight.Write()
                if options.extraHists:
                    puOffline.Write()
                pass
            pass
        pass
    pass

if __name__ == '__main__':
    main()
