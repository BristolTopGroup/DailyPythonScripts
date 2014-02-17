//=====================================================================-*-C++-*-
// File and Version Information:
//      $Id: RooUnfoldExample.cxx 279 2011-02-11 18:23:44Z T.J.Adye $
//
// Description:
//      Simple example usage of the RooUnfold package using toy MC.
//
// Authors: Tim Adye <T.J.Adye@rl.ac.uk> and Fergus Wilson <fwilson@slac.stanford.edu>
//
//==============================================================================

#if !defined(__CINT__) || defined(__MAKECINT__)
#include <iostream>
using std::cout;
using std::endl;

#include "TRandom.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TString.h"
#include "tdrstyle.C"
#include "TLine.h"
#include "TSpline.h"
#include "TGraph.h"

#include "TSVDUnfold.h"
#include "RooUnfold.h"
#include "TUnfold.h"
#include "RooUnfoldResponse.h"
#include "RooUnfoldBayes.h"
#include "RooUnfoldSvd.h"
#include "RooUnfoldTUnfold.h"
#include "RooUnfoldBinByBin.h"
#endif

//==============================================================================
// Example Unfolding
//==============================================================================

void globalCorr() {
#ifdef __CINT__
	gSystem->Load("libRooUnfold");
#endif

	TStyle *tdrStyle = new TStyle("tdrStyle", "Style for P-TDR");
	setTDRStyle();

	double lumi = 5814.;
	double ttbarXsect = 225.197;

	int kval = 4;
	TString syst = "central_dir/central";
// for theory systematics
	TString theory = "madgraph";
	double central[6] = { 0.00682425, 0.0130933, 0.0106169, 0.00597566, 0.00191791, 0.000269403 };

//MET will need choice of variable at the top
	TString Variable = "MET";
	int Nbins = 6;
	double width[6] = { 25, 20, 25, 30, 50, 100 };
	double xbins[7] = { 0, 25, 45, 70, 100, 150, 250 };
	double xbinsTheo[7] = { 3, 28, 48, 73, 103, 153, 253 };
	double xbinsMeas[7] = { -3, 22, 42, 67, 97, 147, 247 };
	TString folder = "unfolding_MET_analyser_muon_channel_patType1CorrectedPFMet/";
	TString Xtitle = "MET [GeV]";

	// Get histograms
	cout << "==================================== READ =====================================" << endl;
	TString dir = "rootFiles/";

	//old
	TFile* unf_file = new TFile(dir + "unfolding_2012_5814.root");
	TFile* meas_file = new TFile(dir + "diffResults_" + Variable + "_5814.root");

	TH1D *events = (TH1D*) unf_file->Get("EventFilter/EventCounter");

	TH2D* hResp = (TH2D*) unf_file->Get(folder + "response_without_fakes_AsymBins");

	TH1D *hRespMeas = (TH1D*) unf_file->Get(folder + "measured_AsymBins");
	//truth with extra for inefficiency
	//TH1D* hTrue = (TH1D*) unf_file->Get(folder+"truth_AsymBins");
	TH1D* hTrue_Assym = (TH1D*) unf_file->Get(folder + "truth_AsymBins");

	double totTT = events->GetBinContent(1);
	hTrue_Assym->Scale(lumi * ttbarXsect / totTT);
	hRespMeas->Scale(lumi * ttbarXsect / totTT);
	hResp->Scale(lumi * ttbarXsect / totTT);

	cout << "==================================== TRAIN ====================================" << endl;
	RooUnfoldResponse response(hRespMeas, hTrue_Assym, hResp, "response", "response");

	cout << "==================================== TEST =====================================" << endl;
//  TH1D* hMeas= (TH1D*) unf_file->Get(folder+"measured_AsymBins");    // this is used for closure test
	TH1D* hMeas = (TH1D*) meas_file->Get(syst + "_ttbar_fit");

	cout << "==================================== UNFOLD ===================================" << endl;
//RooUnfoldBayes   unfold (&response, hMeas, 4);    // OR
//RooUnfoldSvd     unfold (&response, hMeas, kval);    // OR
	RooUnfoldTUnfold unfold(&response, hMeas);
//RooUnfoldBinByBin unfold (&response, hMeas);

	//RooUnfold::ErrorTreatment = withError;  RooUnfold::kCovToy
	unfold.FixTau(0.0004015);

	TH1D* test = (TH1D*) unfold.Hreco();

	//put TUnfold stuff here... this for when using roounfold

	TUnfold unfold(hRespMeas, TUnfold::kHistMapOutputHoriz);

	//histogram for global corr
	double rhos[10000];
	double taus[10000];
	double tauOpt = 0.;
	double rhoMin = 1.;
	for (int i = 1; i < 10001; i++) {
		taus[i - 1] = 1E-7 * i;
		double biasScale = 0.0;
		unfold.RooUnfoldTUnfold::Impl()->DoUnfold(taus[i - 1], hMeas, biasScale);

		TH1D* rhoHist = new TH1D("rho", "", Nbins, xbinsMeas);
		//TH2D* ematrixinv = 0;
		const int* binMap = 0;

		rhos[i - 1] = unfold.RooUnfoldTUnfold::Impl()->GetRhoI(rhoHist, 0, 0);

		//cout << "tau: " << taus[i-1] <<  " ,rho: " << rhos[i-1] << endl;

		if (rhos[i - 1] < rhoMin) {
			rhoMin = rhos[i - 1];
			tauOpt = taus[i - 1];
		}

		delete rhoHist;
	}
	cout << "tau from global corr: " << tauOpt << endl;

	TCanvas *rhoCanv = new TCanvas("c1", "A Simple Graph Example", 200, 10, 700, 500);
	TGraph* globalCorrs = new TGraph(10000, taus, rhos);
	globalCorrs->Draw("AC*");

	//tdrStyle->SetLabelFont(22, "XYZ");
	tdrStyle->SetLabelSize(0.01, "XY");
	globalCorrs->GetXaxis()->SetTitle("#tau"); // globalCorrs->GetXaxis()->SetTitleSize(0.05);
	globalCorrs->GetYaxis()->SetTitle("#bar{#rho}(#tau)");
	globalCorrs->GetYaxis()->SetTitleSize(0.05);
	//rhoCanv->SetLogx();
	rhoCanv->SaveAs("plots/" + Variable + "/" + Variable + "_globalCorrs.png");
//
// 	//result using global corr tau:
//         unfold.RooUnfoldTUnfold::Impl()->DoUnfold(0.0001037,hMeas,0.);
// 	//unfold.RooUnfoldTUnfold::Impl()->DoUnfold(6.27112e-11,hMeas,0.);
// 	TH1D *test=unfold.RooUnfoldTUnfold::Impl()->GetOutput("x","myVariable");

	//unfold.RooUnfoldTUnfold::Impl()->SetInput(hMeas);

//       //Lshape method:
	Int_t nScan = 60;
	Int_t iBest;
	TSpline *logTauX, *logTauY;
	TGraph *lCurve;

	iBest = unfold.RooUnfoldTUnfold::Impl()->ScanLcurve(nScan, 0.00001, 0.001, &lCurve);
	std::cout << "best choice of tau from lshape=" << unfold.RooUnfoldTUnfold::Impl()->GetTau() << "\n";

	//    TH1D *test=unfold.RooUnfoldTUnfold::Impl()->GetOutput("x","myVariable");
	//TH2D *rhoij=unfold.RooUnfoldTUnfold::Impl()->GetRhoIJ("correlation","myVariable");

	//print table of stuff
	unfold.PrintTable(cout, hTrue_Assym);

//   only use if using TSVD unfold
//   TH1D *ddist = unfold.Impl()->GetD();

	//differential histos to change binning of original histos
	TH1D *meas = new TH1D("meas", "", Nbins, xbinsMeas);
	TH1D *theo = new TH1D("theor", "", Nbins, xbinsTheo);
	TH1D *reco = new TH1D("nominal", "", Nbins, xbins);

	for (int i = 0; i < Nbins; i++) {
		meas->SetBinContent(i + 1, hMeas->GetBinContent(i + 1));
		theo->SetBinContent(i + 1, hTrue_Assym->GetBinContent(i + 1));
		reco->SetBinContent(i + 1, test->GetBinContent(i + 1));
		meas->SetBinError(i + 1, hMeas->GetBinError(i + 1));
		theo->SetBinError(i + 1, hTrue_Assym->GetBinError(i + 1));
		reco->SetBinError(i + 1, test->GetBinError(i + 1));
	}

	//raw results from unfolding
	TCanvas *c = new TCanvas("Raw Plot", "Raw Plot", 900, 600);

	reco->SetMinimum(0.0);
	reco->SetMaximum(theo->GetBinContent(hTrue_Assym->GetMaximumBin()) * 1.3);
	reco->Draw();

	reco->GetXaxis()->SetTitle(Xtitle);
	reco->GetXaxis()->SetTitleSize(0.05);
	reco->GetYaxis()->SetTitle("N Events");
	reco->GetYaxis()->SetTitleSize(0.05);

	meas->SetLineColor(kRed);
	meas->SetMarkerColor(kRed);
	meas->Draw("SAME");
	theo->SetLineColor(kGreen);
	theo->SetMarkerColor(kGreen);
	theo->Draw("SAME");
	reco->Draw("SAME");

	TLegend *tleg2;
	tleg2 = new TLegend(0.7, 0.5, 0.8, 0.7);
	tleg2->SetTextSize(0.04);
	tleg2->SetBorderSize(0);
	tleg2->SetFillColor(10);
	tleg2->AddEntry(reco, "unfolded", "lpe");
	tleg2->AddEntry(meas, "measured", "lpe");
	tleg2->AddEntry(theo, "truth", "lpe");

	tleg2->Draw("same");

	c->SaveAs("plots/" + Variable + "/" + Variable + "_raw.png");

	//pre fit used for partial cross section measurement
	TH1D* tt_tot = (TH1D*) meas_file->Get(syst + "_ttbar_prefit");

	reco->Scale((hMeas->Integral() / (reco->Integral() * tt_tot->Integral())) * ttbarXsect);
	meas->Scale((1. / tt_tot->Integral()) * ttbarXsect);
	theo->Scale((1. / hTrue_Assym->Integral()) * ttbarXsect);

	for (int i = 0; i < Nbins; i++) {
		cout << "meas: " << meas->GetBinContent(i + 1) << endl;
		cout << "theor: " << theo->GetBinContent(i + 1) << endl;
		cout << "reco: " << reco->GetBinContent(i + 1) << endl;
	}

	//after normalising unfolded to the measured result and calculating partial cross sections
	TCanvas *c1 = new TCanvas("Partial Plot", "Partial Plot", 900, 600);

	reco->SetMinimum(0.0);
	reco->SetMaximum(theo->GetBinContent(hTrue_Assym->GetMaximumBin()) * 1.3);
	reco->Draw();

	reco->GetXaxis()->SetTitle(Xtitle);
	reco->GetXaxis()->SetTitleSize(0.05);
	reco->GetYaxis()->SetTitle("#partial #sigma [pb]");
	reco->GetYaxis()->SetTitleSize(0.05);
	meas->Draw("SAME");
	theo->Draw("SAME");
	reco->Draw("SAME");

	tleg2->Draw("same");

	c1->SaveAs("plots/" + Variable + "/" + Variable + "_partial.png");

	//normalising to measured (for measurment) or theoretical (for truth) cross section
	TCanvas *c2 = new TCanvas("Norm Plot", "Norm Plot", 900, 600);

	double measXsect = meas->Integral();
	double theoXsect = theo->Integral();
	double recoXsect = reco->Integral();
	meas->Scale(1. / measXsect);
	theo->Scale(1. / theoXsect);
	reco->Scale(1. / recoXsect);

	reco->SetMinimum(0.0);
	reco->SetMaximum(theo->GetBinContent(hTrue_Assym->GetMaximumBin()) * 1.3);
	reco->Draw();

	reco->GetXaxis()->SetTitle(Xtitle);
	reco->GetXaxis()->SetTitleSize(0.05);
	reco->GetYaxis()->SetTitle("#frac{1}{#sigma} #partial #sigma");
	reco->GetYaxis()->SetTitleSize(0.05);

	meas->Draw("SAME");
	theo->Draw("SAME");
	reco->Draw("SAME");
	tleg2->Draw("same");

	c2->SaveAs("plots/" + Variable + "/" + Variable + "_norm.png");

	// divide by width to get differential
	TCanvas *c3 = new TCanvas("Norm Diff Plot", "Norm Diff Plot", 900, 600);

	for (int i = 0; i < Nbins; i++) {
		meas->SetBinContent(i + 1, meas->GetBinContent(i + 1) / width[i]);
		theo->SetBinContent(i + 1, theo->GetBinContent(i + 1) / width[i]);
		reco->SetBinContent(i + 1, reco->GetBinContent(i + 1) / width[i]);
		meas->SetBinError(i + 1, meas->GetBinError(i + 1) / width[i]);
		theo->SetBinError(i + 1, theo->GetBinError(i + 1) / width[i]);
		reco->SetBinError(i + 1, reco->GetBinError(i + 1) / width[i]);
	}

	reco->SetMinimum(0.0);
	reco->SetMaximum(theo->GetBinContent(hTrue_Assym->GetMaximumBin()) * 1.3);
	reco->Draw();

	reco->GetXaxis()->SetTitle(Xtitle);
	reco->GetXaxis()->SetTitleSize(0.05);
	reco->GetYaxis()->SetTitle("#frac{1}{#sigma} #frac{#partial #sigma}{#partial MET} 				[GeV^{-1}]");
	reco->GetYaxis()->SetTitleSize(0.05);

	meas->Draw("SAME");
	theo->Draw("SAME");
	reco->Draw("SAME");
	tleg2->Draw("same");

	c3->SaveAs("plots/" + Variable + "/" + Variable + "_normDiff.png");

	cout.precision(2);

	for (int i = 0; i < Nbins; i++) {
		//cout << 100*reco->GetBinError(i+1)/reco->GetBinContent(i+1) << " & ";

		//cout << 100*(reco->GetBinContent(i+1)-central[i])/central[i] << " & ";
		cout << reco->GetBinContent(i + 1) << " , ";
	}

	//Lcurve plot
	TCanvas *c_di = new TCanvas("l curve", "lcurve", 800, 600);

	//c_di->SetLogy();

	lCurve->Draw("AC*");
	lCurve->GetHistogram()->SetXTitle("log10(chi^2)");
	lCurve->GetHistogram()->SetYTitle("log10(curvature)");
	lCurve->Draw("AC*");

	c_di->SaveAs("plots/" + Variable + "/lcurve.png");

	delete c_di;

}

#ifndef __CINT__
int main() {
	globalCorr();
	return 0;
} // Main program when run stand-alone
#endif
