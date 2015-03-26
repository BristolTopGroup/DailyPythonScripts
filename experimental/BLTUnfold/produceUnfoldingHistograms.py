from rootpy.tree import Tree
from rootpy.plotting import Hist, Hist2D, Canvas
from rootpy.io import root_open, File
#from rootpy.interactive import wait
from optparse import OptionParser

from config.variable_binning import bin_edges

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

def getGenVariable( recoVariable ):
    if recoVariable is 'leptonEta':
        return 'pseudoLepton_eta'
    elif recoVariable is ('leptonPt'):
        return 'pseudoLepton_pT'
    elif recoVariable is 'bEta':
        return 'pseudoB_eta'
    elif recoVariable is 'bPt':
        return 'pseudoB_pT'
    else : return 'pseudo'+recoVariable

fileNames = {
             '13TeV' : {
                    'central' : '/storage/ec6821/AnalysisTools/CMSSW_7_4_0_pre7/src/atOutput/tree_TTJet_5000pb_PFElectron_PFMuon_PF2PATJets_MET.root',
                   #  'scaleup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_scaleup_8TeV.root',
                   #  'scaledown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_scaledown_8TeV.root',
                   #  'matchingup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_matchingup_8TeV.root',
                   #  'matchingdown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_matchingdown_8TeV.root',
                   #  'powheg' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_powhegpythia_8TeV.root',
                   #  'powhegherwig' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_powhegherwig_8TeV.root',
                   #  'mcatnlo' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mcatnlo_8TeV.root',
                   # 'massdown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mass_169_5_8TeV.root',
                   # 'massup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mass_173_5_8TeV.root',
                },
             }

channels = [
        channel( 'ePlusJets', 'rootTupleTreeEPlusJets', 'electron'),
        channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon')
        ]

