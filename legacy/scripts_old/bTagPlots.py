from ROOT import *
import HistGetter
import HistPlotter
import inputFiles
from array import*

#outputFormats = ['png', 'pdf']
outputFormats = ['root']
outputFolder = "/storage/phjaj/Plots/"
#print outputFolder
saveAs = HistPlotter.saveAs
algos = ["CombinedSecondaryVertex", "CombinedSecondaryVertexMVA",
         "JetBProbability", "JetProbability",
         "SimpleSecondaryVertexHighEfficiency", "SimpleSecondaryVertexHighPurity",
         "SoftElectronByIP3d", "SoftElectronByPt",
         "SoftMuon", "SoftMuonByIP3d", "SoftMuonByPt", 
         "TrackCountingHighEfficiency", "TrackCountingHighPurity"]
jets=["allJets", "bQuarkJets", "cQuarkJets", "gluonJets", "udsQuarkJets"]

def makeBTagPlots(hists, rebin=1):
   
    #Scaled individual Plots - stage 1
    print 'Plotting individual btag histograms'
    gStyle.SetOptStat(001111111)
    for name, hist in hists.iteritems():
        entries = hist.Integral(0, hist.GetNbinsX() + 1)
        if entries == 0:
            print name
        else:
	    hist.Scale(1.0 / entries)
        canvas = TCanvas("canvas", "canvas", 800, 800)
        hist.GetXaxis().SetTitle("Discriminator Value")
        hist.GetYaxis().SetTitle("Number of Jets")
        hist.Draw()
        outputFilename = name + "_discriminator"
        print "Saving canvas", name
        saveAs(canvas, outputFilename, outputFormats, outputFolder)

    #Scaled combined plots - stage 2
    print 'Plotting combined btag histograms'
    gStyle.SetOptStat(001111111)
    for algo in algos:
        canvas = TCanvas("canvas", "canvas", 800, 800)
        legend = TLegend(0.7, 0.15, 0.85, 0.35)
        jets = ["allJets", "bQuarkJets", "cQuarkJets", "gluonJets", "udsQuarkJets"]
        for jet in jets:
            for name, hist in hists.iteritems():
                #print name
                outputFilename = "BJetAnalysis/" + algo + "_discriminator_combined"
                if name == "BJetAnalysis/" + algo + "_" + jet:
                    #print algo
                    #print jet
                    #print name
                    #print jets.index(jet)
                    hist.SetLineColor(jets.index(jet) + 1)
                    hist.SetTitle(algo + "_discriminator_combined")
                    hist.GetXaxis().SetTitle("Discriminator Value")
                    hist.GetYaxis().SetTitle("Number of Jets")
                    legend.AddEntry(hist, algo + "_" + jet + "_discriminator", "l")
                    if jets.index(jet) == 0:
		        hist.Draw()
                    else:
                        hist.Draw("same")
        legend.Draw()
        print "Saving canvas", outputFilename 
        saveAs(canvas, outputFilename, outputFormats, outputFolder)

def makeEfficiencyPlots():
    #Efficiency Plots - stage 1
    print 'Plotting individual btag efficiencies'
    gStyle.SetOptStat(001111111)
    #loop through root file (and histogram) for each algorithm for each jet type
    
    for algo in algos:
        #for single efficiency plots
        cutValues = array ('f', [])
        efficiencies = array ('f', [])
        graphs1 = []
        
        #for combined efficiency plots
        multiGraph2 = TMultiGraph()
        legend2 = TLegend(0.7, 0.15, 0.85, 0.35)
        
        for jet in jets:
            inputFilename = "/storage/phjaj/Plots/BJetAnalysis/" + algo + "_" + jet + "_discriminator.root" # e.g. csv_disc_bjets.root, csv_disc_cjets.root etc.
            #file = TFile(inputFilename)
            #canvas = file.Get("canvas")
            #hist = canvas.FindObject(algo + "_" + jet + "_discriminator")
            #hist = TH1D(file.canvas.FindObject(algo + "_" + jet))
            print algo + "_" + jet + "_discriminator"
            file = TFile.Open(inputFilename)
