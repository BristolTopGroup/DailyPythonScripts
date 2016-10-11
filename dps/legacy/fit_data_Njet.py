
# How to scale MC
normMode = 1;

mcIntlumi = 36.145#pb-1
intlumi = 36.145  #pb-1

#-----------------------
# which jet bin to fit
#-----------------------
nj = "all";

YMAX_all = 4000;
YMAX_1mj = 2000;
YMAX_2mj = 400;
YMAX_3mj = -1;
YMAX_4orMoreJets = -1;

TheEstimates;

def fit_data_Njet(nj_user = "all", normMode_user = 1):
#    TheEstimates.open("MyEstimates.txt", ios.app);
    nj = nj_user;
    normMode = normMode_user;
    setStyle();
    getHisto();

    if (normMode < 3):
        #fit_linear(); #bad model
        #fit_expo();
        fit_gaus();
    if (normMode == 3):
        make_QCDnormToEstimate_plot();

    TheEstimates.close();

def fit_linear():
    fit_njet("pol1", 0.1);
    fit_njet("pol1", 0.2);
    fit_njet("pol1", 0.3);

def fit_expo():
    fit_njet("expo", 0.1);
    fit_njet("expo", 0.2);
    fit_njet("expo", 0.3);

def fit_gaus():
    fit_njet("gaus", 0.1);
    fit_njet("gaus", 0.2);
    fit_njet("gaus", 0.3);

def setStyle():
    # Apply TDR style
    tdrStyle = setTDRStyle();

    # slight adaptation
    tdrStyle.SetPadRightMargin(0.05); #originally was 0.02, too narrow!
    tdrStyle.SetStatH(0.2);
    #  tdrStyle.SetOptStat(1110);#off title
    tdrStyle.SetOptStat(0);#off title
    tdrStyle.SetOptFit(0);#off title
    tdrStyle.cd();
    #gStyle.SetHatchesSpacing(1);
    #gStyle.SetHatchesLineWidth(1);
    gROOT.ForceStyle();

