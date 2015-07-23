from rootpy.tree import Tree
from random import gauss
from rootpy.plotting.hist import Hist, Hist2D
import numpy as np


def create_test_tree():
    tree = Tree("test")
    tree.create_branches(
        {'x': 'F',
         'y': 'F',
         'z': 'F',
         'i': 'I'})
    for i in xrange(10000):
        tree.x = gauss(.5, 1.)
        tree.y = gauss(.3, 2.)
        tree.z = gauss(13., 42.)
        tree.i = i
        tree.fill()
    return tree


def create_test_hist():
    h = Hist(100, -10, 10)
    h.SetName('test_hist')
    n = 9000
    mu, sigma = 0, 5
    x = mu + sigma * np.random.randn(n)
    map(h.Fill, x)

    return h


def create_high_purity_2D_hist():
    '''
        this creates
        [0.8, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0.6],
        this should result in a purity and stability value of 1 for all bins
        except the first and last. The first bin should have p = 1/1.8 and 
        s = 1/1.6 and the last bin should have p = 1/1.6 and s = 1/1.8
    '''
    n_bins_x = 6
    n_bins_y = 6
    hist = Hist2D(n_bins_x, -3, 3, n_bins_y, 0, 6)
    for i in range(1,  n_bins_x + 1):
        hist.SetBinContent(i, i, 1)
    hist.SetBinContent(1, n_bins_y, 0.8)
    hist.SetBinContent(n_bins_x, 1, 0.6)
    return hist
