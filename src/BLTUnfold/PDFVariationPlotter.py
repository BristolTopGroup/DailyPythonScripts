
from config.histogram_colours import histogram_colours as colours
from config import XSectionConfig
from rootpy.plotting import Hist
from tools.ROOT_utils import get_histograms_from_trees, set_root_defaults
from tools.latex import setup_matplotlib
from uncertainties import ufloat
from math import sqrt
from copy import deepcopy
from rootpy.io import File
from rootpy import asrootpy
from ROOT import TCanvas, kRed
# latex, font, etc
setup_matplotlib()


if __name__ == '__main__':
    set_root_defaults()

    measurement_config = XSectionConfig( 13 )
    # # caching of variables for shorter access
    files_for_pdfs = { 'PDFWeights_%d' % (index - 9) : File( measurement_config.unfolding_pdfweights[index] ) for index in range( 9, 109 ) }
    files_central = File( measurement_config.unfolding_powheg_pythia8)

    path_to_unfolding = 'abs_lepton_eta_combined'
    i=0
    canvas = TCanvas("CanvasRef", "CanvasTitle", 800,600)

    folder = files_central.Get(path_to_unfolding)
    h_truth = asrootpy( folder.truthVis.Clone() )
    h_measured = asrootpy( folder.measuredVis_without_fakes.Clone() )
    h_measured.Draw()

    for k,f in files_for_pdfs.iteritems():
        folder = f.Get(path_to_unfolding)

        # folder = inputfile.Get( '%s_%s' % ( variable, channel ) )
        h_truth = asrootpy( folder.truthVis.Clone() )
        h_measured = asrootpy( folder.measuredVis_without_fakes.Clone() )
        h_measured.SetMarkerSize( 0 )
        h_measured.Draw("same")

    folder = files_central.Get(path_to_unfolding)
    h_truth = asrootpy( folder.truthVis.Clone() )
    h_measured = asrootpy( folder.measuredVis_without_fakes.Clone() )
    h_measured.SetMarkerColor( kRed )
    h_measured.Draw("same")

    canvas.Update()
    canvas.SaveAs('PDFvsCentral.pdf')   
    canvas.Close() 


