'''
Created on 31 Oct 2012

@author: kreczko
'''
from ROOT import gSystem, cout, TDecompSVD
import config.RooUnfold as unfoldCfg
import config.TopSVDUnfold as top_unfold
from tools.hist_utilities import hist_to_value_error_tuplelist
gSystem.Load( unfoldCfg.library )
gSystem.Load( top_unfold.library )
from ROOT import RooUnfoldResponse, RooUnfoldParms, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
from ROOT import RooUnfoldBinByBin, RooUnfoldInvert, RooUnfoldTUnfold
from ROOT import TSVDUnfold
from ROOT import TopSVDUnfold
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
                 Hreco = unfoldCfg.Hreco,
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
        self.unfolded_closure = None
        self.unfolded_data = None
        self.unfoldObject = None
        self.unfoldResponse = None
        self.closure_test = None
        self.verbose = verbose
        self.tau = tau
        self.k_value = k_value 
        self.n_toy = n_toy
        self.Bayes_n_repeat = Bayes_n_repeat
        self.Hreco = Hreco
        self.measured_truth_without_fakes = measured_truth_without_fakes
    
    def setup_unfolding (self, data):
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
            elif self.method == 'RooUnfoldTUnfold':
                self.unfoldObject = RooUnfoldTUnfold     ( self.unfoldResponse, self.data )
                if self.tau >= 0:
                    self.unfoldObject.FixTau( self.tau )
            elif self.method == 'RooUnfoldSvd':
                self.unfoldObject = RooUnfoldSvd( self.unfoldResponse, self.data, self.k_value, self.n_toy )
            elif self.method == 'TSVDUnfold':
                new_data = Hist( list( self.data.xedges() ), type = 'D' )
                new_data.Add( self.data )
                
                new_measured = Hist( list( self.measured.xedges() ), type = 'D' )
                new_measured.Add( self.measured )
                
                new_truth = Hist( list( self.truth.xedges() ), type = 'D' )
                new_truth.Add( self.truth )


                if self.fakes:
                    new_fakes = Hist( list ( self.fakes.xedges() ), type = 'D')
                    new_fakes.Add ( self.fakes )
                    new_measured = new_measured - new_fakes

                new_response = Hist2D( list( self.response.xedges() ), list( self.response.yedges() ), type = 'D' )
                new_response.Add( self.response )

                #replace global objects with new ones
                self.data = new_data
                self.measured = new_measured
                self.truth = new_truth
                self.response = new_response

                self.unfoldObject = TSVDUnfold( self.data, self.measured, self.truth, self.response )
            elif self.method == 'TopSVDUnfold':
                ''' constructors are
                 TopSVDUnfold(const TH1D* bdat, const TH1D* bini, const TH1D* xini, const TH2D* Adet);
                 TopSVDUnfold(const TH1D* bdat, TH2D* Bcov, const TH1D* bini, const TH1D* xini, const TH2D* Adet);
                 where
                 bdat: data input
                 xini: true underlying spectrum (TH1D, n bins)
                 bini: reconstructed spectrum (TH1D, n bins)
                 Adet: response matrix (TH2D, nxn bins)'''
                # first convert all TH1F to TH2D
                new_data = TH1D()
                new_measured = TH1D()
                new_truth = TH1D()
                new_fakes = TH1D()
                new_response = TH2D()
                self.data.Copy( new_data )
                self.measured.Copy( new_measured )
                self.truth.Copy( new_truth )
                if self.fakes:
                    self.fakes.Copy( new_fakes )
                    new_measured = new_measured - new_fakes
                self.response.Copy( new_response )

                #replace global objects with new ones
                self.data = new_data
                self.measured = new_measured
                self.truth = new_truth
                self.response = new_response
                
                self.unfoldObject = TopSVDUnfold( self.data, self.measured, self.truth, self.response )
                if self.k_value == -1 and self.tau >= 0:
                    self.unfoldObject.SetTau( self.tau )

    def test_regularisation (self, data, k_max):
        self.setup_unfolding( data )
        if self.method == 'RooUnfoldSvd':
            findingK = RooUnfoldParms( self.unfoldObject, self.Hreco, self.truth )
            findingK.SetMinParm(1)
            findingK.SetMaxParm(k_max)
            findingK.SetStepSizeParm(1)
            RMSerror = asrootpy(findingK.GetRMSError().Clone())
            MeanResiduals = asrootpy(findingK.GetMeanResiduals().Clone())
            RMSresiduals = asrootpy(findingK.GetRMSResiduals().Clone())
            Chi2 = asrootpy(findingK.GetChi2().Clone())
            return RMSerror, MeanResiduals, RMSresiduals, Chi2
        else:
            raise ValueError( 'Unfolding method "%s" is not supported for regularisation parameter tests. Please use RooUnfoldSvd.' % ( method ) )

    def unfold( self, data ):
        self.setup_unfolding( data )
        if self.method == 'TSVDUnfold' or self.method == 'TopSVDUnfold':
            self.unfolded_data = asrootpy( self.unfoldObject.Unfold( self.k_value ) )
        else:
            # remove unfold reports (faster)
            self.unfoldObject.SetVerbose( self.verbose )
            self.unfolded_data = asrootpy( self.unfoldObject.Hreco( self.Hreco ) )
        return self.unfolded_data
    
    def closureTest( self ):
        if not self.closure_test:
            if not self.unfoldResponse:
                self.unfoldResponse = self._makeUnfoldResponse()
            if self.method == 'RooUnfoldBayes':
                self.closure_test = RooUnfoldBayes     ( self.unfoldResponse, self.measured, self.Bayes_n_repeat )
            elif self.method == 'RooUnfoldBinByBin':
                self.closure_test = RooUnfoldBinByBin     ( self.unfoldResponse, self.measured )
            elif self.method == 'RooUnfoldInvert':
                self.closure_test = RooUnfoldInvert     ( self.unfoldResponse, self.measured )
            elif self.method == 'RooUnfoldTUnfold':
                self.closure_test = RooUnfoldTUnfold     ( self.unfoldResponse, self.measured )
            elif self.method == 'RooUnfoldSvd':
                self.closure_test = RooUnfoldSvd( self.unfoldResponse, self.measured, self.k_value, self.n_toy )
            elif self.method == 'TSVDUnfold':
                new_measured = Hist( list( self.measured.xedges() ), type = 'D' )
                new_measured.Add( self.measured )
                new_truth = Hist( list( self.truth.xedges() ), type = 'D' )
                new_truth.Add( self.truth )

                if self.fakes:
                    new_fakes = Hist( list ( self.fakes.xedges() ), type = 'D')
                    new_fakes.Add ( self.fakes )
                    new_measured = new_measured - new_fakes

                new_response = Hist2D( list( self.response.xedges() ), list( self.response.yedges() ), type = 'D' )
                new_response.Add( self.response )
                self.closure_test = TSVDUnfold( new_measured, new_measured, new_truth, new_response )
        if self.method == 'TSVDUnfold':
            self.unfolded_closure = asrootpy( self.closure_test.Unfold( self.k_value ) )
        else:
            self.unfolded_closure = asrootpy( self.closure_test.Hreco( self.Hreco ) )
        return self.unfolded_closure
    
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
        if self.closure_test:
            self.closure_test = None
            
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
            temp_list = list( temp )
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
            values = list( diff )
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
            
