fit_variable_bin_edges = {
                          'absolute_eta' : [round( i * 0.2, 2 ) for i in range ( int( 3 / 0.2 ) + 1 )],
                          'M3' : [i * 25 for i in range ( int( 1000 / 25 ) + 1 )],
                          'M_bl' : [i * 10 for i in range ( int( 1000 / 20 ) + 1 )],
                          'angle_bl' : [round( i * 0.2, 2 ) for i in range ( int( 4 / 0.2 ) + 1 )],
                          'Mjj' : [i * 25 for i in range ( int( 500 / 25 ) + 1 )],
                          }

bin_edges = {
'MET' : [0.0, 34.0, 64.0, 119.0, 183.0, 503.0],
'WPT' : [0.0, 42.0, 84.0, 129.0, 185.0, 255.0, 605.0],
'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 17.5],
'HT' : [100.0, 200.0, 241.0, 289.0, 343.0, 403.0, 468.0, 539.0, 617.0, 700.0, 788.0, 900.0, 1460.0],
'ST' : [123.0, 296.0, 356.0, 422.0, 495.0, 577.0, 667.0, 767.0, 875.0, 994.0, 1121.0, 1756.0],
'lepton_pt' : [23.0, 34.0, 45.0, 56.0, 67.0, 78.0, 89.0, 100.0, 111.0, 125.0, 148.0, 263.0],
'abs_lepton_eta' : [0.0, 0.2, 0.41, 0.61, 0.82, 1.02, 1.22, 1.43, 1.68, 2.94],
}

bin_edges_vis = {
'MET' : [0.0, 34.0, 64.0, 119.0, 183.0, 503.0],
'WPT' : [0.0, 42.0, 84.0, 129.0, 185.0, 255.0, 605.0],
'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 17.5],
'HT' : [100.0, 200.0, 241.0, 289.0, 343.0, 403.0, 468.0, 539.0, 617.0, 700.0, 788.0, 900.0, 1460.0],
'ST' : [123.0, 296.0, 356.0, 422.0, 495.0, 577.0, 667.0, 767.0, 875.0, 994.0, 1121.0, 1756.0],
'lepton_pt' : [23.0, 34.0, 45.0, 56.0, 67.0, 78.0, 89.0, 100.0, 111.0, 125.0, 148.0, 263.0],
'abs_lepton_eta' : [0.0, 0.2, 0.41, 0.61, 0.82, 1.02, 1.22, 1.43, 1.68, 2.94],
}

minimum_bin_width = {
  'MET' : 20.,
  'WPT' : 20.,
  'NJets' : 1.,
  'HT' : 20.,
  'ST' : 20.,
  'lepton_pt' : 10.,
  'abs_lepton_eta' : 0.2,
}

control_plots_bins = {
  'NJets' : [i + 0.5 for i in range ( 3, 12 + 1 )],
  'JetPt' : [i * 5  for i in range ( 5, 40 )],  
  'MuonPt' : [i * 11.5 for i in range ( 2, 20 )],
  'ElectronPt' : [i * 10 for i in range ( 3, 20 )],
  'LeptonEta' : [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5],  
  'AbsLeptonEta' : [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.1],  
  'NBJets' : [i - 0.5 for i in range ( 0, 6 + 1 )],
  # 'NVertex' : [i*2 for i in range ( 0,20 + 1 )],
  'NVertex' : [i for i in range ( 0,40 + 1 )],
  'relIso' : [i*0.01 for i in range(0,15)],
  'relIsoQCD' : [i*0.2 for i in range(0,15)],
  'MET' : [i * 15  for i in range ( 0, 21 )],
  'WPT' : [i * 25  for i in range ( 0, 17 )],
  'HT' : [i * 50  for i in range ( 0, 21 )],
  'ST' : [i * 50  for i in range ( 2, 25 )],
  # 'sigmaietaieta' : [i * 0.001  for i in range ( 12, 40 )],
  'sigmaietaieta' : [i * 0.002  for i in range ( 0, 20 )],
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
for variable in bin_edges.keys():
    bin_widths[variable] = []
    variable_bins_ROOT[variable] = []
    variable_bins_latex[variable] = {}
    number_of_edges = len( bin_edges[variable] )
    unit = '\GeV'
    bin_name_template = '%d--%d'
    bin_name_latex_template = '%d--%d%s'
    if 'eta' in variable :
      bin_name_template = '%.2f--%.2f'
      bin_name_latex_template = '%.2f--%.2f%s'
    if 'eta' in variable or variable == 'NJets':
        unit = ''
    for i in range( number_of_edges - 1 ):
        lower_edge = bin_edges[variable][i]
        upper_edge = bin_edges[variable][i + 1]
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
