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
        self.normalisation = {}
        self.variable = None
        self.com = None
        self.channel = None
        self.name = None
        self.is_normalised = False
        self.central = False
        self.samples = {}
        self.setFromConfig()

    def setFromConfig(self):
        self.variable = self.measurement["variable"]
        self.com = self.measurement["com"]
        self.channel = self.measurement["channel"]
        self.samples = self.measurement["samples"]
        self.name = self.measurement["name"]
        # Is this central or a systematic?
        if "central" in self.name:
            self.central = True

        for sample, histogram_info in self.samples.iteritems():
            self.histograms[sample] = self.return_histogram(histogram_info)
            print hist_to_value_error_tuplelist(self.histograms[sample])
        return

    def return_histogram(self, d_hist_info, ignoreUnderflow=True):
        '''
        Takes basic histogram info and returns histo.
        '''
        from rootpy.io.file import File
        from rootpy.plotting import Hist
        from dps.utils.hist_utilities import fix_overflow

        f = d_hist_info['input_file']
        tree = d_hist_info['tree']
        var = d_hist_info['branch']
        bins = d_hist_info['bin_edges']
        weights = d_hist_info['weight_branches']
        weights = "*".join(weights)

        root_file = File( f )
        root_tree = root_file.Get( tree )

        root_histogram = Hist( bins )
        root_tree.Draw(var, weights, hist = root_histogram)

        # When a tree is filled with a dummy variable, it will end up in the underflow, so ignore it
        if ignoreUnderflow:
            root_histogram.SetBinContent(0, 0)
            root_histogram.SetBinError(0,0)

        # Fix overflow (Moves entries from overflow bin into last bin i.e. last bin not | | but |--> ) 
        root_histogram = fix_overflow(root_histogram)
        root_file.Close()
        return root_histogram

    def calculate_normalisation(self):
        '''
        '''
        # normalisation already calculated
        if self.is_normalised: return

        histograms = self.histograms
        self.background_subtraction(histograms)

        # next, let's round all numbers (they are event numbers after all)
        for sample, values in self.normalisation.items():
            new_values = [(round(v, 0), round(e, 0)) for v, e in values]
            self.normalisation[sample] = new_values
        print self.normalisation

        self.is_normalised = True
        return

    def background_subtraction(self, histograms):
        from dps.utils.hist_utilities import clean_control_region

        ttjet_hist = clean_control_region(
            histograms,
            # subtract=['QCD', 'V+Jets', 'SingleTop']
            subtract=['QCD']
        )
        self.normalisation['TTJet'] = hist_to_value_error_tuplelist(ttjet_hist)
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







# def get_histograms_from_trees(
#                               trees = [],
#                               branch = 'var',
#                               weightBranch = 'EventWeight',
#                               selection = '1',
#                               files = {},
#                               verbose = False,
#                               nBins = 40,
#                               xMin = 0,
#                               xMax = 100,
#                               ignoreUnderflow = True,
#                               ):
#     histograms = {}
#     nHistograms = 0

#     # Setup selection and weight string for ttree draw
#     weightAndSelection = '( %s ) * ( %s )' % ( weightBranch, selection )

#     for sample, input_file in files.iteritems():
#         root_file = File( input_file )

#         get_tree = root_file.Get
#         histograms[sample] = {}

#         for tree in trees:

#             tempTree = tree
#             if 'data' in sample and ( 'Up' in tempTree or 'Down' in tempTree ) :
#                 tempTree = tempTree.replace('_'+tempTree.split('_')[-1],'')

#             currentTree = get_tree( tempTree )
#             root_histogram = Hist( nBins, xMin, xMax)
#             currentTree.Draw(branch, weightAndSelection, hist = root_histogram)
#             if not is_valid_histogram( root_histogram, tree, input_file):
#                 return

#             # When a tree is filled with a dummy variable, it will end up in the underflow, so ignore it
#             if ignoreUnderflow:
#                 root_histogram.SetBinContent(0, 0)
#                 root_histogram.SetBinError(0,0)

#             gcd()
#             nHistograms += 1
#             histograms[sample][tree] = root_histogram.Clone()

#         root_file.Close()
#     return histograms

    # @staticmethod
    # def fromDict(d):
    #     m = None
    #     if d['class'] == 'dps.utils.measurement.Measurement':
    #         m = Measurement(d['name'])
    #     if d['class'] == 'dps.utils.measurement.Systematic':
    #         m = Systematic(d['name'], d['type'],
    #                        affected_samples=d['affected_samples'], scale=d['scale'])
    #     m.setVariable(d['variable'])
    #     m.setCentreOfMassEnergy(int(d['centre_of_mass_energy']))
    #     m.setChannel(d['channel'])
    #     m.setMETType(d['met_type'])
    #     for sample, i in d['samples'].items():
    #         if i.has_key('input'):
    #             inp = Input(**i['input'])
    #             m.addSample(sample, read=True, input=inp)
    #         else:
    #             m.addSample(sample, i['file'], i['hist'], read=True)
    #     for shape, obj in d['shapes'].items():
    #         m.addShapeForSample(shape, Measurement.fromDict(obj), read=True)
    #     for norm, obj in d['norms'].items():
    #         m.addNormForSample(
    #             norm, Measurement.fromDict(obj), read=True)
    #     return m






class Systematic(Measurement):

    '''
        The Systematic class is an extension of the Measurement class.
        It allows to implement systematic specific functionality
        (e.g. rate systematics).
    '''

    SHAPE = 10
    RATE = 20

    @meas_log.trace()
    def __init__(self, name,
                 stype=SHAPE,
                 affected_samples=[],
                 scale=1.):
        '''
        Constructor
        '''
        Measurement.__init__(self, name)
        self.type = stype

        self.affected_samples = affected_samples

        self.scale = scale

    @meas_log.trace()
    def toDict(self):
        output = Measurement.toDict(self)
        output['type'] = self.type
        output['affected_samples'] = self.affected_samples
        output['scale'] = self.scale

        return output
