'''
    Provides the classes Measurement and Systematic
'''
from __future__ import division
from . import log
from dps.utils.hist_utilities import hist_to_value_error_tuplelist, clean_control_region

# define logger for this module
meas_log = log["dps.utils.measurement"]

class Measurement():
    '''
        The Measurement class combines files and histogram paths into
        one container. It also allows to provide separate shapes for the
        histograms while using the normalisation from the initial set.
    '''
    @meas_log.trace()
    def __init__(self, measurement):
        self.measurement    = measurement
        self.histograms     = {}
        self.cr_histograms  = {}
        self.normalisation  = {}
        self.variable       = None
        self.com            = None
        self.channel        = None
        self.name           = None
        self.is_normalised  = False
        self.central        = False
        self.samples        = {}
        self.__setFromConfig()

    def __setFromConfig(self):
        self.variable   = self.measurement["variable"]
        self.com        = self.measurement["com"]
        self.channel    = self.measurement["channel"]
        self.samples    = self.measurement["samples"]
        self.name       = self.measurement["name"]
        data_driven_qcd = self.measurement["data_driven_qcd"]

        # Is this central or a systematic?
        if "central" in self.name:
            self.central = True

        # Retrieve histograms from files for SR and CR
        for sample, histogram_info in self.samples.iteritems():
            self.histograms[sample] = self.__return_histogram(histogram_info)
            if data_driven_qcd:
                self.cr_histograms[sample] = self.__return_histogram(histogram_info, useQCDControl=True)

            # print(hist_to_value_error_tuplelist(self.histograms[sample]))
            # print(hist_to_value_error_tuplelist(self.cr_histograms[sample]))

        # Replace QCD MC with data-driven MC
        if data_driven_qcd:
            self.__qcd_from_data()
        return

    def __qcd_from_data(self):
        '''
        Replace Signal region mc qcd with data driven qcd

                        N MC QCD in SR      N DD QCD in CR
        QCD_SHAPE   *   --------------  *   --------------
                        N DD QCD in CR      N MC QCD in CR

          Shape         normalise to        scale from
                        SR mc qcd           mc qcd to dd qcd
        '''
        # Get the shape of the data driven qcd in the control region
        qcd_shape = clean_control_region(
            self.cr_histograms,
            subtract=['TTBar', 'V+Jets', 'SingleTop']
        )
        # print(hist_to_value_error_tuplelist(qcd_shape))

        # Now to normalise the qcd shape to the MC in the Signal Region
        # n_dd_cr= Number of datadriven qcd from Control Region
        n_mc_sr = self.histograms['QCD'].Integral()
        n_dd_cr = qcd_shape.Integral()
        qcd_shape.Scale( n_mc_sr/n_dd_cr )
        # print "scaling to normalisation in SR MC : ", n_mc_sr/n_dd_cr

        # Now to scale from mc qcd to datadriven qcd
        n_mc_cr = self.cr_histograms['QCD'].Integral()
        qcd_shape.Scale( n_dd_cr/n_mc_cr )
        # print "scaling from MC to datadriven : ", n_dd_cr/n_mc_cr
        # print "Total scaling : ", n_mc_sr/n_mc_cr

        # Replace QCD histogram with datadriven one
        self.histograms['QCD'] = qcd_shape
        return

    def __return_histogram(self, d_hist_info, ignoreUnderflow=True, useQCDControl=False):
        '''
        Takes basic histogram info and returns histo.
        Maybe this can move to ROOT_utilities?
        '''
        from rootpy.io.file import File
        from rootpy.plotting import Hist
        from dps.utils.hist_utilities import fix_overflow

        f           = d_hist_info['input_file']
        tree        = d_hist_info['tree']
        qcd_tree    = d_hist_info["qcd_control_region"]
        var         = d_hist_info['branch']
        bins        = d_hist_info['bin_edges']
        lumi_scale  = d_hist_info['lumi_scale']
        scale       = d_hist_info['scale']
        weights     = d_hist_info['weight_branches']
        selection   = d_hist_info['selection']

        if useQCDControl: 
            # replace SR tree with CR tree
            tree = qcd_tree
            # Remove the Lepton reweighting for the datadriven qcd (SF not derived for unisolated leptons)
            for weight in weights:
                if 'Electron' in weight: weights.remove(weight)
                elif 'Muon'   in weight: weights.remove(weight)

        weights = "*".join(weights)
        # Selection will return a weight 0 or 1 depending on whether event passes selection
        weights_and_selection = '( {0} ) * ( {1} )'.format(weights, selection)

        scale *= lumi_scale

        root_file = File( f )
        root_tree = root_file.Get( tree )

        root_histogram = Hist( bins )
        # Draw histogram of var for selection into root_histogram
        root_tree.Draw(var, selection = weights_and_selection, hist = root_histogram)
        root_histogram.Scale(scale)

        # When a tree is filled with a dummy variable, it will end up in the underflow, so ignore it
        if ignoreUnderflow:
            root_histogram.SetBinContent(0, 0)
            root_histogram.SetBinError(0,0)

        # Fix overflow (Moves entries from overflow bin into last bin i.e. last bin not |..| but |--> ) 
        root_histogram = fix_overflow(root_histogram)

        root_file.Close()
        return root_histogram


    def __background_subtraction(self, histograms):
        '''
        Subtracts the backgrounds from data to give amount of ttbar in data.
        Also adds all backgrounds to normalisation output
        '''
        ttjet_hist = clean_control_region(
            histograms,
            subtract=['QCD', 'V+Jets', 'SingleTop']
        )
        self.normalisation['TTJet']     = hist_to_value_error_tuplelist(ttjet_hist)
        self.normalisation['data']      = hist_to_value_error_tuplelist(histograms['data'])
        # self.normalisation['TTBar']   = hist_to_value_error_tuplelist(histograms['TTBar'])
        self.normalisation['SingleTop'] = hist_to_value_error_tuplelist(histograms['SingleTop'])
        self.normalisation['V+Jets']    = hist_to_value_error_tuplelist(histograms['V+Jets'])
        self.normalisation['QCD']       = hist_to_value_error_tuplelist(histograms['QCD'])
        return

    def calculate_normalisation(self):
        '''
        Calls the normalisation of the ttbar samples
        '''
        # normalisation already calculated
        if self.is_normalised: return

        histograms = self.histograms
        self.__background_subtraction(histograms)

        # next, let's round all numbers (they are event numbers after all)
        for sample, values in self.normalisation.items():
            new_values = [(round(v, 1), round(e, 1)) for v, e in values]
            self.normalisation[sample] = new_values
        self.is_normalised = True
        return

    def save(self, phase_space):
        '''
        Saves the normalisation output into a JSON.
        I would like to change this to a pandas Dataframe at somepoint after 
        a few issues have been worked out
        '''
        from dps.utils.pandas_utilities import write_tuple_to_df
        from dps.utils.file_utilities import make_folder_if_not_exists
        # If normalisation hasnt been calculated  - then go calculate it!
        if not self.is_normalised: self.calculate_normalisation()

        output_folder = 'data/normalisation/background_subtraction/{com}TeV/{var}/{ps}/{cat}/'
        output_folder = output_folder.format(
            com = self.com,
            var = self.variable,
            ps  = phase_space,
            cat = self.name,
            )
        make_folder_if_not_exists(output_folder)

        file_template = '{type}_{channel}.txt'
        f = file_template.format(
            type='normalisation', 
            channel=self.channel
        )

        write_tuple_to_df(
            self.normalisation,
            output_folder + f
        )
        return 

    def combine(self, other):
        '''
        Combines the electron and muon measurements
        '''
        from dps.utils.Calculation import combine_complex_results
        if not self.is_normalised or not other.is_normalised:
            mylog.warn(
                'One of the TTJetNormalisations does not have a normalisation, aborting.')
            return

        self.normalisation = combine_complex_results(
            self.normalisation, other.normalisation)
        self.channel = 'combined'
        return
