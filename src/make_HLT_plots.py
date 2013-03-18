from rootpy.io import File
from rootpy.plotting import Canvas
from rootpy import asrootpy
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
#import config.summations as summations
from ROOT import gROOT, TEfficiency, TGraphAsymmErrors, TF1
from array import array
from config import CMS
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
# def makeHLTPlots(hists, triggerPlots, rebin=1):
#    print 'Making HLT plots'
#    data = hists['data']
#    ttbar = hists['ttbar']
#    
#    plots = triggerPlots
#    efficiency = {}
#    mc_efficiency = {}
#    
#    for jetbin in all_jet_bins:
#        for plot in plots: #make all plots
#            if 'Quad' in plot and not '4' in jetbin:#only >=4 jet bin for QuadJet trigger
#                continue
#            
#            elif 'Tri' in plot and ((not '3' in jetbin and not '4' in jetbin) or '3orMoreJets' in jetbin):
#                #only ==3, >=4 jet bins for TriJet trigger
#                continue
#            elif 'Di' in plot and not '2' in jetbin:
#                    continue
#                
#            print plot + '_' + jetbin
#            
#            fired = data[plot + '_' + 'fired_' + jetbin]
#            visited = data[plot + '_' + 'visited_' + jetbin]
#            mc_fired = ttbar[plot + '_' + 'fired_' + jetbin]
#            mc_visited = ttbar[plot + '_' + 'visited_' + jetbin]
#            # calculate the sum of weights for correct error calculation
#            #http://root.cern.ch/root/html/TH1.html#TH1:Sumw2
# #            fired.Sumw2()
# #            visited.Sumw2()
# #            mc_fired.Sumw2()
# #            mc_visited.Sumw2()
#            
#            xlimits, xTitle, yTitle, fitfunction, fitRange = getParams(plot, rebin)
#            
#            fired.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
#            visited.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
#            mc_fired.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
#            mc_visited.GetXaxis().SetRangeUser(xlimits[0], xlimits[1])
#            
#            fired.Rebin(rebin)
#            visited.Rebin(rebin)
#            mc_fired.Rebin(rebin)
#            mc_visited.Rebin(rebin)
#            
#            efficiency[plot + jetbin] = TEfficiency(fired, visited)
#            mc_efficiency[plot + jetbin] = TEfficiency(mc_fired, mc_visited)
#            eff = efficiency[plot + jetbin].Clone("Copy")
#            mceff = mc_efficiency[plot + jetbin].Clone("CopyMC")
#            setStyles(eff, mceff)
#            
#            saveName = plot + '_' + 'efficiency'
#            saveName = saveName.replace('Jet30/', 'Jet30_')
#            
#            legend = getLegend(eff, mceff)
#            caption = getCaption()
#            
#            c = TCanvas("cname" + plot + jetbin, 'cname', 900, 900)
#            eff.Draw('P0')
#            mceff.Draw('SAMEP0')
#            legend.Draw('same')
#            caption.Draw('same')
#            saveAs(c, saveName + '_' + jetbin, outputFolder = outputFolder)
            
