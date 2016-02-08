'''
Created on 31 Oct 2012

@author: kreczko
'''
from ROOT import gSystem, cout, TDecompSVD
import config.RooUnfold as unfoldCfg
from tools.hist_utilities import hist_to_value_error_tuplelist, fix_overflow
gSystem.Load( unfoldCfg.library )
from ROOT import RooUnfoldResponse, RooUnfoldParms, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
from ROOT import TUnfoldDensity, TUnfold
from ROOT import TH2D, TH1D, TGraph
from rootpy import asrootpy
from rootpy.plotting import Hist, Hist2D
from math import sqrt

class Unfolding:

    def __init__( self,
                 data,
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
        self.data = data
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

        self.setup_unfolding( )

    def setup_unfolding ( self ):
        if not self.unfoldObject:
            
            if not self.unfoldResponse:
                self.unfoldResponse = self._makeUnfoldResponse()
            
            if self.method == 'RooUnfoldBayes':
                self.unfoldObject = RooUnfoldBayes     ( self.unfoldResponse, self.data, self.Bayes_n_repeat )
            elif self.method == 'RooUnfoldSvd':
                if self.k_value > 0:
                    self.unfoldObject = RooUnfoldSvd( self.unfoldResponse, self.data, self.k_value, self.n_toy )
                else:
                    if self.tau >= 0:
                        self.unfoldObject = RooUnfoldSvd( self.unfoldResponse, self.data, self.tau, self.n_toy )
            elif self.method == 'TUnfold':

              self.unfoldObject = TUnfoldDensity( self.response, TUnfold.kHistMapOutputVert, TUnfold.kRegModeDerivative)
              self.unfoldObject.SetInput( self.data )
              # self.unfoldObject.ScanLcurve( 30, 0, 0 )

    def unfold( self ):
        # if data is None:
        #     raise ValueError('Data histogram is None')
        # have_zeros = [value == 0 for value,_ in hist_to_value_error_tuplelist( data )]
        # if not False in have_zeros:
        #     raise ValueError('Data histograms contains only zeros')
        # self.setup_unfolding( data )

        # remove unfold reports (faster)
        if self.method == 'TUnfold':
            self.unfoldObject.DoUnfold(self.tau)
            self.unfolded_data = asrootpy( self.unfoldObject.GetOutput('Unfolded') )
        else:
            self.unfoldObject.SetVerbose( self.verbose )
            self.unfolded_data = asrootpy( self.unfoldObject.Hreco( self.error_treatment ) )
        return self.unfolded_data

    def _makeUnfoldResponse( self ):
        if self.fakes:
            return RooUnfoldResponse ( self.measured, self.truth, self.fakes, self.response )
        else:
            return RooUnfoldResponse ( self.measured, self.truth, self.response )

    def getBestTau( self ):
        if self.method != 'TUnfold':
            raise ValueError( 'Can only choose best tau here for TUnfold' )
        g = TGraph()
        # Scan L curve
        # Sets tau value internally, but also need to store what it is
        self.unfoldObject.ScanLcurve(100,0.001,0.05, g);
        self.tau = self.unfoldObject.GetTau()

    def Reset( self ):
        if self.unfoldObject:
            self.unfoldObject = None

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
                scale_to_lumi = False,
                visiblePS = False,
                scale = 1,
                ):
    folder = None
    h_truth = None
    h_measured = None
    h_response = None
    h_fakes = None

    if not channel == 'combined':
        folder = inputfile.Get( '%s_%s' % ( variable, channel ) )
    else:
        folder = inputfile.Get( '%s_COMBINED' % ( variable ) )

    if visiblePS:
      h_truth = asrootpy( folder.truthVis.Clone() )
      h_measured = asrootpy( folder.measuredVis.Clone() )
      h_response = asrootpy( folder.responseVis_without_fakes.Clone() )
    else :
      h_truth = asrootpy( folder.truth.Clone() )
      h_measured = asrootpy( folder.measured.Clone() )
      h_response = asrootpy( folder.response_without_fakes.Clone() )

    if load_fakes:
        h_fakes = asrootpy( folder.fake.Clone() )
    # else:
    #     return get_combined_unfold_histogram_tuple( inputfile = inputfile,
    #                                                variable = variable,
    #                                                met_type = met_type,
    #                                                centre_of_mass = centre_of_mass,
    #                                                ttbar_xsection = ttbar_xsection,
    #                                                luminosity = luminosity,
    #                                                load_fakes = load_fakes,
    #                                                scale_to_lumi = scale_to_lumi,
    #                                                visiblePS = visiblePS,
    #                                                scale = 1,
    #                                                )

    if scale_to_lumi:
        lumiweight = 1. # 13 TeV unfolding files are scaled.
        # we will need to change this as we do not want to reproduce them
        # every time we get new data.
        if hasattr(inputfile, 'EventFilter'):
            nEvents = inputfile.EventFilter.EventCounter.GetBinContent( 1 )  # number of processed events
            lumiweight = ttbar_xsection * luminosity / nEvents

        if load_fakes:
            h_fakes.Scale( lumiweight )
        h_truth.Scale( lumiweight )
        h_measured.Scale( lumiweight )
        h_response.Scale( lumiweight )

    if not scale ==1:
      if load_fakes:
          h_fakes.Scale( scale )
      h_truth.Scale( scale )
      h_measured.Scale( scale )
      h_response.Scale( scale )

    # h_truth, h_measured, h_response = [ fix_overflow( hist ) for hist in [h_truth, h_measured, h_response] ]
    # if load_fakes:
    #    h_fakes = fix_overflow( h_fakes )

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
                visiblePS = False,
                scale = 1,
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
                                                                                  visiblePS = visiblePS,
                                                                                  scale = scale,
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
                                                                                  visiblePS = visiblePS,
                                                                                  scale = scale,
                                                                                  )
    # summing histograms, the errors are added in quadrature
    h_truth = h_truth_e + h_truth_mu
    h_measured = h_measured_e + h_measured_mu
    h_response = h_response_e + h_response_mu
    h_fakes = None
    if load_fakes:
        h_fakes = h_fakes_e + h_fakes_mu
    print list(h_response.z())
    return h_truth, h_measured, h_response, h_fakes
