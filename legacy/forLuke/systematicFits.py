from tdrStyle import setTDRStyle
from ROOT import *
# Declare pointer to data as global (not elegant but TMinuit needs this).
data_Vec = []; #input data

ttbar_Vec = []; #ttbar+single top template from mc
wjets_Vec = []; #wjest template from data driven method
zjets_Vec = []; #zjets template from data driven method
qcd_Vec = [];   #qcd template from data drive method

ttbar_err_Vec = [];
wjets_err_Vec = []; #wjest template from data driven method
zjets_err_Vec = []; #zjets template from data driven method
qcd_err_Vec = [];   #qcd template from data drive method


Ntotal = 0 #define as global, got in getDataFromHis function
nbins=0 #define as global, also got in getDataFromHis function, and it is been used in getTemFromHis function

#double xbins[13] = {0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4};


xmin = 0;
xmax = 0; #calculate in getDataFromHis function


lumi = 4973.4;

Nsignal = 0;
Nwjets = 0
Nzjets = 0
NQCD = 0
NSinglT = 0
Nttbar = 0
NtotPass = 0
NttbarUp = 0
NtotPassUp = 0 
NttbarDown = 0
NtotPassDown = 0
  
NttbarUpMat = 0
NtotPassUpMat = 0 
NttbarDownMat = 0
NtotPassDownMat = 0
  
NttbarNLO = 0
NtotPassNLO = 0
NttbarPOW = 0
NtotPassPOW = 0
  
#-------------------------------------------------------------------------

