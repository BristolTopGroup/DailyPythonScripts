import ROOT as r
from rootpy.io import File
from rootpy.tree import Tree
import json

def readJson(jsonFile):
	runLumis = None
	with open(jsonFile) as j:
		runLumis = json.load(j)

	fullRunLumi = []
	for run in runLumis:
		for lumiRange in runLumis[run]:
			for lumi in range(lumiRange[0],lumiRange[1]+1):
				fullRunLumi.append([int(run),lumi])
	return fullRunLumi


inputFile = File('/hdfs/TopQuarkGroup/run2/ntuples/v22/SingleMuonFullDCS/SingleMuon.root')
treeName = 'nTupleTree/tree'
tree = inputFile.Get(treeName)

jsonForFiltering = '/users/ec6821/lumiScripts/lcr2/lcr2/good_list.txt'
json = readJson(jsonForFiltering)

newFile = File('SingleMuonFiltered.root', 'RECREATE')
newFile.mkdir('nTupleTree')
newFile.cd('nTupleTree')
newTree = tree.CloneTree(0)

print 'Number of events in tree : ',tree.GetEntries()

for event in tree:
	run = event.__getattr__('Event.Run')
	lumi = event.__getattr__('Event.LumiSection')

	if [run,lumi] in json:
		newTree.Fill()
	else :
		pass
newFile.Close()

	# print run, lumi
# newFile = r.TFile('filtered.root','write')