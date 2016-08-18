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
from config import XSectionConfig


def main():
    parser = OptionParser(__doc__)
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    (options, _) = parser.parse_args()
    centre_of_mass_energy = options.CoM
    measurement_config = XSectionConfig(centre_of_mass_energy)
    categories = ['QCD_shape']
    categories.extend(measurement_config.categories_and_prefixes.keys())
    categories.extend(measurement_config.rate_changing_systematics_names)
    categories.extend(measurement_config.met_systematics_suffixes)
    categories.extend([measurement_config.vjets_theory_systematic_prefix +
                       systematic for systematic in measurement_config.generator_systematics])
    for met_unc in ['JetEnUp', 'JetEnDown', 'JetResUp', 'JetResDown']:
        # the above ones are done together with
        # categories_and_prefixes, see get_met_type
        categories.remove(met_unc)

    for variable in ['MET', 'HT', 'ST', 'WPT', 'MT']:
        for category in categories:
            for channel in ['electron', 'muon']:
                create_measurement(
                    centre_of_mass_energy, category, variable, channel)


def create_measurement(com, category, variable, channel):
    config = XSectionConfig(com)
    met_type = get_met_type(category, config)
    if category in config.met_systematics_suffixes and variable == 'HT':
        # no MET uncertainty on HT
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
    }
    variable_template = config.variable_path_templates[
        variable].format(**inputs)
    template_category = category
    if category == 'QCD_shape' or category in config.rate_changing_systematics_names or category in config.met_systematics_suffixes:
        template_category = 'central'
    if category in [config.vjets_theory_systematic_prefix + systematic for systematic in config.generator_systematics]:
        template_category = 'central'

    m.addSample('TTJet', config.ttbar_category_templates[
                template_category], variable_template, False)
    m.addSample(
        'V+Jets', config.VJets_category_templates[template_category], variable_template, False)
    m.addSample('SingleTop', config.SingleTop_category_templates[
                template_category], variable_template, False)
    if channel == 'electron':
        m.addSample('QCD', config.electron_QCD_MC_category_templates[
                    template_category], variable_template, False)
        m.addSample('data', config.data_file_electron, variable_template.replace(
            met_type, config.translate_options['type1']), False)
    else:
        m.addSample('QCD', config.muon_QCD_MC_category_templates[
                    template_category], variable_template, False)
        m.addSample('data', config.data_file_muon, variable_template.replace(
            met_type, config.translate_options['type1']), False)

    m_qcd = tools.measurement.Measurement(category)
    m_qcd.setVariable(variable)
    m_qcd.setCentreOfMassEnergy(com)

    qcd_inputs = {
        'channel': config.analysis_types[channel],
        'met_type': config.translate_options['type1'],  # always central MET
        'selection': 'Ref selection',
        'btag': config.translate_options['2m'],  # 2 or more
        'energy': com,
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
                config.electron_control_region, config.electron_control_region_systematic)
    else:
        qcd_template = qcd_template.replace(
            'Ref selection', config.muon_control_region)
        if category == 'QCD_shape':
            qcd_template = qcd_template.replace(
                config.muon_control_region, config.muon_control_region_systematic)

    m_qcd.addSample('TTJet', config.ttbar_category_templates[
                    template_category], qcd_template, False)
    m_qcd.addSample(
        'V+Jets', config.VJets_category_templates[template_category], qcd_template, False)
    m_qcd.addSample('SingleTop', config.SingleTop_category_templates[
                    template_category], qcd_template, False)
    if channel == 'electron':
        m_qcd.addSample('QCD', config.data_file_electron, qcd_template, False)
    elif channel == 'muon':
        m_qcd.addSample('QCD', config.data_file_muon, qcd_template, False)

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
                'V+Jets', config8.generator_systematic_vjets_templates[v_template_category], variable_template, False)
        else:
            m_vjets.addSample(
                'V+Jets', config.generator_systematic_vjets_templates[v_template_category], variable_template, False)
        m.addShapeForSample('V+Jets', m_vjets, False)

    inputs['channel'] = channel
    if category == 'central':
        m.toJSON(
            'config/measurements/background_subtraction/{energy}TeV/{channel}/{variable}/{category}.json'.format(**inputs))
    else:
        if m.type == tools.measurement.Systematic.SHAPE:
            inputs['type'] = 'shape_systematic'
        else:
            inputs['type'] = 'rate_systematic'
        if category in config.met_systematics_suffixes:
            inputs['category'] = met_type

        m.toJSON(
            'config/measurements/background_subtraction/{energy}TeV/{channel}/{variable}/{category}_{type}.json'.format(**inputs))


def get_met_type(category, config):
    met_type = config.translate_options['type1']
    if category in ['JES_up', 'JES_down', 'JER_up', 'JER_down']:
        if category == 'JES_up':
            met_type += 'JetEnUp'
        elif category == 'JES_down':
            met_type += 'JetEnDown'
        elif category == 'JER_up':
            met_type += 'JetResUp'
        elif category == 'JER_down':
            met_type += 'JetResDown'

    if category in config.met_systematics_suffixes:
        # already done them
        if not category in ['JetEnUp', 'JetEnDown', 'JetResUp', 'JetResDown']:
            met_type = met_type + category

    return met_type

if __name__ == '__main__':
    main()
