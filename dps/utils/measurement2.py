'''
    Provides the classes Measurement and Systematic
'''
from __future__ import division
from . import log
import copy
from dps.utils.file_utilities import make_folder_if_not_exists, read_data_from_JSON
from dps.utils.input import Input
from dps.utils.hist_utilities import hist_to_value_error_tuplelist
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
        self.measurement = measurement
        self.histograms = {}
        self.cr_histograms = {}
        self.normalisation = {}
        self.variable = None
        self.com = None
        self.channel = None
        self.name = None
        self.is_normalised = False
        self.central = False
        self.samples = {}
        self.__setFromConfig()

    def __setFromConfig(self):
        self.variable = self.measurement["variable"]
        self.com = self.measurement["com"]
        self.channel = self.measurement["channel"]
        self.samples = self.measurement["samples"]
        self.name = self.measurement["name"]
        data_driven_qcd = self.measurement["data_driven_qcd"]
        # Is this central or a systematic?
        if "central" in self.name:
            self.central = True

        for sample, histogram_info in self.samples.iteritems():
            self.histograms[sample] = self.__return_histogram(histogram_info)
            if data_driven_qcd:
                self.cr_histograms[sample] = self.__return_histogram(histogram_info, useQCDControl=True)
            # print hist_to_value_error_tuplelist(self.histograms[sample])
            # print hist_to_value_error_tuplelist(self.cr_histograms[sample])

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
        from dps.utils.hist_utilities import clean_control_region

        # Get the shape of the data driven qcd in the control region
        qcd_shape = clean_control_region(
            self.cr_histograms,
            subtract=['TTBar', 'V+Jets', 'SingleTop']
        )

        # Now to normalise the qcd shape to the MC in the Signal Region
        # n_dd_cr= Number of datadriven qcd from Control Region
        n_mc_sr = self.histograms['QCD'].Integral()
        n_dd_cr = qcd_shape.Integral()
        qcd_shape.Scale( n_mc_sr/n_dd_cr )

        # Now to scale from mc qcd to datadriven qcd
        n_mc_cr = self.cr_histograms['QCD'].Integral()
        qcd_shape.Scale( n_dd_cr/n_mc_cr )

        # Replace QCD histogram with datadriven one
        self.histograms['QCD'] = qcd_shape
        return


    def __return_histogram(self, d_hist_info, ignoreUnderflow=True, useQCDControl=False):
        '''
        Takes basic histogram info and returns histo.
        '''
        from rootpy.io.file import File
        from rootpy.plotting import Hist
        from dps.utils.hist_utilities import fix_overflow

        f = d_hist_info['input_file']
        tree = d_hist_info['tree']
        qcd_tree = d_hist_info["qcd_control_region"]
        var = d_hist_info['branch']
        bins = d_hist_info['bin_edges']
        lumi_scale = d_hist_info['lumi_scale']
        scale = d_hist_info['scale']
        weights = d_hist_info['weight_branches']
        weights = "*".join(weights)

        if useQCDControl: 
            tree = qcd_tree

        scale *= lumi_scale

        root_file = File( f )
        root_tree = root_file.Get( tree )

        root_histogram = Hist( bins )
        root_tree.Draw(var, weights, hist = root_histogram)
        root_histogram.Scale(scale)

        # When a tree is filled with a dummy variable, it will end up in the underflow, so ignore it
        if ignoreUnderflow:
            root_histogram.SetBinContent(0, 0)
            root_histogram.SetBinError(0,0)

        # Fix overflow (Moves entries from overflow bin into last bin i.e. last bin not | | but |--> ) 
        root_histogram = fix_overflow(root_histogram)

        root_file.Close()
        return root_histogram

    def __background_subtraction(self, histograms):
        from dps.utils.hist_utilities import clean_control_region

        ttjet_hist = clean_control_region(
            histograms,
            subtract=['QCD', 'V+Jets', 'SingleTop']
        )
        self.normalisation['TTJet'] = hist_to_value_error_tuplelist(ttjet_hist)
        return

    def calculate_normalisation(self):
        '''
        '''
        # normalisation already calculated
        if self.is_normalised: return

        histograms = self.histograms
        self.__background_subtraction(histograms)

        # next, let's round all numbers (they are event numbers after all)
        for sample, values in self.normalisation.items():
            new_values = [(round(v, 0), round(e, 0)) for v, e in values]
            self.normalisation[sample] = new_values
        print self.normalisation

        self.is_normalised = True
        return

    def save(self):
        from dps.utils.file_utilities import write_data_to_JSON
        # If normalisation hasnt been calculated  - then go calculate it!
        if not self.is_normalised: self.calculate_normalisation()

        file_template = '{type}_{channel}.txt'
        output_folder = ''

        write_data_to_JSON(
            self.normalisation,
            output_folder + file_template.format(type='normalisation', channel=self.channel)
        )
        return 
