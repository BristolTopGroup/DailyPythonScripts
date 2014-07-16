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
            sfString += '( ( ( unfolding.leptonEta > '+scaleFactor.etaLowEdge+') && ( unfolding.leptonEta < '+scaleFactor.etaHighEdge+') && ( unfolding.leptonPt > '+scaleFactor.ptLowEdge+') && ( unfolding.leptonPt < '+scaleFactor.ptHighEdge+') ) * '+scaleFactor.factor+') '
            firstScaleFactor = False
        else :
            sfString += '+ ( ( ( unfolding.leptonEta > '+scaleFactor.etaLowEdge+') && ( unfolding.leptonEta < '+scaleFactor.etaHighEdge+') && ( unfolding.leptonPt > '+scaleFactor.ptLowEdge+') && ( unfolding.leptonPt < '+scaleFactor.ptHighEdge+') ) * '+scaleFactor.factor+') '

    sfString += ')'
    return sfString


file_name = '/hdfs/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/BLT/BLTUnfoldTest2/TTJets_MassiveBinDECAY_TuneZ2star_8TeV/TTJets_nTuple_53X_mc_merged.root'


channels = [
        channel( 'ePlusJets', 'rootTupleTreeEPlusJets', 'electron'),
        channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon')
        ]

def main():
    
    parser = OptionParser()
    parser.add_option('--topPtReweighting', action='store_true', dest='applyTopPtReweighting', default=False )
    parser.add_option('--is7TeV', action='store_true', dest='is7TeVData', default=False )
    parser.add_option('-p', '--pdfWeight', type='int', dest='pdfWeight', default=0 )
    (options, _) = parser.parse_args()

    # Output file name
    outputFileName = 'crap.root'
    if options.applyTopPtReweighting:
        outputFileName = 'TestBLTUnfold_nTuple_53X_mc_withTopPtReweighting.root'
    elif options.pdfWeight != 0:
        outputFileName = 'TestBLTUnfold_nTuple_53X_mc_pdfWeight_%i.root' % options.pdfWeight
    else:
        outputFileName = 'TestBLTUnfold_nTuple_53X_mc.root'
        
    with root_open( file_name, 'read' ) as f, root_open( outputFileName, 'recreate') as out:
        for channel in channels:
            print 'Channel : ',channel.channelName

            # Get the tree
            tree = f.Get(channel.treeName+'/'+channel.channelName+'Tree')

            # Keep record of pdf weight
            if options.pdfWeight != 0:
                pdfWeight = '( unfolding.PDFWeights[%i]/unfolding.PDFWeights[0] )' % options.pdfWeight
                pdfWeightHist = Hist( 10, 0.8, 1.2, name='pdfWeights_'+channel.channelName )
                tree.Draw( pdfWeight, hist=pdfWeightHist)
                outputDir = out.mkdir('pdfWeights')
                outputDir.cd()
                pdfWeightHist.Write()
                pass
                        
            for variable in bin_edges:
                if variable != 'HT': continue
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
                scaleFactor = getScaleFactor( options.is7TeVData, channel.channelName )
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
                tree.Draw(genVariable,genWeight+'*'+genSelection,hist=truth)
                tree.Draw(recoVariable,offlineWeight+'*'+offlineSelection,hist=measured)
                tree.Draw(recoVariable,offlineWeight+'*'+fakeSelection,hist=fake)
                # 2D
                tree.Draw(genVariable+':'+recoVariable,offlineWeight+'*'+offlineSelection,hist=response)
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

if __name__ == '__main__':
    main()