#!/usr/bin/env python
from optparse import OptionParser
import os

jobs = [
        # # 13 TeV
        '--centreOfMassEnergy 13 -f',

        '--centreOfMassEnergy 13 -s central',
        '--centreOfMassEnergy 13 -s central --topPtReweighting 1',
        '--centreOfMassEnergy 13 -s central --topPtReweighting -1',

        '--centreOfMassEnergy 13 -s amcatnlo',
        '--centreOfMassEnergy 13 -s madgraph',
        '--centreOfMassEnergy 13 -s powhegherwigpp',
        # '--centreOfMassEnergy 13 -s amcatnloherwigpp',

        # # PS scale samples
        # '--centreOfMassEnergy 13 -s scaleup',
        # '--centreOfMassEnergy 13 -s scaledown',

        # ME scale weights
        '--centreOfMassEnergy 13 --muFmuRWeight 1',
        '--centreOfMassEnergy 13 --muFmuRWeight 2',
        '--centreOfMassEnergy 13 --muFmuRWeight 3',
        '--centreOfMassEnergy 13 --muFmuRWeight 4',
        '--centreOfMassEnergy 13 --muFmuRWeight 6',
        '--centreOfMassEnergy 13 --muFmuRWeight 8',

        '--centreOfMassEnergy 13 --alphaSWeight 0',
        '--centreOfMassEnergy 13 --alphaSWeight 1',

        # # Top mass
        '--centreOfMassEnergy 13 -s massup',
        '--centreOfMassEnergy 13 -s massdown',

        # # Experimental systematics
        '--centreOfMassEnergy 13 -s jesup',
        '--centreOfMassEnergy 13 -s jesdown',

        '--centreOfMassEnergy 13 -s jerup',
        '--centreOfMassEnergy 13 -s jerdown',

        '--centreOfMassEnergy 13 -s leptonup',
        '--centreOfMassEnergy 13 -s leptondown',

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
# #  Add pdf variations to list of jobs
nPDFPerJob = 1
minPDF = 0
maxPDF = 99
variation = minPDF
while variation <= maxPDF :
    nForThisJob = nPDFPerJob
    if variation + nPDFPerJob > maxPDF:
        nForThisJob = maxPDF - variation
    jobs.append('--centreOfMassEnergy 13 --pdfWeight %i --nGeneratorWeights %i' % (variation, nForThisJob) )
    variation += nPDFPerJob
    pass

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