def get_unfold_histogram_tuple( 
                inputfile,
                variable,
                channel,
                met_type,
                centre_of_mass = 8,
                ttbar_xsection = 245.8,
                luminosity = 19712,
                load_fakes = False,
                scale_to_lumi = True ):
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
        
        h_truth = asrootpy( folder.truth_AsymBins ).Clone()
        h_measured = asrootpy( folder.measured_AsymBins ).Clone()

        #response matrix is always without fakes
        #fake subtraction from measured is performed automatically in RooUnfoldSvd (h_measured - h_response->ProjectionX())
        #or manually for TSVDUnfold
        h_response = asrootpy( folder.response_without_fakes_AsymBins ).Clone()
            #h_response = folder.response_AsymBins.Clone()

        if load_fakes:
            h_fakes = asrootpy( folder.fake_AsymBins ).Clone()
    else:
        return get_combined_unfold_histogram_tuple(inputfile = inputfile,
                                                   variable = variable,
                                                   met_type = met_type,
                                                   centre_of_mass = centre_of_mass,
                                                   ttbar_xsection = ttbar_xsection,
                                                   luminosity = luminosity,
                                                   load_fakes = load_fakes
                                                   )

    if scale_to_lumi:
        nEvents = inputfile.EventFilter.EventCounter.GetBinContent( 1 )  # number of processed events 
        lumiweight = ttbar_xsection * luminosity / nEvents
        if load_fakes:
            h_fakes.Scale( lumiweight )
        h_truth.Scale( lumiweight )
        h_measured.Scale( lumiweight )
        h_response.Scale( lumiweight )
    
    if load_fakes:
        return fix_overflow( h_truth, h_measured, h_response, h_fakes )
    else:
        return fix_overflow( h_truth, h_measured, h_response )


