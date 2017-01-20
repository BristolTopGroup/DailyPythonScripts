from __future__ import division
import dps.utils.measurement

class XSectionConfig():
    current_analysis_path = '/hdfs/TopQuarkGroup/ec6821/1.0.0/atOutput/combined/'
    known_centre_of_mass_energies = [13]
    # has to be separate as many variables depend on it
    luminosities = {13:36459}

    parameters = [
        'SingleTop_trees', 'SingleTop_file',
        'VJets_trees', 'analysis_types',
        'categories_and_prefixes', 'central_general_template',
        'centre_of_mass_energy', 'current_analysis_path',
        'data_file_electron', 'data_file_muon',
        'general_trees', 'higgs_file', 'include_higgs',
        'tau_values_electron', 'tau_values_muon', 'tau_values_combined',
        'known_centre_of_mass_energies', 'luminosities',
        'luminosity', 'new_luminosity',
        'luminosity_scale', 'met_systematics',
        'parameters', 'path_to_files', 'path_to_unfolding_histograms',
        'rate_changing_systematics',
        'translate_options',
        'ttbar_trees',
        'ttbar_theory_systematic_prefix', 'ttbar_xsection',
        'unfolding_central', 'unfolding_central_raw',
        'unfolding_powheg_pythia8', 'unfolding_powheg_pythia8_raw',
        'unfolding_amcatnlo', 'unfolding_amcatnlo_raw', 
        'unfolding_madgraphMLM', 'unfolding_madgraphMLM_raw',
        'unfolding_matching_down', 'unfolding_matching_down_raw',
        'unfolding_matching_up', 'unfolding_matching_up_raw',
        'unfolding_mass_down', 'unfolding_mass_up',
        'unfolding_powheg_herwig', 'unfolding_powheg_herwig_raw',
        'unfolding_pdfweights',
        'vjets_theory_systematic_prefix'
    ]
    
    # Used in 01
    samples = [
        'data',
        'TTBar', 
        'V+Jets', 
        'SingleTop', 
        'QCD'
    ]

    # Used in 01
    variables = [
        'HT',
        'MET',
        'ST',
        'WPT',
        'NJets',
        'lepton_pt',
        'abs_lepton_eta'
    ]

    # Used in 01
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

        self.path_to_files = self.current_analysis_path
        path_to_files = self.path_to_files

        self.path_to_unfolding_histograms = '/hdfs/TopQuarkGroup/run2/unfolding/13TeV/Moriond2017/'
        # self.path_to_unfolding_histograms = 'unfolding/13TeV/'
        path_to_unfolding_histograms = self.path_to_unfolding_histograms

        self.luminosity = self.luminosities[self.centre_of_mass_energy]

        # Used in 01
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
        }

        # Remove?
        self.met_systematics_suffixes = self.met_systematics.keys()

        # Used in 01 - combine with self.met_systematics?
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


        self.analysis_types = {
            'electron'  : 'EPlusJets',
            'muon'      : 'MuPlusJets',
            'combined'  : 'combined',
        }

        # Needed? Where?
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

        # Needed?
        self.ttbar_theory_systematic_prefix = 'TTJets_'
        self.vjets_theory_systematic_prefix = 'VJets_'
        # files
        self.middle = '_' + str( self.luminosity ) + 'pb_PFElectron_PFMuon_PF2PATJets_PFMET'
        middle = self.middle

        # self.data_file_muon = path_to_files + 'data_muon_tree.root'
        # self.data_file_electron = path_to_files + 'data_electron_tree.root'
        self.data_file_muon = '/hdfs/TopQuarkGroup/ec6821/1.0.0/atOutput/combined/data_muon_tree.root'
        self.data_file_electron = '/hdfs/TopQuarkGroup/ec6821/1.0.0/atOutput/combined/data_electron_tree.root'

        self.higgs_file = path_to_files + 'central/TTH_Inclusive_M-125' + middle + '.root'

        # self.categories_and_prefixes = {
        #     'central':'',
        #     'Electron_down':'ElectronDown',
        #     'Electron_up':'ElectronUp',
        #     'Muon_down':'MuonDown',
        #     'Muon_up':'MuonUp',
        #     'BJet_down':'BJetDown',
        #     'BJet_up':'BJetUp',
        #     'LightJet_down':'LightJetDown',
        #     'LightJet_up':'LightJetUp',
        #     'JES_down':'_JESDown',
        #     'JES_up':'_JESUp',
        #     # 'JES_down_alphaCorr':'_JESDown_alphaCorr',
        #     # 'JES_up_alphaCorr':'_JESUp_alphaCorr',
        #     'JER_down':'_JERDown',
        #     'JER_up':'_JERUp',

        #     'PileUp_up' : '',
        #     'PileUp_down' : '',

        #     # Other MET uncertainties not already included
        #     'ElectronEnUp' : '',
        #     'ElectronEnDown' : '',
        #     'MuonEnUp' : '',
        #     'MuonEnDown' : '',
        #     'TauEnUp' : '',
        #     'TauEnDown' : '',
        #     'UnclusteredEnUp' : '',
        #     'UnclusteredEnDown' : '',
        # }

        # Used in 01
        # Rename to normalisation_measurements?
        self.normalisation_systematics = [
            'central',

            'JES_up',
            'JES_down',
            'JER_up',
            'JER_down',          

            'BJet_up',
            'BJet_down',
            'LightJet_up',
            'LightJet_down',

            'PileUp_up',
            'PileUp_down',

            'Electron_up',
            'Electron_down',
            'Muon_up',
            'Muon_down',

            'ElectronEnUp',
            'ElectronEnDown',
            'MuonEnUp',
            'MuonEnDown',
            'TauEnUp',
            'TauEnDown',
            'UnclusteredEnUp',
            'UnclusteredEnDown',

            'luminosity+', 
            'luminosity-', 

            'V+Jets_cross_section-',
            'V+Jets_cross_section+', 
            'SingleTop_cross_section+', 
            'SingleTop_cross_section-', 

            'QCD_cross_section', 
            'QCD_shape',
        ]

        # Rename to generator_measurements?
        self.generator_systematics = [ 
            'TTJets_massup',
            'TTJets_massdown',
            'TTJets_alphaSup', 
            'TTJets_alphaSdown',
            'TTJets_hadronisation',
            'TTJets_topPt',
            'TTJets_factorisationup',
            'TTJets_factorisationdown',
            'TTJets_renormalisationup',
            'TTJets_renormalisationdown',
            'TTJets_combinedup',
            'TTJets_combineddown',
            'TTJets_matchingup', 
            'TTJets_matchingdown',
            'TTJets_fsrup', 
            'TTJets_fsrdown',
            'TTJets_isrup', 
            'TTJets_isrdown',
            'TTJets_ueup', 
            'TTJets_uedown'
        ]

        self.measurements = self.normalisation_systematics + self.generator_systematics

        self.list_of_systematics = {
            # Theoretical Uncertainties (Rate Changing)
            'V+Jets_cross_section'      : ['V+Jets_cross_section+', 'V+Jets_cross_section-'],
            'QCD_cross_section'         : ['QCD_cross_section', 'QCD_cross_section'],
            'SingleTop_cross_section'   : ['SingleTop_cross_section+', 'SingleTop_cross_section-'],
            'luminosity'                : ['luminosity+', 'luminosity-'],
            # QCD Shape
            'QCD_shape'                 : ['QCD_shape', 'QCD_shape'],
            # Generator Uncertainties
            'TTJets_mass'               : ['TTJets_massup', 'TTJets_massdown'],
            'TTJets_hadronisation'      : ['TTJets_hadronisation', 'TTJets_hadronisation'],
            'TTJets_ue'                 : ['TTJets_ueup', 'TTJets_uedown'],
            'TTJets_topPt'              : ['TTJets_topPt', 'TTJets_topPt'],
            'TTJets_envelope'           : ['TTJets_factorisationup', 'TTJets_factorisationdown',
                                            'TTJets_renormalisationup', 'TTJets_renormalisationdown',
                                            'TTJets_combinedup', 'TTJets_combineddown',
                                            'TTJets_fsrup', 'TTJets_fsrdown',
                                            'TTJets_isrup', 'TTJets_isrdown'],

            'TTJets_alphaS'             : ['TTJets_alphaSup', 'TTJets_alphaSdown'],
            'TTJets_matching'           : ['TTJets_matchingup', 'TTJets_matchingdown'],

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
            # 'Top_pt_reweight'           : ['Top_pt_reweight', 'Top_pt_reweight'],
            # 'Top_eta_reweight'          : ['Top_eta_reweight_up', 'Top_eta_reweight_down'],
        }

        # now fill in the centre of mass dependent values
        self.__fill_defaults_13TeV__()

        self.topMass_systematics = [ 'TTJets_massup', 'TTJets_massdown']

        self.topMasses = [
            169.5, 
            172.5, 
            173.5,
        ]
        self.topMassUncertainty = 1.0 # GeV from https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO

        # categories_and_prefixes = self.categories_and_prefixes

        # Used in 01
        # self.general_trees          = {
        #     category: path_to_files + category + '/%s' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
        self.ttbar_trees            = {
            category: path_to_files + 'TTJets_PowhegPythia8_tree.root' for category in self.normalisation_systematics}
        self.SingleTop_trees        = {
            category: path_to_files + 'SingleTop_tree.root' for category in self.normalisation_systematics}
        self.VJets_trees            = {
            category: path_to_files + 'VJets_tree.root' for category in self.normalisation_systematics}
        self.electron_QCD_MC_trees  = {
            category: path_to_files + 'QCD_Electron_tree.root' for category in self.normalisation_systematics}
        self.muon_QCD_MC_trees      = {
            category: path_to_files + 'QCD_Muon_tree.root' for category in self.normalisation_systematics}

        self.ttbar_amc_trees = path_to_files + '/TTJets_amc_tree.root'
        self.ttbar_madgraph_trees = path_to_files + '/TTJets_madgraph_tree.root'
        self.ttbar_powhegpythia8_trees = path_to_files + '/TTJets_PowhegPythia8_tree.root'
        self.ttbar_powhegherwigpp_trees = path_to_files + '/TTJets_powhegHerwigpp_tree.root'
        self.ttbar_amcatnloherwigpp_trees = path_to_files + '/TTJets_amcatnloHerwigpp_tree.root'

        self.ttbar_mtop1695_trees = path_to_files + '/TTJets_PowhegPythia8_mtop1695_tree.root'
        self.ttbar_mtop1755_trees = path_to_files + '/TTJets_PowhegPythia8_mtop1755_tree.root'
        self.ttbar_jesup_trees = path_to_files + '/TTJets_PowhegPythia8_plusJES_tree.root'
        self.ttbar_jesdown_trees = path_to_files + '/TTJets_PowhegPythia8_minusJES_tree.root'
        self.ttbar_jerup_trees = path_to_files + '/TTJets_PowhegPythia8_plusJER_tree.root'
        self.ttbar_jerdown_trees = path_to_files + '/TTJets_PowhegPythia8_minusJER_tree.root'

        # Underlying Event trees
        self.ttbar_ueup_trees = path_to_files + '/TTJets_powhegPythia8_up_tree.root'
        self.ttbar_uedown_trees = path_to_files + '/TTJets_powhegPythia8_down_tree.root'
        # Initial(Final) State Radiation event Trees
        self.ttbar_isrup_trees = path_to_files + '/TTJets_powhegPythia8_isrup_tree.root'
        self.ttbar_isrdown_trees = path_to_files + '/TTJets_powhegPythia8_isrdown_tree.root'
        self.ttbar_fsrup_trees = path_to_files + '/TTJets_powhegPythia8_fsrup_tree.root'
        self.ttbar_fsrdown_trees = path_to_files + '/TTJets_powhegPythia8_fsrdown_tree.root'

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

        self.unfolding_ptreweight = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_withTopPtReweighting.root' % self.centre_of_mass_energy

        self.unfolding_renormalisation_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_05muR1muF.root' % self.centre_of_mass_energy
        self.unfolding_renormalisation_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_2muR1muF.root' % self.centre_of_mass_energy
        self.unfolding_factorisation_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_1muR05muF.root' % self.centre_of_mass_energy
        self.unfolding_factorisation_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_1muR2muF.root' % self.centre_of_mass_energy
        self.unfolding_combined_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_05muR05muF.root' % self.centre_of_mass_energy
        self.unfolding_combined_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_2muR2muF.root' % self.centre_of_mass_energy
        self.unfolding_fsr_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_fsrdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_fsr_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_fsrup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_isr_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_isrdown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_isr_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_isrup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_ue_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_uedown_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_ue_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ueup_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_topPtSystematic = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_topPtSystematic_asymmetric.root' % self.centre_of_mass_energy
        self.unfolding_alphaS_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_alphaS_down.root' % self.centre_of_mass_energy
        self.unfolding_alphaS_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_alphaS_up.root' % self.centre_of_mass_energy
        self.unfolding_matching_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_matching_down.root' % self.centre_of_mass_energy
        self.unfolding_matching_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_matching_up.root' % self.centre_of_mass_energy
     
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

        self.pdfWeightMin = 0
        self.pdfWeightMax = 100
        self.unfolding_pdfweights = {index : path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_pdfWeight_%d.root' % (self.centre_of_mass_energy, index) for index in range( self.pdfWeightMin, self.pdfWeightMax )}

        # Used in 01
        self.tree_path = {
            'electron' : 'TTbar_plus_X_analysis/EPlusJets/Ref selection/FitVariables',
            'muon' : 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/FitVariables',
        }
        self.qcd_control_region = {
            'electron'  : 'QCDConversions',
            'muon'      : 'QCD non iso mu+jets 1p5to3',
        }
        self.qcd_shape_syst_region = {
            'electron'  : 'QCD non iso e+jets',
            'muon'      : 'QCD non iso mu+jets 3toInf',
        }

        # Needed?
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

        self.include_higgs = False

        self.luminosity_scale = self.new_luminosity / self.luminosity

        # Needed?
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
                ('QCD_cross_section', 'QCD_cross_section'),
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

        self.new_luminosity = 36459
        self.ttbar_xsection = 831.76  # pb

        self.rate_changing_systematics = {#TODO check where this is used
            'luminosity': 0.062,
            'SingleTop_cross_section': 0.05,  # Currently same as 8 TeV
            'V+Jets_cross_section': 0.5,
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