def systematicFits():
    setTDRStyle();



  # Choose the jet multiplicity
    jet_num = "2b_";
    jet_num_temp = "ge2j";
  
    metBin = ["1","2","3","4","5"]

    templ = "_central";


    #differential histo
    xbins = [1,25,45,70,100,150] 
    #histograms for comaprison
    #diff generators	
    theor  = TH1D("theor", "", 5, xbins);  
    nlo =  TH1D("nlo", "", 5, xbins);
    powheg =  TH1D("powheg", "", 5, xbins);
    #syst samples
    sysup = TH1D("sysup", "", 5, xbins); 
    sysdown = TH1D("sysdown", "", 5, xbins); 
    mup = TH1D("mup", "", 5, xbins); 
    mdown = TH1D("mdown", "", 5, xbins); 
    #measured
    measured  = TH1D("meas", "", 5, xbins);  #muon
    ele  = TH1D("ele", "", 5, xbins);     
    comb  = TH1D("comb", "", 5, xbins); 
   #compare histo
    nominal  = TH1D("nominal", "", 5, xbins);
  
    #theroy onn ttbar only due to stats (need to also change the string for w/z)
    syst = ["_qup","_qdown","_mup","_mdown"]
   
    #syst[8] = {"_jup","_jdown","_METup","_METdown","_pup","_pdown","_bup","_bdown"};

        
    for sysErr in range(0,4):
        print syst[sysErr]

   #asymerrors
        n = 5;
        x = [0]*n;   
        y = [0]*n;
        exl = [0]*n;
        exh = [0]*n;

        theorNum = 0;	
        nloNum = 0;
        powhegNum = 0;
	
        #syst
        upNum = 0;  
        downNum = 0; 
        mupNum = 0;  
        mdownNum = 0; 

        theorXsect = 157.5;
        totXsect = 0;
        for met in range(0,5):
  #for systematics
            f_central = TFile.Open("PFhistosForFitting_met"+metBin[met]+templ+".root");  
            f_all = TFile.Open("PFhistosForFitting_metall"+templ+".root");
            f_templates  = TFile.Open("QCDetaData.root");

            signal = f_central.Get("metEta_h_"+jet_num+"signal");
            wjets = f_central.Get("metEta_h_"+jet_num+"wjets");
            zjets = f_central.Get("metEta_h_"+jet_num+"zjets");
            SinglT = f_central.Get("metEta_h_"+jet_num+"SinglT");
            ttbar = f_central.Get("metEta_h_"+jet_num+"ttbar");
  
            QCD = f_central.Get("metEta_h_"+jet_num+"QCD");
            tt_Z = f_central.Get("metEta_h_"+jet_num+"tt_Z");
            tt_W = f_central.Get("metEta_h_"+jet_num+"tt_W");
            DATA = f_central.Get("metEta_h_"+jet_num+"data");
            QCData = f_templates.Get("metEta_h_"+jet_num_temp);

            ttbarAll = f_all.Get("metEta_h_"+jet_num+"ttbar");
 
            tt_sys = f_central.Get("metEta_h_"+jet_num+"tt"+syst[sysErr]);  
            #wjets_sys = f_central.Get("metEta_h_"+jet_num+"wjets"+syst[sysErr]);
            #zjets_sys = f_central.Get("metEta_h_"+jet_num+"zjets"+syst[sysErr]);
  
            #for other gens
            ttbar_nlo = f_central.Get("metEta_h_"+jet_num+"nlo");   
            ttbar_powheg = f_central.Get("metEta_h_"+jet_num+"powheg");
            ttbar_nloAll = f_all.Get("metEta_h_"+jet_num+"nlo");
            ttbar_powhegAll = f_all.Get("metEta_h_"+jet_num+"powheg");
 
            #for sys up/down
  
            ttbar_sys = f_central.Get("metEta_h_"+jet_num+"tt_qup");   
            ttbar_sysdown = f_central.Get("metEta_h_"+jet_num+"tt_qdown");
            ttbarUpAll = f_all.Get("metEta_h_"+jet_num+"tt_qup");
            ttbarDownAll = f_all.Get("metEta_h_"+jet_num+"tt_qdown");
  
            ttbar_mup = f_central.Get("metEta_h_"+jet_num+"tt_mup");
            ttbar_mdown = f_central.Get("metEta_h_"+jet_num+"tt_mdown");
            ttbarUpAllMat = f_all.Get("metEta_h_"+jet_num+"tt_mup");
            ttbarDownAllMat = f_all.Get("metEta_h_"+jet_num+"tt_mdown");
  
            #Choose rebin factor...
            rebinF = 8;

            ttbar_sys.Rebin(rebinF);

            #tt_sys.Rebin(rebinF);
            #wjets_sys.Rebin(rebinF);
            #zjets_sys.Rebin(rebinF);
  
            ttbar_sysdown.Rebin(rebinF);  
            ttbar_mup.Rebin(rebinF);
            ttbar_mdown.Rebin(rebinF);

            ttbar_nlo.Rebin(rebinF);
            ttbar_powheg.Rebin(rebinF);
 

            signal.Rebin(rebinF);
            wjets.Rebin(rebinF);
            zjets.Rebin(rebinF);
            QCD.Rebin(rebinF);
            SinglT.Rebin(rebinF);
            ttbar.Rebin(rebinF);
            tt_Z.Rebin(rebinF);
            tt_W.Rebin(rebinF);
            DATA.Rebin(rebinF);
            QCData.Rebin(rebinF/2);


            NttbarUp = ttbar_sys.Integral();
            NtotPassUp = ttbarUpAll.Integral();    
            NttbarDown = ttbar_sysdown.Integral();
            NtotPassDown = ttbarDownAll.Integral();      
            NttbarUpMat = ttbar_mup.Integral();
            NtotPassUpMat = ttbarUpAllMat.Integral();    
            NttbarDownMat = ttbar_mdown.Integral();
            NtotPassDownMat = ttbarDownAllMat.Integral();

            NttbarNLO = ttbar_nlo.Integral();
            NtotPassNLO = ttbar_nloAll.Integral();    
            NttbarPOW = ttbar_powheg.Integral();
            NtotPassPOW = ttbar_powhegAll.Integral();
 
            Nsignal = signal.Integral();
            Nwjets = wjets.Integral();
            Nzjets = zjets.Integral();
            NQCD = QCD.Integral();
            NSinglT = SinglT.Integral();
            Nttbar = ttbar.Integral();
            NtotPass = ttbarAll.Integral();


            Ntt_Z =tt_Z.Integral();
            Ntt_W =tt_W.Integral();
            tot =   Nttbar+NSinglT+NQCD+Nzjets+Nwjets+Ntt_Z+Ntt_W;
            Ndata = DATA.Integral();
            wstring = "wjets";
            zstring = "zjets";
            qcdstring = "";


            # Read in the data and templates.
            getDataFromHis(f_central, jet_num, nbins); # Get data histrogram form central selection
            getSignalFromHis(f_central, jet_num, syst[sysErr], nbins, ttbar_Vec, ttbar_err_Vec);# Get ttbar, single-top histrograms form MC with entral selection 

            getTemFromHis(f_central, wstring, jet_num, nbins, wjets_Vec, wjets_err_Vec);                 
            getTemFromHis(f_central, zstring, jet_num, nbins, zjets_Vec, zjets_err_Vec);
            getTemFromHis(f_templates, qcdstring, jet_num_temp, nbins, qcd_Vec, qcd_err_Vec);

            f_central.Close();
            f_templates.Close(); 
 
  # Initialize minuit, set initial values etc. of parameters.
            npar = 4;              # the number of parameters
            minuit = TMinuit(npar);
            minuit.SetFCN(fcn);
  
  #minuit.SetPrintLevel(1);
            minuit.SetPrintLevel(-1);
            minuit.SetErrorDef(1.);
 
            fraction= NSinglT/Nsignal;
  
            ierflg = 0;
            parName = ["ttbar+single-top", "wjets", "zjets", "qcd"] #background parameters
            par = [Nsignal, Nwjets, Nzjets, NQCD]               #using the MC estimation as the start values 1fb

            for i=0 in range(0,npar):
                minuit.mnparm(i, parName[i], par[i], 10., 0, Ntotal, ierflg);

            #the following is copied from Fabian's fitting code to improve minimum, but you can comment it, it won't affect the fitting results.
            # 1 standard
            # 2 try to improve minimum (slower)
            arglist = [0]*10;
            arglist[0]=1;
            minuit.mnexcm("SET STR",arglist,1,ierflg);
            minuit.Migrad();
  
            outpar = [0]*npar
            err = [0]*npar;
    
            for i=0 in range(0,npar):
                minuit.GetParameter(i,outpar[i],err[i]);
  
            xs_fit = (outpar[0]-NSinglT)/(NtotPass/theorXsect);  #=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
            xs_fitup = (outpar[0]+err[0]-NSinglT)/(NtotPass/theorXsect);  #=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
            xs_fitdown = (outpar[0]-err[0]-NSinglT)/(NtotPass/theorXsect);  #=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  
            #madgraph
            theorNum = (Nttbar)/(NtotPass/theorXsect);
            nloNum = (NttbarNLO)/(NtotPassNLO/theorXsect);
            powhegNum = (NttbarPOW)/(NtotPassPOW/theorXsect);

            #systematics  
            upNum = (NttbarUp)/(NtotPassUp/theorXsect);
            downNum = (NttbarDown)/(NtotPassDown/theorXsect);  

            mupNum = (NttbarUpMat)/(NtotPassUpMat/theorXsect);
            mdownNum = (NttbarDownMat)/(NtotPassDownMat/theorXsect); 

  
  
            totXsect += xs_fit;

            data_Vec = []
            ttbar_Vec = []
            wjets_Vec = []
            zjets_Vec = []
            qcd_Vec = []

            ttbar_err_Vec = []
            wjets_err_Vec = []
            zjets_err_Vec = []
            qcd_err_Vec = []


            width = measured.GetBinWidth(met+1);

            measured.SetBinContent(met+1,xs_fit/width);
            measured.SetBinError(met+1,(xs_fitup-xs_fit)/width);     

            nlo.SetBinContent(met+1,nloNum/157.5/width);
            powheg.SetBinContent(met+1,powhegNum/157.5/width);
            theor.SetBinContent(met+1, (theorNum/157.5/width)); 

            sysup.SetBinContent(met+1, (upNum/157.5/width)); 
            sysdown.SetBinContent(met+1, (downNum/157.5/width)); 
            mup.SetBinContent(met+1, (mupNum/157.5/width)); 
            mdown.SetBinContent(met+1, (mdownNum/157.5/width));


            x[met] = measured.GetBinCenter(met+1);
            y[met] = xs_fit/width;
            #exl[met] = measured.GetBinWidth(met+1)/2.;
            #exh[met] = measured.GetBinWidth(met+1)/2.;
            exl[met] = 0.;
            exh[met] = 0.;

        #uncertainties*****************************************************************************
        tempStat = [1.806/25./157.5, 1.888/20./157.5, 2.051/25./157.5, 1.072/30./157.5, 1.215/50./157.5];

        JESup = [-0.000151962 , 0.000272578 , -4.23099e-05 , -3.70002e-05 , 7.25276e-06]; 
        JESdown = [-8.05871e-05 , -0.000135049 , -5.47969e-05 , -1.05896e-05 , 0.000126441];
        
        Qallup = [0.000661542 , -0.00164854 , 0.0015185 , -0.000777495 , 4.91053e-05];
        Qalldown = [0.000976746 , -0.00126681 , 9.94392e-06 , -0.000330413 , 0.000231151];
        
        Mallup = [0.00107054 , -0.00175803 , 0.000500762 , -0.000368955 , 0.000160332];
        Malldown = [0.00054994 , -0.000711093 , 0.000512741 , -0.000469302 , 4.56639e-05];
        
        singletD = [3.79915e-06 , -1.64281e-05 , 1.61034e-05 , -1.38118e-05 , 4.97002e-06];
        singletU = [-3.95387e-06 , 1.7004e-05 , -1.67224e-05 , 1.4347e-05 , -5.16378e-06 ];

        lumiD = [-5.15494e-06 , -2.72603e-06 , -5.41703e-06 , 2.85952e-06 , 4.54458e-06];
        lumiU = [7.62411e-06 , -3.49747e-06 , 3.93426e-06 , -6.09136e-06 , -5.85902e-07];

        pdf = [2.71e-05 , 3.66e-05 , 1.28e-05 , 1.33e-05 , 1.03e-05];

        METup = [0.000177 , -0.000654 , 0.000105 , 1.24e-05 , 0.000117];
        METdown = [2.12e-05 , 0.000176 , 0.00031 , -0.000145 , -0.000149];

        stat = [0.000370122 , 0.000482173 , 0.000393533 , 0.000199431 , 0.000133263];

        up = [0]*5
        down = [0]*5

        for bin in range(0,5):
            down[bin] = sqrt(pow(JESdown[bin],2)+pow(Qalldown[bin],2)+pow(Malldown[bin],2)+pow(singletD[bin],2)+pow(lumiD[bin],2)+pow(pdf[bin],2)+pow(METdown[bin],2)+pow(stat[bin],2)+pow(tempStat[bin],2));
            up[bin] = sqrt(pow(JESup[bin],2)+pow(Qallup[bin],2)+pow(Mallup[bin],2)+pow(singletD[bin],2)+pow(lumiD[bin],2)+pow(pdf[bin],2)+pow(METup[bin],2)+pow(stat[bin],2)+pow(tempStat[bin],2));
            y[bin] = y[bin]/totXsect;

        #electron values for >=2btags
        eleres = [0.01*0.70, 0.01*1.25, 0.01*1.08, 0.01*0.56, 0.01*0.27];
        eleyl = [sqrt(pow(0.01*0.12,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.01,2)+pow(0.01*0.06,2)),sqrt(pow(0.01*0.19,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.05,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.03,2)+pow(0.01*0.01 ,2))];
        eleyh = [sqrt(pow(0.01*0.04,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.37,2)+pow(0.01*0.06,2)),sqrt(pow(0.01*0.03,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.07,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.01,2)+pow(0.01*0.01 ,2))]; 
        #electron values for geq to 4jets
        #  double eleres[5] = {0.01*0.39, 0.01*0.99, 0.01*1.25, 0.01*0.73, 0.01*0.35};
        #  double eleyl[5] = {sqrt(pow(0.01*0.51,2)+pow(0.01*0.07 ,2)),sqrt(pow(0.01*0.10,2)+pow(0.01*0.09,2)),sqrt(pow(0.01*0.40,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.02,2)+pow(0.01*0.39,2)),sqrt(pow(0.01*0.17,2)+pow(0.01*0.02 ,2))};
        #  double eleyh[5] = {sqrt(pow(0.01*0.76,2)+pow(0.01*0.07 ,2)),sqrt(pow(0.01*0.63,2)+pow(0.01*0.09,2)),sqrt(pow(0.01*0.24,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.02,2)+pow(0.01*0.12,2)),sqrt(pow(0.01*0.08,2)+pow(0.01*0.02 ,2))}; 

        #electron values******************************************************************** 
        grele = TGraphAsymmErrors(n,x,eleres,exl,exh,eleyl,eleyh);
        grele.SetMarkerStyle(20);
        grele.SetMarkerColor(4);
        grele.SetLineColor(4);
        grele.SetMarkerStyle(26);

        for bin in range(0,5):
            ele.SetBinContent(bin+1,eleres[bin]);
            ele.SetBinError(bin+1,0.000001);

        ele.SetMarkerStyle(20);
        ele.SetMarkerColor(4);
        ele.SetLineColor(4);

 #muon values*************************************************************************
        eyl = [down[0],down[1],down[2],down[3],down[4]];
        eyh = [up[0],up[1],up[2],up[3],up[4]];   
        gr = TGraphAsymmErrors(n,x,y,exl,exh,eyl,eyh);
        gr.SetMarkerColor(1);
        gr.SetMarkerStyle(20);
        gr.SetFillStyle(3004);


        c= TCanvas("c","c",10,10,800,600);
  


