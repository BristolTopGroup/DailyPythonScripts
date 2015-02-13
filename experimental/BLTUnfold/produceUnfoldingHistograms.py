from rootpy.tree import Tree
from rootpy.plotting import Hist, Hist2D, Canvas
from rootpy.io import root_open, File
from rootpy.interactive import wait
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
def topPtWeight( is7TeV ):
    
    if is7TeV:
        return 'sqrt( exp(0.174-0.00137*unfolding.hadronicTopPt) * exp(0.174-0.00137*unfolding.leptonicTopPt) )'
    else:
        return 'sqrt( exp(0.159-0.00141*unfolding.hadronicTopPt) * exp(0.159-0.00141*unfolding.leptonicTopPt) )'

# Get the lepton scale factors
def getScaleFactor( is7TeV, channelName ):
    if is7TeV:
        if channelName is 'ePlusJets':
            return '(1)'
        else:
            return convertScaleFactorsToString(muon7TeVScaleFactors)
    else:
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

def copyEventFilterHist( inputFile, outputFile ):
    eventFilter = inputFile.Get('EventFilter/EventCounter')
    outputFile.cd()
    eventFilterOutputDir = outputFile.mkdir('EventFilter')
    eventFilterOutputDir.cd()
    eventFilter.Write()
    inputFile.cd()
    pass


fileNames = {
             '8TeV' : {
                    'central' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TTJets_central_8.root',
                    'scaleup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TTJets_scaleup_8.root',
                    'scaledown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TTJets_scaledown_8.root',
                    'matchingup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TTJets_matchingup_8.root',
                    'matchingdown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TTJets_matchingdown_8.root',
                    'powheg' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TT_powhegPythia_8.root',
                    'powhegherwig' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TT_powhegHerwig_8.root',
                    'mcatnlo' : '/hdfs/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/BLT/TTJets_mcatnlo_8.root',
                   'massdown' : '/hdfs/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/BLT/TTJets_mass1695_8.root',
                   'massup' : '/hdfs/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/BLT/TTJets_mass1735_8.root',
                },
             '7TeV' : {
                       'central' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_central.root',
                       'scaledown' :'/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_scaledown.root',
                       'scaleup' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_scaleup.root',
                       'matchingdown' :'/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_matchingdown.root',
                       'matchingup' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_matchingup.root',
                       'massdown' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_mass1695.root',
                       'massup' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TTJets_mass1735.root',
                       'powheg' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TT_powheg_pythia.root',
                       'powhegherwig' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/TT_powheg_herwig.root',
                       }
             }

channels = [
        channel( 'ePlusJets', 'rootTupleTreeEPlusJets', 'electron'),
        channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon')
        ]

def main():
    
    parser = OptionParser()
    parser.add_option('--topPtReweighting', action='store_true', dest='applyTopPtReweighting', default=False )
    parser.add_option('--is7TeV', action='store_true', dest='is7TeVData', default=False )
    parser.add_option('-p', '--pdfWeight', type='int', dest='pdfWeight', default=0 )
    parser.add_option('-s', '--sample', dest='sample', default='central')
    parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False)
    parser.add_option('-n', action='store_true', dest='donothing', default=False)
    parser.add_option('-e', action='store_true', dest='extraHists', default=False)
    parser.add_option('-f',action='store_true', dest='fineBinned', default=False)

    (options, _) = parser.parse_args()



    # Input file name
    file_name = 'crap.root'
    if options.is7TeVData:
        file_name = fileNames['7TeV'][options.sample]
    else:
        file_name = fileNames['8TeV'][options.sample]
    
    # Output file name
    outputFileName = 'crap.root'
    outputFileDir = 'unfolding/'
    energySuffix = '8TeV'
    if options.is7TeVData:
        energySuffix = '7TeV'
        
    if options.applyTopPtReweighting:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopPtReweighting.root' % energySuffix
    elif options.pdfWeight != 0:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_pdfWeight_%i.root' % ( energySuffix, options.pdfWeight )
    elif options.sample != 'central':
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_%s_asymmetric.root' % ( energySuffix, options.sample  )
    else:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric.root' % energySuffix

    with root_open( file_name, 'read' ) as f, root_open( outputFileName, 'recreate') as out:
        
        copyEventFilterHist( f, out )
        
        for channel in channels:
            if options.debug and channel.channelName != 'muPlusJets' : continue
            
            print 'Channel : ',channel.channelName

            # Get the tree
            tree = f.Get(channel.treeName+'/'+channel.channelName+'Tree')

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
                genSelection = '( unfolding.GenSelection == 1 )'
                genWeight = '( unfolding.puWeight )'
                offlineSelection = '( unfolding.OfflineSelection == 1 )'
                offlineWeight = '( unfolding.bTagWeight * unfolding.puWeight )'
                fakeSelection = '( ' + offlineSelection+"&&!"+genSelection +' ) '
                genVariable = 'unfolding.gen'+variable
                recoVariable = 'unfolding.reco'+variable

                # Weights derived from variables in tree
                if options.applyTopPtReweighting:
                    ptWeight = topPtWeight( options.is7TeVData )
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
                # scaleFactor = getScaleFactor( options.is7TeVData, channel.channelName )
                scaleFactor = '( unfolding.leptonWeight )'
                offlineWeight += ' * '+scaleFactor

                # Histograms to fill
                # 1D histograms
                truth = Hist( bin_edges[variable], name='truth')
                measured = Hist( bin_edges[variable], name='measured')
                fake = Hist( bin_edges[variable], name='fake')
                
                # 2D histograms
                response = Hist2D( bin_edges[variable], bin_edges[variable], name='response')
                response_without_fakes = Hist2D( bin_edges[variable], bin_edges[variable], name='response_without_fakes')
                response_only_fakes = Hist2D( bin_edges[variable], bin_edges[variable], name='response_only_fakes')      

                if options.fineBinned:
                    minVar = bin_edges[variable][0]
                    maxVar = bin_edges[variable][-1]
                    nBins = int(maxVar - minVar)
                    truth = Hist( nBins, minVar, maxVar, name='truth')
                    measured = Hist( nBins, minVar, maxVar, name='measured')
                    fake = Hist( nBins, minVar, maxVar, name='fake')
                    response = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response')
                    response_without_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes')
                    response_only_fakes = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_only_fakes')
                    
                # Some interesting histograms
                puOffline = Hist( 20, 0, 2, name='puWeights_offline')
                 
                # Fill histograms
                # 1D
                if not options.donothing:
                    tree.Draw(genVariable,genWeight+'*'+genSelection,hist=truth)
                    tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measured)
                    tree.Draw(recoVariable,offlineWeight+'*'+fakeSelection,hist=fake)
                    # 2D
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'*'+offlineSelection,hist=response)
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes)
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'*'+fakeSelection,hist=response_only_fakes)

                    if options.extraHists:
                        tree.Draw( 'unfolding.puWeight','unfolding.OfflineSelection',hist=puOffline)
                        pass
                
                # Output histgorams to file
                outputDir.cd()
                truth.Write()
                measured.Write()
                fake.Write()
                response.Write()
                response_without_fakes.Write()
                response_only_fakes.Write()
                if options.extraHists:
                    puOffline.Write()
                pass
            pass
        pass
    pass

if __name__ == '__main__':
    main()