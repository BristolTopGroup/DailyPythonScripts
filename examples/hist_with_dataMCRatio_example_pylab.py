#!/usr/bin/env python
import numpy as np
from rootpy.plotting import Hist, HistStack
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import ROOT
from config import CMS
from pylab import subplot
# Setting this to True (default in rootpy)
# changes how the histograms look in ROOT...
ROOT.TH1.SetDefaultSumw2(False)
ROOT.gROOT.SetBatch(True)

# create normal distributions
mu1, mu2, sigma1, sigma2 = 100, 140, 15, 5
x1 = mu1 + sigma1 * np.random.randn(10000)
x2 = mu2 + sigma2 * np.random.randn(500)
x1_obs = mu1 + sigma1 * np.random.randn(10000)
x2_obs = mu2 + sigma2 * np.random.randn(1000)

# create histograms
h1 = Hist(100, 40, 200, title='Background')
h2 = h1.Clone(title='Signal')
h3 = h1.Clone(title='Data')
h3.markersize=1.2

# fill the histograms with our distributions
map(h1.Fill, x1)
map(h2.Fill, x2)
map(h3.Fill, x1_obs)
map(h3.Fill, x2_obs)

# set visual attributes
h1.fillstyle = 'solid'
h1.fillcolor = 'green'
h1.linecolor = 'green'
h1.linewidth = 0

h2.fillstyle = 'solid'
h2.fillcolor = 'red'
h2.linecolor = 'red'
h2.linewidth = 0

stack = HistStack()
stack.Add(h1)
stack.Add(h2)

ratio = h3/(h1+h2)
ratio = Hist.divide(h3, h1+h2)

# plot with matplotlib

plt.figure(figsize=(16, 12), dpi=200)
subplot(211)
rplt.bar(stack, stacked=True)
rplt.errorbar(h3, xerr=False, emptybins=False)
plt.xlabel('Mass', position=(1., 0.), ha='right', fontsize = 24)
plt.ylabel('Events', position=(0., 1.), va='top', fontsize = 24)
plt.tick_params(**CMS.axis_label_major)
plt.tick_params(**CMS.axis_label_minor)
plt.legend(numpoints=1)
subplot(212)
rplt.errorbar(ratio, emptybins=False)
plt.savefig('plots/Hist_with_dataMCRatio_pylab.png')
