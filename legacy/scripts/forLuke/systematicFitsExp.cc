/*A C++ program to use of ROOT class TMinuit for function minimization.It shows a Maximum Likelihood fit for the mean of a binned Poisson pdf in which TMinuit minimizes
 - 2*log(L). fcn passes back f = -2*ln L by reference; this is the function to minimize.

  The factor of -2 allows MINUIT to get the errors using the same recipe as for least squares, i.e., go up from the minimum by 1.

  TMinuit does not allow fcn to be a member function, and the function arguments are fixed, so the one of the only ways to bring the data   into fcn is to declare a poi
nter to the data (xVecPtr) as global.

  For more info on TMinuit see root.cern.ch/root/html/TMinuit.html .

*/

#include <iostream>
#include <cstdlib>
#include <cmath>
#include <string>
#include <vector>

#include <TMinuit.h>
#include <TCanvas.h>
#include <TStyle.h>
#include <TROOT.h>
#include <TF1.h>
#include <TAxis.h>
#include <TLine.h>
#include <TMath.h>
#include <THStack.h>
#include <sstream>
#include "TLatex.h"
#include "TText.h"
#include "TLegend.h"
#include "TFile.h"
#include "TGraphAsymmErrors.h"

#include "tdrstyle.C"

using namespace std;
// Declare pointer to data as global (not elegant but TMinuit needs this).
vector<int> data_Vec; //input data

vector<double> ttbar_Vec; //ttbar+single top template from mc
vector<double> wjets_Vec; //wjest template from data driven method
vector<double> zjets_Vec; //zjets template from data driven method
vector<double> qcd_Vec;   //qcd template from data drive method

vector<double> ttbar_err_Vec;
vector<double> wjets_err_Vec; //wjest template from data driven method
vector<double> zjets_err_Vec; //zjets template from data driven method
vector<double> qcd_err_Vec;   //qcd template from data drive method


int Ntotal; //define as global, got in getDataFromHis function
int nbins; //define as global, also got in getDataFromHis function, and it is been used in getTemFromHis function

//double xbins[13] = {0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4};


double xmin = 0;
double xmax; //calculate in getDataFromHis function

void fcn(int& npar, double* deriv, double& f, double par[], int flag);
void getDataFromHis(TFile* inputFile, TString& jet_num, int& nxbins);
void getSignalFromHis(TFile* inputFile, TString& jet_num, TString& syst, int& nxbins, vector<double>& vect, vector<double>& vect_err);
void getTemFromHis(TFile* inputFile, TString& templ, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err);


TText* doPrelim(float luminosity, float x, float y);

//double lumi = 964.6;
//double lumi = 987.2;
double lumi = 4973.4;

  double Nsignal;
  double Nwjets;
  double Nzjets;
  double NQCD;
  double NSinglT;
  double Nttbar;
  double NtotPass;
  double NttbarUp;
  double NtotPassUp; 
  double NttbarDown;
  double NtotPassDown;
  
  double NttbarUpMat;
  double NtotPassUpMat; 
  double NttbarDownMat;
  double NtotPassDownMat;
  
  double NttbarNLO;
  double NtotPassNLO;
  double NttbarPOW;
  double NtotPassPOW;
  
//-------------------------------------------------------------------------

