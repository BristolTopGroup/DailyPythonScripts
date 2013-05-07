#!/env

import os
import sys
from fileInfo import *
from optparse import OptionParser
import time

skipGroupsUntil = 0
startWithGroup = 1
sizePerFile = 1024 * 1024 * 1024 * 2
timeCut = 0

def groupFilesToSize(files, finalSize=1024 * 1024 * 1024 * 2):# < 2 GB
    getsize = os.path.getsize
    groupSize = 0
    groups = [[]]
    groupIndex = 0
    for file in sorted(files):
        size = getsize(file)
        if (groupSize + size) > finalSize:#start new group
            groupIndex += 1
            groups.append([])
            groupSize = 0
        groupSize += size    
        groups[groupIndex].append(file)
    return groups

def fuseFiles(groupedFiles):
    group = startWithGroup
    
    for files in groupedFiles:
        outputFile = getProcess(files[0]) + '_merged_%03d' % group
        outputFile += '.root'
        command = 'hadd -f7 %s ' % outputFile
        for file in files:
            command += file + ' '
        command.rstrip(' ')
        print '=' * 100
        print '*' * 100
        if group > skipGroupsUntil:
            print 'Executing:'
        else:
            print 'Skipping:'
        print command
        print '*' * 100
        print '=' * 100
        if group > skipGroupsUntil and not options.dryRun:
            os.system(command)
        group += 1

def getProcess(filepath):
    file = filepath.split('/')[-1]
    a = file.split('_')
    process = 'default'
    if len(a) <= 5:
        process = a[0] + '_' + a[1]
    else:
        process = a[0]
        for token in a[1:-3]:
            process += '_' + token
    return process
    

def removeUsedFiles(allFiles, usedFiles):
    allFiles = set(allFiles)
    usedFiles = set(usedFiles)
    return allFiles.difference(usedFiles)

def readMergeLog(mergeLog):
    usedFiles = []
    mergeLog = file(mergeLog)
    lastOutputFileNumber = 0
    for line in mergeLog.readlines():
        if line.startswith('hadd Source file'):
            input = line.split(' ')
            inputfile = input[4].replace('\n', '')
            usedFiles.append(inputfile)
            
        if line.startswith('hadd -f7'):
            input = line.split(' ')
            outputfile = input[2]
            number = outputfile.replace('.root', '')
            number = number.split('_')[-1]
            lastOutputFileNumber = int(number)
    global startWithGroup
    startWithGroup = lastOutputFileNumber + 1
    return usedFiles
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-s", "--size", dest="sizePerFile", default=1024 * 2,
                  help="Set maximum size of output files in MB. Default 2 GB (2048 MB)")
    parser.add_option("-t", "--time", dest="timeCut", default='01 01 2000',
                      help="Cut on creation time. Only consider files for merging after a certain date. Format: DD MM YYYY. Default: 01 Jan 2000")
    parser.add_option("-c", "--continue",
                  action="store_true", dest="continueMerge", default=False,
                  help="Continue merging in the current directory. Merge log must be specified!")
    parser.add_option("-l", "--log", dest="mergeLog", default='merge.log',
                      help="Merge log to be used for continuation.")
    parser.add_option("-n", "--no-merge", dest="dryRun", action="store_true", default=False,
                      help="Do not merge any files.")
                    
    (options, args) = parser.parse_args()
    sizePerFile = 1024 * 1024 * float(options.sizePerFile)
    timeCut = time.mktime(time.strptime(options.timeCut, '%d %m %Y'))
    
    continueLastMerge = False
    allButUsedFiles = []
    groupedFiles = []
    
   #args = sys.argv
    if not len(args) >= 1:
        print "Please specify a folder to merge files in."
        sys.exit()
    
    path = sys.argv[1]
    files = getROOTFiles(path)
    #implement the timeCut here!
    files = filterFilesByTime(files=files, filesNewerThan = timeCut)
    uniqueFiles = getUniqueFiles(files)
    
    if options.continueMerge:
        continueLastMerge = True
        usedFiles = readMergeLog(options.mergeLog)
        allButUsedFiles = removeUsedFiles(uniqueFiles, usedFiles)
        
    if not continueLastMerge:
        groupedFiles = groupFilesToSize(uniqueFiles, sizePerFile)
    else:
        groupedFiles = groupFilesToSize(allButUsedFiles, sizePerFile)
    
    print 'Process recognised:', getProcess(files[0])
    print 'Total number of files:', len(files)
    print 'Total number of unique files:', len(uniqueFiles)
    if continueLastMerge:
        print 'Total number of remaining files:', len(allButUsedFiles)
        if len(allButUsedFiles) == 0:
            print 'Nothing to merge, exiting.'
            sys.exit()
    print 'Target size of output file', sizePerFile
    print 'Number of merged files to be produced:', len(groupedFiles)
    
    fuseFiles(groupedFiles)

