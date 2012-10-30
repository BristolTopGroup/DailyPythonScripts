'''
Created on 29 Oct 2012

@author: kreczko
'''
from ROOT import TH1F
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from rootpy.utils import asrootpy
from array import array

#currently only via ROOT histograms
arglist = array('d', [0, 25, 45, 70, 100, 2000])
nbins = len(arglist) - 1
roothist = TH1F('test', 'Title; x-title;y-title', nbins, arglist)

for bin_i in range(nbins):
    roothist.SetBinContent(bin_i + 1, (bin_i*20 + 25)/arglist[bin_i + 1])
    roothist.SetBinError(bin_i +1, (bin_i*20 + 25)*0.1/arglist[bin_i + 1])

#make it a rootpy histogram
rootpyhist = asrootpy(roothist)

plt.figure(figsize=(16, 10), dpi=100)
plt.figure(1)
rplt.errorbar(rootpyhist, label='test')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Testing')
plt.legend()
plt.savefig('plots/AsymBinsExample.png')
print 'Done'