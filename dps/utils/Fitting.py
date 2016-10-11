'''
Created on 30 Oct 2012

@author: kreczko
'''

from ROOT import TMinuit, TMath, Long, Double
from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, RooHistPdf, \
RooArgSet, RooAddPdf, RooMsgService, RooProdPdf, RooGaussian, RooLinkedList, \
RooCategory, RooSimultaneous, RooDataSet, RooRealSumPdf, RooHistFunc
from array import array
import math
import logging
from .hist_utilities import adjust_overflow_to_limit
import rootpy.stl as stl
from copy import deepcopy
# RooFit is really verbose. Make it stop
RooMsgService.instance().setGlobalKillBelow( RooFit.FATAL )
# from scipy.optimize import curve_fit
# Create python mappings to map and pair

def generate_templates_and_normalisation( histograms ):
    normalisation = {}
    normalisation_errors = {}
    templates = {}

    for sample, histogram in histograms.iteritems():
        normalisation[sample] = histogram.Integral()
        normalisation_errors[sample] = sum( histogram.yerravg() )
        temp = histogram.Clone( sample + '_' + 'template' )
        nEntries = temp.Integral()
        if not nEntries == 0:
            temp.Scale( 1.0 / nEntries )
        templates[sample] = temp
    return templates, normalisation, normalisation_errors

def vectorise( histograms ):
    values = {}
    errors = {}
    for sample in histograms.keys():
        hist = histograms[sample]
        nBins = hist.GetNbinsX()
        for bin_i in range( 1, nBins + 1 ):
            if not values.has_key( sample ):
                values[sample] = []
                errors[sample] = []
            values[sample].append( hist.GetBinContent( bin_i ) )
            errors[sample].append( hist.GetBinError( bin_i ) )
    return values, errors

class FitData():
    data_label = 'data'

    def __init__( self, real_data, mc_histograms, fit_boundaries ):
        self.histograms_ = deepcopy( mc_histograms )
        self.histograms_[FitData.data_label] = deepcopy( real_data )
        # put all events outside the range into the
        # first or last bin
        for sample, histogram in self.histograms_.iteritems():
            self.histograms_[sample] = adjust_overflow_to_limit( histogram, fit_boundaries[0], fit_boundaries[1] )
        self.fit_boundaries = fit_boundaries

        keys = sorted( mc_histograms.keys() )
        self.samples = keys
        self.templates, self.normalisation, self.normalisation_errors = generate_templates_and_normalisation( self.histograms_ )
        self.vectors, self.errors = vectorise( self.templates )

    def n_data( self ):
        return self.normalisation[FitData.data_label]

    def real_data_histogram( self ):
        return self.histograms_[FitData.data_label]

    def real_data_roofit_histogram( self ):
        return self.roofit_histograms[self.data_label]

