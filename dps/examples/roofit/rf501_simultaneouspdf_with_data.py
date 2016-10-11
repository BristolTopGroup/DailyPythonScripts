#####################################
#
# 'ORGANIZATION AND SIMULTANEOUS FITS' RooFit tutorial macro #501
# 
# Using simultaneous p.d.f.s to describe simultaneous fits to multiple
# datasets
#
#
#
# 07/2008 - Wouter Verkerke 
# 
####################################/

# ifndef __CINT__
# include "RooGlobalFunc.h"
# endif
# include "RooRealVar.h"
# include "RooDataSet.h"
# include "RooGaussian.h"
# include "RooConstVar.h"
# include "RooChebychev.h"
# include "RooAddPdf.h"
# include "RooSimultaneous.h"
# include "RooCategory.h"
# include "TCanvas.h"
# include "TAxis.h"
# include "RooPlot.h"
from ROOT import RooFit, RooRealVar, RooGaussian, RooChebychev, RooAddPdf, \
RooArgList, RooArgSet, RooDataSet, RooCategory, RooPlot, TCanvas, gPad, \
RooSimultaneous, kDashed, RooDataHist

import numpy as np
from rootpy.plotting import Hist
import rootpy.stl as stl
MapStrRootPtr = stl.map(stl.string, "TH1*")
StrHist = stl.pair(stl.string, "TH1*")

def get_data():
    N_bkg1_ctl = 10000
    N_signal_ctl = 2000
    N_bkg1_obs = 1000
    N_signal_obs = 200
    mu1, mu2, sigma1, sigma2 = 100, 140, 15, 5
    x1_ctl = mu1 + sigma1 * np.random.randn( N_bkg1_ctl )
    x2_ctl = mu2 + sigma2 * np.random.randn( N_signal_ctl )
    x1_obs = mu1 + sigma1 * np.random.randn( N_bkg1_obs )
    x2_obs = mu2 + sigma2 * np.random.randn( N_signal_obs )
    
    h1 = Hist( 100, 40, 200, title = 'data' )
    h2 = Hist( 100, 40, 200, title = 'data_ctl' )
    
    # fill the histograms with our distributions
    map( h1.Fill, x1_obs )
    map( h1.Fill, x2_obs )
    map( h2.Fill, x1_ctl )
    map( h2.Fill, x2_ctl )
    
    return h1, h2