#            hist = TH1D(file.canvas.FindObject(algo + "_disc_" + jet))
            hist = TH1D(file.canvas.FindObject(algo + "_" + jet))
            #efficiencyHist = hist.Clone() #clone the original histogram for this particular algorithm for this particular jet

            #loop through bins (cut values)
            entries = hist.Integral(0, hist.GetNbinsX() + 1)
            max = hist.GetNbinsX()
            for bin in range(1, max + 1): #bin 1 to bin 1000 - check!
                #print "bin = ", bin
                efficiency = hist.Integral(bin, max) / entries #integral from bin to max divided by the total
                cutValue = hist.GetXaxis().GetBinLowEdge(bin)
                #print cutValue, efficiency
                efficiencies.append(efficiency)
                cutValues.append(cutValue)
            canvas1 = TCanvas("canvas1", "canvas1", 800, 800)
            #print "efficiencies = ", efficiencies, len(efficiencies)
            #print "cutValues = ", cutValues, len(cutValues)
            print max, len(cutValues), len(efficiencies)
            gr = TGraph(max, cutValues, efficiencies) # - check!            
            outputFilename1 = "BJetAnalysis/" + algo + "_" + jet + "_efficiency"
            gr.SetTitle(algo + "_" + jet + "_efficiency")
            gr.GetXaxis().SetTitle("Discriminator Cut Value")
            gr.GetYaxis().SetTitle("Jet Efficiency")
            gr.SetMarkerColor(jets.index(jet) + 1)
            gr.SetLineColor(jets.index(jet) + 1)
            gr.SetMarkerStyle(33)
            gr.SetMarkerSize(0.75)
            gr.Draw("AP")
            graphs1.append(gr) #Add graph to array to plot all 4 jets on the same canvas later below
            multiGraph2.Add(graphs1[jets.index(jet)])
            #print "multiGraph = ", multiGraph
            legend2.AddEntry(graphs1[jets.index(jet)], algo + "_" + jet + "_efficiency", "l")
            print graphs1
            print "Saving canvas", outputFilename1
            saveAs(canvas1, outputFilename1, outputFormats, outputFolder)
            cutValues = array ('f', [])
            efficiencies = array ('f', [])
            #bJetEfficiencies = array ('f', [])
            #cJetEfficiencies = array ('f', [])
            #gluonJetEfficiencies = array ('f', [])
            #udsJetEfficiencies = array ('f', [])
        canvas2 = TCanvas("canvas1", "canvas1", 800, 800)
        outputFilename2 = "BJetAnalysis/" + algo + "_efficiency_combined"
        multiGraph2.Draw("AP")
        legend2.Draw()
        multiGraph2.SetTitle(algo + "_efficiency_combined")
        multiGraph2.GetXaxis().SetTitle("Discriminator Cut Value")
        multiGraph2.GetYaxis().SetTitle("Jet Efficiency")
        saveAs(canvas2, outputFilename2, outputFormats, outputFolder)


    #plot non-b jet efficiencies against b-jet efficiency for all non-b-jets for each algorithm
    print "Plotting non-b jet efficiency against b-jet efficiency"    
    gStyle.SetOptStat(001111111)
    #loop through root file (and histogram) for each algorithm for each jet type
    bJetEfficiencies = array ('f', [])
    cJetEfficiencies = array ('f', [])
    gluonJetEfficiencies = array ('f', [])
    udsJetEfficiencies = array ('f', [])
    graphs3 = []
    #print graphs1
    for algo in algos:
        print algo
        for jet in jets:
            inputFilename = "/storage/phjaj/Plots/BJetAnalysis/" + algo + "_" + jet + "_efficiency.root" # e.g. csv_disc_bjets.root, csv_disc_cjets.root etc.
            file = TFile.Open(inputFilename)
            
#            gr = file.canvas1.GetPrimitive("Graph")
            gr = TGraph(file.canvas.FindObject(algo + "_" + jet))
#            print "type = ", type(gr)
            #gr.Draw()