int systematicFitsExp() {
setTDRStyle();



  // Choose the jet multiplicity
  TString jet_num = "2b_";
  TString jet_num_temp = "ge2j";
  
  TString metBin[5] = {"1","2","3","4","5"};

//choose what to use
TString templ = "_central";


   //differential histo
   double xbins[6]= {1,25,45,70,100,150}; 
   //histograms for comaprison
   //diff generators	
   TH1D *theor  = new TH1D("theor", "", 5, xbins);  
   TH1D *nlo =  new TH1D("nlo", "", 5, xbins);
   TH1D *powheg =  new TH1D("powheg", "", 5, xbins);
   //syst samples
   TH1D *sysup = new TH1D("sysup", "", 5, xbins); 
   TH1D *sysdown = new TH1D("sysdown", "", 5, xbins); 
   TH1D *mup = new TH1D("mup", "", 5, xbins); 
   TH1D *mdown = new TH1D("mdown", "", 5, xbins); 
   //measured
   TH1D *measured  = new TH1D("meas", "", 5, xbins);  //muon
   TH1D *ele  = new TH1D("ele", "", 5, xbins);     
   TH1D *comb  = new TH1D("comb", "", 5, xbins); 
   //compare histo
   TH1D *nominal  = new TH1D("nominal", "", 5, xbins);
  
  //theroy onn ttbar only due to stats (need to also change the string for w/z)
  //TString syst[4] = {"_qup","_qdown","_mup","_mdown"};
   
  TString syst[8] = {"_jup","_jdown","_METup","_METdown","_pup","_pdown","_bup","_bdown"};

        
for(int sysErr = 0; sysErr < 8; sysErr++){

std::cout << syst[sysErr] << std::endl;

//asymerrors
   int n = 5;
   double x[n];   
   double y[n];   
   double exl[n]; 
   double exh[n]; 

double theorNum = 0;	
double nloNum = 0;
double powhegNum = 0;
	
//syst
double upNum = 0;  
double downNum = 0; 
double mupNum = 0;  
double mdownNum = 0; 

double theorXsect = 157.5;
double totXsect = 0;
 for(int met = 0; met<5; met++){
  //for systematics
  TFile* f_central = TFile::Open("PFhistosForFitting_met"+metBin[met]+templ+".root");  
  TFile* f_all = TFile::Open("PFhistosForFitting_metall"+templ+".root");
  TFile* f_templates  = TFile::Open("QCDetaData.root");

  TH1D* signal = (TH1D*) f_central->Get("metEta_h_"+jet_num+"signal");
  TH1D* wjets = (TH1D*) f_central->Get("metEta_h_"+jet_num+"wjets");
  TH1D* zjets = (TH1D*) f_central->Get("metEta_h_"+jet_num+"zjets");
  TH1D* SinglT = (TH1D*) f_central->Get("metEta_h_"+jet_num+"SinglT");
  TH1D* ttbar = (TH1D*) f_central->Get("metEta_h_"+jet_num+"ttbar");
  
  TH1D* QCD = (TH1D*) f_central->Get("metEta_h_"+jet_num+"QCD");
  TH1D* tt_Z = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_Z");
  TH1D* tt_W = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_W");
  TH1D* DATA = (TH1D*) f_central->Get("metEta_h_"+jet_num+"data");
  TH1D* QCData = (TH1D*) f_templates->Get("metEta_h_"+jet_num_temp);

  TH1D* ttbarAll = (TH1D*) f_all->Get("metEta_h_"+jet_num+"ttbar");
 
  TH1D* tt_sys = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt"+syst[sysErr]);  
  TH1D* wjets_sys = (TH1D*) f_central->Get("metEta_h_"+jet_num+"wjets"+syst[sysErr]);
  TH1D* zjets_sys = (TH1D*) f_central->Get("metEta_h_"+jet_num+"zjets"+syst[sysErr]);
  
  //for other gens
  TH1D* ttbar_nlo = (TH1D*) f_central->Get("metEta_h_"+jet_num+"nlo");   
  TH1D* ttbar_powheg = (TH1D*) f_central->Get("metEta_h_"+jet_num+"powheg");
  TH1D* ttbar_nloAll = (TH1D*) f_all->Get("metEta_h_"+jet_num+"nlo");
  TH1D* ttbar_powhegAll = (TH1D*) f_all->Get("metEta_h_"+jet_num+"powheg");
 
  //for sys up/down
  
  TH1D* ttbar_sys = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_qup");   
  TH1D* ttbar_sysdown = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_qdown");
  TH1D* ttbarUpAll = (TH1D*) f_all->Get("metEta_h_"+jet_num+"tt_qup");
  TH1D* ttbarDownAll = (TH1D*) f_all->Get("metEta_h_"+jet_num+"tt_qdown");
  
  TH1D* ttbar_mup = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_mup");
  TH1D* ttbar_mdown = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_mdown");
  TH1D* ttbarUpAllMat = (TH1D*) f_all->Get("metEta_h_"+jet_num+"tt_mup");
  TH1D* ttbarDownAllMat = (TH1D*) f_all->Get("metEta_h_"+jet_num+"tt_mdown");
  
  //Choose rebin factor...
int rebinF = 8;
// if(met==4){
// rebinF=4;
// }
  

  ttbar_sys->Rebin(rebinF);

  tt_sys->Rebin(rebinF);
  wjets_sys->Rebin(rebinF);
  zjets_sys->Rebin(rebinF);
  
  ttbar_sysdown->Rebin(rebinF);  
   
  ttbar_mup->Rebin(rebinF);
  ttbar_mdown->Rebin(rebinF);

  ttbar_nlo->Rebin(rebinF);
  ttbar_powheg->Rebin(rebinF);
 

  signal->Rebin(rebinF);
  wjets->Rebin(rebinF);
  zjets->Rebin(rebinF);
  QCD->Rebin(rebinF);
  SinglT->Rebin(rebinF);
  ttbar->Rebin(rebinF);
  tt_Z->Rebin(rebinF);
  tt_W->Rebin(rebinF);
  DATA->Rebin(rebinF);
  QCData->Rebin(rebinF/2);


//  cout << "input params: " << endl;
  //systematic samples 
  NttbarUp = ttbar_sys->Integral();
  NtotPassUp = ttbarUpAll->Integral();    
  NttbarDown = ttbar_sysdown->Integral();
  NtotPassDown = ttbarDownAll->Integral();      
  NttbarUpMat = ttbar_mup->Integral();
  NtotPassUpMat = ttbarUpAllMat->Integral();    
  NttbarDownMat = ttbar_mdown->Integral();
  NtotPassDownMat = ttbarDownAllMat->Integral();

  NttbarNLO = ttbar_nlo->Integral();
  NtotPassNLO = ttbar_nloAll->Integral();    
  NttbarPOW = ttbar_powheg->Integral();
  NtotPassPOW = ttbar_powhegAll->Integral();
 
  Nsignal = signal->Integral();
  Nwjets = wjets->Integral();
  Nzjets = zjets->Integral();
  NQCD = QCD->Integral();
  NSinglT = SinglT->Integral();
  Nttbar = ttbar->Integral();
  NtotPass = ttbarAll->Integral();


double Ntt_Z =tt_Z->Integral();
double Ntt_W =tt_W->Integral();
double tot =   Nttbar+NSinglT+NQCD+Nzjets+Nwjets+Ntt_Z+Ntt_W;
double Ndata = DATA->Integral();
//  cout  << "all tt: " << NtotPass << endl;
//  cout  << "signal: " << Nsignal << endl;
//  cout  << "wjets: " << Nwjets<< endl;
//  cout  << "zjets: " << Nzjets << endl;
//  cout  << "qcd: " << NQCD << endl;
  
  TString wstring = "wjets"+syst[sysErr];
  TString zstring = "zjets"+syst[sysErr];
  TString qcdstring = "";


  // Read in the data and templates.
  getDataFromHis(f_central, jet_num, nbins); // Get data histrogram form central selection
  getSignalFromHis(f_central, jet_num, syst[sysErr], nbins, ttbar_Vec, ttbar_err_Vec);// Get ttbar, single-top histrograms form MC with entral selection 

  getTemFromHis(f_central, wstring, jet_num, nbins, wjets_Vec, wjets_err_Vec);                 
  getTemFromHis(f_central, zstring, jet_num, nbins, zjets_Vec, zjets_err_Vec);
  getTemFromHis(f_templates, qcdstring, jet_num_temp, nbins, qcd_Vec, qcd_err_Vec);

  f_central->Close();
  f_templates->Close(); 
 
  // Initialize minuit, set initial values etc. of parameters.
  const int npar = 4;              // the number of parameters
  TMinuit minuit(npar);
  minuit.SetFCN(fcn);
  
  //minuit.SetPrintLevel(1);
  minuit.SetPrintLevel(-1);
  minuit.SetErrorDef(1.);
 
 double fraction= NSinglT/Nsignal;
  
  int ierflg = 0;
  string parName[npar] = {"ttbar+single-top", "wjets", "zjets", "qcd"}; //background parameters
  double par[npar] = {Nsignal, Nwjets, Nzjets, NQCD};               //using the MC estimation as the start values 1fb

  //cout << "total data events: " << Ntotal << endl;

  for(int i=0; i<npar; i++){
    
    //minuit.mnparm(i, parName[i], par[i], 10., -1.e6, 1.e6, ierflg);
    minuit.mnparm(i, parName[i], par[i], 10., 0, Ntotal, ierflg);

  }
    


  //the following is copied from Fabian's fitting code to improve minimum, but you can comment it, it won't affect the fitting results.
  // 1 standard
  // 2 try to improve minimum (slower)
  double arglist[10];
  arglist[0]=1;
  minuit.mnexcm("SET STR",arglist,1,ierflg);
  minuit.Migrad();
  
  double outpar[npar], err[npar];
    
  for (int i=0; i<npar; i++){
    minuit.GetParameter(i,outpar[i],err[i]);
  }



  //print out the results
 // cout <<" \n Total number of events after the fit" << endl;
 // cout<<"   & ttbar+single top & w+jets & z+jets & qcd "<<endl;
 // cout <<  " & " << Nsignal <<  " & " << Nwjets << " & " <<  Nzjets << " & " <<  NQCD  <<endl;
 // cout << " & "<<outpar[0]<<"+-"<<err[0]<<" & "<<outpar[1]<<"+-"<<err[1]<<" & "<<outpar[2]<<"+-"<<err[2]<<" & "<<outpar[3]<<"+-"<<err[3]<<endl;
  
  double xs_fit = (outpar[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  double xs_fitup = (outpar[0]+err[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  double xs_fitdown = (outpar[0]-err[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  
  //madgraph
  theorNum = (Nttbar)/(NtotPass/theorXsect);
  nloNum = (NttbarNLO)/(NtotPassNLO/theorXsect);
  powhegNum = (NttbarPOW)/(NtotPassPOW/theorXsect);

  //systematics  
  upNum = (NttbarUp)/(NtotPassUp/theorXsect);
  downNum = (NttbarDown)/(NtotPassDown/theorXsect);  

  mupNum = (NttbarUpMat)/(NtotPassUpMat/theorXsect);
  mdownNum = (NttbarDownMat)/(NtotPassDownMat/theorXsect); 

  
  
  totXsect += xs_fit;
  
 // std::cout<<"cross section is: "<<xs_fit<<"+"<<xs_fitup-xs_fit<<"-"<<xs_fit-xs_fitdown<<std::endl;
 // std::cout<<"theor cross section is: " <<theorNum<<std::endl;

data_Vec.erase(data_Vec.begin(), data_Vec.end()); 

ttbar_Vec.erase(ttbar_Vec.begin(),ttbar_Vec.end());
wjets_Vec.erase(wjets_Vec.begin(),wjets_Vec.end());
zjets_Vec.erase(zjets_Vec.begin(),zjets_Vec.end());
qcd_Vec.erase(qcd_Vec.begin(),qcd_Vec.end());  

ttbar_err_Vec.erase(ttbar_err_Vec.begin(),ttbar_err_Vec.end());
wjets_err_Vec.erase(wjets_err_Vec.begin(),wjets_err_Vec.end());
zjets_err_Vec.erase(zjets_err_Vec.begin(),zjets_err_Vec.end());
qcd_err_Vec.erase(qcd_err_Vec.begin(),qcd_err_Vec.end());  


double width = measured->GetBinWidth(met+1);

measured->SetBinContent(met+1,xs_fit/width);
measured->SetBinError(met+1,(xs_fitup-xs_fit)/width);     

nlo->SetBinContent(met+1,nloNum/157.5/width);
powheg->SetBinContent(met+1,powhegNum/157.5/width);
theor->SetBinContent(met+1, (theorNum/157.5/width)); 

sysup->SetBinContent(met+1, (upNum/157.5/width)); 
sysdown->SetBinContent(met+1, (downNum/157.5/width)); 
mup->SetBinContent(met+1, (mupNum/157.5/width)); 
mdown->SetBinContent(met+1, (mdownNum/157.5/width));


x[met] = measured->GetBinCenter(met+1);
y[met] = xs_fit/width;
//exl[met] = measured->GetBinWidth(met+1)/2.;
//exh[met] = measured->GetBinWidth(met+1)/2.;
exl[met] = 0.;
exh[met] = 0.;
} //end of met loop

//uncertainties*****************************************************************************
double tempStat[5] = {1.806/25./157.5, 1.888/20./157.5, 2.051/25./157.5, 1.072/30./157.5, 1.215/50./157.5};

double JESup[5] = {-0.000151962 , 0.000272578 , -4.23099e-05 , -3.70002e-05 , 7.25276e-06}; 
double JESdown[5] = {-8.05871e-05 , -0.000135049 , -5.47969e-05 , -1.05896e-05 , 0.000126441};

double Qallup[5] = {0.000661542 , -0.00164854 , 0.0015185 , -0.000777495 , 4.91053e-05};
double Qalldown[5] = {0.000976746 , -0.00126681 , 9.94392e-06 , -0.000330413 , 0.000231151};

double Mallup[5] = {0.00107054 , -0.00175803 , 0.000500762 , -0.000368955 , 0.000160332};
double Malldown[5] = {0.00054994 , -0.000711093 , 0.000512741 , -0.000469302 , 4.56639e-05};

double singletD[5] = {3.79915e-06 , -1.64281e-05 , 1.61034e-05 , -1.38118e-05 , 4.97002e-06};
double singletU[5] = {-3.95387e-06 , 1.7004e-05 , -1.67224e-05 , 1.4347e-05 , -5.16378e-06 };

double lumiD[5] = {-5.15494e-06 , -2.72603e-06 , -5.41703e-06 , 2.85952e-06 , 4.54458e-06};
double lumiU[5] = {7.62411e-06 , -3.49747e-06 , 3.93426e-06 , -6.09136e-06 , -5.85902e-07};

double pdf[5] = {2.71e-05 , 3.66e-05 , 1.28e-05 , 1.33e-05 , 1.03e-05};

double METup[5] = {0.000177 , -0.000654 , 0.000105 , 1.24e-05 , 0.000117};
double METdown[5] = {2.12e-05 , 0.000176 , 0.00031 , -0.000145 , -0.000149};

double stat[5] = {0.000370122 , 0.000482173 , 0.000393533 , 0.000199431 , 0.000133263};

double up[5], down[5];

for(int bin = 0; bin < 5; bin++ ){
down[bin] = sqrt(pow(JESdown[bin],2)+pow(Qalldown[bin],2)+pow(Malldown[bin],2)+pow(singletD[bin],2)+pow(lumiD[bin],2)+pow(pdf[bin],2)+pow(METdown[bin],2)+pow(stat[bin],2)+pow(tempStat[bin],2));
up[bin] = sqrt(pow(JESup[bin],2)+pow(Qallup[bin],2)+pow(Mallup[bin],2)+pow(singletD[bin],2)+pow(lumiD[bin],2)+pow(pdf[bin],2)+pow(METup[bin],2)+pow(stat[bin],2)+pow(tempStat[bin],2));
y[bin] = y[bin]/totXsect;

}

//electron values for >=2btags
 double eleres[5] = {0.01*0.70, 0.01*1.25, 0.01*1.08, 0.01*0.56, 0.01*0.27};
 double eleyl[5] = {sqrt(pow(0.01*0.12,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.01,2)+pow(0.01*0.06,2)),sqrt(pow(0.01*0.19,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.05,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.03,2)+pow(0.01*0.01 ,2))};
 double eleyh[5] = {sqrt(pow(0.01*0.04,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.37,2)+pow(0.01*0.06,2)),sqrt(pow(0.01*0.03,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.07,2)+pow(0.01*0.02,2)),sqrt(pow(0.01*0.01,2)+pow(0.01*0.01 ,2))}; 
//electron values for geq to 4jets
//  double eleres[5] = {0.01*0.39, 0.01*0.99, 0.01*1.25, 0.01*0.73, 0.01*0.35};
//  double eleyl[5] = {sqrt(pow(0.01*0.51,2)+pow(0.01*0.07 ,2)),sqrt(pow(0.01*0.10,2)+pow(0.01*0.09,2)),sqrt(pow(0.01*0.40,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.02,2)+pow(0.01*0.39,2)),sqrt(pow(0.01*0.17,2)+pow(0.01*0.02 ,2))};
//  double eleyh[5] = {sqrt(pow(0.01*0.76,2)+pow(0.01*0.07 ,2)),sqrt(pow(0.01*0.63,2)+pow(0.01*0.09,2)),sqrt(pow(0.01*0.24,2)+pow(0.01*0.04 ,2)),sqrt(pow(0.01*0.02,2)+pow(0.01*0.12,2)),sqrt(pow(0.01*0.08,2)+pow(0.01*0.02 ,2))}; 

 //electron values******************************************************************** 
TGraphAsymmErrors* grele = new TGraphAsymmErrors(n,x,eleres,exl,exh,eleyl,eleyh);
 grele->SetMarkerStyle(20);
 grele->SetMarkerColor(4);
 grele->SetLineColor(4);
 grele->SetMarkerStyle(26);

 for(int bin = 0; bin < 5; bin++){
   ele->SetBinContent(bin+1,eleres[bin]);
   ele->SetBinError(bin+1,0.000001);
  }

 ele->SetMarkerStyle(20);
 ele->SetMarkerColor(4);
 ele->SetLineColor(4);

 //muon values*************************************************************************
 double eyl[5] = {down[0],down[1],down[2],down[3],down[4]};
 double eyh[5] = {up[0],up[1],up[2],up[3],up[4]};   
 TGraphAsymmErrors* gr = new TGraphAsymmErrors(n,x,y,exl,exh,eyl,eyh);
 gr->SetMarkerColor(1);
 gr->SetMarkerStyle(20);
 gr->SetFillStyle(3004);


  TCanvas *c= new TCanvas("c","c",10,10,800,600);
  


measured->SetMarkerStyle(20);
measured->Scale(1./ totXsect); 
//std::cout << "total measured x sect: " << totXsect << std::endl;

//cout.precision(3);
//std::cout << "temp stat: " << std::endl;
//for(int i = 0; i<5; i++){
//std::cout <<  tempStat[i] << "(" << (tempStat[i]/measured->GetBinContent(i+1))*100 << "\\%)" << " & " ;
//}

 //central previous vals no trigs
 double central[5] = {0.00609465 , 0.0145213 , 0.0116628 , 0.00549336 , 0.00213862};

//std::cout << (measured->GetBinError(1)/y[0])*100 << " , " << (measured->GetBinError(2)/y[1])*100  << " , " <<  (measured->GetBinError(3)/y[2])*100 << " , " <<   (measured->GetBinError(4)/y[3])*100 << " , " <<   (measured->GetBinError(5)/y[4])*100 << std::endl;

   //uncertaint write out for muon
// std::cout << "tot up: " << std::endl;
// for(int i = 0; i<5; i++){
// std::cout <<  up[i] << "(" << (up[i]/measured->GetBinContent(i+1))*100 << "\\%)" << " & " ;
// }
// std::cout << "tot down: " << std::endl;
// for(int i = 0; i<5; i++){
// std::cout <<  down[i] << "(" << (down[i]/measured->GetBinContent(i+1))*100 << "\\%)" << " & " ;
// }
  

//Combination!!!*********************************************************************************
//std::cout << " combined vals: " << std::endl;
//combination stuff
double val[5]; double combUp[5]; double combDown[5];
for(int i = 0; i<5; i++){
double valnum = (measured->GetBinContent(i+1)/pow(up[i],2))+(measured->GetBinContent(i+1)/pow(down[i],2))+(eleres[i]/pow(eleyh[i],2))+(eleres[i]/pow(eleyl[i],2));
double den = (1./pow(up[i],2))+(1./pow(down[i],2))+(1./pow(eleyh[i],2))+(1./pow(eleyl[i],2));
val[i] = valnum/den;

combUp[i] = sqrt(1./(1./pow(up[i],2)+pow(eleyh[i],2)));
combDown[i] = sqrt(1./(1./pow(down[i],2)+pow(eleyl[i],2)));

//std::cout << val[i]  << " , " ;
comb->SetBinContent(i+1, val[i]);
comb->SetBinError(i+1, 0.00000000001);
}

TGraphAsymmErrors* grcomb = new TGraphAsymmErrors(n,x,val,exl,exh,combDown,combUp);
 grcomb->SetMarkerStyle(20);
 grcomb->SetMarkerColor(7);
 grcomb->SetLineColor(7);
 grcomb->SetMarkerStyle(20);
 
 comb->SetMarkerStyle(20);
 comb->SetMarkerColor(7);
 comb->SetLineColor(7);

//show nominal calculated values
for(int i =1; i < 6; i++){
nominal->SetBinContent(i,central[i-1]);
 }
  
  
  //plot colors
     theor->SetLineColor(kRed+1);
     sysup->SetLineColor(kOrange+1);
     sysdown->SetLineColor(kGreen+1);
     mup->SetLineColor(kBlue+1);
     mdown->SetLineColor(kYellow+1);
     //theor->SetFillColor(kRed+1);
     nominal->SetLineColor(kBlue+1);
     
     sysup->SetLineStyle(7);
     sysdown->SetLineStyle(7);
     mup->SetLineStyle(7);
     mdown->SetLineStyle(7);

     nlo->SetLineStyle(7);
     powheg->SetLineStyle(7);
     nlo->SetLineColor(kBlue+1);
     powheg->SetLineColor(kGreen+1);

theor->SetMinimum(0);
theor->SetMaximum(0.02);    


theor->Draw();
//nominal->Draw("same");
//measured->Draw("Esame");
//ele->Draw("Esame");
gr->Draw("P");
//ele and combined
//grele->Draw("Esame");
//comb->Draw("Esame");
//grcomb->Draw("Esame"); 

nominal->Draw("same");

//systs
// sysup->Draw("same");
// sysdown->Draw("same");
// mup->Draw("same");
// mdown->Draw("same");

//gens
//nlo->Draw("same");
//powheg->Draw("same");

//too see effect of an uncertainty for input of uncertainty

//cout.precision(4);
//too see effect of an uncertainty

//std::cout  <<  " output:  " << std::endl;
for(int bin = 1; bin<=5; bin++){
  //std::cout << 100*(measured->GetBinContent(bin)-nominal->GetBinContent(bin))/measured->GetBinContent(bin)  << "\\\% & " ;
  //for table (later) 
  std::cout << (measured->GetBinContent(bin)-nominal->GetBinContent(bin)) << " , ";


}

std::cout << totXsect << std::endl;

//legend
  TLegend *tleg;
  tleg = new TLegend(0.65,0.75,0.9,0.9);
  tleg->SetTextSize(0.03);
  tleg->SetBorderSize(0);
  tleg->SetFillColor(10);


  tleg->AddEntry(gr  , "data '11'"      , "lep"); 
//  tleg->AddEntry(ele  , "e+jets (#geq 4 jets, #geq 2 btags)"      , "lpe");
//  tleg->AddEntry(ele  , "e+jets (#geq 4 jets)"      , "lpe");
//  tleg->AddEntry(comb  , "combined"      , "lpe");

  tleg->AddEntry(theor    , "t#bar{t} (MADGRAPH)"  , "l");
//  tleg->AddEntry(nlo    , "t#bar{t} (MC@NLO)"  , "l");
//  tleg->AddEntry(powheg    , "t#bar{t} (POWHEG)"  , "l");
  
  //for sys 
//   tleg->AddEntry(sysup    , "t#bar{t} Q^{2} up "  , "l"); 
//   tleg->AddEntry(sysdown    , "t#bar{t} Q^{2} down "  , "l"); 
//   tleg->AddEntry(mup    , "t#bar{t} matching up "  , "l"); 
//   tleg->AddEntry(mdown    , "t#bar{t} matching down "  , "l");
//tleg->AddEntry(nominal    , "no trigger corrections"  , "l");

  tleg->Draw("same");



//titles
theor->GetYaxis()->SetTitle("#frac{1}{#sigma} #frac{#partial #sigma}{#partial MET} [GeV^{-1}]");theor->GetYaxis()->SetTitleSize(0.05);
theor->GetXaxis()->SetTitle("MET [GeV]"); theor->GetXaxis()->SetTitleSize(0.05);

  TText* textPrelim = doPrelim(lumi,0.16,0.96); 
  textPrelim->Draw();

//delete c;
} //end sys loop

//c->SetLogy(1);

//c->SaveAs("240712plots/eComb.png");
//c->SaveAs("240712plots/eComb.pdf");

return 0;

}

//-------------------------------------------------------------------------

//  function to read in the data from a histogram
void getDataFromHis(TFile* inputFile, TString& jet_num, int& nxbins){

  TH1F *h_data = (TH1F*) inputFile->Get("metEta_h_"+jet_num+"data");
Ntotal=0;

//    TFile* output = TFile::Open("muData.root","UPDATE");
//   // his_mc_array->Scale(10909.);
//   h_data->SetName("muData");
//   h_data->Write();



  nbins = h_data->GetNbinsX();
  
  xmax = xmin + nxbins*(h_data->GetBinWidth(1));
  
 // cout<<"num of bins: "<<nbins<<" xmax: "<<xmax<<endl;

  for(int ibin=0; ibin<nxbins; ibin++){

    int nn = h_data->GetBinContent(ibin+1);

    data_Vec.push_back(nn);

    Ntotal += nn;
   
  }

  // cout <<" \n Total number of events before the fit" << endl;
  //cout <<"  Data: \t "<<Ntotal<<endl;

}



void getTemFromHis(TFile* inputFile, TString& templ, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err){

  TH1F* his_mc_array =  (TH1F*) inputFile->Get("metEta_h_"+jet_num+templ);

  //std::cout<<"test: "<<his_mc_array->Integral()<<std::endl;

  his_mc_array->Scale(1./his_mc_array->Integral());
  //std::cout<<"test: "<<nxbins<<std::endl;
  //std::cout << templ << ":  {" << std::endl;
  
  for(int ibin=0; ibin<nxbins; ibin++){

    vect.push_back(his_mc_array->GetBinContent(ibin+1));
    vect_err.push_back(his_mc_array->GetBinError(ibin+1));

    //std::cout << "{" << his_mc_array->GetBinContent(ibin+1) << "," << his_mc_array->GetBinError(ibin+1) << "}, ";

  }
  //std::cout<< "}" << std::endl;

}


void getSignalFromHis(TFile* inputFile, TString& jet_num, TString& syst,int& nxbins, vector<double>& vect, vector<double>& vect_err){


  TH1F* his_mc_array = (TH1F*) inputFile->Get("metEta_h_"+jet_num+"tt"+syst);  
  TH1F* his_mc_stop = (TH1F*) inputFile->Get("metEta_h_"+jet_num+"SinglT");
  his_mc_array->Add(his_mc_stop);
  
  his_mc_array->Scale(1./his_mc_array->Integral());




//   TFile* output = TFile::Open("signal.root","UPDATE");
//   // his_mc_array->Scale(10909.);
//   his_mc_array->SetName("SignalTemplate");
//   his_mc_array->Write();


  for(int ibin=0; ibin<nxbins; ibin++){

    vect.push_back(his_mc_array->GetBinContent(ibin+1));
    vect_err.push_back(his_mc_array->GetBinError(ibin+1));

  }


}
//-------------------------------------------------------------------------

// fcn passes back f = - 2*ln(L), the function to be minimized. not sure if N_{single top} is obtained from fitting
void fcn(int& npar, double* deriv, double& f, double par[], int flag){

  double lnL = 0.0;


  for (int i=0; i<nbins; i++){

    //data_i is the observed number of events in each bin
    int data_i = data_Vec[i];
    //xi is the expected number of events in each bin
    double xi = par[0]*ttbar_Vec[i] + par[1]*wjets_Vec[i] + par[2]*zjets_Vec[i] + par[3]*qcd_Vec[i];


    if(data_i !=0 && xi != 0){
      lnL += log(TMath::Poisson(data_i, xi));
    }
    
   // cout << "data:" << data_i << "  xi: " << xi <<   " lnL:  " << log(TMath::Poisson(data_i, xi)) << endl;
    
  }

  //W+jets, Z+jets constraints
  f = -2.0 * lnL;
  

  double nwjets = Nwjets;
  double nwjets_err = nwjets*0.3;
  //double nwjets_err = nwjets*0.02;
   
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

  //cout << "qcd:" <<  NQCD << "  ,par3: " << par[3] << endl;

  //double r = nwjets/nzjets;
  //double r_err = r*0.01;

  //f += (par[1]/par[2]-r)*(par[1]/par[2]-r)/r_err/r_err;
  //Wjets constrain
//   f += (par[1]-nwjets)*(par[1]-nwjets)/nwjets_err/nwjets_err;
//   //Zjets constrain
//   f += (par[2]-nzjets)*(par[2]-nzjets)/nzjets_err/nzjets_err;
//   //QCD constrain
//   f += (par[3]-nqcd)*(par[3]-nqcd)/nqcd_err/nqcd_err;

  //Ratio Constrain
  //f += ( (par[1]/par[2] - nwjets/nzjets) / (0.3 *nwjets/nzjets) )  * ( (par[1]/par[2] - nwjets/nzjets) / (0.3*nwjets/nzjets) ) * ( (par[1]/par[2] - nwjets/nzjets) / (0.3*nwjets/nzjets) ) * ( (par[1]/par[2] - nwjets/nzjets) / (0.3*nwjets/nzjets) ); //chi4?
  

  //ratio constraints
   f += ( (par[2]/par[1] - nzjets/nwjets) / (0.05 *nzjets/nwjets) )  * ( (par[2]/par[1] - nzjets/nwjets) / (0.05*nzjets/nwjets) ); //swap


   f += ((par[3]-nqcd)*(par[3]-nqcd))/nqcd_err/nqcd_err;


}                         

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
TText* doPrelim(float luminosity, float x, float y)
{
  std::ostringstream stream;
  stream  <<"#mu, #geq 4 jets, #geq 2 b-tags                     CMS Preliminary, L = 5.0 fb^{-1} @ #sqrt{s} = 7 TeV";   

  TLatex* text = new TLatex(x, y, stream.str().c_str());
  //text->SetTextAlign(33);  //left
  //text->SetTextAlign(22);  //center
  //text->SetTextAlign(11);  //right
text->SetNDC(true);
text->SetTextFont(42);
text->SetTextSize(0.035);  // for thesis

  return text;
}
