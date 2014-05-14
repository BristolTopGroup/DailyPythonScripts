'''
Created on Aug 18, 2012

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''
#from ROOT import *
from ROOT import RooRealVar, RooDataHist, RooArgList, RooHistPdf, RooArgSet, RooAddPdf, RooMCStudy, RooFit
import tools.ROOTFileReader as FileReader
import FILES
from math import sqrt

distribution = "TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_PFMET_bin_0-25/muon_AbsEta_2orMoreBtags"
qcdDistribution = "TTbarPlusMetAnalysis/MuPlusJets/QCD non iso mu+jets/BinnedMETAnalysis/Muon_PFMET_bin_0-25/muon_AbsEta_0btag"
qcdDistribution2 = qcdDistribution
data_file = 'SingleMu'
#qcdDistribution = "TTbarPlusMetAnalysis/EPlusJets/QCDConversions/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_0btag"
#qcdDistribution2 = "TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets/BinnedMETAnalysis/Electron_PFMET_bin_0-25/electron_AbsEta_0btag"
#data_file = 'ElectronHad'
h_data = FileReader.getHistogramFromFile(distribution, FILES.files[data_file])
temp_tt = FileReader.getHistogramFromFile(distribution, FILES.files['TTJet'])
temp_wj = FileReader.getHistogramFromFile(distribution, FILES.files['W1Jet'])
temp_wj.Add(FileReader.getHistogramFromFile(distribution, FILES.files['W2Jets']))
temp_wj.Add(FileReader.getHistogramFromFile(distribution, FILES.files['W3Jets']))
temp_wj.Add(FileReader.getHistogramFromFile(distribution, FILES.files['W4Jets']))
temp_zj = FileReader.getHistogramFromFile(distribution, FILES.files['DYJetsToLL'])
temp_qcd = FileReader.getHistogramFromFile(qcdDistribution, FILES.files[data_file])
temp_qcd2  = FileReader.getHistogramFromFile(qcdDistribution2, FILES.files[data_file])
temp_stop = FileReader.getHistogramFromFile(distribution, FILES.files['T_tW-channel'])
temp_stop.Add(FileReader.getHistogramFromFile(distribution, FILES.files['T_t-channel']))
temp_stop.Add(FileReader.getHistogramFromFile(distribution, FILES.files['T_s-channel']))
temp_stop.Add(FileReader.getHistogramFromFile(distribution, FILES.files['Tbar_tW-channel']))
temp_stop.Add(FileReader.getHistogramFromFile(distribution, FILES.files['Tbar_t-channel']))
temp_stop.Add(FileReader.getHistogramFromFile(distribution, FILES.files['Tbar_s-channel']))
temp_VPlusJets = temp_zj.Clone('V+jets')
temp_VPlusJets.Add(temp_wj)
n_ttbar = temp_tt.Integral()
n_wj = temp_wj.Integral()
n_VJ = temp_VPlusJets.Integral()
n_zj = temp_zj.Integral()
n_stop = temp_stop.Integral()
n_qcd = 1
REBIN = 20
n_signal = n_ttbar + n_stop
temp_VPlusJets.Rebin(REBIN)
temp_tt.Rebin(REBIN)
temp_wj.Rebin(REBIN)
temp_zj.Rebin(REBIN)
temp_stop.Rebin(REBIN)
temp_qcd.Rebin(REBIN)
temp_qcd2.Rebin(REBIN)
temp_qcd.Scale(n_qcd / temp_qcd.Integral())
temp_qcd2.Scale(n_qcd/temp_qcd2.Integral())
temp_signal = temp_tt.Clone('signal')
temp_signal.Add(temp_stop)

leptonAbsEta = RooRealVar("leptonAbsEta", "leptonAbsEta", 0., 3.)
variables = RooArgList()
variables.add(leptonAbsEta)
vars_set = RooArgSet()
vars_set.add(leptonAbsEta)
n_event_obs = h_data.Integral();
lowerBound = -10 * sqrt(n_event_obs);
lowerBound = 0
upperBound = n_event_obs + 10 * sqrt(n_event_obs);
upperBound = n_event_obs
n_init = n_event_obs / 2.;
data = RooDataHist("data", "dataset with leptonAbsEta", variables, h_data)
rh_tt = RooDataHist("rh_tt", "tt", variables, temp_tt);
rh_wj = RooDataHist("rh_wj", "wj", variables, temp_wj);
rh_zj = RooDataHist("rh_zj", "zj", variables, temp_zj);
rh_VJ = RooDataHist("rh_VJ", "VJ", variables, temp_VPlusJets);
rh_qcd = RooDataHist("rh_qcd", "qcd", variables, temp_qcd);
rh_qcd2 = RooDataHist("rh_qcd", "qcd", variables, temp_qcd2);
rh_stop = RooDataHist("rh_stop", "singletop", variables, temp_stop);
rh_signal = RooDataHist("rh_signal", "signal", variables, temp_signal);

pdf_tt = RooHistPdf("pdf_tt", "Signal pdf", vars_set, rh_tt, 0);
pdf_wj = RooHistPdf ("pdf_wj", "W+jets pdf", vars_set, rh_wj, 0);
pdf_zj = RooHistPdf ("pdf_zj", "Z+jets pdf", vars_set, rh_zj, 0);
pdf_VJ = RooHistPdf ("pdf_VJ", "Z+jets pdf", vars_set, rh_VJ, 0);
pdf_qcd = RooHistPdf("pdf_qcd", "QCD pdf ", vars_set, rh_qcd, 0);
pdf_qcd2 = RooHistPdf("pdf_qcd", "QCD pdf ", vars_set, rh_qcd2, 0);
pdf_stop = RooHistPdf("pdf_stop", "single top pdf", vars_set, rh_stop, 0);
pdf_signal = RooHistPdf("pdf_signal", "single top pdf", vars_set, rh_signal, 0);

ntt = RooRealVar ("ntt", "number of tt signal events", n_ttbar, lowerBound, upperBound, "event");
nwj = RooRealVar  ("nwj", "number of W+jets bgnd events", n_wj, lowerBound, upperBound, "event");
nzj = RooRealVar  ("nzj", "number of Z+jets bgnd events", n_zj, lowerBound, upperBound, "event");
nVJ = RooRealVar  ("nVJ", "number of Z+jets bgnd events", n_VJ, lowerBound, upperBound, "event");
nqcd = RooRealVar("nqcd", "number of QCD bgnd events", n_qcd, lowerBound, upperBound, "event");
nstop = RooRealVar("nstop", "number of single top bgnd events", n_stop, lowerBound, upperBound, "event");
nSignal = RooRealVar("nSignal", "number of single top + ttbar events", n_stop + n_ttbar, lowerBound, upperBound, "event");
model = RooAddPdf("model", "sig+wj+zj+qcd+stop",
            RooArgList(pdf_signal, pdf_VJ, pdf_qcd),
            RooArgList(nSignal, nVJ, nqcd)) ; 
fitResult = model.fitTo(data, RooFit.Minimizer("Minuit2", "Migrad"), 
                        RooFit.NumCPU(8), RooFit.Extended(True),
                        RooFit.SumW2Error(False), RooFit.Strategy(2), 
                        #verbosity
                        RooFit.PrintLevel(-1), RooFit.Warnings(False), RooFit.Verbose(False))

#ntt_fit = ntt.getVal();
nSignal_fit = nSignal.getVal();
nwj_fit = nwj.getVal();
#nzj_fit = nzj.getVal();
nVJ_fit = nVJ.getVal();
nqcd_fit = nqcd.getVal();
#nstop_fit = nstop.getVal();


nSignal_fiterr = nSignal.getError();
#ntt_fiterr = ntt.getError();
nwj_fiterr = nwj.getError();
nVJ_fiterr = nVJ.getError();
nqcd_fiterr = nqcd.getError();
#nstop_fiterr = nstop.getError();

print "Total events in signal region: ", n_event_obs;
print 'DATA:', n_event_obs
print 'N_tt:', n_ttbar
print 'N_signal', n_signal
print 'N_WJ:', n_wj
print 'N_VJ:', n_VJ
print 'N_sTop:', n_stop
print 'N_QCD:', n_qcd
print 'SumMC:', n_signal + n_VJ + n_qcd
print "nSignal fitted:  %d +/- %d" % (nSignal_fit, nSignal_fiterr)
#print "ntt fitted: ", ntt_fit, " +/- ", ntt_fiterr;
#print "nwj fitted: %d +/- %d" %( nwj_fit, nwj_fiterr)
print "VJ fitted:  %d +/- %d" % (nVJ_fit, nVJ_fiterr)
print "nqcd fitted:  %d +/- %d" % (nqcd_fit, nqcd_fiterr)
#print "nstop fitted: ", nstop_fit, " +/- ", nstop_fiterr;
#print 'SumMC:', ntt_fit + nwj_fit + nzj_fit + nqcd_fit + nstop_fit
print 'SumMC: %d' % (nSignal_fit + nVJ_fit + nqcd_fit)
