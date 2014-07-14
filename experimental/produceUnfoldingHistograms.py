from rootpy.tree import Tree
from rootpy.plotting import Hist, Hist2D, Canvas
from rootpy.io import root_open, File
from rootpy.interactive import wait

from config.variable_binning import bin_edges

is7TeVData = False

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

file_name = 'nTuple_53X_mc.root'

outputFileName = 'TestBLTUnfold_nTuple_53X_mc.root'

channels = [
            'ePlusJets',
            'muPlusJets',
            ]

treeDir = {
            'ePlusJets':'rootTupleTreeEPlusJets',
            'muPlusJets':'rootTupleTreeMuPlusJets',
             }

with root_open( file_name, 'read' ) as f, root_open( outputFileName, 'recreate') as out:
    for channel in channels:
        for variable in bin_edges:
            for weight in [ 'topPtReweighting', 'allOtherWeights' ]:
                
                applyTopPtReweighting=False
                if weight == 'topPtReweighting':
                    applyTopPtReweighting=True
                    pass
                
                # Get the tree
                tree = f.Get(treeDir[channel]+'/'+channel+'Tree')
    
                # Make dir in output file
                if applyTopPtReweighting:
                    outputDir = out.mkdir('unfolding_'+variable+'analyser_withTopPtReweighting_'+channel)
                else:
                    outputDir = out.mkdir('unfolding_'+variable+'analyser_'+channel)
                
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
                    offlineWeight += '&&'+ptWeight
                    pass
                    
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
