import tools.PlottingUtilities as plotting
from ROOT import *
import sys

def GetHist( histName , file ):
    hist = file.Get( histName )
    if( not hist):
        print "ERROR: histogram " + histName + " not found in " + file.GetName()
        print "exiting..."
        sys.exit()
    return hist

if __name__ == "__main__":
    gROOT.Reset()
    gStyle.SetHistMinimumZero(1)
    gStyle.SetOptStat(0)
    gStyle.SetErrorX(0.4)
    
    path = "/Users/phzss/work/Top_Analysis/TTbar+MET/compare_variables/"
    input_path = path + "root_files_full_selection_except_btags/"
    output_path = path + "plots_full_selection_except_btags/" 
    
    ttjet_madgraph_file = input_path + "TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root"
    ttjet_mcatnlo_file = input_path + "TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET_MCatNLO.root"
    ttjet_powheg_file = input_path + "TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET_POWHEG.root"
    ttjet_pythia_file = input_path + "TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET_PYTHIA6.root"

    file_madgraph = TFile(ttjet_madgraph_file)
    file_mcatnlo = TFile(ttjet_mcatnlo_file)
    file_powheg = TFile(ttjet_powheg_file)
    file_pythia = TFile(ttjet_pythia_file)
    
    variables = ['M3', 'HT', 'HT_lepton', 'HT_lepton_MET', 'deltaR_lepton_MET', 'leptons_invariant_mass', 'leptonic_W_pt', 'MET_pt', 'MET_phi', 'MET_1st_jet_pt',
                 'deltaPhi_lepton_2jets', 'invariant_mass_lepton_1bjet', 'deltaPhi_lepton_closest_bjet', 'deltaPhi_lepton_MET',
                 'deltaPhi_lepton_2bjets', 'invariant_mass_lepton_2bjet', 'invariant_mass_2bjets', 'deltaPhi_2bjets', 'MET_bjets_pt', 'deltaPhi_MET_2bjets']
    
    for variable in variables:
        hist_madgraph = GetHist ("DiffVariablesAnalyser/" + variable, file_madgraph)
        hist_mcatnlo = GetHist ("DiffVariablesAnalyser/" + variable, file_mcatnlo)
        hist_powheg = GetHist ("DiffVariablesAnalyser/" + variable, file_powheg)
        hist_pythia = GetHist ("DiffVariablesAnalyser/" + variable, file_pythia)
        
        if not variable == 'HT' and not variable== 'HT_lepton' and not variable== 'HT_lepton_MET':
            hist_madgraph.Rebin(10)
            hist_mcatnlo.Rebin(10)
            hist_powheg.Rebin(10)
            hist_pythia.Rebin(10)
        
        canvas = TCanvas()
        hist_madgraph.SetLineColor(kBlack)
        hist_mcatnlo.SetLineColor(kRed)
        hist_powheg.SetLineColor(kBlue)
        hist_pythia.SetLineColor(kGreen)
        
        hist_madgraph.SetLineWidth(2)
        hist_mcatnlo.SetLineWidth(2)
        hist_powheg.SetLineWidth(2)
        hist_pythia.SetLineWidth(2)
        
        hist_madgraph.SetMarkerSize(2)
        hist_mcatnlo.SetMarkerSize(2)
        hist_powheg.SetMarkerSize(2)
        hist_pythia.SetMarkerSize(2)
        #hist_madgraph.SetMarkerStyle(20)
        
        hist_madgraph.Sumw2()
        hist_mcatnlo.Sumw2()
        hist_powheg.Sumw2()
        hist_pythia.Sumw2()
        
        hist_madgraph.Scale(1/hist_madgraph.Integral())
        hist_mcatnlo.Scale(1/hist_mcatnlo.Integral())
        hist_powheg.Scale(1/hist_powheg.Integral())
        hist_pythia.Scale(1/hist_pythia.Integral())
        
        hist_madgraph.Draw("E1")
        hist_mcatnlo.Draw('E1 same')
        hist_powheg.Draw('E1 same')
        hist_pythia.Draw('E1 same')
        
        if variable == 'MET_phi':
            legend = plotting.create_legend(x0=0.72, y0 = 0.90, x1=0.84, y1=0.80)
        elif variable == 'deltaPhi_2bjets':
            legend = plotting.create_legend(x0=0.42, y0 = 0.90, x1=0.54, y1=0.80)
        else:
            legend = plotting.create_legend(x0=0.72, y0 = 0.90, x1=0.84, y1=0.75)
        legend.SetTextSize(0.03)
        legend.AddEntry(hist_madgraph, 't#bar{t} (MADGRAPH)', 'l')
        legend.AddEntry(hist_mcatnlo, 't#bar{t} (MC@NLO)', 'l')
        legend.AddEntry(hist_powheg, 't#bar{t} (POWHEG)', 'l')
        legend.AddEntry(hist_pythia, 't#bar{t} (PYTHIA6)', 'l')
        legend.Draw()
        
        canvas.SaveAs(output_path+variable + ".pdf")