def main():
    
    parser = OptionParser()
    parser.add_option('--topPtReweighting', action='store_true', dest='applyTopPtReweighting', default=False )
    parser.add_option('-c', '--centreOfMassEnergy', dest='centreOfMassEnergy', default=13 )
    parser.add_option('-p', '--pdfWeight', type='int', dest='pdfWeight', default=0 )
    parser.add_option('-s', '--sample', dest='sample', default='central')
    parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False)
    parser.add_option('-n', action='store_true', dest='donothing', default=False)
    parser.add_option('-e', action='store_true', dest='extraHists', default=False)
    parser.add_option('-f',action='store_true', dest='fineBinned', default=False)

    (options, _) = parser.parse_args()

    # Input file name
    file_name = 'crap.root'
    if int(options.centreOfMassEnergy) == 13:
        file_name = fileNames['13TeV'][options.sample]
    else:
        print "Error: Unrecognised centre of mass energy."

    # Output file name
    outputFileName = 'crap.root'
    outputFileDir = 'unfolding/%sTeV/' & options.centreOfMassEnergy

    energySuffix = '%sTeV' % ( options.centreOfMassEnergy )
        
    if options.applyTopPtReweighting:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopPtReweighting.root' % energySuffix
    elif options.pdfWeight != 0:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_pdfWeight_%i.root' % ( energySuffix, options.pdfWeight )
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

            # Keep record of pdf weight
            if options.pdfWeight != 0:
                pdfWeight = '( unfolding.PDFWeights[%i]/unfolding.PDFWeights[0] )' % options.pdfWeight
                pdfWeightHist = Hist( 10, 0.8, 1.2, name='pdfWeights_'+channel.channelName )
                if not options.donothing:
                    tree.Draw( pdfWeight, hist=pdfWeightHist)
                outputDir = 0
                if not ( out.FindObject('pdfWeights') ):
                    outputDir = out.mkdir('pdfWeights')
                else :
                    outputDir = out.Get('pdfWeights')
                outputDir.cd()
                pdfWeightHist.Write()
                pass
                        
            for variable in bin_edges:
                if options.debug and variable != 'HT' : continue
                
                print '--->Doing variable :',variable

                # Output dir name                
                metSuffix='_patType1CorrectedPFMet'
                if variable is 'HT':
                    metSuffix=''
                    pass
                # Make dir in output file
                outputDir = out.mkdir('unfolding_'+variable+'_analyser_'+channel.outputDirName+'_channel'+metSuffix)

                # Variable names in tree
                genSelection = ''
                genSelectionVis = ''
                if channel.channelName is 'muPlusJets' :
                    genSelection = '( isSemiLeptonicMuon )'
                    genSelectionVis = '( isSemiLeptonicMuon && passesGenEventSelection )'
                elif channel.channelName is 'ePlusJets' :
                    genSelection = '( isSemiLeptonicElectron )'
                    genSelectionVis = '( isSemiLeptonicElectron && passesGenEventSelection )'

                genWeight = '( 1 )'
                # genWeight = '( unfolding.puWeight )'
                offlineSelection = ''
                if channel.channelName is 'muPlusJets' :
                    offlineSelection = '( passSelection == 1 )'
                elif channel.channelName is 'ePlusJets' :               
                    offlineSelection = '( passSelection == 0 )'

                # offlineWeight = '( unfolding.bTagWeight * unfolding.puWeight )'
                offlineWeight = '( 1 )'
                fakeSelection = '( ' + offlineSelection+"&&!"+genSelection +' ) '
                fakeSelectionVis = '( ' + offlineSelection+"&&!"+genSelectionVis +' ) '

                recoVariable = variable
                genVariable = getGenVariable( recoVariable )

                # Weights derived from variables in tree
                if options.applyTopPtReweighting:
                    ptWeight = topPtWeight( int(options.centreOfMassEnergy) )
                    offlineWeight += ' * '+ptWeight
                    genWeight += ' * '+ptWeight
                    pass
                
                # Apply pdf weight
                if options.pdfWeight != 0:
                    pdfWeight = '( unfolding.PDFWeights[%i]/unfolding.PDFWeights[0] )' % options.pdfWeight
                    offlineWeight += ' * '+pdfWeight
                    genWeight += ' * '+pdfWeight
                    pass

                # Scale factors
                # scaleFactor = getScaleFactor( options.centreOfMassEnergy, channel.channelName )
                # scaleFactor = '( unfolding.leptonWeight )'
                # offlineWeight += ' * '+scaleFactor

                # Histograms to fill
                # 1D histograms
                truth = Hist( bin_edges[variable], name='truth')
                truthVis = Hist( bin_edges[variable], name='truthVis')
                measured = Hist( bin_edges[variable], name='measured')
                fake = Hist( bin_edges[variable], name='fake')
                
                # 2D histograms
                response = Hist2D( bin_edges[variable], bin_edges[variable], name='response')
                response_without_fakes = Hist2D( bin_edges[variable], bin_edges[variable], name='response_without_fakes')
                response_only_fakes = Hist2D( bin_edges[variable], bin_edges[variable], name='response_only_fakes')

                responseVis_without_fakes = Hist2D( bin_edges[variable], bin_edges[variable], name='responseVis_without_fakes')
                responseVis_only_fakes = Hist2D( bin_edges[variable], bin_edges[variable], name='responseVis_only_fakes')

                if options.fineBinned:
                    minVar = bin_edges[variable][0]
                    maxVar = max( tree.GetMaximum(genVariable), tree.GetMaximum(recoVariable) )
                    nBins = int(maxVar - minVar)

                    if variable is 'leptonEta' or variable is 'bEta':
                        maxVar = 2.5
                        minVar = -2.5
                        nBins = 1000

                    truth = Hist( nBins, minVar, maxVar, name='truth')
                    truthVis = Hist( nBins, minVar, maxVar, name='truthVis')
                    measured = Hist( nBins, minVar, maxVar, name='measured')
                    fake = Hist( nBins, minVar, maxVar, name='fake')
                    response = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response')
                    response_without_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes')
                    response_only_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_only_fakes')
                    responseVis_without_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='responseVis_without_fakes')
                    responseVis_only_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='responseVis_only_fakes')

                # Some interesting histograms
                puOffline = Hist( 20, 0, 2, name='puWeights_offline')
                 
                # Fill histograms
                # 1D
                if not options.donothing:
                    tree.Draw(genVariable,genWeight+'*'+genSelection,hist=truth)
                    tree.Draw(genVariable,genWeight+'*'+genSelectionVis,hist=truthVis)
                    tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measured)
                    tree.Draw(recoVariable,offlineWeight+'*'+fakeSelection,hist=fake)
                    # 2D
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'*'+offlineSelection,hist=response)
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes)
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'*'+fakeSelection,hist=response_only_fakes)

                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'* ('+offlineSelection+'&&'+genSelectionVis +')',hist=responseVis_without_fakes)
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'*'+fakeSelection,hist=responseVis_only_fakes)

                    if options.extraHists:
                        tree.Draw( 'unfolding.puWeight','unfolding.OfflineSelection',hist=puOffline)
                        pass
                
                # Output histgorams to file
                outputDir.cd()
                truth.Write()
                truthVis.Write()
                measured.Write()
                fake.Write()
                response.Write()
                response_without_fakes.Write()
                response_only_fakes.Write()
                responseVis_without_fakes.Write()
                responseVis_only_fakes.Write()

                if options.extraHists:
                    puOffline.Write()
                pass
            pass
        pass
    pass

if __name__ == '__main__':
    main()
