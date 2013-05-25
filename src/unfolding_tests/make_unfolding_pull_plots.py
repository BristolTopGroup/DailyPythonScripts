'''
Created on 3 Mar 2013

@author: kreczko
'''
# take input folder
# read all *.txt
# but the fit is not saved :(
# I could save the fit using EVAL ...
from __future__ import division
from ROOT import gROOT
from optparse import OptionParser
from glob import glob
import sys

import numpy
from numpy import frompyfunc
from pylab import plot

from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt


from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import hist_to_value_error_tuplelist
from tools.hist_utilities import value_error_tuplelist_to_hist
from config import CMS

from matplotlib import rc
rc('text', usetex=True)

hist_data = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (2.0, 1.4142135623730951), (0.0, 0.0), (0.0, 0.0), (4.0, 2.0), (1.0, 1.0), (4.0, 2.0), (1.0, 1.0), (3.0, 1.7320508075688772), (4.0, 2.0), (7.0, 2.6457513110645907), (7.0, 2.6457513110645907), (5.0, 2.23606797749979), (14.0, 3.7416573867739413), (9.0, 3.0), (14.0, 3.7416573867739413), (17.0, 4.123105625617661), (18.0, 4.242640687119285), (33.0, 5.744562646538029), (41.0, 6.4031242374328485), (57.0, 7.54983443527075), (65.0, 8.06225774829855), (73.0, 8.54400374531753), (76.0, 8.717797887081348), (108.0, 10.392304845413264), (125.0, 11.180339887498949), (155.0, 12.449899597988733), (183.0, 13.527749258468683), (218.0, 14.7648230602334), (278.0, 16.673332000533065), (357.0, 18.894443627691185), (410.0, 20.248456731316587), (524.0, 22.891046284519195), (654.0, 25.573423705088842), (800.0, 28.284271247461902), (997.0, 31.575306807693888), (1228.0, 35.04283093587046), (1532.0, 39.14077158156185), (1914.0, 43.749285708454714), (2222.0, 47.138094997570704), (2781.0, 52.73518749374084), (3470.0, 58.90670590009256), (4274.0, 65.37583651472461), (5281.0, 72.67048919609665), (6308.0, 79.42291860665912), (8105.0, 90.02777349240623), (9393.0, 96.91749068150702), (11699.0, 108.16191566350885), (14193.0, 119.13437790998869), (16879.0, 129.9192056625963), (20225.0, 142.21462653327893), (24106.0, 155.2610704587599), (28475.0, 168.74537030686204), (33932.0, 184.20640596895646), (39777.0, 199.44172081086745), (46662.0, 216.01388844238696), (54651.0, 233.77553336480702), (63060.0, 251.11750237687536), (73221.0, 270.5937915030572), (83516.0, 288.99134935149874), (95851.0, 309.59812660931914), (108586.0, 329.5238989815458), (122795.0, 350.4211751592646), (138574.0, 372.2552887468491), (156076.0, 395.0645516874426), (173636.0, 416.69653226298874), (193267.0, 439.6214280491796), (213258.0, 461.7986574255062), (235074.0, 484.8443049062245), (257108.0, 507.05818206592426), (279759.0, 528.9224895955929), (303596.0, 550.9954627762373), (326327.0, 571.250382932038), (352105.0, 593.3843611016388), (374913.0, 612.3013963727341), (398969.0, 631.6399290735189), (422192.0, 649.7630337284509), (444307.0, 666.5635753624706), (464581.0, 681.6017899037531), (483838.0, 695.5846461790254), (502032.0, 708.5421652943458), (517383.0, 719.2934032785231), (531776.0, 729.2297306062062), (542853.0, 736.7855861782314), (552422.0, 743.2509670360342), (557946.0, 746.9578301350084), (560817.0, 748.8771594861203), (561853.0, 749.5685425629867), (557864.0, 746.902938807982), (553389.0, 743.9012031177258), (545594.0, 738.6433510159013), (533600.0, 730.479294709987), (520837.0, 721.6903768237456), (505033.0, 710.6567385172675), (487720.0, 698.3695296904068), (467598.0, 683.8113775011352), (445852.0, 667.7214988301635), (424574.0, 651.5934315199931), (398743.0, 631.4610043383518), (376152.0, 613.3123184805601), (351405.0, 592.794230741157), (327472.0, 572.2516928764825), (300706.0, 548.366665653557), (277157.0, 526.4570257865308), (253412.0, 503.4004370280185), (230029.0, 479.6133859683234), (207973.0, 456.0405683708413), (187028.0, 432.46733980729687), (166387.0, 407.9056263402112), (148491.0, 385.3452996988545), (132298.0, 363.72792029207767), (115029.0, 339.1592546282646), (100410.0, 316.8753698222694), (88223.0, 297.02356808845997), (75413.0, 274.6142749385035), (64811.0, 254.58004635084816), (55310.0, 235.18078152774302), (47136.0, 217.10826792179057), (39443.0, 198.60261831103838), (33303.0, 182.4910956731862), (27514.0, 165.873445734994), (22954.0, 151.50577546747186), (19179.0, 138.4882666510055), (15534.0, 124.63546846704592), (12395.0, 111.33283433021904), (10046.0, 100.22973610660661), (8111.0, 90.06109037758759), (6449.0, 80.30566605165541), (5138.0, 71.6798437498297), (4032.0, 63.49803146555018), (3117.0, 55.83009940883144), (2408.0, 49.07137658554119), (1853.0, 43.04648650006177), (1396.0, 37.36308338453881), (1017.0, 31.89043743820395), (794.0, 28.178005607210743), (600.0, 24.49489742783178), (426.0, 20.639767440550294), (323.0, 17.97220075561143), (216.0, 14.696938456699069), (159.0, 12.609520212918492), (126.0, 11.224972160321824), (77.0, 8.774964387392123), (61.0, 7.810249675906654), (37.0, 6.082762530298219), (28.0, 5.291502622129181), (13.0, 3.605551275463989), (16.0, 4.0), (6.0, 2.449489742783178), (9.0, 3.0), (3.0, 1.7320508075688772), (4.0, 2.0), (2.0, 1.4142135623730951), (0.0, 0.0), (0.0, 0.0), (1.0, 1.0), (1.0, 1.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
hist_min_x = -9
hist_max_x = 9
hist_n_bins = 180



#def get_data(files):
#    # this takes a LOT of memory
#    data = []
#    extend = data.extend
#    read = read_data_from_JSON
#    for f in files:
#        extend(read(f))
#    return data

#def get_pulls(files):  # no bin resolution! just take them as equals
#    all_pulls = []
#    extend = all_pulls.extend
#    read = read_data_from_JSON
#    for f in files:
#        data = read(f)
#        for entry in data:  # loop over all data entries
#            extend(entry['pull'])
#    return all_pulls

def get_data(files, subset = ''): 
    # this takes a LOT of memory, please use subset!!
    all_data = []
    extend = all_data.extend
    read = read_data_from_JSON
    for f in files:
        data = read(f)
        
        if subset:
            for entry in data:  # loop over all data entries
                extend(entry[subset])
        else:
            extend(data)
                
    return all_data

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step
        
def plot_pull(pulls, bin_index = None, n_bins = 1):
    min_x, max_x = min(pulls), max(pulls)
    abs_max = int(max(abs(min_x), max_x))
    n_x_bins = 2 * abs_max * 10  # bin width = 0.1
#    print n_x_bins, -abs_max, abs_max
    h_pull = Hist(n_x_bins, -abs_max, abs_max)
    filling = h_pull.Fill
    
    for pull_index, pull in enumerate(pulls):
            
        if not bin_index is None:
            matches_bin = (pull_index - bin_index) %(n_bins) == 0
            if pull_index < n_bins:#first set correction
                matches_bin = pull_index == bin_index
            if not matches_bin:
                continue
        filling(pull)
    
    stats = len(pulls)
#    print stats
#    h_list = hist_to_value_error_tuplelist(h_pull)
#    print h_list
#    print len(hist_data), min(hist_data), max(hist_data)
    if bin_index is None:
        plot_h_pull(h_pull, stats = stats, name = 'pull_from_files_all_bins_stats_%d' % stats)
    else:
        plot_h_pull(h_pull, stats = stats, name = 'pull_from_files_bin_%d_stats_%d' % (bin_index, stats))
    
def plot_pull_from_list():
    stats = 19596500
    bin_width = (2.0 * hist_max_x) / hist_n_bins
    print hist_n_bins, bin_width
    bin_edges = list(drange(hist_min_x, hist_max_x, bin_width))
    print bin_edges
    print len(bin_edges)
    h_pull = value_error_tuplelist_to_hist(hist_data, bin_edges)
    plot_h_pull(h_pull, stats = stats, name = 'pull_from_list' )    

def plot_h_pull(h_pull, stats = 19596500, name = 'pull_test'):
    h_pull.Fit('gaus', 'WWSQ')
    fit_pull = h_pull.GetFunction('gaus')
    mean = (fit_pull.GetParameter(1), fit_pull.GetParError(1))
    sigma = (fit_pull.GetParameter(2), fit_pull.GetParError(2))
    print 'Fit data for "' + name + '"'
    print 'A:', fit_pull.GetParameter(0), '+-', fit_pull.GetParError(0)
    print 'mean:', fit_pull.GetParameter(1), '+-', fit_pull.GetParError(1)
    print 'sigma:', fit_pull.GetParameter(2), '+-', fit_pull.GetParError(2)
    
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_pull.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_pull, xerr=True, emptybins=True, axes=axes)
    
    x = numpy.linspace(fit_pull.GetXmin(), fit_pull.GetXmax(), fit_pull.GetNpx()*4)#*4 for a very smooth curve
    function_data = frompyfunc(fit_pull.Eval, 1, 1)
    plot(x, function_data(x), axes=axes, color='red', linewidth=2)
    
    
    plt.xlabel('$\\frac{\mathrm{unfolded} - \mathrm{true}}{\sigma}$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title('Pull distribution for SVD unfolding', CMS.title)
    text = 'entries = %d \n mean = $%.2f \pm %.2f$ \n $\sigma = %.2f \pm %.2f$' % (stats, mean[0], mean[1], sigma[0], sigma[1])
    axes.text(0.6, 0.8, text,
        verticalalignment='bottom', horizontalalignment='left',
        transform=axes.transAxes,
        color='black', fontsize=40, bbox=dict(facecolor='white', edgecolor='none', alpha=0.5))
    plt.tight_layout()  
    
    save_folder = 'plots/'
    save_as = ['png', 'pdf']
    for save in save_as:
        plt.savefig(save_folder + name + '.' + save)        

def plot_difference(difference):
    stats = len(difference)    
    values, errors = [],[]
    add_value = values.append
    add_error = errors.append
    for value, error in difference:
        add_value(value)
        add_error(error)
    min_x, max_x = min(values), max(values)
    abs_max = int(max(abs(min_x), max_x))
#    n_x_bins = 2 * abs_max * 10    
    h_values = Hist(100, -abs_max, abs_max)
    fill_value = h_values.Fill
    for value in values:
        fill_value(value)
        
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_values.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_values, xerr=True, emptybins=True, axes=axes)
    
    plt.xlabel('$\mathrm{unfolded} - \mathrm{true}$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title('SVD unfolding performance', CMS.title)
    plt.tight_layout()  
    
    save_folder = 'plots/'
    save_as = ['png', 'pdf']
    for save in save_as:
        plt.savefig(save_folder + 'difference_stats_' + str(stats) + '.' + save)   
        
    min_x, max_x = min(errors), max(errors)
    h_errors = Hist(1000, min_x, max_x)
    fill_value = h_errors.Fill
    for error in errors:
        fill_value(error)  
        
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_errors.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_errors, xerr=True, emptybins=True, axes=axes)
    
    plt.xlabel('$\sigma(\mathrm{unfolded} - \mathrm{true})$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title('SVD unfolding performance', CMS.title)
    plt.tight_layout()  
    
    save_folder = 'plots/'
    save_as = ['png', 'pdf']
    for save in save_as:
        plt.savefig(save_folder + 'difference_errors_stats_' + str(stats) + '.' + save)  
        
if __name__ == "__main__":
    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    parser = OptionParser()
    parser.add_option("-i", "--input-folder", type='string',
                      dest="input_folder",
                      help="location of the pull data")
    parser.add_option("-c", "--channel", type='string',
                      dest="channel", default='both',
                      help="channel to be analysed: electron|muon|both")
    (options, args) = parser.parse_args()
    
    if not options.input_folder:
        sys.exit('No input folder specified')
        
    files = glob(options.input_folder + '/*_' + options.channel + '*_*.txt')
    
    pulls = get_data(files, subset='pull')
    plot_pull(pulls, bin_index = 0, n_bins = 5)
    plot_pull(pulls, bin_index = 1, n_bins = 5)
    plot_pull(pulls, bin_index = 2, n_bins = 5)
    plot_pull(pulls, bin_index = 3, n_bins = 5)
    plot_pull(pulls, bin_index = 4, n_bins = 5)
    plot_pull(pulls)
    del pulls #deleting to make space in memory
#    plot_pull_from_list()

    difference = get_data(files, subset='difference')
    plot_difference(difference)
