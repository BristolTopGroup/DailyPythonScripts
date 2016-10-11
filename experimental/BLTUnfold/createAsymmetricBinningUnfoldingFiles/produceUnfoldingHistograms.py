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
                    'central' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_central_8TeV.root',
                    'scaleup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_scaleup_8TeV.root',
                    'scaledown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_scaledown_8TeV.root',
                    'matchingup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_matchingup_8TeV.root',
                    'matchingdown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_matchingdown_8TeV.root',
                    'powheg' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_8TeV_powheg_v1_pythia.root',
                    'powhegV2pythia' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_8TeV_powheg_v2_pythia.root',
                    'powhegherwig' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_powhegherwig_8TeV.root',
                    'powhegherwig_new' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_powhegherwig_NEW_8TeV.root',
                    'mcatnlo' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mcatnlo_8TeV.root',
                   'massdown' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mass_169_5_8TeV.root',
                   'massup' : '/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mass_173_5_8TeV.root',
                },
             '7TeV' : {
                       'central' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_central_7TeV.root',
                       'scaledown' :'/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_scaledown_7TeV.root',
                       'scaleup' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_scaleup_7TeV.root',
                       'matchingdown' :'/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_matchingdown_7TeV.root',
                       'matchingup' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_matchingup_7TeV.root',
                       'massdown' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mass_169_5_7TeV.root',
                       'massup' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_mass_173_5_7TeV.root',
                       'powheg' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_powhegpythia_7TeV.root',
                       'powhegherwig' : '/hdfs/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/unfolding_TTJets_powhegherwig_7TeV.root',
                       }
             }

channels = [
        channel( 'ePlusJets', 'rootTupleTreeEPlusJets', 'electron'),
        channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon')
        ]

