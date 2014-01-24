#define additional weights for the various samples
weights = {}

#define binning for different histograms for Rebin()
binning = {}
binning['mttbar'] = 50

#define QCD estimation method
#from ... import X
qcdestimationMethod = None

#define histograms where QCD is not scaled to estimation
doNotUseQCDEstimationFor = [
                            'QCD'
                            ]


