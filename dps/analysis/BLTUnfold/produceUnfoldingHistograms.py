from __future__ import division
from rootpy.plotting import Hist, Hist2D
from rootpy.io import root_open
#from rootpy.interactive import wait
from argparse import ArgumentParser
from dps.config.xsection import XSectionConfig
from dps.config.variable_binning import bin_edges_vis, reco_bin_edges_vis
from dps.config.variableBranchNames import branchNames, genBranchNames_particle, genBranchNames_parton
from dps.utils.file_utilities import make_folder_if_not_exists
from math import trunc, exp, sqrt
import numpy as np
import glob

import ROOT as ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine( 'gErrorIgnoreLevel = 2001;' )

class channel:
    def __init__(self, channelName, treeName, outputDirName):
        self.channelName = channelName
        self.treeName = treeName
        self.outputDirName = outputDirName
        pass
    pass

def calculateTopEtaWeight( lepTopRap, hadTopRap, whichWayToWeight = 1):
    if whichWayToWeight == -1 :
        return max ( (-0.24 * abs(lepTopRap) + 1.24) * (-0.24 * abs(hadTopRap) + 1.24), 0.1 )
    elif whichWayToWeight == 1 :
        return max ( ( 0.24 * abs(lepTopRap) + 0.76) * ( 0.24 * abs(hadTopRap) + 0.76), 0.1 )
    else :
        return 1

def calculateTopPtWeight( lepTopPt, hadTopPt, whichWayToWeight = 1 ):
    if whichWayToWeight == -1 :
        return max ( (-0.001 * lepTopPt + 1.1 ) * (-0.001 * hadTopPt + 1.1), 0.1 )
    elif whichWayToWeight == 1 :
        return max ( (0.001 * lepTopPt + 0.9 ) * (0.001 * hadTopPt + 0.9), 0.1 )
    else :
        return 1

def calculateTopPtSystematicWeight( lepTopPt, hadTopPt ):
    '''
    Calculating the top pt weight
         ______________            A + B.Pt
    W = / SF(t)SF(tbar) , SF(t) = e

    A = 0.0615
    B = -0.0005
    '''     
    lepTopWeight = ptWeight( lepTopPt )
    hadTopWeight = ptWeight( hadTopPt )
    return sqrt( lepTopWeight * hadTopWeight )
 
def ptWeight( pt ):
    return exp( 0.0615 - 0.0005 * pt ) 
 

def calculateTopPtSystematicWeight( lepTopPt, hadTopPt ):
    lepTopWeight = ptWeight( lepTopPt )
    hadTopWeight = ptWeight( hadTopPt )
    return sqrt( lepTopWeight * hadTopWeight )

def ptWeight( pt ):
    return exp( 0.0615 - 0.0005 * pt )

def getUnmergedDirectory( f ) :
    baseDir = f.split('combined')[0]
    sampleName = f.split('combined')[-1].strip('/').split('_tree.root')[0]
    print baseDir
    print sampleName

    if 'TTJets_amc' in sampleName:
        sampleName = 'TTJets_amcatnloFXFX'
    elif 'TTJets_madgraph' in sampleName:
        sampleName = 'TTJets_madgraphMLM'
    new_f = None
    if 'plusJES' in f:
        new_f = baseDir + '/' + sampleName.strip('_plusJES') + '/analysis_JES_up_job_*/*root'
    elif 'minusJES' in f:
        new_f = baseDir + '/' + sampleName.strip('_minusJES') + '/analysis_JES_down_job_*/*root'
    elif 'plusJER' in f:
        new_f = baseDir + '/' + sampleName.strip('_plusJER') + '/analysis_JetSmearing_up_job_*/*root'
    elif 'minusJER' in f:
        new_f = baseDir + '/' + sampleName.strip('_minusJER') + '/analysis_JetSmearing_down_job_*/*root'
    else:
        new_f = baseDir + '/' + sampleName + '/analysis_central_job_*/*root'
    return new_f