def getHisto():

    fdata = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/data_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fttbar = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/ttjet_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fwjets = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/wj_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fzjets = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/zj_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fbce1 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/bce1_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fbce2 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/bce2_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fbce3 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/bce3_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fenri1 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/enri1_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fenri2 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/enri2_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fenri3 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/enri3_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fpj1 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/pj1_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fpj2 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/pj2_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fpj3 = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/pj3_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fsTopTW = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/tW_36.145pb_PFElectron_PF2PATJets_PFMET.root");
    fsToptC = TFile.Open(
            "/storage/workspace/BristolAnalysisTools/outputfiles/Fall10_NovRereco/tchan_36.145pb_PFElectron_PF2PATJets_PFMET.root");

    if (nj == "1mj" or nj == "2mj" or nj == "3mj"):
        get_histo_inclusive(nj);
    elif (nj == "all"):
        #--------------------------------------------------------------------------
        #                                DATA
        #--------------------------------------------------------------------------
        data =  fdata.Get("QCDest_CombRelIso_0jet");
        data.Add( fdata.Get("QCDest_CombRelIso_1jet"));
        data.Add( fdata.Get("QCDest_CombRelIso_2jets"));
        data.Add( fdata.Get("QCDest_CombRelIso_3jets"));
        data.Add( fdata.Get("QCDest_CombRelIso_4orMoreJets"));

        #--------------------------------------------------------------------------
        #                                 MC
        #--------------------------------------------------------------------------
        QCD =  fbce2.Get("QCDest_CombRelIso_0jet");
        QCD.Add( fbce2.Get("QCDest_CombRelIso_1jet"));
        QCD.Add( fbce2.Get("QCDest_CombRelIso_2jets"));
        QCD.Add( fbce2.Get("QCDest_CombRelIso_3jets"));
        QCD.Add( fbce2.Get("QCDest_CombRelIso_4orMoreJets"));

        QCD.Add( fbce3.Get("QCDest_CombRelIso_0jet"));
        QCD.Add( fbce3.Get("QCDest_CombRelIso_1jet"));
        QCD.Add( fbce3.Get("QCDest_CombRelIso_2jets"));
        QCD.Add( fbce3.Get("QCDest_CombRelIso_3jets"));
        QCD.Add( fbce3.Get("QCDest_CombRelIso_4orMoreJets"));

        QCD.Add( fenri1.Get("QCDest_CombRelIso_0jet"));
        QCD.Add( fenri1.Get("QCDest_CombRelIso_1jet"));
        QCD.Add( fenri1.Get("QCDest_CombRelIso_2jets"));
        QCD.Add( fenri1.Get("QCDest_CombRelIso_3jets"));
        QCD.Add( fenri1.Get("QCDest_CombRelIso_4orMoreJets"));

        QCD.Add( fenri2.Get("QCDest_CombRelIso_0jet"));
        QCD.Add( fenri2.Get("QCDest_CombRelIso_1jet"));
        QCD.Add( fenri2.Get("QCDest_CombRelIso_2jets"));
        QCD.Add( fenri2.Get("QCDest_CombRelIso_3jets"));
        QCD.Add( fenri2.Get("QCDest_CombRelIso_4orMoreJets"));

        QCD.Add( fenri3.Get("QCDest_CombRelIso_0jet"));
        QCD.Add( fenri3.Get("QCDest_CombRelIso_1jet"));
        QCD.Add( fenri3.Get("QCDest_CombRelIso_2jets"));
        QCD.Add( fenri3.Get("QCDest_CombRelIso_3jets"));
        QCD.Add( fenri3.Get("QCDest_CombRelIso_4orMoreJets"));

        pj =  fpj1.Get("QCDest_CombRelIso_0jet");
        pj.Add( fpj1.Get("QCDest_CombRelIso_1jet"));
        pj.Add( fpj1.Get("QCDest_CombRelIso_2jets"));
        pj.Add( fpj1.Get("QCDest_CombRelIso_3jets"));
        pj.Add( fpj1.Get("QCDest_CombRelIso_4orMoreJets"));

        pj.Add( fpj2.Get("QCDest_CombRelIso_0jet"));
        pj.Add( fpj2.Get("QCDest_CombRelIso_1jet"));
        pj.Add( fpj2.Get("QCDest_CombRelIso_2jets"));
        pj.Add( fpj2.Get("QCDest_CombRelIso_3jets"));
        pj.Add( fpj2.Get("QCDest_CombRelIso_4orMoreJets"));

        pj.Add( fpj3.Get("QCDest_CombRelIso_0jet"));
        pj.Add( fpj3.Get("QCDest_CombRelIso_1jet"));
        pj.Add( fpj3.Get("QCDest_CombRelIso_2jets"));
        pj.Add( fpj3.Get("QCDest_CombRelIso_3jets"));
        pj.Add( fpj3.Get("QCDest_CombRelIso_4orMoreJets"));

        wj =  fwjets.Get("QCDest_CombRelIso_0jet");
        wj.Add( fwjets.Get("QCDest_CombRelIso_1jet"));
        wj.Add( fwjets.Get("QCDest_CombRelIso_2jets"));
        wj.Add( fwjets.Get("QCDest_CombRelIso_3jets"));
        wj.Add( fwjets.Get("QCDest_CombRelIso_4orMoreJets"));

        zj =  fzjets.Get("QCDest_CombRelIso_0jet");
        zj.Add( fzjets.Get("QCDest_CombRelIso_1jet"));
        zj.Add( fzjets.Get("QCDest_CombRelIso_2jets"));
        zj.Add( fzjets.Get("QCDest_CombRelIso_3jets"));
        zj.Add( fzjets.Get("QCDest_CombRelIso_4orMoreJets"));

        tt =  fttbar.Get("QCDest_CombRelIso_0jet");
        tt.Add( fttbar.Get("QCDest_CombRelIso_1jet"));
        tt.Add( fttbar.Get("QCDest_CombRelIso_2jets"));
        tt.Add( fttbar.Get("QCDest_CombRelIso_3jets"));
        tt.Add( fttbar.Get("QCDest_CombRelIso_4orMoreJets"));

        stop =  fsTopTW.Get("QCDest_CombRelIso_0jet");
        stop.Add( fsTopTW.Get("QCDest_CombRelIso_1jet"));
        stop.Add( fsTopTW.Get("QCDest_CombRelIso_2jets"));
        stop.Add( fsTopTW.Get("QCDest_CombRelIso_3jets"));
        stop.Add( fsTopTW.Get("QCDest_CombRelIso_4orMoreJets"));

        stop.Add( fsToptC.Get("QCDest_CombRelIso_0jet"));
        stop.Add( fsToptC.Get("QCDest_CombRelIso_1jet"));
        stop.Add( fsToptC.Get("QCDest_CombRelIso_2jets"));
        stop.Add( fsToptC.Get("QCDest_CombRelIso_3jets"));
        stop.Add( fsToptC.Get("QCDest_CombRelIso_4orMoreJets"));

        mc =  QCD.Clone("sumMC");
        mc.Add(pj);
        mc.Add(wj);
        mc.Add(zj);
        mc.Add(tt);
        mc.Add(stop);
    else:

        #--------------------------------------------------------------------------
        #                                DATA
        #--------------------------------------------------------------------------
        data =  fdata.Get(Form("QCDest_CombRelIso_%s", nj));

        #--------------------------------------------------------------------------
        #                                 MC
        #--------------------------------------------------------------------------
        #    mc    = fmc.Get(Form("QCDest_CombRelIso_%s",nj));
        QCD =  fbce2.Get(Form("QCDest_CombRelIso_%s", nj));
        QCD.Add( fbce3.Get(Form("QCDest_CombRelIso_%s", nj)));
        QCD.Add( fenri1.Get(Form("QCDest_CombRelIso_%s", nj)));
        QCD.Add( fenri2.Get(Form("QCDest_CombRelIso_%s", nj)));
        QCD.Add( fenri3.Get(Form("QCDest_CombRelIso_%s", nj)));
        pj =  fpj1.Get(Form("QCDest_CombRelIso_%s", nj));
        pj.Add( fpj2.Get(Form("QCDest_CombRelIso_%s", nj)));
        pj.Add( fpj3.Get(Form("QCDest_CombRelIso_%s", nj)));
        wj =  fwjets.Get(Form("QCDest_CombRelIso_%s", nj));
        zj =  fzjets.Get(Form("QCDest_CombRelIso_%s", nj));
        tt =  fttbar.Get(Form("QCDest_CombRelIso_%s", nj));
        stop =  fsTopTW.Get(Form("QCDest_CombRelIso_%s", nj));
        stop.Add( fsToptC.Get(Form("QCDest_CombRelIso_%s", nj)));
        mc =  QCD.Clone("sumMC");
        mc.Add(pj);
        mc.Add(wj);
        mc.Add(zj);
        mc.Add(tt);
        mc.Add(stop);

    # add photon+jets to QCD
    #QCD.Add(pj);

    #scale QCD based on difference in estimate and simulation (before or after adding photon+jets?)
    #QCD.Scale(1.09);

    # Rebin
    this_rebin = 10;
