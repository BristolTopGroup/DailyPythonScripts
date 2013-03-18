'''
Created on 29 Oct 2012

@author: kreczko
'''
from ROOT import TH1F
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt

#updated from http://rootpy.org/qa/questions/80/how-to-create-a-histogram-with-asymmetric-bins
bins = [0, 25, 45, 70, 100, 2000]
nbins = len(bins) - 1

rootpyhist = Hist(bins)
for bin_i in range(nbins):
    rootpyhist.SetBinContent(bin_i + 1, bin_i+1)
    rootpyhist.SetBinError(bin_i +1, (bin_i + 1)*0.1)

plt.figure(figsize=(16, 10), dpi=100)
plt.figure(1)
rplt.errorbar(rootpyhist, label='test')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Testing')
plt.legend(numpoints=1)
plt.axis([bins[0], bins[-1], 0, nbins*1.2])
plt.savefig('plots/AsymBinsExample.png')
print 'Done'