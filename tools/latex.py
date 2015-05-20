'''
Created on 5 May 2015

@author: kreczko
'''

from matplotlib import rc, rcParams
from config import CMS
import subprocess
import os
from distutils.spawn import find_executable


def setup_matplotlib():
    '''
        Seup matplotlib with all the latex fancyness we have
    '''
    rc( 'font', **CMS.font )
    rc( 'text', usetex = True )
    rcParams['text.latex.preamble'] = compile_package_list()
    
def compile_package_list():
    '''
        We are looking for 3 packages:
        - siunitx for scientific units
        - helvet for Helvetica font (CMS style)
        - sansmath for sans serif math (CMS style)
        For this we use the 'kpsewhich'
    '''
    package_list = []
    if is_installed('siunitx'):
        # upright \micro symbols, \TeV, etc
        package_list.append(r'\usepackage{siunitx}')
        # force siunitx to actually use your fonts
        package_list.append(r'\sisetup{detect-all}')
    if is_installed('helvet'):
        # set the normal font here
        package_list.append(r'\usepackage{helvet}')
    if is_installed('sansmath'):
        # load up the sansmath so that math -> helvet
        package_list.append(r'\usepackage{sansmath}')
        # <- tricky! -- gotta actually tell tex to use!
        package_list.append(r'\sansmath')
        
    return package_list

def is_installed(latex_package):
    # check if we have 'kpsewhich' installed
    cmd = 'kpsewhich'
    if find_executable(cmd) is None:
        print 'Latex::WARNING: kpsewhich is not available'
        return False
    p = subprocess.check_output([cmd, latex_package + '.sty'])
    # strip the line break
    p = p.rstrip('\n')
    # check if file exists
    return os.path.exists(p)
    
    
if __name__ == '__main__':
    print compile_package_list()
