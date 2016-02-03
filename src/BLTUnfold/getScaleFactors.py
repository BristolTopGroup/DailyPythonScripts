import pickle

def get7TeVMuonScaleFactors():
    f = open('MuonEfficiencies2011_44X.pkl', 'r')
    data = pickle.load(f)
    
    ptBins = data['combRelPFISO12_2011A']['pt_abseta>1.2'].keys()
    etaBins = ['pt_abseta>1.2','pt_abseta<1.2']
    
    lumi_2011A = 2.311
    lumi_2011B = 2.739
    lumi_2011 = 5.050
    
    for etaBin in etaBins:
        for ptBin in ptBins:
            a = data['combRelPFISO12_2011A'][etaBin][ptBin]['data/mc']['efficiency_ratio']
            b = data['combRelPFISO12_2011B'][etaBin][ptBin]['data/mc']['efficiency_ratio']
            correction = ((lumi_2011A/lumi_2011) * a) + ((lumi_2011B/lumi_2011)* b)
            
            # Eta bins
            lowEta = -1
            highEta = -2
            if etaBin.find('<')>=0:
                lowEta = 0
                highEta = 1.2
            elif etaBin.find('>')>=0:
                lowEta = 1.2
                highEta = 10
                pass
            
            # Pt bin
            lowPt = ptBin.split('_')[0]
            highPt = ptBin.split('_')[-1]
            
            print 'scaleFactor( %s, %s, %s, %s, %s ),' % ( lowEta, highEta, lowPt, highPt, correction )
            pass
        pass
    pass

def get8TeVMuonScaleFactors():
    fID = open('MuonEfficiencies_Run2012ReReco_53X.pkl', 'r')
    fISO = open('MuonEfficiencies_ISO_Run_2012ReReco_53X.pkl', 'r')
    fTRIG = open('SingleMuonTriggerEfficiencies_eta2p1_Run2012ABCD_v5trees.pkl', 'r')
    
    dataID = pickle.load(fID)['Tight']
    dataISO = pickle.load(fISO)['combRelIsoPF04dBeta<012_Tight']
    dataTRIG = pickle.load(fTRIG)['IsoMu24']['TightID_IsodB']
    
    ptBins = dataID['ptabseta<0.9'].keys()
    etaBins = ['ptabseta<0.9','ptabseta0.9-1.2','ptabseta1.2-2.1','ptabseta2.1-2.4']
    # Different just to be annoying
    trigEtaBins = {
                   'ptabseta2.1-2.4':'PT_ABSETA_Endcaps_1p2to2p1',
                   'ptabseta1.2-2.1':'PT_ABSETA_Endcaps_1p2to2p1',
                   'ptabseta0.9-1.2':'PT_ABSETA_Transition_0p9to1p2',
                   'ptabseta<0.9':'PT_ABSETA_Barrel_0to0p9'}


    for etaBin in etaBins:
        for ptBin in ptBins:
            idCorrection = dataID[etaBin][ptBin]['data/mc']['efficiency_ratio']
            isoCorrection = dataISO[etaBin][ptBin]['data/mc']['efficiency_ratio']

            trigCorrection = 1.
            if not( ptBin == '10_20' or ptBin == '20_25' ):
                if ( ptBin == '140_300'):
                    trigCorrection = dataTRIG[ trigEtaBins[etaBin] ]['140_500']['data/mc']['efficiency_ratio']
                else:
                    trigCorrection = dataTRIG[ trigEtaBins[etaBin] ][ptBin]['data/mc']['efficiency_ratio']
            
            correction = idCorrection*isoCorrection*trigCorrection
             
            # Eta bins
            lowEta = -1
            highEta = -2
            if etaBin.find('<0.9')>=0:
                lowEta = 0
                highEta = 0.9
            elif etaBin.find('0.9-1.2')>=0:
                lowEta = 0.9
                highEta = 1.2
            elif etaBin.find('1.2-2.1')>=0:
                lowEta = 1.2
                highEta = 2.1
            elif etaBin.find('2.1-2.4')>=0:
                lowEta = 2.1
                highEta = 2.4
                pass
             
            # Pt bin
            lowPt = ptBin.split('_')[0]
            highPt = ptBin.split('_')[-1]
             
            print 'scaleFactor( %s, %s, %s, %s, %s ),' % ( lowEta, highEta, lowPt, highPt, correction )
            pass
        pass
    pass

print 'MUON 7TEV\n'
get7TeVMuonScaleFactors()
print '\nMUON 8TEV\n'
get8TeVMuonScaleFactors()