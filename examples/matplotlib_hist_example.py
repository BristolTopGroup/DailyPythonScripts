#!/usr/bin/env python
import numpy as np
import matplotlib as mpl
mpl.use('agg')
from rootpy.plotting import Hist, HistStack
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from tools.plotting import Histogram_properties, make_data_mc_comparison_plot, make_control_region_comparison
import ROOT

# Setting this to True (default in rootpy)
# changes how the histograms look in ROOT...
ROOT.TH1.SetDefaultSumw2(False)
ROOT.gROOT.SetBatch(True)

# create normal distributions
mu1, mu2, sigma1, sigma2 = 100, 140, 15, 5
x1 = mu1 + sigma1 * np.random.randn(10000)
x2 = mu2 + sigma2 * np.random.randn(1000)
x1_obs = mu1 + sigma1 * np.random.randn(10000)
x2_obs = mu2 + sigma2 * np.random.randn(1000)

# create histograms
h1 = Hist(50, 40, 200, title='Background')
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
h1.legendstyle = 'F'

h2.fillstyle = 'solid'
h2.fillcolor = 'red'
h2.linecolor = 'red'
h2.linewidth = 0
h2.legendstyle = 'F'

stack = HistStack()
stack.Add(h1)
stack.Add(h2)

# plot with matplotlib
plot_with_plotting_script = True

if plot_with_plotting_script:
	properties = Histogram_properties()
	properties.name = 'matplotlib_hist'
	properties.x_axis_title = 'Mass'
	properties.y_axis_title = 'Events'
	make_data_mc_comparison_plot( [h3, h1, h2], ['data', 'background', 'signal'], ['black', 'green', 'red'], properties )
	
	properties.name += '_with_ratio'
	make_data_mc_comparison_plot( [h3, h1, h2], ['data', 'background', 'signal'], ['black', 'green', 'red'], properties, show_ratio = True )

	properties.name = 'matplotlib_hist_comparison'
	properties.y_limits = [0, 0.4]
	make_control_region_comparison( h1, h2, 'background', 'signal', properties )

else:
	fig = plt.figure(figsize=(14, 10), dpi=300)#, facecolor='white')
	axes = plt.axes()
	axes.xaxis.set_minor_locator(AutoMinorLocator())
	axes.yaxis.set_minor_locator(AutoMinorLocator())
	# axes.yaxis.set_major_locator(MultipleLocator(20))
	axes.tick_params(which='major', labelsize=15, length=8)
	axes.tick_params(which='minor', length=4)
	rplt.errorbar(h3, xerr=False, emptybins=False, axes=axes, zorder = 4)
	rplt.hist(stack, stacked=True, axes=axes, zorder = 1)
	plt.xlabel('Mass', position=(1., 0.), ha='right')
	plt.ylabel('Events', position=(0., 1.), va='bottom', ha='right')
	plt.legend(numpoints=1)
	plt.tight_layout()
	plt.savefig('plots/matplotlib_hist.pdf')