measured.SetMarkerStyle(20);
measured.Scale(1./ totXsect); 
#std::cout << "total measured x sect: " << totXsect << std::endl;

#cout.precision(3);
#std::cout << "temp stat: " << std::endl;
#for(int i = 0; i<5; i++){
#std::cout <<  tempStat[i] << "(" << (tempStat[i]/measured.GetBinContent(i+1))*100 << "\\%)" << " & " ;
#}

 #central previous vals no trigs
 double central[5] = {0.00609465 , 0.0145213 , 0.0116628 , 0.00549336 , 0.00213862};

#std::cout << (measured.GetBinError(1)/y[0])*100 << " , " << (measured.GetBinError(2)/y[1])*100  << " , " <<  (measured.GetBinError(3)/y[2])*100 << " , " <<   (measured.GetBinError(4)/y[3])*100 << " , " <<   (measured.GetBinError(5)/y[4])*100 << std::endl;

   #uncertaint write out for muon
# std::cout << "tot up: " << std::endl;
# for(int i = 0; i<5; i++){
# std::cout <<  up[i] << "(" << (up[i]/measured.GetBinContent(i+1))*100 << "\\%)" << " & " ;
# }
# std::cout << "tot down: " << std::endl;
# for(int i = 0; i<5; i++){
# std::cout <<  down[i] << "(" << (down[i]/measured.GetBinContent(i+1))*100 << "\\%)" << " & " ;
# }
  

