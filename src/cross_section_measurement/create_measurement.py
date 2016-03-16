'''
    Translates the current config (for a given centre-of-mass energy)
    into JSON configs. The configs will be written to 
    config/measurements/background_subtraction/<centre of mass energy>TeV/
    
    Usage:
        python src/cross_section_measurement/create_measurement.py -c <centre of mass energy>
        
    Example:
        python src/cross_section_measurement/create_measurement.py -c 
'''
from __future__ import print_function
from optparse import OptionParser
import tools.measurement
from config import XSectionConfig, variable_binning
from tools.input import Input
from tools.logger import log
from copy import deepcopy

# define logger for this module
create_measurement_log = log["01b_get_ttjet_normalisation"]
cml = create_measurement_log  # alias


@cml.trace()
def main():
    parser = OptionParser(__doc__)
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=13, type=int,
                      help="set the centre of mass energy for analysis. Default = 13 [TeV]")
    parser.add_option('-d', '--debug', dest="debug", action="store_true",
                      help="Print the debug information")
    (options, _) = parser.parse_args()
    centre_of_mass_energy = options.CoM
    # set global variables
    debug = options.debug
    if debug:
        log.setLevel(log.DEBUG)

    measurement_config = XSectionConfig(centre_of_mass_energy)
    categories = ['QCD_shape']
    categories.extend(measurement_config.categories_and_prefixes.keys())
    categories.extend(measurement_config.rate_changing_systematics_names)
    categories.extend([measurement_config.vjets_theory_systematic_prefix +
                       systematic for systematic in measurement_config.generator_systematics if not ('mass' in systematic or 'hadronisation' in systematic or 'NLO' in systematic)])

    for variable in measurement_config.variables():
        for category in categories:
            for channel in ['electron', 'muon']:
                if channel == 'electron' and (category == 'Muon_down' or category == 'Muon_up'):
                    continue
                elif channel == 'muon' and (category == 'Electron_down' or category == 'Electron_up'):
                    continue
                create_measurement(
                    centre_of_mass_energy, category, variable, channel,
                    phase_space='FullPS', norm_method='background_subtraction')
                # and the visible phase space
                create_measurement(
                    centre_of_mass_energy, category, variable, channel,
                    phase_space='VisiblePS', norm_method='background_subtraction')


@cml.trace()
def create_measurement(com, category, variable, channel, phase_space, norm_method):
    if com == 13:
        # exclude non existing systematics
        if 'VJets' in category and 'scale' in category:
            print('Exculding {0} for now'.format(category))
            return
    config = XSectionConfig(com)
    met_type = get_met_type(category, config)
    should_not_run_systematic = category in config.met_systematics_suffixes and variable in config.variables_no_met and not 'JES' in category and not 'JER' in category
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
        'lepton': channel.title(),
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
            variable_template, phase_space=phase_space, measurement=m,
        ),
    )
    m.addSample(
        'V+Jets',
        False,
        input=create_input(
            config, 'V+Jets', variable, template_category, channel,
            variable_template, phase_space=phase_space, measurement=m,
        ),
    )
    m.addSample(
        'SingleTop',
        False,
        input=create_input(
            config, 'SingleTop', variable, template_category, channel,
            variable_template, phase_space=phase_space, measurement=m,
        ),
    )
    m.addSample(
        'QCD',
        False,
        input=create_input(
            config, 'QCD', variable, template_category, channel,
            variable_template, phase_space=phase_space, measurement=m,
        ),
    )
    variable_template_data = variable_template.replace(
        met_type, config.translate_options['type1'])

    m.addSample(
        'data',
        False,
        input=create_input(
            config, 'data', variable, template_category, channel,
            variable_template_data, phase_space=phase_space, measurement=m,
        ),
    )

    m_qcd = tools.measurement.Measurement(category)
    m_qcd.setVariable(variable)
    m_qcd.setCentreOfMassEnergy(com)

    qcd_template = get_qcd_template(config, variable, category, channel)

    # we want "measurement = m" here since all rate systematics should apply
    # to the control regions as well
    m_qcd.addSample(
        'TTJet',
        False,
        input=create_input(
            config, 'TTJet', variable, template_category, channel,
            qcd_template, phase_space=phase_space, measurement=m,
        ),
    )
    m_qcd.addSample(
        'V+Jets',
        False,
        input=create_input(
            config, 'V+Jets', variable, template_category, channel,
            qcd_template, phase_space=phase_space, measurement=m,
        ),
    )
    m_qcd.addSample(
        'SingleTop',
        False,
        input=create_input(
            config, 'SingleTop', variable, template_category, channel,
            qcd_template, phase_space=phase_space, measurement=m,
        ),
    )
    m_qcd.addSample(
        'QCD',
        False,
        input=create_input(
            config, 'QCD', variable, template_category, channel,
            qcd_template, phase_space=phase_space, measurement=m,
        ),
    )
    m_qcd.addSample(
        'data',
        False,
        input=create_input(
            config, 'data', variable, template_category, channel,
            qcd_template, phase_space=phase_space, measurement=m,
        ),
    )

    m.addShapeForSample('QCD', m_qcd, False)
    norm_qcd = deepcopy(m_qcd)
    # we want QCD shape and normalisation to be separate
    if category == 'QCD_shape':
        for sample in norm_qcd.samples.keys():
            tree = norm_qcd.samples[sample]['input'].tree_name
            if channel == 'electron':
                tree = tree.replace(config.electron_control_region_systematic,
                                    config.electron_control_region)
            else:
                tree = tree.replace(config.muon_control_region_systematic,
                                    config.muon_control_region)
            norm_qcd.samples[sample]['input'].tree_name = tree
    if 'QCD_cross_section' in category:
        for sample in norm_qcd.samples.keys():
            tree = norm_qcd.samples[sample]['input'].tree_name
            if channel == 'electron':
                tree = tree.replace(config.electron_control_region,
                                    config.electron_control_region_systematic)
            else:
                tree = tree.replace(config.muon_control_region,
                                    config.muon_control_region_systematic)
            norm_qcd.samples[sample]['input'].tree_name = tree

    m.addNormForSample('QCD', norm_qcd, False)

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
                    config8.generator_systematic_vjets_templates[
                        v_template_category],
                    phase_space=phase_space, measurement=m,
                )
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
                phase_space=phase_space, measurement=m,
            )
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


