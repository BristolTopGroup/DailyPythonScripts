'''
    Provides the classes Measurement and Systematic
'''
from tools import log
import tools.ROOT_utils
import tools.file_utilities as fu
import tools.hist_utilities as hu
import copy
# define logger for this module
meas_log = log["tools.measurement"]

class Measurement():
    '''
        The Measurement class combines files and histogram paths into
        one container. It also allows to provide separate shapes for the
        histograms while using the normalisation from the initial set.
    '''

    @meas_log.trace()
    def __init__( self, name ):
        self.name = name
        self.variable = ''
        self.centre_of_mass_energy = 0
        self.channel = ''
        self.samples = {}
        self.shapes = {}
        self.histograms = {}
        self.fit_variables = {}

        self.have_read_samples = False

        self.met_type = ''

    def addSample( self, sample, input_file, histogram_path, read = True ):
        self.samples[sample] = {'file': input_file,
                                'hist': histogram_path}
        if read:
            self.read_sample( sample )

    def addShapeForSample( self, sample, measurement, read = True ):
        self.shapes[sample] = measurement
        if read:
            self.read_shape( sample )

    def addFitVariable( self, variable, measurement ):
        self.fit_variables[variable] = measurement

    def toJSON( self, JSON_file ):
        output = self.toDict()
        filename = JSON_file.split( '/' )[-1]
        directory = JSON_file.replace( filename, '' )
        fu.make_folder_if_not_exists( directory )
        fu.write_data_to_JSON( output, JSON_file )

    def toDict( self ):
        output = {}
        output['class'] = str( self.__class__ )
        output['name'] = self.name
        output['variable'] = self.variable
        output['centre_of_mass_energy'] = self.centre_of_mass_energy
        output['samples'] = self.samples
        output['shapes'] = {shape : meas.toDict() for shape, meas in self.shapes.items()}
        output['channel'] = self.channel
        output['met_type'] = self.met_type
        return output

    @staticmethod
    def fromJSON( JSON_file ):
        src = fu.read_data_from_JSON( JSON_file )
        m = Measurement.fromDict( src )

        return m

    @staticmethod
    def fromDict( d ):
        m = None
        if d['class'] == 'tools.measurement.Measurement':
            m = Measurement( d['name'] )
        if d['class'] == 'tools.measurement.Systematic':
            m = Systematic( d['name'], d['type'],
                           affected_samples = d['affected_samples'], scale = d['scale'] )
        m.setVariable( d['variable'] )
        m.setCentreOfMassEnergy( int( d['centre_of_mass_energy'] ) )
        m.setChannel( d['channel'] )
        m.setMETType( d['met_type'] )
        for sample, i in d['samples'].items():
            m.addSample( sample, i['file'], i['hist'], read = True )
        for shape, obj in d['shapes'].items():
            m.addShapeForSample( shape, Measurement.fromDict( obj ), read = True )
        return m

    def setVariable( self, variable ):
        self.variable = variable

    def setCentreOfMassEnergy( self, com ):
        self.centre_of_mass_energy = com

    def setChannel( self, channel ):
        self.channel = channel

    def setMETType( self, met_type ):
        self.met_type = met_type

    def getCleanedShape( self, sample ):
        subtract = copy.copy( self.histograms.keys() )
        subtract.remove( sample )
        hist = hu.clean_control_region( self.histograms,
                                       data_label = sample,
                                       subtract = subtract,
                                       fix_to_zero = True )
        return hist

    def read_samples( self ):
        if self.have_read_samples:
            return
        for sample in self.samples.keys():
            self.read_sample( sample )
        self.have_read_samples = True

    def read_sample( self, sample ):
        histogram_path = self.samples[sample]['hist']
        input_file = self.samples[sample]['file']
        self.histograms[sample] = tools.ROOT_utils.get_histogram_from_file( histogram_path, input_file )

    def read_shapes( self ):
        if not self.have_read_samples:
            self.read_samples()
        for sample in self.shapes.keys():
            self.read_shape( sample )

    def read_shape( self, sample ):
        measurement = self.shapes[sample]
        shape = measurement.getCleanedShape( sample )
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
            shape.Scale( scale )
            self.histograms[sample] = shape
        else:
            meas_log.warning( 'No MC entry found for sample "{0}", using shape normalisation'.format( sample ) )
            self.histograms[sample] = shape

class Systematic( Measurement ):
    '''
        The Systematic class is an extension of the Measurement class.
        It allows to implement systematic specific functionality
        (e.g. rate systematics).
    '''
    
    SHAPE = 10
    RATE = 20


    def __init__( self, name,
                 stype = SHAPE,
                 affected_samples = [],
                 scale = 1. ):
        '''
        Constructor
        '''
        Measurement.__init__( self, name )
        self.type = stype
        
        self.affected_samples = affected_samples
        
        self.scale = scale

    def toDict( self ):
        output = Measurement.toDict( self )
        output['type'] = self.type
        output['affected_samples'] = self.affected_samples
        output['scale'] = self.scale

        return output

    def scale_histograms( self ):
        if self.type == Systematic.RATE:
            for sample in self.affected_samples:
                self.histograms[sample].Scale( self.scale )
