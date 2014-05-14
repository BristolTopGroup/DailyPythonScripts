#!/env
from __future__ import division
import os
import sys
import glob
from fileInfo import *

def getFileSizes(files):# < 3 GB
    totalSize = 0
    maxSize = 0
    minSize = 99999999999999
    SIZE = os.path.getsize
    for file in files:
        size = SIZE(file)
        if size < minSize:
            minSize = size
        if size > maxSize:
            maxSize = size
        totalSize += size    
    return {'min': minSize, 'max': maxSize, 'total': totalSize}


if __name__ == "__main__":
    args = sys.argv
    if not len(args) == 2:
        print "Please specify a folder to analyze."
        sys.exit()
        
    path = sys.argv[1]
    files = getROOTFiles(path)
    sizes = getFileSizes(files)
    print 'Total size of files: %.3f MB' % (sizes['total']/10**6)
    print 'Number of files: %d'% len(files)
    print 'Minimal file size: %.3f MB'% (sizes['min']/10**6)
    print 'Maximal file size: %.3f MB'% (sizes['max']/10**6)
    print 'Average file size: %.3f MB'% (sizes['total']/10**6/len(files))
    print 'target max file size: 250MB', '=> scale factor =', (10**9)/4/sizes['max']