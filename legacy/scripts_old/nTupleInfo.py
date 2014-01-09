'''
Created on Mar 5, 2011

@author: lkreczko
'''
from __future__ import division
from ROOT import *
import sys, os
from math import sqrt

def getBranchInfo(listOfBranches):
    branches = []
    bapp = branches.append
    for branch in listOfBranches:
        info = {}
        info['name'] = branch.GetName()
        info['totalSize'] = branch.GetTotalSize()
        info['totalBytes'] = branch.GetTotBytes()
        info['zippedBytes'] = branch.GetZipBytes()
        bapp(info)
    return branches


def printTwikiTable(branches, filesize):
    
    prevObj = ' '
    info = {}
    info['totalSize'] = 0
    info['zippedBytes'] = 0
    info['totalBytes'] = 0
    for branch in sorted(branches):
        name = branch['name']
        size = branch['totalSize'] / 1024 / 1024 #MB
        zipSize = branch['zippedBytes'] / 1024 / 1024#MB
        compression = size / zipSize
        totalBytes = branch['totalBytes'] / 1024 / 1024#MB
        buffer = (size - totalBytes) * 1024#KB
        fraction = zipSize / filesize * 100#%
        
        obj = ' '
        if '.' in name:
            obj = name.split('.')[0] + '.'
        else:
            obj = name.capitalize()
        
        if not name.startswith(prevObj):
            if '.' in prevObj:
                Osize = info['totalSize']
                OzipSize = info['zippedBytes']
                Ocompression = Osize / OzipSize
                Obuffer = (size - info['totalBytes'] / 1024 / 1024) * 1024#KB
                Ofraction = OzipSize / filesize * 100
                
                print '| *Total*  |  %.3f |  %.3f | %.2f |  %.3f |  %.2f%% |' % (Osize, OzipSize, Ocompression, Obuffer, Ofraction)
                print '%ENDTWISTY%'
                print
            #print summary
            print '---+++ %s' % obj.replace('.', '')
            print '%TWISTY{mode="div" showlink="Show&nbsp;" hidelink="Hide&nbsp;"  firststart="hide" showimgright="%ICONURLPATH{toggleopen-small}%" hideimgright="%ICONURLPATH{toggleclose-small}%"}%'
            print '|  *%s*  ||||||' % obj.replace('.', '')
            print '| *Name* | *Total Size (MB)* | *Compressed size (MB)* | *compression factor* | *Buffer (KB)* | *Fraction of file size* |'
            info['totalSize'] = 0
            info['zippedBytes'] = 0
            info['totalBytes'] = 0
        else:
            info['totalSize'] += size
            info['zippedBytes'] += zipSize
            info['totalBytes'] += totalBytes
        print '| !%s  |  %.3f |  %.3f | %.2f |  %.3f |  %.2f%% |' % (name, size, zipSize, compression, buffer, fraction)
        prevObj = obj
    print '%ENDTWISTY%'

def printBiggestConsumers(branches, filesize):
    consumers = []
    for branch in sorted(branches):
        consumer = {}
        zipSize = branch['zippedBytes'] / 1024 / 1024#MB
        fraction = zipSize / filesize * 100#%
        consumer[branch['zippedBytes']] = branch
        consumers.append(consumer)
    top = 10
    current = 1
    
    print '| *Name* | *Compressed size (MB)* | *Fraction of file size* |'
    for consumer in sorted(consumers, reverse=True):
        if current > top:
            break
        
        current += 1
        branch = consumer[consumer.keys()[0]]
        zipSize = branch['zippedBytes'] / 1024 / 1024#MB
        print '| !%s  |  %.3f |  %.3f%% |' %(branch['name'], zipSize, zipSize / filesize * 100)#%)
#        print branch['name'], zipSize, zipSize / filesize * 100#%

def getTriggers(chain):
    for event in chain:
        triggers = event.__getattr__("Trigger.HLTNames")
        for trigger in triggers:
            if not 'not found' in trigger:
                print '   * ' + trigger
        break      
        
if __name__ == '__main__':
    gROOT.SetBatch(1);
    chain = TChain("rootTupleTree/tree");
    filesize = 0
    
    if len(sys.argv) < 2:
        print 'wrong usage'
        
    files = sys.argv[1:]
    add = chain.Add
    size = os.path.getsize
        
    for file in files:
        add(file)
        filesize += size(file)

    filesize = filesize/ 1024 / 1024#MB

    branches = getBranchInfo(chain.GetListOfBranches())
    numberOfEvents = chain.GetEntries()
    if '_data_' in files[0]:
        print '---++ DATA content'
    else:
        print '---++ MC content'
    
    sizePerEvent = filesize/numberOfEvents*1024
    print 'Size of event: %.3f KB +- %.3f' % (sizePerEvent, 1/sqrt(numberOfEvents)*sizePerEvent)
    printTwikiTable(branches, filesize)
    
    print '---+++ Biggest consumers'
    printBiggestConsumers(branches, filesize)
    
    print '---+++ Available Triggers'
    getTriggers(chain)
