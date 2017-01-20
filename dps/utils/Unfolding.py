'''
Created on 31 Oct 2012

@author: kreczko
'''
from __future__ import division
from ROOT import gSystem, cout, TDecompSVD
from .ROOT_utils import set_root_defaults
set_root_defaults(set_batch=True, msg_ignore_level=3001)
from .hist_utilities import hist_to_value_error_tuplelist
from ROOT import TUnfoldDensity, TUnfold
from ROOT import TH2D, TH1D, TGraph
from rootpy import asrootpy
from math import sqrt


class Unfolding:

    def __init__(self,
                 data,
                 truth,
                 measured,
                 response,
                 fakes=None,
                 method='TUnfold',
                 tau=-1,  # unfoldCfg.SVD_tau_value,
                 n_toy=1000,  # unfoldCfg.SVD_n_toy,
                 Bayes_n_repeat=4,  # unfoldCfg.Bayes_n_repeat,
                 error_treatment=3,  # unfoldCfg.error_treatment,
                 measured_truth_without_fakes=None,
                 verbose=0):
        # if not method in unfoldCfg.availablemethods:
        #     raise ValueError( 'Unknown unfolding method "%s". Available methods: %s' % ( method, str( unfoldCfg.availablemethods ) ) )
        self.method = method
        self.truth = truth
        self.measured = measured
        self.fakes = fakes
        self.response = response
        self.data = data
        self.unfolded_data = None
        self.refolded_data = None
        self.unfoldObject = None
        self.verbose = verbose
        self.tau = float(tau)
        self.n_toy = n_toy
        self.Bayes_n_repeat = Bayes_n_repeat
        self.error_treatment = error_treatment
        self.measured_truth_without_fakes = measured_truth_without_fakes

        self.setup_unfolding()

    def setup_unfolding(self):
        if not self.unfoldObject:
            if self.method == 'TUnfold':
                self.unfoldObject = TUnfoldDensity(self.response, TUnfold.kHistMapOutputVert,
                                                   TUnfold.kRegModeCurvature,
                                                   )
                self.unfoldObject.SetInput(self.data, 1.0)

                # self.unfoldObject.ScanLcurve( 30, 0, 0 )

    def unfold(self):
        # if data is None:
        #     raise ValueError('Data histogram is None')
        # have_zeros = [value == 0 for value,_ in hist_to_value_error_tuplelist( data )]
        # if not False in have_zeros:
        #     raise ValueError('Data histograms contains only zeros')
        # self.setup_unfolding( data )

        # remove unfold reports (faster)
        if self.method == 'TUnfold':
            self.unfoldObject.DoUnfold(self.tau)
            self.unfolded_data = asrootpy(
                self.unfoldObject.GetOutput('Unfolded'))
