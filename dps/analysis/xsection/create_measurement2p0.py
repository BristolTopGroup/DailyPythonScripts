'''
    Translates the current config (for a given centre-of-mass energy)
    into JSON configs. The configs will be written to 
    config/measurements/background_subtraction/<centre of mass energy>TeV/
    
    Usage:
        python src/cross_section_measurement/create_measurement.py -c <centre of mass energy>
        
    Example:
        python src/cross_section_measurement/create_measurement.py -c 
'''
from argparse import ArgumentParser
from dps.config.xsection import XSectionConfig
from dps.config import variable_binning
from dps.utils.logger import log
from copy import deepcopy
from dps.utils.file_utilities import write_data_to_JSON
import pprint
pp = pprint.PrettyPrinter(indent=4)

# define logger for this module
create_measurement_log = log["01b_get_ttjet_normalisation"]
cml = create_measurement_log  # alias

@cml.trace()
def main():
    parser = ArgumentParser(__doc__)
    parser.add_argument(
    	"-c", 
    	"--centre-of-mass-energy", 
    	dest="CoM", 
    	default=13, 
    	type=int,
        help="set the centre of mass energy for analysis. Default = 13 [TeV]"
    )
    parser.add_argument(
    	'-d', 
    	'--debug', 
    	dest="debug", 
    	action="store_true",
        help="Print the debug information"
    )
    parser.add_argument(
        '-q', 
        '--qcd_from_data', 
        dest="data_driven_qcd", 
        default=True, 
        help="Print the debug information"
    )
    args = parser.parse_args()

    options = {}
    options['com'] = args.CoM
    options['data_driven_qcd'] = args.data_driven_qcd
    if args.debug: log.setLevel(log.DEBUG)


    xsec_config = XSectionConfig(options['com'])
    categories = xsec_config.normalisation_systematics
    print categories

    # Create specific configs required
    for ps in ['VisiblePS', 'FullPS']:
        options['ps']=ps
        for channel in ['electron', 'muon']:
            options['channel']=channel
            for variable in xsec_config.variables:
                options['variable']=variable
                for category in categories:
                    if channel == 'electron' and (category == 'Muon_down' or category == 'Muon_up'):
                        continue
                    elif channel == 'muon' and (category == 'Electron_down' or category == 'Electron_up'):
                        continue
                    elif variable in xsec_config.variables_no_met and category in xsec_config.met_specific_systematics: 
                        continue
                    options['category']=category

                    m = create_measurement(
                        options,
                        norm_method='background_subtraction',
                    )

                    write_measurement(
                        options,
                        m,
                        norm_method='background_subtraction',
                    )


def create_measurement(options, norm_method):
    '''
    Create the config file
    '''
    # Create dictionary to write to config file
    measurement = {}
    xsec_config = XSectionConfig(options['com'])

    # Generate basic normalisation config info
    measurement["com"]              =   options['com']
    measurement["channel"]          =   options['channel']
    measurement["variable"]         =   options['variable']
    measurement["name"]             =   options['category']
    measurement["data_driven_qcd"]  =   options['data_driven_qcd']

    # Add specific samples to config
    measurement["samples"]          =   get_samples(options, xsec_config)
    return measurement


def get_samples(options, xsec_config):
    '''
    Return the dictionary of all sample information
    '''
    # create samples dictionary
    samples = {}
    for s in xsec_config.samples:
        samples[s] = get_sample_info(options, xsec_config, s)

    return samples

