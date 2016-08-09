'''
Created on 31 Oct 2012

@author: kreczko
'''
availablemethods = [
                    'TUnfold'
                    ]

SVD_k_value = 5
SVD_tau_value = -1
SVD_n_toy = 1000
# 0 = no error treatment: returns sqrt(N)
# 1 = bin-by-bin errors (diagonal covariance matrix)
# 2 = covariance matrix from unfolding
# 3 = covariance matrix from toy MC
error_treatment = 3
Bayes_n_repeat = 4

unfolded_markerStyle = 20
unfolded_fillStyle = 0
unfolded_color = 'black'

truth_color = 'red'
truth_fillStyle = 0

measured_color = 'blue'
measured_fillStyle = 0
