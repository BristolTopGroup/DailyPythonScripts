'''
    Provides the classes Measurement and Systematic
'''
from __future__ import division
from tools import log
import tools.ROOT_utils
import tools.file_utilities as fu
import tools.hist_utilities as hu
import tools.input as ti
import copy
from rootpy.io.file import Directory
# define logger for this module
meas_log = log["tools.measurement"]


class Measurement():

    '''
        The Measurement class combines files and histogram paths into
        one container. It also allows to provide separate shapes for the
        histograms while using the normalisation from the initial set.
    '''

    @meas_log.trace()
    def __init__(self, name):
        self.name = name
        self.variable = ''
        self.centre_of_mass_energy = 0
        self.channel = ''
        self.samples = {}
        self.shapes = {}
        self.norms = {}
        self.histograms = {}
        self.fit_variables = {}

        self.have_read_samples = False
        self.have_read_shapes = False
        self.have_read_norms = False

        self.met_type = ''

        self.type = 0

        self.aux_info_norms = {}

    @meas_log.trace()
    def addSample(self, sample, read=True, **kwargs):
        self.samples[sample] = kwargs
        # TODO: add tree & branch, selection etc
        # whatever get_histograms_from_trees needs
        if read:
            self.read_sample(sample)

    @meas_log.trace()
    def addShapeForSample(self, sample, measurement, read=True):
        self.shapes[sample] = measurement
        if read:
            self.read_shape(sample)

    @meas_log.trace()
    def addNormForSample(self, sample, measurement, read=True):
        self.norms[sample] = measurement
        if read:
            self.read_norm(sample)

    @meas_log.trace()
    def addFitVariable(self, variable, measurement):
        self.fit_variables[variable] = measurement

    @meas_log.trace()
    def toJSON(self, JSON_file):
        output = self.toDict()
        filename = JSON_file.split('/')[-1]
        directory = JSON_file.replace(filename, '')
        fu.make_folder_if_not_exists(directory)
        fu.write_data_to_JSON(output, JSON_file)

    @meas_log.trace()
    def toDict(self):
        output = {}
        output['class'] = str(self.__class__)
        output['name'] = self.name
        output['variable'] = self.variable
        output['centre_of_mass_energy'] = self.centre_of_mass_energy
        output['samples'] = self.samples
        output['shapes'] = {shape: meas.toDict()
                            for shape, meas in self.shapes.items()}
        output['norms'] = {norm: meas.toDict()
                           for norm, meas in self.norms.items()}
        output['channel'] = self.channel
        output['met_type'] = self.met_type
        for sample in output['samples'].keys():
            if output['samples'][sample].has_key('input'):
                output['samples'][sample]['input'] = output[
                    'samples'][sample]['input'].toDict()

        return output

    @staticmethod
    def fromJSON(JSON_file):
        src = fu.read_data_from_JSON(JSON_file)
        m = Measurement.fromDict(src)

        return m

    @staticmethod
    def fromDict(d):
        m = None
        if d['class'] == 'tools.measurement.Measurement':
            m = Measurement(d['name'])
        if d['class'] == 'tools.measurement.Systematic':
            m = Systematic(d['name'], d['type'],
                           affected_samples=d['affected_samples'], scale=d['scale'])
        m.setVariable(d['variable'])
        m.setCentreOfMassEnergy(int(d['centre_of_mass_energy']))
        m.setChannel(d['channel'])
        m.setMETType(d['met_type'])
        for sample, i in d['samples'].items():
            if i.has_key('input'):
                inp = ti.Input(**i['input'])
                m.addSample(sample, read=True, input=inp)
            else:
                m.addSample(sample, i['file'], i['hist'], read=True)
        for shape, obj in d['shapes'].items():
            m.addShapeForSample(shape, Measurement.fromDict(obj), read=True)
        for norm, obj in d['norms'].items():
            m.addNormForSample(
                norm, Measurement.fromDict(obj), read=True)
        return m

    @meas_log.trace()
    def toROOT(self):
        '''
            Converts measurement into something that can be stored in a ROOT
            file
        '''
        return
        d = Directory(name=self.name)
        # create shape and norm folders if there is anything to be saved
        # what needs to be saved
        # MET type
        return d

    @meas_log.trace()
    def setVariable(self, variable):
        self.variable = variable

    @meas_log.trace()
    def setCentreOfMassEnergy(self, com):
        self.centre_of_mass_energy = com

    @meas_log.trace()
    def setChannel(self, channel):
        self.channel = channel

    @meas_log.trace()
    def setMETType(self, met_type):
        self.met_type = met_type

    @meas_log.trace()
    def getCleanedShape(self, sample):
        subtract = copy.copy(self.histograms.keys())
        subtract.remove(sample)
        subtract.remove('data')
        hist = hu.clean_control_region(self.histograms,
                                       data_label='data',
                                       subtract=subtract,
                                       fix_to_zero=True)
        return hist

    @meas_log.trace()
    def read(self):
        self.read_samples()
        self.read_shapes()
        self.read_norms()

    @meas_log.trace()
    def read_samples(self):
        if self.have_read_samples:
            return
        for sample in self.samples.keys():
            self.read_sample(sample)
        self.have_read_samples = True

    @meas_log.trace()
    def read_sample(self, sample):
        if self.samples[sample].has_key('input'):
            i = self.samples[sample]['input']
            if isinstance(i, dict):
                i = ti.Input(**self.samples[sample]['input'])
            self.histograms[sample] = i.read()
            return
        input_file = self.samples[sample]['input_file']
        if self.samples[sample].has_key('hist'):
            hist = self.samples[sample]['hist']
            self.histograms[sample] = tools.ROOT_utils.get_histogram_from_file(
                hist, input_file)

    @meas_log.trace()
    def read_shapes(self):
        if self.have_read_shapes:
            return
        if not self.have_read_samples:
            self.read_samples()
        for sample in self.shapes.keys():
            self.read_shape(sample)
        self.have_read_shapes = True

    @meas_log.trace()
    def read_norms(self):
        if self.have_read_norms:
            return
        if not self.have_read_samples:
            self.read_samples()
        for sample in self.norms.keys():
            self.read_norm(sample)
        self.have_read_norms = True

    @meas_log.trace()
    def read_shape(self, sample):
        '''
            Shape from a Control Region (CR) is currently treated as:
             - define process A for which you which to get the shape
             - define CR
             - subtract other processes from data in the CR
             - normalise the result to process A in signal region
             - replace process A in signal region with the new histogram
        '''
        measurement = self.shapes[sample]
        shape = measurement.getCleanedShape(sample)
        if sample in self.histograms.keys():
            n_shape = shape.Integral()
            mc = self.histograms[sample]
            n_mc = mc.Integral()
            scale = 1
            if not n_shape == 0:
                if not n_mc == 0:
                    scale = 1 / n_shape * n_mc
                else:
                    scale = 1 / n_shape
            shape.Scale(scale)
            self.histograms[sample] = shape
        else:
            meas_log.warning(
                'No MC entry found for sample "{0}", using shape normalisation'.format(sample))
            self.histograms[sample] = shape

    @meas_log.trace()
    def read_norm(self, sample):
        '''
            Normalisation from a Control Region (CR) is currently treated as:
             - define normalisation for process A
             - define CR
             - subtract other processes from data in the CR
             - calculate the ratio between process A and data (both in CR)
             - apply ratio to process A in signal region
        '''
        measurement = self.norms[sample]
        self.aux_info_norms[sample] = {}
        # get ratio from control region
        norm = measurement.getCleanedShape(sample)
        mc_in_control = measurement.histograms[sample]
        # scale sample to this ratio
        if sample in self.histograms.keys():
            n_data_control = norm.Integral()
            n_mc_control = mc_in_control.Integral()
            ratio = n_data_control / n_mc_control
            meas_log.debug('Ratio from control region {0}'.format(ratio))
            n_mc_signal_region = self.histograms[sample].integral()
            self.histograms[sample].Scale(ratio)
            self.aux_info_norms[sample]['norm_factor'] = round(ratio, 2)
            self.aux_info_norms[sample]['n_mc_control'] = n_mc_control
            self.aux_info_norms[sample][
                'n_mc_signal_region'] = n_mc_signal_region
            self.aux_info_norms[sample]['n_data_control'] = n_data_control
        else:
            meas_log.warning(
                'No MC entry found for sample "{0}", using control region normalisation'.format(sample))
            self.histograms[sample] = norm


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