#         else:
#             self.unfoldObject.SetVerbose( self.verbose )
#             self.unfolded_data = asrootpy( self.unfoldObject.Hreco( self.error_treatment ) )
        return self.unfolded_data

    def refold(self):
        '''
        Refold the unfolded data
        '''
        # Data has to be folded first before refolding
        if self.unfolded_data is not None:
            self.refolded_data = asrootpy(
                self.unfoldObject.GetFoldedOutput('Refolded'))
        else:
            print("Data has not been unfolded. You cannot refold something that hasn't been first unfolded")
        return self.refolded_data
    def get_covariance_matrix(self):
        '''
        Get the covariance matrix from all contributions
        https://root.cern.ch/doc/master/classTUnfoldDensity.html#a7f9335973b3c520e2a4311d2dd6f5579
        '''
        import uncertainties as u
        from numpy import array, matrix, zeros
        from numpy import sqrt as np_sqrt
        if self.unfolded_data is not None:
            # Calculate the covariance from TUnfold
            covariance = asrootpy( 
                self.unfoldObject.GetEmatrixTotal('Covariance'))
            # Reformat into a numpy matrix
            xs = list(covariance.x())
            zs = list(covariance.z())
            cov_matrix = matrix(zs)
            bin_widths = array(xs)
            corr = array(zeros((cov_matrix.shape[0], cov_matrix.shape[1]) ))
            # Create a correlation matrix
            for i in range(0,cov_matrix.shape[0]):
                for j in range(0,cov_matrix.shape[1]):
                    corr[i,j] = cov_matrix[i,j] / np_sqrt( cov_matrix[i,i] * cov_matrix[j,j] )
                    
            # Normalising the covariance matrix
            inputs = hist_to_value_error_tuplelist(self.unfolded_data)
            norm_cov_matrix = cov_matrix.copy()
            values = [u.ufloat( i[0], i[1] ) for i in inputs]
            nominal_values = [v.nominal_value for v in values]
            
            normalisation = sum( values )
            values_correlated = u.correlated_values( nominal_values, cov_matrix.tolist() )
            # print 'Original values :',values_correlated
            # print 'Original correlation :',u.correlation_matrix(values_correlated)
            
            norm = sum(values_correlated)
            norm_values_correlated = []
            for v,width in zip( values_correlated, bin_widths ):
                norm_values_correlated.append( v / width / norm )
            # Return correlations? Probably should
            # print 'New values :',norm_values_correlated
            # print 'New correlation :',u.correlation_matrix(norm_values_correlated)
            norm_cov_matrix = matrix(u.covariance_matrix(norm_values_correlated) )
            # print 'New covariance :',u.covariance_matrix(norm_values_correlated)
            return cov_matrix, norm_cov_matrix
        else:
            print("Data has not been unfolded. Cannot return unfolding covariance matrix")
        return

    def getBestTau(self):
        if self.method != 'TUnfold':
            raise ValueError('Can only choose best tau here for TUnfold')
        g = TGraph()
        # Scan L curve
        # Sets tau value internally, but also need to store what it is
        self.unfoldObject.ScanLcurve(100, 0.001, 0.05, g)
        self.tau = self.unfoldObject.GetTau()

    def Reset(self):
        if self.unfoldObject:
            self.unfoldObject = None

    def chi2(self):
        chi2 = 99999999, 0
        if self.unfolded_data and self.truth:
            diff = self.truth - self.unfolded_data
            values = list(diff)
            errors = []
            for bin_i in range(len(values)):
                errors.append(diff.GetBinError(bin_i + 1))
            values = [abs(value) for value in values]
            errorsSquared = [error * error for error in errors]
            value = sum(values)
            error = sqrt(sum(errorsSquared))
            chi2 = value, error
        return chi2


    def getUnfoldRefoldChi2(self):
        '''
        Calculate the chi sq between the refolded data and the measured data
                                  2
                    (Model - Meas)
        Chi2 = SUM ----------------
                                  2
                    (Model Uncert)
        '''
        chi2 = 0
        diff = 0
        meas, model, model_unc = [], [], []

        if self.data is not None and self.refolded_data is not None:

            # We are measuring the refolded data and comparing to the data
            meas = [entry[0] for entry in hist_to_value_error_tuplelist(self.refolded_data)]
            # Data is the true distribution (In this case classified as our exact model)
            model = [entry[0] for entry in hist_to_value_error_tuplelist(self.data)]
            model_unc = [entry[1] for entry in hist_to_value_error_tuplelist(self.data)]
        else:
            print("There is no refolded data or measured data to be found")

        for x, mu, sigma in zip (meas, model, model_unc):

            # At the moment for some reason in electron lepton pt the first bin is empty...
            # Need to figure out why. Until then using this.
            if (sigma == 0): continue
            # Is this correct?
            diff = pow(mu-x,2) / pow(sigma, 2)
            chi2 += diff
        return chi2

    def pull(self):
        result = [9999999]

        if self.unfolded_data and self.truth:
            for bin in range(0, self.truth.GetNbinsX()):
                self.truth.SetBinError(bin, 0)

            diff = self.unfolded_data - self.truth
            value_error_tuplelist = hist_to_value_error_tuplelist(diff)
            result = [value / error for value, error in value_error_tuplelist]

        return result

    def Impl(self):
        return self.unfoldObject.Impl()