def getFileName( com, sample, measurementConfig ) :

    fileNames = {
        '13TeV' : {
            'central'           : measurementConfig.ttbar_trees,
            'central_70pc'           : measurementConfig.ttbar_trees,
            'central_30pc'           : measurementConfig.ttbar_trees,

            'central_firstHalf'           : measurementConfig.ttbar_trees,
            'central_secondHalf'           : measurementConfig.ttbar_trees,

            'amcatnlo'          : measurementConfig.ttbar_amc_trees,
            'madgraph'          : measurementConfig.ttbar_madgraph_trees,
            'powhegherwigpp'    : measurementConfig.ttbar_powhegherwigpp_trees,


            'ueup'              : measurementConfig.ttbar_ueup_trees,
            'uedown'            : measurementConfig.ttbar_uedown_trees,
            'isrup'             : measurementConfig.ttbar_isrup_trees,
            'isrdown'           : measurementConfig.ttbar_isrdown_trees,
            'fsrup'             : measurementConfig.ttbar_fsrup_trees,
            'fsrdown'           : measurementConfig.ttbar_fsrdown_trees,

            'hdampup'             : measurementConfig.ttbar_hdampup_trees,
            'hdampdown'           : measurementConfig.ttbar_hdampdown_trees,

            'erdOn'           : measurementConfig.ttbar_erdOn_trees,
            'QCDbased_erdOn'           : measurementConfig.ttbar_QCDbased_erdOn_trees,
            'GluonMove'           : measurementConfig.ttbar_GluonMove_trees,

            'massdown'          : measurementConfig.ttbar_mtop1695_trees,
            'massup'            : measurementConfig.ttbar_mtop1755_trees,

            'jesdown'           : measurementConfig.ttbar_jesdown_trees,
            'jesup'             : measurementConfig.ttbar_jesup_trees,
            'jerdown'           : measurementConfig.ttbar_jerdown_trees,
            'jerup'             : measurementConfig.ttbar_jerup_trees,

            'bjetdown'          : measurementConfig.ttbar_trees,
            'bjetup'            : measurementConfig.ttbar_trees,
            'lightjetdown'      : measurementConfig.ttbar_trees,
            'lightjetup'        : measurementConfig.ttbar_trees,

            'electrondown'        : measurementConfig.ttbar_trees,
            'electronup'          : measurementConfig.ttbar_trees,
            'muondown'        : measurementConfig.ttbar_trees,
            'muonup'          : measurementConfig.ttbar_trees,
            'pileupUp'          : measurementConfig.ttbar_trees,
            'pileupDown'        : measurementConfig.ttbar_trees,

            'ElectronEnUp'      : measurementConfig.ttbar_trees,
            'ElectronEnDown'    : measurementConfig.ttbar_trees,
            'MuonEnUp'          : measurementConfig.ttbar_trees,
            'MuonEnDown'        : measurementConfig.ttbar_trees,
            'TauEnUp'           : measurementConfig.ttbar_trees,
            'TauEnDown'         : measurementConfig.ttbar_trees,
            'UnclusteredEnUp'   : measurementConfig.ttbar_trees,
            'UnclusteredEnDown' : measurementConfig.ttbar_trees,

            'topPtSystematic'   : measurementConfig.ttbar_trees,

        },
    }

    return fileNames[com][sample]

channels = [
    channel( 'ePlusJets', 'rootTupleTreeEPlusJets', 'electron'),
    channel( 'muPlusJets', 'rootTupleTreeMuPlusJets', 'muon'),
]