#    /*
#     if(nj=="all") this_rebin = 2;
#     if(nj=="1mj") this_rebin = 2;
#     if(nj=="2mj") this_rebin = 5;
#     if(nj=="3mj") this_rebin = 5;
#     if(nj=="4orMoreJets") this_rebin = 5;
#     if(nj=="1jet") this_rebin = 2;
#     if(nj=="2jets") this_rebin = 5;
#     if(nj=="3jets") this_rebin = 5;
#     if(nj=="4j") this_rebin = 5;
#     */

    data.Rebin(this_rebin);
    mc.Rebin(this_rebin);
    QCD.Rebin(this_rebin);
    wj.Rebin(this_rebin);
    zj.Rebin(this_rebin);
    tt.Rebin(this_rebin);
    pj.Rebin(this_rebin);
    stop.Rebin(this_rebin);

    sf = intlumi / mcIntlumi;
    print "\n\n\n";
    print "-----------------------"
    print "data lumi: ",intlumi
    print "mc lumi: ",mcIntlumi
    print "scale factor: ",sf
    print "------------------------"

    # Scale MC to intlumi
    mc .Scale(sf);
    QCD .Scale(sf);
    wj .Scale(sf);
    zj .Scale(sf);
    pj .Scale(sf);
    tt .Scale(sf);
    stop.Scale(sf);

    if (normMode == 1):
        print "Scale MC to measured integrated luminosity"
    elif (normMode == 2):
        print "Scale MC so that n(MC) = n(Data) [same area]"
        #    nData = data.GetEntries();
        nData = data.Integral();
        nMC = mc.Integral();
        print "n(Data) = ",nData
        print "n(MC)   = ",nMC
        sf2 = nData / nMC;
        print "sf n(Data)/n(MC) = ",sf2
        # norm MC to Data
        mc .Scale(sf2);
        QCD .Scale(sf2);
        wj .Scale(sf2);
        zj .Scale(sf2);
        pj .Scale(sf2);
        tt .Scale(sf2);
        stop.Scale(sf2);
    print "------------------------"

    if (normMode == 3):
        print "Scale QCD MC to data-driven (average) estimate"
        if (nj == "all"):
            QCD.Scale(4944.44 / QCD.GetBinContent(1));
        if (nj == "0jet"):
            QCD.Scale(2131.79 / QCD.GetBinContent(1));
        if (nj == "1jet"):
            QCD.Scale(2432.21 / QCD.GetBinContent(1));
        if (nj == "2jets"):
            QCD.Scale(416.259 / QCD.GetBinContent(1));
        if (nj == "3jets"):
            QCD.Scale(56.0141 / QCD.GetBinContent(1));
        if (nj == "4orMoreJets"):
            QCD.Scale(24.1861 / QCD.GetBinContent(1));


    # stack up mc
    mcStack = THStack("mcStack", "MC stack");
    mcStack.Add(QCD); #bottom to top
    mcStack.Add(pj);
    mcStack.Add(zj);
    mcStack.Add(wj);
    #  mcStack.Add(stop);
    mcStack.Add(tt);

    # set style
    QCD.SetFillColor(Col_qcd);
    wj.SetFillColor(Col_wj);
    zj.SetFillColor(Col_zj);
    pj.SetFillColor(Col_pj);
    tt.SetFillColor(Col_sig);
    stop.SetFillColor(Col_stop);

    QCD.SetFillStyle(Sty_qcd);
    wj.SetFillStyle(Sty_wj);
    zj.SetFillStyle(Sty_zj);
    pj.SetFillStyle(Sty_pj);
    tt.SetFillStyle(Sty_sig);
    stop.SetFillStyle(Sty_stop);

    data.SetXTitle("Relative Isolation");
    data.SetYTitle("Events / 0.1");
    data.SetMarkerStyle(20);
#------------------------------------------------------------------------------------