#Combination!!!*********************************************************************************
#std::cout << " combined vals: " << std::endl;
#combination stuff
double val[5]; double combUp[5]; double combDown[5];
for(int i = 0; i<5; i++){
double valnum = (measured.GetBinContent(i+1)/pow(up[i],2))+(measured.GetBinContent(i+1)/pow(down[i],2))+(eleres[i]/pow(eleyh[i],2))+(eleres[i]/pow(eleyl[i],2));
double den = (1./pow(up[i],2))+(1./pow(down[i],2))+(1./pow(eleyh[i],2))+(1./pow(eleyl[i],2));
val[i] = valnum/den;

combUp[i] = sqrt(1./(1./pow(up[i],2)+pow(eleyh[i],2)));
combDown[i] = sqrt(1./(1./pow(down[i],2)+pow(eleyl[i],2)));

#std::cout << val[i]  << " , " ;
comb.SetBinContent(i+1, val[i]);
comb.SetBinError(i+1, 0.00000000001);
}

TGraphAsymmErrors* grcomb = TGraphAsymmErrors(n,x,val,exl,exh,combDown,combUp);
 grcomb.SetMarkerStyle(20);
 grcomb.SetMarkerColor(7);
 grcomb.SetLineColor(7);
 grcomb.SetMarkerStyle(20);
 
 comb.SetMarkerStyle(20);
 comb.SetMarkerColor(7);
 comb.SetLineColor(7);

