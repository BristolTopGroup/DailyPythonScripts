fit_variable_bin_edges = {
                          'absolute_eta' : [round( i * 0.2, 2 ) for i in range ( int( 3 / 0.2 ) + 1 )],
                          'M3' : [i * 25 for i in range ( int( 1000 / 25 ) + 1 )],
                          'M_bl' : [i * 10 for i in range ( int( 1000 / 20 ) + 1 )],
                          'angle_bl' : [round( i * 0.2, 2 ) for i in range ( int( 4 / 0.2 ) + 1 )],
                          'Mjj' : [i * 25 for i in range ( int( 500 / 25 ) + 1 )],
                          }
bin_edges = {
'MET' : [0.0, 42.0, 100.0, 332.0],
'WPT' : [0.0, 44.0, 87.0, 134.0, 197.0, 449.0],
'NJets' : [3.5, 4.5, 5.5, 6.5, 10.5],
'HT' : [100.0, 204.0, 248.0, 298.0, 354.0, 418.0, 488.0, 561.0, 642.0, 755.0, 1207.0],
'ST' : [123.0, 298.0, 359.0, 425.0, 501.0, 587.0, 682.0, 790.0, 898.0, 1330.0],
'lepton_pt' : [23.0, 31.0, 37.0, 42.0, 48.0, 54.0, 61.0, 69.0, 79.0, 92.0, 113.0, 197.0],
'abs_lepton_eta' : [0.0, 0.117, 0.234, 0.357, 0.483, 0.609, 0.741, 0.885, 1.041, 1.218, 1.416, 2.208],
}

bin_edges_vis = {
'MET' : [0.0, 42.0, 100.0, 332.0],
'WPT' : [0.0, 44.0, 87.0, 134.0, 197.0, 449.0],
'NJets' : [3.5, 4.5, 5.5, 6.5, 10.5],
'HT' : [100.0, 204.0, 248.0, 298.0, 354.0, 418.0, 488.0, 561.0, 642.0, 755.0, 1207.0],
'ST' : [123.0, 298.0, 359.0, 425.0, 501.0, 587.0, 682.0, 790.0, 898.0, 1330.0],
'lepton_pt' : [23.0, 31.0, 37.0, 42.0, 48.0, 54.0, 61.0, 69.0, 79.0, 92.0, 113.0, 197.0],
'abs_lepton_eta' : [0.0, 0.117, 0.234, 0.357, 0.483, 0.609, 0.741, 0.885, 1.041, 1.218, 1.416, 2.208],
}

control_plots_bins = {
  'NJets' : [i + 0.5 for i in range ( 3, 12 + 1 )],
  'JetPt' : [i * 5  for i in range ( 5, 40 )],  
  'MuonPt' : [i * 11.5 for i in range ( 2, 20 )],
  'ElectronPt' : [i * 10 for i in range ( 3, 20 )],
  'LeptonEta' : [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5],  
  'AbsLeptonEta' : [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.1],  
  'NBJets' : [i - 0.5 for i in range ( 0, 6 + 1 )],
  'NVertex' : [i*2 for i in range ( 0,20 + 1 )],
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
