'''
Created on 16 Jun 2015

@author: kreczko
'''

from tools.toy_mc import generate_n_poisson_weights_for_average
from rootpy.interactive.rootwait import wait

a = generate_n_poisson_weights_for_average(10000, [2000, 5000, 3000, 1000, 500])
print min(a), max(a)
from rootpy.plotting import Hist
h = Hist(100, min(a), max(a))
for i in a:
    h.fill(i)
h.Fit("gaus")
h.Draw()
wait()
