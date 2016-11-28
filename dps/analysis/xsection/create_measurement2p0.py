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
    # Scale and Mass????
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


# 'ElectronEnUp', 'ElectronEnDown', 'MuonEnUp', 'MuonEnDown', 'TauEnUp', 'TauEnDown', 'UnclusteredEnUp', 'UnclusteredEnDown', 
# if category in config.met_systematics_suffixes and not variable in config.variables_no_met:
#     branch = template.split('/')[-1]
#     branch += '_METUncertainties[%s]' % config.met_systematics[
#         category]
# if 'JES_down' in category or 'JES_up' in category or 'JER_down' in category or 'JER_up' in category:
#     tree += config.categories_and_prefixes[category]

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
    base_path = 'TESTING/config/measurements/{norm_method}/{energy}TeV/{variable}/{phase_space}/'
    path = base_path + '{category}.json'
    pp.pprint(measurement)

    path = path.format(
        norm_method = norm_method,
        energy = options['com'],
        variable = options['variable'],
        phase_space = options['ps'],
        category = options['category'],
    )
    write_data_to_JSON(measurement, path, indent = True)
    return

# @cml.trace()
# def create_measurement(com, category, variable, channel, phase_space, norm_method):
#     if com == 13:
#         # exclude non existing systematics
#         if 'VJets' in category and 'scale' in category:
#             print('Excluding {0} for now'.format(category))
#             return
#     config = XSectionConfig(com)
#     met_type = get_met_type(category, config)
#     should_not_run_systematic = category in config.met_systematics_suffixes and variable in config.variables_no_met and not 'JES' in category and not 'JER' in category
#     if should_not_run_systematic:
#         # no MET uncertainty on HT (but JES and JER of course)
#         return

#     m = None
#     if category == 'central':
#         m = Measurement(category)
#     else:
#         vjet_systematics = [config.vjets_theory_systematic_prefix +
#                             systematic for systematic in config.generator_systematics]
#         if category in config.categories_and_prefixes.keys() or \
#                 category in config.met_systematics_suffixes or \
#                 category in vjet_systematics:
#             m = Systematic(category,
#                            stype=Systematic.SHAPE,
#                            affected_samples=config.samples)
#         elif category in config.rate_changing_systematics_names:
#             m = config.rate_changing_systematics_values[category]

#         elif category == 'QCD_shape':
#             m = Systematic(category,
#                            stype=Systematic.SHAPE,
#                            affected_samples=['QCD'],
#             )

#     m.setVariable(variable)
#     m.setCentreOfMassEnergy(com)
#     m.setChannel(channel)
#     m.setMETType(met_type)

#     inputs = {
#         'channel': config.analysis_types[channel],
#         'met_type': met_type,
#         'selection': 'Ref selection',
#         'btag': config.translate_options['2m'],  # 2 or more
#         'energy': com,
#         'variable': variable,
#         'category': category,
#         'phase_space': phase_space,
#         'norm_method': norm_method,
#         'lepton': channel.title(),
#     }
#     variable_template = config.variable_path_templates[
#         variable].format(**inputs)

#     template_category = category
#     if category == 'QCD_shape' or category in config.rate_changing_systematics_names:
#         template_category = 'central'
#     if category in [config.vjets_theory_systematic_prefix + systematic for systematic in config.generator_systematics]:
#         template_category = 'central'

#     m.addSample(
#         'TTJet',
#         False,
#         input=create_input(
#             config, 'TTJet', variable, template_category, channel,
#             variable_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     m.addSample(
#         'V+Jets',
#         False,
#         input=create_input(
#             config, 'V+Jets', variable, template_category, channel,
#             variable_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     m.addSample(
#         'SingleTop',
#         False,
#         input=create_input(
#             config, 'SingleTop', variable, template_category, channel,
#             variable_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     m.addSample(
#         'QCD',
#         False,
#         input=create_input(
#             config, 'QCD', variable, template_category, channel,
#             variable_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     variable_template_data = variable_template.replace(
#         met_type, config.translate_options['type1'])

#     m.addSample(
#         'data',
#         False,
#         input=create_input(
#             config, 'data', variable, template_category, channel,
#             variable_template_data, phase_space=phase_space, measurement=m,
#         ),
#     )

#     m_qcd = Measurement(category)
#     m_qcd.setVariable(variable)
#     m_qcd.setCentreOfMassEnergy(com)

#     qcd_template = get_qcd_template(config, variable, category, channel)

#     # we want "measurement = m" here since all rate systematics should apply
#     # to the control regions as well
#     m_qcd.addSample(
#         'TTJet',
#         False,
#         input=create_input(
#             config, 'TTJet', variable, template_category, channel,
#             qcd_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     m_qcd.addSample(
#         'V+Jets',
#         False,
#         input=create_input(
#             config, 'V+Jets', variable, template_category, channel,
#             qcd_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     m_qcd.addSample(
#         'SingleTop',
#         False,
#         input=create_input(
#             config, 'SingleTop', variable, template_category, channel,
#             qcd_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     m_qcd.addSample(
#         'QCD',
#         False,
#         input=create_input(
#             config, 'QCD', variable, template_category, channel,
#             qcd_template, phase_space=phase_space, measurement=m,
#         ),
#     )
#     m_qcd.addSample(
#         'data',
#         False,
#         input=create_input(
#             config, 'data', variable, template_category, channel,
#             qcd_template, phase_space=phase_space, measurement=m,
#         ),
#     )

