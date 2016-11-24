'''
    Provides the classes Measurement and Systematic
'''
from __future__ import division
from . import log
import copy
from rootpy.io.file import Directory
from dps.utils.ROOT_utils import get_histogram_from_file
from dps.utils.file_utilities import make_folder_if_not_exists,\
    write_data_to_JSON, read_data_from_JSON
from dps.utils.input import Input
from dps.utils.hist_utilities import clean_control_region
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
        self.variable = None
        self.com = None
        self.channel = None
        self.name = None
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
            print sample
            print histogram_info
            self.histograms[sample] = self.get_measurement_histograms(histogram_info)

    def get_measurement_histograms(d_hist_info):
        '''
        Takes basic histogram info and reutrns histo.
        '''
        print d_hist_info
        return


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
