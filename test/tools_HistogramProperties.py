'''
Created on 8 Jan 2015

@author: kreczko
'''
from tools.plotting import Histogram_properties

def test_init_from_dictionary():
    test_values = {}
    test_values['x_limits'] = [0,300]
    test_values['y_limits'] = [0,0.09]
    test_values['ratio_y_limits'] = [0.8, 1.3]
    test_values['title'] = 'Comparison of W+Jets MC between $\\sqrt{s}$ = 7 and 8 TeV'
    test_values['x_axis_title'] = '$E_T^{\\text{miss}}$ [GeV]'
    test_values['y_axis_title'] = 'normalised to unit area'
    
    hp = Histogram_properties(test_values)
    
    assert hp.title == test_values['title']
    assert hp.x_limits == test_values['x_limits']
    assert hp.y_limits == test_values['y_limits']
    assert hp.ratio_y_limits == test_values['ratio_y_limits']
    assert hp.x_axis_title == test_values['x_axis_title']
    assert hp.y_axis_title == test_values['y_axis_title']