def rf501_simultaneouspdf():
    # C r e a t e   m o d e l   f o r   p h y s i c s   s a m p l e
    # -------------------------------------------------------------

    # Create observables
    x = RooRealVar( "x", "x", 40, 200 ) 

    # Construct signal pdf
    mean = RooRealVar( "mean", "mean", 140, 40, 200 ) 
    sigma = RooRealVar( "sigma", "sigma", 5, 0.1, 10 ) 
    gx = RooGaussian( "gx", "gx", x, mean, sigma ) 

    # Construct background pdf
    mean_bkg = RooRealVar( "mean_bkg", "mean_bkg", 100, 40, 200 ) 
    sigma_bkg = RooRealVar( "sigma_bkg", "sigma_bkg", 15, 0.1, 20 ) 
    px = RooGaussian( "px", "px", x, mean_bkg, sigma_bkg ) 

    # Construct composite pdf
    f = RooRealVar( "f", "f", 0.2, 0., 20. ) 
    model = RooAddPdf( "model", "model", RooArgList( gx, px ), RooArgList( f ) ) 



    # C r e a t e   m o d e l   f o r   c o n t r o l   s a m p l e
    # --------------------------------------------------------------

    # Construct signal pdf. 
    # NOTE that sigma is shared with the signal sample model
    mean_ctl = RooRealVar( "mean_ctl", "mean_ctl", 140, 40, 200 ) 
    gx_ctl = RooGaussian( "gx_ctl", "gx_ctl", x, mean_ctl, sigma ) 

    # Construct the background pdf
    mean_bkg_ctl = RooRealVar( "mean_bkg_ctl", "mean_bkg_ctl", 100, 40, 200 ) 
    sigma_bkg_ctl = RooRealVar( "sigma_bkg_ctl", "sigma_bkg_ctl", 15, 0.1, 20 ) 
    px_ctl = RooGaussian( "px_ctl", "px_ctl", x, mean_bkg_ctl, sigma_bkg_ctl ) 

    # Construct the composite model
    f_ctl = RooRealVar( "f_ctl", "f_ctl", 0.5, 0., 20. ) 
    model_ctl = RooAddPdf( "model_ctl", "model_ctl", RooArgList( gx_ctl, px_ctl ),
                           RooArgList( f_ctl ) ) 
    


    # G e t   e v e n t s   f o r   b o t h   s a m p l e s 
    # ---------------------------------------------------------------
    real_data, real_data_ctl = get_data()
    input_hists = MapStrRootPtr()
    input_hists.insert(StrHist("physics", real_data))
    input_hists.insert(StrHist("control", real_data_ctl ))

    # C r e a t e   i n d e x   c a t e g o r y   a n d   j o i n   s a m p l e s 
    # ---------------------------------------------------------------------------
    # Define category to distinguish physics and control samples events
    sample = RooCategory( "sample", "sample" ) 
    sample.defineType( "physics" ) 
    sample.defineType( "control" ) 

    # Construct combined dataset in (x,sample)
    combData = RooDataHist("combData", "combined data", RooArgList( x ), sample ,
                           input_hists)


    # C o n s t r u c t   a   s i m u l t a n e o u s   p d f   i n   ( x , s a m p l e )
    # -----------------------------------------------------------------------------------

    # Construct a simultaneous pdf using category sample as index
    simPdf = RooSimultaneous( "simPdf", "simultaneous pdf", sample ) 

    # Associate model with the physics state and model_ctl with the control state
    simPdf.addPdf( model, "physics" ) 
    simPdf.addPdf( model_ctl, "control" ) 



    # P e r f o r m   a   s i m u l t a n e o u s   f i t
    # ---------------------------------------------------

    # Perform simultaneous fit of model to data and model_ctl to data_ctl
    simPdf.fitTo( combData ) 



    # P l o t   m o d e l   s l i c e s   o n   d a t a    s l i c e s 
    # ----------------------------------------------------------------

    # Make a frame for the physics sample
    frame1 = x.frame( RooFit.Bins( 30 ), RooFit.Title( "Physics sample" ) ) 

    # Plot all data tagged as physics sample
    combData.plotOn( frame1, RooFit.Cut( "sample==sample::physics" ) ) 

    # Plot "physics" slice of simultaneous pdf. 
    # NBL You _must_ project the sample index category with data using ProjWData 
    # as a RooSimultaneous makes no prediction on the shape in the index category 
    # and can thus not be integrated
    simPdf.plotOn( frame1, RooFit.Slice( sample, "physics" ),
                   RooFit.ProjWData( RooArgSet( sample ), combData ) ) 
    simPdf.plotOn( frame1, RooFit.Slice( sample, "physics" ),
                   RooFit.Components( "px" ),
                   RooFit.ProjWData( RooArgSet( sample ), combData ),
                   RooFit.LineStyle( kDashed ) ) 

    # The same plot for the control sample slice
    frame2 = x.frame( RooFit.Bins( 30 ), RooFit.Title( "Control sample" ) ) 
    combData.plotOn( frame2, RooFit.Cut( "sample==sample::control" ) ) 
    simPdf.plotOn( frame2, RooFit.Slice( sample, "control" ),
                  RooFit.ProjWData( RooArgSet( sample ), combData ) ) 
    simPdf.plotOn( frame2, RooFit.Slice( sample, "control" ),
                  RooFit.Components( "px_ctl" ),
                  RooFit.ProjWData( RooArgSet( sample ), combData ),
                  RooFit.LineStyle( kDashed ) ) 



    c = TCanvas( "rf501_simultaneouspdf", "rf403_simultaneouspdf", 800, 400 ) 
    c.Divide( 2 ) 
    c.cd( 1 )
    gPad.SetLeftMargin( 0.15 )
    frame1.GetYaxis().SetTitleOffset( 1.4 )
    frame1.Draw() 
    c.cd( 2 )
    gPad.SetLeftMargin( 0.15 )
    frame2.GetYaxis().SetTitleOffset( 1.4 )
    frame2.Draw() 
    raw_input()

if __name__ == '__main__':
    rf501_simultaneouspdf()