# nj must take one of these values: "1mj", "2mj","3mj"
def get_histo_inclusive(nj):

    ijet;
    if (nj == "1mj"):
        ijet = 1;
    elif (nj == "2mj"):
        ijet = 2;
    elif (nj == "3mj"):
        ijet = 3;
    else:
        return -1;

    ijlabel = [ ">=0jet", ">=1jet", ">=2jets", ">=3jets" ]

    # 0-jet
    data_0jet =  fdata.Get("QCDest_CombRelIso_0jet");
    QCD_0jet =  fbce2.Get("QCDest_CombRelIso_0jet");
    QCD_0jet.Add( fbce3.Get("QCDest_CombRelIso_0jet"));
    QCD_0jet.Add( fenri1.Get("QCDest_CombRelIso_0jet"));
    QCD_0jet.Add( fenri2.Get("QCDest_CombRelIso_0jet"));
    QCD_0jet.Add( fenri3.Get("QCDest_CombRelIso_0jet"));
    pj_0jet =  fpj1.Get("QCDest_CombRelIso_0jet");
    pj_0jet.Add( fpj2.Get(Form("QCDest_CombRelIso_0jet", nj)));
    pj_0jet.Add( fpj3.Get(Form("QCDest_CombRelIso_0jet", nj)));
    wj_0jet =  fwjets.Get("QCDest_CombRelIso_0jet");
    zj_0jet =  fzjets.Get("QCDest_CombRelIso_0jet");
    tt_0jet =  fttbar.Get("QCDest_CombRelIso_0jet");
    stop_0jet =  fsTopTW.Get("QCDest_CombRelIso_0jet");
    stop_0jet.Add( fsToptC.Get("QCDest_CombRelIso_0jet"));
    mc_0jet =  QCD_0jet.Clone("sumMC_0jet");
    mc_0jet.Add(pj_0jet);
    mc_0jet.Add(wj_0jet);
    mc_0jet.Add(zj_0jet);
    mc_0jet.Add(tt_0jet);
    mc_0jet.Add(stop_0jet);

    # 1-jet
    data_1jet =  fdata.Get("QCDest_CombRelIso_1jet");
    QCD_1jet =  fbce2.Get("QCDest_CombRelIso_1jet");
    QCD_1jet.Add( fbce3.Get("QCDest_CombRelIso_1jet"));
    QCD_1jet.Add( fenri1.Get("QCDest_CombRelIso_1jet"));
    QCD_1jet.Add( fenri2.Get("QCDest_CombRelIso_1jet"));
    QCD_1jet.Add( fenri3.Get("QCDest_CombRelIso_1jet"));
    pj_1jet =  fpj1.Get("QCDest_CombRelIso_1jet");
    pj_1jet.Add( fpj2.Get(Form("QCDest_CombRelIso_1jet", nj)));
    pj_1jet.Add( fpj3.Get(Form("QCDest_CombRelIso_1jet", nj)));
    wj_1jet =  fwjets.Get("QCDest_CombRelIso_1jet");
    zj_1jet =  fzjets.Get("QCDest_CombRelIso_1jet");
    tt_1jet =  fttbar.Get("QCDest_CombRelIso_1jet");
    stop_1jet =  fsTopTW.Get("QCDest_CombRelIso_1jet");
    stop_1jet.Add( fsToptC.Get("QCDest_CombRelIso_1jet"));
    mc_1jet = QCD_1jet.Clone("sumMC_1jet");
    mc_1jet.Add(pj_1jet);
    mc_1jet.Add(wj_1jet);
    mc_1jet.Add(zj_1jet);
    mc_1jet.Add(tt_1jet);
    mc_1jet.Add(stop_1jet);

    # 2-jet
    data_2jets =  fdata.Get("QCDest_CombRelIso_2jets");
    QCD_2jets =  fbce2.Get("QCDest_CombRelIso_2jets");
    QCD_2jets.Add( fbce3.Get("QCDest_CombRelIso_2jets"));
    QCD_2jets.Add( fenri1.Get("QCDest_CombRelIso_2jets"));
    QCD_2jets.Add( fenri2.Get("QCDest_CombRelIso_2jets"));
    QCD_2jets.Add( fenri3.Get("QCDest_CombRelIso_2jets"));
    pj_2jets =  fpj1.Get("QCDest_CombRelIso_2jets");
    pj_2jets.Add( fpj2.Get(Form("QCDest_CombRelIso_2jets", nj)));
    pj_2jets.Add( fpj3.Get(Form("QCDest_CombRelIso_2jets", nj)));
    wj_2jets =  fwjets.Get("QCDest_CombRelIso_2jets");
    zj_2jets =  fzjets.Get("QCDest_CombRelIso_2jets");
    tt_2jets =  fttbar.Get("QCDest_CombRelIso_2jets");
    stop_2jets =  fsTopTW.Get("QCDest_CombRelIso_2jets");
    stop_2jets.Add( fsToptC.Get("QCDest_CombRelIso_2jets"));
    mc_2jets = QCD_2jets.Clone("sumMC_2jets");
    mc_2jets.Add(pj_2jets);
    mc_2jets.Add(wj_2jets);
    mc_2jets.Add(zj_2jets);
    mc_2jets.Add(tt_2jets);
    mc_2jets.Add(stop_2jets);

    # 3-jet
    data_3jets =  fdata.Get("QCDest_CombRelIso_3jets");
    QCD_3jets =  fbce2.Get("QCDest_CombRelIso_3jets");
    QCD_3jets.Add( fbce3.Get("QCDest_CombRelIso_3jets"));
    QCD_3jets.Add( fenri1.Get("QCDest_CombRelIso_3jets"));
    QCD_3jets.Add( fenri2.Get("QCDest_CombRelIso_3jets"));
    QCD_3jets.Add( fenri3.Get("QCDest_CombRelIso_3jets"));
    pj_3jets =  fpj1.Get("QCDest_CombRelIso_3jets");
    pj_3jets.Add( fpj2.Get(Form("QCDest_CombRelIso_3jets", nj)));
    pj_3jets.Add( fpj3.Get(Form("QCDest_CombRelIso_3jets", nj)));
    wj_3jets =  fwjets.Get("QCDest_CombRelIso_3jets");
    zj_3jets =  fzjets.Get("QCDest_CombRelIso_3jets");
    tt_3jets =  fttbar.Get("QCDest_CombRelIso_3jets");
    stop_3jets =  fsTopTW.Get("QCDest_CombRelIso_3jets");
    stop_3jets.Add( fsToptC.Get("QCDest_CombRelIso_3jets"));
    mc_3jets = QCD_3jets.Clone("sumMC_3jets");
    mc_3jets.Add(pj_3jets);
    mc_3jets.Add(wj_3jets);
    mc_3jets.Add(zj_3jets);
    mc_3jets.Add(tt_3jets);
    mc_3jets.Add(stop_3jets);

    # >=4-jet
    data_4orMoreJets =  fdata.Get("QCDest_CombRelIso_4orMoreJets");
    QCD_4orMoreJets =  fbce2.Get("QCDest_CombRelIso_4orMoreJets");
    QCD_4orMoreJets.Add( fbce3.Get("QCDest_CombRelIso_4orMoreJets"));
    QCD_4orMoreJets.Add( fenri1.Get("QCDest_CombRelIso_4orMoreJets"));
    QCD_4orMoreJets.Add( fenri2.Get("QCDest_CombRelIso_4orMoreJets"));
    QCD_4orMoreJets.Add( fenri3.Get("QCDest_CombRelIso_4orMoreJets"));
    pj_4orMoreJets =  fpj1.Get("QCDest_CombRelIso_4orMoreJets");
    pj_4orMoreJets.Add( fpj2.Get(Form("QCDest_CombRelIso_4orMoreJets", nj)));
    pj_4orMoreJets.Add( fpj3.Get(Form("QCDest_CombRelIso_4orMoreJets", nj)));
    wj_4orMoreJets =  fwjets.Get("QCDest_CombRelIso_4orMoreJets");
    zj_4orMoreJets =  fzjets.Get("QCDest_CombRelIso_4orMoreJets");
    tt_4orMoreJets =  fttbar.Get("QCDest_CombRelIso_4orMoreJets");
    stop_4orMoreJets =  fsTopTW.Get("QCDest_CombRelIso_4orMoreJets");
    stop_4orMoreJets.Add( fsToptC.Get("QCDest_CombRelIso_4orMoreJets"));
    mc_4orMoreJets = QCD_4orMoreJets.Clone("sumMC_4orMoreJets");
    mc_4orMoreJets.Add(pj_4orMoreJets);
    mc_4orMoreJets.Add(wj_4orMoreJets);
    mc_4orMoreJets.Add(zj_4orMoreJets);
    mc_4orMoreJets.Add(tt_4orMoreJets);
    mc_4orMoreJets.Add(stop_4orMoreJets);

    # First make clone of 4orMoreJets since this will be added for all cases
    data =  data_4orMoreJets.Clone("data");
    mc =  mc_4orMoreJets.Clone("mc");
    QCD =  QCD_4orMoreJets.Clone("QCD");
    pj =  pj_4orMoreJets.Clone("pj");
    wj =  wj_4orMoreJets.Clone("wj");
    zj =  zj_4orMoreJets.Clone("zj");
    tt =  tt_4orMoreJets.Clone("tt");
    stop =  stop_4orMoreJets.Clone("stop");

    #----------------------------------
    # >=0jet: 0jet+1jet+2jets+3jets+4orMoreJets = all
    # >=1jet:    1jet+2jets+3jets+4orMoreJets
    # >=2jets:       2jets+3jets+4orMoreJets
    # >=3jets:          3jets+4orMoreJets
    # >=4j:             4orMoreJets = 4orMoreJets
    #----------------------------------

    # Add 1jet
    if (nj == "1mj"):
        data.Add(data_1jet);
        mc.Add(mc_1jet);
        QCD.Add(QCD_1jet);
        pj.Add(pj_1jet);
        wj.Add(wj_1jet);
        zj.Add(zj_1jet);
        tt.Add(tt_1jet);
        stop.Add(stop_1jet);

    # Add 2jets
    if (nj == "1mj" or nj == "2mj"):
        data.Add(data_2jets);
        mc.Add(mc_2jets);
        QCD.Add(QCD_2jets);
        pj.Add(pj_2jets);
        wj.Add(wj_2jets);
        zj.Add(zj_2jets);
        tt.Add(tt_2jets);
        stop.Add(stop_2jets);

    # Add 3jets
    data.Add(data_3jets);
    mc.Add(mc_3jets);
    QCD.Add(QCD_3jets);
    pj.Add(pj_3jets);
    wj.Add(wj_3jets);
    zj.Add(zj_3jets);
    tt.Add(tt_3jets);
    stop.Add(stop_3jets);

    print "-----------------------------------"
    print "     DATA      nEntries    Integral"
    print "-----------------------------------"
    print ' '*10,"0jet",' '*10,data_0jet.GetEntries(),' '*10,data_0jet.Integral()
    print ' '*10,"1jet",' '*10,data_1jet.GetEntries(),' '*10,data_1jet.Integral()
    print ' '*10,"2jets",' '*10,data_2jets.GetEntries(),' '*10,data_2jets.Integral()
    print ' '*10,"3jets",' '*10,data_3jets.GetEntries(),' '*10,data_3jets.Integral()
    print ' '*10,">=4j",' '*10,data_4orMoreJets.GetEntries(),' '*10 ,data_4orMoreJets.Integral()
    print "-----------------------------------"
    print ' '*10,ijlabel[ijet],' '*10,data.GetEntries(),' '*10,data.Integral()
    print "-----------------------------------"

    return 0;


