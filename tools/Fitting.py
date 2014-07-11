'''
Created on 30 Oct 2012

@author: kreczko
'''

from ROOT import TMinuit, TMath, Long, Double
from array import array
import math
import logging
from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, RooHistPdf, RooArgSet, RooAddPdf, RooMsgService
from ROOT import RooProdPdf, RooGaussian, RooLinkedList
# RooFit is really verbose. Make it stop
RooMsgService.instance().setGlobalKillBelow( RooFit.FATAL )
# from scipy.optimize import curve_fit

class TemplateFit():
    def __init__( self, histograms, data_label = 'data' ):
        self.performedFit = False
        self.results = {}
        self.normalisation = {}
        self.normalisation_errors = {}
        self.data_label = data_label
        self.histograms = histograms
        self.templates = {}
        self.module = None
        # samples = all inputs except data
        keys = sorted( histograms.keys() )
        keys.remove( data_label )
        self.samples = keys
        
        self.templates, self.normalisation, self.normalisation_errors = TemplateFit.generateTemplatesAndNormalisation( histograms )
        self.vectors, self.errors = TemplateFit.vectorise( self.templates )
        self.param_indices = {}
        # check for consistency
        # vectors and templates all same size!!
        data_length = len( self.vectors[data_label] )
        error = False
        for sample in self.vectors.keys():
            current_length = len( self.vectors[sample] )
            if not data_length == current_length:
                # TODO: This should be a while loop
                if current_length < data_length:
                    for entry in range( current_length, data_length ):
                        self.vectors[sample].append( 0. )
                        self.errors[sample].append( 0. )
                else:
                    print 'Error:'
                    print 'Sample "', sample, '" has different length'
                    print 'Expected:', data_length, ', found:', current_length
                    error = True
        if error:
            import sys
            sys.exit( -1 )
            
    def readResults( self ):
        return self.results
        
    @staticmethod
    def generateTemplatesAndNormalisation( histograms ):
        normalisation = {}
        normalisation_errors = {}
        templates = {}
        for sample, histogram in histograms.iteritems():
            normalisation[sample] = histogram.Integral()
            normalisation_errors[sample] = sum( histogram.yerravg() )
            temp = histogram.Clone( sample + '_' + 'template' )
            nEntries = temp.Integral()
            if not nEntries == 0:
                temp.Scale( 1 / nEntries )
            templates[sample] = temp
        return templates, normalisation, normalisation_errors
            
    @staticmethod
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
        
class TMinuitFit( TemplateFit ):
    
    fitfunction = None
    
    def __init__( self, histograms = {}, dataLabel = 'data', method = 'logLikelihood', verbose = False ):
        TemplateFit.__init__( self, histograms, dataLabel )
        self.method = method
        self.logger = logging.getLogger( 'TMinuitFit' )
        self.constraints = {}
        self.constraint_type = ''
        self.verbose = verbose  # prints the correlation matrix, fit info
        
    def fit( self ):
        numberOfParameters = len( self.samples )
        gMinuit = TMinuit( numberOfParameters )
        if self.method == 'logLikelihood':  # set function for minimisation
            gMinuit.SetFCN( self.logLikelihood )
            
        # set Minuit print level
        # printlevel  = -1  quiet (also suppresse all warnings)
        #            =  0  normal
        #            =  1  verbose
        #            =  2  additional output giving intermediate results. 
        #            =  3  maximum output, showing progress of minimizations. 
        gMinuit.SetPrintLevel( -1 )
        
        # Error definition: 1 for chi-squared, 0.5 for negative log likelihood
        # SETERRDEF<up>: Sets the value of UP (default value= 1.), defining parameter errors.
        # Minuit defines parameter errors as the change in parameter value required to change the function value by UP.
        # Normally, for chisquared fits UP=1, and for negative log likelihood, UP=0.5.
        gMinuit.SetErrorDef( 1 )
        
        # error flag for functions passed as reference.set to as 0 is no error
        errorFlag = Long( 2 )
        
        N_total = self.normalisation[self.data_label] * 2
        N_min = 0
        
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
            gMinuit.mnparm( param_index, sample, self.normalisation[sample], 10.0, N_min, N_total, errorFlag )
            param_index += 1
        
        
#        N_signal = self.normalisation['signal']
#        gMinuit.mnparm(0, "N_signal(ttbar+single_top)", N_signal, 10.0, N_min, N_total, errorFlag)
#        gMinuit.mnparm(1, "bkg1", 10, 10.0, N_min, N_total, errorFlag)
        
        arglist = array( 'd', 10 * [0.] )
        
        # minimisation strategy: 1 standard, 2 try to improve minimum (a bit slower)
        arglist[0] = 2
        
        # minimisation itself
        # SET STRategy<level>: Sets the strategy to be used in calculating first and second derivatives and in certain minimization methods.
        # In general, low values of <level> mean fewer function calls and high values mean more reliable minimization.
        # Currently allowed values are 0, 1 (default), and 2. 
        gMinuit.mnexcm( "SET STR", arglist, 1, errorFlag )
        
        gMinuit.Migrad()

        if self.verbose:
            gMinuit.mnmatu( 1 )  # prints correlation matrix

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
            
            results[sample] = ( temp_par, temp_err )
            param_index += 1
        
        self.results = results
    
    def logLikelihood( self, nParameters, gin, f, par, iflag ):
        # nParameters= number of free parameters involved in the minimisation
        # gin = computed gradient values (optional)
        # f = the function value itself
        # par = vector of constant and variable parameters
        # flag = to switch between several actions of FCN
        
        lnL = 0.0
        data_vector = self.vectors[self.data_label]
        
        vector_entry = 0
        for data in data_vector:
            x_i = 0
