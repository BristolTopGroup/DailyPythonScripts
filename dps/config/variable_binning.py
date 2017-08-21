def produce_reco_bin_edges( gen_bin_edges ):
  reco_bin_edges = {}
  for variable in gen_bin_edges:
    edges = gen_bin_edges[variable]
    reco_bin_edges[variable] = []
    for i in range(0,len(edges)-1):
      reco_bin_edges[variable].append( edges[i])
      reco_bin_edges[variable].append( round ( edges[i] + ( edges[i+1] - edges[i] ) / 2, 2 ) )
    reco_bin_edges[variable].append(edges[-1])
  return reco_bin_edges


fit_variable_bin_edges = {
                          'absolute_eta' : [round( i * 0.2, 2 ) for i in range ( int( 3 / 0.2 ) + 1 )],
                          'M3' : [i * 25 for i in range ( int( 1000 / 25 ) + 1 )],
                          'M_bl' : [i * 10 for i in range ( int( 1000 / 20 ) + 1 )],
                          'angle_bl' : [round( i * 0.2, 2 ) for i in range ( int( 4 / 0.2 ) + 1 )],
                          'Mjj' : [i * 25 for i in range ( int( 500 / 25 ) + 1 )],
                          }

bin_edges_full = {
'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 10.5],
'WPT' : [0.0, 50.0, 105.0, 165.0, 240.0, 325.0, 415.0, 845.0],
'lepton_pt' : [26.0, 40.0, 55.0, 70.0, 85.0, 100.0, 115.0, 130.0, 145.0, 160.0, 175.0, 190.0, 205.0, 220.0, 235.0, 255.0, 285.0, 435.0],
'HT' : [110.0, 220.0, 275.0, 340.0, 410.0, 485.0, 570.0, 660.0, 760.0, 870.0, 990.0, 1115.0, 1250.0, 1925.0],
'ST' : [136.0, 315.0, 390.0, 475.0, 565.0, 665.0, 770.0, 885.0, 1010.0, 1140.0, 1285.0, 1440.0, 1615.0, 2490.0],
'MET' : [0.0, 50.0, 105.0, 175.0, 245.0, 315.0, 565.0],
'abs_lepton_eta' : [0.0, 0.14, 0.27, 0.39, 0.53, 0.65, 0.78, 0.92, 1.05, 1.16, 1.27, 1.38, 1.48, 1.62, 1.72, 1.83, 2.0, 2.4],

'abs_lepton_eta_coarse' : [0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.0, 2.4],

}

bin_edges_vis = {
'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 10.5],
'WPT' : [0.0, 50.0, 105.0, 165.0, 240.0, 325.0, 415.0, 845.0],
'lepton_pt' : [26.0, 40.0, 55.0, 70.0, 85.0, 100.0, 115.0, 130.0, 145.0, 160.0, 175.0, 190.0, 205.0, 220.0, 235.0, 255.0, 285.0, 435.0],
'HT' : [110.0, 220.0, 275.0, 340.0, 410.0, 485.0, 570.0, 660.0, 760.0, 870.0, 990.0, 1115.0, 1250.0, 1925.0],
'ST' : [136.0, 315.0, 390.0, 475.0, 565.0, 665.0, 770.0, 885.0, 1010.0, 1140.0, 1285.0, 1440.0, 1615.0, 2490.0],
'MET' : [0.0, 50.0, 105.0, 175.0, 245.0, 315.0, 565.0],
'abs_lepton_eta' : [0.0, 0.14, 0.27, 0.39, 0.53, 0.65, 0.78, 0.92, 1.05, 1.16, 1.27, 1.38, 1.48, 1.62, 1.72, 1.83, 2.0, 2.4],

'abs_lepton_eta_coarse' : [0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.0, 2.4],

}

reco_bin_edges_vis = produce_reco_bin_edges( bin_edges_vis )
reco_bin_edges_full = produce_reco_bin_edges( bin_edges_full )

minimum_bin_width = {
  'MET' : 20.,
  'WPT' : 20.,
  'NJets' : 1.,
  'HT' : 20.,
  'ST' : 20.,
  'lepton_pt' : 10.,
  'abs_lepton_eta' : 0.1,
}

nice_bin_width = {
  'MET' : 5.,
  'WPT' : 5.,
  'NJets' : 0.5,
  'HT' : 5.,
  'ST' : 5.,
  'lepton_pt' : 5.,
  'abs_lepton_eta' : 0.005,
}

