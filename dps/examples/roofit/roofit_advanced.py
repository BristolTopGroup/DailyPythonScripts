#same as roofit_beginner.py but with explicit variables
from ROOT import RooFit, RooRealVar, RooArgusBG, RooGaussian, RooArgList, RooArgSet, RooAddPdf, kDashed

mes = RooRealVar("mes", "m_{ES} (GeV)", 5.20, 5.30)
 
# --- Parameters ---
sigmean = RooRealVar("sigmean", "B^{#pm} mass", 5.28, 5.20, 5.30)
sigwidth = RooRealVar("sigwidth", "B^{#pm} width", 0.0027, 0.001, 1.)
 
# --- Build Gaussian PDF ---
signal = RooGaussian("signal", "signal PDF", mes, sigmean, sigwidth)

argpar = RooRealVar("argpar", "argus shape parameter", -20.0, -100., -1.)
background = RooArgusBG("background", "Argus PDF", mes, RooFit.RooConst(5.291), argpar)
 
# --- Construct signal+background PDF ---
nsig = RooRealVar("nsig", "#signal events", 200, 0., 10000)
nbkg = RooRealVar("nbkg", "#background events", 800, 0., 10000)
model = RooAddPdf("model", "g+a", RooArgList(signal, background), RooArgList(nsig, nbkg))

# --- Generate a toyMC sample from composite PDF ---
data = model.generate(RooArgSet(mes), 2000)
 
# --- Perform extended ML fit of composite PDF to toy data ---
model.fitTo(data)
 
# --- Plot toy data and composite PDF overlaid ---
mesframe = mes.frame()
data.plotOn(mesframe)
model.plotOn(mesframe)
model.plotOn(mesframe, RooFit.Components('background'), RooFit.LineStyle(kDashed))

mesframe.Draw()

print 'nsig:',nsig.getValV(), '+-', nsig.getError()
print 'nbkg:', nbkg.getValV(), '+-', nbkg.getError()
print 'mes:', mes.getValV(), '+-', mes.getError()
print 'mean:', sigmean.getValV(), '+-', sigmean.getError()
print 'width:', sigwidth.getValV(), '+-', sigwidth.getError()
print 'argpar:', argpar.getValV(), '+-', argpar.getError()


from time import sleep
sleep(10)
