from __future__ import division
import dps.utils.measurement

class XSectionConfig():
    current_analysis_path = '/hdfs/TopQuarkGroup/ec6821/1.0.12/atOutput/combined/'
    known_centre_of_mass_energies = [13]
    # has to be separate as many variables depend on it
    luminosities = {13:35900}

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
        'unfolding_amcatnlo_pythia8', 'unfolding_amcatnlo_pythia8_raw', 
        'unfolding_madgraphMLM', 'unfolding_madgraphMLM_raw',
        'unfolding_hdamp_down', 'unfolding_hdamp_down_raw',
        'unfolding_hdamp_up', 'unfolding_hdamp_up_raw',
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
        'abs_lepton_eta',
        'abs_lepton_eta_coarse'
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
        'abs_bjets_eta',
        'abs_lepton_eta_coarse'
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

        # self.path_to_unfolding_histograms = '/hdfs/TopQuarkGroup/run2/unfolding/13TeV/Moriond2017/'
        # self.path_to_unfolding_histograms = '/hdfs/TopQuarkGroup/run2/unfolding/13TeV/EPS2017/'
        self.path_to_unfolding_histograms = 'unfolding/13TeV/'
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

        self.data_file_muon = path_to_files + 'data_muon_tree.root'
        self.data_file_electron = path_to_files + 'data_electron_tree.root'

        self.higgs_file = path_to_files + 'central/TTH_Inclusive_M-125' + middle + '.root'

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

            'QCD_other_control_region',
            'QCD_signal_MC'
        ]

        # Rename to generator_measurements?
        self.generator_systematics = [ 
            'TTJets_massup',
            'TTJets_massdown',
            'TTJets_alphaSup', 
            'TTJets_alphaSdown',
            'TTJets_topPt',
            'TTJets_factorisationup',
            'TTJets_factorisationdown',
            'TTJets_renormalisationup',
            'TTJets_renormalisationdown',
            'TTJets_combinedup',
            'TTJets_combineddown',
            'TTJets_hdampup', 
            'TTJets_hdampdown',
            'TTJets_erdOn',
            'TTJets_QCDbased_erdOn',
            'TTJets_GluonMove',
            'TTJets_semiLepBrup', 
            'TTJets_semiLepBrdown',
            'TTJets_fragup', 
            'TTJets_fragdown',
            'TTJets_petersonFrag',
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
            'TTJets_ue'                 : ['TTJets_ueup', 'TTJets_uedown'],
            'TTJets_topPt'              : ['TTJets_topPt', 'TTJets_topPt'],
            'TTJets_scale'              : [ 'TTJets_factorisationup', 'TTJets_factorisationdown',
                                            'TTJets_renormalisationup', 'TTJets_renormalisationdown',
                                            'TTJets_combinedup', 'TTJets_combineddown',
                                            'TTJets_fsrup', 'TTJets_fsrdown',
                                            'TTJets_isrup', 'TTJets_isrdown'
                                            ],
            # 'TTJets_fsr'                   :    ['TTJets_fsrup', 'TTJets_fsrdown'],
            # 'TTJets_isr'                   :    ['TTJets_isrup', 'TTJets_isrdown'],


            'TTJets_alphaS'             : ['TTJets_alphaSup', 'TTJets_alphaSdown'],
            'TTJets_hdamp'           : ['TTJets_hdampup', 'TTJets_hdampdown'],
            'TTJets_semiLepBr'           : ['TTJets_semiLepBrup', 'TTJets_semiLepBrdown'],
            'TTJets_frag'           : ['TTJets_fragup', 'TTJets_fragdown'],
            'TTJets_petersonFrag'           : ['TTJets_petersonFrag', 'TTJets_petersonFrag'],
            'TTJets_CR_erdOn'           : ['TTJets_erdOn', 'TTJets_erdOn'],
            'TTJets_CR_QCDbased_erdOn'           : ['TTJets_QCDbased_erdOn', 'TTJets_QCDbased_erdOn'],
            'TTJets_CR_GluonMove'           : ['TTJets_GluonMove', 'TTJets_GluonMove'],

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

        self.mcTheoryUncertainties = {
            'TTJets_mass'               : ['TTJets_massup', 'TTJets_massdown'],
            'TTJets_ue'                 : ['TTJets_ueup', 'TTJets_uedown'],
            'TTJets_topPt'              : ['TTJets_topPt', 'TTJets_topPt'],
            'TTJets_scale'              : ['TTJets_factorisationup', 'TTJets_factorisationdown',
                                            'TTJets_renormalisationup', 'TTJets_renormalisationdown',
                                            'TTJets_combinedup', 'TTJets_combineddown',
                                            'TTJets_fsrup', 'TTJets_fsrdown',
                                            'TTJets_isrup', 'TTJets_isrdown'
                                            ],
            'TTJets_alphaS'             : ['TTJets_alphaSup', 'TTJets_alphaSdown'],
            'TTJets_hdamp'           : ['TTJets_hdampup', 'TTJets_hdampdown'],
            'TTJets_semiLepBr'           : ['TTJets_semiLepBrup', 'TTJets_semiLepBrdown'],
            'TTJets_frag'           : ['TTJets_fragup', 'TTJets_fragdown'],
            'TTJets_petersonFrag'           : ['TTJets_petersonFrag', 'TTJets_petersonFrag'],
            'TTJets_CR_erdOn'           : ['TTJets_erdOn', 'TTJets_erdOn'],
            'TTJets_CR_QCDbased_erdOn'           : ['TTJets_QCDbased_erdOn', 'TTJets_QCDbased_erdOn'],
        }

        self.systematic_group_bkg = [
            'V+Jets_cross_section',
            'SingleTop_cross_section', 
            'QCD_cross_section', 
            'QCD_shape',
        ]
        self.systematic_group_met = [
            'ElectronEn',
            'MuonEn',
            'TauEn',
            'UnclusteredEn',
        ]
        self.systematic_group_experimental = [
            'JES',
            'JER',
            'BJet',
            'LightJet',
            'PileUp',
            'Electron',
            'Muon',
            'luminosity', 
        ]
        self.systematic_group_partonShower = [
            'TTJets_scale',

            # 'TTJets_fsr',
            # 'TTJets_isr',

            'TTJets_ue',
            'TTJets_hdamp',
            'TTJets_semiLepBr',
            'TTJets_frag',
            'TTJets_petersonFrag',
            'TTJets_CR_erdOn',
            'TTJets_CR_QCDbased_erdOn',
            'TTJets_CR_GluonMove',
            'JES',
        ]
        self.systematic_group_otherTheoretical = [
            'PDF',
            'TTJets_alphaS',
            'TTJets_mass',
            'TTJets_topPt'
        ]
        self.systematic_group_pdf = [
            'PDF',
            'CT14',
            'MMHT14',
        ]
        self.systematic_other = [
            'inputMC',
        ]

        self.samplesForChi2Comparison = [
            'TTJets_powhegPythia8',
            'TTJets_powhegHerwig',
            'TTJets_amcatnloPythia8',
            'TTJets_madgraphMLM'
        ]
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
        self.ttbar_trees = path_to_files + 'TTJets_PowhegPythia8_tree.root'
        self.SingleTop_trees = path_to_files + 'SingleTop_tree.root'

        self.VJets_trees = path_to_files + 'VJets_tree.root'
        self.electron_QCD_MC_trees = path_to_files + 'QCD_Electron_tree.root'
        self.muon_QCD_MC_trees = path_to_files + 'QCD_Muon_tree.root'
        # self.electron_QCD_MC_trees = path_to_files + 'QCD_Inclusive_tree.root'
        # self.muon_QCD_MC_trees = path_to_files + 'QCD_Inclusive_tree.root'
        # self.muon_QCD_MC_trees = path_to_files + 'QCD_All_tree.root'

        self.ttbar_amc_trees = path_to_files + '/TTJets_amc_tree.root'
        self.ttbar_madgraph_trees = path_to_files + '/TTJets_madgraph_tree.root'
        self.ttbar_powhegpythia8_trees = path_to_files + '/TTJets_PowhegPythia8_tree.root'
        self.ttbar_powhegherwigpp_trees = path_to_files + '/TTJets_PowhegHerwigpp_tree.root'
        self.ttbar_amcatnloherwigpp_trees = path_to_files + '/TTJets_amcatnloHerwigpp_tree.root'

        self.ttbar_mtop1695_trees = path_to_files + '/TTJets_PowhegPythia8_mtop1695_tree.root'
        self.ttbar_mtop1755_trees = path_to_files + '/TTJets_PowhegPythia8_mtop1755_tree.root'
        self.ttbar_jesup_trees = path_to_files + '/TTJets_PowhegPythia8_plusJES_tree.root'
        self.ttbar_jesdown_trees = path_to_files + '/TTJets_PowhegPythia8_minusJES_tree.root'
        self.ttbar_jerup_trees = path_to_files + '/TTJets_PowhegPythia8_plusJER_tree.root'
        self.ttbar_jerdown_trees = path_to_files + '/TTJets_PowhegPythia8_minusJER_tree.root'

        self.st_s_trees = '/scratch/db0268/DPS/DPSTestingGround/DailyPythonScripts/ST_s.root'
        self.st_t_trees = '/scratch/db0268/DPS/DPSTestingGround/DailyPythonScripts/ST_t.root'
        self.st_tW_trees = '/scratch/db0268/DPS/DPSTestingGround/DailyPythonScripts/ST_tW.root'
        self.stbar_t_trees = '/scratch/db0268/DPS/DPSTestingGround/DailyPythonScripts/STbar_t.root'
        self.stbar_tW_trees = '/scratch/db0268/DPS/DPSTestingGround/DailyPythonScripts/STbar_tW.root'

        # Underlying Event trees
        self.ttbar_ueup_trees = path_to_files + '/TTJets_PowhegPythia8_up_tree.root'
        self.ttbar_uedown_trees = path_to_files + '/TTJets_PowhegPythia8_down_tree.root'
        # Initial(Final) State Radiation event Trees
        self.ttbar_isrup_trees = path_to_files + '/TTJets_PowhegPythia8_isrup_tree.root'
        self.ttbar_isrdown_trees = path_to_files + '/TTJets_PowhegPythia8_isrdown_tree.root'
        self.ttbar_fsrup_trees = path_to_files + '/TTJets_PowhegPythia8_fsrup_tree.root'
        self.ttbar_fsrdown_trees = path_to_files + '/TTJets_PowhegPythia8_fsrdown_tree.root'
        # hdamp up/down
        self.ttbar_hdampup_trees = path_to_files + '/TTJets_PowhegPythia8_hdampup_tree.root'
        self.ttbar_hdampdown_trees = path_to_files + '/TTJets_PowhegPythia8_hdampdown_tree.root'

        # erdOn
        self.ttbar_erdOn_trees = path_to_files + '/TTJets_PowhegPythia8_erdOn_tree.root'
        self.ttbar_QCDbased_erdOn_trees = path_to_files + '/TTJets_PowhegPythia8_QCDbased_erdOn_tree.root'
        self.ttbar_GluonMove_trees = path_to_files + '/TTJets_PowhegPythia8_GluonMove_tree.root'

        # Unfolding MC Different Generator Samples
        self.unfolding_powheg_pythia8_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV.root' % self.centre_of_mass_energy
        self.unfolding_amcatnlo_pythia8_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_amcatnloPythia8.root' % self.centre_of_mass_energy
        self.unfolding_madgraphMLM_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_madgraph.root' % self.centre_of_mass_energy
        self.unfolding_powheg_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_powhegherwigpp.root' % self.centre_of_mass_energy
        self.unfolding_amcatnlo_herwig_raw = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_amcatnloherwigpp.root' % self.centre_of_mass_energy

        # Choose central MC Sample
        # self.unfolding_central_raw = self.unfolding_powheg_pythia8_raw
        self.unfolding_central_raw = 'unfolding/13TeV/unfolding_TTJets_13TeV.root'

        # Raw --> asymmetric
        self.unfolding_powheg_pythia8 = self.unfolding_powheg_pythia8_raw.replace( '.root', '_asymmetric_newPS.root' )
        self.unfolding_amcatnlo_pythia8 = self.unfolding_amcatnlo_pythia8_raw.replace( '.root', '_asymmetric_newPS.root' )
        self.unfolding_madgraphMLM = self.unfolding_madgraphMLM_raw.replace( '.root', '_asymmetric_newPS.root' )
        self.unfolding_powheg_herwig = self.unfolding_powheg_herwig_raw.replace( '.root', '_asymmetric_newPS.root' )
        self.unfolding_amcatnlo_herwig = self.unfolding_amcatnlo_herwig_raw.replace( '.root', '_asymmetric_newPS.root' )

        self.unfolding_central = self.unfolding_powheg_pythia8

        self.unfolding_ptreweight = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_withTopPtReweighting.root' % self.centre_of_mass_energy

        self.unfolding_ptreweight_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_withTopPtReweighting_up.root' % self.centre_of_mass_energy
        self.unfolding_ptreweight_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_withTopPtReweighting_down.root' % self.centre_of_mass_energy
        self.unfolding_etareweight_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_withTopEtaReweighting_up.root' % self.centre_of_mass_energy
        self.unfolding_etareweight_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_withTopEtaReweighting_down.root' % self.centre_of_mass_energy

        self.unfolding_central_firstHalf = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_firstHalf.root' % self.centre_of_mass_energy
        self.unfolding_central_secondHalf = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_secondHalf.root' % self.centre_of_mass_energy

        self.unfolding_ptreweight_up_firstHalf = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_firstHalf_withTopPtReweighting_up.root' % self.centre_of_mass_energy
        self.unfolding_ptreweight_down_firstHalf = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_firstHalf_withTopPtReweighting_down.root' % self.centre_of_mass_energy

        self.unfolding_ptreweight_up_secondHalf = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_secondHalf_withTopPtReweighting_up.root' % self.centre_of_mass_energy
        self.unfolding_ptreweight_down_secondHalf = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_secondHalf_withTopPtReweighting_down.root' % self.centre_of_mass_energy


        self.unfolding_renormalisation_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_05muR1muF.root' % self.centre_of_mass_energy
        self.unfolding_renormalisation_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_2muR1muF.root' % self.centre_of_mass_energy
        self.unfolding_factorisation_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_1muR05muF.root' % self.centre_of_mass_energy
        self.unfolding_factorisation_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_1muR2muF.root' % self.centre_of_mass_energy
        self.unfolding_combined_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_05muR05muF.root' % self.centre_of_mass_energy
        self.unfolding_combined_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_2muR2muF.root' % self.centre_of_mass_energy
        self.unfolding_fsr_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_fsrdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_fsr_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_fsrup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_isr_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_isrdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_isr_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_isrup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_ue_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_uedown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_ue_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ueup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_topPtSystematic = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_topPtSystematic_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_alphaS_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_alphaS_down.root' % self.centre_of_mass_energy
        self.unfolding_alphaS_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_alphaS_up.root' % self.centre_of_mass_energy
        self.unfolding_hdamp_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_hdampdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_hdamp_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_hdampup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_semiLepBr_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_semiLepBr_down.root' % self.centre_of_mass_energy
        self.unfolding_semiLepBr_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_semiLepBr_up.root' % self.centre_of_mass_energy
        self.unfolding_frag_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_frag_down.root' % self.centre_of_mass_energy
        self.unfolding_frag_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_frag_up.root' % self.centre_of_mass_energy
        self.unfolding_petersonFrag = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_frag_peterson.root' % self.centre_of_mass_energy
        self.unfolding_erdOn = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_erdOn_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_QCDbased_erdOn = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_QCDbased_erdOn_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_GluonMove = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_GluonMove_asymmetric_newPS.root' % self.centre_of_mass_energy

        self.unfolding_mass_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_massdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_mass_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_massup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_Electron_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_electrondown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_Electron_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_electronup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_Muon_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_muondown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_Muon_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_muonup_asymmetric_newPS.root' % self.centre_of_mass_energy
        
        self.unfolding_jes_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jesdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_jes_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jesup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_jer_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jerdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_jer_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_jerup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_bjet_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_bjetdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_bjet_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_bjetup_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_lightjet_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_lightjetdown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_lightjet_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_lightjetup_asymmetric_newPS.root' % self.centre_of_mass_energy

        self.unfolding_ElectronEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ElectronEnDown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_ElectronEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_ElectronEnUp_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_MuonEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_MuonEnDown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_MuonEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_MuonEnUp_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_TauEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_TauEnDown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_TauEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_TauEnUp_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_UnclusteredEn_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_UnclusteredEnDown_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_UnclusteredEn_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_UnclusteredEnUp_asymmetric_newPS.root' % self.centre_of_mass_energy

        self.unfolding_PUSystematic_up = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_pileupUp_asymmetric_newPS.root' % self.centre_of_mass_energy
        self.unfolding_PUSystematic_down = path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_pileupDown_asymmetric_newPS.root' % self.centre_of_mass_energy

        self.pdfWeightMin = 0
        self.pdfWeightMax = 100
        self.ct14WeightMax = 54
        self.mmht14WeightMax = 55
        self.unfolding_pdfweights = {index : path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_pdfWeight_%d.root' % (self.centre_of_mass_energy, index) for index in range( self.pdfWeightMin, self.pdfWeightMax )}
        self.unfolding_CT14weights = {index : path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_CT14Weight_%d.root' % (self.centre_of_mass_energy, index) for index in range( self.pdfWeightMin, self.ct14WeightMax )}
        self.unfolding_MMHT14weights = {index : path_to_unfolding_histograms + 'unfolding_TTJets_%dTeV_asymmetric_newPS_MMHT14Weight_%d.root' % (self.centre_of_mass_energy, index) for index in range( self.pdfWeightMin, self.mmht14WeightMax )}

        # Used in 01
        self.tree_path = {
            'electron' : 'TTbar_plus_X_analysis/EPlusJets/Ref selection/AnalysisVariables',
            'muon' : 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/AnalysisVariables',
        }
        self.qcd_control_region = {
            'electron'  : 'QCD non iso e+jets',
            'muon'      : 'QCD non iso mu+jets 1p5to3',
        }
        self.qcd_shape_syst_region = {
            'electron'  : 'QCDConversions',
            'muon'      : 'QCD non iso mu+jets 3toInf',
        }

        # Needed?
        self.variable_path_templates = {
            'MET' : 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/MET',
            'HT' : 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/HT',
            'ST': 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/ST',
            'MT': 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/MT',
            'WPT': 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/WPT',
            'NJets': 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/NJets',
            'lepton_pt': 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/lepton_pt',
            'lepton_eta': 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/lepton_eta',
            'abs_lepton_eta': 'TTbar_plus_X_analysis/{channel}/{selection}/AnalysisVariables/absolute_eta',
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

        self.new_luminosity = 35900
        # self.new_luminosity = 8610

        ### Estimated luminosity for each period
        # B
        self.new_luminosity_periods = {
            'B' : 5790,
            'C' : 2570,
            'D' : 4250,
            'E' : 4010,
            'F' : 3100,
            'G' : 7540,
            'H' : 8610,
        }
        self.ttbar_xsection = 831.76  # pb

        self.rate_changing_systematics = {
            'luminosity': 0.025,
            'SingleTop_cross_section': 0.3, 
            'V+Jets_cross_section': 0.5,
         }

        self.tau_values_electron = {
            "WPT" : 0.0008844791043,
            "NJets" : 8.10189009766e-05,
            "lepton_pt" : 0.000314736393369,
            "HT" : 0.00113322118389,
            "ST" : 0.0014859830286,
            "MET" : 0.00186599526208,
            "abs_lepton_eta" : 1.1970850305e-08,
            "abs_lepton_eta_coarse" : 1.1970850305e-08,
        }

        self.tau_values_muon = {
            "WPT" : 0.0011493622426,
            "NJets" : 0.000102772350787,
            "lepton_pt" : 0.000431806985455,
            "HT" : 0.00146446910083,
            "ST" : 0.00192109241721,
            "MET" : 0.00240030731786,
            "abs_lepton_eta" : 2.29348568572e-06,
            "abs_lepton_eta_coarse" : 2.29348568572e-06,
        }

        self.tau_values_combined = {
            "WPT" : 0,
            "NJets" : 0,
            "lepton_pt" : 0,
            "HT" : 0,
            "ST" : 0,
            "MET" : 0,
            "abs_lepton_eta" : 0,
            "abs_lepton_eta_coarse" : 0,

           }

        # self.categories_and_prefixes['PU_down'] = '_PU_65835mb'
        # self.categories_and_prefixes['PU_up'] = '_PU_72765mb'
