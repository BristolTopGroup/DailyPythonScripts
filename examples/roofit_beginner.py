from ROOT import RooFit, RooWorkspace, RooDataSet, kDashed, TBrowser

w = RooWorkspace("w", True)
w.factory("Gaussian::gauss(mes[5.20,5.30],mean[5.28,5.2,5.3],width[0.0027,0.001,1])")
w.factory("ArgusBG::argus(mes,5.291,argpar[-20,-100,-1])")
w.factory("SUM::sum(nsig[200,0,10000]*gauss,nbkg[800,0,10000]*argus)")

#--- Generate a toyMC sample from composite PDF ---
data = w.function('sum').generate(w.argSet('mes'), 2000)
#--- Perform extended ML fit of composite PDF to toy data ---
w.function('sum').fitTo(data)
# --- Plot toy data and composite PDF overlaid ---
mesframe = w.var('mes').frame()
data.plotOn(mesframe)
w.function('sum').plotOn(mesframe)
w.function('sum').plotOn(mesframe, RooFit.Components('argus'), RooFit.LineStyle(kDashed))
 
mesframe.Draw()
mesframe.Browse(TBrowser())

print 'nsig:',w.var('nsig').getValV(), '+-', w.var('nsig').getError()
print 'nbkg:', w.var('nbkg').getValV(), '+-', w.var('nbkg').getError()
print 'mes:', w.var('mes').getValV(), '+-', w.var('mes').getError()
print 'mean:', w.var('mean').getValV(), '+-', w.var('mean').getError()
print 'width:', w.var('width').getValV(), '+-', w.var('width').getError()
print 'argpar:', w.var('argpar').getValV(), '+-', w.var('argpar').getError()

from time import sleep
sleep(5)
