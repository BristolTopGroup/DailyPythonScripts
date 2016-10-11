from rootpy.tree import Tree, TreeModel, FloatCol, BoolCol
from rootpy.io import root_open
from random import gauss
import random

random.seed(0)


class Sample(TreeModel):
    a = FloatCol()
    b = FloatCol()
    label = BoolCol()


with root_open('sample.root', 'recreate'):
    tree = Tree('sample', model=Sample)
    for i in xrange(10000):
        if i % 4 == 0:
            tree.a = gauss(1, 1)
            tree.b = gauss(1, 1)
            tree.label = True
        elif i % 4 == 1:
            tree.a = gauss(1, 1)
            tree.b = gauss(-1.5, 1)
            tree.label = False
        elif i % 4 == 2:
            tree.a = gauss(-1.5, 1)
            tree.b = gauss(-1, 1)
            tree.label = True
        else:
            tree.a = gauss(-1, 1)
            tree.b = gauss(1, 1)
            tree.label = False
        tree.Fill()
    tree.write()
