'''
Created on 31 Oct 2012

@author: kreczko
'''
from ROOT import gSystem, cout, TDecompSVD
import config.RooUnfold as unfoldCfg
from tools.hist_utilities import hist_to_value_error_tuplelist, fix_overflow
gSystem.Load( unfoldCfg.library )
from ROOT import RooUnfoldResponse, RooUnfoldParms, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
from ROOT import RooUnfoldBinByBin, RooUnfoldInvert, RooUnfoldTUnfold
from ROOT import TSVDUnfold
from ROOT import TH2D, TH1D
from rootpy import asrootpy
from rootpy.plotting import Hist, Hist2D
from math import sqrt

class Unfolding:

    def __init__( self,
                 truth,
                 measured,
                 response,
                 fakes = None,
                 method = 'RooUnfoldSvd',
                 tau = unfoldCfg.SVD_tau_value,
                 k_value = unfoldCfg.SVD_k_value,
                 n_toy = unfoldCfg.SVD_n_toy,
                 Bayes_n_repeat = unfoldCfg.Bayes_n_repeat,
                 error_treatment = unfoldCfg.error_treatment,
                 measured_truth_without_fakes = None,
                 verbose = 0 ):
        if not method in unfoldCfg.availablemethods:
            raise ValueError( 'Unknown unfolding method "%s". Available methods: %s' % ( method, str( unfoldCfg.availablemethods ) ) )
        self.method = method        
        self.truth = truth
        self.measured = measured
        self.fakes = fakes
        self.response = response
        self.data = None
        self.unfolded_data = None
        self.unfoldObject = None
        self.unfoldResponse = None
        self.verbose = verbose
        self.tau = float(tau)
        self.k_value = int(k_value)
        self.n_toy = n_toy
        self.Bayes_n_repeat = Bayes_n_repeat
        self.error_treatment = error_treatment
        self.measured_truth_without_fakes = measured_truth_without_fakes
    
    def setup_unfolding ( self, data ):
        self.data = data
        if not self.unfoldObject:
            if not self.unfoldResponse:
                self.unfoldResponse = self._makeUnfoldResponse()
            if self.method == 'RooUnfoldBayes':
                self.unfoldObject = RooUnfoldBayes     ( self.unfoldResponse, self.data, self.Bayes_n_repeat )
            elif self.method == 'RooUnfoldBinByBin':
                self.unfoldObject = RooUnfoldBinByBin     ( self.unfoldResponse, self.data )
            elif self.method == 'RooUnfoldInvert':
                self.unfoldObject = RooUnfoldInvert     ( self.unfoldResponse, self.data )
            elif self.method == 'RooUnfoldSvd':
                if self.k_value > 0:
                    self.unfoldObject = RooUnfoldSvd( self.unfoldResponse, self.data, self.k_value, self.n_toy )
                else:
                    if self.tau >= 0:
                        self.unfoldObject = RooUnfoldSvd( self.unfoldResponse, self.data, self.tau, self.n_toy )
            elif self.method == 'RooUnfoldTUnfold':
                self.unfoldObject = RooUnfoldTUnfold ( self.unfoldResponse, data )
                if self.tau >= 0:
                    self.unfoldObject.FixTau( self.tau )
            elif self.method == 'TSVDUnfold':
                new_data = Hist( list( self.data.xedges() ), type = 'D' )
                new_data.Add( self.data )
                
                new_measured = Hist( list( self.measured.xedges() ), type = 'D' )
                new_measured.Add( self.measured )
                
                new_truth = Hist( list( self.truth.xedges() ), type = 'D' )
                new_truth.Add( self.truth )


                if self.fakes:
                    new_fakes = Hist( list ( self.fakes.xedges() ), type = 'D' )
                    new_fakes.Add ( self.fakes )
                    new_measured = new_measured - new_fakes

                new_response = Hist2D( list( self.response.xedges() ), list( self.response.yedges() ), type = 'D' )
                new_response.Add( self.response )

                # replace global objects with new ones
                self.data = new_data
                self.measured = new_measured
                self.truth = new_truth
                self.response = new_response

                self.unfoldObject = TSVDUnfold( self.data, self.measured, self.truth, self.response )

    def test_regularisation ( self, data, k_max ):
        self.setup_unfolding( data )
        if self.method == 'RooUnfoldSvd':
            findingK = RooUnfoldParms( self.unfoldObject, self.error_treatment, self.truth )
            findingK.SetMinParm( 1 )
            findingK.SetMaxParm( k_max )
            findingK.SetStepSizeParm( 1 )
            RMSerror = asrootpy( findingK.GetRMSError().Clone() )
            MeanResiduals = asrootpy( findingK.GetMeanResiduals().Clone() )
            RMSresiduals = asrootpy( findingK.GetRMSResiduals().Clone() )
            Chi2 = asrootpy( findingK.GetChi2().Clone() )
            return RMSerror, MeanResiduals, RMSresiduals, Chi2
        else:
            raise ValueError( 'Unfolding method "%s" is not supported for regularisation parameter tests. Please use RooUnfoldSvd.' % ( self.method ) )

    def unfold( self, data ):
        if data is None:
            raise ValueError('Data histogram is None')
        have_zeros = [value == 0 for value,_ in hist_to_value_error_tuplelist( data )]
        if not False in have_zeros:
            raise ValueError('Data histograms contains only zeros')
        self.setup_unfolding( data )
        if self.method == 'TSVDUnfold':
            self.unfolded_data = asrootpy( self.unfoldObject.Unfold( self.k_value ) )
        else:
            # remove unfold reports (faster)
            self.unfoldObject.SetVerbose( self.verbose )
            self.unfolded_data = asrootpy( self.unfoldObject.Hreco( self.error_treatment ) )
        return self.unfolded_data
    
    def closureTest( self ):
        return self.unfold(self.measured)
    
    def _makeUnfoldResponse( self ):
        if self.fakes:
            return RooUnfoldResponse ( self.measured, self.truth, self.fakes, self.response )
        else:
            return RooUnfoldResponse ( self.measured, self.truth, self.response )

    def printTable( self ):
        self.unfoldObject.PrintTable( cout, self.truth )
    
    def Reset( self ):
        if self.unfoldObject:
            self.unfoldObject = None
