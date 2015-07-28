'''
    Translates the current config (for a given centre-of-mass energy)
    into JSON configs. The configs will be written to 
    config/measurements/background_subtraction/<centre of mass energy>TeV/
    
    Usage:
        python src/cross_section_measurement/create_measurement.py -c <centre of mass energy>
        
    Example:
        python src/cross_section_measurement/create_measurement.py -c 
'''

from optparse import OptionParser
import tools.measurement
from config import XSectionConfig, variable_binning
from tools.input import Input


def main():
    parser = OptionParser(__doc__)
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=13, type=int,
                      help="set the centre of mass energy for analysis. Default = 13 [TeV]")
    (options, _) = parser.parse_args()
    centre_of_mass_energy = options.CoM
    measurement_config = XSectionConfig(centre_of_mass_energy)
    categories = ['QCD_shape']
    categories.extend(measurement_config.categories_and_prefixes.keys())
    categories.extend(measurement_config.rate_changing_systematics_names)
    categories.extend([measurement_config.vjets_theory_systematic_prefix +
                       systematic for systematic in measurement_config.generator_systematics if not 'mass' in systematic])

    for variable in ['MET', 'HT', 'ST', 'WPT']:
        for category in categories:
            for channel in ['electron', 'muon']:
                create_measurement(
                    centre_of_mass_energy, category, variable, channel,
                    phase_space='FullPS', norm_method='background_subtraction')
                # and the visible phase space
                create_measurement(
                    centre_of_mass_energy, category, variable, channel,
                    phase_space='VisiblePS', norm_method='background_subtraction')