control_plots_bins = {
  'NJets' : [i + 0.5 for i in range ( 3, 16 + 1 )],
  'JetPt' : [i * 5  for i in range ( 5, 40 )],  
  'MuonPt' : [i * 10 for i in range ( 1, 40 )],
  'ElectronPt' : [i * 10 for i in range ( 1, 40 )],

  'LeptonEta' : [i*0.2 for i in range( -12, 13 )],

    # 'LeptonEta' : [i*0.02 for i in range( -25, 26 )],
    # 'LeptonEta' : [i*0.04 for i in range( -12, 13 )],

    
  # 'AbsLeptonEta' : [i*0.1 for i in range( 0, 25 )],  
  'AbsLeptonEta' : [i*0.3 for i in range( 0, 9 )],  

  'NBJets' : [i - 0.5 for i in range ( 0, 6 + 1 )],
  'NVertex' : [i for i in range ( 0,40 + 1 )],
  'relIso' : [i*0.01 for i in range(0,20)],
  'relIsoQCD' : [i*0.025 for i in range(0,40)],
  'AbsLeptonEtaQCD' : [i*0.2 for i in range( 0, 24 )],

  'MET' : [i * 15  for i in range ( 0, 40 )],
  'WPT' : [i * 25  for i in range ( 0, 35 )],
  'HT' : [i * 50  for i in range ( 0, 40 )],
  'ST' : [i * 50  for i in range ( 2, 40 )],
  'Tau' : [i*500 for i in range (0,20)],

  'MT' : [i * 25  for i in range ( 0, 35 )],
  'sigmaietaieta' : [i * 0.002  for i in range ( 0, 20 )],
}

control_plots_bins_for01 = {
  'NJets'           : [3.5,16.5],
  'lepton_pt'       : [10, 390],
  'abs_lepton_eta'  : [0,2.4],  
  'MET'             : [0,585],
  'WPT'             : [0,864],
  'HT'              : [0,2000],
  'ST'              : [100,2000],
  'Tau'             : [0,10000],
  'MT'              : [0, 900],

  'abs_lepton_eta_coarse' : bin_edges_vis['abs_lepton_eta_coarse'],

}

control_plot_nbins = {
  'NJets' : 13,
  'lepton_pt' : 38,
  'abs_lepton_eta' : 24,
  'abs_lepton_eta_coarse' : 8,
  'MET' : 39,
  'WPT' : 16,
  'HT' : 20,
  'ST' : 20,
  'Tau' : 25,
  'MT' : 36,
}


# should we want separate binning for different centre of mass energies
# we can put the logic here, maybe as a function:
# get_variable_binning(centre_of_mass_energy, combined = False)
# where combined gives you the best bins across the different
# centre of mass energies

bin_widths = {}
variable_bins_ROOT = {}
variable_bins_latex = {}
# calculate all the other variables
for variable in bin_edges_full.keys():
    bin_widths[variable] = []
    variable_bins_ROOT[variable] = []
    variable_bins_latex[variable] = {}
    number_of_edges = len( bin_edges_full[variable] )
    unit = '\GeV'
    bin_name_template = '%d--%d'
    bin_name_latex_template = '%d--%d%s'
    if 'eta' in variable :
      bin_name_template = '%.2f--%.2f'
      bin_name_latex_template = '%.2f--%.2f%s'
    if 'eta' in variable or variable == 'NJets':
        unit = ''
    for i in range( number_of_edges - 1 ):
        lower_edge = bin_edges_full[variable][i]
        upper_edge = bin_edges_full[variable][i + 1]
        bin_widths[variable].append( upper_edge - lower_edge )
        bin_name = bin_name_template % ( lower_edge, upper_edge )
        bin_name_latex = bin_name_latex_template % ( lower_edge, upper_edge, unit )
        if ( i + 1 ) == number_of_edges - 1 and not 'eta' in variable:
            bin_name = '%d-inf' % int( lower_edge )
            bin_name_latex = '$\\geq %d$%s' % (int( lower_edge ), unit)
        variable_bins_ROOT[variable].append( bin_name )
        variable_bins_latex[variable][bin_name] = bin_name_latex

bin_widths_visiblePS = {}
variable_bins_visiblePS_ROOT = {}
variable_bins_visiblePS_latex = {}
# calculate all the other variables
for variable in bin_edges_vis.keys():
    bin_widths_visiblePS[variable] = []
    variable_bins_visiblePS_ROOT[variable] = []
    variable_bins_visiblePS_latex[variable] = {}
    number_of_edges = len( bin_edges_vis[variable] )
    unit = '\GeV'
    bin_name_template = '%d--%d'
    bin_name_latex_template = '%d--%d%s'
    if 'eta' in variable :
      bin_name_template = '%.2f--%.2f'
      bin_name_latex_template = '%.2f--%.2f%s'
    if 'eta' in variable or variable == 'NJets':
        unit = ''
    for i in range( number_of_edges - 1 ):
        lower_edge = bin_edges_vis[variable][i]
        upper_edge = bin_edges_vis[variable][i + 1]
        bin_widths_visiblePS[variable].append( upper_edge - lower_edge )
        bin_name = bin_name_template % ( lower_edge, upper_edge )
        bin_name_latex = bin_name_latex_template % ( lower_edge, upper_edge, unit )
        if ( i + 1 ) == number_of_edges - 1 and not 'eta' in variable:
            bin_name = '%d-inf' % int( lower_edge )
            bin_name_latex = '$\\geq %d$%s' % (int( lower_edge ), unit)
        variable_bins_visiblePS_ROOT[variable].append( bin_name )
        variable_bins_visiblePS_latex[variable][bin_name] = bin_name_latex