#         if self.closure_test:
#             self.closure_test = None
            
    def chi2( self ):
        chi2 = 99999999, 0
        if self.unfolded_data and self.truth:
            diff = self.truth - self.unfolded_data
            values = list( diff )
            errors = []
            for bin_i in range( len( values ) ):
                errors.append( diff.GetBinError( bin_i + 1 ) )
            values = [abs( value ) for value in values]
            errorsSquared = [error * error for error in errors]
            value = sum( values )
            error = sqrt( sum( errorsSquared ) )
            chi2 = value, error
        return chi2
    
    def pull( self ):
        result = [9999999]
        
        if self.unfolded_data and self.truth:
            diff = self.unfolded_data - self.truth 
            value_error_tuplelist = hist_to_value_error_tuplelist( diff )

            result = [value / error for value, error in value_error_tuplelist]
        
        return result
    
    def pull_inputErrorOnly( self ):
        result = [9999999]
        if self.unfolded_data and self.truth:
            # set unfolded_data errors to stat errors from data
            temp = self.unfolded_data.Clone()
            temp_list = list( temp.y() )
#            data_list = list(self.data)
            unfolded_errors = self.get_unfolded_data_errors()
            for bin_i in range( len( temp_list ) ):
                temp.SetBinError( bin_i + 1, unfolded_errors[bin_i] )
            # set truth errors to 0
            temp_truth = self.truth.Clone()
            for bin_i in range( len( temp_truth ) ):
                temp_truth.SetBinError( bin_i + 1, 0 )
                
            diff = temp - temp_truth
            errors = []
            values = list( diff.y() )
            for bin_i in range( len( values ) ):
                errors.append( diff.GetBinError( bin_i + 1 ) )
            result = [value / error for value, error in zip( values, errors )]
        return result
    
    def get_unfolded_data_errors( self ):
        # get the data errors
        input_errors = self.unfoldObject.Emeasured()
#        input_errors.Print()
        unfolded_errors = input_errors.Clone()
        # get the response matrix
        decomposition = TDecompSVD( self.unfoldResponse.Mresponse() );
        # apply R-1 to data errors
        decomposition.Solve( unfolded_errors );
        
        return unfolded_errors
    
    def Impl(self):
        return self.unfoldObject.Impl()
            
