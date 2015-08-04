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

'WPT' : [0.0, 40.0, 77.0, 116.0, 161.0, 341.0],
'MET' : [0.0, 40.0, 85.0, 265.0],
'ST' : [130.0, 317.0, 367.0, 422.0, 481.0, 556.0, 856.0],
'HT' : [100.0, 209.0, 250.0, 294.0, 343.0, 405.0, 514.0, 950.0],
'NJets' : [3.5, 4.5, 5.5, 9.5],

# 'lepton_pt' : [30.0, 37.0, 44.0, 52.0, 61.0, 73.0, 90.0, 120],
# 'lepton_eta' : [-2.5, -1.15, -0.7, -0.35, 0, 0.35, 0.7, 1.15, 2.5],
# 'abs_lepton_eta' : [0, 0.35, 0.7, 1.15, 2.5],

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

'WPT' : [0.0, 58.0, 96.0, 140.0, 316.0],
'MET' : [0.0, 48.0, 86.0, 238.0],
'ST' : [130.0, 355.0, 431.0, 543.0, 991.0],
'HT' : [100.0, 239.0, 301.0, 394.0, 766.0],
'NJets' : [3.5, 4.5, 5.5, 9.5],

# 'lepton_pt' : [30.0, 40.0, 52.0, 71.0, 150.0],
# 'lepton_eta' : [-2.5, -0.7, 0, 0.7, 2.5],
# 'abs_lepton_eta' : [0, 0.7, 2.5],

# 'bjets_pt' : [30, 50, 70, 100, 300],
# 'bjets_eta' : [-2.0, -1.0, 0.0, 1.0, 2.0],
# 'abs_bjets_eta' : [0.0, 1.0, 2.0],
}

control_plots_bins = {
  'NJets' : [i + 0.5 for i in range ( 3, 13 + 1 )],
  # 'NJets' : [i*0.25 for i in range ( 0, 40 + 1 )],
  'JetPt' : [i * 5  for i in range ( 5, 40 )],  
  'LeptonPt' : [i * 10 for i in range ( 3, 20 )],  
  'LeptonEta' : [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5],  
  'AbsLeptonEta' : [0.0, 0.5, 1.0, 1.5, 2.0, 2.1, 2.5, 3.0],  
  'NBJets' : [i + 0.5 for i in range ( 1, 6 + 1 )],
  'NVertex' : [i*2 for i in range ( 0,20 + 1 )],
  'relIso' : [i*0.01 for i in range(0,15)],
  'relIsoQCD' : [i*0.2 for i in range(0,15)],
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
    number_of_edges = len( bin_edges[variable] )
    for i in range( number_of_edges - 1 ):
        lower_edge = bin_edges[variable][i]
        upper_edge = bin_edges[variable][i + 1]
        bin_widths[variable].append( upper_edge - lower_edge )
        bin_name = '%d-%d' % ( int( lower_edge ), int( upper_edge ) )
        bin_name_latex = '%d--%d~\GeV' % ( int( lower_edge ), int( upper_edge ) )
        if ( i + 1 ) == number_of_edges - 1:
            bin_name = '%d-inf' % int( lower_edge )
            bin_name_latex = '$\\geq %d$~\GeV' % int( lower_edge )
        variable_bins_ROOT[variable].append( bin_name )
        variable_bins_latex[bin_name] = bin_name_latex