def create_measurement(com, category, variable, channel, phase_space, norm_method):
    if com == 13:
        # exclude non existing systematics
        if 'VJets' in category and 'scale' in category:
            print('Exculding {0} for now'.format(category))
            return
    config = XSectionConfig(com)
    met_type = get_met_type(category, config)
    should_not_run_systematic = category in config.met_systematics_suffixes and variable == 'HT' and not 'JES' in category and not 'JER' in category
    if should_not_run_systematic:
        # no MET uncertainty on HT (but JES and JER of course)
        return

    m = None

    if category == 'central':
        m = tools.measurement.Measurement(category)
    else:
        vjet_systematics = [config.vjets_theory_systematic_prefix +
                            systematic for systematic in config.generator_systematics]
        if category in config.categories_and_prefixes.keys() or \
                category in config.met_systematics_suffixes or \
                category in vjet_systematics:
            m = tools.measurement.Systematic(category,
                                             stype=tools.measurement.Systematic.SHAPE,
                                             affected_samples=config.samples)
        elif category in config.rate_changing_systematics_names:
            m = config.rate_changing_systematics_values[category]

        elif category == 'QCD_shape':
            m = tools.measurement.Systematic(category,
                                             stype=tools.measurement.Systematic.SHAPE,
                                             affected_samples=['QCD'],
                                             )

    m.setVariable(variable)
    m.setCentreOfMassEnergy(com)
    m.setChannel(channel)
    m.setMETType(met_type)

    inputs = {
        'channel': config.analysis_types[channel],
        'met_type': met_type,
        'selection': 'Ref selection',
        'btag': config.translate_options['2m'],  # 2 or more
        'energy': com,
        'variable': variable,
        'category': category,
        'phase_space': phase_space,
        'norm_method': norm_method,
    }
    variable_template = config.variable_path_templates[
        variable].format(**inputs)
    template_category = category
    if category == 'QCD_shape' or category in config.rate_changing_systematics_names:
        template_category = 'central'
    if category in [config.vjets_theory_systematic_prefix + systematic for systematic in config.generator_systematics]:
        template_category = 'central'
    m.addSample(
        'TTJet',
        False,
        input=create_input(
            config, 'TTJet', variable, template_category, channel,
            variable_template, phase_space = phase_space),
    )
    m.addSample(
        'V+Jets',
        False,
        input=create_input(
            config, 'V+Jets', variable, template_category, channel,
            variable_template, phase_space = phase_space),
    )
    m.addSample(
        'SingleTop',
        False,
        input=create_input(
            config, 'SingleTop', variable, template_category, channel,
            variable_template, phase_space = phase_space),
    )
    m.addSample(
        'QCD',
        False,
        input=create_input(
            config, 'QCD', variable, template_category, channel,
            variable_template, phase_space = phase_space),
    )
    variable_template_data = variable_template.replace(
        met_type, config.translate_options['type1'])
    m.addSample(
        'data',
        False,
        input=create_input(
            config, 'data', variable, template_category, channel, 
            variable_template_data, phase_space = phase_space),
    )

    m_qcd = tools.measurement.Measurement(category)
    m_qcd.setVariable(variable)
    m_qcd.setCentreOfMassEnergy(com)

    qcd_template = get_qcd_template(config, variable, category, channel)

    m_qcd.addSample(
        'TTJet',
        False,
        input=create_input(
            config, 'TTJet', variable, template_category, channel,
            qcd_template, phase_space = phase_space),
    )
    m_qcd.addSample(
        'V+Jets',
        False,
        input=create_input(
            config, 'V+Jets', variable, template_category, channel,
            qcd_template, phase_space = phase_space),
    )
    m_qcd.addSample(
        'SingleTop',
        False,
        input=create_input(
            config, 'SingleTop', variable, template_category, channel,
            qcd_template, phase_space = phase_space),
    )
    m_qcd.addSample(
        'QCD',
        False,
        input=create_input(
            config, 'data', variable, template_category, channel,
            qcd_template, phase_space = phase_space),
    )

    m.addShapeForSample('QCD', m_qcd, False)

    if category in [config.vjets_theory_systematic_prefix + systematic for systematic in config.generator_systematics]:
        v_template_category = category.replace(
            config.vjets_theory_systematic_prefix, '')
        m_vjets = tools.measurement.Measurement(category)
        m_vjets.setVariable(variable)
        m_vjets.setCentreOfMassEnergy(com)
        if com == 7:  # special case for 7 TeV where we use 8 TeV shapes
            config8 = XSectionConfig(8)
            m_vjets.addSample(
                'V+Jets',
                False,
                input=create_input(
                    config, 'V+Jets', variable, v_template_category,
                    channel,
                    variable_template,
                    config8.generator_systematic_vjets_templates[v_template_category],
                    phase_space = phase_space)
            )
        else:
            m_vjets.addSample(
                'V+Jets',
                False,
                input=create_input(
                    config, 'V+Jets', variable, v_template_category,
                    channel,
                    variable_template,
                    config.generator_systematic_vjets_templates[
                        v_template_category]),
                    phase_space = phase_space)
        m.addShapeForSample('V+Jets', m_vjets, False)

    inputs['channel'] = channel
    base_path = 'config/measurements/{norm_method}/{energy}TeV/'
    base_path += '{channel}/{variable}/{phase_space}/'
    if category == 'central':
        path = base_path + '{category}.json'
        m.toJSON(path.format(**inputs))
    else:
        if m.type == tools.measurement.Systematic.SHAPE:
            inputs['type'] = 'shape_systematic'
        else:
            inputs['type'] = 'rate_systematic'
        if category in config.met_systematics_suffixes and category not in ['JES_up', 'JES_down', 'JER_up', 'JER_down']:
            inputs['category'] = met_type
        path = base_path + '{category}_{type}.json'
        m.toJSON(path.format(**inputs))


def get_met_type(category, config):
    met_type = config.translate_options['type1']
    if category == 'JES_up':
        met_type += 'JetEnUp'
    elif category == 'JES_down':
        met_type += 'JetEnDown'
    elif category == 'JER_up':
        met_type += 'JetResUp'
    elif category == 'JER_down':
        met_type += 'JetResDown'

    isJetSystematic = 'JetEn' in category or 'JetRes' in category
    isJetSystematic = isJetSystematic or 'JES' in category
    isJetSystematic = isJetSystematic or 'JER' in category

    if category in config.met_systematics_suffixes:
        # already done them
        if not isJetSystematic:
            met_type = met_type + category

    return met_type


