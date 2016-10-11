import numpy as np
from ROOT import TH1, TCanvas, TLine, gDirectory, TObjArray, TColor, TLegend, TAxis, TFile, TObject
from rootpy import asrootpy
from rootpy.io import File
from tools.file_utilities import make_folder_if_not_exists
    

def get_bin_resolution( fine_binned_response , bin_number ):
    '''
    Return the resolution for the reco and gen distributions for each variable in each fine bin
    '''
    gen_resolution = 0
    reco_resolution = 0

    reco_array = TObjArray()
    gen_array = TObjArray()

    # produces 4 TH1D histograms
    # 0 : constant
    # 1 : mean
    # 2 : sigma
    # 3 : chi-squared of it
    gen_slices = fine_binned_response.FitSlicesY(0, bin_number, bin_number, 1, "Q", gen_array)
    # for hist in gen_array:
    #     print (type(hist))
    # print("Gen Sigma : ", gen_array[2].GetBinContent(bin_number))
    # print("Gen Mean : ", gen_array[1].GetBinContent(bin_number))
    # print("Gen Constant : ", gen_array[0].GetBinContent(bin_number))
    gen_resolution = gen_array[2].GetBinContent(bin_number)

    reco_slices = fine_binned_response.FitSlicesX(0, bin_number, bin_number, 1, "Q", reco_array) 
    # for hist in reco_array:
    #     print (type(hist))
    # print("Reco Sigma : ", reco_array[2].GetBinContent(bin_number))
    # print("Reco Mean : ", reco_array[1].GetBinContent(bin_number))
    # print("Reco Constant : ", reco_array[0].GetBinContent(bin_number))
    reco_resolution = reco_array[2].GetBinContent(bin_number)

    # resolution = max(gen_resolution, reco_resolution)
    # return resolution
    return reco_resolution, gen_resolution


def get_merged_bin_resolution(res_file, var, low_bin, high_bin):
    '''
    Return mean value of resolutions in fine bins of the merged bin.
    '''

    bin_contents = []

    f = File( res_file )
    res_hist = f.Get( 'res_r_'+var ).Clone()
    # change scope from file to memory
    res_hist.SetDirectory( 0 )
    f.close()

    low_bin_n = res_hist.GetXaxis().FindBin(low_bin)
    high_bin_n = res_hist.GetXaxis().FindBin(high_bin)

    for bin_i in range(low_bin_n, high_bin_n+1):
        bin_content = res_hist.GetBinContent(bin_i)
        # resolution couldnt be reconstructed (High GeV with low stats)
        # remove these from list of resolutions
        if bin_content == 0 : continue
        bin_contents.append(bin_content)

    # print(bin_contents)
    res = np.mean(bin_contents)
    return res


def generate_resolution_plots(histogram_information, var):
    '''
    Save the reconstructed resolution to root file
    Plot rexonstructed vs generated resolution
    '''

    histograms = [info['hist'] for info in histogram_information]
    first_hist = histograms[0]
    rebin_hist = first_hist.Rebin2D( 10, 10, "rebinned" ) # Make a coarser fine bin - mor stats for fit and saves compute time
    res_r_hist = rebin_hist.ProjectionX().Clone('res_r_'+var) #Initialise resolution plots
    res_g_hist = rebin_hist.ProjectionX().Clone('res_g_'+var)
    res_r_g_bias_hist = rebin_hist.ProjectionX().Clone('res_r_g_bias')

    n_bins = rebin_hist.GetNbinsX()
    for n_bin in range (0, n_bins):
        r_res, g_res = get_bin_resolution(rebin_hist, n_bin)
        res_r_hist.SetBinContent(n_bin, r_res)
        res_g_hist.SetBinContent(n_bin, g_res)
        res_r_hist.SetBinError(n_bin, 0)
        res_g_hist.SetBinError(n_bin, 0)
        res_r_g_bias_hist.SetBinContent(n_bin, r_res-g_res)

    make_folder_if_not_exists('plots/resolutionStudies/')

    # c = TCanvas('c1', 'c1', 800, 600)
    # c.SetLogy()
    # c.SetGrid()
    # # res_r_hist.GetXaxis().SetRangeUser(0, 1500)
    # res_r_hist.SetTitle("Reco(Gen) resolution;"+var+"; Resolution (GeV)")
    # res_r_hist.SetFillColor(3)
    # res_r_hist.SetFillStyle(3003);
    # res_r_hist.Draw("hist")
    # res_g_hist.SetFillColor(2)
    # res_g_hist.SetFillStyle(3003);
    # res_g_hist.Draw("hist same")
    # leg = TLegend(0.1,0.8,0.38,0.9);
    # leg.AddEntry(res_r_hist,"Res of Reco","f")
    # leg.AddEntry(res_g_hist,"Res of Gen","f")
    # leg.Draw()
    # c.Update()
    # c.SaveAs("plots/resolutionStudies/Resolution_"+var+".png")

    # c2 = TCanvas('c2', 'c2', 800, 600)
    # c.SetLogy()
    # c2.SetGrid()
    # res_r_g_bias_hist.SetTitle("Resolution Bias;"+var+"; Reco-Gen Resolution(GeV)")
    # # res_r_g_bias_hist.GetXaxis().SetRangeUser(0, 1500)
    # res_r_g_bias_hist.Draw("hist")
    # leg2 = TLegend(0.75,0.1,0.9,0.2);
    # leg2.AddEntry(res_r_g_bias_hist,"Resolution Bias","f")
    # leg2.Draw()
    # c2.Update()
    # c2.SaveAs("plots/resolutionStudies/ResolutionBias_"+var+".png")


    f = TFile("plots/resolutionStudies/resolution.root", "update")
    res_r_hist.Write(res_r_hist.GetName(),TObject.kOverwrite)
    f.Close()

    return