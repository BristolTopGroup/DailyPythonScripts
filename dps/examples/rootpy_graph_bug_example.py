from rootpy.plotting import Hist, Graph
from rootpy import asrootpy
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt

value_error_tuplelist = [(0.0, 0.0), (17808.0, 133.4466185408982), (12051.0, 109.77704678119193), (8626.0, 92.87626176801045), (6378.0, 79.86238163240563), (13160.0, 114.71704319759989), (5553.0, 74.51845409024533)]
value_errors_tuplelist = [(20,1,0.5), (21,2,1), (18,3,4)]
bin_edges = [0, 30, 35, 40, 45, 50, 70, 100]
rootpy_hist = Hist(bin_edges)
set_bin_value = rootpy_hist.SetBinContent
set_bin_error = rootpy_hist.SetBinError
for bin_i, (value, error) in enumerate(value_error_tuplelist):
    set_bin_value(bin_i + 1, value)
    set_bin_error(bin_i + 1, error)

value_error_tuplelist = [(0.0, 0.0), (13146.0, 114.65600725648875), (11114.0, 105.4229576515476), (8373.0, 91.50409826887537), (6284.0, 79.27168473042566), (13022.0, 114.11397810960759), (5517.0, 74.27651041883968)]
value_errors_tuplelist = [(20,1,0.5), (21,2,1), (18,3,4)]
bin_edges = [0, 30, 35, 40, 45, 50, 70, 100]
rootpy_hist_passed = Hist(bin_edges)
set_bin_value = rootpy_hist_passed.SetBinContent
set_bin_error = rootpy_hist_passed.SetBinError
for bin_i, (value, error) in enumerate(value_error_tuplelist):
    set_bin_value(bin_i + 1, value)
    set_bin_error(bin_i + 1, error)

#works with TGraphAsymmErrors
from ROOT import TGraphAsymmErrors        
rootpy_graph = asrootpy(TGraphAsymmErrors()) 
rootpy_graph.Divide(rootpy_hist_passed, rootpy_hist, "cl=0.683 b(1,1) mode")
#hist = rootpy_hist
#rootpy_graph = Graph(hist)
set_lower_error = rootpy_graph.SetPointEYlow
set_upper_error = rootpy_graph.SetPointEYhigh
   
# for point_i, (value, lower_error, upper_error) in enumerate(value_errors_tuplelist):
#     set_lower_error(point_i, lower_error)
#     set_upper_error(point_i, upper_error)
        
plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
axes = plt.axes()
axes.minorticks_on()
    
plt.xlabel('X')
plt.ylabel('y')
#rootpy_graph.visible = True #if commented out -> trace 1, else -> trace 2
rplt.errorbar(rootpy_graph, axes=axes)
plt.title('title')
plt.savefig('bug.png')

################# trace 1 ############################
'''
Traceback (most recent call last):
  File "examples/rootpy_graph_bug_example.py", line 34, in <module>
    rplt.errorbar(rootpy_graph, axes=axes, label='I am buggy', xerr=False, capsize=0, elinewidth=2)
  File "/storage/Workspace/Analysis/DailyPythonScripts/external/rootpy/rootpy/plotting/root2matplotlib.py", line 359, in errorbar
    axes=axes, emptybins=emptybins, **kwargs)
  File "/storage/Workspace/Analysis/DailyPythonScripts/external/rootpy/rootpy/plotting/root2matplotlib.py", line 381, in _errorbar
    _set_defaults(h, kwargs, ['common', 'errors', 'errorbar', 'marker'])
  File "/storage/Workspace/Analysis/DailyPythonScripts/external/rootpy/rootpy/plotting/root2matplotlib.py", line 27, in _set_defaults
    defaults['visible'] = h.visible
AttributeError: 'Graph' object has no attribute 'visible'
'''
################# trace 2 ############################
'''
Traceback (most recent call last):
  File "examples/rootpy_graph_bug_example.py", line 53, in <module>
    rplt.errorbar(rootpy_graph, axes=axes, label='I am buggy', xerr=False, capsize=0, elinewidth=2)
  File "/storage/Workspace/Analysis/DailyPythonScripts/external/rootpy/rootpy/plotting/root2matplotlib.py", line 359, in errorbar
    axes=axes, emptybins=emptybins, **kwargs)
  File "/storage/Workspace/Analysis/DailyPythonScripts/external/rootpy/rootpy/plotting/root2matplotlib.py", line 381, in _errorbar
    _set_defaults(h, kwargs, ['common', 'errors', 'errorbar', 'marker'])
  File "/storage/Workspace/Analysis/DailyPythonScripts/external/rootpy/rootpy/plotting/root2matplotlib.py", line 41, in _set_defaults
    defaults['ecolor'] = h.GetLineColor('mpl')
  File "/storage/Workspace/Analysis/DailyPythonScripts/external/rootpy/rootpy/plotting/core.py", line 234, in GetLineColor
    return self._linecolor(mode)
AttributeError: 'Graph' object has no attribute '_linecolor'
'''
