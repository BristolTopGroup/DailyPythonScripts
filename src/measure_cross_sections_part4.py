'''
Created on 9 Dec 2012

@author: kreczko

Episode 4 - Calculation of (differential) cross section:
- Read JSON files
- calculate the cross sections (with systematics)
- write JSON files
'''
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from config import cross_section_measurement as csm
from tools.Calculation import calculate_xsection, calculate_normalised_xsection


def get_cross_sections(normalisation_unfolded, luminosity, branching_ratio):
    result = {}
    for sample in normalisation_unfolded.keys():
        result[sample] = calculate_xsection(normalisation_unfolded[sample], luminosity, branching_ratio)
    return result

def get_normalised_xsection(normalisation_unfolded, normalise_to_one):
    bin_widths = [25, 20, 25, 30, 150]
    result = {}
    for sample in normalisation_unfolded.keys():
        result[sample] = calculate_normalised_xsection(normalisation_unfolded[sample], bin_widths, normalise_to_one)
    return result

if __name__ == '__main__':
    luminosity = 5050  # L in pb1
    branching_ratio = 0.15  # to be corrected for
    normalisation_electron_unfolded = read_data_from_JSON(csm.normalisation_electron_unfolded_file)
    normalisation_muon_unfolded = read_data_from_JSON(csm.normalisation_muon_unfolded_file)
    normalisation_combined_unfolded = read_data_from_JSON(csm.normalisation_combined_unfolded_file)
    
    xsection_electron_unfolded = get_cross_sections(normalisation_electron_unfolded, luminosity, branching_ratio)
    xsection_muon_unfolded = get_cross_sections(normalisation_muon_unfolded, luminosity, branching_ratio)
    xsection_combined_unfolded = get_cross_sections(normalisation_combined_unfolded, luminosity, branching_ratio*2)
    
    normalised_to_one_xsection_electron = get_normalised_xsection(normalisation_electron_unfolded, True)
    normalised_to_one_xsection_muon = get_normalised_xsection(normalisation_muon_unfolded, True)
    normalised_to_one_xsection_combined = get_normalised_xsection(normalisation_combined_unfolded, True)
    
    normalised_xsection_electron = get_normalised_xsection(normalisation_electron_unfolded, False)
    normalised_xsection_muon = get_normalised_xsection(normalisation_muon_unfolded, False)
    normalised_xsection_combined = get_normalised_xsection(normalisation_combined_unfolded, False)
    
    #write results
    write_data_to_JSON(xsection_electron_unfolded, csm.xsection_electron_unfolded_file)
    write_data_to_JSON(xsection_muon_unfolded, csm.xsection_muon_unfolded_file)
    write_data_to_JSON(xsection_combined_unfolded, csm.xsection_combined_unfolded_file)
    
    write_data_to_JSON(normalised_to_one_xsection_electron, csm.normalised_to_one_xsection_electron_unfolded_file)
    write_data_to_JSON(normalised_to_one_xsection_muon, csm.normalised_to_one_xsection_muon_unfolded_file)
    write_data_to_JSON(normalised_to_one_xsection_combined, csm.normalised_to_one_xsection_combined_unfolded_file)
    
    write_data_to_JSON(normalised_xsection_electron, csm.normalised_xsection_electron_unfolded_file)
    write_data_to_JSON(normalised_xsection_muon, csm.normalised_xsection_muon_unfolded_file)
    write_data_to_JSON(normalised_xsection_combined, csm.normalised_xsection_combined_unfolded_file)
