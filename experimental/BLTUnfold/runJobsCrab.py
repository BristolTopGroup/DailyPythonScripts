from optparse import OptionParser
import os

jobs = [
#         # 8 TeV
#         # Central
#          '--centreOfMassEnergy 8 -s central',
#           
#         # Scale up/down
#         '--centreOfMassEnergy 8 -s scaleup',
#         '--centreOfMassEnergy 8 -s scaledown',
#             
#         # Matching up/down
#         '--centreOfMassEnergy 8 -s matchingup',
#         '--centreOfMassEnergy 8 -s matchingdown',
#             
#         # # Other generators
#         '--centreOfMassEnergy 8 -s powheg',
#         '--centreOfMassEnergy 8 -s powhegherwig',
#         '--centreOfMassEnergy 8 -s mcatnlo',
#   
#         # Mass up/down
#         '--centreOfMassEnergy 8 -s massup',
#         '--centreOfMassEnergy 8 -s massdown',
#           
#         # Top pt reweighting
        '--centreOfMassEnergy 8 --topPtReweighting',
#            
#         # 7 TeV
#         # Central
#         '--centreOfMassEnergy 7 -s central',
#    
#         # Scale up/down
#         '--centreOfMassEnergy 7 -s scaleup',
#         '--centreOfMassEnergy 7 -s scaledown',
#    
#         # Matching up/down
#         '--centreOfMassEnergy 7 -s matchingup',
#         '--centreOfMassEnergy 7 -s matchingdown',
#    
#         # # Other generators
#         '--centreOfMassEnergy 7 -s powheg',
#         '--centreOfMassEnergy 7 -s powhegherwig',
#    
#         # Mass up/down
#         '--centreOfMassEnergy 7 -s massup',
#         '--centreOfMassEnergy 7 -s massdown',
#                    
#         # Top pt reweighting
        '--centreOfMassEnergy 7 --topPtReweighting',
        ]

#  Add pdf variations to list of jobs
# for variation in range(1,45+1):
#     jobs.append('--centreOfMassEnergy 8 -p %i' % variation)
#     jobs.append('--centreOfMassEnergy 7 -p %i' % variation)
#     pass

# print len(jobs)
parser = OptionParser()
parser.add_option('-j','--job_number',type='int',dest='jobNumber',default=0)
(options, _) = parser.parse_args()
       
print 'Running job :',jobs[options.jobNumber-1]
os.system('python experimental/BLTUnfold/produceUnfoldingHistograms.py %s ' % jobs[options.jobNumber-1] )