#show nominal calculated values
for(int i =1; i < 6; i++){
nominal.SetBinContent(i,central[i-1]);
 }
  
  
  #plot colors
     theor.SetLineColor(kRed+1);
     sysup.SetLineColor(kOrange+1);
     sysdown.SetLineColor(kGreen+1);
     mup.SetLineColor(kBlue+1);
     mdown.SetLineColor(kYellow+1);
     #theor.SetFillColor(kRed+1);
     nominal.SetLineColor(kBlue+1);
     
     sysup.SetLineStyle(7);
     sysdown.SetLineStyle(7);
     mup.SetLineStyle(7);
     mdown.SetLineStyle(7);

     nlo.SetLineStyle(7);
     powheg.SetLineStyle(7);
     nlo.SetLineColor(kBlue+1);
     powheg.SetLineColor(kGreen+1);

theor.SetMinimum(0);
theor.SetMaximum(0.02);    


theor.Draw();
#nominal.Draw("same");
#measured.Draw("Esame");
#ele.Draw("Esame");
gr.Draw("P");
#ele and combined
#grele.Draw("Esame");
#comb.Draw("Esame");
#grcomb.Draw("Esame"); 

nominal.Draw("same");

#systs
# sysup.Draw("same");
# sysdown.Draw("same");
# mup.Draw("same");
# mdown.Draw("same");

