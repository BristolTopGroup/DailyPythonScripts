#!/usr/bin/env python
from optparse import OptionParser
import os
from copy import deepcopy

jobs = [
        # # 13 TeV
        # '--centreOfMassEnergy 13 -f',

        '--centreOfMassEnergy 13 -s central',

        # '--centreOfMassEnergy 13 -s central_firstHalf',
        # '--centreOfMassEnergy 13 -s central_secondHalf',

        # '--centreOfMassEnergy 13 -s central_firstHalf --topPtReweighting 1',
        # '--centreOfMassEnergy 13 -s central_secondHalf --topPtReweighting 1',
        # '--centreOfMassEnergy 13 -s central_firstHalf --topPtReweighting -1',
        # '--centreOfMassEnergy 13 -s central_secondHalf --topPtReweighting -1',

        '--centreOfMassEnergy 13 -s amcatnlo',
        '--centreOfMassEnergy 13 -s madgraph',
        '--centreOfMassEnergy 13 -s powhegherwigpp',

        # Top pt
        '--centreOfMassEnergy 13 -s topPtSystematic',

        # Underlying event samples
        '--centreOfMassEnergy 13 -s ueup',
        '--centreOfMassEnergy 13 -s uedown',

        # # isr/fsr variations
        '--centreOfMassEnergy 13 -s isrup',
        '--centreOfMassEnergy 13 -s isrdown',
        '--centreOfMassEnergy 13 -s fsrup',
        '--centreOfMassEnergy 13 -s fsrdown',


        # hdamp up/down
        '--centreOfMassEnergy 13 -s hdampup',
        '--centreOfMassEnergy 13 -s hdampdown',

        # erdOn
        '--centreOfMassEnergy 13 -s erdOn',
        '--centreOfMassEnergy 13 -s QCDbased_erdOn',
        '--centreOfMassEnergy 13 -s GluonMove',

        # ME scale weights
        '--centreOfMassEnergy 13 --muFmuRWeight 1',
        '--centreOfMassEnergy 13 --muFmuRWeight 2',
        '--centreOfMassEnergy 13 --muFmuRWeight 3',
        '--centreOfMassEnergy 13 --muFmuRWeight 4',
        '--centreOfMassEnergy 13 --muFmuRWeight 6',
        '--centreOfMassEnergy 13 --muFmuRWeight 8',

        '--centreOfMassEnergy 13 --alphaSWeight 0',
        '--centreOfMassEnergy 13 --alphaSWeight 1',

        # B fragmentation weights
        '--centreOfMassEnergy 13 --fragWeight 1',
        '--centreOfMassEnergy 13 --fragWeight 2',
        '--centreOfMassEnergy 13 --fragWeight 3',
        '--centreOfMassEnergy 13 --fragWeight 4',

        # Semileptonic BR
        '--centreOfMassEnergy 13 --semiLepBrWeight -1',
        '--centreOfMassEnergy 13 --semiLepBrWeight 1',

        # Top mass
        '--centreOfMassEnergy 13 -s massup',
        '--centreOfMassEnergy 13 -s massdown',

        # Experimental systematics
        '--centreOfMassEnergy 13 -s jesup',
        '--centreOfMassEnergy 13 -s jesdown',

        '--centreOfMassEnergy 13 -s jerup',
        '--centreOfMassEnergy 13 -s jerdown',

        '--centreOfMassEnergy 13 -s electronup',
        '--centreOfMassEnergy 13 -s electrondown',
        '--centreOfMassEnergy 13 -s muonup',
        '--centreOfMassEnergy 13 -s muondown',

        '--centreOfMassEnergy 13 -s bjetup',
        '--centreOfMassEnergy 13 -s bjetdown',

        '--centreOfMassEnergy 13 -s lightjetup',
        '--centreOfMassEnergy 13 -s lightjetdown',

        '--centreOfMassEnergy 13 -s pileupUp',
        '--centreOfMassEnergy 13 -s pileupDown',

        '--centreOfMassEnergy 13 -s ElectronEnUp',
        '--centreOfMassEnergy 13 -s ElectronEnDown' ,
        '--centreOfMassEnergy 13 -s MuonEnUp',
        '--centreOfMassEnergy 13 -s MuonEnDown',
        '--centreOfMassEnergy 13 -s TauEnUp',
        '--centreOfMassEnergy 13 -s TauEnDown',
        '--centreOfMassEnergy 13 -s UnclusteredEnUp',
        '--centreOfMassEnergy 13 -s UnclusteredEnDown',
        ]

#  Add pdf variations to list of jobs
minPDF = 0
maxPDF = 99
variation = minPDF
while variation <= maxPDF :
    jobs.append('--centreOfMassEnergy 13 --pdfWeight {} '.format(variation) )
    variation += 1
    pass

# maxPDF = 54
# variation = minPDF
# while variation <= maxPDF :
#     jobs.append('--centreOfMassEnergy 13 --CT14Weight {} '.format(variation) )
#     variation += 1
#     pass

# maxPDF = 55
# variation = minPDF
# while variation <= maxPDF :
#     jobs.append('--centreOfMassEnergy 13 --MMHT14Weight {} '.format(variation) )
#     variation += 1
#     pass

# jobsWithNewPS = deepcopy( jobs )
jobsWithNewPS = []
for job in jobs:
    jobsWithNewPS.append( job + ' --newPS')
jobs = jobsWithNewPS

def parse_args(parameters = []):
    parser = OptionParser( __doc__ )
    parser.add_option( '--return_job_options', dest = 'return_job_options', action = "store_true",
                       help = 'Return the options for the job you are running'  )
    parser.add_option( '--return_nJobs', dest = 'return_nJobs', action = "store_true",
                       help = 'Return the total number of jobs'  )
    parser.add_option('-j','--job_number',type='int',dest='jobNumber',default=0)

    options, args = None, None
    if len(parameters) > 0:
        ( options, args ) = parser.parse_args(parameters)
    else:
        ( options, args ) = parser.parse_args()
    return options, args

def main(options, args = []):
    if options.return_nJobs:
        return len(jobs)

    if options.return_job_options:
        return jobs[options.jobNumber-1]

    parser = OptionParser()
          
    print 'Running job :',jobs[options.jobNumber-1]
    os.system('python dps/analysis/BLTUnfold/produceUnfoldingHistograms.py %s ' % jobs[options.jobNumber-1] )

if __name__ == '__main__':
    options, args = parse_args()
    print main(options, args)
