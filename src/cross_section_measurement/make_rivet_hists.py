'''
    Script to create ROOT files for the Rivet implementation of our analysis.
    All measurement scripts up to 03_caculate_systematics must have been run.
    This script will create a file named 
    'measurement_<centre-of-mass energy>TeV.root'
    
    Usage:
        python src/cross_section_measurement/make_rivet_hists.py \
        -c <centre-of-mass energy> <path template>
        
    Example:
        python src/cross_section_measurement/make_rivet_hists.py \
        -c 7 \
        data/absolute_eta_M3_angle_bl/{centre_of_mass_energy}TeV/{variable}/xsection_measurement_results/{channel}/central/
'''
from optparse import OptionParser
from config import XSectionConfig
from config.variable_binning import bin_edges_full
from tools.file_utilities import read_data_from_JSON
from rootpy.io import File
from tools.hist_utilities import value_error_tuplelist_to_hist,\
    value_errors_tuplelist_to_graph


def main(options, args):
    config = XSectionConfig(options.CoM)
    variables = ['MET', 'HT', 'ST', 'WPT']
    channels = ['electron', 'muon', 'combined']
    m_file = 'normalised_xsection_patType1CorrectedPFMet.txt'
    m_with_errors_file = 'normalised_xsection_patType1CorrectedPFMet_with_errors.txt'
    path_template = args[0]
    output_file = 'measurement_{0}TeV.root'.format(options.CoM)
    f = File(output_file, 'recreate')
    for channel in channels:
        d = f.mkdir(channel)
        d.cd()
        for variable in variables:
            dv = d.mkdir(variable)
            dv.cd()
            if channel == 'combined':
                path = path_template.format(variable=variable,
                                            channel=channel,
                                            centre_of_mass_energy=options.CoM)
            else:
                kv = channel + \
                    '/kv{0}/'.format(config.k_values[channel][variable])
                path = path_template.format(variable=variable,
                                            channel=kv,
                                            centre_of_mass_energy=options.CoM)

            m = read_data_from_JSON(path + '/' + m_file)
            m_with_errors = read_data_from_JSON(
                path + '/' + m_with_errors_file)

            for name, result in m.items():
                h = make_histogram(result, bin_edges_full[variable])
                h.SetName(name)
                h.write()

            for name, result in m_with_errors.items():
                if not 'TTJet' in name:
                    continue
                h = make_histogram(result, bin_edges_full[variable])
                h.SetName(name + '_with_syst')
                h.write()
            dv.write()
            d.cd()
        d.write()
    f.write()
    f.close()


def make_histogram(result, bin_edges):
    if len(result[0]) == 2:
        h = value_error_tuplelist_to_hist(result, bin_edges)
        return h
    else:  # len(result[0]) == 3
        g = value_errors_tuplelist_to_graph(result, bin_edges)
        return g

if __name__ == '__main__':
    parser = OptionParser(__doc__)
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    (options, args) = parser.parse_args()
    main(options, args)