def get_combined_unfold_histogram_tuple( 
                inputfile,
                variable,
                met_type,
                centre_of_mass = 8,
                ttbar_xsection = 245.8,
                luminosity = 19712,
                load_fakes = False ):
    
    h_truth_e, h_measured_e, h_response_e, h_fakes_e = get_unfold_histogram_tuple(inputfile = inputfile,
                                                                                  variable = variable,
                                                                                  channel = 'electron',
                                                                                  met_type = met_type,
                                                                                  centre_of_mass = centre_of_mass,
                                                                                  ttbar_xsection = ttbar_xsection,
                                                                                  luminosity = luminosity,
                                                                                  load_fakes = load_fakes,
                                                                                  scale_to_lumi = False
                                                                                  )
    h_truth_mu, h_measured_mu, h_response_mu, h_fakes_mu = get_unfold_histogram_tuple(inputfile = inputfile,
                                                                                  variable = variable,
                                                                                  channel = 'muon',
                                                                                  met_type = met_type,
                                                                                  centre_of_mass = centre_of_mass,
                                                                                  ttbar_xsection = ttbar_xsection,
                                                                                  luminosity = luminosity,
                                                                                  load_fakes = load_fakes,
                                                                                  scale_to_lumi = False
                                                                                  )
    #summing histograms, the errors are added in quadrature
    h_truth = h_truth_e + h_truth_mu
    h_measured = h_measured_e + h_measured_mu
    h_response = h_response_e + h_response_mu
    h_fakes = None
    if load_fakes:
        h_fakes = h_fakes_e + h_fakes_mu
    
    nEvents = inputfile.EventFilter.EventCounter.GetBinContent( 1 )  # number of processed events 
    lumiweight = ttbar_xsection * luminosity / nEvents

    h_truth.Scale( lumiweight )
    h_measured.Scale( lumiweight )
    h_response.Scale( lumiweight )
    if load_fakes:
        h_fakes.Scale( lumiweight )
    
    return h_truth, h_measured, h_response, h_fakes

