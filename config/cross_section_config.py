from __future__ import division
import tools.measurement

class XSectionConfig():
    current_analysis_path = '/hdfs/TopQuarkGroup/run2/atOutput/'
    known_centre_of_mass_energies = [13]
    # has to be separate as many variables depend on it
    luminosities = {13:2172}

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
        'higgs_category_templates', 'higgs_file',
        'include_higgs',
        'k_values_combined', 'k_values_electron', 'k_values_muon',
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
        if self.centre_of_mass_energy != 13:
            self.current_analysis_path = '/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_7th_draft/'
            self.path_to_files = self.current_analysis_path + str( self.centre_of_mass_energy ) + 'TeV/'
            self.path_to_unfolding_histograms = self.path_to_files + 'unfolding/'
        else:
            self.path_to_files = self.current_analysis_path + str( self.centre_of_mass_energy ) + 'TeV/25ns/'
            self.path_to_unfolding_histograms = '/hdfs/TopQuarkGroup/run2/unfolding/13TeV/25ns/15_02_16/'

        path_to_files = self.path_to_files
        path_to_unfolding_histograms = self.path_to_unfolding_histograms

        self.luminosity = self.luminosities[self.centre_of_mass_energy]

        # general
        self.met_systematics = {
            'ElectronEnUp' : 6,
            'ElectronEnDown' : 7,
            'MuonEnUp' : 4,
            'MuonEnDown' : 5,
            'TauEnUp' : 8,
            'TauEnDown' : 9,
            'JER_up' : 0,
            'JER_down' : 1,
            'JES_up' : 2,
            'JES_down' : 3,
            'UnclusteredEnUp' : 10,
            'UnclusteredEnDown' : 11,
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

        self.fit_boundaries = {
           'absolute_eta' : ( 0., 2.4 ),
           'M3' : ( 0, 900 ),
           'M_bl' : ( 0, 400 ),
           'angle_bl' : ( 0, 4 ),
       }

        # dependent on rebin
        self.fit_variable_bin_width = {
            'absolute_eta' : 0.2,
            'M3' : 20,
            'M_bl' : 10,
            'angle_bl' : 0.2,
        }

        # relates to fit_variable_bin_width
        self.rebin = {
            'absolute_eta' : 2, # 2 -> 0.2
            'M3' : 5, # 5 -> 25 GeV
            'M_bl' : 4, # 2 -> 20 GeV
            'angle_bl' : 2, # 2 -> 0.2
        }

        self.fit_variable_unit = {
            'absolute_eta' : '',
            'M3' : 'GeV',
            'M_bl' : 'GeV',
            'angle_bl' : '',
        }

        self.ttbar_theory_systematic_prefix = 'TTJets_'
        self.vjets_theory_systematic_prefix = 'VJets_'
        # files
        self.middle = '_' + str( self.luminosity ) + 'pb_PFElectron_PFMuon_PF2PATJets_PFMET'
        middle = self.middle

        self.data_file_muon = path_to_files + 'data_muon_tree.root'
        self.data_file_electron = path_to_files + 'data_electron_tree.root'

        self.data_file_muon_trees = path_to_files + 'data_muon_tree.root'
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
            'JES_down':'_JESDown',
            'JES_up':'_JESUp',
            # 'JES_down_alphaCorr':'_JESDown_alphaCorr',
            # 'JES_up_alphaCorr':'_JESUp_alphaCorr',
            'JER_down':'_JERDown',
            'JER_up':'_JERUp',
            # 'LightJet_down':'_minusLightJet',
            # 'LightJet_up':'_plusLightJet',

            'PileUpSystematic' : '',

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

        self.met_systematics_suffixes = self.met_systematics.keys()

        # now fill in the centre of mass dependent values
        self.__fill_defaults_13TeV__()

        self.generator_systematics = [ 
            # 'matchingup', 'matchingdown', 
            'scaleup', 'scaledown',
            'massup', 'massdown',
            'hadronisation',
            'NLOgenerator'
        ]

        self.k_values = {
            'electron' : self.k_values_electron,
            'muon' : self.k_values_muon,
        }

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
                        stype = tools.measurement.Systematic.RATE,
                        affected_samples = affected_samples,
                        scale = 1 + self.rate_changing_systematics[systematic],
                        )
            scale = 1 - self.rate_changing_systematics[systematic]
            if scale <= 0: scale = 10e-5

            sm = tools.measurement.Systematic( 
                        systematic + '-',
                        stype = tools.measurement.Systematic.RATE,
                        affected_samples = affected_samples,
                        scale = scale,
                        )
            self.rate_changing_systematics_values[sp.name] = sp
            self.rate_changing_systematics_values[sm.name] = sm

        self.rate_changing_systematics_names = self.rate_changing_systematics_values.keys()

        self.topMass_systematics = [ 'TTJets_massup', 'TTJets_massdown']
        self.topMasses = [169.5, 172.5, 173.5]
        self.topMassUncertainty = 1.0 # GeV from https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO

        self.central_general_template = path_to_files + 'central/%s' + middle + '.root'
        self.generator_systematic_vjets_templates = {}
        for systematic in self.generator_systematics:
            if 'mass' in systematic or 'hadronisation' in systematic or 'NLOgenerator' in systematic:
                continue
            tmp = path_to_files + 'central/VJets-{0}_{1}pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
            tmp = tmp.format(systematic, self.luminosity)
            self.generator_systematic_vjets_templates[systematic] = tmp

        self.kValueSystematic = [ 'kValue_up', 'kValue_down']

        categories_and_prefixes = self.categories_and_prefixes

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
        
        self.ttbar_amc_category_templates_trees = path_to_files + '/TTJets_amc_tree.root'
        self.ttbar_madgraph_category_templates_trees = path_to_files + '/TTJets_madgraph_tree.root'
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
        self.unfolding_powheg_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_herwigpp.root' % self.centre_of_mass_energy
        self.unfolding_amcatnlo_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_herwigpp.root' % self.centre_of_mass_energy

        # Choose central MC Sample
        self.unfolding_central_raw = self.unfolding_powheg_pythia8_raw

        # Raw --> asymmetric
        self.unfolding_powheg_pythia8 = self.unfolding_powheg_pythia8_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_amcatnlo = self.unfolding_amcatnlo_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_madgraphMLM = self.unfolding_madgraphMLM_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_powheg_herwig = self.unfolding_powheg_herwig_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_amcatnlo_herwig = self.unfolding_amcatnlo_herwig_raw.replace( '.root', '_asymmetric.root' )

        self.unfolding_central = self.unfolding_powheg_pythia8

        self.unfolding_scale_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_scaleDownWeight.root' % self.centre_of_mass_energy
        self.unfolding_scale_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_scaleUpWeight.root' % self.centre_of_mass_energy
        self.unfolding_matching_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_matchingdown.root' % self.centre_of_mass_energy
        self.unfolding_matching_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_matchingup.root' % self.centre_of_mass_energy

        self.unfolding_scale_down = self.unfolding_scale_down_raw.replace( '_scaleDown', '_asymmetric_scaleDown' )
        self.unfolding_scale_up = self.unfolding_scale_up_raw.replace( '_scaleUp', '_asymmetric_scaleUp' )
        self.unfolding_matching_down = self.unfolding_matching_down_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_matching_up = self.unfolding_matching_up_raw.replace( '.root', '_asymmetric.root' )


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

        self.unfolding_ElectronEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ElectronEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_ElectronEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ElectronEnUp_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_MuonEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_MuonEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_MuonEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_MuonEnUp_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_TauEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_TauEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_TauEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_TauEnUp_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_UnclusteredEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_UnclusteredEnDown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_UnclusteredEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_UnclusteredEnUp_asymmetric.root' % self.centre_of_mass_energy

        self.unfolding_PUSystematic = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_pileupSystematic_asymmetric.root' % self.centre_of_mass_energy


        self.unfolding_pdfweights = {index : path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_generatorWeight_%d.root' % (self.centre_of_mass_energy, index) for index in range( 9, 109 )}

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
                ('BJet_down', 'BJet_up')
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

        self.new_luminosity = 2172. 
        self.ttbar_xsection = 831.76  # pb

        self.rate_changing_systematics = {#TODO check where this is used
            'luminosity': 0.027,  # Best guess for 13 TeV 4.8->2.7

            'SingleTop_cross_section': 0.05,  # Currently same as 8 TeV
            # 'TTJet_cross_section': 0.043, # Currently same as 8 TeV
            'V+Jets_cross_section': 0.5,
            'QCD_cross_section' : 1.,
         }

        # optimal regularisation parameters
        self.k_values_electron = {
                   'MET' : 3,
                   'HT' : 3,
                   'ST' : 4,
                   'MT' : 2,
                   'WPT' : 3,
                   'lepTopPt' : 2,
                   'lepTopRap' : 2,
                   'hadTopPt' : 2,
                   'hadTopRap' : 2,
                   'ttbarPt' : 2,
                   'ttbarRap' : 2,
                   'ttbarM' : 2,
                   'NJets' : 2,
                   'bjets_pt': 2,
                   'bjets_eta': 2,
                   'lepton_pt': 2,
                   'lepton_eta': 2,
                   'abs_lepton_eta': 2,
                   }

        self.k_values_muon = {
                   'MET' : 3,
                   'HT' : 3,
                   'ST' : 4,
                   'MT' : 2,
                   'WPT' : 3,
                   'lepTopPt' : 1,
                   'lepTopRap' : 1,
                   'hadTopPt' : 1,
                   'hadTopRap' : 1,
                   'ttbarPt' : 1,
                   'ttbarRap' : 1,
                   'ttbarM' : 1,
                   'NJets' : 2,
                   'bjets_pt': 2,
                   'bjets_eta': 2,
                   'lepton_pt': 2,
                   'lepton_eta': 2,
                   'abs_lepton_eta': 2,
                   }
        #keeping combined values for backward compatibility
        self.k_values_combined = {
                   'MET' : 0,
                   'HT' : 0,
                   'ST' : 0,
                   'MT' : 0,
                   'WPT' : 0,
                   'lepTopPt' : 1,
                   'lepTopRap' : 1,
                   'hadTopPt' : 1,
                   'hadTopRap' : 1,
                   'ttbarPt' : 1,
                   'ttbarRap' : 1,
                   'ttbarM' : 1,
                   'NJets' : 2,
                   'bjets_pt': 2,
                   'bjets_eta': 2,
                   'lepton_pt': 2,
                   'lepton_eta': 2,
                   }

        self.tau_values_electron = {
"NJets" : 7.01709784152e-05,
"WPT" : 0.00405221546909,
"lepton_pt" : 0.0018018584057,
"abs_lepton_eta" : 9.04882514124e-06,
"ST" : 0.00819214840909,
"MET" : 0.00251365428441,
"HT" : 0.00598912536223,
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
"NJets" : 7.80818061768e-05,
"WPT" : 0.00456749598096,
"lepton_pt" : 0.0023203738699,
"abs_lepton_eta" : 9.34057573916e-06,
"ST" : 0.00949131291812,
"MET" : 0.0027781136603,
"HT" : 0.00723438444419,
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
"NJets" : 5.25335153942e-05,
"WPT" : 0.00305416528307,
"lepton_pt" : 0.00144311408625,
"abs_lepton_eta" : 6.65419197707e-06,
"ST" : 0.00626425547204,
"MET" : 0.000143301257024,
"HT" : 0.00468724990318,



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

fit_var_inputs = ['absolute_eta', 'M3', 'M_bl', 'angle_bl',
    'absolute_eta_angle_bl',
    'absolute_eta_M3',
    'absolute_eta_M_bl',
    'absolute_eta_M_bl_angle_bl',
    'absolute_eta_M3_angle_bl',
    'absolute_eta_M_bl_M3',
    'absolute_eta_M_bl_M3_angle_bl' 
]
