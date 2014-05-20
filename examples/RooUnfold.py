#!/usr/bin/env python
# ==============================================================================
#  File and Version Information:
#       $Id: RooUnfoldExample.py 302 2011-09-30 20:39:20Z T.J.Adye $
#
#  Description:
#       Simple example usage of the RooUnfold package using toy MC.
#
#  Author: Tim Adye <T.J.Adye@rl.ac.uk>
#
# ==============================================================================

from ROOT import gRandom, cout, gSystem
gSystem.Load('/software/RooUnfold-1.1.1/libRooUnfold.so')
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldBayes
from ROOT import RooUnfoldSvd
from ROOT import RooUnfoldTUnfold
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from rootpy import asrootpy


# ==============================================================================
#  Gaussian smearing, systematic translation, and variable inefficiency
# ==============================================================================

def smear(xt):
    xeff= 0.3 + (1.0-0.3)/20*(xt+10.0);  #  efficiency
    x= gRandom.Rndm();
    if x>xeff: 
        return None
    xsmear= gRandom.Gaus(-2.5,0.2);     #  bias and smear
    return xt+xsmear;

# ==============================================================================
#  Example Unfolding
# ==============================================================================

print "==================================== TRAIN ===================================="
response= RooUnfoldResponse (40, -10.0, 10.0);

#  Train with a Breit-Wigner, mean 0.3 and width 2.5.
for i in xrange(100000):
    xt= gRandom.BreitWigner (0.3, 2.5);
    x= smear (xt);
    if x!=None:
        response.Fill (x, xt);
    else:
        response.Miss (xt);

print "==================================== TEST ====================================="
hTrue= Hist(40, -10.0, 10.0);
hMeas= Hist(40, -10.0, 10.0);
hTrue.SetLineColor('red')
hMeas.SetLineColor('blue')
#  Test with a Gaussian, mean 0 and width 2.
for i in xrange(10000):
    xt= gRandom.Gaus (0.0, 2.0)
    x= smear (xt);
    hTrue.Fill(xt);
    if x!=None: hMeas.Fill(x);

print "==================================== UNFOLD ==================================="
unfold= RooUnfoldBayes     (response, hMeas, 4);    #  OR
# unfold= RooUnfoldSvd     (response, hMeas, 20);   #  OR
# unfold= RooUnfoldTUnfold (response, hMeas);

hReco= unfold.Hreco();
h_unfolded = asrootpy(hReco)
unfold.PrintTable (cout, hTrue);

plt.figure(figsize=(16, 12), dpi=100)
rplt.hist(hTrue, label='truth', stacked=False)
rplt.hist(hMeas, label='measured', stacked=False)
rplt.errorbar(h_unfolded, label='unfolded')
plt.xlabel('var')
plt.ylabel('Events')
plt.title('Unfolding')
plt.legend()
plt.savefig('plots/RooUnfoldBayesExample.png')
print 'Done'
