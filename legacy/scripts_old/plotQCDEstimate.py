#
# 31 Mar 2010
# Plots (signed) Delta = (est-true)/true, for QCD estimate
#
#---------------------------------------------------------------
from __future__ import division
from ROOT import *

n = 4;
nrange = 9;
plot_average_est = True;

# free in 12j, fix in 34j
constrain_gaus_mean_12j = False;
show_free_fit_res_34j = True;

# landau free
#bool show_free_fit_res_34j = true;
#const bool constrain_gaus_mean_12j = true;


# gaus mean-constrained in 12j, fix in 34j
def plot_qcd_estimate_gaus_mean12j():
  constrain_gaus_mean_12j = true;
  show_free_fits_res_34j = false;
  plot_qcd_estimate( "gaus" );

def setStyle():

  gROOT.SetStyle( "Plain" );
  gStyle.SetTextFont( 42 );
  gStyle.SetLabelFont( 42, "xy" );
  gStyle.SetFrameFillColor( 0 );
  gStyle.SetTitleBorderSize( 0 );

  gStyle.SetTitleH( 0.06 );
  gStyle.SetPadTopMargin( 0.15 );

  gStyle.SetOptFit( 1 );
  gStyle.SetPalette( 1 );

  gStyle.SetPadTickX( 1 );
  gStyle.SetPadTickY( 1 );