class FitDataCollection():
    default_name_prefix = 'var'
    def __init__( self ):
        self.fit_data = {}
        self.n_fit_data = 0
        self.normalisation = {}
        self.constraint_type = ''
        self.constraints_ = {}

    def add( self, fit_data, name = '' ):
        if name == '':
            name = self.default_name_prefix + str( self.n_fit_data )

        if self.fit_data.has_key( name ):
            raise UserWarning( name + 'is already registered with this collection. It will be overwritten!' )
        self.normalisation[name] = fit_data.normalisation
        self.fit_data[name] = fit_data
        self.n_fit_data += 1

    def is_valid_for_simultaneous_fit( self ):
        if self.n_fit_data == 1:
            return True

        data_normalisation = []
        n_samples = []
        for _, data in self.fit_data.iteritems():
            data_normalisation.append( data.n_data() )
            n_samples.append( len( data.samples ) )
        # check if all are the same
        has_same_n_data = reduce( lambda x, y: x if round( abs( x - y ) ) <= ((x + y)/2 * 0.01) else False, data_normalisation ) != False
        mc_samples = self.mc_samples()
        n_samples.append( len( mc_samples ) )
        has_same_n_samples = reduce( lambda x, y: x if x == y else False, n_samples ) != False
        self.has_same_n_data = has_same_n_data
        self.has_same_n_samples = has_same_n_samples

        return has_same_n_data and has_same_n_samples

    def mc_samples( self ):
        samples = []
        for _, data in self.fit_data.iteritems():
            samples.extend( data.samples )
        return sorted( set( samples ) )

    def mc_normalisation( self, name = '' ):
        if self.n_fit_data == 1:
            return self.fit_data.items()[0][1].normalisation
        if not name == '':
            return self.fit_data[name].normalisation
        else:
            normalisation = {}
            for dist, data in self.fit_data.iteritems():
                normalisation[dist] = data.normalisation
            return normalisation

    def mc_normalisation_errors( self, name = '' ):
        if self.n_fit_data == 1:
            return self.fit_data.items()[0][1].normalisation_errors
        if not name == '':
            return self.fit_data[name].normalisation_errors
        else:
            normalisation_errors = {}
            for dist, data in self.fit_data.iteritems():
                normalisation_errors[dist] = data.normalisation_errors
            return normalisation_errors

    def n_data( self, name = '' ):
        if self.n_fit_data == 1:
            return self.fit_data.items()[0][1].n_data()
        if not name == '':
            return self.fit_data[name].n_data()
        else:
            normalisation = {}
            for dist, data in self.fit_data.iteritems():
                normalisation[dist] = data.n_data()
            return normalisation

    def max_n_data( self ):
        n_data = self.n_data()
        if type( n_data ) == dict:
            return max( [n for _, n in n_data.iteritems()] )
        else:
            return n_data

    def vectors( self, name = '' ):
        if self.n_fit_data == 1:
            return self.fit_data.items()[0][1].vectors
        if not name == '':
            return self.fit_data[name].vectors
        else:
            vectors = {}
            for dist, data in self.fit_data.iteritems():
                vectors[dist] = data.vectors
            return vectors

    def set_normalisation_constraints( self, constraints ):
        self.constraint_type = 'normalisation'
        self.constraints_ = constraints

    def constraints( self ):
        return self.constraints_

class Minuit():

    fitfunction = None

    def __init__( self, fit_data_collection, method = 'logLikelihood', verbose = False ):
        # only simultaneous fit data is supported!
