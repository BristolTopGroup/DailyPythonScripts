from rootplot.core import plotmpl, plot, rootplot, rootplotmpl
import inputFiles

data = inputFiles.files['data']
ttbar = inputFiles.files['ttbar']
print data
print ttbar
#rootplotmpl(data, ttbar, path='topReconstruction/mttbar_withMETAndAsymJets_0orMoreBtag', output='plots', rebin=50, range = (0,1), data=1, 
#         fill=True, data_marker = 8, data_color=(255,0,0), legend_entries='data, ttbar',
#         xmin=300, xmax=2500, overflow=True, underflow = True)

rootplotmpl(data, output='plots')
#plotmpl(data, ttbar, 'topReconstruction/mttbar_withMETAndAsymJets_0orMoreBtag', output='plots', debug = True, ext = 'png', hist=True)