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
RooSimultaneous, kDashed

def rf501_simultaneouspdf():
    # C r e a t e   m o d e l   f o r   p h y s i c s   s a m p l e
    # -------------------------------------------------------------

    # Create observables
    x = RooRealVar( "x", "x", -8, 8 ) 

    # Construct signal pdf
    mean = RooRealVar( "mean", "mean", 0, -8, 8 ) 
    sigma = RooRealVar( "sigma", "sigma", 0.3, 0.1, 10 ) 
    gx = RooGaussian( "gx", "gx", x, mean, sigma ) 

    # Construct background pdf
    a0 = RooRealVar( "a0", "a0", -0.1, -1, 1 ) 
    a1 = RooRealVar( "a1", "a1", 0.004, -1, 1 ) 
    px = RooChebychev( "px", "px", x, RooArgList( a0, a1 ) ) 

    # Construct composite pdf
    f = RooRealVar( "f", "f", 0.2, 0., 1. ) 
    model = RooAddPdf( "model", "model", RooArgList( gx, px ), RooArgList( f ) ) 



    # C r e a t e   m o d e l   f o r   c o n t r o l   s a m p l e
    # --------------------------------------------------------------

    # Construct signal pdf. 
    # NOTE that sigma is shared with the signal sample model
    mean_ctl = RooRealVar( "mean_ctl", "mean_ctl", -3, -8, 8 ) 
    gx_ctl = RooGaussian( "gx_ctl", "gx_ctl", x, mean_ctl, sigma ) 

    # Construct the background pdf
    a0_ctl = RooRealVar( "a0_ctl", "a0_ctl", -0.1, -1, 1 ) 
    a1_ctl = RooRealVar( "a1_ctl", "a1_ctl", 0.5, -0.1, 1 ) 
    px_ctl = RooChebychev( "px_ctl", "px_ctl", x, RooArgList( a0_ctl, a1_ctl ) ) 

    # Construct the composite model
    f_ctl = RooRealVar( "f_ctl", "f_ctl", 0.5, 0., 1. ) 
    model_ctl = RooAddPdf( "model_ctl", "model_ctl", RooArgList( gx_ctl, px_ctl ),
                           RooArgList( f_ctl ) ) 
    


    # G e n e r a t e   e v e n t s   f o r   b o t h   s a m p l e s 
    # ---------------------------------------------------------------

    # Generate 1000 events in x and y from model
    data = model.generate( RooArgSet( x ), 100 ) 
    data_ctl = model_ctl.generate( RooArgSet( x ), 2000 ) 



    # C r e a t e   i n d e x   c a t e g o r y   a n d   j o i n   s a m p l e s 
    # ---------------------------------------------------------------------------
    # Define category to distinguish physics and control samples events
    sample = RooCategory( "sample", "sample" ) 
    sample.defineType( "physics" ) 
    sample.defineType( "control" ) 

    # Construct combined dataset in (x,sample)
    combData = RooDataSet( "combData", "combined data", RooArgSet(x), RooFit.Index( sample ),
                          RooFit.Import( "physics", data ),
                          RooFit.Import( "control", data_ctl ) ) 



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
                   RooFit.ProjWData( RooArgSet(sample), combData ) ) 
    simPdf.plotOn( frame1, RooFit.Slice( sample, "physics" ),
                   RooFit.Components( "px" ),
                   RooFit.ProjWData( RooArgSet(sample), combData ),
                   RooFit.LineStyle( kDashed ) ) 

    # The same plot for the control sample slice
    frame2 = x.frame( RooFit.Bins( 30 ), RooFit.Title( "Control sample" ) ) 
    combData.plotOn( frame2, RooFit.Cut( "sample==sample::control" ) ) 
    simPdf.plotOn( frame2, RooFit.Slice( sample, "control" ),
                  RooFit.ProjWData( RooArgSet(sample), combData ) ) 
    simPdf.plotOn( frame2, RooFit.Slice( sample, "control" ),
                  RooFit.Components( "px_ctl" ),
                  RooFit.ProjWData( RooArgSet(sample), combData ),
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