#         assert( fit_data_collection.is_valid_for_simultaneous_fit() )
        self.method = method
        self.logger = logging.getLogger( 'TMinuitFit' )
        self.constraints = {}
        self.constraint_type = ''
        self.verbose = verbose  # prints the correlation matrix, fit info
        self.fit_data_collection = fit_data_collection
        self.samples = fit_data_collection.mc_samples()
        self.normalisation = fit_data_collection.mc_normalisation()
        self.n_distributions = fit_data_collection.n_fit_data
        self.distributions = fit_data_collection.fit_data.keys()
        self.vectors = fit_data_collection.vectors()
        self.param_indices = {}

    def fit( self ):
        numberOfParameters = len( self.samples )
        gMinuit = TMinuit( numberOfParameters )
        if self.method == 'logLikelihood':  # set function for minimisation
            gMinuit.SetFCN( self.logLikelihood )

        gMinuit.SetMaxIterations(1000000000000)
        
        # set Minuit print level
        # printlevel  = -1  quiet (also suppress all warnings)
        #            =  0  normal
        #            =  1  verbose
        #            =  2  additional output giving intermediate results.
        #            =  3  maximum output, showing progress of minimizations.
        gMinuit.SetPrintLevel( -1 )

        # Error definition: 1 for chi-squared, 0.5 for negative log likelihood
        # SETERRDEF<up>: Sets the value of UP (default value= 1.), defining parameter errors.
        # Minuit defines parameter errors as the change in parameter value required to change the function value by UP.
        # Normally, for chisquared fits UP=1, and for negative log likelihood, UP=0.5.
        gMinuit.SetErrorDef( 0.5 )

        # error flag for functions passed as reference.set to as 0 is no error
        errorFlag = Long( 2 )

        N_min = 0
        N_max = self.fit_data_collection.max_n_data() * 2

        param_index = 0

        # MNPARM
        # Implements one parameter definition:
        # mnparm(k, cnamj, uk, wk, a, b, ierflg)
        #     K     (external) parameter number
        #     CNAMK parameter name
        #     UK    starting value
        #     WK    starting step size or uncertainty
        #     A, B  lower and upper physical parameter limits
        # and sets up (updates) the parameter lists.
        # Output: IERFLG  =0 if no problems
        #                >0 if MNPARM unable to implement definition
        for sample in self.samples:  # all samples but data
            if self.n_distributions > 1:
                gMinuit.mnparm( param_index, sample, self.normalisation[self.distributions[0]][sample], 10.0, N_min, N_max, errorFlag )
            else:
                gMinuit.mnparm( param_index, sample, self.normalisation[sample], 10.0, N_min, N_max, errorFlag )
            param_index += 1

        arglist = array( 'd', 10 * [0.] )

        # minimisation strategy: 1 standard, 2 try to improve minimum (a bit slower)
        arglist[0] = 2

        # minimisation itself
        # SET STRategy<level>: Sets the strategy to be used in calculating first and second derivatives and in certain minimization methods.
        # In general, low values of <level> mean fewer function calls and high values mean more reliable minimization.
        # Currently allowed values are 0, 1 (default), and 2.
        gMinuit.mnexcm( "SET STR", arglist, 1, errorFlag )

        gMinuit.Migrad()
        gMinuit.mnscan() # class for minimization using a scan method to find the minimum; allows for user interaction: set/change parameters, do minimization, change parameters, re-do minimization etc. 

        gMinuit.mnmatu( 1 )  # prints correlation matrix (always needed)

        self.module = gMinuit
        self.performedFit = True

        if not self.module:
            raise Exception( 'No fit results available. Please run fit method first' )

        results = {}
        param_index = 0
        for sample in self.samples:
            temp_par = Double( 0 )
            temp_err = Double( 0 )
            self.module.GetParameter( param_index, temp_par, temp_err )
            if ( math.isnan( temp_err ) ):
                self.logger.warning( 'Template fit error is NAN, setting to sqrt(N).' )
                temp_err = math.sqrt( temp_par )
            
#             gMinuit.Command("SCAn %i %i %i %i" % ( param_index, 100, N_min, N_total ) );
#             scan = gMinuit.GetPlot()
#             results[sample] = ( temp_par, temp_err, scan )
            results[sample] = ( temp_par, temp_err )
            param_index += 1
            
# #         gMinuit.Command("CONtour 1 2 3 50")
#         gMinuit.SetErrorDef(1)
#         results['contour'] = [gMinuit.Contour(100, 0, 1)]
#         gMinuit.SetErrorDef(4)
#         results['contour'].append(gMinuit.Contour(100, 0, 1))

        self.results = results

    def logLikelihood( self, nParameters, gin, f, par, iflag ):
        # nParameters= number of free parameters involved in the minimisation
        # gin = computed gradient values (optional)
        # f = the function value itself
        # par = vector of constant and variable parameters
        # flag = to switch between several actions of FCN

        lnL = 0.0
        if self.n_distributions > 1:
            lnL = sum( [self.build_single_LL( self.vectors[distribution][FitData.data_label],
                                       self.vectors[distribution],
                                       self.normalisation[distribution],
                                       par ) for distribution in self.distributions] )
        else:
            lnL = self.build_single_LL( self.vectors[FitData.data_label],
                                       self.vectors,
                                       self.normalisation,
                                       par )

        f[0] = -2.0 * lnL / self.n_distributions

        # Adding the QCD and V+jets constraints
        if self.fit_data_collection.constraint_type == 'normalisation':
            f[0] += self.get_fit_normalisation_constraints( par )
        # print 'Par :',par[0], 'f[0]',f[0], 'lnL',lnL

    def build_single_LL( self, data_vector, mc_vectors, normalisation, par ):
        lnL = 0.0
        for vector_entry, v_data in enumerate( data_vector ):
            x_i = 0
            param_index = 0
            for sample in self.samples:
                x_i += par[param_index] * mc_vectors[sample][vector_entry]
                self.param_indices[sample] = param_index
                param_index += 1
            data_i = normalisation[FitData.data_label] * v_data
            L = TMath.Poisson( data_i, x_i )
            if not L == 0:
                lnL += math.log( L )
            else:
                lnL += -1e10
        return lnL

    def get_fit_normalisation_constraints( self, params ):
        ''' Only valid for simultanous fit for now'''
        result = 0
        for sample, constraint in self.fit_data_collection.constraints().iteritems():
            normalisation = 0
            if self.n_distributions > 1:
                normalisation = self.normalisation.items()[0][1][sample]
            else:
                normalisation = self.normalisation[sample]

            if normalisation != 0:
                result += ( params[self.param_indices[sample]] - normalisation ) ** 2 / ( constraint * normalisation ) ** 2
        return result

    def readResults( self ):
        return self.results

