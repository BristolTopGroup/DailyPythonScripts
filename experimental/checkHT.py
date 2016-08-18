from rootpy.tree import Tree
from rootpy.plotting import Hist, Hist2D, Canvas
from rootpy.io import root_open, File
from ROOT import gPad

powhegHerwigFile = '/storage/ec6821/NTupleProd/CMSSW_5_3_23/src/TTJets_PowhegHerwig_8TeV.root'
powhegV2HerwigppFile = '/storage/ec6821/NTupleProd/CMSSW_5_3_23/src/TTJets_newPowhegHerwig_8TeV.root'
madgraphFile = '/storage/ec6821/NTupleProd/CMSSW_5_3_23/src/TTJets_Madgraph_8TeV.root'

powhegHerwigHists = {}
powhegV2HerwigppHists = {}
madgraphHists = {}

htBins = [120.0, 185.0, 215.0, 247.0, 283.0, 323.0, 365.0, 409.0, 458.0, 512.0, 570.0, 629.0, 691.0, 769.0, 1000.0]
for file in [powhegHerwigFile,powhegV2HerwigppFile,madgraphFile]:

	histStorage = None
	if file == powhegHerwigFile:
		histStorage = powhegHerwigHists
	elif file == powhegV2HerwigppFile:
		histStorage = powhegV2HerwigppHists
	elif file == madgraphFile:
		histStorage = madgraphHists

	h_genHT20 = Hist(htBins, name='genHT20')
	h_genNJets20 = Hist(10,0.5,10.5, name='genNJets20')
	h_genHT30 = Hist(htBins, name='genHT30')
	h_genNJets30 = Hist(10,0.5,10.5, name='genNJets30')

	h_HT20 = Hist(htBins, name='HT20')
	h_nJets20 = Hist(10,0.5,10.5, name='nJets20')
	h_HT30 = Hist(htBins, name='HT30')
	h_nJets30 = Hist(10,0.5,10.5, name='nJets30')

	h_jetPt = [
				Hist(16,20,100,name='jet1Pt'),
				Hist(16,20,100,name='jet2Pt'),
				Hist(16,20,100,name='jet3Pt'),
				Hist(16,20,100,name='jet4Pt'),
				Hist(16,20,100,name='jet5Pt'),
				Hist(16,20,100,name='jet6Pt'),
				Hist(16,20,100,name='jet7Pt'),
				]

	h_recoJetPt = Hist(16,20,100,name='recoJetPt')

	with root_open( file, 'read' ) as f:
		tree = f.Get('rootTupleTreeEPlusJets/ePlusJetsTree')

		tree.SetBranchStatus('*',0)
		tree.SetBranchStatus('unfolding.genHT',1)
		tree.SetBranchStatus('unfolding.genNJets',1)
		tree.SetBranchStatus('unfolding.GenSelection',1)
		tree.SetBranchStatus('unfolding.OfflineSelection',1)
		tree.SetBranchStatus('unfolding.genJetPt',1)
		tree.SetBranchStatus('unfolding.jetPt',1)
		tree.SetBranchStatus('unfolding.jetPtSmear',1)

		print tree.GetEntries()
		nEvents = 0
		for event in tree:

			passesOffline = event.__getattr__('unfolding.OfflineSelection')
			passesGen = event.__getattr__('unfolding.GenSelection')
			if not ( passesOffline and passesGen ) : continue

			nEvents += 1
			genHT = event.__getattr__('unfolding.genHT')
			genNJets = event.__getattr__('unfolding.genNJets')
			genJetPt = event.__getattr__('unfolding.genJetPt')
			jetPt = event.__getattr__('unfolding.jetPt')
			jetPtSmear = event.__getattr__('unfolding.jetPtSmear')

			genHT20 = 0
			genNJet20 = 0
			genHT30 = 0
			genNJet30 = 0
			genJetIndex = 0
			for pt in genJetPt:
				if pt > 20 :
					genNJet20 += 1
					genHT20 += pt
					if genJetIndex < 7:
						h_jetPt[genJetIndex].Fill(pt)
						genJetIndex += 1


				if pt > 30 :
					genNJet30 += 1
					genHT30 += pt

			HT20 = 0
			nJet20 = 0
			HT30 = 0
			nJet30 = 0
			for pt, ptSmear in zip( jetPt, jetPtSmear ):
				smearedPt = pt * ptSmear
				if smearedPt > 20 :
					nJet20 += 1
					HT20 += smearedPt
					h_recoJetPt.Fill( smearedPt )

				if smearedPt > 30 :
					nJet30 += 1
					HT30 += smearedPt

			if nJet30 < 4 :
				print "Fewer than 4 reco jets above 30 : ",nJet30
			h_genHT20.Fill(genHT20)
			h_genNJets20.Fill(genNJet20)
			h_genHT30.Fill( genHT30 )
			h_genNJets30.Fill( genNJet30 )

			h_HT20.Fill( HT20 )
			h_nJets20.Fill( nJet20 )
			h_HT30.Fill( HT30 )
			h_nJets30.Fill( nJet30 )

			if nEvents > 5939:
				break
	histStorage['genHT20'] = h_genHT20.Clone()
	histStorage['genNJets20'] = h_genNJets20.Clone()
	histStorage['genHT30'] = h_genHT30.Clone()
	histStorage['genNJets30'] = h_genNJets30.Clone()

	histStorage['HT20'] = h_HT20.Clone()
	histStorage['nJets20'] = h_nJets20.Clone()
	histStorage['HT30'] = h_HT30.Clone()
	histStorage['nJets30'] = h_nJets30.Clone()

	histStorage['recoJetPt'] = h_recoJetPt.Clone()

	for jetIndex in range(0,7):
		histStorage['jetPt%i' % jetIndex ] = h_jetPt[jetIndex].Clone()

