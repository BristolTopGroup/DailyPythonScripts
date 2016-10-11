'''
inputFiles as argument
e.g. /hdfs/TopQuarkGroup/phxlk/ntuple/v0.0.8/Spring16/SingleMuon_Run2016E_PromptReco_v2/tmp/*/*.root
'''
import ROOT 
from ROOT import gROOT, TFile, TH1F
import sys

inputFiles = sys.argv[1:]


outputJson = {}

for file in inputFiles:
	f = file
	# print file
	# f = glob.glob(file+'/*.root')[0]
	inputFile = TFile(f)
	tree = inputFile.Get('nTupleTree/tree')

	for event in tree:
		run = event.__getattr__('Event.Run')
		lumi = event.__getattr__('Event.LumiSection')

		if str(run) in outputJson.keys():
			lumisSoFar = outputJson[str(run)]
			newLumi = True
			for l in lumisSoFar:
				if lumi == l[0]: newLumi = False
			if newLumi: outputJson[str(run)].append([lumi, lumi])
		else:
			outputJson[str(run)] = [[lumi, lumi]]
		# print run,lumi
	# print outputJson
print json.dumps(outputJson)