#include <iomanip>
#include "tdrstyle.C"
#include "TTree.h"
#include "TFile.h"
#include "TFile.h"
#include "TH1F.h"
#include "TH2D.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TCanvas.h"
#include "TText.h"
#include "TLegend.h"
#include "THStack.h"
#include "TLine.h"
#include "TChain.h"
#include "TLatex.h"
#include <iostream>
#include <sstream>
#include "TLegend.h"
using namespace std;

void do2DPlots();
void do2DPlots(bool muon, TString variable, TString xtitle, TString ytitle);
void getBinning(bool muon, TString variable, TString xtitle, TString ytitle);
void do2DPlots(){

bool muon = true;

TString variable[8] = {"RecoHT_vs_GenHT", "RecoHT_lep_vs_GenHT_lep", "RecoHT_lep_met_vs_GenHT_lep_met", "Recoleptonic_W_pt_vs_Genleptonic_W_pt", "RecoM3_vs_GenM3", "RecoMET_vs_GenNu", "RecoHT_vs_GenParton", "GenJetHT_vs_GenParton"};
TString xtitle[8] = {"Reco HT (GeV)", "Reco HT+lep (GeV)", "Reco HT+lep+met (GeV)", "Reco leptonic W pt (GeV)", "Reco M3 (GeV)", "Reco MET (GeV)", "Reco HT GeV", "Gen Jet HT (GeV)"};
TString ytitle[8] = {"Gen HT (GeV)", "Gen HT+lep (GeV)", "Gen HT+lep+met (GeV)", "Gen leptonic W pt (GeV)", "Gen M3 (GeV)", "Gen Nu (GeV)", "Gen Parton HT (GeV)", "Gen Parton HT (GeV)"};



for(int i =4; i<5; i++){
//do2DPlots(muon, variable[i], xtitle[i], ytitle[i]);
getBinning(muon, variable[i], xtitle[i], ytitle[i]);
}

}

void do2DPlots(bool muon, TString variable, TString xtitle, TString ytitle){

	TString leptonFolder;
	if(muon == true){
		leptonFolder = "MuPlusJets/";
	}else{
		leptonFolder = "EPlusJets/";
		}	
		
  	setTDRStyle();
  	gStyle->SetPalette(1);

	TString dir = "../";
	TFile* tt_file = new TFile(dir + "TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET_TESTING.root");  



TString Nbtags[5] = {"_0btag","_1btag", "_2btags","_3btags",  "_4orMoreBtags"};

for(int i = 2; i < 3; i++){

	TH2D* tt_2d = (TH2D*) tt_file->Get("Binning/"+leptonFolder+variable+Nbtags[i]);

	tt_2d->Rebin2D(10,10);
  	tt_2d->GetYaxis()->SetTitle(ytitle);
  	tt_2d->GetXaxis()->SetTitle(xtitle); 
	tt_2d->GetYaxis()->SetTitleOffset(1.8);
	tt_2d->GetXaxis()->SetTitleOffset(1.5);	

        TCanvas *c= new TCanvas("c","c",10,10,800,600);
	tt_2d->Draw("COLZ");
	
  	TString plotName("plots/"+leptonFolder);
        plotName += variable;
        plotName += Nbtags[i]+".png";
 
  c->SaveAs(plotName);
  delete c;
	
}


}


void getBinning(bool muon, TString variable, TString xtitle, TString ytitle){

	TString leptonFolder;
	if(muon == true){
		leptonFolder = "MuPlusJets/";
	}else{
		leptonFolder = "EPlusJets/";
		}

	TString dir = "../";
	TFile* tt_file = new TFile(dir + "TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET_TESTING.root");

	TH2D* tt_2d = (TH2D*) tt_file->Get("Binning/"+leptonFolder+variable+"_2btags");

	int i = 0;
	int binMin[20];
	binMin[0] = 0;
//	int binCho[6] = {0, 80, 110, 160, 240, 340}; //hT
//	int binCho[6] = {0, 60, 90, 120, 160, 240}; //mwt
	int binCho[5] = {0, 100, 140, 190, 299};

for(int bin = 0; bin<tt_2d->GetNbinsX(); bin++){
	double purity[20];
	double stability[20];

	purity[i] = tt_2d->Integral(binMin[i], bin+1,binMin[i],bin+1)/tt_2d->Integral(binMin[i], bin+1,0,tt_2d->GetNbinsX()+1);
	stability[i] = tt_2d->Integral(binMin[i], bin+1,binMin[i],bin+1)/tt_2d->Integral(0,tt_2d->GetNbinsX()+1 ,binMin[i],bin+1);


//	if(purity[i]>=0.5 && stability[i]>=0.5){
//	cout << "purity: " << purity[i] << ", stability: " << stability[i] << " bin: " << bin << endl;
//	i++;
//	binMin[i] = bin;
//	}

		if(bin == binCho[i+1]){
		//cout <<setprecision(2) << stability[i] << " & " ;
			cout <<setprecision(2) << purity[i] << " & " ;
			//cout <<setprecision(2) << "purity: " << purity[i] << ", stability: " << stability[i] << " bin: " << bin*2000/500 << endl;
		i++;
		binMin[i] = bin;
		}


}




}