def fix_overflow( h_truth, h_measured, h_response, h_fakes = None ):
    ''' Moves entries from the overflow bin into the last bin as we treat the last bin as everything > last_bin.lower_edge.
    This is to fix a bug in the unfolding workflow where we neglect this treatment.'''
    
    # first the 1D histograms
    for hist in [h_truth, h_measured, h_fakes]:
        if not hist:
            continue
        last_bin = hist.nbins()
        overflow_bin = last_bin + 1
        overflow = hist.GetBinContent( overflow_bin )
        overflow_error= hist.GetBinError( overflow_bin )
        
        new_last_bin_content = hist.GetBinContent( last_bin ) + overflow
        new_last_bin_error = hist.GetBinError( last_bin ) + overflow_error
        
        hist.SetBinContent( last_bin, new_last_bin_content )
        hist.SetBinError( last_bin, new_last_bin_error )
        hist.SetBinContent( overflow_bin, 0. )
    # then the 2D histogram
    if h_response:
        last_bin_x = h_response.nbins()
        last_bin_y = h_response.nbins( axis = 1 )
        overflow_bin_x = last_bin_x + 1
        overflow_bin_y = last_bin_y + 1
        # first all y-overflow
        for x in range( 1, overflow_bin_x +1):
            overflow_y = h_response.GetBinContent( x, overflow_bin_y )
            overflow_error_y = h_response.GetBinError( x, overflow_bin_y )
            
            last_bin_content_y = h_response.GetBinContent( x, last_bin_y )
            last_bin_error_y = h_response.GetBinError( x, last_bin_y )
            
            h_response.SetBinContent( x, overflow_bin_y, 0. )
            h_response.SetBinContent( x, last_bin_y, overflow_y + last_bin_content_y )
            h_response.SetBinError( x, last_bin_y, overflow_error_y + last_bin_error_y )
        # now all x-overflow
        for y in range( 1, overflow_bin_y +1):
            overflow_x = h_response.GetBinContent( overflow_bin_x, y )
            overflow_error_x = h_response.GetBinError( overflow_bin_x, y )
            
            last_bin_content_x = h_response.GetBinContent( last_bin_x, y )
            last_bin_error_x = h_response.GetBinError( last_bin_x, y )
            
            h_response.SetBinContent( overflow_bin_x, y, 0. )
            h_response.SetBinContent( last_bin_x, y, overflow_x + last_bin_content_x )
            h_response.SetBinError( last_bin_x, y, overflow_error_x + last_bin_error_x )
        # and now the final bin (both x and y overflow)
        overflow_x_y = h_response.GetBinContent( overflow_bin_x, overflow_bin_y )
        last_bin_content_x_y = h_response.GetBinContent( last_bin_x, last_bin_y )
        h_response.SetBinContent( overflow_bin_x, overflow_bin_y, 0. )
        h_response.SetBinContent( last_bin_x, last_bin_y, overflow_x_y + last_bin_content_x_y )
        
    # now the fun part. Since the above histograms still have an entry in overflow, that needs to be rectified.
    h_truth = transfer_values_without_overflow(h_truth)
    h_measured = transfer_values_without_overflow(h_measured)
    h_response = transfer_values_without_overflow(h_response)
    h_fakes = transfer_values_without_overflow(h_fakes)

    return h_truth, h_measured, h_response, h_fakes

def transfer_values_without_overflow( histogram ):
    if histogram == None:
        return histogram
    
    dimension = 1
    histogram_new= None
    if str( type( histogram ) ) == str( Hist2D.dynamic_cls( 'D' ) ):
        dimension = 2
    if dimension == 1:
        histogram_new = Hist( list( histogram.xedges() ), type = 'D' ) 
        n_bins = histogram_new.nbins()
        for i in range(1, n_bins + 1):
            histogram_new.SetBinContent(i, histogram.GetBinContent(i))
            histogram_new.SetBinError(i, histogram.GetBinError(i))
    else:
        histogram_new = Hist2D( list( histogram.xedges() ), list( histogram.yedges() ), type = 'D' )
        n_bins_x = histogram_new.nbins()
        n_bins_y = histogram_new.nbins(axis=1)
        for i in range(1, n_bins_x + 1):
            for j in range(1, n_bins_y + 1):
                histogram_new.SetBinContent(i,j, histogram.GetBinContent(i, j))
                histogram_new.SetBinError(i,j, histogram.GetBinError(i, j))
    return histogram_new