# This class name won't cause any confusion, right?
class RooFitFit():

    def __init__( self, fit_data_collection, method = 'TMinuit' ):
        RooMsgService.instance().setGlobalKillBelow( RooFit.FATAL )
        self.method = method
        self.logger = logging.getLogger( 'RooFit' )
        self.constraints = fit_data_collection.constraints()
        self.constraint_type = ''
        self.saved_result = None

        self.fit_data_collection = fit_data_collection
        self.samples = fit_data_collection.mc_samples()
        self.normalisation = fit_data_collection.mc_normalisation()

        self.fit_data_1 = self.fit_data_collection.fit_data.items()[0][1]
        self.fit_boundaries = self.fit_data_1.fit_boundaries
        self.data_label = FitData.data_label
        self.histograms = self.fit_data_1.histograms_

    def fit( self ):
        fit_variable = RooRealVar( "fit_variable", "fit_variable", self.fit_boundaries[0], self.fit_boundaries[1] )
        fit_variable.setBins( self.histograms[self.data_label].nbins() )
        variables = RooArgList()
        variables.add( fit_variable )
        variable_set = RooArgSet()
        variable_set.add( fit_variable )

        roofit_histograms = {}
        roofit_pdfs = {}
        roofit_variables = {}

        N_min = 0.
        N_max = self.normalisation[self.data_label] * 2.
        pdf_arglist = RooArgList()
        variable_arglist = RooArgList()

        roofit_histograms[self.data_label] = RooDataHist( self.data_label,
                                                         self.data_label,
                                                         variables,
                                                         self.histograms[self.data_label] )
        for sample in self.samples:
            roofit_histogram = RooDataHist( sample, sample, variables, self.histograms[sample] )
            roofit_histograms[sample] = roofit_histogram
            roofit_pdf = RooHistPdf ( 'pdf' + sample, 'pdf' + sample, variable_set, roofit_histogram)
            roofit_pdfs[sample] = roofit_pdf
            roofit_variable = RooRealVar( sample, sample + " events",
                                          self.normalisation[sample],
                                          N_min,
                                          N_max )
            roofit_variables[sample] = roofit_variable
            pdf_arglist.add( roofit_pdf )
            variable_arglist.add( roofit_variable )

        model = RooAddPdf( 'model',
                           'sum of all known',
                           pdf_arglist,
                           variable_arglist)
        use_model = model
        if self.constraints:
            arg_set = RooArgSet( model )
            constraints = self.get_fit_normalisation_constraints( model, roofit_variables )
            for constraint in constraints:
                arg_set.add( constraint )
            model_with_constraints = RooProdPdf( "model_with_constraints",
                                                "model  with gaussian constraints",
                                                arg_set,
                                                RooLinkedList()
                                                )
            use_model = model_with_constraints

        if self.method == 'TMinuit':
            #WARNING: number of cores changes the results!!!
            self.saved_result = use_model.fitTo(
                        roofit_histograms[self.data_label],
                        RooFit.Minimizer( "Minuit", "Migrad" ),
                        RooFit.NumCPU( 1 ),
                        RooFit.Extended(),
                        RooFit.Save(),
                        )

        results = {}
        for sample in self.samples:
            results[sample] = ( roofit_variables[sample].getVal(), roofit_variables[sample].getError() )
        self.results = results

    def get_fit_normalisation_constraints( self, model, roofit_variables ):
        result = []
        for sample, constraint in self.constraints.iteritems():
            if self.normalisation[sample] != 0:
                roo_constraint = RooGaussian( sample + "_constraint",
                                             sample + "_constraint",
                                             roofit_variables[sample],
                                             RooFit.RooConst( self.normalisation[sample] ),
                                             RooFit.RooConst( constraint * self.normalisation[sample] ),
                                             )
                result.append( roo_constraint )
        return result

    def readResults( self ):
        return self.results

