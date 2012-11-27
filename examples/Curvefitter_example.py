'''
Created on 8 Nov 2012

@author: kreczko
'''

from tools.Fitting import CurveFit
import numpy as np
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt

# create normal distributions
mu1, sigma1 = 100, 15
x1 = mu1 + sigma1 * np.random.randn(10000)

h1 = Hist(100, 40, 200)
map(h1.Fill, x1)

hist_fit, bin_centres = CurveFit.fit(h1, 'gaus', [10000,mu1,sigma1])
fig = plt.figure(figsize=(16, 10), dpi=100, facecolor='white')
rplt.hist(h1, label=r'data', alpha = 0.7)
plt.plot(bin_centres, hist_fit, label='Fitted data')
plt.legend()
plt.savefig('plots/CurveFit.png')
