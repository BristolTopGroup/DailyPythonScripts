from tdrStyle import *

inclusiveJetBins = [
        "0orMoreJets",
        "1orMoreJets",
        "2orMoreJets",
        "3orMoreJets" , 
        "4orMoreJets"]

exclusiveJetBins = [
        "0jet",
        "1jet",
        "2jets",
        "3jets"]

inclusiveBjetBins = [
        "0orMoreBtag",
        "1orMoreBtag",
        "2orMoreBtags",
        "3orMoreBtags",
        '4orMoreBtags' ]

exclusiveBjetBins = [
        '0btag',
        "1btag",
        "2btags",
        "3btags"]

allJetBins = []
allJetBins.extend(inclusiveJetBins)
allJetBins.extend(exclusiveJetBins)

allBjetBins = []
allBjetBins.extend(inclusiveBjetBins)
allBjetBins.extend(exclusiveBjetBins)

jetBinsLatex = {'0jet':'0 jet', '0orMoreJets':'#geq 0 jets', '1jet':'1 jet', '1orMoreJets':'#geq 1 jet',
                    '2jets':'2 jets', '2orMoreJets':'#geq 2 jets', '3jets':'3 jets', '3orMoreJets':'#geq 3 jets',
                    '4orMoreJets':'#geq 4 jets'}

BjetBinsLatex = {'0btag':'0 b-tags', '0orMoreBtag':'#geq 0 b-tags', '1btag':'1 b-tags', 
                    '1orMoreBtag':'#geq 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'#geq 2 b-tags', 
                    '3btags':'3 b-tags', '3orMoreBtags':'#geq 3 b-tags',
                    '4orMoreBtags':'#geq 4 b-tags'}

def setStyle():
    tdrStyle = setTDRStyle();

    #slight adaptation
    tdrStyle.SetPadRightMargin( 0.05 ); #originally was 0.02, too narrow!
    tdrStyle.SetStatH( 0.2 );
    #tdrStyle.SetOptStat(1110);//off title
    tdrStyle.SetOptStat( 0 );#off title
    tdrStyle.SetOptFit( 0 );#off title
    tdrStyle.cd();
    gROOT.ForceStyle();
    