def get_file(config, sample, category, channel):
    use_trees = True if config.centre_of_mass_energy == 13 else False
    if channel == 'electron':
        qcd_template = config.electron_QCD_MC_category_templates[category]
        data_template = config.data_file_electron
        qcd_template_tree = config.electron_QCD_MC_category_templates_trees[
            category]
        data_template_tree = config.data_file_electron_trees
    else:
        qcd_template = config.muon_QCD_MC_category_templates[category]
        data_template = config.data_file_muon
        qcd_template_tree = config.muon_QCD_MC_category_templates_trees[
            category]
        data_template_tree = config.data_file_muon_trees

    tree_files = {
        'TTJet': config.ttbar_category_templates_trees[category],
        'V+Jets': config.VJets_category_templates_trees[category],
        'SingleTop': config.SingleTop_category_templates_trees[category],
        'QCD': qcd_template_tree,
        'data': data_template_tree
    }
    files = {
        'TTJet': config.ttbar_category_templates[category],
        'V+Jets': config.VJets_category_templates[category],
        'SingleTop': config.SingleTop_category_templates[category],
        'QCD': qcd_template,
        'data': data_template,
    }

    if use_trees:
        return tree_files[sample]
    else:
        return files[sample]


def get_qcd_template(config, variable, category, channel):
    qcd_inputs = {
        'channel': config.analysis_types[channel],
        'met_type': config.translate_options['type1'],  # always central MET
        'selection': 'Ref selection',
        'btag': config.translate_options['2m'],  # 2 or more
        'energy': config.centre_of_mass_energy,
        'variable': variable,
        'category': 'central',  # always central
    }
    qcd_template = config.variable_path_templates[
        variable].format(**qcd_inputs)
    if channel == 'electron':
        qcd_template = qcd_template.replace(
            'Ref selection', config.electron_control_region)
        if category == 'QCD_shape':
            qcd_template = qcd_template.replace(
                config.electron_control_region,
                config.electron_control_region_systematic)
    else:
        qcd_template = qcd_template.replace(
            'Ref selection', config.muon_control_region)
        if category == 'QCD_shape':
            qcd_template = qcd_template.replace(
                config.muon_control_region,
                config.muon_control_region_systematic)

    return qcd_template


def create_input(config, sample, variable, category, channel, template,
                 input_file=None, phase_space = None):
    tree, branch, hist = None, None, None
    selection = '1'
    if not input_file:
        input_file = get_file(config, sample, category, channel)

    if config.centre_of_mass_energy == 13:
        branch = template.split('/')[-1]
        tree = template.replace('/' + branch, '')

        if sample != 'data':
            if category in config.met_systematics_suffixes and variable != 'HT':
                branch = template.split('/')[-1]
                branch += '_METUncertainties[%s]' % config.met_systematics[
                    category]

            if 'JES_down' in category or 'JES_up' in category:
                tree += config.categories_and_prefixes[category]

        selection = '{0} >= 0'.format(branch)
    else:
        hist = template
    lumi_scale = 1.
    if not sample == 'data':
        lumi_scale = config.luminosity_scale
        if channel == 'electron':
            lumi_scale = lumi_scale * 0.84
        if channel == 'muon':
            lumi_scale = lumi_scale * 0.63
    edges = variable_binning.bin_edges[variable]
    if phase_space == 'VisiblePS':
        edges = variable_binning.bin_edges_vis[variable]

    i = Input(
        input_file=input_file,
        hist=hist,
        tree=tree,
        branch=branch,
        selection=selection,
        bin_edges=edges,
        lumi_scale=lumi_scale,
    )
    return i

if __name__ == '__main__':
    main()