def make_QCDnormToEstimate_plot():

    c1 = TCanvas("c1", "RelIso fit", 600, 400);#,"",500,500);

    data.GetXaxis().SetRangeUser(0, 1.6 - 0.01);
    if (nj == "2jets"):
        data.GetYaxis().SetRangeUser(0, 16.);

    # draw data
    data.Draw();
    if (nj == "all" and YMAX_all > 0):
        data.GetYaxis().SetRangeUser(0, YMAX_all);
    if (nj == "1mj" and YMAX_1mj > 0):
        data.GetYaxis().SetRangeUser(0, YMAX_1mj);
    if (nj == "2mj" and YMAX_2mj > 0):
        data.GetYaxis().SetRangeUser(0, YMAX_2mj);
    if (nj == "3mj" and YMAX_3mj > 0):
        data.GetYaxis().SetRangeUser(0, YMAX_3mj);
    if (nj == "4orMoreJets" and YMAX_4orMoreJets > 0):
        data.GetYaxis().SetRangeUser(0, YMAX_4orMoreJets);

    # draw mc
    mcStack.Draw("ahist same");
    data.Draw("ae same");
    data.Draw("axis same");

    # Add "CMS Preliminary", integrated luminosity and sqrt(s), and legend
    add_cms_label(intlumi, nj);
    add_legend_nofit();

    out = Form("ele_reliso_normToLumi_QCDnormToEst_%s", nj);

    print "out: ",out
    c1.SaveAs(Form("%s.C", out));
    c1.SaveAs(Form("%s.eps", out));
    gROOT.ProcessLine(Form(".!ps2pdf -dEPSCrop %s.eps", out));
    gROOT.ProcessLine(Form(".!rm -f %s.eps", out));

    c1.Close(); #crucial!