#            print algo, " ", jet
            n = gr.GetN()
            yValues = gr.GetY()
            for i in range(n):
                if jet == "bQuarkJets":
                    bJetEfficiencies.append(yValues[i])
                if jet == "cQuarkJets":
                    cJetEfficiencies.append(yValues[i])
                if jet == "gluonJets":
                    gluonJetEfficiencies.append(yValues[i])
                if jet == "udsQuarkJets":
                    udsJetEfficiencies.append(yValues[i])
        legend3 = TLegend(0.7, 0.15, 0.85, 0.35)
        gr1 = TGraph(max, bJetEfficiencies, cJetEfficiencies)
        gr1.SetMarkerColor(jets.index("cQuarkJets") + 1)
        gr1.SetLineColor(jets.index("cQuarkJets") + 1)
        gr1.SetLineWidth(2)
        gr1.SetMarkerStyle(33)
        gr1.SetMarkerSize(0.75)
        legend3.AddEntry(gr1, algo + "cQuarkJets_efficiency", "p")
        gr2 = TGraph(max, bJetEfficiencies, gluonJetEfficiencies)
        gr2.SetMarkerColor(jets.index("gluonJets") + 1)
        gr2.SetLineColor(jets.index("gluonJets") + 1)
        gr2.SetLineWidth(2)
        gr2.SetMarkerStyle(33)
        gr2.SetMarkerSize(0.75)
        legend3.AddEntry(gr2, algo + "gluonJets_efficiency", "p")
        gr3 = TGraph(max, bJetEfficiencies, udsJetEfficiencies)
        gr3.SetMarkerColor(jets.index("udsQuarkJets") + 1)
        gr3.SetLineColor(jets.index("udsQuarkJets") + 1)
        gr3.SetLineWidth(2)
        gr3.SetMarkerStyle(33)
        gr3.SetMarkerSize(0.75)
        legend3.AddEntry(gr3, algo + "udsQuarkJets_efficiency", "p")
        graphs3.append(gr1)
        graphs3.append(gr2)
        graphs3.append(gr3)
        print graphs3
        canvas3 = TCanvas("canvas3", "canvas3", 800, 800)
        multiGraph3 = TMultiGraph()
        for i in range(len(graphs3)):
            print graphs3[i]
            multiGraph3.Add(graphs3[i])
        print multiGraph3
        multiGraph3.Draw("AP")
        legend3.Draw()
        multiGraph3.SetTitle(algo + "_nonBJetEfficiency_v_BJetEfficiency")
        multiGraph3.GetXaxis().SetTitle("B-Jet Efficiency")
        multiGraph3.GetYaxis().SetTitle("Non-B-Jet Efficiency")
        outputFilename3 = "/BJetAnalysis/" + algo + "_nonBJetEfficiency_v_bJetEfficiency"
        saveAs(canvas3, outputFilename3, outputFormats, outputFolder)
        bJetEfficiencies = array ('f', [])
        cJetEfficiencies = array ('f', [])
        gluonJetEfficiencies = array ('f', [])
        udsJetEfficiencies = array ('f', [])
        graphs3 = []

    #plot uds jet efficiencies against b-jet efficiency for all algorithms
    print "Plotting non-b jet efficiency against b-jet efficiency"    
    gStyle.SetOptStat(001111111)
    #loop through root file (and histogram) for each algorithm for each jet type
    
    bJetEfficiencies = {}
    udsJetEfficiencies = {}

    graphs4 = []
    #print graphs1
    for algo in algos:
        print algo
        for jet in jets:
            inputFilename = "/storage/phjaj/Plots/BJetAnalysis/" + algo + "_" + jet + "_efficiency.root" # e.g. csv_disc_bjets.root, csv_disc_cjets.root etc.
            file = TFile.Open(inputFilename)
            gr = file.canvas1.GetPrimitive("Graph")
            print "type = ", type(gr)
            #gr.Draw()
            print algo, " ", jet
            n = gr.GetN()
            yValues = gr.GetY()

            b = array('f', [])
            uds = array('f', [])

            for i in range(n):
                if jet == "bQuarkJets":
                    b.append(yValues[i])
                if jet == "udsQuarkJets":
                    uds.append(yValues[i])
            if b:
                bJetEfficiencies[algo] = b
            if uds:
                udsJetEfficiencies[algo] = uds
        legend4 = TLegend(0.7, 0.15, 0.85, 0.35)
        print len(bJetEfficiencies[algo])
        print len(udsJetEfficiencies[algo])

        gr = TGraph(max, bJetEfficiencies[algo], udsJetEfficiencies[algo])
        
        gr.SetMarkerColor(algos.index(algo) + 1)
        #gr.SetLineColor(algos.index(algo) + 1)
        #gr.SetLineWidth(2)
        gr.SetMarkerStyle(algos.index(algo) + 20)
        gr.SetMarkerSize(0.75)
        graphs4.append(gr)        
        #print graphs4
    canvas4 = TCanvas("canvas4", "canvas4", 800, 800)
    multiGraph4 = TMultiGraph()
    for i in range(len(graphs4)):
        #print graphs4[i]
        multiGraph4.Add(graphs4[i])
        legend4.AddEntry(graphs4[i], algos[i] + "_efficiency", "p")
    #print multiGraph4
    multiGraph4.Draw("AP")
    legend4.Draw()
    multiGraph4.SetTitle("UDS-JetEfficiency_v_B-JetEfficiency")
    multiGraph4.GetXaxis().SetTitle("B-Jet Efficiency")
    multiGraph4.GetYaxis().SetTitle("UDS-Jet Efficiency")
    outputFilename4 = "/BJetAnalysis/udsJetEfficiency_v_bJetEfficiency"
    print "Saving canvas", outputFilename4
    saveAs(canvas4, outputFilename4, outputFormats, outputFolder)

    
