class Config(object):
    ''' 
    A class that enables the storing all attributes in a dictionary
    '''
    def __init__(self, data = {}, **kw):
        object.__init__(self)
        self.data = data
        self.data.update(kw)
        self.defaults = {}
        
    def __getattribute__(self, name):
        if name in ['data', 'defaults', 'param_']:
            return object.__getattribute__(self, name)
        
        if self.data.has_key(name):
            return self.data.get(name)
        elif self.defaults.has_key(name):
            return self.defaults.get(name)
        else:
            self.data[name] = None
            print 'here'
            return self.data[name]
        
    def __setattr__(self, name, value):
        if name in ['data', 'defaults']:
            return object.__setattr__(self, name, value) 
        
        self.data[name] = value
        
        return
    
    def __delattr__(self, name):
        if name in ['data', 'defaults']:
            object.__delattr__(self, name)
        else:
            if self.data.has_key(name):
                self.data.remove(name)
            elif self.defaults.has_key(name):
                self.defaults.remove(name) 
        return
    
    def param_(self, name):
        if self.data.has_key(name):
            return self.data.get(name)
        elif self.defaults.has_key(name):
            return self.defaults.get(name)
        else:
            self.__setattr__(name, value = None)
            return self.__getattribute__(name)
        
class XSectionConfig(Config):
    parameters = ['met_systematics_suffixes', 'analysis_types', 
                  'translate_options', 'ttbar_theory_systematic_prefix',
                  'vjets_theory_systematic_prefix']
    
    def __init__(self, data = {}, **kw):
        Config.__init__(self, data)
        self.update(kw)
        self.__fill_defaults__()

    def __fill_defaults__(self):
        self.defaults = {}