#!/usr/bin/python
'''
Created on 1 Jun 2010

@author: kreczko

Email: kreczko@cern.ch
'''

from optparse import OptionParser
import os
import copy
import glob
import sys
import ROOT
rootFile = ROOT.TFile

duplicates = []
duplicateFiles = {}

def getROOTFiles(path):
    path += "/*.root"
    files = glob.glob(path)
    return files

def getUniqueFiles(files):
    if listContainsDuplicates(files):
        findDuplicates(files)
    else:
        return files
    uniqueFiles = copy.copy(files)
    for values in duplicateFiles.itervalues():
        for value in values:
            if value in uniqueFiles:
                uniqueFiles.remove(value)
        values.sort()
        uniqueFiles.append(values[-1])
    return uniqueFiles

def listContainsDuplicates(list):
    seen = []
    for item in list:
        jobnumber = extractJobnumber(item)
        if jobnumber in seen:
            duplicates.append(jobnumber)
        else:
            seen.append(jobnumber)
    return len(duplicates) >0

def findDuplicates(files):
    for file in files:
        for job in duplicates:
            if job == extractJobnumber(file):
                addDuplicate(job, file)
        
def extractJobnumber(file):
    jobnumber = file.split('_')[-3]
    number = 0
    try:
        number = int(jobnumber)
    except:
        print "Could not find the job number for"
        print file
        print 'exiting...'
        sys.exit(-1)
    return number

def addDuplicate(jobnumber, file):
    if not duplicateFiles.has_key(jobnumber):
        duplicateFiles[jobnumber] = []
    duplicateFiles[jobnumber].append(file)

def getDuplicateFiles(allFiles, uniqueFiles):
    filesToRemove = [file for file in allFiles if not file in uniqueFiles]
    return filesToRemove

def checkFiles(files):
    goodFiles = []
    badFiles = []
    
    for file in files:
        if checkFile(file):
            goodFiles.append(file)
        else:
            badFiles.append(file)
            
    return goodFiles, badFiles

def checkFile(file):
    passesCheck = False
    
    try:
        openFile = rootFile.Open(file)
        if openFile:
            passesCheck = True
    except:
        print "Could not open ROOT file"
    
    return passesCheck


if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    parser = OptionParser()
    parser.add_option("-c", "--check",
                  action="store_false", dest="check", default=True,
                  help="check if files are valid files ")
    (options, args) = parser.parse_args()
    if len(args) >0:
        
        path = args[0]
        files = getROOTFiles(path)
        files.sort()
        if options.check:
            print 'checking files'
            good, bad = checkFiles(files)
            print 'Number of good files', len(good)
            print 'Number of bad files', len(bad)
        uniqueFiles = getUniqueFiles(files)
        uniqueFiles.sort()
        duplicateFiles = getDuplicateFiles(files, uniqueFiles)
        print 'Number of file in path:', len(files)
        print 'Number of unique files', len(uniqueFiles)
        print 'Number of duplicate files:', len(duplicateFiles)
        if len(duplicateFiles) > 0:
            print 'Files to remove:'
        for file in duplicateFiles:
            print path + file
        if options['check']:
            print 'check files'
    else:
        print 'File path was not specified. Use script "./remove_duplicates path"'
        
#print a list of
#Files in 'Folder'
# FileName, size, reason to delete
#Do you want to delete these files? (Y/N) [need valid grid certificate]: