'''
Created on 29 Oct 2012

@author: kreczko
'''
import matplotlib.pyplot as plt

plt.errorbar( [0, 1, 2], [2, 3, 1], xerr = None, fmt = "s", label = "test 1" )
plt.errorbar( [0, 1, 2], [3, 2, 4], yerr = 0.3, fmt = "o", label = "test 2" )
plt.errorbar( [0, 1, 2], [1, 1, 3], xerr = 0.4, yerr = 0.3, fmt = "^", label = "test 3" )

plt.legend(numpoints=1)
plt.savefig('examples/plots/LegendManipulation.png')
print 'Done'