def get_sample_info(options, xsec_config, sample):
    '''
    Generate each measurements information
    '''
    # create sample info
    sample_info = {}

    # Branch (variable) 
    sample_info["branch"] = options['variable']
    # MET Systematics
    # Only Met Variables
    if options['variable'] not in xsec_config.variables_no_met:
        # Only MET Syst measurement
        if options['category'] in xsec_config.met_specific_systematics:
            sample_info["branch"] += '_METUncertainties[{index}]'.format(index = str(xsec_config.met_systematics[options['category']]))

    # Bin Edges
    if options['ps'] == 'VisiblePS':
        sample_info["bin_edges"] = variable_binning.reco_bin_edges_vis[options['variable']]
    elif options['ps'] == 'FullPS':
        sample_info["bin_edges"] = variable_binning.reco_bin_edges_full[options['variable']]
    else:
        sample_info["bin_edges"] = None

    # Lumi Scale (Rate)
    sample_info["lumi_scale"]=1.0
    lumi_scale = xsec_config.rate_changing_systematics['luminosity']
    if options['category'] == 'luminosity+':
        sample_info["lumi_scale"]= 1.0 + 1.0*lumi_scale
    elif options['category'] == 'luminosity-':
        sample_info["lumi_scale"]= 1.0 - 1.0*lumi_scale

    # Generator Scale (Rate)
    sample_info["scale"]=1.0
    generator_scale = xsec_config.rate_changing_systematics['V+Jets_cross_section']
    if options['category'] == 'V+Jets_cross_section+':
        sample_info["scale"] = 1.0 + 1.0*generator_scale
    elif options['category'] == 'V+Jets_cross_section-':
        sample_info["scale"] = 1.0 - 1.0*generator_scale
    generator_scale = xsec_config.rate_changing_systematics['SingleTop_cross_section']
    if options['category'] == 'SingleTop_cross_section+':
        sample_info["scale"] = 1.0 + 1.0*generator_scale
    elif options['category'] == 'SingleTop_cross_section-':
        sample_info["scale"] = 1.0 - 1.0*generator_scale
    generator_scale = xsec_config.rate_changing_systematics['QCD_cross_section']
    if options['category'] == 'QCD_cross_section+':
        sample_info["scale"] = 1.0 + 1.0*generator_scale
    elif options['category'] == 'QCD_cross_section-':
        sample_info["scale"] = 1.0 - 1.0*generator_scale
    # scaling will always have some non zero value
    if sample_info["scale"] <= 0.0001: sample_info["scale"] = 0.0001

    # Weight branches (Shape)
    weight_branches = []
    if sample == 'data':
        weight_branches.append('1')
    else:
        weight_branches.append('EventWeight')

        # PU Weights
        if options['category'] == 'PileUp_up':
            weight_branches.append('PUWeight_up')
        elif  options['category'] == 'PileUp_down':
            weight_branches.append('PUWeight_down')
        else:
            weight_branches.append('PUWeight')

        # BJet Weights 
        if options['category'] == 'BJet_up':
            weight_branches.append('BJetUpWeight')
        elif  options['category'] == 'BJet_down':
            weight_branches.append('BJetDownWeight')
        elif options['category'] == 'LightJet_up':
            weight_branches.append('LightJetUpWeight')
        elif  options['category'] == 'LightJet_down':
            weight_branches.append('LightJetDownWeight')
        else:
            weight_branches.append('BJetWeight')

        # Lepton Weights
        # Lepton weights for nonisolated leptons are removed in measurement.py
        # The lepton sf are not derived for non isolated leptons
        if options['channel'] == 'muon':
            if options['category'] == 'Muon_down':
                weight_branches.append('MuonDown')
            elif options['category'] == 'Muon_up':
                weight_branches.append('MuonUp')
            else:
                weight_branches.append('MuonEfficiencyCorrection')
        elif options['channel'] == 'electron':
            if options['category'] == 'Electron_down':
                weight_branches.append('ElectronDown')
            elif options['category'] == 'Electron_up':
                weight_branches.append('ElectronUp')
            else:
                weight_branches.append('ElectronEfficiencyCorrection')
    sample_info["weight_branches"] = weight_branches

    # Input File
    sample_info["input_file"] = get_file(xsec_config, sample, options)
    if sample != 'data':
        if options['category'] == 'JES_up':
            sample_info["input_file"] = sample_info["input_file"].replace('tree', 'plusJES_tree')
        elif options['category'] == 'JES_down':
            sample_info["input_file"] = sample_info["input_file"].replace('tree', 'minusJES_tree')
        elif options['category'] == 'JER_up':
            sample_info["input_file"] = sample_info["input_file"].replace('tree', 'plusJER_tree')
        elif options['category'] == 'JER_down':
            sample_info["input_file"] = sample_info["input_file"].replace('tree', 'minusJER_tree')

    # Input Trees
    # QCD Shape and QCD Control Regions
    sample_info["tree"], sample_info["qcd_control_region"] = get_tree(xsec_config, options)
    
    return sample_info



@cml.trace()
def get_file(config, sample, options):
    '''
    Return a specific sample file
    '''
    if options['channel'] == 'electron':
        qcd = config.electron_QCD_MC_trees[options['category']]
        data = config.data_file_electron
    else:
        qcd = config.muon_QCD_MC_trees[options['category']]
        data = config.data_file_muon

    files = {
        'TTBar': config.ttbar_trees[options['category']],
        'V+Jets': config.VJets_trees[options['category']],
        'SingleTop': config.SingleTop_trees[options['category']],
        'QCD': qcd,
        'data': data
    }
    return files[sample]

@cml.trace()
def get_tree(config, options):
    '''
    Return a specific sample tree
    '''
    tree = config.tree_path[options['channel']]
    if options["data_driven_qcd"]:
        # QCD control region
        qcd_tree = tree.replace(
            "Ref selection", config.qcd_control_region[options['channel']])
        # QCD shape systematic
        if "QCD_shape" in options['category']:
            qcd_tree = tree.replace(
                "Ref selection", config.qcd_shape_syst_region[options['channel']])
    else:
        qcd_tree = None
    return tree, qcd_tree



def write_measurement(options, measurement, norm_method):
    '''
    Write the config
    '''
    base_path = 'TESTING/config/measurements/{norm_method}/{energy}TeV/{channel}/{variable}/{phase_space}/'
    path = base_path + '{category}.json'
    # pp.pprint(measurement)

    path = path.format(
        norm_method = norm_method,
        energy = options['com'],
        channel = options['channel'],
        variable = options['variable'],
        phase_space = options['ps'],
        category = options['category'],
    )
    write_data_to_JSON(measurement, path, indent = True)
    return

if __name__ == '__main__':
    main()