#gens
#nlo.Draw("same");
#powheg.Draw("same");

#too see effect of an uncertainty for input of uncertainty

#cout.precision(4);
#too see effect of an uncertainty

#std::cout  <<  " output:  " << std::endl;
for(int bin = 1; bin<=5; bin++){
  #std::cout << 100*(measured.GetBinContent(bin)-nominal.GetBinContent(bin))/measured.GetBinContent(bin)  << "\\\% & " ;
  #for table (later) 
  std::cout << (measured.GetBinContent(bin)-nominal.GetBinContent(bin)) << " , " ;


}

std::cout << totXsect << std::endl;

#legend
  TLegend *tleg;
  tleg = TLegend(0.65,0.75,0.9,0.9);
  tleg.SetTextSize(0.03);
  tleg.SetBorderSize(0);
  tleg.SetFillColor(10);


  tleg.AddEntry(gr  , "data '11'"      , "lep"); 
#  tleg.AddEntry(ele  , "e+jets (#geq 4 jets, #geq 2 btags)"      , "lpe");
#  tleg.AddEntry(ele  , "e+jets (#geq 4 jets)"      , "lpe");
#  tleg.AddEntry(comb  , "combined"      , "lpe");

  tleg.AddEntry(theor    , "t#bar{t} (MADGRAPH)"  , "l");
