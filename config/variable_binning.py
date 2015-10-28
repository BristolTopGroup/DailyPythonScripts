fit_variable_bin_edges = {
                          'absolute_eta' : [round( i * 0.2, 2 ) for i in range ( int( 3 / 0.2 ) + 1 )],
                          'M3' : [i * 25 for i in range ( int( 1000 / 25 ) + 1 )],
                          'M_bl' : [i * 10 for i in range ( int( 1000 / 20 ) + 1 )],
                          'angle_bl' : [round( i * 0.2, 2 ) for i in range ( int( 4 / 0.2 ) + 1 )],
                          'Mjj' : [i * 25 for i in range ( int( 500 / 25 ) + 1 )],
                          }
bin_edges = {
# 'hadTopRap' : [-3.0, -0.47100000000000003, 0.0, 0.47100000000000003, 3.0],
# 'lepTopPt' : [0.0, 78.00582296558886, 156.01164593117775, 262.0195591921062, 400.0298613619942, 865.0645751953126],
# 'hadTopPt' : [0.0, 82.01796010578649, 167.03657728861393, 836.1831054687499],
# 'ttbarPt' : [0.0, 73.08446987841735, 791.915283203125],
# 'ttbarM' : [250.0, 467.0353802977426, 740.0798909949027, 2267.328857421875],
# 'lepTopRap' : [-3.0, -0.441, 0.0, 0.441, 3.0],
# 'ttbarRap' : [-3.0, -1.452, -0.771, -0.264, 0.0, 0.264, 0.771, 1.452, 3.0],

# 'MET' : [0.0, 44.0, 102.0, 334.0],
# 'WPT' : [0.0, 44.0, 85.0, 131.0, 315.0],
# 'NJets' : [3.5, 4.5, 5.5, 9.5],
# 'HT' : [100.0, 212.0, 251.0, 294.0, 341.0, 391.0, 465.0, 761.0],
# 'ST' : [123.0, 319.0, 379.0, 446.0, 522.0, 606.0, 942.0],
# 'lepton_pt' : [23.0, 36.0, 43.0, 50.0, 58.0, 68.0, 81.0, 101.0, 181.0],
# 'abs_lepton_eta' : [0.0, 0.159, 0.315, 0.48000000000000004, 0.648, 0.8310000000000001, 1.0319999999999998, 1.272, 2.232000000000001],

'MET' : [0.0, 48.0, 99.0, 175.0, 300.0],
'WPT' : [0.0, 49.0, 90.0, 137.0, 325.0],
'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 10.5],
'HT' : [100.0, 235.0, 284.0, 340.0, 425.0, 600.0, 1000.0],
'ST' : [123.0, 349.0, 408.0, 476.0, 578.0, 700.0, 1200.0],
'lepton_pt' : [23.0, 39.0, 49.0, 61.0, 81.0, 120, 200.0],
'abs_lepton_eta' : [0.0, 0.25, 0.5, 0.8, 1.1, 1.5, 2.1],

# 'bjets_pt' : [30.0, 45.0, 62.0, 82.0, 106.0, 135.0, 250.0],
# 'bjets_eta' : [-2.0, -1.0, 0.0, 1.0, 2.0],
# 'abs_bjets_eta' : [0.0, 1.0, 2.0],
}

bin_edges_vis = {
# 'hadTopRap' : [-3.0, -0.47400000000000003, 0.0, 0.47400000000000003, 3.0],
# 'lepTopPt' : [0.0, 79.00589761899386, 156.01164593117775, 256.0191112716763, 388.0289655211344, 865.0645751953126],
# 'hadTopPt' : [0.0, 80.01752205442584, 162.0354821602123, 836.1831054687499],
# 'ttbarPt' : [0.0, 45.052070472997, 123.14232595952514, 791.915283203125],
# 'ttbarM' : [250.0, 428.0290216267198, 576.0531519680375, 882.1030430791399, 2267.328857421875],
# 'lepTopRap' : [-3.0, -1.0979999999999999, -0.438, 0.0, 0.438, 1.0979999999999999, 3.0],
# 'ttbarRap' : [-3.0, -1.3679999999999999, -0.93, -0.54, -0.195, 0.0, 0.195, 0.54, 0.93, 1.3679999999999999, 3.0],

# 'MET' : [0.0, 51.0, 97.0, 281.0],
# 'WPT' : [0.0, 57.0, 99.0, 146.0, 334.0],
# 'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 10.5],
# 'HT' : [100.0, 243.0, 300.0, 375.0, 675.0],
# 'ST' : [123.0, 360.0, 431.0, 524.0, 896.0],
# 'lepton_pt' : [23.0, 39.0, 50.0, 66.0, 120.0, 200.0],
# 'abs_lepton_eta' : [0.0, 0.3, 0.6, 0.9, 2.1],

# 'MET' : [0.0, 48.0, 99.0, 303.0],
# 'WPT' : [0.0, 49.0, 90.0, 137.0, 325.0],
# 'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 10.5],
# 'HT' : [100.0, 235.0, 284.0, 340.0, 425.0, 765.0],
# 'ST' : [123.0, 349.0, 408.0, 476.0, 578.0, 986.0],
# 'lepton_pt' : [23.0, 39.0, 49.0, 61.0, 81.0, 120, 200.0],
# 'abs_lepton_eta' : [0.0, 0.25, 0.5, 0.8, 1.1, 2.1],

'MET' : [0.0, 48.0, 99.0, 175.0, 300.0],
'WPT' : [0.0, 49.0, 90.0, 137.0, 325.0],
'NJets' : [3.5, 4.5, 5.5, 6.5, 7.5, 10.5],
'HT' : [100.0, 235.0, 284.0, 340.0, 425.0, 600.0, 1000.0],
'ST' : [123.0, 349.0, 408.0, 476.0, 578.0, 700.0, 1200.0],
'lepton_pt' : [23.0, 39.0, 49.0, 61.0, 81.0, 120, 200.0],
'abs_lepton_eta' : [0.0, 0.25, 0.5, 0.8, 1.1, 1.5, 2.1],

# 'bjets_pt' : [30, 50, 70, 100, 300],
# 'bjets_eta' : [-2.0, -1.0, 0.0, 1.0, 2.0],
# 'abs_bjets_eta' : [0.0, 1.0, 2.0],
}

control_plots_bins = {
  'NJets' : [i + 0.5 for i in range ( 3, 10 + 1 )],
  'JetPt' : [i * 5  for i in range ( 5, 40 )],  
  'MuonPt' : [i * 11.5 for i in range ( 2, 20 )],
  'ElectronPt' : [i * 10 for i in range ( 3, 20 )],
  'LeptonEta' : [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5],  
  'AbsLeptonEta' : [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.1],  
  'NBJets' : [i + 0.5 for i in range ( 1, 6 + 1 )],
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
