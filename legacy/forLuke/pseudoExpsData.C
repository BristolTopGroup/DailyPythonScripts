/*A C++ program to use of ROOT class TMinuit for function minimization.It shows a Maximum Likelihood fit for the mean of a binned Poisson pdf in which TMinuit minimizes
 - 2*log(L). fcn passes back f = -2*ln L by reference; this is the function to minimize.

  The factor of -2 allows MINUIT to get the errors using the same recipe as for least squares, i.e., go up from the minimum by 1.

  TMinuit does not allow fcn to be a member function, and the function arguments are fixed, so the one of the only ways to bring the data   into fcn is to declare a poi
nter to the data (xVecPtr) as global.

  For more info on TMinuit see root.cern.ch/root/html/TMinuit.html .

  Yao Weng 11/30/2009

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

#include "tdrstyle.C"
#include "TRandom3.h"


using namespace std;
// Declare pointer to data as global (not elegant but TMinuit needs this).
vector<double> data_Vec; //input data

vector<double> sig_Vec; //ttbar+single top template from mc
vector<double> ttbar_Vec; //ttbar+single top template from mc
vector<double> SinglT_Vec; //ttbar+single top template from mc
vector<double> wjets_Vec; //wjest template from mc
vector<double> zjets_Vec; //zjets template from mc
vector<double> qcd_Vec;   //qcd template from data drive method

vector<double> sig_err_Vec;
vector<double> ttbar_err_Vec; //ttbar+single top template from mc
vector<double> SinglT_err_Vec; //ttbar+single top template from mc
vector<double> wjets_err_Vec; //wjest template from data driven method
vector<double> zjets_err_Vec; //zjets template from data driven method
vector<double> qcd_err_Vec;   //qcd template from data drive method

vector<double> sig_Vec_Exp; //ttbar+single top template from mc
vector<double> ttbar_Vec_Exp; //ttbar+single top template from mc
vector<double> SinglT_Vec_Exp; //ttbar+single top template from mc
vector<double> wjets_Vec_Exp; //wjest template from data driven method
vector<double> zjets_Vec_Exp; //zjets template from data driven method
vector<double> qcd_Vec_Exp;   //qcd template from data drive method

int Ntotal; //define as global, got in getDataFromHis function
int nbins; //define as global, also got in getDataFromHis function, and it is been used in getTemFromHis function
double total;
  
//double xbins[13] = {0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4};


double xmin = 0;
double xmax; //calculate in getDataFromHis function

void fcn(int& npar, double* deriv, double& f, double par[], int flag);
void getDataFromHis(TFile* inputFile, TString& jet_num, int& nxbins);
void getSignalFromHis(TFile* inputFile, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err);
void getTemFromHis(TFile* inputFile, TString& templ, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err);

//added for pseudo exps
void makePseudoData(int metBin, TString sample, vector<double>& vect_exp, vector<double>& vect, vector<double>& vect_err, double Nin, double jes, double q2);
void allPseudoData(vector<double>& vect_data, vector<double>& vect_tt,vector<double>& vect_singl, vector<double>& vect_w, vector<double>& vect_z,vector<double>& vect_qcd);

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

  double NQCD_Exp;
//systematic stuff
  double sigJES[5] = {0.0931625,0.0913714,0.0878864,0.0907158,0.0727412};
  double wJES[5] = { 0.177986,0.182469,0.164872,0.145936,0.107857};
  double zJES[5] = { 0.191011,0.165981,0.143306,0.179691,0.104074};
  double qcdJES[5] = { 0.,0.,0.,0.,0.};
  
  double sigQ2[5] = {-0.0555018, -0.0561554, -0.0684114, -0.06333, -0.128015};
  //double wQ2A[5] = {0.0409279, 0.0323349,0.0434689, 0.023042, 0.0134098};
  double wQ2A[5] = {0.0, 0.0,0.0, 0.0, 0.0};
  double wQ2B[5] = {-1.29644, -1.25751, -1.27239, -1.19836, -1.44405};
  //double zQ2A[5] = {-0.0109077, -0.00468542, 0.0150196, 0.00462842, 0.00129225};
  double zQ2A[5] = {-0.0, -0.0, 0.0, 0.0, 0.0};
  double zQ2B[5] = {-1.00334, -1.04471, -1.16302, -1.0853, -0.636802};


//-------------------------------------------------------------------------
int pseudoExpsData() {

int nExperiments = 5000;

double theorXsect = 157.5;

  // Choose the jet multiplicity
  TString jet_num = "2b_";
  TString jet_num_temp = "ge2j";
  
  TString dir = "/home/mepgphs/project/CMSSW_4_2_5/CMGTools/CMSSW_4_2_5/src/CMGTools/TtbarMuonJets/metPlots1907/output/";
    
  TString number = "2";
  int metBin = 2;
  
  TFile* f_central = TFile::Open(dir+"PFhistosForFitting_met"+number+"_central.root");
  TFile* f_templates  = TFile::Open(dir+"QCDetaData.root");
  TFile* f_all = TFile::Open(dir+"PFhistosForFitting_metall_central.root");	

  TFile* f_sys = TFile::Open(dir+"scaledown_met"+number+"_central.root"); 

  TH1D* signal = (TH1D*) f_central->Get("metEta_h_"+jet_num+"signal");
  TH1D* wjets = (TH1D*) f_central->Get("metEta_h_"+jet_num+"wjets");
  TH1D* zjets = (TH1D*) f_central->Get("metEta_h_"+jet_num+"zjets");
  TH1D* QCD = (TH1D*) f_central->Get("metEta_h_"+jet_num+"QCD");
  TH1D* SinglT = (TH1D*) f_central->Get("metEta_h_"+jet_num+"SinglT");
  TH1D* ttbar = (TH1D*) f_central->Get("metEta_h_"+jet_num+"ttbar");
  TH1D* tt_Z = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_Z");
  TH1D* tt_W = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_W");
  TH1D* DATA = (TH1D*) f_central->Get("metEta_h_"+jet_num+"data");
  TH1D* QCDeta = (TH1D*) f_templates->Get("metEta_h_"+jet_num_temp);
  TH1D* ttbarAll = (TH1D*) f_all->Get("metEta_h_"+jet_num+"ttbar");
     
  TH1D* signal_sys = (TH1D*) f_sys->Get("metEta_h_"+jet_num+"signal");
  
  int rebinF = 8;
  signal_sys->Rebin(rebinF);
  
  signal->Rebin(rebinF);
  wjets->Rebin(rebinF);
  zjets->Rebin(rebinF);
  QCD->Rebin(rebinF);
  SinglT->Rebin(rebinF);
  ttbar->Rebin(rebinF);
  tt_Z->Rebin(rebinF);
  tt_W->Rebin(rebinF);
  DATA->Rebin(rebinF);
  QCDeta->Rebin(rebinF/2);
  
  cout << "input params: " << endl;
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

 cout  << "signal: " << Nsignal << endl;
 cout  << "wjets: " << Nwjets << endl;
 cout  << "zjets: " << Nzjets << endl;
 cout  << "qcd: "   << NQCD << endl;
  
//  cout << Nttbar << " & " << Nwjets << " & " << Nzjets << " & " << NQCD << " & " <<  NSinglT << " & " << Ntt_Z << " & "  << Ntt_W << " & " << tot << " & " << Ndata <<endl;


  TString ttstring = "ttbar";
  TString singlstring = "SinglT";
  TString wstring = "wjets";
  TString zstring = "zjets";
  TString qcdstring = "";

  // Read in the data and templates.
  getDataFromHis(f_central, jet_num, nbins); // Get data histrogram from central selection
  getSignalFromHis(f_central, jet_num, nbins, sig_Vec, sig_err_Vec);// Get ttbar, single-top histrograms form MC with entral selection 


  getTemFromHis(f_central, ttstring, jet_num, nbins, ttbar_Vec, ttbar_err_Vec);
  getTemFromHis(f_central, singlstring, jet_num, nbins, SinglT_Vec, SinglT_err_Vec);
  
  getTemFromHis(f_central, wstring, jet_num, nbins, wjets_Vec, wjets_err_Vec);                 
  getTemFromHis(f_central, zstring, jet_num, nbins, zjets_Vec, zjets_err_Vec);
  getTemFromHis(f_templates, qcdstring, jet_num_temp, nbins, qcd_Vec, qcd_err_Vec);

  f_central->Close();
  f_templates->Close(); 
  
  TH1D* his_beta_fit = new TH1D("his_beta_fit", "", 1500, -0.5, 2.5); //used to plot beta_fit distribution
  TH1F* his_pull = new TH1F("his_pull", "", 1000, -10., 10.); //used to plot beta_fit distribution
  TH1F* his_result = new TH1F("his_result", "", 1000, 0. , 80.); //used to plot beta_fit distribution

int iexp =0;
while(iexp < nExperiments) {  // loop doing experiments
  //data_Vec.erase(data_Vec.begin(),data_Vec.end());
  total = 0;
  
  //std::cout << "sig before: " << Nsignal << std::endl;
  TRandom3* rng = new TRandom3(0);
  //JES parameterisation
  double delta_JES=1000;
  double JESwidth = 1.0;
  while(fabs(delta_JES)>2.*JESwidth)
    delta_JES=rng->Gaus(0.,JESwidth);
  delta_JES = 0.;
  
  //Q2 for V+jets
  double delta_qscale = 1000.;
  double Q2width  = TMath::Log(2.);  
while((TMath::Exp((wQ2B[metBin-1]-zQ2B[metBin-1])*delta_qscale))<0.75||TMath::Exp((wQ2B[metBin-1]-zQ2B[metBin-1])*delta_qscale)>1.25)
     delta_qscale = rng->Gaus(0.,Q2width);
   delta_qscale = 0.;
     
     //Q2 for tt+jets
  double delta_qscale_tt = 1000.;  
while((delta_qscale_tt)>2.*Q2width)
     delta_qscale_tt = rng->Gaus(0.,Q2width); 
    delta_qscale_tt = 0.;
  
    //  makePseudoData(metBin,"ttbar", ttbar_Vec_Exp, ttbar_Vec, ttbar_err_Vec,Nttbar, delta_JES, delta_qscale_tt );
    //  makePseudoData(metBin,"SinglT", SinglT_Vec_Exp, SinglT_Vec, SinglT_err_Vec,NSinglT, delta_JES, delta_qscale_tt ); 
    //  makePseudoData(metBin,"wjets", wjets_Vec_Exp, wjets_Vec, wjets_err_Vec,Nwjets, delta_JES, delta_qscale);
    //  makePseudoData(metBin,"zjets", zjets_Vec_Exp, zjets_Vec, zjets_err_Vec,Nzjets, delta_JES, delta_qscale);
    //  makePseudoData(metBin,"qcd", qcd_Vec_Exp, qcd_Vec, qcd_err_Vec,NQCD, NQCD_Exp, NQCD_Exp);
    
  //allPseudoData(data_Vec, ttbar_Vec_Exp, SinglT_Vec_Exp, wjets_Vec_Exp, zjets_Vec_Exp, qcd_Vec_Exp);

sig_Vec_Exp.erase(sig_Vec_Exp.begin(),sig_Vec_Exp.end());
wjets_Vec_Exp.erase(wjets_Vec_Exp.begin(),wjets_Vec_Exp.end());
zjets_Vec_Exp.erase(zjets_Vec_Exp.begin(),zjets_Vec_Exp.end());
qcd_Vec_Exp.erase(qcd_Vec_Exp.begin(),qcd_Vec_Exp.end());

TRandom3* rand = new TRandom3(0);
 
 for(int i = 0; i < nbins; i++){    
    sig_Vec_Exp.push_back(rand->Gaus(sig_Vec[i], sig_err_Vec[i]));

    wjets_Vec_Exp.push_back(rand->Gaus(wjets_Vec[i], wjets_err_Vec[i]));

    zjets_Vec_Exp.push_back(rand->Gaus(zjets_Vec[i], zjets_err_Vec[i]));

    qcd_Vec_Exp.push_back(rand->Gaus(qcd_Vec[i], qcd_err_Vec[i]));
    
    //std::cout << sig_Vec_Exp[i] << " , " ;
    
  }
  
  // Initialize minuit, set initial values etc. of parameters.
  const int npar = 4;              // the number of parameters
  TMinuit minuit(npar);
  minuit.SetFCN(fcn);
  
  minuit.SetPrintLevel(-1);
  minuit.SetErrorDef(1.);
  
  int ierflg = 0;
  string parName[npar] = {"ttbar+single-top", "wjets", "zjets", "qcd"}; //background parameters
  double par[npar] = {Nsignal, Nwjets, Nzjets, NQCD};               //using the MC estimation as the start values 1fb

  //cout << "total data events: " << Ntotal << endl;


  for(int i=0; i<npar; i++){
    minuit.mnparm(i, parName[i], par[i], 10., -1.e6, 1.e6, ierflg);
    //minuit.mnparm(i, parName[i], par[i], 10., 0, Ntotal, ierflg);

  }
    
  //the following is copied from Fabian's fitting code to improve minimum, but you can comment it, it won't affect the fitting results.
  // 1 standard
  // 2 try to improve minimum (slower)
  double arglist[10];
  arglist[0]=2;
  minuit.mnexcm("SET STR",arglist,1,ierflg);
  minuit.Migrad();
  
  double outpar[npar], err[npar];
    
  for (int i=0; i<npar; i++){
    minuit.GetParameter(i,outpar[i],err[i]);
  }


//   //print out the results
//   cout <<" \n Total number of events after the fit" << endl;
//   cout<<"   & ttbar+single top & w+jets & z+jets & qcd "<<endl;
//   cout <<  " & " << Nsignal <<  " & " << Nwjets << " & " <<  Nzjets << " & " <<  NQCD  <<endl;
//   cout<< " & "<<outpar[0]<<"+-"<<err[0]<<" & "<<outpar[1]<<"+-"<<err[1]<<" & "<<outpar[2]<<"+-"<<err[2]<<" & "<<outpar[3]<<"+-"<<err[3]<<endl;
   
  double xs_fit = (outpar[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  double xs_fitup = (outpar[0]+err[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  double xs_fitdown = (outpar[0]-err[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb


  if(iexp%1000==0) {
  std::cout<<"cross section is: "<<xs_fit<<"+"<<xs_fitup-xs_fit<<"-"<<xs_fit-xs_fitdown<<std::endl;
  }

 //fill histograms
 double beta = ((xs_fit*(NtotPass/Nttbar))/theorXsect);

 double pull = (xs_fit-theorXsect*(Nttbar/NtotPass))/(xs_fitup-xs_fit);

 if(xs_fit!= (Nttbar)/(NtotPass/theorXsect)){

 iexp++;
 
 his_beta_fit->Fill(beta);
 his_pull->Fill(pull);
 his_result->Fill(xs_fit);
 }

}

//draw histograms

  TCanvas* cBetaFit = new TCanvas("cBetaFit", "cBetaFit", 10,10,800,600);
  cBetaFit->cd();
  //his_beta_fit->Fit("gaus","L");
  //TF1* fitFunction = his_beta_fit->GetFunction("gaus");
  //fitFunction->SetLineWidth(2);
  his_beta_fit->Scale(1./his_beta_fit->Integral());
  his_beta_fit->GetXaxis()->SetTitle("#sigma_{fit}/#sigma_{theory}");
  //his_beta_fit->SetAxisRange(1.,1.2) ;
  his_beta_fit->Draw();
  
  TCanvas* cPull = new TCanvas("cPull", "cPull", 10,10,800,600);
  cPull->cd();
  //his_pull->Fit("gaus","L");
  //TF1* fitFunction2 = his_pull->GetFunction("gaus");
  //fitFunction2->SetLineWidth(2);
  his_pull->Scale(1./his_pull->Integral());
  his_pull->GetXaxis()->SetTitle("#sigma_{fit}-#sigma_{theory}/#Delta#sigma");
  his_pull->Draw();
  //his_result->SetAxisRange(0.75*his_result->GetMaximum(), 1.25*his_result->GetMaximum() ;

  TCanvas* cRes = new TCanvas("cRes", "cRes", 10,10,800,600);
  cRes->cd();
  //his_pull->Fit("gaus","L");
  //TF1* fitFunction2 = his_pull->GetFunction("gaus");
  //fitFunction2->SetLineWidth(2);
  his_result->Scale(1./his_result->Integral());
  his_result->GetXaxis()->SetTitle("#sigma_{fit} (pb)");
  his_result->Draw();
  his_result->SetAxisRange(0.5*his_result->GetMean(), 1.5*his_result->GetMean()) ;
 
 
  cBetaFit->SaveAs("notePlots/xbeta_stat"+number+".pdf"); 
  cBetaFit->SaveAs("notePlots/xbeta_stat"+number+".png");
  cBetaFit->SaveAs("notePlots/xbeta_stat"+number+".eps"); 

  cPull->SaveAs("notePlots/xpull_stat"+number+".pdf");
  cPull->SaveAs("notePlots/xpull_stat"+number+".eps");
  cPull->SaveAs("notePlots/xpull_stat"+number+".png");
 
  cRes->SaveAs("notePlots/xres_stat"+number+".pdf");
  cRes->SaveAs("notePlots/xres_stat"+number+".eps");
  cRes->SaveAs("notePlots/xres_stat"+number+".png");
 
 
  // compute the results, you can either use the following code, or use a Guassian to fit his_beta_fit, as nexp is very large here, then  his_beta_fit is normally distributed !!!!! but we will find the resutls are the same :D

  double sum=0;
  double m2s=-100000.;
  double m1s=-100000.;
  double cent=-100000.;
  double p1s=-100000.;
  double p2s=-100000.;

  for(int i=1; i<his_beta_fit->GetNbinsX(); ++i) {
    
    sum += his_beta_fit->GetBinContent(i);
    if(sum > 0.023) { // hit the -2sigam
      if(m2s < -10000.) m2s=his_beta_fit->GetBinCenter(i);
      if(sum > 0.159) {
	if(m1s < -10000.) m1s=his_beta_fit->GetBinCenter(i);
	if(sum > 0.5) {
	  if(cent < -10000.) cent=his_beta_fit->GetBinCenter(i);
	  if(sum > 0.841) {
	    if(p1s < -10000.) p1s=his_beta_fit->GetBinCenter(i);
	    if(sum > 0.977) {
	      if(p2s < -10000.) p2s=his_beta_fit->GetBinCenter(i);
	    }
	  }
	}
      }
    }
  }

  std::cout<<" FINAL RESULT:"<<std::endl;
  std::cout<<"   beta_fit(-2s) = "<<m2s<<std::endl;
  std::cout<<"   beta_fit(-1s) = "<<m1s<<std::endl;
  std::cout<<"        beta_fit = "<<cent<<std::endl;
  std::cout<<"   beta_fit(+1s) = "<<p1s<<std::endl;
  std::cout<<"   beta_fit(+2s) = "<<p2s<<std::endl;
  
  
  std::cout <<  cent*(Nttbar)/(NtotPass/theorXsect)-m1s*(Nttbar)/(NtotPass/theorXsect) << " & " << p1s*(Nttbar)/(NtotPass/theorXsect)-cent*(Nttbar)/(NtotPass/theorXsect) << std::endl;
  return 0;
}

//-------------------------------------------------------------------------

//  function to read in the data from a histogram
void getDataFromHis(TFile* inputFile, TString& jet_num, int& nxbins){

  
  TH1F *h_data = (TH1F*) inputFile->Get("metEta_h_"+jet_num+"data");


//    TFile* output = TFile::Open("muData.root","UPDATE");
//   // his_mc_array->Scale(10909.);
//   h_data->SetName("muData");
//   h_data->Write();



  nbins = h_data->GetNbinsX();
  xmax = xmin + nxbins*(h_data->GetBinWidth(1));
  
  //cout<<"num of bins: "<<nxbins<<" xmax: "<<xmax<<endl;
  //std::cout << ":  {" << std::endl;
  for(int ibin=0; ibin<nxbins; ibin++){
   //std::cout << "{" << h_data->GetBinContent(ibin+1) << "," << h_data->GetBinError(ibin+1) << "}, ";
    int nn = h_data->GetBinContent(ibin+1);

    data_Vec.push_back(nn);

    Ntotal += nn;
   
  }
 //std::cout<< "}" << std::endl;
  // cout <<" \n Total number of events before the fit" << endl;
  //cout <<"  Data: \t "<<Ntotal<<endl;

}



void getTemFromHis(TFile* inputFile, TString& templ, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err){

  TH1F* his_mc_array =  (TH1F*) inputFile->Get("metEta_h_"+jet_num+templ);


  nbins = his_mc_array->GetNbinsX();
  
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


void getSignalFromHis(TFile* inputFile, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err){



  TH1F* his_mc_array = (TH1F*) inputFile->Get("metEta_h_"+jet_num+"signal");
  his_mc_array->Scale(1./his_mc_array->Integral());




//   TFile* output = TFile::Open("signal.root","UPDATE");
//   // his_mc_array->Scale(10909.);
//   his_mc_array->SetName("SignalTemplate");
//   his_mc_array->Write();

 //std::cout << ":  {" << std::endl;
  for(int ibin=0; ibin<nxbins; ibin++){
 	
	//std::cout << "{" << his_mc_array->GetBinContent(ibin+1) << "," << his_mc_array->GetBinError(ibin+1) << "}, ";
    
    vect.push_back(his_mc_array->GetBinContent(ibin+1));
    vect_err.push_back(his_mc_array->GetBinError(ibin+1));

  }  
  //std::cout<< "}" << std::endl;
}

//-------------------------------------------------------------------------
//pseudodata
void makePseudoData(int metBin, TString sample,vector<double>& vect_exp, vector<double>& vect, vector<double>& vect_err,double Nin, double jes, double q2){
TRandom3* rng = new TRandom3(0);

  vect_exp.erase(vect_exp.begin(),vect_exp.end());



double errJES =0.;
double delta_Q2 = 0.; 
// turn off single t and lumi error here
double errSinglT = 1.;
//errSinglT = 1.+rng->Gaus(0., 0.3);
double errLumi = 1.;
//errLumi = 1.+rng->Gaus(0., 0.022);

if(sample == "ttbar" ||sample == "SinglT" ){ 
errJES=sigJES[metBin-1];
delta_Q2 =  sigQ2[metBin-1]*q2 + 1.0;

}

if(sample == "wjets"){ 
errJES=wJES[metBin-1];
delta_Q2 =  TMath::Exp(wQ2A[metBin-1]+wQ2B[metBin-1]*q2);
}


if(sample == "zjets"){ 
errJES=zJES[metBin-1];
delta_Q2 =  TMath::Exp(zQ2A[metBin-1]+zQ2B[metBin-1]*q2);

}
 
   
  double delta_JES = errJES*jes + 1.0;
  
  
  //std::cout << sample << " : "; 

//readin vector
  for(int i=0; i<nbins; i++){

    vect_exp.push_back(vect[i]);
    
    //std::cout << vect_exp[i] << " ," ;
  }
   
  //std::cout << "pre: " << Nexp << std::endl;

  double tot_pois = 0; 
  for(int i=0; i<nbins; i++){
	
	if(sample=="SinglT"){
	vect_exp[i] = vect_exp[i]*errSinglT;
	}
	
	if(sample=="qcd"){
	//turn off/on qcd here
	double thisval = rng->Gaus(vect_exp[i], vect_err[i]);
	vect_exp[i] = thisval;
	if(thisval > 0.)
	vect_exp[i] = vect_exp[i]*Nin;
	else
	vect_exp[i] = 0.000;
	}else{
	vect_exp[i] = vect_exp[i]*Nin*delta_JES*delta_Q2;
	}
	
	//fluctuate around stat error comment out line below to turn off
	//vect_exp[i] = rng->Poisson(vect_exp[i]);
	//std::cout << vect_exp[i] << " ," ; 	
	vect_exp[i] = vect_exp[i]*errLumi;
	
	tot_pois += vect_exp[i];
	}
//std::cout << " " << std::endl;
//std::cout << "apres: " << tot_pois << std::endl;
  

}

void allPseudoData(vector<double>& vect_data, vector<double>& vect_tt, vector<double>& vect_singl, vector<double>& vect_w,vector<double>& vect_z,vector<double>& vect_qcd){
//std::cout << "data: " << std::endl;
  for(int i=0; i<nbins; i++){
	vect_data.push_back(vect_tt[i]+vect_singl[i]+vect_w[i]+vect_z[i]+vect_qcd[i]);
	//std::cout << vect_data[i] << " ,  ";
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
    //double xi = par[0]*sig_Vec[i] + par[1]*wjets_Vec[i] + par[2]*zjets_Vec[i] + par[3]*qcd_Vec_Exp[i];
    double xi = par[0]*sig_Vec_Exp[i] + par[1]*wjets_Vec_Exp[i] + par[2]*zjets_Vec_Exp[i] + par[3]*qcd_Vec[i];
    

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
  stream  <<"CMS Preliminary, L = " <<  luminosity << " pb^{-1}";  //stream  <<"CMS Preliminary, L = " <<  lumi << " pb^{-1} at #sqrt{7} TeV";
  TLatex* text = new TLatex(x, y, stream.str().c_str());

  text->SetNDC(true);
  text->SetTextFont(62);
  text->SetTextSize(0.04);
  return text;
}
