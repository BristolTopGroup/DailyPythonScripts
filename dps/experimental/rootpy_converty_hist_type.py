'''
Created on 11 Mar 2015

@author: kreczko
'''

from rootpy.io import File
from rootpy.plotting import Hist
from rootpy import asrootpy

rootpy_hist = Hist( 100, 0, 100, type = 'F' )


rootpy_hist.SetName('hist')
test_file = File('test.root', 'RECREATE')
test_file.mkdir("test")
test_file.cd('test')
rootpy_hist.Write()
test_file.Write()
test_file.Close()

read_file = File('test.root')
folder = read_file.Get('test')
hist = folder.hist
print hist.TYPE
read_file.Close()

hist = None

read_file = File('test.root')
hist = read_file.Get('test/hist')
hist1 = hist.empty_clone(type='D')
print hist1.TYPE
read_file.Close()
