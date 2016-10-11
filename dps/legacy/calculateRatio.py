from uncertainties import ufloat
from math import sqrt

reductionRelIso = ufloat((1.394, 0.878))

ThreeJet1b_A = ufloat((263.3,134.8))
ThreeJet1b_B = ufloat((720,102.1))
ThreeJet1b_B = ThreeJet1b_B/reductionRelIso

FourJet0b_A = ufloat((812.3,217.6))
FourJet0b_B = ufloat((1097.3,185.53))
FourJet0b_B = FourJet0b_B/reductionRelIso

FourJet1b_A = ufloat((157.2,100.2))
FourJet1b_B = ufloat((398.7,42.6))
FourJet1b_B = FourJet1b_B/reductionRelIso

FourJet2b_A = ufloat((15.3,84.7))
FourJet2b_B = ufloat((58.7, 30.0))
FourJet2b_B = FourJet2b_B/reductionRelIso

#correct errors for bias
#ThreeJet1b_B = ufloat((ThreeJet1b_B.nominal_value,sqrt(ThreeJet1b_B.std_dev()**2 + (ThreeJet1b_B.nominal_value*biasrelIso)**2)))
#FourJet0b_B = ufloat((FourJet0b_B.nominal_value,sqrt(FourJet0b_B.std_dev()**2 + (FourJet0b_B.nominal_value*biasrelIso)**2)))
#FourJet1b_B = ufloat((FourJet1b_B.nominal_value,sqrt(FourJet1b_B.std_dev()**2 + (FourJet1b_B.nominal_value*biasrelIso)**2)))
#FourJet2b_B = ufloat((FourJet2b_B.nominal_value,sqrt(FourJet2b_B.std_dev()**2 + (FourJet2b_B.nominal_value*biasrelIso)**2)))



ratio3j1t = ThreeJet1b_A/ThreeJet1b_B
ratio4j0t = FourJet0b_A/FourJet0b_B
ratio4j1t = FourJet1b_A/FourJet1b_B
ratio4j2t = FourJet2b_A/FourJet2b_B

ThreeJ1t = (ThreeJet1b_A.nominal_value, ThreeJet1b_A.std_dev(), ThreeJet1b_B.nominal_value, ThreeJet1b_B.std_dev(),
            ratio3j1t.nominal_value, ratio3j1t.std_dev(), ((1-ratio3j1t)/ratio3j1t.std_dev()).nominal_value)

FourJ0t = (FourJet0b_A.nominal_value, FourJet0b_A.std_dev(), FourJet0b_B.nominal_value, FourJet0b_B.std_dev(),
            ratio4j0t.nominal_value, ratio4j0t.std_dev(), ((1-ratio4j0t)/ratio4j0t.std_dev()).nominal_value)

FourJ1t = (FourJet1b_A.nominal_value, FourJet1b_A.std_dev(), FourJet1b_B.nominal_value, FourJet1b_B.std_dev(),
            ratio4j1t.nominal_value, ratio4j1t.std_dev(), ((1-ratio4j1t)/ratio4j1t.std_dev()).nominal_value)

FourJ2t = (FourJet2b_A.nominal_value, FourJet2b_A.std_dev(), FourJet2b_B.nominal_value, FourJet2b_B.std_dev(),
            ratio4j2t.nominal_value, ratio4j2t.std_dev(), ((1-ratio4j2t)/ratio4j2t.std_dev()).nominal_value)

print '| * signal region* | *estimate m<sub>T</sub>* | *estimate relative isolation* | *ratio* | *# std deviations from 1* |'
print '| 3j1t |  %.1f &plusmn; %.1f |  %.1f &plusmn; %.1f |  %.2f &plusmn; %.2f |  %.2f |' % ThreeJ1t
print '| 4j0t |  %.1f &plusmn; %.1f |  %.1f &plusmn; %.1f |  %.2f &plusmn; %.2f |  %.2f |' % FourJ0t
print '| 4j1t |  %.1f &plusmn; %.1f |  %.1f &plusmn; %.1f |  %.2f &plusmn; %.2f |  %.2f |' % FourJ1t
print '| 4j2t |  %.1f &plusmn; %.1f |  %.1f &plusmn; %.1f |  %.2f &plusmn; %.2f |  %.2f |' % FourJ2t


#print '3j1t', ratio3j1t, '(1-ratio)/error', (1-ratio3j1t)/ratio3j1t.std_dev()
#print '4j0t', ratio4j0t, '(1-ratio)/error', (1-ratio4j0t)/ratio4j0t.std_dev()
#print '4j1t', ratio4j1t, '(1-ratio)/error', (1-ratio4j1t)/ratio4j1t.std_dev()
#print '4j2t', ratio4j2t, '(1-ratio)/error', (1-ratio4j2t)/ratio4j2t.std_dev()