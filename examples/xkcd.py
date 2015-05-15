import matplotlib.pyplot as plt
import numpy as np
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
from config import CMS

with plt.xkcd():
    # Based on "Stove Ownership" from XKCD by Randall Monroe
    # http://xkcd.com/418/

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.xticks([])
    plt.yticks([])
    ax.set_ylim([-30, 10])

    data = np.ones(100)
    data[70:] -= np.arange(30)

    plt.annotate(
        'THE DAY I REALIZED\nI COULD COOK BACON\nWHENEVER I WANTED',
        xy=(70, 1), arrowprops=dict(arrowstyle='->'), xytext=(15, -10))

    plt.plot(data)

    plt.xlabel('time')
    plt.ylabel('my overall health')
    fig.text(
        0.5, 0.05,
        '"Stove Ownership" from xkcd by Randall Monroe',
        ha='center')

    # Based on "The Data So Far" from XKCD by Randall Monroe
    # http://xkcd.com/373/

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.bar([-0.125, 1.0-0.125], [0, 100], 0.25)
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([0, 1])
    ax.set_xlim([-0.5, 1.5])
    ax.set_ylim([0, 110])
    ax.set_xticklabels(['CONFIRMED BY\nEXPERIMENT', 'REFUTED BY\nEXPERIMENT'])
    plt.yticks([])

    plt.title("CLAIMS OF SUPERNATURAL POWERS")

    fig.text(
        0.5, 0.05,
        '"The Data So Far" from xkcd by Randall Monroe',
        ha='center')

plt.savefig('examples/plots/xkcd.png')

with plt.xkcd():
    
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
plt.savefig('examples/plots/xkcd2.png')