def get_unfold_histogram_tuple( 
                inputfile,
                variable,
                channel,
                met_type = 'patType1CorrectedPFMet',
                centre_of_mass = 8,
                ttbar_xsection = 245.8,
                luminosity = 19712,
                load_fakes = False,
                scale_to_lumi = True,
                ):
    folder = None
    h_truth = None
    h_measured = None
    h_response = None
    h_fakes = None
    if not channel == 'combined':
        if not 'HT' in variable:
            folder = inputfile.Get( 'unfolding_%s_analyser_%s_channel_%s' % ( variable, channel, met_type ) )
        else:
            folder = inputfile.Get( 'unfolding_%s_analyser_%s_channel' % ( variable, channel ) )
        
        h_truth = asrootpy( folder.truth.Clone() )
        h_measured = asrootpy( folder.measured.Clone() )
        # response matrix is always without fakes
        # fake subtraction from measured is performed automatically in RooUnfoldSvd (h_measured - h_response->ProjectionX())
        # or manually for TSVDUnfold
        # fix for a bug/typo in NTupleTools
        h_response = asrootpy( folder.response_without_fakes.Clone() )

        if load_fakes:
            h_fakes = asrootpy( folder.fake.Clone() )
    else:
        return get_combined_unfold_histogram_tuple( inputfile = inputfile,
                                                   variable = variable,
                                                   met_type = met_type,
                                                   centre_of_mass = centre_of_mass,
                                                   ttbar_xsection = ttbar_xsection,
                                                   luminosity = luminosity,
                                                   load_fakes = load_fakes,
                                                   scale_to_lumi = scale_to_lumi,
                                                   )

    if scale_to_lumi:
        nEvents = inputfile.EventFilter.EventCounter.GetBinContent( 1 )  # number of processed events 
        lumiweight = ttbar_xsection * luminosity / nEvents
        if load_fakes:
            h_fakes.Scale( lumiweight )
        h_truth.Scale( lumiweight )
        h_measured.Scale( lumiweight )
        h_response.Scale( lumiweight )
    
    h_truth, h_measured, h_response = [ fix_overflow( hist ) for hist in [h_truth, h_measured, h_response] ]
    if load_fakes:
        h_fakes = fix_overflow( h_fakes )
    
    return h_truth, h_measured, h_response, h_fakes

def get_combined_unfold_histogram_tuple( 
                inputfile,
                variable,
                met_type,
                centre_of_mass = 8,
                ttbar_xsection = 245.8,
                luminosity = 19712,
                load_fakes = False,
                scale_to_lumi = True,
                ):
    
    h_truth_e, h_measured_e, h_response_e, h_fakes_e = get_unfold_histogram_tuple( inputfile = inputfile,
                                                                                  variable = variable,
                                                                                  channel = 'electron',
                                                                                  met_type = met_type,
                                                                                  centre_of_mass = centre_of_mass,
                                                                                  ttbar_xsection = ttbar_xsection,
                                                                                  luminosity = luminosity,
                                                                                  load_fakes = load_fakes,
                                                                                  scale_to_lumi = scale_to_lumi,
                                                                                  )
    h_truth_mu, h_measured_mu, h_response_mu, h_fakes_mu = get_unfold_histogram_tuple( inputfile = inputfile,
                                                                                  variable = variable,
                                                                                  channel = 'muon',
                                                                                  met_type = met_type,
                                                                                  centre_of_mass = centre_of_mass,
                                                                                  ttbar_xsection = ttbar_xsection,
                                                                                  luminosity = luminosity,
                                                                                  load_fakes = load_fakes,
                                                                                  scale_to_lumi = scale_to_lumi,
                                                                                  )
    # summing histograms, the errors are added in quadrature
    h_truth = h_truth_e + h_truth_mu
    h_measured = h_measured_e + h_measured_mu
    h_response = h_response_e + h_response_mu
    h_fakes = None
    if load_fakes:
        h_fakes = h_fakes_e + h_fakes_mu
    
    return h_truth, h_measured, h_response, h_fakes
