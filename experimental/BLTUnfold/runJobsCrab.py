from optparse import OptionParser
import os

jobs = [
        # 8 TeV
        # Central
        '',
        
        # Scale up/down
        '-s scaleup',
        '-s scaledown',
         
        # Matching up/down
        '-s matchingup',
        '-s matchingdown',
         
        # Other generators
        '-s powheg',
        '-s powhegherwig',
        '-s mcatnlo',
        
        # Top pt reweighting
        '--topPtReweighting',
        
        # 7 TeV
        # Central
        '--is7TeV',

        # Scale up/down
        '--is7TeV -s scaleup',
        '--is7TeV -s scaledown',
                
        # Top pt reweighting
        '--is7TeV --topPtReweighting',
        ]

 # Add pdf variations to list of jobs
# for variation in range(1,45+1):
#     jobs.append('-p %i' % variation)
#     jobs.append('--is7TeV -p %i' % variation)
#     pass
    
parser = OptionParser()
parser.add_option('-j','--job_number',type='int',dest='jobNumber',default=0)
(options, _) = parser.parse_args()

print 'Running job :',jobs[options.jobNumber-1]
os.system('python experimental/BLTUnfold/produceUnfoldingHistograms.py %s ' % jobs[options.jobNumber-1] )

