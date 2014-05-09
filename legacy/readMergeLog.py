
mergeLog = file('merge.log')

groups = []
groupIndex = 0
foundStart = False
for line in mergeLog.readlines():
    
    if line.startswith('hadd'):
        print '='*200
        foundStart = True
        groups.append([])
        #split by space
        input = line.split(' ')
        #first 3 entries are command, parameter and output file, rest are the input files
        outputfile = input[2]
#        inputfiles = input[3:]
        print 'Output file:', outputfile
#        for file in inputfiles:
#            print file
            
    if line.startswith('Sources and Target'):
        foundStart = False
        groupIndex += 1
        print '='*200
        
    if foundStart:
        if line.startswith('Source file'):
            input = line.split(' ')
            file = input[3].replace('\n', '')
            groups[groupIndex].append(file)
            print file
        
print 'Number of groups:', len(groups)