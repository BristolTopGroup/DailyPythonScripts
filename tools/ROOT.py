'''
Created on 12 May 2014

@author: kreczko
'''

import ROOT

def set_root_defaults():
    ROOT.SetBatch( True )
    ROOT.ProcessLine( 'gErrorIgnoreLevel = 1001;' )