def make_efficiency_plot(pass_data, pass_mc, total_data, total_mc, name):
    pass_data.Sumw2()
    total_data.Sumw2()
    pass_mc.Sumw2()
    total_mc.Sumw2()
    bin_edges = [0, 20, 25, 35, 45, 70, 100, 200]
    n_bins = len(bin_edges) - 1
    bin_edge_array = array('d', bin_edges)
    
    pass_data = asrootpy(pass_data.Rebin(n_bins, 'truth', bin_edge_array))
    total_data = asrootpy(total_data.Rebin(n_bins, 'truth', bin_edge_array))
    pass_mc = asrootpy(pass_mc.Rebin(n_bins, 'truth', bin_edge_array))
    total_mc = asrootpy(total_mc.Rebin(n_bins, 'truth', bin_edge_array))
    
    efficiency_data = asrootpy(TGraphAsymmErrors())  # Efficiency(fired_data, visited_data)
    efficiency_mc = asrootpy(TGraphAsymmErrors())  # TEfficiency(fired_mc, visited_mc)
    
    efficiency_data.Divide(pass_data, total_data, "cl=0.683 b(1,1) mode")
    efficiency_mc.Divide(pass_mc, total_mc, "cl=0.683 b(1,1) mode")
    
    scale_factor = pass_data.Clone("pass_mc")
    scale_factor.Multiply(total_mc)
    scale_factor.Divide(total_data)
    scale_factor.Divide(pass_mc)
    scale_factor.linecolor = 'green'
    scale_factor.linewidth = 6
    scale_factor.SetMarkerSize(3)
    scale_factor.SetMarkerColor('green')
    
    fit_function = "[0]*exp([1]*exp([2]*x))"
    fit_range = [20,200]
    f1= asrootpy(TF1("f1",fit_function,fit_range[0],fit_range[1]))
    f1.SetParLimits(0,0.8,1.0);
    f1.SetParLimits(1,-100,-1);
    f1.SetParLimits(2,-1,-0.01);
    efficiency_data.Fit(f1)
    setStyles(efficiency_data, efficiency_mc)
    
    saveName = name 
    saveName = saveName.replace('Jet30/', 'Jet30_')
    
#    legend = getLegend(eff, mceff)
#    caption = getCaption()
    c = Canvas(900, 900)
    setStyles(total_data, pass_data)
    total_data.Draw()
    pass_data.Draw('same')
    
    c.SaveAs(outputFolder + saveName + '_data.png')
    
    c = Canvas(900, 900)
    total_mc.Draw()
    pass_mc.Draw('same')
    setStyles(pass_mc, total_mc)
    c.SaveAs(outputFolder + saveName + '_ttbar.png')
    
    c = Canvas(900, 900)
    efficiency_data.Draw('AP0')
    efficiency_mc.Draw('SAMEP0')
#    legend.Draw('same')
#    caption.Draw('same')
    c.SaveAs(outputFolder + saveName + '_efficiency.png')
    
    # plot with matplotlib
    plt.figure(figsize=(16, 12), dpi=200, facecolor='white')
    gs = gridspec.GridSpec(2, 1, height_ratios=[5,1]) 
    axes = plt.axes()
