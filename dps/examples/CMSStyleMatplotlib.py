'''
Created on 30 Oct 2012

@author: kreczko
'''
import numpy as np
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from dps.config import CMS
CMS.axis_label_major['labelsize'] = 40
CMS.title['fontsize'] = 40
# create a normal distribution
mu, sigma = 100, 15
x = mu + sigma * np.random.randn(10000)

# create a histogram with 100 bins from 40 to 160
h = Hist(100, 40, 160)

# fill the histogram with our distribution
map(h.Fill, x)

# normalize the histogram
h /= h.Integral()

# set visual attributes
h.SetFillStyle('solid')
h.SetFillColor('green')
h.SetLineColor('green')

# the histogram of the data
plt.figure(figsize=(16, 12), dpi=200)
axes = plt.axes()
axes.minorticks_on()
rplt.hist(h, label=r'$\epsilon$(Something complicated)', alpha = 0.7)
plt.xlabel('Discovery', CMS.x_axis_title)
plt.ylabel('Probability of a discovery', CMS.y_axis_title)
#plt.title(r'combined, CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV',
#          fontsize=30,
#          verticalalignment='bottom')
#plt.title(r'e+jets, CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV',
#fontsize=30,
#          verticalalignment='bottom')
plt.title(r'$\mu$+jets, CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV', CMS.title)
# plt.annotate('look at this', xy=(60, 0.005), xytext=(50, 0.01),
#            arrowprops=dict(facecolor='black', shrink=0.05))
plt.tick_params(**CMS.axis_label_major)
plt.tick_params(**CMS.axis_label_minor)
plt.legend(numpoints=1, prop=CMS.legend_properties)
plt.tight_layout()
plt.savefig('plots/CMSStyleMatplotlib.png')
