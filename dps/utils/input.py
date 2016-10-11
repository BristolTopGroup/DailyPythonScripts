'''
    Helper classes for inputs
'''
import os
from rootpy.io import File

from . import log
from dps.utils.file_utilities import read_data_from_JSON, write_data_to_JSON
from dps.utils.ROOT_utils import get_histogram_from_file,\
    get_histogram_from_tree

# define logger for this module
input_log = log["dps.utils.input"]


class Input():

    '''
        Base class for input
    '''
    @input_log.trace()
    def __init__(self, **kwargs):
        '''
            Takes
            @param input_file
            @param hist: input histogram path
            @param tree: input tree
            @param branch: branch to be used
            @param selection: selection to be used
            @param weight_branches: branches to be (multiplicatively) used as event weight
            @param n_bins: number of bins for histogram if from tree
            @param x_min: min value for histogram from tree
            @param x_max: max value for histogram from tree
            @param lumi_scale: the lumi scale for this input
            @param scale: all other scales
        '''
        if kwargs.has_key('input_file'):
            self.file = kwargs.pop('input_file')
        else:
            self.file = kwargs.pop('file')
        if self.file.endswith('.root'):
            self.file_type = 'ROOT'
        if self.file.endswith('.txt') or self.file.endswith('.json'):
            self.file_type = 'JSON'

        self.hist = None
        self.hist_name = None
        self.tree = None
        self.tree_name = None
        self.selection = '1'
        self.weight_branches = ['EventWeight']
        self.selection_branches = []
        self.lumi_scale = 1.0
        self.scale = 1.0

        if kwargs.has_key('hist'):
            self.hist_name = kwargs.pop('hist')
        if kwargs.has_key('tree'):
            self.tree_name = kwargs.pop('tree')
            self.branch = kwargs.pop('branch')
        if kwargs.has_key('selection'):
            self.selection = kwargs.pop('selection')
        if kwargs.has_key('weight_branches'):
            self.weight_branches = kwargs.pop('weight_branches')
        if kwargs.has_key('selection_branches'):
            self.selection_branches = kwargs.pop('selection_branches')
        if kwargs.has_key('lumi_scale'):
            self.lumi_scale = kwargs.pop('lumi_scale')
        # all other scales
        if kwargs.has_key('scale'):
            self.scale = kwargs.pop('scale')
        # store remaining parameters
        self.kwargs = kwargs
        self.error = ''

    @input_log.trace()
    def isValid(self):
        # file has to exists
        if not os.path.exists(self.file):
            msg = 'File does not exist: ' + self.file
            self.error = msg
            input_log.debug(msg)
            return False
        if self.hist_name:
            with File.open(self.file) as f:
                if not f.__contains__(self.hist_name):
                    msg = 'File "{0}" does not contain histogram "{1}"'
                    msg = msg.format(self.file, self.hist_name)
                    self.error = msg
                    input_log.debug(msg)
                    return False
        if self.tree_name:
            with File.open(self.file) as f:
                if not f.__contains__(self.tree_name):
                    msg = 'File "{0}" does not contain tree "{1}"'
                    msg = msg.format(self.file, self.tree_name)
                    self.error = msg
                    input_log.debug(msg)
                    return False
                tree = f[self.tree_name]
                branchToCheck = self.branch
                if '[' in branchToCheck and ']' in branchToCheck:
                    branchToCheck = branchToCheck.split('[')[0]
                elif 'abs(' in branchToCheck:
                    branchToCheck = branchToCheck.split('(')[-1].split(')')[0]
                if not tree.has_branch(branchToCheck):
                    msg = 'Tree "{0}" does not contain branch "{1}"'
                    msg = msg.format(self.tree_name, branchToCheck)
                    self.error = msg
                    input_log.debug(msg)
                    return False
        return True

    @input_log.trace()
    def read(self):
        if not self.isValid():
            raise ValueError('Inputs are not valid {0}'.format(self.error))

        if self.hist_name:
            self.hist = get_histogram_from_file(
                self.hist_name, self.file)

        if self.tree_name:
            self.hist = get_histogram_from_tree(
                tree=self.tree_name,
                branch=self.branch,
                weight_branches=self.weight_branches,
                selection=self.selection,
                input_file=self.file,
                **self.kwargs
            )
        self.hist.Scale(self.lumi_scale * self.scale)
        return self.hist

    @staticmethod
    def fromJSON(json_file):
        src = read_data_from_JSON(json_file)
        i = Input(**src)
        return i

    @input_log.trace()
    def toJSON(self, json_file):
        d = self.toDict()
        write_data_to_JSON(d, json_file)

    @input_log.trace()
    def toDict(self):
        d = {}
        d.update(self.kwargs)
        d['class'] = str(self.__class__)
        d['input_file'] = self.file
        if self.hist_name:
            d['hist'] = self.hist_name
        if self.tree_name:
            d['tree'] = self.tree_name
            d['branch'] = self.branch
            d['selection'] = self.selection
            d['weight_branches'] = self.weight_branches
            d['selection_branches'] = self.selection_branches
            d['lumi_scale'] = self.lumi_scale
            d['scale'] = self.scale
        return d
