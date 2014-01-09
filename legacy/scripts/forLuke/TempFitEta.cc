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
void getSignalFromHis(TFile* inputFile, TString& jet_num, int& nxbins, vector<double>& vect, vector<double>& vect_err);
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
//-------------------------------------------------------------------------
int TempFitEta() {


double theorXsect = 157.5;

  // Choose the jet multiplicity
  TString jet_num = "2b_";
  TString jet_num_temp = "ge2j";
  //choose what to use
  TString templ = "_central";
  TString num = "3";
  
  
  //trig
  TFile* f_central = TFile::Open("PFhistosForFitting_met"+num+templ+".root");
  //no trig  
  TFile* f_centraln = TFile::Open("../../metPlots1907/output/PFhistosForFitting_met"+num+templ+".root");
  
  TFile* f_templates  = TFile::Open("QCDetaData.root");
  TFile* f_all = TFile::Open("PFhistosForFitting_metall"+templ+".root");
  
  
  TH1D* signaln = (TH1D*) f_centraln->Get("metEta_h_"+jet_num+"signal");
  TH1D* zjetsn = (TH1D*) f_centraln->Get("metEta_h_"+jet_num+"zjets");
  
  
  TH1D* signal = (TH1D*) f_central->Get("metEta_h_"+jet_num+"signal");
  TH1D* wjets = (TH1D*) f_central->Get("metEta_h_"+jet_num+"wjets");
  TH1D* zjets = (TH1D*) f_central->Get("metEta_h_"+jet_num+"zjets");
  TH1D* QCD = (TH1D*) f_central->Get("metEta_h_"+jet_num+"QCD");
  TH1D* SinglT = (TH1D*) f_central->Get("metEta_h_"+jet_num+"SinglT");
  TH1D* ttbar = (TH1D*) f_central->Get("metEta_h_"+jet_num+"ttbar");
  TH1D* tt_Z = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_Z");
  TH1D* tt_W = (TH1D*) f_central->Get("metEta_h_"+jet_num+"tt_W");
  TH1D* DATA = (TH1D*) f_central->Get("metEta_h_"+jet_num+"data");

  TH1D* QCData = (TH1D*) f_templates->Get("metEta_h_"+jet_num_temp);
  TH1D* ttbarAll = (TH1D*) f_all->Get("metEta_h_"+jet_num+"ttbar");
  
  int rebinF = 8;
  
  signaln->Rebin(rebinF);
  zjetsn->Rebin(rebinF);
  
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
  
  
  cout << "input params: " << endl;
  Nsignal = signal->Integral();
  Nwjets = wjets->Integral();
  Nzjets = zjets->Integral();
  NQCD = QCD->Integral();
  NSinglT = SinglT->Integral();
  Nttbar = ttbar->Integral();
double Ntt_Z =tt_Z->Integral();
double Ntt_W =tt_W->Integral();
double tot =   Nttbar+NSinglT+NQCD+Nzjets+Nwjets+Ntt_Z+Ntt_W;
double Ndata = DATA->Integral();
  NtotPass = ttbarAll->Integral();
  
  
  TString wstring = "wjets";
  TString zstring = "zjets";
  TString qcdstring = "";

  // Read in the data and templates.
  getDataFromHis(f_central, jet_num, nbins); // Get data histrogram form central selection
  getSignalFromHis(f_central, jet_num, nbins, ttbar_Vec, ttbar_err_Vec);// Get ttbar, single-top histrograms form MC with entral selection 

  //  TString wstring = "Wtemplate";
  //  TString zstring = "DYtemplate";

  getTemFromHis(f_central, wstring, jet_num, nbins, wjets_Vec, wjets_err_Vec);                 
  getTemFromHis(f_central, zstring, jet_num, nbins, zjets_Vec, zjets_err_Vec);
  getTemFromHis(f_templates, qcdstring, jet_num_temp, nbins, qcd_Vec, qcd_err_Vec);

  f_central->Close();
  f_templates->Close(); 
//   f_signal->Close(); 
//   f_wjets->Close(); 
//   f_zjets->Close(); 
//   f_qcd->Close(); 
 
  // Initialize minuit, set initial values etc. of parameters.
  const int npar = 4;              // the number of parameters
  TMinuit minuit(npar);
  minuit.SetFCN(fcn);
  
  //minuit.SetPrintLevel(1);
  minuit.SetPrintLevel(-1);
  minuit.SetErrorDef(1.);
  
  int ierflg = 0;
  string parName[npar] = {"ttbar+single-top", "wjets", "zjets", "qcd"}; //background parameters
  double par[npar] = {Nsignal, Nwjets, Nzjets, NQCD};               //using the MC estimation as the start values 1fb
  //double par[npar] = {4667.33 , 3790.39 , 1376.35 , 194.751};
  cout << "total data events: " << Ntotal << endl;


  for(int i=0; i<npar; i++){

    //minuit.mnparm(i, parName[i], par[i],10., -1.e6, 1.e6, ierflg);
    minuit.mnparm(i, parName[i], par[i], 10., 0, Ntotal, ierflg);

    //cout << "ttbar: " <<  par[0] << endl;
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



  
  // Plot the result. 
  setTDRStyle();
  
  TH1F* result = new TH1F("result", "", nbins, xmin, xmax);
  TH1F* data = new TH1F("data", "", nbins, xmin, xmax);

  //ttbar, stop, wjets, zjets and qcd contribution 
  TH1F* ttbar_Con = new TH1F("ttbar_Con", "", nbins, xmin, xmax);
  TH1F* wjets_Con = new TH1F("wjets_Con", "", nbins, xmin, xmax);
  TH1F* zjets_Con = new TH1F("zjets_Con", "", nbins, xmin, xmax);
  TH1F* qcd_Con   = new TH1F("qcd_Con"  , "", nbins, xmin, xmax);
  

  //ttbar, stop, wjets, zjets and qcd template
  TH1F* ttbar_Temp = new TH1F("ttbar_Temp", "", nbins, xmin, xmax);
  TH1F* wjets_Temp = new TH1F("wjets_Temp", "", nbins, xmin, xmax);
  TH1F* zjets_Temp = new TH1F("zjets_Temp", "", nbins, xmin, xmax);
  TH1F* qcd_Temp   = new TH1F("qcd_Temp"  , "", nbins, xmin, xmax);

  THStack* hs = new THStack("hs","stacked histograms"); //used for stack plot

  for (int i=0; i<data_Vec.size(); i++){

    data->SetBinContent(i+1, data_Vec[i]);

    // cout<<"data: "<<data_Vec[i]<<endl;
    double mean, ttbar_con, wjets_con, zjets_con, qcd_con;

    ttbar_con = outpar[0]*ttbar_Vec[i];
    wjets_con = outpar[1]*wjets_Vec[i];
    zjets_con = outpar[2]*zjets_Vec[i];
    qcd_con   = outpar[3]*qcd_Vec[i];

    //std::cout<<"{"<<wjets_con<<", "<<err[1]*wjets_Vec[i]<<"} ";
    //std::cout<<"{"<<zjets_con<<", "<<err[2]*zjets_Vec[i]<<"} ";
    //std::cout<<"{"<<qcd_con<<", "<<err[3]*qcd_Vec[i]<<"} ";
    //std::cout<<wjets_Vec[i]<<", ";
    //std::cout<<zjets_Vec[i]<<", ";
    //std::cout<<qcd_Vec[i]<<", ";
    //std::cout<<ttbar_Vec[i]<<", ";

    //std::cout<<"{"<<wjets_Vec[i]*outpar[1]<<", "<<wjets_err_Vec[i]*outpar[1]<<"}, ";
    //std::cout<<wjets_err_Vec[i]/wjets_Vec[i]*100<<"%"<<std::endl;
    //std::cout<<"{"<<zjets_Vec[i]*outpar[2]<<", "<<zjets_err_Vec[i]*outpar[2]<<"}, ";
    //std::cout<<"{"<<qcd_Vec[i]*outpar[3]<<", "<<qcd_err_Vec[i]*outpar[3]<<"}, ";


    //std::cout<<""<<wjets_Vec[i]<<"\\pm"<<wjets_err_Vec[i]<<"& ";
    //std::cout<<wjets_err_Vec[i]/wjets_Vec[i]*100<<"%"<<std::endl;
    // std::cout<<""<<zjets_Vec[i]<<"$\\pm$ "<<zjets_err_Vec[i]<<"& ";
    //std::cout<<zjets_err_Vec[i]/zjets_Vec[i]*100<<"%"<<std::endl;

    //std::cout<<""<<qcd_Vec[i]<<"$\\pm$ "<<qcd_err_Vec[i]<<"& ";
    //std::cout<<qcd_err_Vec[i]/qcd_Vec[i]*100<<"%"<<std::endl;

    mean = ttbar_con + wjets_con + zjets_con + qcd_con;
    
    result->SetBinContent(i+1, mean); //fitting results

    ttbar_Con->SetBinContent(i+1, ttbar_con);
    wjets_Con->SetBinContent(i+1, wjets_con);
    zjets_Con->SetBinContent(i+1, zjets_con);
    qcd_Con->SetBinContent(i+1, qcd_con);
    
    ttbar_Temp->SetBinContent(i+1, ttbar_Vec[i]);
    wjets_Temp->SetBinContent(i+1, wjets_Vec[i]);
    zjets_Temp->SetBinContent(i+1, zjets_Vec[i]);
    qcd_Temp->SetBinContent(i+1, qcd_Vec[i]);
    
  }

  //print out the results
  cout <<" \n Total number of events after the fit" << endl;
  cout<<"   & ttbar+single top & w+jets & z+jets & qcd "<<endl;
  cout <<  " & " << Nsignal <<  " & " << Nwjets << " & " <<  Nzjets << " & " <<  NQCD  <<endl;
  cout<< " & "<<outpar[0]<<"+-"<<err[0]<<" & "<<outpar[1]<<"+-"<<err[1]<<" & "<<outpar[2]<<"+-"<<err[2]<<" & "<<outpar[3]<<"+-"<<err[3]<<endl;
  
  double xs_fit = (outpar[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  double xs_fitup = (outpar[0]+err[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb
  double xs_fitdown = (outpar[0]-err[0]-NSinglT)/(NtotPass/theorXsect);  //=out-Nsing/lumi*Accept  Nsing should probs be xsect*Accept... 1fb

  std::cout<<"sig: " << outpar[0] << std::endl;
  std::cout<<"s-top: " << NSinglT << std::endl;
  std::cout<<"total: " << NtotPass << std::endl;  

  std::cout<<"cross section is: "<<xs_fit<<"+"<<xs_fitup-xs_fit<<"-"<<xs_fit-xs_fitdown<<std::endl;



  //make template plots
  TCanvas* canvasTemp = new TCanvas("canvasTemp", "canvasTemp", 700, 500);
  canvasTemp->cd();
  ttbar_Temp->SetLineColor(kRed+1);
  wjets_Temp->SetLineColor(kGreen-3);
  zjets_Temp->SetLineColor(kAzure-2);
  qcd_Temp->SetLineColor(kYellow);
  // stop_Temp->SetLineColor(kOrange);

  ttbar_Temp->SetLineWidth(5);
  wjets_Temp->SetLineWidth(5);
  zjets_Temp->SetLineWidth(5);
  qcd_Temp->SetLineWidth(5);
  // stop_Temp->SetLineWidth(5);
	ttbar_Temp->SetAxisRange(0.,2.6);
  ttbar_Temp->SetTitle("");
  ttbar_Temp->Draw();
  ttbar_Temp->SetMaximum(1.3*ttbar_Temp->GetMaximum());
  //ttbar_Temp->SetMaximum(.12);
  ttbar_Temp->GetXaxis()->SetTitle("muon |#eta|");
  ttbar_Temp->GetYaxis()->SetTitle("");
  
  wjets_Temp->Draw("same");
  zjets_Temp->Draw("same");
  qcd_Temp  ->Draw("same");
  //stop_Temp  ->Draw("same");

  TLegend* legTemp = new TLegend(0.66, 0.6, 0.96, 0.92);
  legTemp->SetBorderSize(0);
  legTemp->SetTextFont(42);
  legTemp->SetFillColor(0);

  legTemp->AddEntry(ttbar_Temp, " t#bar{t}+single top", "L");
  // legTemp->AddEntry(stop_Temp, " single top", "L");
  legTemp->AddEntry(wjets_Temp, " W#rightarrowl#nu", "L");
  legTemp->AddEntry(zjets_Temp, " Z/#gamma*#rightarrowl^{+}l^{-}", "L");
  legTemp->AddEntry(qcd_Temp  , " QCD", "L");
  legTemp->SetTextSize(0.045);

  legTemp->Draw("same");

  TText* textPrelim1 = doPrelim(lumi,0.49,0.96);
  textPrelim1->Draw();

  //canvasTemp->SaveAs("notePlots/Temp"+num+".png");
  //canvasTemp->SaveAs("notePlots/Temp"+num+".pdf");
  //make fit plot

  TCanvas* canvasFit = new TCanvas("canvasFit", "canvasFit", 700, 500);
  canvasFit->cd();	
  
  ttbar_Con->SetFillColor(kRed+1);
  wjets_Con->SetFillColor(kGreen-3);
  zjets_Con->SetFillColor(kAzure-2);
  qcd_Con  ->SetFillColor(kYellow);
  // stop_Con->SetFillColor(kOrange);


   
  hs->Add(qcd_Con);
  hs->Add(zjets_Con);
  hs->Add(wjets_Con);
  // hs->Add(stop_Con);
  hs->Add(ttbar_Con);

  result->SetLineStyle(1);             //  1 = solid, 2 = dashed, 3 = dotted
  result->SetLineColor(kViolet-3);    //  black (default)
  result->SetLineWidth(3);
  
  data->Sumw2();
  data->SetMarkerStyle(20);
  data->SetMarkerSize(1.2);
  data->SetLineWidth(1); 
  double h_max = data->GetMaximum();
  data->SetMaximum(1.2*h_max);
  data->GetXaxis()->SetTitle("|#eta|(#mu)");
  data->GetYaxis()->SetTitle("Events/(0.2)");
  data->SetAxisRange(0.,2.6);
  canvasFit->SetLogy(0);
  hs->SetTitle("");

  data->Draw();
  hs->Draw("same");

  //result->Draw("same");
  data->Draw("same");


  TLegend* legFit = new TLegend(0.66, 0.6, 0.96, 0.92);
  legFit->SetBorderSize(0);
  legFit->SetTextFont(42);
  legFit->SetFillColor(0);

  legFit->AddEntry(data     , " Data", "LPE");
//  legFit->AddEntry(result   , " Fit", "L");
  legFit->AddEntry(ttbar_Con, " t#bar{t}+single top", "F");
  // legFit->AddEntry(stop_Con , " Single-Top", "F");
  legFit->AddEntry(wjets_Con, " W#rightarrowl#nu", "F");
  legFit->AddEntry(zjets_Con, " Z/#gamma*#rightarrowl^{+}l^{-}", "F");
  legFit->AddEntry(qcd_Con  , " QCD", "F");  

  legFit->SetTextSize(0.04);

  legFit->Draw("same");
 
  TText* textPrelim = doPrelim(lumi,0.16,0.96);
  textPrelim->Draw();

  gPad->RedrawAxis();
  canvasFit->SaveAs("../pasPlots/Fit"+num+".png");
  canvasFit->SaveAs("../pasPlots/Fit"+num+".pdf");
  
  cout << "To exit, quit ROOT from the File menu of the plot" << endl;
  canvasFit->SetLogy(0);
    data->SetAxisRange(0.,2.6);
 //canvasFit->SaveAs("../pasPlots/Fit.png");
 //canvasFit->SaveAs("../pasPlots/Fit.pdf");

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
  
  cout<<"num of bins: "<<nbins<<" xmax: "<<xmax<<endl;
  

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

// fcn passes back f = - 2*ln(L), the function to be minimized. not sure if N_{single top} is obtained from fitting
void fcn(int& npar, double* deriv, double& f, double par[], int flag){

   double lnL = 0.0;


  for (int i=0; i<nbins; i++){

    //data_i is the observed number of events in each bin
    int data_i = data_Vec[i];
    //xi is the expected number of events in each bin
    double xi = par[0]*ttbar_Vec[i] + par[1]*wjets_Vec[i] + par[2]*zjets_Vec[i] + par[3]*qcd_Vec[i];
    //double xi = par[0]*sig_Vec_Exp[i] + par[1]*wjets_Vec_Exp[i] + par[2]*zjets_Vec_Exp[i] + par[3]*qcd_Vec_Exp[i];
    

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
  stream  <<"#mu, #geq 4 jets, #geq 2 b-tags                                 CMS Preliminary, L = 5.0 fb^{-1} @ #sqrt{s} = 7 TeV";   

  TLatex* text = new TLatex(x, y, stream.str().c_str());
  //text->SetTextAlign(33);  //left
  //text->SetTextAlign(22);  //center
  //text->SetTextAlign(11);  //right
text->SetNDC(true);
text->SetTextFont(42);
text->SetTextSize(0.035);  // for thesis

  return text;
}
