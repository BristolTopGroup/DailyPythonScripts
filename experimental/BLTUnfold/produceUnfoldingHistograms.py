from rootpy.tree import Tree
from rootpy.plotting import Hist, Hist2D, Canvas
from rootpy.io import root_open, File
from rootpy.interactive import wait

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
            sfString += '( ( ( unfolding.leptonEta > '+scaleFactor.etaLowEdge+') && ( unfolding.leptonEta < '+scaleFactor.etaHighEdge+') && ( unfolding.leptonPt > '+scaleFactor.ptLowEdge+') && ( unfolding.leptonPt < '+scaleFactor.ptHighEdge+') ) * '+scaleFactor.factor+') '
            firstScaleFactor = False
        else :
            sfString += '+ ( ( ( unfolding.leptonEta > '+scaleFactor.etaLowEdge+') && ( unfolding.leptonEta < '+scaleFactor.etaHighEdge+') && ( unfolding.leptonPt > '+scaleFactor.ptLowEdge+') && ( unfolding.leptonPt < '+scaleFactor.ptHighEdge+') ) * '+scaleFactor.factor+') '

    sfString += ')'
    return sfString


is7TeVData = False

file_name = 'nTuple_53X_mc.root'

outputFileName = 'TestBLTUnfold_nTuple_53X_mc.root'

channels = [
            channel( 'ePlusJets', 'rootTupleTreeEPlusJets', 'electron'),
            channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon')
            ]

with root_open( file_name, 'read' ) as f, root_open( outputFileName, 'recreate') as out:
    for channel in channels:
        for variable in bin_edges:
            for weight in [ 'topPtReweighting', 'allOtherWeights' ]:
                
                applyTopPtReweighting=False
                if weight == 'topPtReweighting':
                    applyTopPtReweighting=True
                    pass
                
                # Get the tree
                tree = f.Get(channel.treeName+'/'+channel.channelName+'Tree')
    
                # Make dir in output file
                metSuffix='_patType1CorrectedPFMet'
                if variable is 'HT':
                    metSuffix=''
                    pass
                
                if applyTopPtReweighting:
                    outputDir = out.mkdir('unfolding_'+variable+'_analyser_'+channel.outputDirName+'_channel'+metSuffix+'_withTopPtReweighting')
                else:
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
                if applyTopPtReweighting:
                    ptWeight = topPtWeight( is7TeVData )
                    offlineWeight += ' * '+ptWeight
                    pass
                
                # Scale factors
                scaleFactor = getScaleFactor( is7TeVData, channel.channelName )
                offlineWeight += ' * '+scaleFactor

                # Histograms to fill
                # 1D histograms
                truth = Hist( bin_edges[variable], name='truth')
                measured = Hist( bin_edges[variable], name='measured')
                fake = Hist( bin_edges[variable], name='fake')
                # 2D histograms
                response = Hist2D( bin_edges[variable], bin_edges[variable], name='response')
                response_without_fakes = Hist2D( bin_edges[variable], bin_edges[variable], name='response_without_fakes')
                
                # Fill histograms
                # 1D
                print '1D'
                print 'Gen'
                tree.Draw(genVariable,genWeight+'*'+genSelection,hist=truth)
                print 'Reco'
                tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measured)
                print 'Fake'
                tree.Draw(recoVariable,offlineWeight+'*'+fakeSelection,hist=fake)
                # 2D
                print 'Response'
                tree.Draw(genVariable+':'+recoVariable,offlineWeight+'*'+offlineSelection,hist=response)
                print 'Response without fakes'
                tree.Draw(genVariable+':'+recoVariable,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes)
                            
                outputDir.cd()
                truth.Write()
                measured.Write()
                fake.Write()
                response.Write()
                response_without_fakes.Write()
                pass
            pass
        pass
    pass
