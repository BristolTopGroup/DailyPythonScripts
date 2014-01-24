from ROOT import RooRealVar, RooDataHist, RooArgList, RooHistPdf, RooArgSet, RooAddPdf, RooMCStudy, RooFit
import PlottingUtilities as plotting

class Fitter:
    results = {}
    templates = {}
    normalisation = {}
    dataLabel = ''
    
    def __init__(self):
        pass
    
    def fit(self, histograms = {}, dataLabel = 'data'):
        self.dataLabel = dataLabel
        self.templates = self.generateTemplatesAndNormalisation(histograms)
    
    def generateTemplatesAndNormalisation(self, histograms):
        for sample, histogram in histograms.iteritems():
            self.normalisation[sample] = histogram.Integral()
            temp = histogram.Clone(sample + '_' + 'template')
            self.templates[sample] = plotting.normalise(temp)
    
    def getResults(self):
        return self.results
    
    def getResult(self, label):
        return self.results[label]
    

class RooFitter(Fitter):
    pdfs = {}
    variableName = ''
    minX = 0
    maxX = 0
    
    def __init__(self, variableName, minX, maxX):
        Fitter.__init__(self)
        self.variableName = variableName
        self.minX = minX
        self.maxX = maxX
        
    def fit(self, histograms = {}, dataLabel = 'data', signalLabel = 'TTJet'):
        self.dataLabel = dataLabel
        self.signalLabel = signalLabel
    
    def generatePDFs(self, histograms):
        pass
    
class TMinuitFitter(Fitter):
    def __init__(self):
        Fitter.__init__(self)


def goodnessOfFit(fitter):
    pass



#TODO: move bkgN to list
# 1 data, 1 signal and N background histograms
def performFitInLeptonAbsEta(data_histogram, signal_histogram, bkg1_histogram, bkg2_histogram):
    N_Data = data_histogram.Integral()
    N_signal = signal_histogram.Integral()
    N_bkg1 = bkg1_histogram.Integral()
    N_bkg2 = bkg2_histogram.Integral()
    leptonAbsEta = RooRealVar("leptonAbsEta", "leptonAbsEta", 0., 3.)
    variables = RooArgList()
    variables.add(leptonAbsEta)
    variable_set = RooArgSet()
    variable_set.add(leptonAbsEta)
    
    lowerBound = 0
    upperBound = N_Data*2
    
    data_RooDataHist = RooDataHist("data", "dataset with leptonAbsEta", variables, data_histogram)
    signal_RooDataHist =  RooDataHist("rh_signal", "signal", variables, signal_histogram);
    bkg1_RooDataHist =  RooDataHist("rh_bkg1", "bkg1", variables, bkg1_histogram);
    bkg2_RooDataHist =  RooDataHist("rh_bkg2", "bkg2", variables, bkg2_histogram);

    signal_RooHistPdf = RooHistPdf("pdf_signal", "Signal PDF", variable_set, signal_RooDataHist, 0)
    signal_RooHistPdf = RooHistPdf("pdf_signal", "Signal PDF", variable_set, signal_RooDataHist, 0)

