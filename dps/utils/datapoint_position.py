'''
Created on 12 Nov 2012

@author: kreczko
'''

from .hist_utilities import rebin_asymmetric

def get_bin_centers(bin_edges):
    centers = []
    add_center = centers.append
    for lowerEdge, upperEdge in zip(bin_edges[:-1], bin_edges[1:]):
        center = (upperEdge - lowerEdge)/2 + lowerEdge
        add_center(center)
    return centers

def barycenters(finedbinnedhist, coarsebinnedhist):
    distribution = list(finedbinnedhist.y())
    distribution_binEdges = list(finedbinnedhist.xedges())
    data_binEdges = list(coarsebinnedhist.xedges())
    centers = []
    old_centers = []
    for lowerEdge, upperEdge in zip(data_binEdges[:-1], data_binEdges[1:]):
        data_position = 0
        mass = 0
        for x,y in zip(distribution_binEdges[1:], distribution):
            if x < upperEdge and x>= lowerEdge:
                data_position += x*y
                mass +=y
        data_position /= mass
        centers.append(data_position)
        old_centers.append(object)
    return centers

def calculate_bin_centers(hist, bins):
    pass

def calculate_bin_widths(data_binEdges):
    widths = []
    add_width = widths.append
    for lowerEdge, upperEdge in zip(data_binEdges[:-1], data_binEdges[1:]):
        width = abs(upperEdge) - abs(lowerEdge)
        add_width(width)
    return widths

def calculate_correct_x_coordinates(mc_truth, bins):
    mc_temp = rebin_asymmetric(mc_truth, bins)
    widths = calculate_bin_widths(bins)
    
    x_positions = []
    add_position = x_positions.append
    
    for bin_i, width in enumerate(widths):
        y = mc_temp.GetBinContent(bin_i + 1)/width
        #find closest y-distance on MC hist and get the x-value
        x_low = bins[bin_i]# + 1)
        x_high = x_low + width
        x = find_x_of_closest_approach(mc_truth, x_low, x_high, y)
        add_position(x)
        
    return x_positions
        
def find_x_of_closest_approach(hist, x_low, x_high, y_search):
    y_values = list(hist.y())
    x_edges = list(hist.xedges())
    closest_x = 0
    closest_distance = 99999999
    centers = get_bin_centers(x_edges)
    for x,y, center in zip(x_edges, y_values, centers):
        if x < x_high and x>= x_low:
            distance = abs(y_search - y)
            if distance < closest_distance:
                closest_distance = distance
                closest_x = center
    return closest_x
