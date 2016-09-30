from __future__ import division
import tools.measurement

class XSectionConfig():
    current_analysis_path = '/hdfs/TopQuarkGroup/run2/atOutput/'
    known_centre_of_mass_energies = [13]
    # has to be separate as many variables depend on it
    luminosities = {13:12835}

    parameters = [
        'SingleTop_category_templates', 'SingleTop_category_templates_trees', 'SingleTop_file',
        'VJets_category_templates', 'VJets_category_templates_trees', 'analysis_types',
        'categories_and_prefixes', 'central_general_template',
        'centre_of_mass_energy', 'current_analysis_path',
        'data_file_electron', 'data_file_muon',
        'data_file_electron_trees', 'data_file_muon_trees',
        'data_muon_category_templates', 'electron_QCD_MC_file',
        'electron_control_region',
        'electron_control_region_systematic',
        'fit_boundaries',
        'fit_variable_bin_width',
        'fit_variable_unit',
        'general_category_templates',
        'general_category_templates_trees',
        'generator_systematic_vjets_templates',
        'generator_systematics',
        'generator_mcsamples',
        'higgs_category_templates', 'higgs_file',
        'include_higgs',
        'tau_values_electron', 'tau_values_muon',
        'known_centre_of_mass_energies', 'luminosities',
        'luminosity', 'luminosity_scale', 'met_systematics',
        'muon_QCD_MC_category_templates', 'muon_QCD_MC_file',
        'muon_QCD_file', 'muon_control_region',
        'muon_control_region_systematic', 'new_luminosity',
        'parameters', 'path_to_files', 'path_to_unfolding_histograms',
        'rate_changing_systematics',
        'rebin', 'special_muon_histogram', 'translate_options',
        'ttbar_category_templates',
        'ttbar_category_templates_trees',
        'ttbar_generator_category_templates_trees',
        'ttbar_theory_systematic_prefix', 'ttbar_xsection',
        'unfolding_central', 'unfolding_central_raw',
        'unfolding_powheg_pythia8', 'unfolding_powheg_pythia8_raw',
        'unfolding_amcatnlo', 'unfolding_amcatnlo_raw', 
        'unfolding_madgraphMLM', 'unfolding_madgraphMLM_raw',
        'unfolding_matching_down', 'unfolding_matching_down_raw',
        'unfolding_matching_up', 'unfolding_matching_up_raw',
        'unfolding_mass_down', 'unfolding_mass_up',
        'unfolding_mcatnlo', 'unfolding_mcatnlo_raw',
        'unfolding_powheg_pythia', 'unfolding_powheg_pythia_raw',
        'unfolding_powheg_herwig', 'unfolding_powheg_herwig_raw',
        'unfolding_scale_down', 'unfolding_scale_down_raw',
        'unfolding_scale_up', 'unfolding_scale_up_raw',
        'unfolding_ptreweight', 'unfolding_ptreweight_raw',
        'unfolding_pdfweights',
        'vjets_theory_systematic_prefix'
    ]
    
    samples = [
        'TTJet', 
        'V+Jets', 
        'SingleTop', 
        'QCD'
    ]

    variables = [
        'HT',
        'MET',
        'ST',
        'WPT',
        'NJets',
        'lepton_pt',
        'abs_lepton_eta'
    ]

    variables_no_met = [
        'HT', 
        'NJets', 
        'lepton_pt', 
        'lepton_eta',
        'abs_lepton_eta', 
        'bjets_pt', 
        'bjets_eta',
        'abs_bjets_eta'
    ]

    def __init__( self, centre_of_mass_energy ):
        if not centre_of_mass_energy in self.known_centre_of_mass_energies:
            raise AttributeError( 'Unknown centre of mass energy' )
        self.centre_of_mass_energy = centre_of_mass_energy
        self.__fill_defaults__()

    def __fill_defaults__( self ):
        self.met_type = 'patType1CorrectedPFMet'

        self.path_to_files = self.current_analysis_path + str( self.centre_of_mass_energy ) + 'TeV/2016/'
        self.path_to_unfolding_histograms = '/hdfs/TopQuarkGroup/run2/unfolding/13TeV/2016/'

        path_to_files = self.path_to_files
        path_to_unfolding_histograms = self.path_to_unfolding_histograms

        self.luminosity = self.luminosities[self.centre_of_mass_energy]

        # general
        self.met_systematics = {
            'JER_up' : 0,
            'JER_down' : 1,
            'JES_up' : 2,
            'JES_down' : 3,
            'ElectronEnUp' : 6,
            'ElectronEnDown' : 7,
            'MuonEnUp' : 4,
            'MuonEnDown' : 5,
            'TauEnUp' : 8,
            'TauEnDown' : 9,
            'UnclusteredEnUp' : 10,
            'UnclusteredEnDown' : 11,
            # 'ElectronEn_up' : 6,
            # 'ElectronEn_down' : 7,
            # 'MuonEn_up' : 4,
            # 'MuonEn_down' : 5,
            # 'TauEn_up' : 8,
            # 'TauEn_down' : 9,
            # 'UnclusteredEn_up' : 10,
            # 'UnclusteredEn_down' : 11,
        }

        self.analysis_types = {
            'electron':'EPlusJets',
            'muon':'MuPlusJets',
            'combined':'combined'
        }

        # measurement script options
        self.translate_options = {
            'all':'',
            '0':'0btag',
            '1':'1btag',
            '2':'2btags',
            '3':'3btags',
            '0m':'0orMoreBtag',
            '1m':'1orMoreBtag',
            '2m':'2orMoreBtags',
            '3m':'3orMoreBtags',
            '4m':'4orMoreBtags',
            # mettype:
            'pf':'PFMET',
            'type1':'patType1CorrectedPFMet',
        }

        self.ttbar_theory_systematic_prefix = 'TTJets_'
        self.vjets_theory_systematic_prefix = 'VJets_'
        # files
        self.middle = '_' + str( self.luminosity ) + 'pb_PFElectron_PFMuon_PF2PATJets_PFMET'
        middle = self.middle

        self.data_file_muon = path_to_files + 'data_muon_tree.root'
        self.data_file_electron = path_to_files + 'data_electron_tree.root'

        self.data_file_muon_trees = path_to_files + 'data_muon_tree.root'
        # self.data_file_muon_trees = '/storage/ec6821/AnalysisTools/CMSSW_8_0_17/src/tree_SingleMuon_15930pb_PFElectron_PFMuon_PF2PATJets_MET_201.root'
        self.data_file_electron_trees = path_to_files + 'data_electron_tree.root'

        self.muon_QCD_file = path_to_files + 'QCD_data_mu.root'
        self.SingleTop_file = path_to_files + 'SingleTop.root'
        self.electron_QCD_MC_file = path_to_files + 'QCD_Electron.root'
        self.muon_QCD_MC_file = path_to_files + 'QCD_data_mu.root'

        self.SingleTop_tree_file = path_to_files + 'SingleTop_tree.root'
        self.muon_QCD_tree_file = path_to_files + 'QCD_Muon_tree.root'
        self.electron_QCD_MC_tree_file = path_to_files + 'QCD_Electron_tree.root'
        self.muon_QCD_MC_tree_file = path_to_files + 'QCD_Muon_tree.root'

        self.higgs_file = path_to_files + 'central/TTH_Inclusive_M-125' + middle + '.root'

        self.categories_and_prefixes = {
            'central':'',
            'Electron_down':'ElectronDown',
            'Electron_up':'ElectronUp',
            'Muon_down':'MuonDown',
            'Muon_up':'MuonUp',
            'BJet_down':'BJetDown',
            'BJet_up':'BJetUp',
            'LightJet_down':'LightJetDown',
            'LightJet_up':'LightJetUp',
            'JES_down':'_JESDown',
            'JES_up':'_JESUp',
            # 'JES_down_alphaCorr':'_JESDown_alphaCorr',
            # 'JES_up_alphaCorr':'_JESUp_alphaCorr',
            'JER_down':'_JERDown',
            'JER_up':'_JERUp',

            'PileUp_up' : '',
            'PileUp_down' : '',

            # Other MET uncertainties not already included
            'ElectronEnUp' : '',
            'ElectronEnDown' : '',
            'MuonEnUp' : '',
            'MuonEnDown' : '',
            'TauEnUp' : '',
            'TauEnDown' : '',
            'UnclusteredEnUp' : '',
            'UnclusteredEnDown' : '',
        }

        self.list_of_systematics = {
            # Theoretical Uncertainties (Rate Changing)
            'V+Jets_cross_section'      : ['V+Jets_cross_section+', 'V+Jets_cross_section-'],
            'QCD_cross_section'         : ['QCD_cross_section+', 'QCD_cross_section-'],
            'SingleTop_cross_section'   : ['SingleTop_cross_section+', 'SingleTop_cross_section-'],
            'luminosity'                : ['luminosity+', 'luminosity-'],
            # QCD Shape
            'QCD_shape'                 : ['QCD_shape', 'QCD_shape'],
            # Generator Uncertainties
            'TTJets_scale'              : ['TTJets_scaleup', 'TTJets_scaledown'],
            'TTJets_mass'               : ['TTJets_massup', 'TTJets_massdown'],
            'TTJets_hadronisation'      : ['TTJets_hadronisation', 'TTJets_hadronisation'],
            'TTJets_NLOgenerator'       : ['TTJets_NLOgenerator', 'TTJets_NLOgenerator'],

            'TTJets_alphaS'             : ['TTJets_alphaSup', 'TTJets_alphaSdown'],
            'TTJets_envelope'           : ['TTJets_factorisationup', 'TTJets_factorisationdown',
                                            'TTJets_renormalisationup', 'TTJets_renormalisationdown',
                                            'TTJets_combinedup', 'TTJets_combineddown'],

            # Event Reweighting
            'PileUp'                    : ['PileUp_up', 'PileUp_down'],
            'JES'                       : ['JES_up', 'JES_down'],
            'JER'                       : ['JER_up', 'JER_down'],
            'BJet'                      : ['BJet_up', 'BJet_down'],
            'LightJet'                  : ['LightJet_up', 'LightJet_down'],
            # Lepton Uncertainties (Id/Iso/Trig Eff)
            'Electron'                  : ['Electron_up', 'Electron_down'],
            'Muon'                      : ['Muon_up', 'Muon_down'],
            # PDF Uncertainties
            'PDF'                       : ['PDF', 'PDF'],
            # MET Uncertainties
            'ElectronEn'                : ['ElectronEnUp', 'ElectronEnDown'],
            'MuonEn'                    : ['MuonEnUp', 'MuonEnDown'],
            'TauEn'                     : ['TauEnUp', 'TauEnDown'],
            'UnclusteredEn'             : ['UnclusteredEnUp', 'UnclusteredEnDown'],
            # Top Reweighting Uncertainties
            # 'Top_pt_reweight'           : ['Top_pt_reweight_up', 'Top_pt_reweight_down'],
            # 'Top_eta_reweight'          : ['Top_eta_reweight_up', 'Top_eta_reweight_down'],
        }

        self.met_specific_systematics = [
            'ElectronEnUp',
            'ElectronEnDown',
            'MuonEnUp',
            'MuonEnDown',
            'TauEnUp',
            'TauEnDown',
            'UnclusteredEnUp',
            'UnclusteredEnDown',
        ]



        self.met_systematics_suffixes = self.met_systematics.keys()

        # now fill in the centre of mass dependent values
        self.__fill_defaults_13TeV__()

        self.generator_systematics = [ 
            'scaleup', 'scaledown',
            'massup', 'massdown',
            'hadronisation',
            'NLOgenerator',
            'factorisationup', 'factorisationdown', 
            'renormalisationup', 'renormalisationdown', 
            'combinedup', 'combineddown', 
            'alphaSup', 'alphaSdown',
        ]

        self.generator_mcsamples = [
            'PowhegPythia8',
            'powhegHerwigpp',
            'amc',
            'amcatnloHerwigpp',    
            'madgraph'    
        ]

        self.rate_changing_systematics_values = {}
        for systematic in self.rate_changing_systematics.keys():
            affected_samples = XSectionConfig.samples # all samples
            if 'SingleTop' in systematic:
                affected_samples = ['SingleTop']
            if 'TTJet' in systematic:
                affected_samples = ['TTJet'] 
            if 'VJets' in systematic:
                affected_samples = ['V+Jets']
            if 'QCD' in systematic:
                affected_samples = ['QCD']

            sp = tools.measurement.Systematic( 
                        systematic + '+',
                        # systematic + '_up',
                        stype = tools.measurement.Systematic.RATE,
                        affected_samples = affected_samples,
                        scale = 1 + self.rate_changing_systematics[systematic],
                        )
            scale = 1 - self.rate_changing_systematics[systematic]
            if scale <= 0: scale = 10e-5

            sm = tools.measurement.Systematic( 
                        systematic + '-',
                        # systematic + '_down',
                        stype = tools.measurement.Systematic.RATE,
                        affected_samples = affected_samples,
                        scale = scale,
                        )
            self.rate_changing_systematics_values[sp.name] = sp
            self.rate_changing_systematics_values[sm.name] = sm

        self.rate_changing_systematics_names = self.rate_changing_systematics_values.keys()

        self.topMass_systematics = [ 'TTJets_massup', 'TTJets_massdown']
        # self.topMass_systematics = [ 'TTJets_mass_up', 'TTJets_mass_down']
        self.topMasses = [
            169.5, 
            172.5, 
            173.5,
        ]
        self.topMassUncertainty = 1.0 # GeV from https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO

        self.central_general_template = path_to_files + 'central/%s' + middle + '.root'
        self.generator_systematic_vjets_templates = {}
        for systematic in self.generator_systematics:
            if 'mass' in systematic or 'hadronisation' in systematic or 'NLOgenerator' in systematic:
                continue
            tmp = path_to_files + 'central/VJets-{0}_{1}pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
            tmp = tmp.format(systematic, self.luminosity)
            self.generator_systematic_vjets_templates[systematic] = tmp

        categories_and_prefixes = self.categories_and_prefixes
        generator_mcsamples = self.generator_mcsamples

        # File Templates
        self.general_category_templates = {category: path_to_files + category + '/%s' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
        self.ttbar_category_templates = {category: path_to_files + 'TTJets_PowhegPythia8.root' for category, prefix in categories_and_prefixes.iteritems()}
        self.SingleTop_category_templates = {category: path_to_files + '/SingleTop.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.VJets_category_templates = {category: path_to_files + '/VJets.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.higgs_category_templates = {category: path_to_files + '/TTH_Inclusive_M-125' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.electron_QCD_MC_category_templates = {category: path_to_files + '/QCD_Electron.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.muon_QCD_MC_category_templates = {category: path_to_files + '/QCD_Muon.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}

        self.general_category_templates_trees = {category: path_to_files + category + '/%s' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
        self.ttbar_category_templates_trees = {category: path_to_files + '/TTJets_PowhegPythia8_tree.root' for category, prefix in categories_and_prefixes.iteritems()}
        self.SingleTop_category_templates_trees = {category: path_to_files + '/SingleTop_tree.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.VJets_category_templates_trees = {category: path_to_files + '/VJets_tree.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.electron_QCD_MC_category_templates_trees = {category: path_to_files + '/QCD_Electron_tree.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.muon_QCD_MC_category_templates_trees = {category: path_to_files + '/QCD_Muon_tree.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.ttbar_generator_category_templates_trees = {category: path_to_files + '/TTJets_' + category + '_tree.root' for category in generator_mcsamples}
        
        self.ttbar_amc_category_templates_trees = path_to_files + '/TTJets_amc_tree.root'
        self.ttbar_madgraph_category_templates_trees = path_to_files + '/TTJets_madgraph_tree.root'
        self.ttbar_powhegpythia8_category_templates_trees = path_to_files + '/TTJets_powhegPythia8_tree.root'
        self.ttbar_powhegherwigpp_category_templates_trees = path_to_files + '/TTJets_powhegHerwigpp_tree.root'
        self.ttbar_amcatnloherwigpp_category_templates_trees = path_to_files + '/TTJets_amcatnloHerwigpp_tree.root'
        self.ttbar_scaleup_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_scaleup_tree.root'
        self.ttbar_scaledown_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_scaledown_tree.root'
        self.ttbar_mtop1695_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_mtop1695_tree.root'
        self.ttbar_mtop1755_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_mtop1755_tree.root'
        self.ttbar_jesup_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_plusJES_tree.root'
        self.ttbar_jesdown_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_minusJES_tree.root'
        self.ttbar_jerup_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_plusJER_tree.root'
        self.ttbar_jerdown_category_templates_trees = path_to_files + '/TTJets_PowhegPythia8_minusJER_tree.root'

        self.data_muon_category_templates = {
            'central': self.data_file_muon,
            'JES_up': self.data_file_muon,
            'JES_down': self.data_file_muon
        }
        self.data_muon_category_templates_trees = self.data_file_muon_trees

        self.data_electron_category_templates = {
            'central': self.data_file_electron,
            'JES_up': self.data_file_electron,
            'JES_down': self.data_file_electron,
        }
        self.data_electron_category_templates_trees = self.data_file_electron_trees

        # Unfolding MC Different Generator Samples
        self.unfolding_powheg_pythia8_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV.root' % self.centre_of_mass_energy
        self.unfolding_amcatnlo_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_amcatnlo.root' % self.centre_of_mass_energy
        self.unfolding_madgraphMLM_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_madgraph.root' % self.centre_of_mass_energy
        self.unfolding_powheg_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_powhegherwigpp.root' % self.centre_of_mass_energy
        self.unfolding_amcatnlo_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_amcatnloherwigpp.root' % self.centre_of_mass_energy

        # Choose central MC Sample
        self.unfolding_central_raw = self.unfolding_powheg_pythia8_raw

        # Raw --> asymmetric
        self.unfolding_powheg_pythia8 = self.unfolding_powheg_pythia8_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_amcatnlo = self.unfolding_amcatnlo_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_madgraphMLM = self.unfolding_madgraphMLM_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_powheg_herwig = self.unfolding_powheg_herwig_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_amcatnlo_herwig = self.unfolding_amcatnlo_herwig_raw.replace( '.root', '_asymmetric.root' )

        self.unfolding_central = self.unfolding_powheg_pythia8

        self.unfolding_ptreweight_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_withTopPtReweighting_up.root' % self.centre_of_mass_energy
        self.unfolding_ptreweight_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_withTopPtReweighting_down.root' % self.centre_of_mass_energy

        self.unfolding_scale_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_scaleDownWeight.root' % self.centre_of_mass_energy
        self.unfolding_scale_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_scaleUpWeight.root' % self.centre_of_mass_energy
        self.unfolding_matching_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_matchingdown.root' % self.centre_of_mass_energy
        self.unfolding_matching_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_matchingup.root' % self.centre_of_mass_energy

        self.unfolding_scale_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_alphaSDown.root' % self.centre_of_mass_energy
        self.unfolding_scale_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_alphaSUp.root' % self.centre_of_mass_energy

        # self.unfolding_scale_down = self.unfolding_scale_down_raw.replace( '_scaleDown', '_asymmetric_scaleDown' )
        # self.unfolding_scale_up = self.unfolding_scale_up_raw.replace( '_scaleUp', '_asymmetric_scaleUp' )
        self.unfolding_matching_down = self.unfolding_matching_down_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_matching_up = self.unfolding_matching_up_raw.replace( '.root', '_asymmetric.root' )

        self.unfolding_renormalisation_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_05muR1muF.root' % self.centre_of_mass_energy
        self.unfolding_renormalisation_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_2muR1muF.root' % self.centre_of_mass_energy
        self.unfolding_factorisation_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_1muR05muF.root' % self.centre_of_mass_energy
        self.unfolding_factorisation_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_1muR2muF.root' % self.centre_of_mass_energy
        self.unfolding_combined_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_05muR05muF.root' % self.centre_of_mass_energy
        self.unfolding_combined_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_2muR2muF.root' % self.centre_of_mass_energy
        self.unfolding_alphaS_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_alphaSDown.root' % self.centre_of_mass_energy
        self.unfolding_alphaS_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_alphaSUp.root' % self.centre_of_mass_energy

        self.unfolding_mass_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_massdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_mass_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_massup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_Lepton_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_leptondown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_Lepton_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_leptonup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_jes_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jesdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_jes_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jesup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_jer_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jerdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_jer_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jerup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_bjet_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_bjetdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_bjet_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_bjetup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_lightjet_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_lightjetdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_lightjet_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_lightjetup_asymmetric.root' % self.centre_of_mass_energy

        self.unfolding_ElectronEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ElectronEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_ElectronEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ElectronEnUp_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_MuonEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_MuonEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_MuonEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_MuonEnUp_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_TauEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_TauEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_TauEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_TauEnUp_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_UnclusteredEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_UnclusteredEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_UnclusteredEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_UnclusteredEnUp_asymmetric.root' % self.centre_of_mass_energy

        self.unfolding_PUSystematic_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_pileupUp_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_PUSystematic_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_pileupDown_asymmetric.root' % self.centre_of_mass_energy


        self.unfolding_pdfweights = {index : path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_pdfWeight_%d.root' % (self.centre_of_mass_energy, index) for index in range( 0, 100 )}

        self.tree_path_templates = {
            'electron' : 'TTbar_plus_X_analysis/EPlusJets/Ref selection/FitVariables',
            'muon' : 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/FitVariables'
        }

        self.tree_path_control_templates = {
            'electron' : 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/FitVariables',
            'muon' : 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets 3toInf/FitVariables'
        }

        self.variable_path_templates = {
            'MET' : 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/MET',
            'HT' : 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/HT',
            'ST': 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/ST',
            'MT': 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/MT',
            'WPT': 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/WPT',
            'NJets': 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/NJets',
            'lepton_pt': 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/lepton_pt',
            'lepton_eta': 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/lepton_eta',
            'abs_lepton_eta': 'TTbar_plus_X_analysis/{channel}/{selection}/FitVariables/absolute_eta',
            'bjets_pt': 'TTbar_plus_X_analysis/{channel}/{selection}/Jets/bjet_pt',
            'bjets_eta': 'TTbar_plus_X_analysis/{channel}/{selection}/Jets/bjet_eta',
            'abs_bjets_eta': 'TTbar_plus_X_analysis/{channel}/{selection}/Jets/abs(bjet_eta)',
        }

        self.electron_control_region = 'QCDConversions'
        self.electron_control_region_systematic = 'QCD non iso e+jets'

        self.muon_control_region = 'QCD non iso mu+jets 1p5to3'
        self.muon_control_region_systematic = 'QCD non iso mu+jets 3toInf'

        self.include_higgs = False

        self.luminosity_scale = self.new_luminosity / self.luminosity

        # structure
        # { summary_name : [(Electron_down, Electron_up)), (TTJets_hadronisation, TTJets_hadronisation)
        self.typical_systematics_summary = {
            'Lepton selection efficiency': [
                ('Electron_down', 'Electron_up'), 
                ('Muon_down', 'Muon_up')
            ],
            'Jet energy \& resolution': [
                ('JES_down', 'JES_up', 'JER_down', 'JER_up')
            ],
            'B-tagging' : [
                ('BJet_down', 'BJet_up'),
                ('LightJet_down', 'LightJet_up')
            ],
            '\met' : [
                ('ElectronEnDown', 'ElectronEnUp'), 
                ('MuonEnDown','MuonEnUp'),
                ('TauEnDown','TauEnUp'),
                ('UnclusteredEnDown','UnclusteredEnUp')
            ],
            'Background Normalisation (non-QCD)': [
                # ('TTJet_cross_section-', 'TTJet_cross_section+'),
                ('SingleTop_cross_section-', 'SingleTop_cross_section+'),
                ('luminosity-', 'luminosity+'),
            ],
            'QCD Normalisation': [
                ('QCD_cross_section-', 'QCD_cross_section+'),
            ],
            'QCD shape': [
                ('QCD_shape', 'QCD_shape')
            ],
            'Theory': [
                ('TTJets_scaledown', 'TTJets_scaleup'),
                ('TTJets_massdown', 'TTJets_massup')
            ],
            'Hadronisation': [
                ('TTJets_hadronisation', 'TTJets_hadronisation')
            ],
            'NLO generator': [
                ('TTJets_NLOgenerator', 'TTJets_NLOgenerator')
            ],
            'PDF': [
                ('PDF_total_lower', 'PDF_total_upper')
            ],
            'Pileup' : [
                ('PileUpSystematic','PileUpSystematic')
            ],
        }
        self.typical_systematics = []
        for _, values in self.typical_systematics_summary.items():
            for tuple in values:
                if tuple[0] == tuple[1]:
                    self.typical_systematics.append(tuple[0])
                else:
                    self.typical_systematics.extend(tuple)


    def __fill_defaults_13TeV__( self ):
        middle = self.middle
        path_to_files = self.path_to_files

        self.new_luminosity = 12835
        self.ttbar_xsection = 831.76  # pb

        self.rate_changing_systematics = {#TODO check where this is used
            'luminosity': 0.027,  # Best guess for 13 TeV 4.8->2.7
            'SingleTop_cross_section': 0.05,  # Currently same as 8 TeV
            # 'TTJet_cross_section': 0.043, # Currently same as 8 TeV
            'V+Jets_cross_section': 0.5,
            'QCD_cross_section' : 1.,
         }

        self.tau_values_electron = {
            "NJets" : 7.14289851984e-05,
            "WPT" : 0.00412403632721,
            "lepton_pt" : 0.0018054271566,
            "abs_lepton_eta" : 9.24702326429e-06,
            "ST" : 0.00831765143666,
            "MET" : 0.00256015359682,
            "HT" : 0.00602254137204,
            'bjets_pt': 0.,
            'bjets_eta': 0.,
            'lepton_eta': 0.,
            'abs_lepton_eta':0.,
            "hadTopRap" : 10.0,
            "lepTopPt" : 53.3669923121,
            "hadTopPt" : 58.5702081806,
            "ttbarPt" : 27.8255940221,
            "ttbarM" : 21.0490414451,
            "lepTopRap" : 10.0,
            "ttbarRap" : 93.2603346883,
           }

        self.tau_values_muon = {
            "NJets" : 8.00904290212e-05,
            "WPT" : 0.00475761126845,
            "lepton_pt" : 0.00242164061853,
            "abs_lepton_eta" : 9.61561880023e-06,
            "ST" : 0.00972730152042,
            "MET" : 0.00290173731922,
            "HT" : 0.00740965179358,
            'bjets_pt': 0.,
            'bjets_eta': 0.,
            'lepton_eta': 0.,
            'abs_lepton_eta':0.,
            "hadTopRap" : 10.0,
            "lepTopPt" : 546.227721768,
            "hadTopPt" : 453.487850813,
            "ttbarPt" : 312.571584969,
            "ttbarM" : 196.304065004,
            "lepTopRap" : 10.0,
            "ttbarRap" : 236.448941265,
        }

        self.tau_values_combined = {
            "WPT" : 0.00322241847459,
            "NJets" : 5.37441937171e-05,
            "lepton_pt" : 0.000939525715364,
            "HT" : 0.00394515055942,
            "ST" : 0.00621522525829,
            "MET" : 0.00188739860157,
            "abs_lepton_eta" : 4.55639578634e-06,

            'bjets_pt': 0.,
            'bjets_eta': 0.,
            'lepton_eta': 0.,
            'abs_lepton_eta':0.,
            "hadTopRap" : 10.0,
            "lepTopPt" : 53.3669923121,
            "hadTopPt" : 58.5702081806,
            "ttbarPt" : 27.8255940221,
            "ttbarM" : 21.0490414451,
            "lepTopRap" : 10.0,
            "ttbarRap" : 93.2603346883,
           }

        # self.categories_and_prefixes['PU_down'] = '_PU_65835mb'
        # self.categories_and_prefixes['PU_up'] = '_PU_72765mb'

        self.special_muon_histogram = 'muon_AbsEta_0btag'
