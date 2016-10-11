'''
Created on Aug 18, 2012

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''
from ROOT import *
from ROOT import RooRealVar, RooDataHist, RooArgList, RooHistPdf, RooArgSet, RooAddPdf
import dps.utils.ROOTFileReader as FileReader
import FILES
from math import sqrt
h_m3_data = FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['ElectronHad'])
temp_tt = FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['TTJet'])
temp_wj = FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['W1Jet'])
temp_wj.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['W2Jets']))
temp_wj.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['W3Jets']))
temp_wj.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['W4Jets']))
temp_zj = FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['DYJetsToLL'])
temp_qcd = FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/QCDConversions/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_0btag", FILES.files['ElectronHad'])
temp_stop = FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['T_tW-channel'])
temp_stop.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['T_t-channel']))
temp_stop.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['T_s-channel']))
temp_stop.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['Tbar_tW-channel']))
temp_stop.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['Tbar_t-channel']))
temp_stop.Add(FileReader.getHistogramFromFile("TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_2orMoreBtags", FILES.files['Tbar_s-channel']))

n_ttbar = temp_tt.Integral()
n_wj = temp_wj.Integral()
n_zj = temp_zj.Integral()
n_stop = temp_stop.Integral()
n_qcd = 800
n_signal = n_ttbar + n_stop

temp_tt.Rebin(20)
temp_wj.Rebin(20)
temp_zj.Rebin(20)
temp_stop.Rebin(20)
temp_qcd.Rebin(20)
temp_qcd.Scale(800/temp_qcd.Integral())
temp_signal = temp_tt.Clone('signal')
temp_signal.Add(temp_stop)
#temp_tt.Scale(1/temp_tt.Integral())
#temp_wj.Scale(1/temp_wj.Integral())
#temp_zj.Scale(1/temp_zj.Integral())
#temp_stop.Scale(1/temp_stop.Integral())
#temp_qcd.Scale(1/temp_qcd.Integral())
leptonAbsEta = RooRealVar("leptonAbsEta", "leptonAbsEta", 0., 3.)
vars = RooArgList()
vars.add(leptonAbsEta)
vars_set = RooArgSet()
vars_set.add(leptonAbsEta)
n_event_obs = h_m3_data.GetEntries();
lowerBound = -10 * sqrt(n_event_obs); 
upperBound = n_event_obs + 10 * sqrt(n_event_obs);
n_init = n_event_obs / 2.;
data = RooDataHist("data", "dataset with leptonAbsEta", vars, h_m3_data)
rh_tt = RooDataHist("rh_tt", "tt", vars, temp_tt);
rh_wj = RooDataHist("rh_wj", "wj", vars, temp_wj);
rh_zj = RooDataHist("rh_zj", "zj", vars, temp_zj);
rh_qcd = RooDataHist("rh_qcd", "qcd", vars, temp_qcd);
rh_stop = RooDataHist("rh_stop", "singletop", vars, temp_stop);
rh_signal = RooDataHist("rh_signal", "signal", vars, temp_signal);

pdf_tt = RooHistPdf("pdf_tt", "Signal pdf", vars_set, rh_tt, 0);
pdf_wj = RooHistPdf ("pdf_wj", "W+jets pdf", vars_set, rh_wj, 0);
pdf_zj = RooHistPdf ("pdf_zj", "Z+jets pdf", vars_set, rh_zj, 0);
pdf_qcd = RooHistPdf("pdf_qcd", "QCD pdf ", vars_set, rh_qcd, 0);
pdf_stop = RooHistPdf("pdf_stop", "single top pdf", vars_set, rh_stop, 0);
pdf_signal = RooHistPdf("pdf_signal", "single top pdf", vars_set, rh_signal, 0);

ntt = RooRealVar ("ntt", "number of tt signal events", n_ttbar, lowerBound, upperBound, "event");
nwj = RooRealVar  ("nwj", "number of W+jets bgnd events", n_wj, lowerBound, upperBound, "event");
nzj = RooRealVar  ("nzj", "number of Z+jets bgnd events", n_zj, lowerBound, upperBound, "event");
nqcd = RooRealVar("nqcd", "number of QCD bgnd events", n_qcd, lowerBound, upperBound, "event");
nstop = RooRealVar("nstop", "number of single top bgnd events", n_stop, lowerBound, upperBound, "event");
nSignal = RooRealVar("nSignal", "number of single top + ttbar events", n_stop + n_ttbar, lowerBound, upperBound, "event");
model = RooAddPdf("model", "sig+wj+zj+qcd+stop",
#            RooArgList(pdf_tt, pdf_wj, pdf_zj, pdf_qcd, pdf_stop),
#            RooArgList(ntt, nwj, nzj, nqcd, nstop)) ; 
            RooArgList(pdf_signal, pdf_wj, pdf_zj, pdf_qcd),
            RooArgList(nSignal, nwj, nzj, nqcd)) ; 
model.fitTo(data, RooFit.Minimizer("Minuit2", "Migrad"), RooFit.NumCPU(8))
#leptonAbsEtaframe1 = leptonAbsEta.frame();
#leptonAbsEtaframe2 = leptonAbsEta.frame();
#leptonAbsEtaframe3 = leptonAbsEta.frame();
#leptonAbsEtaframe4 = leptonAbsEta.frame();
#leptonAbsEtaframe5 = leptonAbsEta.frame();
#leptonAbsEtaframe6 = leptonAbsEta.frame();
#leptonAbsEtaframe7 = leptonAbsEta.frame();
#leptonAbsEtaframe8 = leptonAbsEta.frame();
#leptonAbsEtaframe9 = leptonAbsEta.frame();
#leptonAbsEtaframe10 = leptonAbsEta.frame();
#leptonAbsEtaframe11 = leptonAbsEta.frame();
#
#etype = RooAbsData.Poisson;
#rh_tt.plotOn(leptonAbsEtaframe1, RooFit.MarkerSize(1), RooFit.DataError(etype));
#rh_wj.plotOn(leptonAbsEtaframe2, RooFit.MarkerSize(1), RooFit.DataError(etype));
#rh_qcd.plotOn(leptonAbsEtaframe3, RooFit.MarkerSize(1), RooFit.DataError(etype));
#pdf_tt.plotOn(leptonAbsEtaframe4);
#pdf_wj.plotOn(leptonAbsEtaframe5);
#pdf_qcd.plotOn(leptonAbsEtaframe6);
#data.plotOn(leptonAbsEtaframe8, RooFit.MarkerSize(1)); #plot pseudo-data
#model.plotOn(leptonAbsEtaframe8); #plot composite pdf (s+b model)
#model.plotOn(leptonAbsEtaframe8, RooFit.Components(RooArgSet(pdf_tt)), RooFit.LineStyle(kDashed), RooFit.LineColor(kBlue + 1));
#model.plotOn(leptonAbsEtaframe8, RooFit.Components(RooArgSet(pdf_wj)), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed + 1));
#model.plotOn(leptonAbsEtaframe8, RooFit.Components(RooArgSet(pdf_qcd)), RooFit.LineStyle(kDashed), RooFit.LineColor(kOrange - 6));
      
# single top plots
#rh_stop.plotOn(leptonAbsEtaframe9, RooFit.MarkerSize(1), RooFit.DataError(etype));
#pdf_stop.plotOn(leptonAbsEtaframe10);

#ntt_fit = ntt.getVal();
nSignal_fit = nSignal.getVal();
nwj_fit = nwj.getVal();
nzj_fit = nzj.getVal();
nqcd_fit = nqcd.getVal();
#nstop_fit = nstop.getVal();


nSignal_fiterr = nSignal.getError();
#ntt_fiterr = ntt.getError();
nwj_fiterr = nwj.getError();
nzj_fiterr = nzj.getError();
nqcd_fiterr = nqcd.getError();
#nstop_fiterr = nstop.getError();

print "Total events in signal region: ", n_event_obs;
print 'DATA:', n_event_obs
print 'N_tt:', n_ttbar
print 'N_signal', n_signal
print 'N_WJ:', n_wj
print 'N_ZJ:', n_zj
print 'N_sTop:', n_stop
print 'N_QCD:', n_qcd
print 'SumMC:', n_ttbar + n_wj + n_zj + n_stop + n_qcd
print "nSignal fitted: ", nSignal_fit, " +/- ", nSignal_fiterr;
#print "ntt fitted: ", ntt_fit, " +/- ", ntt_fiterr;
print "nwj fitted: ", nwj_fit, " +/- ", nwj_fiterr;
print "zj fitted: ", nzj_fit, " +/- ", nzj_fiterr;
print "nqcd fitted: ", nqcd_fit, " +/- ", nqcd_fiterr;
#print "nstop fitted: ", nstop_fit, " +/- ", nstop_fiterr;
#print 'SumMC:', ntt_fit + nwj_fit + nzj_fit + nqcd_fit + nstop_fit
print 'SumMC:', nSignal_fit + nwj_fit + nzj_fit + nqcd_fit