def get_unfold_histogram_tuple(
    inputfile,
    variable,
    channel,
    met_type='patType1CorrectedPFMet',
    centre_of_mass=8,
    ttbar_xsection=245.8,
    luminosity=19712,
    load_fakes=False,
    scale_to_lumi=False,
    visiblePS=False,
    scale=1,
):
    h_truth = None
    h_measured = None
    h_response = None
    h_fakes = None

    folder = inputfile.Get('%s_%s' % (variable, channel))

    if visiblePS:
        h_truth = asrootpy(folder.truthVis.Clone())
        h_measured = asrootpy(folder.measuredVis_without_fakes.Clone())
        h_response = asrootpy(folder.responseVis_without_fakes.Clone())
    else:
        h_truth = asrootpy(folder.truth.Clone())
        h_measured = asrootpy(folder.measured_without_fakes.Clone())
        h_response = asrootpy(folder.response_without_fakes.Clone())

    if load_fakes:
        h_fakes = asrootpy(folder.fakeVis.Clone())
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
        lumiweight = 1.  # 13 TeV unfolding files are scaled.
        # we will need to change this as we do not want to reproduce them
        # every time we get new data.
        if hasattr(inputfile, 'EventFilter'):
            nEvents = inputfile.EventFilter.EventCounter.GetBinContent(
                1)  # number of processed events
            lumiweight = ttbar_xsection * luminosity / nEvents

        if load_fakes:
            h_fakes.Scale(lumiweight)
        h_truth.Scale(lumiweight)
        h_measured.Scale(lumiweight)
        h_response.Scale(lumiweight)

    if not scale == 1:
        if load_fakes:
            h_fakes.Scale(scale)
        h_truth.Scale(scale)
        h_measured.Scale(scale)
        h_response.Scale(scale)

    return h_truth, h_measured, h_response, h_fakes


def get_combined_unfold_histogram_tuple(
    inputfile,
    variable,
    met_type,
    centre_of_mass=8,
    ttbar_xsection=245.8,
    luminosity=19712,
    load_fakes=False,
    scale_to_lumi=True,
    visiblePS=False,
    scale=1,
):

    h_truth_e, h_measured_e, h_response_e, h_fakes_e = get_unfold_histogram_tuple(inputfile=inputfile,
                                                                                  variable=variable,
                                                                                  channel='electron',
                                                                                  met_type=met_type,
                                                                                  centre_of_mass=centre_of_mass,
                                                                                  ttbar_xsection=ttbar_xsection,
                                                                                  luminosity=luminosity,
                                                                                  load_fakes=load_fakes,
                                                                                  scale_to_lumi=scale_to_lumi,
                                                                                  visiblePS=visiblePS,
                                                                                  scale=scale,
                                                                                  )
    h_truth_mu, h_measured_mu, h_response_mu, h_fakes_mu = get_unfold_histogram_tuple(inputfile=inputfile,
                                                                                      variable=variable,
                                                                                      channel='muon',
                                                                                      met_type=met_type,
                                                                                      centre_of_mass=centre_of_mass,
                                                                                      ttbar_xsection=ttbar_xsection,
                                                                                      luminosity=luminosity,
                                                                                      load_fakes=load_fakes,
                                                                                      scale_to_lumi=scale_to_lumi,
                                                                                      visiblePS=visiblePS,
                                                                                      scale=scale,
                                                                                      )
    # summing histograms, the errors are added in quadrature
    h_truth = h_truth_e + h_truth_mu
    h_measured = h_measured_e + h_measured_mu
    h_response = h_response_e + h_response_mu
    h_fakes = None
    if load_fakes:
        h_fakes = h_fakes_e + h_fakes_mu
    return h_truth, h_measured, h_response, h_fakes


def removeFakes(h_measured, h_fakes, h_data):
    nonFakeRatio = 1 - h_fakes / (h_measured + h_fakes)
    h_data *= nonFakeRatio
    return h_data
