fit_variable_bin_edges = {
                          'absolute_eta' : [round( i * 0.2, 2 ) for i in range ( int( 3 / 0.2 ) + 1 )],
                          'M3' : [i * 25 for i in range ( int( 1000 / 25 ) + 1 )],
                          'M_bl' : [i * 10 for i in range ( int( 1000 / 20 ) + 1 )],
                          'angle_bl' : [round( i * 0.2, 2 ) for i in range ( int( 4 / 0.2 ) + 1 )],
                          }
bin_edges = {
                'WPT' : [0.0, 43.0, 88.0, 139.0, 203.0, 300.0],
                'MET' : [0.0, 37.0, 98.0, 300.0],
                'MT' : [0.0, 59.0, 100.0],
                'HT' : [0.0, 200.0, 252.0, 308.0, 369.0, 437.0, 513.0, 597.0, 693.0, 800.0, 926.0, 1000.0],
                'ST' : [0.0, 302.0, 365.0, 439.0, 523.0, 620.0, 731.0, 858.0, 1008.0, 1200.0],
             }

control_plots_bins = {
  'NJets' : [i + 0.5 for i in range ( 4 - 1, 13 + 1 )],
  'pt' : [i * 15 for i in range ( 0,40 )],  
  'NBJets' : [i + 0.5 for i in range ( 2 - 1, 6 + 1 )],
  'NPV' : [i for i in range ( 0,60 + 1 )],
  'relIso_03_deltaBeta' : [i for i in range ( 0,2 + 1 )],
  'relIso_04_deltaBeta' : [i for i in range ( 0,2 + 1 )],
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