#------------------------------------------------------------------------------
#
#                                  main fit code
#
#------------------------------------------------------------------------------

def fit_njet(function = "pol1", Fit_From_user = 0.1):

    firstTime = True;
    print "\nSwitched from chi2 fit to likelihood fit (better with low stats)\n"

    # Try: 0.1, 0.2
    Fit_From = Fit_From_user;
    print "-----------------------"
    print " FIT:  ",function,"   range ",Fit_From,"--1.6"
    print "-----------------------"

    lw = 2; #line width (function)


    c1 = TCanvas("c1", "RelIso fit", 600, 400);#,"",500,500);


    #  gStyle.SetOptStat(1110);#off title


    data.GetXaxis().SetRangeUser(0, 1.6 - 0.01);
    if (nj == "2jets"):
        #    data_max = data.GetMaximum();
        data.GetYaxis().SetRangeUser(0, 18.);
    # MET>25
    #  data.GetYaxis().SetRangeUser(0,50.);


    #data.SetTitleFont(42,"XY");
    #  data.GetYaxis().SetTitleOffset(1.5);

    data.Draw();
    if (firstTime):
        YMAX_all = 2 * data.GetMaximum();
        firstTime = False;

    #if(nj=="all" and YMAX_all>0) data.GetYaxis().SetRangeUser( 0,YMAX_all );
    data.GetYaxis().SetRangeUser(0, YMAX_all);

