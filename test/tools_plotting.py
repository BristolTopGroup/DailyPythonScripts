'''
Created on 5 May 2015

@author: kreczko
'''
from tools.plotting import get_best_max_y
from tools.hist_utilities import value_errors_tuplelist_to_graph
from tools.hist_utilities import value_error_tuplelist_to_hist

data_h =  [( 3, 1 ),
         ( 2, 1 ),
         ( 1, 1 ),
        ]
data_g =  [( 3, 1, 1 ),
         ( 2, 1, 1 ),
         ( 1, 1, 1 ),
        ]
bin_edges = [0, 1, 2, 3]

def test_get_max_y_hist():
    h = value_error_tuplelist_to_hist(data_h, bin_edges)
    max_y = get_best_max_y([h])
    assert max_y == 3 + 1
    
def test_get_max_y_graph():
    g = value_errors_tuplelist_to_graph(data_g, bin_edges)
    max_y = get_best_max_y([g])
    assert max_y == 3 + 1