#     m.addShapeForSample('QCD', m_qcd, False)
#     norm_qcd = deepcopy(m_qcd)
#     # we want QCD shape and normalisation to be separate
#     if category == 'QCD_shape':
#         for sample in norm_qcd.samples.keys():
#             tree = norm_qcd.samples[sample]['input'].tree_name
#             if channel == 'electron':
#                 tree = tree.replace(config.electron_control_region_systematic,
#                                     config.electron_control_region)
#             else:
#                 tree = tree.replace(config.muon_control_region_systematic,
#                                     config.muon_control_region)
#             norm_qcd.samples[sample]['input'].tree_name = tree
#     if 'QCD_cross_section' in category:
#         for sample in norm_qcd.samples.keys():
#             tree = norm_qcd.samples[sample]['input'].tree_name
#             if channel == 'electron':
#                 tree = tree.replace(config.electron_control_region,
#                                     config.electron_control_region_systematic)
#             else:
#                 tree = tree.replace(config.muon_control_region,
#                                     config.muon_control_region_systematic)
#             norm_qcd.samples[sample]['input'].tree_name = tree

#     m.addNormForSample('QCD', norm_qcd, False)

#     if category in [config.vjets_theory_systematic_prefix + systematic for systematic in config.generator_systematics]:
#         v_template_category = category.replace(
#             config.vjets_theory_systematic_prefix, '')
#         m_vjets = Measurement(category)
#         m_vjets.setVariable(variable)
#         m_vjets.setCentreOfMassEnergy(com)
#         m_vjets.addSample(
#             'V+Jets',
#             False,
#             input=create_input(
#                 config, 'V+Jets', variable, v_template_category,
#                 channel,
#                 variable_template,
#                 config.generator_systematic_vjets_templates[
#                     v_template_category]),
#             phase_space=phase_space, measurement=m,
#         )
#         m.addShapeForSample('V+Jets', m_vjets, False)

#     inputs['channel'] = channel
#     base_path = 'config/measurements/{norm_method}/{energy}TeV/'
#     base_path += '{channel}/{variable}/{phase_space}/'
#     if category == 'central':
#         path = base_path + '{category}.json'
#         m.toJSON(path.format(**inputs))
#     else:
#         if m.type == Systematic.SHAPE:
#             inputs['type'] = 'shape_systematic'
#         else:
#             inputs['type'] = 'rate_systematic'
#         if category in config.met_systematics_suffixes and category not in ['JES_up', 'JES_down', 'JER_up', 'JER_down']:
#             inputs['category'] = met_type
#         path = base_path + '{category}_{type}.json'
#         m.toJSON(path.format(**inputs))


# @cml.trace()
# def get_met_type(category, config):
#     met_type = config.translate_options['type1']
#     if category == 'JES_up':
#         met_type += 'JetEnUp'
#     elif category == 'JES_down':
#         met_type += 'JetEnDown'
#     elif category == 'JER_up':
#         met_type += 'JetResUp'
#     elif category == 'JER_down':
#         met_type += 'JetResDown'

#     isJetSystematic = 'JetEn' in category or 'JetRes' in category
#     isJetSystematic = isJetSystematic or 'JES' in category
#     isJetSystematic = isJetSystematic or 'JER' in category

#     if category in config.met_systematics_suffixes:
#         # already done them
#         if not isJetSystematic:
#             met_type = met_type + category

#     return met_type


# @cml.trace()
# def get_file(config, sample, category, channel):
#     use_trees = True if config.centre_of_mass_energy == 13 else False
#     if channel == 'electron':
#         qcd_template = config.electron_QCD_MC_category_templates[category]
#         data_template = config.data_file_electron
#         qcd_template_tree = config.electron_QCD_MC_category_templates_trees[
#             category]
#         data_template_tree = config.data_file_electron_trees
#     else:
#         qcd_template = config.muon_QCD_MC_category_templates[category]
#         data_template = config.data_file_muon
#         qcd_template_tree = config.muon_QCD_MC_category_templates_trees[
#             category]
#         data_template_tree = config.data_file_muon_trees

#     tree_files = {
#         'TTJet': config.ttbar_category_templates_trees[category],
#         'V+Jets': config.VJets_category_templates_trees[category],
#         'SingleTop': config.SingleTop_category_templates_trees[category],
#         'QCD': qcd_template_tree,
#         'data': data_template_tree
#     }
#     files = {
#         'TTJet': config.ttbar_category_templates[category],
#         'V+Jets': config.VJets_category_templates[category],
#         'SingleTop': config.SingleTop_category_templates[category],
#         'QCD': qcd_template,
#         'data': data_template,
#     }

#     if use_trees:
#         return tree_files[sample]
#     else:
#         return files[sample]


