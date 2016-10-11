'''
Created on 21 Aug 2015

@author: phxlk
'''
from rootpy.plotting.hist import Hist
from rootpy.io.file import root_open
from rootpy.interactive.rootwait import wait

if __name__ == '__main__':
    input_file = '/hdfs/TopQuarkGroup/run2/atOutput/13TeV/50ns/data_electron_tree.root'
    tree_path = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/FitVariables'
    h = Hist(100, 0, 2)
    with root_open(input_file) as f:
        tree = f.Get(tree_path)
        tree.Draw('PUWeight', 'PUWeight > 0', hist = h)
    h.Draw()
    wait()