def plot_qcd_estimate( func = "gaus" ):

  setStyle();

  if constrain_gaus_mean_12j:
      show_free_fit_res_34j = False;

  x = [1, 2, 3, 4]
  xx = [3, 4]
  x12j = [1, 2]
  # Gaus (Free-fits)

  result = open( "est_free_%s.txt" % func );
  #result.open(Form("gaus_mean_0.3to0.6_12j__rb5/est_free_%s.txt",func));

  m = nrange * ( 4 + 2 );
  est = []
  estFix = []
  max_dev = 0;
  max_dev_12j = 0;
  max_dev_34j = 0;
  max_dev_3j = 0;
  max_dev_4j = 0;
  max_dev_34j_fix = 0;
  max_dev_3j_fix = 0;
  max_dev_4j_fix = 0;

  # Free fits
  for i in range( 0, 4 * nrange ):
    est.append( result.readline() )
    if fabs( est[-1] ) > max_dev:
        max_dev = fabs( est[-1] );

    if i % 4 <= 1:   #1,2j
      if fabs( est[-1] ) > max_dev_12j:
          max_dev_12j = fabs( est[-1] );
    elif i % 4 == 2 : #3j
      if fabs( est[-1] ) > max_dev_3j :
          max_dev_3j = fabs( est[-1] );
    elif i % 4 == 3: #4mj
      if fabs( est[-1] ) > max_dev_4j :
          max_dev_4j = fabs( est[-1] );

    if i % 4 == 0:
        print #first of 4
    print i % 4 + 1, "j   est[", i, "] = ", est[i], "   ";
    if i % 4 <= 1:
        print "max_dev_12j = ", max_dev_12j; #12j
    print endl;
  result.close();

  # Gaus (Constrained-fits in 3,4j)
  result.open( "est_fix_%s.txt" % func )
  #result.open(Form("gaus_mean_0.3to0.6_12j__rb5/est_fix_%s.txt",func));

  estFix2 = [];
  maxDevFix = 0;

  for i in range( 0, 4 * nrange ):

    # read in 3,4j only
    #print "amtb: i=", i
    if not constrain_gaus_mean_12j and i % 4 < 2:
        continue;

    estFix.append( result.readline() )
    estFix2.append( estFix[-1] );


    print i % 4 + 1, "j   estFix[", i, "] = " , estFix[-1], "   ", endl;

    #print "amtb: i=", i


    if fabs( estFix[-1] ) > maxDevFix :
        maxDevFix = fabs( estFix[-1] );
    if fabs( estFix[-1] ) > max_dev_34j_fix :
        max_dev_34j_fix = fabs( estFix[-1] );
    if i % 4 == 2:#3j
      if fabs( estFix[-1] ) > max_dev_3j_fix:
          max_dev_3j_fix = fabs( estFix[-1] );
    elif i % 4 == 3: #>=4j
      if fabs( estFix[-1] ) > max_dev_4j_fix:
          max_dev_4j_fix = fabs( estFix[-1] );

  for k in range( 0, len( estFix2 ) ):
    print "amtb: estFix2[", k, "]: ", estFix2[k]

  result.close();
  max_dev_34j_fix = TMath.Max( max_dev_3j_fix, max_dev_4j_fix );
  max_dev_34j = TMath.Max( max_dev_3j, max_dev_4j );

  print "maxDevFix: ", maxDevFix


  print "\nFor all ranges, |max| deviation is ", max_dev
  print "For 1,2j,   |max| deviation is ", max_dev_12j
  print "For free fit (3j)      |max| deviation is ", max_dev_3j
  print "For free fit (>=4j)    |max| deviation is ", max_dev_4j
  print "For free fit (3,>=4j), |max| deviation is ", max_dev_34j
  print "For constrained fit (3j),     |max| deviation is ", max_dev_3j_fix
  print "For constrained fit (>=4j),   |max| deviation is ", max_dev_4j_fix
  print "For constrained fit (3,>=4j), |max| deviation is ", max_dev_34j_fix



  c2 = TCanvas( "c2", "QCD estimates", 600, 600 );

  y[nrange][4];

  index = 0;

  for i in range( 0, nrange ):
      for j in range( 0, 4 ):
          y[i][j] = est[index]; #read in
          index += 1
      #print "index="<<index<< endl;
      #print y[i][j]<<endl;;
  yy12j = [[0, 0] for x in xrange( nrange )]
  yy34j = [[0, 0] for x in xrange( nrange )]
  # ix=0;
  jj = 0;
  for i in range( 0, nrange ):
      jj += 1
      yy12j[i][0] = estFix[jj];#1j
      jj += 1
      yy12j[i][1] = estFix[jj];#2j
      jj += 1
      yy34j[i][0] = estFix[jj];#3j
      jj += 1
      yy34j[i][1] = estFix[jj];#4mj

    #print "index="<<index<< endl;






  gStyle.SetMarkerSize( 1.7 );
  gStyle.SetMarkerStyle( 20 );
  c2.SetTopMargin( 0.1 );
  c2.SetLeftMargin( 0.12 );
  c2.SetRightMargin( 0.35 );

  gr1;
  gr2;
  gr3;
  gr4;
  gr5;
  gr6;
  gr7;
  gr8;
  gr9;
  if constrain_gaus_mean_12j == False:
    if show_free_fit_res_34j:
      #draw free-fit results for 1-4j
      gr1 = TGraph( n, x, y[1 - 1] );
      gr2 = TGraph( n, x, y[2 - 1] );
      gr3 = TGraph( n, x, y[3 - 1] );
      gr4 = TGraph( n, x, y[4 - 1] );
      gr5 = TGraph( n, x, y[5 - 1] );
      gr6 = TGraph( n, x, y[6 - 1] );
      gr7 = TGraph( n, x, y[7 - 1] );
      gr8 = TGraph( n, x, y[8 - 1] );
      gr9 = TGraph( n, x, y[9 - 1] );
    else:
      #draw: free-fit results for 1-2j, OR
      #      gaus-mean-limited in 1,2j
      gr1 = TGraph( 2, x12j, y[1 - 1] );
      gr2 = TGraph( 2, x12j, y[2 - 1] );
      gr3 = TGraph( 2, x12j, y[3 - 1] );
      gr4 = TGraph( 2, x12j, y[4 - 1] );
      gr5 = TGraph( 2, x12j, y[5 - 1] );
      gr6 = TGraph( 2, x12j, y[6 - 1] );
      gr7 = TGraph( 2, x12j, y[7 - 1] );
      gr8 = TGraph( 2, x12j, y[8 - 1] );
      gr9 = TGraph( 2, x12j, y[9 - 1] );


  else:
    gr1 = TGraph( 2, x12j, yy12j[1 - 1] );
    gr2 = TGraph( 2, x12j, yy12j[2 - 1] );
    gr3 = TGraph( 2, x12j, yy12j[3 - 1] );
    gr4 = TGraph( 2, x12j, yy12j[4 - 1] );
    gr5 = TGraph( 2, x12j, yy12j[5 - 1] );
    gr6 = TGraph( 2, x12j, yy12j[6 - 1] );
    gr7 = TGraph( 2, x12j, yy12j[7 - 1] );
    gr8 = TGraph( 2, x12j, yy12j[8 - 1] );
    gr9 = TGraph( 2, x12j, yy12j[9 - 1] );

  # constrained
  gr_1 = TGraph( 2, xx, yy34j[1 - 1] );
  gr_2 = TGraph( 2, xx, yy34j[2 - 1] );
  gr_3 = TGraph( 2, xx, yy34j[3 - 1] );
  gr_4 = TGraph( 2, xx, yy34j[4 - 1] );
  gr_5 = TGraph( 2, xx, yy34j[5 - 1] );
  gr_6 = TGraph( 2, xx, yy34j[6 - 1] );
  gr_7 = TGraph( 2, xx, yy34j[7 - 1] );
  gr_8 = TGraph( 2, xx, yy34j[8 - 1] );
  gr_9 = TGraph( 2, xx, yy34j[9 - 1] );


  gr1.SetMarkerColor( kGreen + 1 );
  gr2.SetMarkerColor( kGreen + 2 );
  gr3.SetMarkerColor( kGreen + 3 );
  gr4.SetMarkerColor( kAzure + 7 );
  gr5.SetMarkerColor( kAzure - 3 );
  gr6.SetMarkerColor( kBlue );
  gr7.SetMarkerColor( kOrange );
  gr8.SetMarkerColor( kOrange - 1 );
  gr9.SetMarkerColor( kOrange - 6 );

  gr_1.SetMarkerColor( kGreen + 1 );
  gr_2.SetMarkerColor( kGreen + 2 );
  gr_3.SetMarkerColor( kGreen + 3 );
  gr_4.SetMarkerColor( kAzure + 7 );
  gr_5.SetMarkerColor( kAzure - 3 );
  gr_6.SetMarkerColor( kBlue );
  gr_7.SetMarkerColor( kOrange );
  gr_8.SetMarkerColor( kOrange - 1 );
  gr_9.SetMarkerColor( kOrange - 6 );


  gr_1.SetMarkerStyle( 22 );
  gr_2.SetMarkerStyle( 22 );
  gr_3.SetMarkerStyle( 22 );
  gr_4.SetMarkerStyle( 22 );
  gr_5.SetMarkerStyle( 22 );
  gr_6.SetMarkerStyle( 22 );
  gr_7.SetMarkerStyle( 22 );
  gr_8.SetMarkerStyle( 22 );
  gr_9.SetMarkerStyle( 22 );



  # To get desired x range, draw blank histo
  gStyle.SetTitleW( 0.9 );
  gStyle.SetTitleH( 0.05 );#?
  if func == "gaus":
      h = TH1D( "h", "Variation of QCD estimates with fit range (Gaussian)", 4, 0.5, 4.5 );
  elif func == "pol3":
      h = TH1D( "h", "Variation of QCD estimates with fit range (Pol3)", 4, 0.5, 4.5 );
  elif func == "landau":
      h = TH1D( "h", "Variation of QCD estimates with fit range (Landau)", 4, 0.5, 4.5 );


  h.SetStats( kFALSE ); # no statistics
  h.Draw();
  h.SetYTitle( "Deviation = (Est-True)/True" );

  show_range = int( max_dev ) + 1;
  if constrain_gaus_mean_12j:
      show_range = int( max_dev ) + 1;

  print "show_range: ", show_range

  h.GetYaxis().SetRangeUser( 0 - show_range, show_range );
  h.GetXaxis().SetRangeUser( 0.5, 5.5 );
  h.GetXaxis().SetBinLabel( 1., "1j" );
  h.GetXaxis().SetBinLabel( 2., "2j" );
  h.GetXaxis().SetBinLabel( 3., "3j" );
  h.GetXaxis().SetBinLabel( 4., "#geq4j" );
  h.GetXaxis().SetLabelSize( 0.07 );
  h.GetYaxis().SetTitleOffset( 1.3 );


  # Free-fits
  gr1.Draw( "P" );
  gr2.Draw( "P" ); #to superimpose graphs, do not re-draw axis
  gr3.Draw( "P" );
  gr4.Draw( "P" );
  gr5.Draw( "P" );
  gr6.Draw( "P" );
  gr7.Draw( "P" );
  gr8.Draw( "P" );
  gr9.Draw( "P" );

  if not show_free_fit_res_34j:
  # Constrained fits
    gr_1.Draw( "P" );
    gr_2.Draw( "P" );
    gr_3.Draw( "P" );
    gr_4.Draw( "P" );
    gr_5.Draw( "P" );
    gr_6.Draw( "P" );
    gr_7.Draw( "P" );
    gr_8.Draw( "P" );
    gr_9.Draw( "P" );

  c2.SetGrid( 1, 1 );

  leg = TLegend( 0.65, 0.1, 0.98, 0.9 );
  leg.SetFillColor( 0 );
  #  leg.SetTextFont(62);
  if func != "gaus" or not constrain_gaus_mean_12j:
    leg.AddEntry( gr1, "Free: 0.1-1.0", "p" );
    leg.AddEntry( gr2, "Free: 0.1-1.2", "p" );
    leg.AddEntry( gr3, "Free: 0.1-1.4", "p" );
    leg.AddEntry( gr4, "Free: 0.2-1.1", "p" );
    leg.AddEntry( gr5, "Free: 0.2-1.3", "p" );
    leg.AddEntry( gr6, "Free: 0.2-1.5", "p" );
    leg.AddEntry( gr7, "Free: 0.3-1.2", "p" );
    leg.AddEntry( gr8, "Free: 0.3-1.4", "p" );
    leg.AddEntry( gr9, "Free: 0.3-1.6", "p" );

  if func == "gaus" and constrain_gaus_mean_12j:
    leg.AddEntry( gr1, "#mu-constr.: 0.1-1.0", "p" );
    leg.AddEntry( gr2, "#mu-constr.: 0.1-1.2", "p" );
    leg.AddEntry( gr3, "#mu-constr.: 0.1-1.4", "p" );
    leg.AddEntry( gr4, "#mu-constr.: 0.2-1.1", "p" );
    leg.AddEntry( gr5, "#mu-constr.: 0.2-1.3", "p" );
    leg.AddEntry( gr6, "#mu-constr.: 0.2-1.5", "p" );
    leg.AddEntry( gr7, "#mu-constr.: 0.3-1.2", "p" );
    leg.AddEntry( gr8, "#mu-constr.: 0.3-1.4", "p" );
    leg.AddEntry( gr9, "#mu-constr.: 0.3-1.6", "p" );

  if not show_free_fit_res_34j:
      leg.AddEntry( gr_1, "Constrained: 0.1-1.0", "p" );
      leg.AddEntry( gr_2, "Constrained: 0.1-1.2", "p" );
      leg.AddEntry( gr_3, "Constrained: 0.1-1.4", "p" );
      leg.AddEntry( gr_4, "Constrained: 0.2-1.1", "p" );
      leg.AddEntry( gr_5, "Constrained: 0.2-1.3", "p" );
      leg.AddEntry( gr_6, "Constrained: 0.2-1.5", "p" );
      leg.AddEntry( gr_7, "Constrained: 0.3-1.2", "p" );
      leg.AddEntry( gr_8, "Constrained: 0.3-1.4", "p" );
      leg.AddEntry( gr_9, "Constrained: 0.3-1.6", "p" );

  leg.Draw();
  if func == "gaus":
      c2.SaveAs( "qcd_estimate_gaus.gif" );
  elif( func == "pol3" ):
      c2.SaveAs( "qcd_estimate_pol3.gif" );
  elif( func == "landau" ):
      c2.SaveAs( "qcd_estimate_landau.gif" );


  h.GetYaxis().SetRangeUser( -1, 1 );
  c2.SaveAs( Form( "qcd_estimate_%s_zoom_11.gif", func ) );

  h.GetYaxis().SetRangeUser( -2, 2 );
  c2.SaveAs( Form( "qcd_estimate_%s_zoom_22.gif", func ) );

  h.GetYaxis().SetRangeUser( -3, 3 );
  c2.SaveAs( Form( "qcd_estimate_%s_zoom_33.gif", func ) );

  h.GetYaxis().SetRangeUser( -6, 6 );
  c2.SaveAs( Form( "qcd_estimate_%s_zoom_66.gif", func ) );

  h.GetYaxis().SetRangeUser( -8, 8 );
  c2.SaveAs( Form( "qcd_estimate_%s_zoom_88.gif", func ) );



  #------------------------------
  # Plot 2: Average of 9 ranges
  #------------------------------

  if plot_average_est:
    average_1j;
    average_2j;
    average_3j;
    average_4mj;
    average_3j_fix;
    average_4mj_fix;

    for i in range( 0, nrange ):
      average_1j += y[i][0];
      average_2j += y[i][1];
      average_3j += y[i][2];
      average_4mj += y[i][3];
      average_3j_fix += yy34j[i][0];
      average_4mj_fix += yy34j[i][1];

    average_1j = average_1j / nrange;
    average_2j = average_2j / nrange;
    average_3j = average_3j / nrange;
    average_4mj = average_4mj / nrange;
    average_3j_fix = average_3j_fix / nrange;
    average_4mj_fix = average_4mj_fix / nrange;
    print "------------------------------------------" << endl;
    print "average of 9 ranges, 1j:  ", average_1j << endl;
    print "average of 9 ranges, 2j:  ", average_2j
    print "average of 9 ranges, 3j:  ", average_3j_fix
    print "average of 9 ranges, 4mj: ", average_4mj_fix
    print "average of 9 ranges, 3j (free):  ", average_3j
    print "average of 9 ranges, 4mj (free): ", average_4mj
    print "------------------------------------------" << endl;

    x12 = [1, 2]
    av12 = [ average_1j, average_2j ]
    av34 = [ average_3j, average_4mj ]
    av34fix = [ average_3j_fix, average_4mj_fix]
    gra12 = TGraph( 2, x12, av12 );
    gra34 = TGraph( 2, xx, av34 );
    gra34fix = TGraph( 2, xx, av34fix );


    c3 = TCanvas( "c3", "Average QCD estimate", 610, 10, 600, 600 );
    c3.cd();
    c3.SetGrid( 1, 1 );
    c3.SetLeftMargin( 0.12 );
    c3.SetRightMargin( 0.35 );

    hh = h.Clone();
    hh.GetYaxis().SetRangeUser( -1, 1 );
    hh.SetTitle( Form( "Average QCD estimate (%s)", func ) );
    hh.Draw();

    gra12.SetMarkerColor( kRed );
    gra34.SetMarkerColor( kRed );
    gra34fix.SetMarkerColor( kGreen + 3 );

    gra12.SetMarkerStyle( 29 );
    gra34.SetMarkerStyle( 30 );
    gra34fix.SetMarkerStyle( 29 );

    gra12.SetMarkerSize( 2.5 );
    gra34.SetMarkerSize( 2.5 );
    gra34fix.SetMarkerSize( 2.5 );

    gra12.Draw( "P" );
    gra34.Draw( "P" );
    gra34fix.Draw( "P" );

    leg2 = TLegend( 0.65, 0.7, 0.98, 0.9 );
    leg2.SetFillColor( 0 );
    leg2.AddEntry( gra12, "Free fits (1,2j)", "p" );
    leg2.AddEntry( gra34, "Free fits (3,#geq4j)", "p" );
    leg2.AddEntry( gra34fix, "Constrained fits (3,#geq4j)", "p" );
    leg2.Draw();

    c3.SaveAs( Form( "qcd_estimate_%s_average.gif", func ) );