#  tleg.AddEntry(nlo    , "t#bar{t} (MC@NLO)"  , "l");
#  tleg.AddEntry(powheg    , "t#bar{t} (POWHEG)"  , "l");
  
  #for sys 
#   tleg.AddEntry(sysup    , "t#bar{t} Q^{2} up "  , "l"); 
#   tleg.AddEntry(sysdown    , "t#bar{t} Q^{2} down "  , "l"); 
#   tleg.AddEntry(mup    , "t#bar{t} matching up "  , "l"); 
#   tleg.AddEntry(mdown    , "t#bar{t} matching down "  , "l");
#tleg.AddEntry(nominal    , "no trigger corrections"  , "l");

  tleg.Draw("same");



#titles
theor.GetYaxis().SetTitle("#frac{1}{#sigma} #frac{#partial #sigma}{#partial MET} [GeV^{-1}]");theor.GetYaxis().SetTitleSize(0.05);
theor.GetXaxis().SetTitle("MET [GeV]"); theor.GetXaxis().SetTitleSize(0.05);

  TText* textPrelim = doPrelim(lumi,0.16,0.96); 
  textPrelim.Draw();

#delete c;
} #end sys loop

#c.SetLogy(1);

#c.SaveAs("240712plots/eComb.png");
#c.SaveAs("240712plots/eComb.pdf");

return 0;

}

#-------------------------------------------------------------------------

#  function to read in the data from a histogram
void getDataFromHis(inputFile, TString& jet_num, int& nxbins){

  TH1F *h_data = (TH1F*) inputFile.Get("metEta_h_"+jet_num+"data");
Ntotal=0;

#    output = TFile.Open("muData.root","UPDATE");
#   # his_mc_array.Scale(10909.);
#   h_data.SetName("muData");
#   h_data.Write();



  nbins = h_data.GetNbinsX();
  
  xmax = xmin + nxbins*(h_data.GetBinWidth(1));
  
 # cout<<"num of bins: "<<nbins<<" xmax: "<<xmax<<endl;

  for(int ibin=0; ibin<nxbins; ibin++){

    int nn = h_data.GetBinContent(ibin+1);

    data_Vec.push_back(nn);

    Ntotal += nn;
   
  }

  # cout <<" \n Total number of events before the fit" << endl;
  #cout <<"  Data: \t "<<Ntotal<<endl;

}



void getTemFromHis(inputFile, TString& templ, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err){

  TH1F* his_mc_array =  (TH1F*) inputFile.Get("metEta_h_"+jet_num+templ);

  #std::cout<<"test: "<<his_mc_array.Integral()<<std::endl;

  his_mc_array.Scale(1./his_mc_array.Integral());
  #std::cout<<"test: "<<nxbins<<std::endl;
  #std::cout << templ << ":  {" << std::endl;
  
  for(int ibin=0; ibin<nxbins; ibin++){

    vect.push_back(his_mc_array.GetBinContent(ibin+1));
    vect_err.push_back(his_mc_array.GetBinError(ibin+1));

    #std::cout << "{" << his_mc_array.GetBinContent(ibin+1) << "," << his_mc_array.GetBinError(ibin+1) << "}, ";

  }
  #std::cout<< "}" << std::endl;

}


void getSignalFromHis(inputFile, TString& jet_num, TString& syst,int& nxbins, vector<double>& vect, vector<double>& vect_err){


  TH1F* his_mc_array = (TH1F*) inputFile.Get("metEta_h_"+jet_num+"tt"+syst);  
  TH1F* his_mc_stop = (TH1F*) inputFile.Get("metEta_h_"+jet_num+"SinglT");
  his_mc_array.Add(his_mc_stop);
  
  his_mc_array.Scale(1./his_mc_array.Integral());




#   output = TFile.Open("signal.root","UPDATE");
#   # his_mc_array.Scale(10909.);
#   his_mc_array.SetName("SignalTemplate");
#   his_mc_array.Write();


  for(int ibin=0; ibin<nxbins; ibin++){

    vect.push_back(his_mc_array.GetBinContent(ibin+1));
    vect_err.push_back(his_mc_array.GetBinError(ibin+1));

  }


}
#-------------------------------------------------------------------------

