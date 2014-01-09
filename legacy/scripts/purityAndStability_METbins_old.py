'''
Created on Aug 1, 2012

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''
from tools import Styles
import FILES
import tools.ROOTFileReader as FileReader

from ROOT import *
#import HistGetter
#import HistPlotter
#import inputFiles
from array import*
import os

samples = [
         'TTJet',
#         'POWHEG',
#         'PYTHIA6',
#         'MCatNLO'
         ]

metBins = [
           '0-24',
           '25-44',
           '45-69',
           '70-99',
           '100-inf'
           ]

metTypes = [
#            'patMETsPFlow',
            'patType1CorrectedPFMet',
#            'patType1p2CorrectedPFMet'
            ]

bJetBins = [
#           '0btag',
#           '0orMoreBtag',
#           '1btag',
#           '1orMoreBtag',
           '2orMoreBtags'
           ]

outputFolder = "/storage/phjaj/Plots/" #REMEMBER TO CHANGE
outputFolder = "/storage/results/plots/" #REMEMBER TO CHANGE
#saveAs = HistPlotter.saveAs

if __name__ == "__main__":
    base = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/'
    base = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/'
#    base = "METAnalysis/"

    
    gROOT.Reset()
    gROOT.ForceStyle()
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 5001;')
    
    tdrStyle = Styles.tdrStyle()

    gStyle.SetOptStat(0)

    for sample in samples:
        path = outputFolder + base + sample
#        if not os.path.exists(path):
#            os.makedirs(path)
#        print 'Sample = ', sample
#        outputFile = open(path + "/outputFile_" + str(sample) + ".txt", "w")
        for metType in metTypes:
            for bJetBin in bJetBins:
                histFile = base + metType + "/RecoMET_vs_GenMET_" + bJetBin
                print histFile
                hist = FileReader.getHistogramFromFile(histFile, FILES.files[sample])
                print "Plotting..."
                print "hist = ", hist
                title1 = TPaveText(0.15, 0.965, 0.4, 1.01, "NDC")
                title1.SetFillStyle(0)
                title1.SetBorderSize(0)
                title1.SetTextFont(42)
                title1.SetTextAlign(13)

                title2 = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
                title2.SetFillStyle(0)
                title2.SetBorderSize(0)
                title2.SetTextFont(42)
                title2.SetTextAlign(13)

#                bJetBinTitles = {'0btag':'0 b-tags', '0orMoreBtag':'#geq0 b-tags', '1btag':'1 b-tags', '1orMoreBtag':'#geq1 b-tags', '2orMoreBtags':'#geq2 b-tags'}
#                title1.AddText("e, #geq4 jets, #geq2 b-tags")
                title1.AddText("#mu, #geq4 jets, #geq2 b-tags")
                title2.AddText("CMS Simulation, L = 5.1fb^{-1} at #sqrt{s} = 7 TeV")

                hist.GetXaxis().SetTitle("generated MET [GeV]")
                hist.GetYaxis().SetTitle("reconstructed MET [GeV]")
                hist.SetTitle("")

#                metBins = {0:[0, 24], 1:[25, 44], 2:[45, 69], 3:[70, 99], 4:[100, "inf"]}
#
#                for c in range (len(metBins)):
#                    cutBinX1 = hist.GetXaxis().FindBin(metBins[c][0])
#                    cutBinY1 = hist.GetYaxis().FindBin(metBins[c][0])
#                    if metBins[c][1] != "inf":
#                        cutBinX2 = hist.GetXaxis().FindBin(metBins[c][1]) 
#                        cutBinY2 = hist.GetYaxis().FindBin(metBins[c][1])
#                    elif metBins[c][1] == "inf":
#                        cutBinX2 = hist.GetNbinsX()+1
#                        cutBinY2 = hist.GetNbinsY()+1
#
#                    nReco = hist.Integral(0, hist.GetNbinsX()+1, cutBinY1, cutBinY2)
#                    nGen = hist.Integral(cutBinX1, cutBinX2, 0, hist.GetNbinsY()+1)
#                    nRecoPlusnGen = hist.Integral(cutBinX1, cutBinX2, cutBinY1, cutBinY2)
#
#                    purity = nRecoPlusnGen/nReco
#                    stability = nRecoPlusnGen/nGen
#                    correctionFactor1 = nGen/nReco
#                    correctionFactor2 = purity/stability
#                    
#                    outputFile.write("mettype = " + metType + "\n")
#                    outputFile.write("bin: " + str(metBins[c]) + "\n")
#                    outputFile.write("purity = " + str(purity) + "\n")
#                    outputFile.write("stability = " + str(stability) + "\n")
#                    outputFile.write("correctionFactor1 = nGen/nReco = " + str(correctionFactor1) + "\n")
#                    outputFile.write("correctionFactor2 = purity/stability = " + str(correctionFactor2) + "\n")
#
#                    if metType == "patType1p2CorrectedPFMet":
#                        bJetStart = 55
#                    elif metType == "patType1CorrectedPFMet":
#                        bJetStart = 53
#                    elif metType == "patMETsPFlow":
#                        bJetStart = 43
#
#                    outputFile.write(histFile[bJetStart:] + " nReco = " + str(nReco) + "\n")
#                    outputFile.write(histFile[bJetStart:] + " nGen = " + str(nGen) + "\n")
#                    outputFile.write(histFile[bJetStart:] + " nRecoPlusnGen = " + str(nRecoPlusnGen) + "\n\n")
                
                canvas = TCanvas("canvas", "canvas", 1600, 1200)
                #canvas.SetRightMargin(0.04)
                outputFilename = histFile
                hist.Draw("COLZ")
                title1.Draw()
                title2.Draw()
                print "Saving canvas", path + "/" + metType + "_RecoMET_vs_GenMET_" + bJetBin + ".root"
                canvas.SaveAs(path + "/" + metType + "_RecoMET_vs_GenMET_" + bJetBin + "_withoutMETbinLines.pdf")
                
                lineX1 = TLine(25, 0, 25, 300)
                lineX1.Draw()
                lineX2 = TLine(45, 0, 45, 300)
                lineX2.Draw()
                lineX3 = TLine(70, 0, 70, 300)
                lineX3.Draw()
                lineX4 = TLine(100, 0, 100, 300)
                lineX4.Draw()
                lineY1 = TLine(0, 25, 300, 25)
                lineY1.Draw()
                lineY2 = TLine(0, 45, 300, 45)
                lineY2.Draw()
                lineY3 = TLine(0, 70, 300, 70)
                lineY3.Draw()
                lineY4 = TLine(0, 100, 300, 100)
                lineY4.Draw()
                canvas.SaveAs(path + "/" + metType + "_RecoMET_vs_GenMET_" + bJetBin + "_withMETbinLines.pdf")
