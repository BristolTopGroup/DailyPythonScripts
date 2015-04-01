from iminuit import Minuit
from probfit import BinnedLH, gaussian, Extended
from matplotlib import pyplot as plt
from numpy.random import randn
from rootpy.plotting import Hist
from numpy import array
import numpy as np

data = randn(1000)*2 + 2
# print data
h1 = Hist( 40, -6, 10, title = 'data' )
map( h1.Fill, data )
# data = array( list( h1.y() ) )
# print data
#Unextended

# blh = BinnedLH(gaussian, data, bins = 40, bound = ( -6, 10 ))
# # #if you wonder what it loos like call desceibe(blh)
# m = Minuit(blh, mean=0., sigma=0.5)
#  
# plt.figure(figsize=(8, 6))
# plt.subplot(221)
# blh.draw(m)
# plt.title('Unextended Before')
#  
# m.migrad() # fit
#  
# plt.subplot(222)
# blh.draw(m)
# plt.title('Unextended After')
#  
# #Extended
#  
# ext_gauss = Extended(gaussian)
#  
# blh = BinnedLH(ext_gauss, data, extended=True, bins = 40, bound = ( -6, 10 ))
# m = Minuit(blh, mean=0., sigma=0.5, N=900.)
#  
# plt.subplot(223)
# blh.draw(m)
# plt.title('Extended Before')
#  
# m.migrad()
#  
# plt.subplot(224)
# blh.draw(m)
# plt.title('Extended After')
# plt.savefig('test.png')
