import os

do7TeV = True
do8TeV = False

doCentral = True

scaleSyst = False
matchingSyst = False

topPtReweighting = True

pdfVariations = False

otherGenerators = False


# Construct list of jobs
jobs = [
        ]

if do8TeV:
    # 8 TeV
    # Central
    if doCentral:
        jobs.append('')
    
    # Scale up/down
    if scaleSyst:
        jobs.append('-s scaleup')
        jobs.append('-s scaledown')
        pass
    
    # Matching up/down
    if matchingSyst:
        jobs.append('-s matchingup')
        jobs.append('-s matchingdown')
        pass
    
    # Other generators
    if otherGenerators:
        jobs.append('-s powheg')
        jobs.append('-s mcatnlo')
        pass
    
    # Top pt reweighting
    if topPtReweighting:
        jobs.append('--topPtReweighting')
        pass
    pass

if do7TeV:
    # 7 TeV
    # Central
    if doCentral:
        jobs.append('--is7TeV')
    
    # Top pt reweighting
    if topPtReweighting:
        jobs.append('--is7TeV --topPtReweighting')
        pass
    pass

# Add pdf systematic jobs
if pdfVariations:
    for variation in range (1,2+1):
        # 8 TeV
        if do8TeV:
            jobs.append('-p %i' % variation)
            pass
        
        # 7 TeV
        if do7TeV:
            jobs.append(' --is7TeV -p %i' % variation)
            pass
        pass

# Set up job for each job
for job in jobs:
    command = 'nohup python DailyPythonScripts/src/BLTUnfold/produceUnfoldingHistograms.py '+job+' &> unfolding/log_'+job.replace(' ','').replace('-','')+'.log &'
    os.system(command)
    pass
