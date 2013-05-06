'''
Created on 3 May 2013

@author: kreczko
'''
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import HistStack
from config import CMS
from matplotlib.patches import Rectangle

def make_data_mc_comparison_plot(histograms=[],
                                 histogram_lables=[],
                                 histogram_colors=[],
                                 histogram_name='Test',
                                 histogram_title="Test",
                                 x_axis_title="I am the x-axis",
                                 y_axis_title="I am the y-axis",
                                 x_limits=[],
                                 mc_error=0.,  # lets to flat error for now
                                 mc_errors_label='MC uncertainty',
                                 data_index=0,
                                 normalise=False,
                                 save_folder='plots/',
                                 save_as=['pdf', 'png']
                                 ):
    
    stack = HistStack()
    add_mc = stack.Add
    for index, histogram in enumerate(histograms):
        label = histogram_lables[index]
        color = histogram_colors[index]
        
        histogram.SetTitle(label)
        
        if not index == data_index:
            histogram.fillstyle = 'solid'
            histogram.fillcolor = color
            add_mc(histogram)
            
    data = histograms[data_index]
    data.SetMarkerSize(CMS.data_marker_size)
    
    # plot with matplotlib
    plt.figure(figsize=CMS.figsize, dpi=CMS.dpi, facecolor=CMS.facecolor)
    axes = plt.axes()
    
    if mc_error > 0:
        stack_lower = sum(stack.GetHists())
        stack_upper = stack_lower.Clone('upper')
        stack_lower.Scale(1 - mc_error)
        stack_upper.Scale(1 + mc_error)
        rplt.fill_between(stack_upper, stack_lower, axes, facecolor='0.75', alpha=0.5, hatch='/',zorder=2)
    rplt.errorbar(data, xerr=False, emptybins=False, axes=axes, elinewidth=2, capsize=10, capthick=2, zorder=3)
    rplt.hist(stack, stacked=True, axes=axes, zorder=1)
    
    
    plt.xlabel(x_axis_title, CMS.x_axis_title)
    plt.ylabel(y_axis_title, CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title(histogram_title, CMS.title)
    
    # put legend into the correct order (data is always first!
    handles, labels = axes.get_legend_handles_labels()
    data_label_index = labels.index('data')
    data_handle = handles[data_label_index]
    labels.remove('data')
    handles.remove(data_handle)
    labels.insert(0, 'data')
    handles.insert(0, data_handle)
    if mc_error > 0:
        p1 = Rectangle((0, 0), 1, 1, fc="0.75", alpha=0.5, hatch='/')
        handles.append(p1)
        labels.append(mc_errors_label)
    
    plt.legend(handles, labels, numpoints=1, loc='best', prop=CMS.legend_properties)
    if len(x_limits) == 2:
        axes.set_xlim(xmin=x_limits[0], xmax=x_limits[1])
    axes.set_ylim(ymin=0)
    plt.tight_layout()    
    
    for save in save_as:
        plt.savefig(save_folder + histogram_name + '.' + save)  