# experimental
class Observable():
    def __init__( self, name, title, value, min_value, max_value, unit ):
        assert( value >= min_value )
        assert( value <= max_value )
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.name = name
        self.title = title
        self.roofit = RooRealVar( name, title, value, min_value, max_value )  # , unit )

    def roofit_object( self ):
        return self.roofit

# experimental
class SimultaneousFit():
    ''' A fit that performs a simultaneous fit in more than one variable.
    It expects the input of fit_data which is a dictionary of the form
    {variable_name: FitData()}'''
    def __init__( self, fit_data ):
        MapStrRootPtr = stl.map( stl.string, "TH1*" )
        StrHist = stl.pair( stl.string, "TH1*" )
        self.fit_data = fit_data
        self.models = {}
        self.sample = RooCategory( 'sample', 'sample' )
        self.roofit_variables = []
        input_hists = MapStrRootPtr()

        # first create observables
        # Since we are looking for normalisation in equivalent regions
        # the number of events in each sample has to be identical
        # Hence, pick one fit_data to create the set of observables
        fit_data_1 = fit_data.itervalues().next()
        samples = fit_data_1.samples
        self.observables = {}
        N_min = 0
        N_max = fit_data_1.n_data() * 2
        for sample in samples:
            self.observables[sample] = Observable( 'n_' + sample,
                                                  'number of ' + sample + " events",
                                                  fit_data_1.normalisation[sample],
                                                  N_min,
                                                  N_max,
                                                  "events" )

        # next create the models
        for variable, fit_input in fit_data.iteritems():
            self.models[variable] = fit_input.get_roofit_model( variable, self.observables )
            self.sample.defineType( variable )
            self.sample.setLabel ( variable )
            data = deepcopy( fit_input.real_data_histogram() )
            input_hists.insert( StrHist( variable, data ) )
            self.roofit_variables.append( fit_input.fit_variable )
        self.comb_data = RooDataHist( "combData",
                                    "combined data",
                                    RooArgList( self.roofit_variables[0] ),
                                    self.sample,
                                    input_hists,
                                    )

    def fit( self ):
        sim_pdf = RooSimultaneous( "simPdf", "simultaneous pdf", self.sample )
        self.individual_results = {}
        for name, model in self.models.iteritems():
            fit_input = self.fit_data[name]
            model.fitTo( fit_input.real_data_roofit_histogram() )
            self.individual_results[name] = fit_input.get_results()
            sim_pdf.addPdf( model, name )

        argument_list = RooLinkedList()
        argument_list.Add( RooFit.Minimizer( "Minuit2", "Migrad" ) )
        argument_list.Add( RooFit.NumCPU( 1 ) )
        argument_list.Add( RooFit.Extended() )
        argument_list.Add( RooFit.Save() )

        sim_pdf.fitTo( self.comb_data,
#                        argument_list
                       )

#         sim_pdf.fitTo( self.combined_data,
#                        RooFit.Minimizer( "Minuit2", "Migrad" ) )

#         sim_pdf.fitTo( data = self.combined_data,
#                        arg1 = RooFit.Minimizer( "Minuit2", "Migrad" ),
#                        arg2 = RooFit.NumCPU( 1 ),
#                        arg3 = RooFit.Extended(),
#                        arg4 = RooFit.Save() )
#         sim_pdf.fitTo( self.combined_data,
#                        argument_list )

        # get fit results
        results = {}
        for variable, fit_input in self.fit_data.iteritems():
            results[variable] = fit_input.get_results()
        self.results = results
        return results