canvas = Canvas(width=700,height=500)
for name,h in powhegHerwigHists.iteritems():
	# h.Scale(1/h.Integral())
	h.linecolor = 'red'
	h.linewidth = 1

for name,h in powhegV2HerwigppHists.iteritems():
	# h.Scale(1/h.Integral())
	h.linecolor = 'blue'
	h.linewidth = 1

for name,h in madgraphHists.iteritems():
	# h.Scale(1/h.Integral())
	h.linecolor = 'green'
	h.linewidth = 1

print powhegHerwigHists['genHT20'].Integral()
print powhegV2HerwigppHists['genHT20'].Integral()
print madgraphHists['genHT20'].Integral()
powhegHerwigHists['genHT20'].Draw('HIST X0')
powhegV2HerwigppHists['genHT20'].Draw('SAME HIST X0')
madgraphHists['genHT20'].Draw('SAME HIST X0')
raw_input('...')

powhegHerwigHists['genNJets20'].Draw('HIST X0')
powhegV2HerwigppHists['genNJets20'].Draw('SAME HIST X0')
madgraphHists['genNJets20'].Draw('SAME HIST X0')
raw_input('...')

# powhegHerwigHists['genHT30'].Draw('HIST X0')
# powhegV2HerwigppHists['genHT30'].Draw('SAME HIST X0')
# madgraphHists['genHT30'].Draw('SAME HIST X0')
# raw_input('...')

# powhegHerwigHists['genNJets30'].Draw('HIST X0')
# powhegV2HerwigppHists['genNJets30'].Draw('SAME HIST X0')
# madgraphHists['genNJets30'].Draw('SAME HIST X0')
# raw_input('...')

powhegV2HerwigppHists['HT20'].Draw('HIST X0')
powhegHerwigHists['HT20'].Draw('SAME HIST X0')
madgraphHists['HT20'].Draw('SAME HIST X0')
raw_input('...')

# powhegHerwigHists['HT30'].Draw('HIST X0')
# powhegV2HerwigppHists['HT30'].Draw('SAME HIST X0')
# madgraphHists['HT30'].Draw('SAME HIST X0')
# raw_input('...')

# powhegHerwigHists['nJets20'].Draw('HIST X0')
# powhegV2HerwigppHists['nJets20'].Draw('SAME HIST X0')
# madgraphHists['nJets20'].Draw('SAME HIST X0')
# raw_input('...')

# powhegHerwigHists['nJets30'].Draw('HIST X0')
# powhegV2HerwigppHists['nJets30'].Draw('SAME HIST X0')
# madgraphHists['nJets30'].Draw('SAME HIST X0')

# raw_input('...')

# powhegHerwigHists['recoJetPt'].Draw('HIST X0')
# powhegV2HerwigppHists['recoJetPt'].Draw('SAME HIST X0')
# madgraphHists['recoJetPt'].Draw('SAME HIST X0')
# raw_input('...')

# gPad.SetLogy()
for jetIndex in range(0,7):
	print jetIndex
	powhegV2HerwigppHists['jetPt%i' % jetIndex ].Draw('HIST X0')
	powhegHerwigHists['jetPt%i' % jetIndex ].Draw('SAME HIST X0')
	madgraphHists['jetPt%i' % jetIndex ].Draw('SAME HIST X0')
	print powhegHerwigHists['jetPt%i' % jetIndex ].Integral()
	print powhegV2HerwigppHists['jetPt%i' % jetIndex ].Integral()
	print madgraphHists['jetPt%i' % jetIndex ].Integral()
	raw_input('...')