# fcn passes back f = - 2*ln(L), the function to be minimized. not sure if N_{single top} is obtained from fitting
void fcn(int& npar, double* deriv, double& f, double par[], int flag){

  double lnL = 0.0;


  for (int i=0; i<nbins; i++){

    #data_i is the observed number of events in each bin
    int data_i = data_Vec[i];
    #xi is the expected number of events in each bin
    double xi = par[0]*ttbar_Vec[i] + par[1]*wjets_Vec[i] + par[2]*zjets_Vec[i] + par[3]*qcd_Vec[i];


    if(data_i !=0 && xi != 0){
      lnL += log(TMath::Poisson(data_i, xi));
    }
    
   # cout << "data:" << data_i << "  xi: " << xi <<   " lnL:  " << log(TMath::Poisson(data_i, xi)) << endl;
    
  }

  #W+jets, Z+jets constraints
  f = -2.0 * lnL;
  

  double nwjets = Nwjets;
  double nwjets_err = nwjets*0.3;
  #double nwjets_err = nwjets*0.02;
   
  double nzjets = Nzjets;
  double nzjets_err = nzjets*0.1;

double nqcd = 0;
if(NQCD>0){
  nqcd = NQCD;
  }
  else{
  nqcd = 0.00000001;
  }
  double nqcd_err = nqcd*1.;

  #cout << "qcd:" <<  NQCD << "  ,par3: " << par[3] << endl;

  #double r = nwjets/nzjets;
  #double r_err = r*0.01;

  #f += (par[1]/par[2]-r)*(par[1]/par[2]-r)/r_err/r_err;
  #Wjets constrain
#   f += (par[1]-nwjets)*(par[1]-nwjets)/nwjets_err/nwjets_err;
#   #Zjets constrain
#   f += (par[2]-nzjets)*(par[2]-nzjets)/nzjets_err/nzjets_err;
#   #QCD constrain
#   f += (par[3]-nqcd)*(par[3]-nqcd)/nqcd_err/nqcd_err;

  #Ratio Constrain
  #f += ( (par[1]/par[2] - nwjets/nzjets) / (0.3 *nwjets/nzjets) )  * ( (par[1]/par[2] - nwjets/nzjets) / (0.3*nwjets/nzjets) ) * ( (par[1]/par[2] - nwjets/nzjets) / (0.3*nwjets/nzjets) ) * ( (par[1]/par[2] - nwjets/nzjets) / (0.3*nwjets/nzjets) ); #chi4?
  

  #ratio constraints
   f += ( (par[2]/par[1] - nzjets/nwjets) / (0.05 *nzjets/nwjets) )  * ( (par[2]/par[1] - nzjets/nwjets) / (0.05*nzjets/nwjets) ); #swap


   f += ((par[3]-nqcd)*(par[3]-nqcd))/nqcd_err/nqcd_err;


}                         

#########################################################################/
def doPrelim(luminosity, x, y):
    stream  = "#mu, #geq 4 jets, #geq 2 b-tags                     CMS Preliminary, L = 5.0 fb^{-1} @ #sqrt{s} = 7 TeV";   

    text = TLatex(x, y, stream);
    #text.SetTextAlign(33);  #left
    #text.SetTextAlign(22);  #center
    #text.SetTextAlign(11);  #right
    text.SetNDC(true);
    text.SetTextFont(42);
    text.SetTextSize(0.035);  # for thesis

  return text;
}
