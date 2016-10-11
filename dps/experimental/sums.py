'''
Created on 23 Jan 2015

@author: phxlk
'''
from dps.utils.file_utilities import read_data_from_JSON

if __name__ == '__main__':
    JSON_input_file = 'data/absolute_eta_M3_angle_bl/7TeV/HT/fit_results/central/fit_results_muon_patType1CorrectedPFMet.txt'
    normalisation = read_data_from_JSON(JSON_input_file)
    absolute_total_value = 0
    absolute_total_error = 0
    absolute_total_corrected_error = 0
    for sample, fit_result in normalisation.iteritems():
        print 'Calculating total # events for sample "%s"' % sample
        total_events = 0
        total_error = 0
        total_corrected_error = 0
        # loop over binsZ
        for result in fit_result:
            value = result[0]
            error = result[1]
            total_events += value
            total_error += error
        if total_error > total_events:
            total_corrected_error = total_events
        else:
            total_corrected_error = total_error
        print 'Total number of events %d += %d (%d)' %(total_events, total_corrected_error, total_error)
        absolute_total_value += total_events
        absolute_total_error += total_error
        absolute_total_corrected_error += total_corrected_error
    print '=========================================================================='
    print 'Total number of events %d += %d (%d)' %(absolute_total_value, absolute_total_corrected_error, absolute_total_error)
        