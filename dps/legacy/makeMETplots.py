import dps.utils.PlottingUtilities as plotting
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
    
    path = "/Users/phzss/work/Top_Analysis/TTbar+MET/MET_corr_test/hists/"
    input_path = path
    output_path = "/Users/phzss/work/Top_Analysis/TTbar+MET/MET_corr_test/plots/" 
    
    ttjet_nominal_file = input_path + "TTJet_nominal.root"
    ttjet_sysshift_file = input_path + "TTJet_sysshift.root"
    ttjet_type0_file = input_path + "TTJet_type0.root"
    ttjet_sysshift_type0_file = input_path + "TTJet_sysshift_type0.root"
    
    file_nominal = TFile(ttjet_nominal_file)
    file_sysshift = TFile(ttjet_sysshift_file)
    file_type0 = TFile(ttjet_type0_file)
    file_sysshift_type0 = TFile(ttjet_sysshift_type0_file)
    
    mets = ['patMETsPFlow', 'patType1CorrectedPFMet', 'patType1p2CorrectedPFMet', 'recoMetPFlow', 'GenMET' ]
    variables = ['MET_phi', 'MET']
    bjet_bins = ['0btag', '1btag', '2btags', '3btags', '4orMoreBtags' ]
    
    for met in mets:
        for variable in variables:
            for bjet_bin in bjet_bins:
                hist_nominal = GetHist ("METAnalysis/" + met +"/" + variable + "_" + bjet_bin, file_nominal)
                hist_sysshift = GetHist ("METAnalysis/" + met +"/" + variable + "_" + bjet_bin, file_sysshift)
                hist_type0 = GetHist ("METAnalysis/" + met +"/" + variable + "_" + bjet_bin, file_type0)
                hist_sysshift_type0 = GetHist ("METAnalysis/" + met +"/" + variable + "_" + bjet_bin, file_sysshift_type0)
                
                if variable == 'MET':
                    rebin_value = 10
                else:
                    rebin_value = 4
                    
                hist_nominal.Rebin(rebin_value)
                hist_sysshift.Rebin(rebin_value)
                hist_type0.Rebin(rebin_value)
                hist_sysshift_type0.Rebin(rebin_value)
                
                canvas = TCanvas()
                hist_nominal.SetLineColor(kBlack)
                hist_sysshift.SetLineColor(kRed)
                hist_type0.SetLineColor(kBlue)
                hist_sysshift_type0.SetLineColor(kGreen)
                
                hist_nominal.SetLineWidth(2)
                hist_sysshift.SetLineWidth(2)
                hist_type0.SetLineWidth(2)
                hist_sysshift_type0.SetLineWidth(2)
                
                hist_nominal.SetMarkerSize(2)
                hist_sysshift.SetMarkerSize(2)
                hist_type0.SetMarkerSize(2)
                hist_sysshift_type0.SetMarkerSize(2)
                
                hist_type0.Draw()
                hist_sysshift.Draw('same')
                hist_sysshift_type0.Draw('same')
                hist_nominal.Draw('same')
                
                if variable == 'MET':
                    hist_nominal.SetAxisRange(0,300, "X")
                    hist_sysshift.SetAxisRange(0,300, "X")
                    hist_type0.SetAxisRange(0,300, "X")
                    hist_sysshift_type0.SetAxisRange(0,300, "X")
                    
                    hist_type0.Draw()
                    hist_sysshift.Draw('same')
                    hist_sysshift_type0.Draw('same')
                    hist_nominal.Draw('same')
                
                legend = plotting.create_legend(x0=0.72, y0 = 0.90, x1=0.84, y1=0.75)
                legend.SetTextSize(0.03)
                legend.AddEntry(hist_nominal, 't#bar{t} nominal', 'l')
                legend.AddEntry(hist_sysshift, 't#bar{t} sys_shift', 'l')
                legend.AddEntry(hist_type0, 't#bar{t} type0', 'l')
                legend.AddEntry(hist_sysshift_type0, 't#bar{t} sys_shift+type0', 'l')
                legend.Draw()
               
                canvas.SaveAs(output_path + met +"_" + variable + "_" + bjet_bin + ".pdf")
                
                
