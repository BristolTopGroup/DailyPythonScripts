#!/bin/bash

python measureCrossSection_2012.py -v MET -k 3
python plotCrossSections.py -v MET -k 3
python measureCrossSection_2012.py -v MET -k 4
python plotCrossSections.py -v MET -k 4
python measureCrossSection_2012.py -v MET -k 5
python plotCrossSections.py -v MET -k 5
python measureCrossSection_2012.py -v MET -k 6
python plotCrossSections.py -v MET -k 6

python measureCrossSection_2012.py -v HT -k 4
python plotCrossSections.py -v HT -k 4
python measureCrossSection_2012.py -v HT -k 5
python plotCrossSections.py -v HT -k 5
python measureCrossSection_2012.py -v HT -k 6
python plotCrossSections.py -v HT -k 6
python measureCrossSection_2012.py -v HT -k 7
python plotCrossSections.py -v HT -k 7

python measureCrossSection_2012.py -v ST -k 4
python plotCrossSections.py -v ST -k 4
python measureCrossSection_2012.py -v ST -k 5
python plotCrossSections.py -v ST -k 5
python measureCrossSection_2012.py -v ST -k 6
python plotCrossSections.py -v ST -k 6
python measureCrossSection_2012.py -v ST -k 7
python plotCrossSections.py -v ST -k 7

python measureCrossSection_2012.py -v MT -k 2
python plotCrossSections.py -v MT -k 2
python measureCrossSection_2012.py -v MT -k 3
python plotCrossSections.py -v MT -k 3
python measureCrossSection_2012.py -v MT -k 4
python plotCrossSections.py -v MT -k 4
python measureCrossSection_2012.py -v MT -k 5
python plotCrossSections.py -v MT -k 5
