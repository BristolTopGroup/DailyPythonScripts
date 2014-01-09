from ROOT import *
#from math import fsum
btag_bins_inclusive = ['0orMoreBtag', '1orMoreBtag', '2orMoreBtags', '3orMoreBtags']
btag_sums = {
             '0orMoreBtag':['0btag', '1btag', '2btags', '3btags', '4orMoreBtags'],
             '1orMoreBtag':['1btag', '2btags', '3btags', '4orMoreBtags'],
             '2orMoreBtags':['2btags', '3btags', '4orMoreBtags'],
             '3orMoreBtags':['3btags', '4orMoreBtags']
             }

def getHistsFromFiles( histnames = [], files = {}, bJetBins = [], jetBins = [] ):
        TFileOpen = TFile.Open
        allHists = {}
        gcd = gROOT.cd
        
        if bJetBins and jetBins:
            print 'enabling both binnings at the same time is not supported!'
            return []
        
        if bJetBins:
            histnames = [name + '_' + bjetBin for name in histnames for bjetBin in bJetBins]
            
        if jetBins:
            histnames = [name + '_' + jetBin for name in histnames for jetBin in jetBins]
            
        for sample, filename in files.iteritems():
            file = TFileOpen( filename )
            if not file:
                print "Could not find file:", filename
                return
            allHists[sample] = {}
            fg = file.Get
            gcd()
            rootHist = None
            for hist in histnames:
                btag_found = ''
                for btag in btag_bins_inclusive:
                    if btag in hist:
                        btag_found = btag
                        break
                if btag_found == '':
                    rootHist = fg(hist)
                    if not rootHist:
                        print filename
                        print 'sample:', sample, ',hist:', hist, "could not be found."
                        continue
                else:
                    listOfExclusiveBins = btag_sums[btag_found]
                    exclhists = []
                    for excbin in listOfExclusiveBins:
                        fhist = fg(hist.replace(btag_found, excbin))
                        if not fhist:
                            print filename
                            print 'sample:', sample, ',hist:', hist, "could not be found."
                            continue
                        exclhists.append(fhist)
                    rootHist = exclhists[0].Clone()
                    for fhist in exclhists[1:]:
                        rootHist.Add(fhist)
#                fhist = fg( hist )
#                if not fhist:
#                    print filename
#                    print 'sample:', sample, ',hist:', hist, "could not be found."
#                    continue
                allHists[sample][hist] = rootHist.Clone()
        return allHists
    
def sumHistograms(listOfHistograms):
    if not listOfHistograms:
        return None
    newHistogram = listOfHistograms[0].Clone()
    for histogram in listOfHistograms[1:]:
        newHistogram.Add(histogram)
    return newHistogram
        
    
def addSampleSum( hists = {} ):
        qcdList = {}
        mc_all_list = {}
        singleTopList = {}
        wjets = {}

        qcdSamples = ['bce1', 'bce2', 'bce3', 'enri1', 'enri2', 'enri3', 'pj1', 'pj2', 'pj3']
        allMCSamples = ['ttbar', 'wjets', 'zjets', 'bce1', 'bce2', 'bce3', 'enri1',
                        'enri2', 'enri3', 'pj1', 'pj2', 'pj3', 'T_TuneZ2_tW-channel', 'T_TuneZ2_t-channel', 'T_TuneZ2_s-channel', 
                            'Tbar_TuneZ2_tW-channel', 'Tbar_TuneZ2_t-channel', 'Tbar_TuneZ2_s-channel']
        singleTopSamples = ['T_TuneZ2_tW-channel', 'T_TuneZ2_t-channel', 'T_TuneZ2_s-channel', 
                            'Tbar_TuneZ2_tW-channel', 'Tbar_TuneZ2_t-channel', 'Tbar_TuneZ2_s-channel']
        wjetsSamples = ['W1Jet', 'W2Jets', 'W3Jets', 'W4Jets']


        for sample, histlist in hists.iteritems():
            for histname, hist in histlist.iteritems():
                if sample in qcdSamples:
                    if not qcdList.has_key( histname ):
                        qcdList[histname] = hist.Clone( 'qcd' )
                    else:
                        qcdList[histname].Add( hist )

                if sample in allMCSamples:
                    if not mc_all_list.has_key( histname ):
                        mc_all_list[histname] = hist.Clone( 'all_mc' )
                    else:
                        mc_all_list[histname].Add( hist )

                if sample in singleTopSamples:
                    if not singleTopList.has_key( histname ):
                        singleTopList[histname] = hist.Clone( 'singleTop' )
                    else:
                        singleTopList[histname].Add( hist )
                if sample in wjetsSamples:
                    if not wjets.has_key( histname ):
                        wjets[histname] = hist.Clone( 'wjets' )
                    else:
                        wjets[histname].Add( hist )

        hists['qcd'] = qcdList
        hists['allMC'] = mc_all_list
        hists['singleTop'] = singleTopList
        hists['wjets'] = wjets
        return hists

