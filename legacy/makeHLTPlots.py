from ROOT import *
import HistGetter
import HistPlotter
import inputFiles

outputFormats = ['png', 'pdf']
outputFolder = '/storage/results/plots/ElectronHad/'
saveAs = HistPlotter.saveAs

triggers = [
#            'HLT_Ele25_CaloIdVT_TrkIdT_CentralJet30',
#            'HLT_Ele25_CaloIdVT_TrkIdT_DiCentralJet30',
                'HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30',
#                'HLT_Ele25_CaloIdVT_TrkIdT_QuadCentralJet30',
#                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralJet30', 
#                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_DiCentralJet30',
                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30',
#                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFJet30',
#                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_QuadCentralJet30'
                ]
    
triggerVariables = ['jet_pt',
                    'jet_eta',
                    'jet_phi',
                    'jet_eta_PtGT45',
                    'jet_phi_PtGT45']
triggerModifiers = ['visited', 'fired']
    
def makeHLTPlots(hists, rebin=1):
    print 'Making HLT plots'
    data = hists['data']
    ttbar = hists['ttbar']
    
    plots = ['HLTStudy/' + trigger + '/' + variable for trigger in triggers for variable in triggerVariables]
    efficiency = {}
    mc_efficiency = {}
    
    for jetbin in HistPlotter.allJetBins:
        for plot in plots: #make all plots
            if 'Quad' in plot and not '4' in jetbin:#only >=4 jet bin for QuadJet trigger
                continue
            
            elif 'Tri' in plot and ((not '3' in jetbin and not '4' in jetbin) or '3orMoreJets' in jetbin):
                #only ==3, >=4 jet bins for TriJet trigger
                continue
            elif 'Di' in plot and not '2' in jetbin:
                    continue
                
            print plot + '_' + jetbin
            
            fired = data[plot + '_' + 'fired_' + jetbin]
            visited = data[plot + '_' + 'visited_' + jetbin]
            mc_fired = ttbar[plot + '_' + 'fired_' + jetbin]
            mc_visited = ttbar[plot + '_' + 'visited_' + jetbin]
            # calculate the sum of weights for correct error calculation
            #http://root.cern.ch/root/html/TH1.html#TH1:Sumw2
            fired.Sumw2()
            visited.Sumw2()
            mc_fired.Sumw2()
            mc_visited.Sumw2()
            
            xlimits, xTitle, yTitle, fitfunction, fitRange = getParams(plot, rebin)
            
            fired.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
            visited.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
            mc_fired.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
            mc_visited.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
            
            fired.Rebin(rebin)
            visited.Rebin(rebin)
            mc_fired.Rebin(rebin)
            mc_visited.Rebin(rebin)
            
            efficiency[plot + jetbin] = TEfficiency(fired, visited)
            mc_efficiency[plot + jetbin] = TEfficiency(mc_fired, mc_visited)
            eff = efficiency[plot + jetbin].Clone("Copy")
            mceff = mc_efficiency[plot + jetbin].Clone("CopyMC")
            setStyles(eff, mceff)
            
            saveName = plot + '_' + 'efficiency'
            saveName = saveName.replace('Jet30/', 'Jet30_')
            
            legend = getLegend(eff, mceff)
            caption = getCaption()
            
            c = TCanvas("cname" + plot + jetbin, 'cname', 900, 900)
            eff.Draw('P0')
            mceff.Draw('SAMEP0')
            legend.Draw('same')
            caption.Draw('same')
            saveAs(c, saveName + '_' + jetbin, outputFolder = outputFolder)
            
def getParams(plot, rebin):
    xlimits = [10,200]
    xTitle = 'jet p_{T} (GeV)'
    yTitle = 'efficiency/(GeV)'
    fitfunction = ''
    fitRange = [-9999, 9999]
    if 'jet_pt' in plot:
        xlimits = [10,200]
        xTitle = 'jet p_{T} (GeV)'
        yTitle = 'efficiency/(%d GeV)' % (1*rebin)
        fitfunction = "[0]*exp([1]*exp([2]*x))"
        fitRange = [20,200]
    elif 'jet_eta' in plot:
        xlimits = [-3,3]
        xTitle = 'jet #eta (GeV)'
        yTitle = 'efficiency/(%0.1f)' % (0.1*rebin)
        fitfunction = 'pol2'
        fitRange = [-3,3]
    elif 'jet_phi' in plot:
        xlimits = [-4.,4.]
        xTitle = 'jet #phi (GeV)'
        yTitle = 'efficiency/(%0.1f)' % (0.1*rebin)
        fitfunction = 'pol0'
        fitRange = [-3.1,3.1]
    return xlimits, xTitle, yTitle, fitfunction, fitRange
    
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
    tex = TLatex(0.18,1,"CMS Preliminary 2011,  #sqrt{s} = 7 TeV, L = 4.69 fb^{-1}");
    tex.SetNDC();
    tex.SetTextAlign(13);
    tex.SetTextFont(42);
    tex.SetTextSize(0.04);
    tex.SetLineWidth(2);
    return tex

if __name__ == '__main__':
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    
    files = inputFiles.files
    
    hltFiles = {}
    
    hltFiles['data'] = inputFiles.files['data']
    hltFiles['ttbar'] = inputFiles.files['ttbar']

    triggerPlots = ['HLTStudy/' + trigger + '/' + variable + '_' + modifier for trigger in triggers for variable in triggerVariables for modifier in triggerModifiers]
    HistPlotter.setStyle()
    hists = HistGetter.getHistsFromFiles(triggerPlots, hltFiles, jetBins=HistPlotter.allJetBins)
    makeHLTPlots(hists)
