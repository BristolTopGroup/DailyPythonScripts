from dps.config import CMS
from optparse import OptionParser
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from dps.utils.plotting import Histogram_properties

from matplotlib import pyplot as plt
from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import Hist2D
import linecache
from dps.config.variable_binning import variable_bins_ROOT
from dps.config.latex_labels import samples_latex

def get_fit_results( variable, channel ):
    global path_to_JSON, category, met_type
    fit_results = read_data_from_JSON( path_to_JSON + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt' )
    return fit_results

def make_correlation_plot_from_file( channel, variable, fit_variables, CoM, title, x_title, y_title, x_limits, y_limits, rebin = 1, save_folder = 'plots/fitchecks/', save_as = ['pdf', 'png'] ):
# global b_tag_bin
    parameters = ["TTJet", "SingleTop", "V+Jets", "QCD"]
    parameters_latex = []
    for template in parameters:
        parameters_latex.append(samples_latex[template])
        
    input_file = open( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), "r" )
    # cycle through the lines in the file
    for line_number, line in enumerate( input_file ):
        # for now, only make plots for the fits for the central measurement
        if "central" in line:
            # matrix we want begins 11 lines below the line with the measurement ("central")
            line_number = line_number + 11
            break
    input_file.close()
    
    #Note: For some reason, the fit outputs the correlation matrix with the templates in the following order:
    #parameter1: QCD
    #parameter2: SingleTop
    #parameter3: TTJet
    #parameter4: V+Jets
        
    for variable_bin in variable_bins_ROOT[variable]:
        weights = {}
        if channel == 'electron':
            #formula to calculate the number of lines below "central" to access in each loop
            number_of_lines_down = (variable_bins_ROOT[variable].index( variable_bin ) * 12)

            #Get QCD correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down )
            weights["QCD_QCD"] = matrix_line.split()[2]
            weights["QCD_SingleTop"] = matrix_line.split()[3]
            weights["QCD_TTJet"] = matrix_line.split()[4]
            weights["QCD_V+Jets"] = matrix_line.split()[5]

            #Get SingleTop correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down + 1 )
            weights["SingleTop_QCD"] = matrix_line.split()[2]
            weights["SingleTop_SingleTop"] = matrix_line.split()[3]
            weights["SingleTop_TTJet"] = matrix_line.split()[4]
            weights["SingleTop_V+Jets"] = matrix_line.split()[5]

            #Get TTJet correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down + 2 )
            weights["TTJet_QCD"] = matrix_line.split()[2]
            weights["TTJet_SingleTop"] = matrix_line.split()[3]            
            weights["TTJet_TTJet"] = matrix_line.split()[4]
            weights["TTJet_V+Jets"] = matrix_line.split()[5]

            #Get V+Jets correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down + 3 )
            weights["V+Jets_QCD"] = matrix_line.split()[2]
            weights["V+Jets_SingleTop"] = matrix_line.split()[3]
            weights["V+Jets_TTJet"] = matrix_line.split()[4]
            weights["V+Jets_V+Jets"] = matrix_line.split()[5]

        if channel == 'muon':
            #formula to calculate the number of lines below "central" to access in each bin loop
            number_of_lines_down =  ( len( variable_bins_ROOT [variable] ) * 12 ) + ( variable_bins_ROOT[variable].index( variable_bin ) * 12 )
            
            #Get QCD correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down )
            weights["QCD_QCD"] = matrix_line.split()[2]
            weights["QCD_SingleTop"] = matrix_line.split()[3]
            weights["QCD_TTJet"] = matrix_line.split()[4]
            weights["QCD_V+Jets"] = matrix_line.split()[5]

            #Get SingleTop correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down + 1 )
            weights["SingleTop_QCD"] = matrix_line.split()[2]
            weights["SingleTop_SingleTop"] = matrix_line.split()[3]
            weights["SingleTop_TTJet"] = matrix_line.split()[4]
            weights["SingleTop_V+Jets"] = matrix_line.split()[5]

            #Get TTJet correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down + 2 )
            weights["TTJet_QCD"] = matrix_line.split()[2]
            weights["TTJet_SingleTop"] = matrix_line.split()[3]
            weights["TTJet_TTJet"] = matrix_line.split()[4]
            weights["TTJet_V+Jets"] = matrix_line.split()[5]
            
            #Get V+Jets correlations
            matrix_line = linecache.getline( "logs/01_%s_fit_%dTeV_%s.log" % ( variable, CoM, fit_variables ), line_number + number_of_lines_down + 3 )
            weights["V+Jets_QCD"] = matrix_line.split()[2]
            weights["V+Jets_SingleTop"] = matrix_line.split()[3]
            weights["V+Jets_TTJet"] = matrix_line.split()[4]
            weights["V+Jets_V+Jets"] = matrix_line.split()[5]

        #Create histogram
        histogram_properties = Histogram_properties()
        histogram_properties.title = title
        histogram_properties.name = 'Correlations_' + channel + '_' + variable + '_' + variable_bin
        histogram_properties.y_axis_title = y_title
        histogram_properties.x_axis_title = x_title
        histogram_properties.y_limits = y_limits
        histogram_properties.x_limits = x_limits
        histogram_properties.mc_error = 0.0
        histogram_properties.legend_location = 'upper right'

        #initialise 2D histogram
        a = Hist2D( 4, 0, 4, 4, 0, 4 )
        #fill histogram
        for i in range( len( parameters ) ):
            for j in range( len( parameters ) ):
                a.fill( float( i ), float( j ), float( weights["%s_%s" % ( parameters[i], parameters[j] )] ) )
        # create figure
        plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
        # make subplot(?) 
        fig, ax = plt.subplots( nrows = 1, ncols = 1 )
        rplt.hist2d( a )
        plt.subplots_adjust( right = 0.8 )

        #Set labels and formats for titles and axes
        plt.ylabel( histogram_properties.y_axis_title )
        plt.xlabel( histogram_properties.x_axis_title )
        plt.title( histogram_properties.title )
        x_limits = histogram_properties.x_limits
        y_limits = histogram_properties.y_limits
        ax.set_xticklabels( parameters_latex )
        ax.set_yticklabels( parameters_latex )
        ax.set_xticks( [0.5, 1.5, 2.5, 3.5] )
        ax.set_yticks( [0.5, 1.5, 2.5, 3.5] )
        plt.setp( ax.get_xticklabels(), visible = True )
        plt.setp( ax.get_yticklabels(), visible = True )

        #create and draw colour bar to the right of the main plot
        im = rplt.imshow( a, axes = ax, vmin = -1.0, vmax = 1.0 )
        #set location and dimensions (left, lower, width, height)
        cbar_ax = fig.add_axes( [0.85, 0.10, 0.05, 0.8] )
        fig.colorbar( im, cax = cbar_ax )

        for xpoint in range( len( parameters ) ):
            for ypoint in range( len( parameters ) ):
                correlation_value = weights["%s_%s" % ( parameters[xpoint], parameters[ypoint] )]
                ax.annotate( correlation_value, xy = ( xpoint + 0.5, ypoint + 0.5 ), ha = 'center', va = 'center', bbox = dict( fc = 'white', ec = 'none' ) )
        for save in save_as:
            plt.savefig( save_folder + histogram_properties.name + '.' + save )
        plt.close(fig)
    plt.close('all')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/',
                  help = "set path to JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                  help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_option( "-f", "--fit-variables", dest = "fit_variables", default = 'absolute_eta',
                      help = "set the fit variable to use in the minimalisation" +
                           " (absolute_eta, M3, M_bl, angle_bl) or any" +
                           " combination separated by commas" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/fitchecks/',
                  help = "set path to save plots" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET-dependent variables" )
    parser.add_option( "-c", "--category", dest = "category", default = 'central',
                      help = "set the category to take the fit results from (default: central)" )
    parser.add_option( "-n", "--normalise_to_fit", dest = "normalise_to_fit", action = "store_true",
                  help = "normalise the MC to fit results" )
    parser.add_option( "-e", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                  help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
#    parser.add_option("-i", "--use_inputs", dest="use_inputs", action="store_true",
#                  help="use fit inputs instead of fit results")

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    lumi = measurement_config.new_luminosity
    CoM = measurement_config.centre_of_mass_energy
    electron_histogram_title = 'CMS Preliminary, $\mathcal{L}$ = %.1f fb$^{-1}$ at $\sqrt{s}$ = %d TeV \n e+jets, $\geq$4 jets' % ( lumi/1000.0, CoM )
    muon_histogram_title = 'CMS Preliminary, $\mathcal{L}$ = %.1f fb$^{-1}$ at $\sqrt{s}$ = %d TeV \n $\mu$+jets, $\geq$4 jets' % ( lumi/1000.0, CoM )

    path_to_JSON = options.path + '/' + str( CoM ) + 'TeV/'
    output_folder = options.output_folder + '/%dTeV/' % CoM
    make_folder_if_not_exists(output_folder)
    normalise_to_fit = options.normalise_to_fit
    category = options.category
    met_type = translate_options[options.metType]
    fit_variables = options.fit_variables.replace( ',' , '_' )

    histogram_files = {
            'electron' : measurement_config.data_file_electron,
            'muon' : measurement_config.data_file_muon,
            'TTJet': measurement_config.ttbar_category_templates[category],
            'V+Jets': measurement_config.VJets_category_templates[category],
            'QCD': measurement_config.electron_QCD_MC_file,  # this should also be category-dependent, but unimportant and not available atm
            'SingleTop': measurement_config.SingleTop_category_templates[category]
    }

    # make correlation plots for electron and muon channel
    make_correlation_plot_from_file( channel = 'electron',
                                     variable = options.variable,
                                     fit_variables = fit_variables,
                                     CoM = options.CoM,
                                     title = electron_histogram_title,
                                     x_title = '',
                                     y_title = '',
                                     x_limits = [0, 4],
                                     y_limits = [0, 4],
                                     rebin = 1,
                                     save_folder = output_folder,
                                     save_as = ['pdf'] )
    make_correlation_plot_from_file( channel = 'muon',
                                     variable = options.variable,
                                     CoM = options.CoM,
                                     fit_variables = fit_variables,
                                     title = muon_histogram_title,
                                     x_title = '',
                                     y_title = '',
                                     x_limits = [0, 3],
                                     y_limits = [0, 3],
                                     rebin = 1,
                                     save_folder = output_folder,
                                     save_as = ['pdf'] )
