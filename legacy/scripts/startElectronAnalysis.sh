nohup BAT BristolAnalysis/Tools/python/electronAnalysis_specificMCOnly.py >&electronMC.log &
nohup BAT BristolAnalysis/Tools/python/electronAnalysis_DataOnly.py &> electronData.log &
nohup BAT BristolAnalysis/Tools/python/leptonAnalysis_CommonMCWithoutBigSamples.py &> leptonMC_smallSamples.log &
nohup BAT BristolAnalysis/Tools/python/leptonAnalysis_WPlusJetsMC.py &> leptonMC_WJets.log &
nohup BAT BristolAnalysis/Tools/python/leptonAnalysis_DYPlusJetsMC.py &> leptonMC_DYJets.log &
nohup BAT BristolAnalysis/Tools/python/leptonAnalysis_TTbar.py &> leptonMC_TTJets.log &

