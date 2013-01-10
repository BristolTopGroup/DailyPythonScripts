'''
Created on 31 Oct 2012

@author: kreczko
'''

#library = '/software/RooUnfold-1.1.1/libRooUnfold.so'
#testing
library = '/storage/Workspace/Analysis/RooUnfold/libRooUnfold.so'

availablemethods = ['RooUnfoldTUnfold', 'RooUnfoldBayes',
                        'RooUnfoldSvd','RooUnfoldBinByBin',
                        'RooUnfoldInvert', 'RooUnfoldTUnfold']
SVD_k_value = 5
SVD_n_toy = 1000
Bayes_n_repeat = 4

unfolded_markerStyle = 20
unfolded_fillStyle = 0
unfolded_color = 'black'

truth_color = 'red'
truth_fillStyle = 0

measured_color = 'blue'
measured_fillStyle = 0