# @cml.trace()
# def get_qcd_template(config, variable, category, channel):
#     qcd_inputs = {
#         'channel': config.analysis_types[channel],
#         'met_type': config.translate_options['type1'],  # always central MET
#         'selection': 'Ref selection',
#         'btag': config.translate_options['2m'],  # 2 or more
#         'energy': config.centre_of_mass_energy,
#         'variable': variable,
#         'category': 'central',  # always central
#         'lepton': channel.title(),
#     }

#     qcd_template = config.variable_path_templates[
#         variable].format(**qcd_inputs)
#     if channel == 'electron':
#         qcd_template = qcd_template.replace(
#             'Ref selection', config.electron_control_region)
#         if category == 'QCD_shape':
#             qcd_template = qcd_template.replace(
#                 config.electron_control_region,
#                 config.electron_control_region_systematic)
#     else:
#         qcd_template = qcd_template.replace(
#             'Ref selection', config.muon_control_region)
#         if category == 'QCD_shape':
#             qcd_template = qcd_template.replace(
#                 config.muon_control_region,
#                 config.muon_control_region_systematic)

#     return qcd_template


# @cml.trace()
# def create_input(config, sample, variable, category, channel, template,
#                  input_file=None, phase_space=None, **kwargs):
#     tree, branch, hist = None, None, None
#     selection = '1'
#     if not input_file:
#         input_file = get_file(config, sample, category, channel)

#     if config.centre_of_mass_energy == 13:
#         branch = template.split('/')[-1]
#         tree = template.replace('/' + branch, '')

#         if 'absolute_eta' in branch:
#             branch = 'abs(lepton_eta)'

#         if sample != 'data':
#             if category in config.met_systematics_suffixes and not variable in config.variables_no_met:
#                 branch = template.split('/')[-1]
#                 branch += '_METUncertainties[%s]' % config.met_systematics[
#                     category]

#             if 'JES_down' in category or 'JES_up' in category or 'JER_down' in category or 'JER_up' in category:
#                 tree += config.categories_and_prefixes[category]

#             if not sample == 'data':
#                 if 'JES_down' in category:
#                     input_file = input_file.replace('tree', 'minusJES_tree')
#                 elif 'JES_up' in category:
#                     input_file = input_file.replace('tree', 'plusJES_tree')
#                 elif 'JER_up' in category:
#                     input_file = input_file.replace('tree', 'plusJER_tree')
#                 elif 'JER_down' in category:
#                     input_file = input_file.replace('tree', 'minusJER_tree')

#         selection = '{0} >= 0'.format(branch)
#         if variable == 'abs_lepton_eta':
#             selection += ' && {0} <= 3'.format(branch)
#     else:
#         hist = template

#     lumi_scale = config.luminosity_scale
#     scale = 1.

#     m = kwargs['measurement']
#     if m.type == Systematic.RATE:
#         if 'luminosity' in m.name:
#             lumi_scale = lumi_scale * m.scale
#         else:
#             if sample in m.affected_samples:
#                 scale = m.scale
#     if sample == 'data':  # data is not scaled in any way
#         lumi_scale = 1.
#         scale = 1.

#     edges = variable_binning.reco_bin_edges_full[variable]
#     if phase_space == 'VisiblePS':
#         edges = variable_binning.reco_bin_edges_vis[variable]

#     weight_branches = []
#     if sample == 'data':
#         weight_branches.append('1')
#     else:
#         weight_branches.append('EventWeight')

#         if 'PileUp' not in category:
#             weight_branches.append('PUWeight')
#         elif category == 'PileUp_up':
#             weight_branches.append('PUWeight_up')
#         elif category == 'PileUp_down':
#             weight_branches.append('PUWeight_down')
#         else:
#             weight_branches.append('1')

#         if category == 'BJet_down':
#             weight_branches.append('BJetDownWeight')
#         elif category == 'BJet_up':
#             weight_branches.append('BJetUpWeight')
#         elif category == 'LightJet_down':
#             weight_branches.append('LightJetDownWeight')
#         elif category == 'LightJet_up':
#             weight_branches.append('LightJetUpWeight')
#         else:
#             weight_branches.append('BJetWeight')

        # if not 'QCD' in tree:
        #     if channel == 'muon':
        #         if category == 'Muon_down':
        #             weight_branches.append('MuonDown')
        #         elif category == 'Muon_up':
        #             weight_branches.append('MuonUp')
        #         else:
        #             weight_branches.append('MuonEfficiencyCorrection')
        #     elif channel == 'electron':
        #         if category == 'Electron_down':
        #             weight_branches.append('ElectronDown')
        #         elif category == 'Electron_up':
        #             weight_branches.append('ElectronUp')
        #         else:
        #             weight_branches.append('ElectronEfficiencyCorrection')

#     i = Input(
#         input_file=input_file,
#         hist=hist,
#         tree=tree,
#         branch=branch,
#         selection=selection,
#         bin_edges=edges,
#         lumi_scale=lumi_scale,
#         scale=scale,
#         weight_branches=weight_branches,
#     )
#     return i

if __name__ == '__main__':
    main()