#    /*
#     if(nj=="all" and YMAX_all>0) data.GetYaxis().SetRangeUser(0,YMAX_all);
#     if(nj=="1mj"  and YMAX_1mj >0) data.GetYaxis().SetRangeUser(0,YMAX_1mj);
#     if(nj=="2mj"  and YMAX_2mj >0) data.GetYaxis().SetRangeUser(0,YMAX_2mj);
#     if(nj=="3mj"  and YMAX_3mj >0) data.GetYaxis().SetRangeUser(0,YMAX_3mj);
#     if(nj=="4orMoreJets"  and YMAX_4orMoreJets >0) data.GetYaxis().SetRangeUser(0,YMAX_4orMoreJets);
#     */

    # draw mc
    #  mc.Draw("ahist same");
    mcStack.Draw("ahist same");
    data.Draw("ae same");
    data.Draw("axis same");

    print "Fit Range: ",Fit_From,"-1.6"

    #  TFitResultPtr myFitResult = data.Fit("pol1","0S","ah",Fit_From,1.6); # <----Fit Range
    #    const char *func = Form("%s", function);

    # Fit options used:
    #  L : likelihood method
    #  S : store fit results
    #  0 : do not draw
    myFitResult = data.Fit(function, "0SL", "ah", Fit_From, 1.6); # <----Fit Range
    print "func ",function
    # Fit line in red
    #  myf = data.GetFunction("pol1");
    myf = data.GetFunction(function);
    myf.SetLineColor(kRed);
    myf.SetLineWidth(lw);

    # Extrapolation in dashed blue
    myf2 =  myf.Clone(); #range 0-0.1
    myf2.SetLineColor(kBlue);
    myf2.SetLineStyle(kDashed);
    myf2.SetLineWidth(lw);
    myf2.SetRange(0, Fit_From);

    myf.Draw("same");
    myf2.Draw("same");

    # Get estimate from extrapolation
    n_extrap = myf2.Integral(0, 0.1) / 0.1; #note divided by bin width=0.1

    p0 = myf.GetParameter(0);
    p1 = myf.GetParameter(1);
    e0 = myf.GetParError(0);
    e1 = myf.GetParError(1);

    chi2 = myFitResult.Chi2();
    ndf = myFitResult.Ndf();

    print "------------"
    print "Fit results"
    print "------------"
    print "n extrap = ",n_extrap
    print "p0 = ",p0," +/- ",e0
    print "p1 = ",p1," +/- ",e1
    print "chi2/ndf =  ",chi2," / ",ndf

    # Constructfunctions to see how estimate varies within fit parameter
    # uncertainties, ie error of p0 and p1

    # vary p0 (normalization)
    #  newF1_up =TF1("pol1","pol1",0,1.6);
    newF1_up =TF1(function, function, 0, 1.6);
    newF1_up.SetParameters(p0 + e0, p1);
    newF1_up.SetLineColor(kGreen);
    newF1_up.SetLineWidth(lw);
    #newF1_up.SetLineStyle(kDashed);
    #newF1_up.Draw("same");

    #  newF1_down =TF1("pol1","pol1",0,1.6);
    newF1_down =TF1(function, function, 0, 1.6);
    newF1_down.SetParameters(p0 - e0, p1);
    newF1_down.SetLineColor(kGreen);
    newF1_down.SetLineWidth(lw);
    #newF1_down.SetLineStyle(kDashed);
    #newF1_down.Draw("same");