def makeDetailedMCStack( hists ):

    allMCSamples = ['bce1', 'bce2', 'bce3', 'enri1',
                        'enri2', 'enri3', 'pj1', 'pj2', 'pj3', 'zjets', 'wjets','T_TuneZ2_tW-channel', 'T_TuneZ2_t-channel', 'T_TuneZ2_s-channel', 
                            'Tbar_TuneZ2_tW-channel', 'Tbar_TuneZ2_t-channel', 'Tbar_TuneZ2_s-channel', 'ttbar' ]

    hists['allMCDetailed'] = makeStack( hists, allMCSamples )
    return hists
#    mcStack = {}
#    
#    for sample in allMCSamples:
#        if hists.has_key(sample):
#            histlist = hists[sample]
#            for histname, hist in histlist.iteritems():
#                if sample in allMCSamples:
#                    if not mcStack.has_key( histname ):
#                        mcStack[histname] = THStack("MC", "MC")
#                    mcStack[histname].Add( hist )
#    hists['allMCDetailed'] = mcStack
#    return hists

def makeMCStack( hists ):

    allMCSamples = ['qcd', 'zjets', 'wjets', 'singleTop', 'ttbar']
    hists['allMCStack'] = makeStack( hists, allMCSamples )
    return hists

def makeStack( hists, samples ):
    mcStack = {}

    for sample in samples:
        if hists.has_key( sample ):
            histlist = hists[sample]
            for histname, hist in histlist.iteritems():
                if not mcStack.has_key( histname ):
                    mcStack[histname] = THStack( "MC", "MC" )
                mcStack[histname].Add( hist )

    return mcStack

def addJetSum( hists ):
        allhists = ['QCDest_CombRelIso_0jet', 'QCDest_CombRelIso_1jet', 'QCDest_CombRelIso_2jets',
                        'QCDest_CombRelIso_3jets', 'QCDest_CombRelIso_4orMoreJets']
        oneOrMore = ['QCDest_CombRelIso_1jet', 'QCDest_CombRelIso_2jets',
                        'QCDest_CombRelIso_3jets', 'QCDest_CombRelIso_4orMoreJets']
        twoOrMore = ['QCDest_CombRelIso_2jets',
                        'QCDest_CombRelIso_3jets', 'QCDest_CombRelIso_4orMoreJets']
        threeOrMore = ['QCDest_CombRelIso_3jets', 'QCDest_CombRelIso_4orMoreJets']

        addUp = addUpHistograms
        for sample, histlist in hists.iteritems():
            if( len( hists[sample].keys() ) == 0 ):
                continue
            hists[sample]['QCDest_CombRelIso_0orMoreJets'] = addUp( hists[sample], allhists )
            hists[sample]['QCDest_CombRelIso_1orMoreJets'] = addUp( hists[sample], oneOrMore )
            hists[sample]['QCDest_CombRelIso_2orMoreJets'] = addUp( hists[sample], twoOrMore )
            hists[sample]['QCDest_CombRelIso_3orMoreJets'] = addUp( hists[sample], threeOrMore )
        return hists

def addUpHistograms( dictOfHists, histsToAdd ):
        hist = dictOfHists[histsToAdd[0]].Clone()
        hadd = hist.Add
        [hadd( h ) for name, h in dictOfHists.iteritems() if name in histsToAdd[1:]]
        return hist


def joinHistogramDictionaries(listOfDicts):
    joinedDicts = {}
    for histDict in listOfDicts:
        for sample, hists in histDict.iteritems():
            if not joinedDicts.has_key(sample):
                joinedDicts[sample] = {}
            
            for histname, hist in hists.iteritems():
                joinedDicts[sample][histname] = hist
    return joinedDicts

