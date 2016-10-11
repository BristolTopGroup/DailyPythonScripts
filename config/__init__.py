from __future__ import division
import tools.measurement

__all__ = [
    'XSectionConfig',
]

class XSectionConfig():
    current_analysis_path = '/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_8th_draft/'
    known_centre_of_mass_energies = [7, 8]
    # has to be separate as many variables depend on it
    luminosities = {7:5050, 8:19584}
    parameters = ['SingleTop_category_templates', 'SingleTop_file',
                  'VJets_category_templates', 'analysis_types',
                  'categories_and_prefixes', 'central_general_template',
                  'centre_of_mass_energy', 'current_analysis_path',
                  'data_file_electron', 'data_file_muon',
                  'data_muon_category_templates', 'electron_QCD_MC_file',
                  'electron_control_region',
                  'electron_control_region_systematic',
                  'fit_boundaries',
                  'fit_variable_bin_width',
                  'fit_variable_unit',
                  'general_category_templates',
                  'generator_systematic_vjets_templates',
                  'generator_systematics',
                  'higgs_category_templates', 'higgs_file',
                  'histogram_path_templates', 'include_higgs',
                  'k_values_combined', 'k_values_electron', 'k_values_muon',
                  'known_centre_of_mass_energies', 'luminosities',
                  'luminosity', 'luminosity_scale', 'met_systematics_suffixes',
                  'muon_QCD_MC_category_templates', 'muon_QCD_MC_file',
                  'muon_QCD_file', 'muon_control_region',
                  'muon_control_region_systematic', 'new_luminosity',
                  'parameters', 'path_to_files', 'path_to_unfolding_histograms',
                  'rate_changing_systematics',
                  'rebin', 'special_muon_histogram', 'translate_options',
                  'ttbar_category_templates',
                  'ttbar_theory_systematic_prefix', 'ttbar_xsection',
                  'unfolding_madgraph', 'unfolding_madgraph_raw',
                  'unfolding_matching_down', 'unfolding_matching_down_raw',
                  'unfolding_matching_up', 'unfolding_matching_up_raw',
                  'unfolding_mass_down', 'unfolding_mass_up',
                  'unfolding_mcatnlo', 'unfolding_mcatnlo_raw',
                  'unfolding_powheg_v2_pythia', 'unfolding_powheg_v2_pythia_raw',
                  'unfolding_powheg_v1_herwig', 'unfolding_powheg_v1_herwig_raw',
                  'unfolding_powheg_v2_herwig', 'unfolding_powheg_v2_herwig_raw',
                  'unfolding_scale_down', 'unfolding_scale_down_raw',
                  'unfolding_scale_up', 'unfolding_scale_up_raw',
                  'unfolding_ptreweight', 'unfolding_ptreweight_raw',
                  'unfolding_pdfweights',
                  'vjets_theory_systematic_prefix'
                  ]
    samples = ['TTJet', 'V+Jets', 'SingleTop', 'QCD']

    def __init__( self, centre_of_mass_energy ):
        if not centre_of_mass_energy in self.known_centre_of_mass_energies:
            raise AttributeError( 'Unknown centre of mass energy' )
        self.centre_of_mass_energy = centre_of_mass_energy
        self.__fill_defaults__()

    def __fill_defaults__( self ):
        self.path_to_files = self.current_analysis_path + str( self.centre_of_mass_energy ) + 'TeV/'
        self.path_to_unfolding_histograms = self.path_to_files + 'unfolding/'
        path_to_files = self.path_to_files
        path_to_unfolding_histograms = self.path_to_unfolding_histograms

        self.luminosity = self.luminosities[self.centre_of_mass_energy]

        # general
        self.met_systematics_suffixes = [
                                         "ElectronEnUp",
                                         "ElectronEnDown",
                                         "MuonEnUp",
                                         "MuonEnDown",
                                         "TauEnUp",
                                         "TauEnDown",
                                         "JetResUp",
                                         "JetResDown",
                                         "JetEnUp",
                                         "JetEnDown",
                                         "UnclusteredEnUp",
                                         "UnclusteredEnDown"
                                        ]

        self.analysis_types = {
                'electron':'EPlusJets',
                'muon':'MuPlusJets'
                }

        # measurement script options
        self.translate_options = {
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

        self.data_file_muon = path_to_files + 'central/SingleMu' + middle + '.root'
        self.muon_QCD_file = path_to_files + 'QCD_data_mu.root'
        self.SingleTop_file = path_to_files + 'central/SingleTop' + middle + '.root'
        self.electron_QCD_MC_file = path_to_files + 'central/QCD_Electron' + middle + '.root'
        self.muon_QCD_MC_file = path_to_files + 'central/QCD_Muon' + middle + '.root'
        self.higgs_file = path_to_files + 'central/TTH_Inclusive_M-125' + middle + '.root'

        self.categories_and_prefixes = {
                 'central':'',
                 'Electron_down':'_minusElectron',
                 'Electron_up':'_plusElectron',
                 'Muon_down':'_minusMuon',
                 'Muon_up':'_plusMuon',
                 'BJet_down':'_minusBJet',
                 'BJet_up':'_plusBjet',
                 'JES_down':'_minusJES',
                 'JES_up':'_plusJES',
                 'JER_down':'_minusJER',
                 'JER_up':'_plusJER',
                 'LightJet_down':'_minusLightJet',
                 'LightJet_up':'_plusLightJet',
                 }

        # now fill in the centre of mass dependent values
        # this position is crucial
        if self.centre_of_mass_energy == 7:
            self.__fill_defaults_7TeV__()
        if self.centre_of_mass_energy == 8:
            self.__fill_defaults_8TeV__()

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
            sp = tools.measurement.Systematic( systematic + '+', stype = tools.measurement.Systematic.RATE,
                            affected_samples = affected_samples,
                            scale = 1 + self.rate_changing_systematics[systematic] )
            sm = tools.measurement.Systematic( systematic + '-', stype = tools.measurement.Systematic.RATE,
                            affected_samples = affected_samples,
                            scale = 1 - self.rate_changing_systematics[systematic] )
            self.rate_changing_systematics_values[sp.name] = sp
            self.rate_changing_systematics_values[sm.name] = sm
        self.rate_changing_systematics_names = self.rate_changing_systematics_values.keys()

        self.k_values = {
                         'electron' : self.k_values_electron,
                         'muon' : self.k_values_muon,
                         }
        self.generator_systematics = [ 'matchingup', 'matchingdown', 'scaleup', 'scaledown' ]
        self.topMass_systematics = [ 'TTJets_massup', 'TTJets_massdown']
        self.topMasses = [169.5, 172.5, 173.5]
        self.topMassUncertainty = 1.0 # GeV from https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO
        self.central_general_template = path_to_files + 'central/%s' + middle + '.root'
        self.generator_systematic_vjets_templates = { systematic: path_to_files + 'central/VJets-%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % ( systematic, self.luminosity ) for systematic in self.generator_systematics}

        self.kValueSystematic = [ 'kValue_up', 'kValue_down']

        categories_and_prefixes = self.categories_and_prefixes

        self.general_category_templates = {category: path_to_files + category + '/%s' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
        self.ttbar_category_templates = {category: path_to_files + category + '/TTJet' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
        self.SingleTop_category_templates = {category: path_to_files + category + '/SingleTop' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.VJets_category_templates = {category: path_to_files + category + '/VJets' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.higgs_category_templates = {category: path_to_files + category + '/TTH_Inclusive_M-125' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.electron_QCD_MC_category_templates = {category: path_to_files + category + '/QCD_Electron' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
        self.muon_QCD_MC_category_templates = {category: path_to_files + category + '/QCD_Muon' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}

        self.data_muon_category_templates = {
                                    'central': self.data_file_muon,
                                    'JES_up': self.data_file_muon,
                                    'JES_down': self.data_file_muon
                                    }

        self.unfolding_madgraph_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV.root' % self.centre_of_mass_energy
        self.unfolding_powheg_v1_pythia_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_powhegV1pythia.root' % self.centre_of_mass_energy
        self.unfolding_powheg_v2_pythia_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_powhegV2pythia.root' % self.centre_of_mass_energy
        self.unfolding_powheg_v1_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_powhegV1herwig.root' % self.centre_of_mass_energy
        self.unfolding_powheg_v2_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_powhegV2herwig.root' % self.centre_of_mass_energy
        self.unfolding_mcatnlo_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_mcatnlo.root' % self.centre_of_mass_energy
        self.unfolding_ptreweight_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_withTopPtReweighting.root' % self.centre_of_mass_energy

        self.unfolding_scale_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_scaledown.root' % self.centre_of_mass_energy
        self.unfolding_scale_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_scaleup.root' % self.centre_of_mass_energy
        self.unfolding_matching_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_matchingdown.root' % self.centre_of_mass_energy
        self.unfolding_matching_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_matchingup.root' % self.centre_of_mass_energy

        self.unfolding_madgraph = self.unfolding_madgraph_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_powheg_v1_pythia = self.unfolding_powheg_v1_pythia_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_powheg_v2_pythia = self.unfolding_powheg_v2_pythia_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_powheg_v1_herwig = self.unfolding_powheg_v1_herwig_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_powheg_v2_herwig = self.unfolding_powheg_v2_herwig_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_mcatnlo = self.unfolding_mcatnlo_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_ptreweight = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_withTopPtReweighting.root' % self.centre_of_mass_energy

        self.unfolding_scale_down = self.unfolding_scale_down_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_scale_up = self.unfolding_scale_up_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_matching_down = self.unfolding_matching_down_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_matching_up = self.unfolding_matching_up_raw.replace( '.root', '_asymmetric.root' )
        self.unfolding_mass_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_massdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_mass_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_massup_asymmetric.root' % self.centre_of_mass_energy

        self.unfolding_pdfweights = {index : path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_pdfWeight_%d.root' % (self.centre_of_mass_energy, index) for index in range( 1, 46 )}

        self.histogram_path_templates = {
                           'MET' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MET_Analysis/%s_bin_%s/%s',
                           'HT' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_HT_Analysis/HT_bin_%s/%s',
                           'ST': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/%s',
                           'MT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/%s',
                           'WPT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_WPT_Analysis/WPT_with_%s_bin_%s/%s'
                           }
        
        #folder_template = '{path}/normalisation/{method}/{CoM}TeV/{variable}/{category}/'
        self.variable_path_templates = {
                           'MET' : 'TTbar_plus_X_analysis/{channel}/{selection}/MET/{met_type}/MET_{btag}',
                           'HT' : 'TTbar_plus_X_analysis/{channel}/{selection}/MET/HT_{btag}',
                           'ST': 'TTbar_plus_X_analysis/{channel}/{selection}/MET/{met_type}/ST_{btag}',
                           'MT': 'TTbar_plus_X_analysis/{channel}/{selection}/MET/{met_type}/MT_{btag}',
                           'WPT': 'TTbar_plus_X_analysis/{channel}/{selection}/MET/{met_type}/WPT_{btag}',
                            }

        self.electron_control_region = 'QCDConversions'
        self.electron_control_region_systematic = 'QCD non iso e+jets'

        self.muon_control_region = 'QCD non iso mu+jets ge3j'
        self.muon_control_region_systematic = 'QCD non iso mu+jets ge3j'  # no systematic yet

        self.include_higgs = False

        self.luminosity_scale = self.new_luminosity / self.luminosity
        
        self.typical_systematics = {
                                      "typical_systematics_electron": ['Electron_down',
                                                          'Electron_up'],
                         "typical_systematics_muon": ['Muon_down',
                                                       'Muon_up'],
                         "typical_systematics_btagging": ['BJet_down',
                                                           'BJet_up'],
                         "typical_systematics_JES": ['JES_down',
                                                      'JES_up'],
                         "typical_systematics_JER": ['JER_down',
                                                      'JER_up'],
                         "typical_systematics_PU": ['PU_down',
                                                     'PU_up'],
                        "typical_systematics_hadronisation": ['hadronisation'],
                        "typical_systematics_QCD_shape": ['QCD_shape'],
                         "typical_systematics_PDF": ['PDF_total_lower',
                                                      'PDF_total_upper'],
                         "typical_systematics_top_mass": ['TTJets_massdown',
                                                           'TTJets_massup'],
                         "typical_systematics_background_other": ["TTJet_cross_section+",
                                                                   "TTJet_cross_section-",
                                                                   "SingleTop_cross_section+",
                                                                   "SingleTop_cross_section-",
                                                                   "V+Jets_cross_section+",                                                                   
                                                                   "V+Jets_cross_section-",
                                                                   "QCD_cross_section+",
                                                                   "QCD_cross_section-",
                                                                   "luminosity+",
                                                                   "luminosity-"],
                        "typical_systematics_theoretical": ["TTJets_matchingup",
                                                             "TTJets_matchingdown",
                                                             "VJets_matchingup",
                                                             'VJets_matchingdown',
                                                             "TTJets_scaleup",
                                                             "TTJets_scaledown",
                                                             "VJets_scaleup",
                                                             "VJets_scaledown"],
                        "typical_systematics_MET": ["patType1CorrectedPFMetElectronEnUp",
                                                     "patType1CorrectedPFMetElectronEnDown",
                                                     "patType1CorrectedPFMetMuonEnUp",
                                                     "patType1CorrectedPFMetMuonEnDown",
                                                     "patType1CorrectedPFMetTauEnUp",
                                                     "patType1CorrectedPFMetTauEnDown",
                                                     "patType1CorrectedPFMetUnclusteredEnUp",
                                                     "patType1CorrectedPFMetUnclusteredEnDown"],
                        "typical_systematics_pt_reweight": ['ptreweight_max']
                       }

    def __fill_defaults_7TeV__( self ):
        middle = self.middle
        path_to_files = self.path_to_files

        self.new_luminosity = 5050  # pb^-1
        self.ttbar_xsection = 177.31 # pb from https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO

        self.data_file_electron = path_to_files + 'central/ElectronHad' + middle + '.root'
        self.rate_changing_systematics = {
                        'luminosity': 0.022,  # https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupSystematicErrors
                        'SingleTop_cross_section': 0.3,
                        'TTJet_cross_section': 0.15,
                        'V+Jets_cross_section': 0.3,
                        'QCD_cross_section' : 1.,
                         }

        # optimal regularisation parameters
        self.k_values_electron = {
                   'MET' : 2,
                   'HT' : 3,
                   'ST' : 3,
                   'MT' : 2,
                   'WPT' : 3
                   }

        self.k_values_muon = {
                   'MET' : 2,
                   'HT' : 3,
                   'ST' : 3,
                   'MT' : 2,
                   'WPT' : 3
                   }
        #keeping combined values for backward compatibility
        self.k_values_combined = {
                   'MET' : 0,
                   'HT' : 0,
                   'ST' : 0,
                   'MT' : 0,
                   'WPT' : 0
                   }

        self.tau_values_electron = {
        }

        self.tau_values_muon = {
        }

        self.categories_and_prefixes['PU_down'] = '_PU_64600mb'
        self.categories_and_prefixes['PU_up'] = '_PU_71400mb'

        self.special_muon_histogram = 'etaAbs_ge2j_data'

        self.data_electron_category_templates = {'central': self.data_file_electron,
                                    'JES_up': self.data_file_electron,
                                    'JES_down': self.data_file_electron
                                    }

    def __fill_defaults_8TeV__( self ):
        middle = self.middle
        path_to_files = self.path_to_files

        self.new_luminosity = 19712  # pb^-1
        self.ttbar_xsection = 252.89 # pb from https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO

        self.data_file_electron = path_to_files + 'central/SingleElectron' + middle + '.root'
        self.rate_changing_systematics = {
                        'luminosity': 0.026,  # https://hypernews.cern.ch/HyperNews/CMS/get/physics-announcements/2526.html
                        'SingleTop_cross_section': 0.034,  # https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat8TeV
                        'TTJet_cross_section': 0.043,
                        'V+Jets_cross_section': 0.3,
                        'QCD_cross_section' : 1.,
                         }

        # optimal regularisation parameters
        self.k_values_electron = {
                   'MET' : 3,
                   'HT' : 3,
                   'ST' : 4,
                   'MT' : 2,
                   'WPT' : 3
                   }

        self.k_values_muon = {
                   'MET' : 3,
                   'HT' : 3,
                   'ST' : 4,
                   'MT' : 2,
                   'WPT' : 3
                   }
        #keeping combined values for backward compatibility
        self.k_values_combined = {
                   'MET' : 0,
                   'HT' : 0,
                   'ST' : 0,
                   'MT' : 0,
                   'WPT' : 0
                   }

        self.tau_values_electron = {
        }

        self.tau_values_muon = {
        }

        self.categories_and_prefixes['PU_down'] = '_PU_65835mb'
        self.categories_and_prefixes['PU_up'] = '_PU_72765mb'

        self.special_muon_histogram = 'muon_AbsEta_0btag'

        self.data_electron_category_templates = {'central': self.data_file_electron,
                                    'JES_up': path_to_files + 'JES_up/SingleElectron' + middle + self.categories_and_prefixes['JES_up'] + '.root',
                                    'JES_down': path_to_files + 'JES_down/SingleElectron' + middle + self.categories_and_prefixes['JES_down'] + '.root'
                                    }

fit_var_inputs = [
                  'absolute_eta', 'M3', 
# 'M_bl', 
                  'angle_bl',
                      # 'absolute_eta_angle_bl',
                      # 'absolute_eta_M3',
                      # 'absolute_eta_M_bl',
                      # 'absolute_eta_M_bl_angle_bl',
                      'absolute_eta_M3_angle_bl',
                      # 'absolute_eta_M_bl_M3',
                      # 'absolute_eta_M_bl_M3_angle_bl'
                       ]
