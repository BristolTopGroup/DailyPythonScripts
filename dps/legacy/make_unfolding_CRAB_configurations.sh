#!/bin/bash
#A script for using make_CRAB_configuration.py to write CRAB configuration files for datasets specified in dataset_input.txt.
#
#It is recommended to run this script in the Configurations folder of NTupleTools, so that the created CRAB configuration files go into the correct locations/folders.
#If it is run from another location, any new folder(s) will be created in the working location, into which the created files will be placed, that is all.
#
#With current filepaths (as committed), make_CRAB_configuration.py should be in the same folder as this make_CRAB_configuration_from_file.sh script
#and das_client.py should be in the ../tools folder relative to this script.
#
#Simply run with: ./make_unfolding_CRAB_configurations.sh >&makeunfoldingconfigs.log &

#Monte Carlo (LeptonPlus3Jets skim)
python make_CRAB_configuration.py --jobtype=cmssw --scheduler=glite --use_server=1 --version=v10 --datasetpath=/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM --pset=BristolAnalysis/NTupleTools/test/unfoldingAndCutflow_cfg.py --numberevents=-1 --numberlumis=0 --numberjobs=200 --lumi_mask=None --useData=0 --dataType=TTJets --skim=NoSkim --storePDFWeights=1 --isTTbarMC=1 --mail=None --whiteList=None --blackList=None

python make_CRAB_configuration.py --jobtype=cmssw --scheduler=glite --use_server=1 --version=v10 --datasetpath=/TT_8TeV-mcatnlo/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM --pset=BristolAnalysis/NTupleTools/test/unfoldingAndCutflow_cfg.py --numberevents=-1 --numberlumis=0 --numberjobs=900 --lumi_mask=None --useData=0 --dataType=TTJets --skim=NoSkim --isTTbarMC=1 --isMCatNLO=1 --mail=None --whiteList=None --blackList=None
python make_CRAB_configuration.py --jobtype=cmssw --scheduler=glite --use_server=1 --version=v10 --datasetpath=/TT_CT10_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM --pset=BristolAnalysis/NTupleTools/test/unfoldingAndCutflow_cfg.py --numberevents=-1 --numberlumis=0 --numberjobs=600 --lumi_mask=None --useData=0 --dataType=TTJets --skim=NoSkim --isTTbarMC=1 --mail=None --whiteList=None --blackList=None

python make_CRAB_configuration.py --jobtype=cmssw --scheduler=glite --use_server=1 --version=v10 --datasetpath=/TTJets_scaleup_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM --pset=BristolAnalysis/NTupleTools/test/unfoldingAndCutflow_cfg.py --numberevents=-1 --numberlumis=0 --numberjobs=150 --lumi_mask=None --useData=0 --dataType=TTJets-scaleup --skim=NoSkim --isTTbarMC=1 --mail=None --whiteList=None --blackList=None
python make_CRAB_configuration.py --jobtype=cmssw --scheduler=glite --use_server=1 --version=v10 --datasetpath=/TTJets_scaledown_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM --pset=BristolAnalysis/NTupleTools/test/unfoldingAndCutflow_cfg.py --numberevents=-1 --numberlumis=0 --numberjobs=150 --lumi_mask=None--useData=0 --dataType=TTJets-scaledown --skim=NoSkim --isTTbarMC=1 --mail=None --whiteList=None --blackList=None
python make_CRAB_configuration.py --jobtype=cmssw --scheduler=glite --use_server=1 --version=v10 --datasetpath=/TTJets_matchingup_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM --pset=BristolAnalysis/NTupleTools/test/unfoldingAndCutflow_cfg.py --numberevents=-1 --numberlumis=0 --numberjobs=150 --lumi_mask=None --useData=0 --dataType=TTJets-matchingup --skim=NoSkim --isTTbarMC=1 --mail=None --whiteList=None --blackList=None
python make_CRAB_configuration.py --jobtype=cmssw --scheduler=glite --use_server=1 --version=v10 --datasetpath=/TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM --pset=BristolAnalysis/NTupleTools/test/unfoldingAndCutflow_cfg.py --numberevents=-1 --numberlumis=0 --numberjobs=150 --lumi_mask=None --useData=0 --dataType=TTJets-matchingdown --skim=NoSkim --isTTbarMC=1 --mail=None --whiteList=None --blackList=None
