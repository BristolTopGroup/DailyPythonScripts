from rootpy.tree import Tree
from random import gauss
from rootpy.plotting.hist import Hist
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