#            sumxerrorssquared_i = 0
            param_index = 0
            for sample in self.samples:
                x_i += par[param_index] * self.vectors[sample][vector_entry]
#                sumxerrorssquared_i += par[param_index] * self.errors[sample][vector_entry]**2
                self.param_indices[sample] = param_index
                param_index += 1
            data_i = self.normalisation[self.data_label] * data
            if not data == 0 and not x_i == 0:
                L = TMath.Poisson( data_i, x_i )
#                L = TMath.Gaus(data_i, x_i, ((data_i + sumxerrorssquared_i)**0.5))
#                L = TMath.Gaus(data_i, x_i, (x_i**0.5))
                lnL += math.log( L )
            
            
            
            vector_entry += 1
        
        f[0] = -2.0 * lnL
        
        # Adding the QCD and V+jets constraints
        if self.constraint_type == 'normalisation':
            f[0] += self.get_fit_normalisation_constraints( par )

    # constraints = {sample: constraint}
    def set_fit_constraints( self, constraints, constraint_type = 'normalisation' ):
        self.constraints = constraints
        self.constraint_type = constraint_type
    
    def get_fit_normalisation_constraints( self, params ):
        result = 0
        for sample, constraint in self.constraints.iteritems():
            if self.normalisation[sample] != 0:
                result += ( params[self.param_indices[sample]] - self.normalisation[sample] ) ** 2 / ( constraint * self.normalisation[sample] ) ** 2
        return result

# This class name won't cause any confusion, right?    
class RooFitFit( TemplateFit ):
    
    def __init__( self, histograms = {}, dataLabel = 'data', method = 'TMinuit', fit_boundries = ( 0., 2.4 ) ):
        RooMsgService.instance().setGlobalKillBelow( RooFit.FATAL )
        TemplateFit.__init__( self, histograms, dataLabel )
        self.method = method
        self.logger = logging.getLogger( 'RooFit' )
        self.fit_boundries = fit_boundries
        self.constraints = {}
        self.constraint_type = ''
        self.saved_result = None
        
    def fit( self ):
        fit_variable = RooRealVar( "fit_variable", "fit_variable", self.fit_boundries[0], self.fit_boundries[1] )
        variables = RooArgList()
        variables.add( fit_variable )
        variable_set = RooArgSet()
        variable_set.add( fit_variable )
        n_event_obs = self.histograms[self.data_label].Integral()
        roofit_histograms = {}
        roofit_pdfs = {}
        roofit_variables = {}
        
        N_total = self.normalisation[self.data_label] * 2
        N_min = 0
        pdf_arglist = RooArgList()
        variable_arglist = RooArgList()
        
        roofit_histograms[self.data_label] = RooDataHist( self.data_label,
                                                         self.data_label,
                                                         variables,
                                                         self.histograms[self.data_label] )
        for sample in self.samples:
            roofit_histogram = RooDataHist( sample, sample, variables, self.histograms[sample] )
            roofit_histograms[sample] = roofit_histogram
            roofit_pdf = RooHistPdf ( 'pdf' + sample, 'pdf' + sample, variable_set, roofit_histogram, 0 )
            roofit_pdfs[sample] = roofit_pdf
            roofit_variable = RooRealVar( sample, "number of " + sample + " events", self.normalisation[sample], N_min, N_total, "event" )
            roofit_variables[sample] = roofit_variable
            pdf_arglist.add( roofit_pdf )
            variable_arglist.add( roofit_variable )
                
        model = RooAddPdf( "model",
                          "sum of all known",
                          pdf_arglist,
                          variable_arglist
                          )
        use_model = model
        if self.constraints:
            arg_set = RooArgSet( model )
            constraints = self.get_fit_normalisation_constraints( model, roofit_variables )
            for constraint in constraints:
                arg_set.add( constraint )
            model_with_constraints = RooProdPdf( "model_with_constraints",
                                                "model with gaussian constraints",
                                                arg_set,
                                                RooLinkedList()
                                                )
            use_model = model_with_constraints
            
        if self.method == 'TMinuit':
            #WARNING: number of cores changes the results!!!
            self.saved_result = use_model.fitTo( 
                        roofit_histograms[self.data_label],
                        RooFit.Minimizer( "Minuit2", "Migrad" ),
                        RooFit.NumCPU( 1 ),
                        RooFit.Extended(),
                        RooFit.Save(),
                        )    
        results = {}
        for sample in self.samples:
            results[sample] = ( roofit_variables[sample].getVal(), roofit_variables[sample].getError() )    
        self.results = results
        
    # constraints = {sample: constraint}
    def set_fit_constraints( self, constraints, constraint_type = 'normalisation' ):
        self.constraints = constraints
        self.constraint_type = constraint_type
    
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
        
# class CurveFit():
#    defined_functions = ['gaus', 'gauss'] 
#    
#    @staticmethod
#    def gauss(x, *p):
#        A, mu, sigma = p
#        return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))
#    
#    @staticmethod
#    def fit(hist, function, params):
#        if type(function) == type('s'):#string input
#            if not function in CurveFit.defined_functions:
#                raise Exception('Unknown function')
#            if function == 'gaus' or function == 'gauss':
#                function = CurveFit.gauss
#        x,y = list(hist.x()), list(hist.y())
#        
#        coeff, var_matrix = curve_fit(function, x, y, p0=params)
#        print coeff, var_matrix
#        #this should be transferred into rootpy.TF1
#        hist_fit = function(x, *coeff)
#        return hist_fit, x
