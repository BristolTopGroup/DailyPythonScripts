#!/bin/bash

#python getFitResults_2012.py -v MET
#python getFitResults_2012.py -v HT
#python getFitResults_2012.py -v ST
#python getFitResults_2012.py -v MT


python unfoldAndMeasure_2012.py -v MET -k 3
python unfoldAndMeasure_2012.py -v MET -k 4
python unfoldAndMeasure_2012.py -v MET -k 5
python unfoldAndMeasure_2012.py -v MET -k 6

python unfoldAndMeasure_2012.py -v HT -k 4
python unfoldAndMeasure_2012.py -v HT -k 5
python unfoldAndMeasure_2012.py -v HT -k 6
python unfoldAndMeasure_2012.py -v HT -k 7

python unfoldAndMeasure_2012.py -v ST -k 4
python unfoldAndMeasure_2012.py -v ST -k 5
python unfoldAndMeasure_2012.py -v ST -k 6
python unfoldAndMeasure_2012.py -v ST -k 7

python unfoldAndMeasure_2012.py -v MT -k 2
python unfoldAndMeasure_2012.py -v MT -k 3
python unfoldAndMeasure_2012.py -v MT -k 4
python unfoldAndMeasure_2012.py -v MT -k 5


python plotCrossSections.py -v MET -k 3
python plotCrossSections.py -v MET -k 4
python plotCrossSections.py -v MET -k 5
python plotCrossSections.py -v MET -k 6

python plotCrossSections.py -v HT -k 4
python plotCrossSections.py -v HT -k 5
python plotCrossSections.py -v HT -k 6
python plotCrossSections.py -v HT -k 7

python plotCrossSections.py -v ST -k 4
python plotCrossSections.py -v ST -k 5
python plotCrossSections.py -v ST -k 6
python plotCrossSections.py -v ST -k 7

python plotCrossSections.py -v MT -k 2
python plotCrossSections.py -v MT -k 3
python plotCrossSections.py -v MT -k 4
python plotCrossSections.py -v MT -k 5


python printCrossSections.py -v MET -k 3
python printCrossSections.py -v MET -k 4
python printCrossSections.py -v MET -k 5
python printCrossSections.py -v MET -k 6

python printCrossSections.py -v HT -k 4
python printCrossSections.py -v HT -k 5
python printCrossSections.py -v HT -k 6
python printCrossSections.py -v HT -k 7

python printCrossSections.py -v ST -k 4
python printCrossSections.py -v ST -k 5
python printCrossSections.py -v ST -k 6
python printCrossSections.py -v ST -k 7

python printCrossSections.py -v MT -k 2
python printCrossSections.py -v MT -k 3
python printCrossSections.py -v MT -k 4
python printCrossSections.py -v MT -k 5
