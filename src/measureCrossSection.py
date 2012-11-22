from __future__ import division
from tools.Calculation import calculate_xsection, calculate_normalised_xsection


if __name__ == '__main__':
    #get data
    #get fit values
    #get fit values for systematics
    #unfold all above
    #calculate the x-sections and
    inputs = [(2146,145), (3399,254), (3723,69), (2256, 53), (1722, 91)]
    bin_widths = [25,20,25,30,150]
    xsection = calculate_xsection(inputs, 5050) #L in pb1
    normalisedToOne_xsection = calculate_normalised_xsection(inputs, bin_widths, normalise_to_one = True)
    normalised_xsection = calculate_normalised_xsection(inputs, bin_widths, normalise_to_one = False)
    print xsection
    print normalised_xsection
    print normalisedToOne_xsection
    normalisation = 0
    
    for value in normalised_xsection:
        print value
        