def main():
    
    parser = OptionParser()
    parser.add_option('--topPtReweighting', action='store_true', dest='applyTopPtReweighting', default=False )
    parser.add_option('-c', '--centreOfMassEnergy', dest='centreOfMassEnergy', default=8 )
    parser.add_option('-p', '--pdfWeight', type='int', dest='pdfWeight', default=0 )
    parser.add_option('-s', '--sample', dest='sample', default='central')
    parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False)
    parser.add_option('-n', action='store_true', dest='donothing', default=False)
    parser.add_option('-e', action='store_true', dest='extraHists', default=False)
    parser.add_option('-f',action='store_true', dest='fineBinned', default=False)

    (options, _) = parser.parse_args()

    # Input file name
    file_name = 'crap.root'
    if int(options.centreOfMassEnergy) == 7:
        file_name = fileNames['7TeV'][options.sample]
    elif int(options.centreOfMassEnergy) == 8:
        file_name = fileNames['8TeV'][options.sample]
    else:
        print "Error: Unrecognised centre of mass energy."

    # Output file name
    outputFileName = 'crap.root'
    outputFileDir = 'unfolding/'

    energySuffix = '%sTeV' % ( options.centreOfMassEnergy )
        
    if options.applyTopPtReweighting:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopPtReweighting.root' % energySuffix
    elif options.pdfWeight != 0:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_pdfWeight_%i.root' % ( energySuffix, options.pdfWeight )
    elif options.sample != 'central':
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_%s_asymmetric.root' % ( energySuffix, options.sample  )
    elif options.fineBinned:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s.root' % ( energySuffix  )
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
                scaleFactor = '( unfolding.leptonWeight )'
                offlineWeight += ' * '+scaleFactor

                # Histograms to fill
                # 1D histograms
                truth = Hist( bin_edges[variable], name='truth')
                measured = Hist( bin_edges[variable], name='measured')
                fake = Hist( bin_edges[variable], name='fake')

                h_nJets = Hist([-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5], name='nJets')
                
                h_nJetsG20 = Hist([-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5], name='nJetsG20')
                h_nJetsG30 = Hist([-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5], name='nJetsG30')
                h_htG20 = Hist([i*20 for i in range(5,26)], name='htG20')
                h_htG30 = Hist([i*20 for i in range(5,26)], name='htG30')

                jetPt = Hist([i*2.5 for i in range(8,20)], name='jetPt')

                jetPt1 = Hist([i*5 for i in range(3,40)], name='jetPt1')
                jetPt2 = Hist([i*5 for i in range(3,40)], name='jetPt2')
                jetPt3 = Hist([i*5 for i in range(3,40)], name='jetPt3')
                jetPt4 = Hist([i*5 for i in range(3,40)], name='jetPt4')
                jetPt5 = Hist([i*5 for i in range(3,40)], name='jetPt5')
                jetPt6 = Hist([i*5 for i in range(3,40)], name='jetPt6')
                jetPt7 = Hist([i*5 for i in range(3,40)], name='jetPt7')

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
                    tree.Draw("@(unfolding.jetPt).size()",genWeight+'*'+genSelection,hist=nJets)
                    tree.Draw('unfolding.jetPt',genWeight+'*'+genSelection,hist=jetPt)
                    tree.Draw('unfolding.recoNJets',offlineSelection+'&&'+genSelection,hist=h_nJets)

                    # 2D
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'*'+offlineSelection,hist=response)
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'* ('+offlineSelection+'&&'+genSelection +')',hist=response_without_fakes)
                    tree.Draw(recoVariable+':'+genVariable,offlineWeight+'*'+fakeSelection,hist=response_only_fakes)

                    if options.extraHists:
                        tree.Draw( 'unfolding.puWeight','unfolding.OfflineSelection',hist=puOffline)
                        pass


                # tree.SetBranchStatus('*',0)
                # tree.SetBranchStatus('unfolding.jetPt',1)
                # tree.SetBranchStatus('unfolding.GenSelection',1)
                # tree.SetBranchStatus('unfolding.OfflineSelection',1)
                # print tree.GetEntries()
                # nEvents = 0
                # for event in tree:
                #     nEvents += 1
                #     genSelection = event.__getattr__('unfolding.GenSelection')
                #     offlineSelection = event.__getattr__('unfolding.OfflineSelection')

                #     if genSelection == 1 and offlineSelection == 1 :
                #         jets = event.__getattr__('unfolding.jetPt')
                #         nJetsG20 = 0
                #         nJetsG30 = 0
                #         htG20 = 0
                #         htG30 = 0

                #         if len(jets) > 0 :
                #             jetPt1.Fill(jets[0])
                            
                #             if len(jets) > 1:
                #                 jetPt2.Fill(jets[1])
                                
                #                 if len(jets) > 2:
                #                     jetPt3.Fill(jets[2])
                                    
                #                     if len(jets) > 3:
                #                         jetPt4.Fill(jets[3])
                                        
                #                         if len(jets) > 4:
                #                             jetPt5.Fill(jets[4])
                                            
                #                             if len(jets) > 5:
                #                                 jetPt6.Fill(jets[5])
                                                
                #                                 if len(jets) > 6:
                #                                     jetPt7.Fill(jets[6])
                #         for jetPt in jets:
                #             if jetPt >= 20:
                #                 nJetsG20 += 1
                #                 htG20 += jetPt
                #                 if jetPt >= 30:
                #                     nJetsG30 += 1
                #                     htG30 += jetPt
                #         h_nJetsG20.Fill(nJetsG20)
                #         h_nJetsG30.Fill(nJetsG30)
                #         h_htG20.Fill(htG20)
                #         h_htG30.Fill(htG30)
                #     if nEvents > 100000 : break
                # Output histgorams to file
                outputDir.cd()
                # truth.Scale(1/truth.Integral())
                truth.Write()
                measured.Write()

                # h_nJetsG20.Scale(1/h_nJetsG20.Integral())
                # h_nJetsG30.Scale(1/h_nJetsG30.Integral())
                # h_htG20.Scale(1/h_htG20.Integral())
                # h_htG30.Scale(1/h_htG30.Integral())

                h_nJets.Write()
                h_nJetsG20.Write()
                h_nJetsG30.Write()
                h_htG20.Write()
                h_htG30.Write()

                jetPt1.Write()
                jetPt2.Write()
                jetPt3.Write()
                jetPt4.Write()
                jetPt5.Write()
                jetPt6.Write()
                jetPt7.Write()

                # jetPt.Scale( 1/jetPt.Integral() )
                # jetPt.Write()
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