#    /*
#     # vary p1 (gradient)
#     newF2_up =TF1("pol1","pol1",0,1.6);
#     newF2_up.SetParameters(p0, p1+e1);
#     newF2_up.SetLineColor(kViolet);
#     newF2_up.SetLineWidth(lw);
#     #newF2_up.SetLineStyle(kDashed);
#     #newF2_up.Draw("same");
#
#     newF2_down =TF1("pol1","pol1",0,1.6);
#     newF2_down.SetParameters(p0, p1-e1);
#     newF2_down.SetLineColor(kViolet);
#     newF2_down.SetLineWidth(lw);
#     #newF2_down.SetLineStyle(kDashed);
#     #newF2_down.Draw("same");
#     */

    # Get theestimates
    est_1 = newF1_up.Integral(0, 0.1) / 0.1;
    est_2 = newF1_down.Integral(0, 0.1) / 0.1;
    #est_3 = newF2_up.Integral(0,0.1)/0.1;
    #est_4 = newF2_down.Integral(0,0.1)/0.1;
    print "n extrap (p0 + e0,   p1     ) = ",est_1
    print "n extrap (p0 - e0,   p1     ) = ",est_2
    #print "n extrap (p0     ,   p1 + e1) = ",est_3
    #print "n extrap (p0     ,   p1 - e1) = ",est_4

    # take the maximum deviation as the uncertainty
    est_unc = 0;
    if (fabs(est_1 - n_extrap) > est_unc):
        est_unc = fabs(est_1 - n_extrap);
    if (fabs(est_2 - n_extrap) > est_unc):
        est_unc = fabs(est_2 - n_extrap);
    #if( fabs(est_3 - n_extrap) > est_unc ) est_unc = fabs(est_3 - n_extrap);
    #if( fabs(est_4 - n_extrap) > est_unc ) est_unc = fabs(est_4 - n_extrap);

    print "Take the maximum deviation as the uncertainty of the QCD estimate."
    print "--------------------------------------------"
    print "  RESULT: ",function," ",Fit_From,"-1.6"
    print "--------------------------------------------"
    # prout MC prediction for QCD + photon+jets
    if (normMode == 1):
        print "\n  QCD predicted =  ",QCD.Integral(0, 1)," (Lumi)"
        TheEstimates,"\n  QCD predicted =  ",QCD.Integral(0, 1)," (Lumi)"
    print "\n  QCD estimate  =  ",n_extrap,"  +/-  ",est_unc," (vary p0)"
    TheEstimates,"  QCD estimate  =  ",n_extrap,"  +/-  ",est_unc," (vary p0)"

    #----------------------
    # error propagation
    #----------------------
    N = 0;
    sigmaN = 0;

    if (function == "pol1"):
        c = p0;
        m = p1;

        eC = e0;
        eM = e1;

        N = 0.05 * m + c;
        sigmaN = TMath.Hypot(0.05 * eM, eC);

    elif (function == "expo"):
        a = p0;
        b = p1;
        eA = e0;
        eB = e1;

        x2 = 0.1;

        exp_ab = exp(a + 0.1 * b);
        exp_a = exp(a);

        N = 10 / b * (exp_ab - exp_a);

        # del(N)/del(a/b)
        dNda = 1 / (b * x2) * (exp_ab - exp_a);
        dNdb = -1 / (b * b * x2) * (exp_ab - exp_a) + 1 / b * exp_ab;

        # Note: sigma(N) = sqrt( dNda^2*eA^2 + dBdb^2*eB^2  )
        sigmaN = TMath.Hypot(dNda * eA, dNdb * eB);
    elif (function == "gaus"):
        p2 = myf.GetParameter(2);
        e2 = myf.GetParError(2);
        # Not finished. Calculated estimate is wrong.
        print "\n-. Error propagation for Gaussian not yet implemented!"
        #calculate_gaus_unc(p0,p1,p2);

    print "\n  QCD estimate  =  ",N;
    print "  +/-  ",sigmaN," (error propagation)\n\n";
    print "--------------------------------------------"

    # Add "CMS Preliminary", integrated luminosity and sqrt(s), and legend
    add_cms_label(intlumi, nj);
    #  add_fit_res( Fit_From, chi2, ndf );
    add_legend(function);

    # save as eps, then convert to pdf
    print "Fit_From=",Fit_From
    out;
    if (function == "pol1"):
        out = Form("ele_reliso_fit_%s_linear_from_0%.0f", nj, Fit_From * 10.0);
    else:
        out = Form("ele_reliso_fit_%s_%s_from_0%.0f", function, nj, Fit_From * 10.0);

    if (normMode == 1):
        out += "_normToLumi";
    else:
        out += "_normToData";

    print "out: ",out
    c1.SaveAs(Form("%s.C", out)); #save as C++ root macro
    c1.SaveAs(Form("%s.eps", out));
    gROOT.ProcessLine(Form(".!ps2pdf -dEPSCrop %s.eps", out));
    gROOT.ProcessLine(Form(".!rm -f %s.eps", out));

    c1.Close(); #crucial!

def calculate_gaus_unc(a, b, c):

    # This formula gives wrong results. ??
    print "a: ",a
    print "b: ",b
    print "c: ",c
    x1 = 0.1;
    exp1 = exp(-0.5 * pow((x1 - b) / c, 2));
    exp2 = exp(-0.5 * pow(b / c, 2));
    est = -a * c * c / x1 * (exp1 / (x1 - b) + exp2 / b);
    #print "est: "<< est

#------------------------------------------------------------------------------------

def ScaleMCtoEstimate(nj_user = "all", estimate):
    #aim: scale QCD in signal region to data estimate and compare MC to data
    nj = nj_user;
    setStyle();
    getHisto();

    data.GetXaxis().SetRangeUser(0, 1.6);

    tempCan =TCanvas("tempCan", "tempCan", 600, 400);
    data.Draw("");
    data.SetMaximum(2 * data.GetMaximum());

    myStack =THStack("myStack", "myMC stack");
    mcQCD = QCD.Integral(0, 1);
    print mcQCD
    QCD.Scale(estimate / mcQCD);#setes QCD to estimate
    #QCD.Add(pj);

    myStack.Add(QCD);
    myStack.Add(pj);
    myStack.Add(stop);
    myStack.Add(zj);
    myStack.Add(wj);
    myStack.Add(tt);
    myStack.Draw("ahist same");
#    /*
#     QCD.Draw("hist same");
#     pj.Draw("hist same");
#     wj.Draw("hist same");
#     zj.Draw("hist same");
#     tt.Draw("hist same");
#     stop.Draw("hist same");
#     */

    data.Draw("ae same");
    data.Draw("axis same");

    #mcStack.Draw("ahist same");
    #data.Draw("ae same");
    tempCan.SaveAs(Form("MCQCDscaledtoData_%s.pdf", nj_user));
    tempCan.Close();

    #  cout<<mcStack.GetBinContent(1)<<endl;
