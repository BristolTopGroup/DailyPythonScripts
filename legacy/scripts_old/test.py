from ROOT import *

c1 = TCanvas("c1","c1",600,400);
# create/fill draw h1
gStyle.SetOptStat(kFALSE);
h1 = TH1F("h1","Superimposing two histograms with different scales",100,-3,3);

for i in range(0,10000):
    h1.Fill(gRandom.Gaus(0,1));
h1.Draw();



h1.Fit('gaus', "Q0", "ah", -3, 3)
fit = h1.GetFunction('gaus')
fit.Draw('same')
c1.Update();
print 'Number of parameter errors', len(fit.GetParErrors())

errors = fit.GetParErrors()
for i in range(0, 10):
    print 'Error No. %d:' % i, errors[i]
    
print fit.GetNumberFreeParameters()

