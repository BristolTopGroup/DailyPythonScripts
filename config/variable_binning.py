fit_variable_bin_edges = {
                          'absolute_eta' : [round( i * 0.2, 2 ) for i in range ( int( 3 / 0.2 ) + 1 )],
                          'M3' : [i * 25 for i in range ( int( 1000 / 25 ) + 1 )],
                          'M_bl' : [i * 10 for i in range ( int( 1000 / 20 ) + 1 )],
                          'angle_bl' : [round( i * 0.2, 2 ) for i in range ( int( 4 / 0.2 ) + 1 )],
                          }
bin_edges = {
             'MET':[0.0, 27.0, 52.0, 87.0, 130.0, 172.0, 300],
            'HT':[0.0, 186.0, 216.0, 249.0, 286.0, 326.0, 368.0, 412.0, 462.0, 516.0, 574.0, 634.0, 696.0, 781.0, 1000],
#             'HT':[186.0, 216.0, 249.0, 286.0, 326.0, 368.0, 412.0, 462.0, 516.0, 574.0, 634.0, 696.0, 781.0, 1000],
             'ST':[0.0, 277.0, 319.0, 361.0, 408.0, 459.0, 514.0, 573.0, 637.0, 705.0, 774.0, 854.0, 946.0, 1200],
             'MT':[0.0, 23.0, 58.0, 100],
             'WPT':[0.0, 27.0, 52.0, 78.0, 105.0, 134.0, 166.0, 200.0, 237.0, 300]
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