if __name__ == "__main__":
    histnames = ['QCDest_CombRelIso_0jet', 'QCDest_CombRelIso_1jet', 'QCDest_CombRelIso_2jets',
                        'QCDest_CombRelIso_3jets', 'QCDest_CombRelIso_4orMoreJets']
    files = {'data':"/storage/workspace/BristolAnalysisTools/outputfiles/new/data_35pb_PFElectron_PF2PATJets_PFMET.root",
    'ttbar' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/ttjet_35pb_PFElectron_PF2PATJets_PFMET.root",
    'wjets' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/wj_35pb_PFElectron_PF2PATJets_PFMET.root",
    'zjets' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/zj_35pb_PFElectron_PF2PATJets_PFMET.root",
#    'bce1' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/bce1_35pb.root",
    'bce2' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/bce2_35pb_PFElectron_PF2PATJets_PFMET.root",
    'bce3' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/bce3_35pb_PFElectron_PF2PATJets_PFMET.root",
    'enri1' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/enri1_35pb_PFElectron_PF2PATJets_PFMET.root",
    'enri2' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/enri2_35pb_PFElectron_PF2PATJets_PFMET.root",
    'enri3' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/enri3_35pb_PFElectron_PF2PATJets_PFMET.root",
    'pj1' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/pj1_35pb_PFElectron_PF2PATJets_PFMET.root",
    'pj2' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/pj2_35pb_PFElectron_PF2PATJets_PFMET.root",
    'pj3' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/pj3_35pb_PFElectron_PF2PATJets_PFMET.root"}
#    'tW' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/tW_35pb_PFElectron_PF2PATJets_PFMET.root",
#    'tchan' : "/storage/workspace/BristolAnalysisTools/outputfiles/new/tchan_35pb_PFElectron_PF2PATJets_PFMET.root"}
#    HistGetter.samplefiles = files
#    HG = HistGetter()
#    HG.setStyle()
    hists = getHistsFromFiles( histnames, files )
    hists = addSampleSum( hists )
    hists = addJetSum( hists )
    qcdSamples = ['bce1', 'bce2', 'bce3', 'enri1', 'enri2', 'enri3', 'pj1', 'pj2', 'pj3']
    allMCSamples = ['ttbar', 'wjets', 'zjets', 'tW', 'tchan', 'bce1', 'bce2', 'bce3', 'enri1',
                        'enri2', 'enri3', 'pj1', 'pj2', 'pj3']
    singleTopSamples = ['tW', 'tchan']

    nqcd = 0
    nstop = 0
    nmc = 0
    nqcd = sum( [hists[sample]['QCDest_CombRelIso_0jet'].Integral() for sample in qcdSamples if hists.has_key( sample )] )
#    nstop = sum([hists[sample][0].Integral() for sample in singleTopSamples if hists.has_key(sample)])
    nmc = sum( [hists[sample]['QCDest_CombRelIso_0jet'].Integral() for sample in allMCSamples if hists.has_key( sample )] )
    print hists['qcd']['QCDest_CombRelIso_0jet'].Integral(), nqcd
#    print hists['singleTop'][0].Integral(), nstop
    print hists['allMC']['QCDest_CombRelIso_0jet'].Integral(), nmc
    print
    print hists['allMC']['QCDest_CombRelIso_0orMoreJets'].Integral(), hists['allMC']['QCDest_CombRelIso_0jet'].Integral()
    print hists['allMC']['QCDest_CombRelIso_1orMoreJets'].Integral(), hists['allMC']['QCDest_CombRelIso_1jet'].Integral()
    print hists['allMC']['QCDest_CombRelIso_2orMoreJets'].Integral(), hists['allMC']['QCDest_CombRelIso_2jets'].Integral()
    print hists['allMC']['QCDest_CombRelIso_3orMoreJets'].Integral(), hists['allMC']['QCDest_CombRelIso_3jets'].Integral()
    print hists['allMC']['QCDest_CombRelIso_4orMoreJets'].Integral()
    print hists['allMC'].keys()
    c = []
    for histname, hist in hists['allMC'].iteritems():
        c.append( TCanvas( "cname" + histname, histname, 800, 600 ) )
        c[-1].cd()
        hist.Draw()

    a = raw_input()
