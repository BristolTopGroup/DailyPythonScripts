'''
Created on 5 May 2015

@author: kreczko
'''
from tools.plotting import get_best_max_y
from tools.hist_utilities import value_errors_tuplelist_to_graph
from tools.hist_utilities import value_error_tuplelist_to_hist

data_h1 =  [( 3, 1 ),
         ( 2, 1 ),
         ( 1, 1 ),
        ]
data_h2 =  [( 10, 3 ),
         ( 3, 1 ),
         ( 5, 2 ),
        ]
data_g1 =  [( 3, 1, 1 ),
         ( 2, 1, 1 ),
         ( 1, 1, 1 ),
        ]
bin_edges = [0, 1, 2, 3]

h1 = value_error_tuplelist_to_hist(data_h1, bin_edges)
h2 = value_error_tuplelist_to_hist(data_h2, bin_edges)
g1 = value_errors_tuplelist_to_graph(data_g1, bin_edges)

def test_get_max_y_hist():
    max_y = get_best_max_y([h1])
    assert max_y == 3 + 1
    
def test_get_max_y_graph():
    max_y = get_best_max_y([g1])
    assert max_y == 3 + 1