#    axes = plt.axes([0.15, 0.15, 0.8, 0.8])

    ax0 = plt.subplot(gs[0])
    ax0.minorticks_on()
    ax0.grid(True, 'major', linewidth=2)
    ax0.grid(True, 'minor')
    rplt.errorbar(efficiency_data,  xerr=True, emptybins=True, axes=ax0)
    rplt.errorbar(efficiency_mc, xerr=False, emptybins=True, axes=ax0)
    import numpy
    x = numpy.linspace( f1.GetXmin(), f1.GetXmax(), f1.GetNpx() )
    f1.Eval, x
    from numpy import frompyfunc
    fun = frompyfunc( f1.Eval, 1, 1 )
    from pylab import plot
    
    plot( x, fun(x), axes = ax0)

    ax0.set_xlim([0,200])
    
    plt.xlabel('$p_{\mathrm{T}}$(jet)', CMS.x_axis_title)
    plt.ylabel('Efficiency', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title(r'e+jets, CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV', CMS.title)
#    plt.xlabel('Mass', position=(1., 0.), ha='right')
#    plt.ylabel('Events', position=(0., 1.), va='top')
    plt.legend(['data', r'$\mathrm{t}\bar{\mathrm{t}}$ MC'], numpoints=1, loc='center right', prop={'size':32})
    ax1 = plt.subplot(gs[1])
    ax1.minorticks_on()
    ax1.grid(True, 'major', linewidth=2)
    ax1.grid(True, 'minor')
#    yloc = plt.MaxNLocator(4)
    ax1.yaxis.set_major_locator(MultipleLocator(1.))
    ax1.yaxis.set_minor_locator(MultipleLocator(0.5))
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.xlabel('$p_{\mathrm{T}}$(jet)', CMS.x_axis_title)
    plt.ylabel('data/MC', CMS.y_axis_title)
    rplt.errorbar(scale_factor,  xerr=True, emptybins=False, axes=ax1)
    plt.tight_layout()
    plt.savefig(outputFolder + saveName + '_efficiency_matplot.png')  
          
def getParams(plot, rebin):
    xlimits = [10, 200]
    xTitle = 'jet p_{T} (GeV)'
    yTitle = 'efficiency/(GeV)'
    fitfunction = ''
    fitRange = [-9999, 9999]
    if 'jet_pt' in plot:
        xlimits = [10, 200]
        xTitle = 'jet p_{T} (GeV)'
        yTitle = 'efficiency/(%d GeV)' % (1 * rebin)
        fitfunction = "[0]*exp([1]*exp([2]*x))"
        fitRange = [20, 200]
    elif 'jet_eta' in plot:
        xlimits = [-3, 3]
        xTitle = 'jet #eta (GeV)'
        yTitle = 'efficiency/(%0.1f)' % (0.1 * rebin)
        fitfunction = 'pol2'
        fitRange = [-3, 3]
    elif 'jet_phi' in plot:
        xlimits = [-4., 4.]
        xTitle = 'jet #phi (GeV)'
        yTitle = 'efficiency/(%0.1f)' % (0.1 * rebin)
        fitfunction = 'pol0'
        fitRange = [-3.1, 3.1]
    return xlimits, xTitle, yTitle, fitfunction, fitRange
    
def setStyles(dataPlot, mcPlot):
    mcPlot.SetLineColor(2)
    mcPlot.SetMarkerColor(2)
    mcPlot.SetMarkerStyle(22)
    mcPlot.SetLineWidth(6)
    mcPlot.SetMarkerSize(3)
    dataPlot.SetMarkerSize(3)
    
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
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    
    outputFormats = ['png', 'pdf']
    outputFolder = '/storage/TopQuarkGroup/results/plots/Trigger/'
    
    triggers = ['HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30',
#                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30',
#                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFJet30',
                    ]
        
    triggerVariables = ['jet_pt',
#                        'jet_eta',
#                        'jet_phi',
#                        'jet_eta_PtGT45',
#                        'jet_phi_PtGT45'
                        ]
    triggerModifiers = ['visited', 'fired']
    
    hltFiles = {}
    
    hltFiles['data'] = '/storage/TopQuarkGroup/results/histogramfiles/HLT_V1/ElectronHad_4692.36pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    hltFiles['ttbar'] = '/storage/TopQuarkGroup/results/histogramfiles/HLT_V1/TTJetsFall11_4692.36pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    
    triggerPlots = ['HLTStudy/' + trigger + '/' + variable + '_' + modifier for trigger in triggers for variable in triggerVariables for modifier in triggerModifiers]
    data_file = File(hltFiles['data'])
    ttbar_file = File(hltFiles['ttbar'])
    plot = triggerPlots[0]
    plot_data_visited = data_file.Get('HLTStudy/HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30/jet_pt_visited_3jets')
    plot_data_fired = data_file.Get('HLTStudy/HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30/jet_pt_fired_3jets')
    plot_ttbar_visited = ttbar_file.Get('HLTStudy/HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30/jet_pt_visited_3jets')
    plot_ttbar_fired = ttbar_file.Get('HLTStudy/HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30/jet_pt_fired_3jets')
    
    plot_data_visited.Sumw2()
    plot_data_fired.Sumw2()
    plot_ttbar_visited.Sumw2()
    plot_ttbar_fired.Sumw2()
    
#    plot_data_visited.Rebin(5)
#    plot_data_fired.Rebin(5)
#    plot_ttbar_visited.Rebin(5)
#    plot_ttbar_fired.Rebin(5)
    plot_data_visited.GetXaxis().SetRangeUser(10, 200)
    plot_data_fired.GetXaxis().SetRangeUser(10, 200)
    plot_ttbar_visited.GetXaxis().SetRangeUser(10, 200)
    plot_ttbar_fired.GetXaxis().SetRangeUser(10, 200)
    make_efficiency_plot(plot_data_fired, plot_ttbar_fired, plot_data_visited, plot_ttbar_visited, 'test')
#    HistPlotter.setStyle()
#    hists = HistGetter.getHistsFromFiles(triggerPlots, hltFiles, jetBins=HistPlotter.allJetBins)
#    makeHLTPlots(hists, triggerPlots)
    