def setStyles(dataPlot, mcPlot):
    mcPlot.SetLineColor(2)
    mcPlot.SetMarkerColor(2)
    mcPlot.SetMarkerStyle(22)
    
def getLegend(dataPlot, mcPlot):
    leg = TLegend(0.7, 0.2, 0.8, 0.3)
    leg.SetBorderSize(0);
    leg.SetLineStyle(0);
    leg.SetTextFont(42);
    leg.SetFillStyle(0);
    leg.AddEntry(dataPlot, 'data', 'P')
    leg.AddEntry(mcPlot, 'MC', 'P')
    return leg

def getCaption():
    tex = TLatex(0.18, 1, "CMS Preliminary 2011,  #sqrt{s} = 7 TeV, L = 4.69 fb^{-1}");
    tex.SetNDC();
    tex.SetTextAlign(13);
    tex.SetTextFont(42);
    tex.SetTextSize(0.04);
    tex.SetLineWidth(2);
    return tex

if __name__ == '__main__':
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 5001;')
    
    files = inputFiles.files

    histNames = [
                'BJetAnalysis/CombinedSecondaryVertex_allJets',
		'BJetAnalysis/CombinedSecondaryVertex_bQuarkJets',
		'BJetAnalysis/CombinedSecondaryVertex_cQuarkJets',
		'BJetAnalysis/CombinedSecondaryVertex_gluonJets',
		'BJetAnalysis/CombinedSecondaryVertex_udsQuarkJets',
		'BJetAnalysis/CombinedSecondaryVertexMVA_allJets',
		'BJetAnalysis/CombinedSecondaryVertexMVA_bQuarkJets',
		'BJetAnalysis/CombinedSecondaryVertexMVA_cQuarkJets',
		'BJetAnalysis/CombinedSecondaryVertexMVA_gluonJets',
		'BJetAnalysis/CombinedSecondaryVertexMVA_udsQuarkJets',
		'BJetAnalysis/JetBProbability_allJets',
		'BJetAnalysis/JetBProbability_bQuarkJets',
		'BJetAnalysis/JetBProbability_cQuarkJets',
		'BJetAnalysis/JetBProbability_gluonJets',
		'BJetAnalysis/JetBProbability_udsQuarkJets',
		'BJetAnalysis/JetProbability_allJets',
		'BJetAnalysis/JetProbability_bQuarkJets',
		'BJetAnalysis/JetProbability_cQuarkJets',
		'BJetAnalysis/JetProbability_gluonJets',
		'BJetAnalysis/JetProbability_udsQuarkJets',
		'BJetAnalysis/SimpleSecondaryVertexHighEfficiency_allJets',
		'BJetAnalysis/SimpleSecondaryVertexHighEfficiency_bQuarkJets',
		'BJetAnalysis/SimpleSecondaryVertexHighEfficiency_cQuarkJets',
		'BJetAnalysis/SimpleSecondaryVertexHighEfficiency_gluonJets',
		'BJetAnalysis/SimpleSecondaryVertexHighEfficiency_udsQuarkJets',
		'BJetAnalysis/SimpleSecondaryVertexHighPurity_allJets',
		'BJetAnalysis/SimpleSecondaryVertexHighPurity_bQuarkJets',
		'BJetAnalysis/SimpleSecondaryVertexHighPurity_cQuarkJets',
		'BJetAnalysis/SimpleSecondaryVertexHighPurity_gluonJets',
		'BJetAnalysis/SimpleSecondaryVertexHighPurity_udsQuarkJets',
		'BJetAnalysis/SoftElectronByIP3d_allJets',
		'BJetAnalysis/SoftElectronByIP3d_bQuarkJets',
		'BJetAnalysis/SoftElectronByIP3d_cQuarkJets',
		'BJetAnalysis/SoftElectronByIP3d_gluonJets',
		'BJetAnalysis/SoftElectronByIP3d_udsQuarkJets',
		'BJetAnalysis/SoftElectronByPt_allJets',
		'BJetAnalysis/SoftElectronByPt_bQuarkJets',
		'BJetAnalysis/SoftElectronByPt_cQuarkJets',
		'BJetAnalysis/SoftElectronByPt_gluonJets',
		'BJetAnalysis/SoftElectronByPt_udsjets',
		'BJetAnalysis/SoftMuon_allJets',
		'BJetAnalysis/SoftMuon_bQuarkJets',
		'BJetAnalysis/SoftMuon_cQuarkJets',
		'BJetAnalysis/SoftMuon_gluonJets',
		'BJetAnalysis/SoftMuon_udsQuarkJets',
		'BJetAnalysis/SoftMuonByIP3d_allJets',
		'BJetAnalysis/SoftMuonByIP3d_bQuarkJets',
		'BJetAnalysis/SoftMuonByIP3d_cQuarkJets',
		'BJetAnalysis/SoftMuonByIP3d_gluonJets',
		'BJetAnalysis/SoftMuonByIP3d_udsQuarkJets',
		'BJetAnalysis/SoftMuonByPt_allJets',
		'BJetAnalysis/SoftMuonByPt_bQuarkJets',
		'BJetAnalysis/SoftMuonByPt_cQuarkJets',
		'BJetAnalysis/SoftMuonByPt_gluonJets',
		'BJetAnalysis/SoftMuonByPt_udsQuarkJets',
		'BJetAnalysis/TrackCountingHighEfficiency_allJets',
		'BJetAnalysis/TrackCountingHighEfficiency_bQuarkJets',
		'BJetAnalysis/TrackCountingHighEfficiency_cQuarkJets',
		'BJetAnalysis/TrackCountingHighEfficiency_gluonJets',
		'BJetAnalysis/TrackCountingHighEfficiency_udsQuarkJets',
		'BJetAnalysis/TrackCountingHighPurity_allJets',
		'BJetAnalysis/TrackCountingHighPurity_bQuarkJets',
		'BJetAnalysis/TrackCountingHighPurity_cQuarkJets',
		'BJetAnalysis/TrackCountingHighPurity_gluonJets',
		'BJetAnalysis/TrackCountingHighPurity_udsQuarkJets',
                ]        


    bTagFiles = {}
    
    #bTagFiles['data'] = inputFiles.files['data']
    bTagFiles['ttbar'] = '/storage/results/histogramfiles/TTJet_50000pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'

    #histNames = ['BJetAnalysis/' + histName for histName in histNames]
    HistPlotter.setStyle()
    hists = HistGetter.getHistsFromFiles(histNames, bTagFiles) #returns a dictionary of form {histname:hist}
    makeBTagPlots(hists['ttbar'])
    makeEfficiencyPlots()