@cml.trace()
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


@cml.trace()
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


@cml.trace()
def get_qcd_template(config, variable, category, channel):
    qcd_inputs = {
        'channel': config.analysis_types[channel],
        'met_type': config.translate_options['type1'],  # always central MET
        'selection': 'Ref selection',
        'btag': config.translate_options['2m'],  # 2 or more
        'energy': config.centre_of_mass_energy,
        'variable': variable,
        'category': 'central',  # always central
        'lepton': channel.title(),
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


@cml.trace()
def create_input(config, sample, variable, category, channel, template,
                 input_file=None, phase_space=None, **kwargs):
    tree, branch, hist = None, None, None
    selection = '1'
    if not input_file:
        input_file = get_file(config, sample, category, channel)

    if config.centre_of_mass_energy == 13:
        branch = template.split('/')[-1]
        tree = template.replace('/' + branch, '')

        if 'absolute_eta' in branch:
            branch = 'abs(lepton_eta)'

        if sample != 'data':
            if category in config.met_systematics_suffixes and not variable in config.variables_no_met:
                branch = template.split('/')[-1]
                branch += '_METUncertainties[%s]' % config.met_systematics[
                    category]

            if 'JES_down' in category or 'JES_up' in category or 'JER_down' in category or 'JER_up' in category:
                tree += config.categories_and_prefixes[category]

            if not sample == 'data':
                if 'JES_down' in category:
                    input_file = input_file.replace('tree', 'minusJES_tree')
                elif 'JES_up' in category:
                    input_file = input_file.replace('tree', 'plusJES_tree')
                elif 'JER_up' in category:
                    input_file = input_file.replace('tree', 'plusJER_tree')
                elif 'JER_down' in category:
                    input_file = input_file.replace('tree', 'minusJER_tree')

        selection = '{0} >= 0'.format(branch)
        if variable == 'abs_lepton_eta':
            selection += ' && {0} <= 3'.format(branch)
    else:
        hist = template

    lumi_scale = config.luminosity_scale
    scale = 1.

    m = kwargs['measurement']
    if m.type == tools.measurement.Systematic.RATE:
        if 'luminosity' in m.name:
            lumi_scale = lumi_scale * m.scale
        else:
            if sample in m.affected_samples:
                scale = m.scale
    if sample == 'data':  # data is not scaled in any way
        lumi_scale = 1.
        scale = 1.

    edges = variable_binning.reco_bin_edges_vis_full[variable]
    if phase_space == 'VisiblePS':
        edges = variable_binning.reco_bin_edges_vis[variable]

    weight_branches = []
    if sample == 'data':
        weight_branches.append('1')
    else:
        weight_branches.append('EventWeight')
        if category != 'PileUpSystematic':
            weight_branches.append('PUWeight')
        if category == 'BJet_down':
            weight_branches.append('BJetDownWeight')
        elif category == 'BJet_up':
            weight_branches.append('BJetUpWeight')
        else:
            weight_branches.append('BJetWeight')

        if not 'QCD' in tree:
            if channel == 'muon':
                if category == 'Muon_down':
                    weight_branches.append('MuonDown')
                elif category == 'Muon_up':
                    weight_branches.append('MuonUp')
                else:
                    weight_branches.append('MuonEfficiencyCorrection')
            elif channel == 'electron':
                if category == 'Electron_down':
                    weight_branches.append('ElectronDown')
                elif category == 'Electron_up':
                    weight_branches.append('ElectronUp')
                else:
                    weight_branches.append('ElectronEfficiencyCorrection')

    i = Input(
        input_file=input_file,
        hist=hist,
        tree=tree,
        branch=branch,
        selection=selection,
        bin_edges=edges,
        lumi_scale=lumi_scale,
        scale=scale,
        weight_branches=weight_branches,
    )
    return i

if __name__ == '__main__':
    main()