def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument('--topPtReweighting', 
        dest='applyTopPtReweighting', 
        type=int, 
        default=0 
    )
    parser.add_argument('--topEtaReweighting', 
        dest='applyTopEtaReweighting', 
        type=int, 
        default=0 
    )
    parser.add_argument('-c', '--centreOfMassEnergy', 
        dest='centreOfMassEnergy', 
        type=int, 
        default=13 
    )
    parser.add_argument('--pdfWeight', 
        type=int, 
        dest='pdfWeight', 
        default=-1 
    )
    parser.add_argument('--CT14Weight', 
        type=int, 
        dest='CT14Weight', 
        default=-1 
    )
    parser.add_argument('--MMHT14Weight', 
        type=int, 
        dest='MMHT14Weight', 
        default=-1 
    )
    parser.add_argument('--muFmuRWeight', 
        type=int, 
        dest='muFmuRWeight', 
        default=-1 
    )
    parser.add_argument('--alphaSWeight', 
        type=int, 
        dest='alphaSWeight', 
        default=-1 
    )
    parser.add_argument('--semiLepBrWeight', 
        type=int, 
        dest='semiLepBrWeight', 
        default=0
    )
    parser.add_argument('--fragWeight', 
        type=int, 
        dest='fragWeight', 
        default=0
    )
    parser.add_argument('-s', '--sample', 
        dest='sample', 
        default='central'
    )
    parser.add_argument('-d', '--debug', 
        action='store_true', 
        dest='debug', 
        default=False
    )
    parser.add_argument('-n', 
        action='store_true', 
        dest='donothing', 
        default=False
    )
    parser.add_argument('-e', 
        action='store_true', 
        dest='extraHists', 
        default=False
    )
    parser.add_argument('-f',
        action='store_true', 
        dest='fineBinned', 
        default=False
    )
    parser.add_argument('--newPS',
        action='store_true', 
        dest='newPS', 
        default=False
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    measurement_config = XSectionConfig( args.centreOfMassEnergy )

    # Input file name
    file_name = 'crap.root'
    if int(args.centreOfMassEnergy) == 13:
        file_name = getFileName('13TeV', args.sample, measurement_config)
    else:
        print "Error: Unrecognised centre of mass energy."

    pdfWeight       = args.pdfWeight
    CT14Weight      = args.CT14Weight
    MMHT14Weight    = args.MMHT14Weight
    muFmuRWeight    = args.muFmuRWeight
    alphaSWeight    = args.alphaSWeight
    semiLepBrWeight = args.semiLepBrWeight
    fragWeight      = args.fragWeight

    # Output file name
    outputFileName = 'crap.root'
    outputFileDir = 'unfolding/%sTeV/' % args.centreOfMassEnergy
    make_folder_if_not_exists(outputFileDir)
   
    energySuffix = '%sTeV' % ( args.centreOfMassEnergy )

    if args.applyTopEtaReweighting != 0:
        if args.applyTopEtaReweighting == 1:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopEtaReweighting_up.root' % energySuffix
        elif args.applyTopEtaReweighting == -1:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopEtaReweighting_down.root' % energySuffix
    elif args.applyTopPtReweighting:
        if args.applyTopPtReweighting == 1:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopPtReweighting_up.root' % energySuffix
        elif args.applyTopPtReweighting == -1:
            outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_withTopPtReweighting_down.root' % energySuffix
    elif muFmuRWeight == 1:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_1muR2muF.root' % ( energySuffix )
    elif muFmuRWeight == 2:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_1muR05muF.root' % ( energySuffix )
    elif muFmuRWeight == 3:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_2muR1muF.root' % ( energySuffix )
    elif muFmuRWeight == 4:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_2muR2muF.root' % ( energySuffix )
    elif muFmuRWeight == 6:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_05muR1muF.root' % ( energySuffix )
    elif muFmuRWeight == 8:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_05muR05muF.root' % ( energySuffix )
    elif alphaSWeight == 0:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_alphaS_down.root' % ( energySuffix )
    elif alphaSWeight == 1:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_alphaS_up.root' % ( energySuffix )
    elif semiLepBrWeight == -1:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_semiLepBr_down.root' % ( energySuffix )
    elif semiLepBrWeight == 1:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_semiLepBr_up.root' % ( energySuffix )
    elif fragWeight == 1:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_frag_down.root' % ( energySuffix )
    elif fragWeight == 2:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_frag_central.root' % ( energySuffix )
    elif fragWeight == 3:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_frag_up.root' % ( energySuffix )
    elif fragWeight == 4:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_frag_peterson.root' % ( energySuffix )
    elif pdfWeight >= 0 and pdfWeight <= 99:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_pdfWeight_%i.root' % ( energySuffix, pdfWeight )
    elif CT14Weight >= 0 and CT14Weight <= 54:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_CT14Weight_%i.root' % ( energySuffix, CT14Weight )
    elif MMHT14Weight >= 0 and MMHT14Weight <= 55:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric_MMHT14Weight_%i.root' % ( energySuffix, MMHT14Weight )
    elif 'central' not in args.sample:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_%s_asymmetric.root' % ( energySuffix, args.sample  )
    elif args.fineBinned :
        outputFileName = outputFileDir+'/unfolding_TTJets_%s.root' % ( energySuffix  )
    else:
        outputFileName = outputFileDir+'/unfolding_TTJets_%s_asymmetric.root' % energySuffix

    if '70pc' in args.sample or '30pc' in args.sample:
        outputFileName.replace('asymmetric','asymmetric_'+args.sample.split('_')[1])

    if 'firstHalf' in args.sample:
        outputFileName = outputFileName.replace('asymmetric','asymmetric_firstHalf')
    elif 'secondHalf' in args.sample:
        outputFileName = outputFileName.replace('asymmetric','asymmetric_secondHalf')

    if args.newPS :
        outputFileName = outputFileName.replace('asymmetric','asymmetric_newPS')

    # outputFileName = outputFileName.replace('asymmetric','asymmetric_AlternativeWeightAndCorrection')

    # Get the tree/chain
    treeName = "TTbar_plus_X_analysis/Unfolding/Unfolding"
    print file_name
    file_name = getUnmergedDirectory(file_name)
    print file_name
    tree = ROOT.TChain(treeName);
    filenames = glob.glob( file_name )
    for f in filenames:
        tree.Add(f)

    with root_open( outputFileName, 'recreate') as out:
            nEntries = tree.GetEntries()
            print 'Number of entries:',nEntries

            # For variables where you want bins to be symmetric about 0, use abs(variable) (but also make plots for signed variable)
            allVariablesBins = bin_edges_vis.copy()
            for variable in bin_edges_vis:
                if 'Rap' in variable:
                    allVariablesBins['abs_%s' % variable] = [0,bin_edges_vis[variable][-1]]

            recoVariableNames = {}
            genVariable_particle_names = {}
            genVariable_parton_names = {}
            histograms      = {}
            residuals       = {}
            residual_options= {}
            outputDirs      = {}
            outputDirsRes   = {}

            for variable in allVariablesBins:
                if args.debug and variable != 'HT' : continue
                if args.sample in measurement_config.met_specific_systematics \
                and variable in measurement_config.variables_no_met:
                    continue

                outputDirs[variable]        = {}
                outputDirsRes[variable]     = {}
                histograms[variable]        = {}
                residuals[variable]         = {}
                residual_options[variable]  = {}

                #
                # Variable names
                #
                recoVariableName = branchNames[variable]
                sysIndex = None
                if variable in ['MET', 'ST', 'WPT']:
                    if args.sample == "jerup":
                        recoVariableName += '_METUncertainties'
                        sysIndex = 0
                    elif args.sample == "jerdown":
                        recoVariableName+= '_METUncertainties'
                        sysIndex = 1
                    elif args.sample == "jesup":
                        recoVariableName += '_METUncertainties'
                        sysIndex = 2
                    elif args.sample == "jesdown":
                        recoVariableName += '_METUncertainties'
                        sysIndex = 3
                    # Dont need this?
                    elif args.sample in measurement_config.met_systematics:
                        recoVariableName += '_METUncertainties'
                        sysIndex = measurement_config.met_systematics[args.sample]

                genVariable_particle_name = None
                genVariable_parton_name = None
                if variable in genBranchNames_particle:
                    genVariable_particle_name = genBranchNames_particle[variable]
                    if args.newPS and variable in ['HT', 'ST', 'NJets']:
                        genVariable_particle_name += '_20GeVLastJet'
                if variable in genBranchNames_parton:
                    genVariable_parton_name = genBranchNames_parton[variable]

                recoVariableNames[variable] = recoVariableName
                genVariable_particle_names[variable] = genVariable_particle_name
                genVariable_parton_names[variable] = genVariable_parton_name 

                reco_bin_edges_vis_to_use = reco_bin_edges_vis[variable]

                for channel in channels:
                    # Make dir in output file
                    outputDirName = variable+'_'+channel.outputDirName
                    outputDir = out.mkdir(outputDirName)
                    outputDirs[variable][channel.channelName] = outputDir

                    if args.fineBinned:
                        outputDirResName = outputDirName + '/residuals/'
                        outputDirRes = out.mkdir(outputDirResName)
                        outputDirsRes[variable][channel.channelName] = outputDirRes

                    #
                    # Book histograms
                    #
                    # 1D histograms
                    histograms[variable][channel.channelName] = {}
                    h = histograms[variable][channel.channelName]
                    h['truth']                          = Hist( allVariablesBins[variable], name='truth')
                    h['truthVis']                       = Hist( allVariablesBins[variable], name='truthVis')
                    h['truth_parton']                   = Hist( allVariablesBins[variable], name='truth_parton')                
                    h['measured']                       = Hist( reco_bin_edges_vis_to_use, name='measured')
                    h['measuredVis']                    = Hist( reco_bin_edges_vis_to_use, name='measuredVis')
                    h['measured_without_fakes']         = Hist( reco_bin_edges_vis_to_use, name='measured_without_fakes')
                    h['measuredVis_without_fakes']      = Hist( reco_bin_edges_vis_to_use, name='measuredVis_without_fakes')
                    h['fake']                           = Hist( reco_bin_edges_vis_to_use, name='fake')
                    h['fakeVis']                        = Hist( reco_bin_edges_vis_to_use, name='fakeVis')
                    # 2D histograms
                    h['response']                       = Hist2D( reco_bin_edges_vis_to_use, allVariablesBins[variable], name='response')
                    h['response_without_fakes']         = Hist2D( reco_bin_edges_vis_to_use, allVariablesBins[variable], name='response_without_fakes')
                    h['responseVis_without_fakes']      = Hist2D( reco_bin_edges_vis_to_use, allVariablesBins[variable], name='responseVis_without_fakes')
                    h['response_parton']                = Hist2D( reco_bin_edges_vis_to_use, allVariablesBins[variable], name='response_parton')
                    h['response_without_fakes_parton']  = Hist2D( reco_bin_edges_vis_to_use, allVariablesBins[variable], name='response_without_fakes_parton')

                    if args.fineBinned:
                        minVar = trunc( allVariablesBins[variable][0] )
                        maxVar = trunc( max( tree.GetMaximum(genVariable_particle_names[variable]), tree.GetMaximum( reco_bin_edges_vis_to_use ) ) * 1.2 )
                        nBins = int(maxVar - minVar)
                        if variable is 'lepton_eta' or variable is 'bjets_eta':
                            maxVar = 2.4
                            minVar = -2.4
                            nBins = 1000
                        # nBins = 960 so that small bin width is usable in 00. [0.0025]
                        elif 'abs' in variable and 'eta' in variable:
                            maxVar = 2.4
                            minVar = 0.
                            nBins = 960
                        elif 'Rap' in variable:
                            maxVar = 2.4
                            minVar = -2.4
                            nBins = 1000
                        elif 'NJets' in variable:
                            maxVar = 20.5
                            minVar = 3.5
                            nBins = 17

                        h['truth']                          = Hist( nBins, minVar, maxVar, name='truth')
                        h['truthVis']                       = Hist( nBins, minVar, maxVar, name='truthVis')
                        h['truth_parton']                   = Hist( nBins, minVar, maxVar, name='truth_parton')
                        h['measured']                       = Hist( nBins, minVar, maxVar, name='measured')
                        h['measuredVis']                    = Hist( nBins, minVar, maxVar, name='measuredVis')
                        h['measured_without_fakes']         = Hist( nBins, minVar, maxVar, name='measured_without_fakes')
                        h['measuredVis_without_fakes']      = Hist( nBins, minVar, maxVar, name='measuredVis_without_fakes')
                        h['fake']                           = Hist( nBins, minVar, maxVar, name='fake')
                        h['fakeVis']                        = Hist( nBins, minVar, maxVar, name='fakeVis')
                        h['response']                       = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response')
                        h['response_without_fakes']         = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes')
                        h['responseVis_without_fakes']      = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='responseVis_without_fakes')

                        h['response_parton']                = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_parton')
                        h['response_without_fakes_parton']  = Hist2D( nBins, minVar, maxVar, nBins, minVar, maxVar, name='response_without_fakes_parton')

                        residuals[variable][channel.channelName] = {}
                        r = residuals[variable][channel.channelName]
                        for i in range (1, nBins+1):
                            r[i] = Hist(100, 0, maxVar*0.1, name='Residuals_Bin_'+str(i))

                        residual_options[variable][channel.channelName] = {}
                        o = residual_options[variable][channel.channelName]
                        o['min']        = minVar
                        o['max']        = maxVar
                        o['nbins']      = nBins
                        o['step']       = (maxVar-minVar)/nBins
                        o['bin_edges']  = np.arange(minVar, maxVar, (maxVar-minVar)/nBins)

                    # Some interesting histograms
                    h['puOffline']          = Hist( 20, 0, 2, name='puWeights_offline')
                    h['eventWeightHist']    = Hist( 100, -2, 2, name='eventWeightHist')                    
                    h['genWeightHist']      = Hist( 100, -2, 2, name='genWeightHist')
                    h['offlineWeightHist']  = Hist( 100, -2, 2, name='offlineWeightHist')
                    h['phaseSpaceInfoHist'] = Hist( 10, 0, 1, name='phaseSpaceInfoHist')

            print("Initialisation of Histograms Complete")

            # Counters for studying phase space
            nVis            = {c.channelName : 0 for c in channels}
            nVisNotOffline  = {c.channelName : 0 for c in channels}
            nOffline        = {c.channelName : 0 for c in channels}
            nOfflineNotVis  = {c.channelName : 0 for c in channels}
            nFull           = {c.channelName : 0 for c in channels}
            nOfflineSL      = {c.channelName : 0 for c in channels}

            n=0
            maxEvents = -1
            halfOfEvents = 0
            if '70pc' in args.sample or '30pc' in args.sample:
                print 'Only processing fraction of total events for sample :',args.sample
                totalEvents = tree.GetEntries()
                if '70pc' in args.sample:
                    maxEvents = int( totalEvents * 0.7 )
                elif '30pc' in args.sample:
                    maxEvents = int( totalEvents * 0.3 )
                print 'Will process ',maxEvents,'out of',totalEvents,'events'

            if 'firstHalf' in args.sample or 'secondHalf' in args.sample:
                totalEvents = tree.GetEntries()
                halfOfEvents = int( totalEvents / 2 )

            # Event Loop
            # for event, weight in zip(tree,weightTree):
            for event in tree:
                branch = event.__getattr__
                n+=1
                if not n%100000: print 'Processing event %.0f Progress : %.2g %%' % ( n, float(n)/nEntries*100 )
                # if n > 100000: break

                if maxEvents > 0 and n > maxEvents: break

                if 'firstHalf' in args.sample and n >= halfOfEvents: break
                elif 'secondHalf' in args.sample and n < halfOfEvents: continue

                # # #
                # # # Weights and selection
                # # #

                # Pileup weight
                # Don't apply if calculating systematic
                pileupWeight = event.PUWeight
                # print event.PUWeight,event.PUWeight_up,event.PUWeight_down
                if args.sample == "pileupUp":
                    pileupWeight = event.PUWeight_up
                elif args.sample == "pileupDown":
                    pileupWeight = event.PUWeight_down

                # Generator level weight
                genWeight = event.EventWeight * measurement_config.luminosity_scale

                # B Jet Weight
                # bjetWeight = event.BJetWeight
                bjetWeight = event.BJetAlternativeWeight
                if 'fsr' in args.sample:
                    # bjetWeight = event.BJetAlternativeWeight * event.BJetEfficiencyCorrectionWeight
                    bjetWeight = event.BJetWeight * event.BJetEfficiencyCorrectionWeight

                if args.sample == "bjetup":
                    bjetWeight = event.BJetUpWeight
                elif args.sample == "bjetdown":
                    bjetWeight = event.BJetDownWeight
                elif args.sample == "lightjetup":
                    bjetWeight = event.LightJetUpWeight
                elif args.sample == "lightjetdown":
                    bjetWeight = event.LightJetDownWeight

                # Top pt systematic weight
                topPtSystematicWeight = 1
                if args.sample == 'topPtSystematic':
                    topPtSystematicWeight = calculateTopPtSystematicWeight( branch('lepTopPt_parton'), branch('hadTopPt_parton'))

                # Offline level weights
                offlineWeight = 1
                offlineWeight *= pileupWeight
                offlineWeight *= bjetWeight

                offlineWeight_forLeptonEta = offlineWeight
                genWeight *= topPtSystematicWeight
                
                # Generator weight
                # Scale up/down, pdf
                if pdfWeight >= 0:
                    genWeight *= branch('pdfWeight_%i' % pdfWeight)
                    pass

                if MMHT14Weight >= 0:
                    genWeight *= branch('MMHT14Weight_%i' % MMHT14Weight)
                    pass


                if CT14Weight >= 0:
                    genWeight *= branch('CT14Weight_%i' % CT14Weight)
                    pass

                if muFmuRWeight >= 0:
                    genWeight *= branch('muFmuRWeight_%i' % muFmuRWeight)
                    pass

                if alphaSWeight == 0 or alphaSWeight == 1:
                    genWeight *= branch('alphaSWeight_%i' % alphaSWeight)
                    pass

                if semiLepBrWeight == -1:
                    genWeight *= branch('semilepbrDown')
                elif semiLepBrWeight == 1:
                    genWeight *= branch('semilepbrUp')
                    pass

                if fragWeight == 1:
                    genWeight *= branch('downFrag')
                elif fragWeight == 2:
                    genWeight *= branch('centralFrag')
                elif fragWeight == 3:
                    genWeight *= branch('upFrag')
                elif fragWeight == 4:
                    genWeight *= branch('petersonFrag')
                    pass

                if args.applyTopPtReweighting != 0:
                    ptWeight = calculateTopPtWeight( branch('lepTopPt_parton'), branch('hadTopPt_parton'), args.applyTopPtReweighting)
                    genWeight *= ptWeight
                
                if args.applyTopEtaReweighting != 0:
                    etaWeight = calculateTopEtaWeight( branch('lepTopRap_parton'), branch('hadTopRap_parton'), args.applyTopEtaReweighting)
                    genWeight *= etaWeight

                for channel in channels:
                    # Generator level selection
                    genSelection = ''
                    genSelectionVis = ''
                    if channel.channelName is 'muPlusJets' :
                        genSelection = event.isSemiLeptonicMuon == 1
                        genSelectionVis = event.passesGenEventSelection == 1 and event.pseudoLepton_pdgId == 13
                        if args.newPS:
                            genSelectionVis = event.passesGenEventSelection_20GeVLastJet == 1 and event.pseudoLepton_pdgId == 13
                    elif channel.channelName is 'ePlusJets' :
                        genSelection = event.isSemiLeptonicElectron == 1
                        genSelectionVis = event.passesGenEventSelection == 1 and event.pseudoLepton_pdgId == 11
                        if args.newPS:
                            genSelectionVis = event.passesGenEventSelection_20GeVLastJet == 1 and event.pseudoLepton_pdgId == 11

                    # Lepton weight
                    # Channel specific
                    leptonWeight = 1
                    leptonWeight_forLeptonEta = 1

                    if channel.channelName is 'muPlusJets' :
                        leptonWeight = event.MuonEfficiencyCorrection
                        leptonWeight_forLeptonEta = event.MuonEfficiencyCorrection_etaBins

                        if args.sample == 'muonup':
                            leptonWeight = event.MuonEfficiencyCorrectionUp
                            leptonWeight_forLeptonEta = event.MuonEfficiencyCorrectionUp_etaBins
                        elif args.sample == 'muondown':
                            leptonWeight = event.MuonEfficiencyCorrectionDown
                            leptonWeight_forLeptonEta = event.MuonEfficiencyCorrectionDown_etaBins
                    elif channel.channelName is 'ePlusJets' :
                        leptonWeight = event.ElectronEfficiencyCorrection
                        leptonWeight_forLeptonEta = event.ElectronEfficiencyCorrection_etaBins

                        if args.sample == 'electronup':
                            leptonWeight = event.ElectronEfficiencyCorrectionUp
                            leptonWeight_forLeptonEta = event.ElectronEfficiencyCorrectionUp_etaBins
                        elif args.sample == 'electrondown':
                            leptonWeight = event.ElectronEfficiencyCorrectionDown
                            leptonWeight_forLeptonEta = event.ElectronEfficiencyCorrectionDown_etaBins

                    offlineWeight_withLeptonWeight = offlineWeight * leptonWeight
                    offlineWeight_withLeptonWeight_forLeptonEta = offlineWeight_forLeptonEta * leptonWeight_forLeptonEta

                    # Offline level selection
                    offlineSelection = 0

                    if channel.channelName is 'muPlusJets' :
                        offlineSelection = int(event.passSelection) == 1
                    elif channel.channelName is 'ePlusJets' :               
                        offlineSelection = int(event.passSelection) == 2

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
                        nOffline[channel.channelName] += offlineWeight * genWeight
                        if not genSelectionVis:
                            nOfflineNotVis[channel.channelName] += offlineWeight * genWeight

                    for variable in allVariablesBins:
                        if args.debug and variable != 'HT' : continue
                        if args.sample in measurement_config.met_specific_systematics and \
                        variable in measurement_config.variables_no_met:
                            continue

                        offlineWeight_toUse = offlineWeight_withLeptonWeight
                        if 'abs_lepton_eta' in variable:
                            offlineWeight_toUse = offlineWeight_withLeptonWeight_forLeptonEta

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
                        if not args.fineBinned:
                            recoVariable = min( recoVariable, allVariablesBins[variable][-1] - 0.000001 )
                        genVariable_particle = branch(genVariable_particle_names[variable])
                        if 'abs' in variable:
                            genVariable_particle = abs(genVariable_particle)

                        # #
                        # # Fill histograms
                        # #
                        histogramsToFill = histograms[variable][channel.channelName]
                        if not args.donothing:

                            if genSelection:
                                histogramsToFill['truth'].Fill( genVariable_particle, genWeight)
                            if genSelectionVis:
                                filledTruth = True
                                histogramsToFill['truthVis'].Fill( genVariable_particle, genWeight)

                            if offlineSelection:
                                histogramsToFill['measured'].Fill( recoVariable, offlineWeight_toUse * genWeight )
                                histogramsToFill['measuredVis'].Fill( recoVariable, offlineWeight_toUse * genWeight )
                                if genSelectionVis :
                                    histogramsToFill['measuredVis_without_fakes'].Fill( recoVariable, offlineWeight_toUse * genWeight )
                                if genSelection:
                                    histogramsToFill['measured_without_fakes'].Fill( recoVariable, offlineWeight_toUse * genWeight )
                                histogramsToFill['response'].Fill( recoVariable, genVariable_particle, offlineWeight_toUse * genWeight )
                            
                            if offlineSelection and genSelection:
                                histogramsToFill['response_without_fakes'].Fill( recoVariable, genVariable_particle, offlineWeight_toUse * genWeight  ) 
                                histogramsToFill['response_without_fakes'].Fill( allVariablesBins[variable][0]-1, genVariable_particle, ( 1 - offlineWeight_toUse ) * genWeight  ) 
                            elif genSelection:
                                histogramsToFill['response_without_fakes'].Fill( allVariablesBins[variable][0]-1, genVariable_particle, genWeight )
                            
                            if offlineSelection and genSelectionVis:
                                histogramsToFill['responseVis_without_fakes'].Fill( recoVariable, genVariable_particle, offlineWeight_toUse * genWeight )
                                histogramsToFill['responseVis_without_fakes'].Fill( allVariablesBins[variable][0]-1, genVariable_particle, ( 1 - offlineWeight_toUse ) * genWeight )
                                filledResponse = True
                            elif genSelectionVis:
                                histogramsToFill['responseVis_without_fakes'].Fill( allVariablesBins[variable][0]-1, genVariable_particle, genWeight )
                                filledResponse = True
                            
                            if fakeSelection:
                                histogramsToFill['fake'].Fill( recoVariable, offlineWeight_toUse * genWeight )
                            if fakeSelectionVis:
                                histogramsToFill['fakeVis'].Fill( recoVariable, offlineWeight_toUse * genWeight )

                            if args.extraHists:
                                if genSelection:
                                    histogramsToFill['eventWeightHist'].Fill(event.EventWeight)
                                    histogramsToFill['genWeightHist'].Fill(genWeight)
                                    histogramsToFill['offlineWeightHist'].Fill(offlineWeight_toUse )

                            if args.fineBinned:
                                # Bin reco var is in
                                options = residual_options[variable][channel.channelName]
                                if offlineSelection and genSelection:
                                    # i will be fine bin number the reco var resides in
                                    for i, edge in enumerate(options['bin_edges']):
                                        if recoVariable > edge: continue
                                        else: break
                                    residual = abs(recoVariable - genVariable_particle)                                 
                                    if not residual > options['max']*0.1: 
                                        residuals[variable][channel.channelName][i].Fill(residual, offlineWeight_toUse*genWeight)

            #
            # Output histgorams to file
            #
            for variable in allVariablesBins:
                if args.debug and variable != 'HT' : continue
                if args.sample in measurement_config.met_systematics and variable not in ['MET', 'ST', 'WPT']:
                    continue
                for channel in channels:

                    if nOffline[channel.channelName] != 0 : 
                        # Fill phase space info
                        h = histograms[variable][channel.channelName]['phaseSpaceInfoHist']
                        h.SetBinContent(1, nVisNotOffline[channel.channelName] / nVis[channel.channelName])
                        # h.GetXaxis().SetBinLabel(1, "nVisNotOffline/nVis")

                        h.SetBinContent(2, nOfflineNotVis[channel.channelName] / nOffline[channel.channelName])
                        # h.GetXaxis().SetBinLabel(2, "nOfflineNotVis/nOffline")

                        h.SetBinContent(3, nVis[channel.channelName] / nFull[channel.channelName])
                        # h.GetXaxis().SetBinLabel(3, "nVis/nFull")

                        # Selection efficiency for SL ttbar
                        h.SetBinContent(4, nOfflineSL[channel.channelName] / nFull[channel.channelName])
                        # h.GetXaxis().SetBinLabel(4, "nOfflineSL/nFull")

                        # Fraction of offline that are SL
                        h.SetBinContent(5, nOfflineSL[channel.channelName] / nOffline[channel.channelName])
                        # h.GetXaxis().SetBinLabel(5, "nOfflineSL/nOffline")


                    outputDirs[variable][channel.channelName].cd()
                    for h in histograms[variable][channel.channelName]:
                        histograms[variable][channel.channelName][h].Write()
                    if args.fineBinned:
                        outputDirsRes[variable][channel.channelName].cd()
                        for r in residuals[variable][channel.channelName]:
                            residuals[variable][channel.channelName][r].Write()



    with root_open( outputFileName, 'update') as out:
        # Done all channels, now combine the two channels, and output to the same file
        for path, dirs, objects in out.walk():
            if 'electron' in path:
                if 'Bins' in path or 'coarse' in path: continue
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
