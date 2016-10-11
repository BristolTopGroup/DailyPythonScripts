#!/usr/bin/python

'''
StorageDump v2.0
author: Iban Cabrillo
'''

import os
import sys
#import urllib
#import urllib2
import datetime
import subprocess
#from xml.dom import minidom


def get_local_cksum(surl, lfn, alder_path, modify = False):
    '''
    Get the cksum store at local file level. If the file has no cksum value we should calc it.
    '''
    #Look for the adler32 value 
    output, error = subprocess.Popen(['getfattr', '--only-values', '--absolute-names', '-n', 'user.storm.checksum.adler32', surl],
                                     stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    cksum = 'N/A'
    
    if len(output) == 0:
       print "No checksum value found for file %s. Processing..." % lfn
       try:
           #Calc the adler32 value
           adler32, error = subprocess.Popen([adler_path, surl], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
           cksum = adler32.rstrip('\n').lstrip('0')
       except OSError:
           print 'Could not calculate cksum:', error
       
       # Delete the \n on the right and the 0's on the left to be the same adler32 format that is stored by the phedex API
       # and set the adler32 value for the file.
       if modify:
           try:
               setadler32, error = subprocess.Popen(['setfattr', '-n', 'user.storm.checksum.adler32', '-v', cksum, surl],
                                            stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
           except OSError:
               print 'Could not set extra attribute for cksum:', error
       
       print "Calculated cksum:", cksum
    else:
       cksum = output.rstrip('\n')
       
    return cksum

def get_local_timestamp(surl, lfn, modify = False):
    '''
    Get the mtime store for local file as extra attribute. If the file has no this 
    value stored we calc it.
    '''
    #Look for the adler32 value
    output, error = subprocess.Popen(['getfattr', '--only-values', '--absolute-names', '-n', 'user.timestamp', surl],
                                     stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    timestamp = 0
    if len(output) == 0:
        print "No timestamp value found for file %s. Processing..." % lfn
        #Calc de timestamp value
        timestamp = str(os.stat(surl).st_ctime).rstrip('\n')

        if modify:
            try:
                # Set the timstamp value for the file.
                settimestamp, error = subprocess.Popen(['setfattr', '-n', 'user.timestamp', '-v', timestamp, surl],
                                              stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
            except OSError:
                print 'Could not set extra attribute for timestamp:', error
            
        print "Calculated timestamp:", timestamp                                      
    else:
        timestamp = output.rstrip('\n')
       
    return timestamp


def get_local_size(surl, lfn, modify = False):
    '''
    Get the size of local file from extra attribute. If the file has no value stored we calculate it.
    '''
    #Look for the adler32 value
    output, error = subprocess.Popen(['getfattr', '--only-values', '--absolute-names', '-n', 'user.size', surl],
                                     stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    size = 0
    if len(output) == 0:
        print "No size value found as extra attribute for file %s. Processing..." % lfn

        #Calculate the timestamp value
        size = str(os.stat(surl).st_size).rstrip('\n')
        if modify:
            try:
                # Set the timestamp value for the file.
                setsize, error = subprocess.Popen(['setfattr', '-n', 'user.size', '-v', size, surl], stderr=subprocess.PIPE,
                                          stdout=subprocess.PIPE).communicate()
            except OSError:
                print 'Could not set extra attribute for size', error
        print "Calculated size:", size    
    else:
        size = output.rstrip('\n')
    return size

def print_storage_dump(lfn, size, ctime, cksum):
    '''
    Create a file with keys: lfn, size, timestamp, cksum
    '''

    f = open(DumpFile, 'a')
    line = '%s|%s|%s|%s\n' % (lfn, size, ctime, cksum)
    f.write(line)


def getopts():
    '''
    Get the command line arguments
    '''
          
    from optparse import OptionParser
                    
    parser = OptionParser()
    parser.add_option('--localpath', '-p', action='store',
                      type='string', dest='localpath', default='/gpfs/csic_projects/cms/',
                      help='Local prefix to your file system to complete the plfn'
                      )
    
    parser.add_option('--dumpfilepath', '-l', action='store',
                      type='string', dest='dumpfilepath', default='~/',
                      help='Path where the file with the lfns will be written')
    (opt, arg) = parser.parse_args()
    return opt
 
if __name__ == '__main__':
###########################Globals################################
    #Path to file where the lfns will be written
    DumpFile = 'DumpFile_%s.log' % datetime.date.today()
##################################################################
    cmsdir = '/gpfs_phys/storm/cms/'
    adler_path = 'adler32/calc_adler32.py'
    #bristol
    alder_path = '/opt/g/ui/3.2.5-0/d-cache/srm/bin/adler32'

    

    try:
        myargs = getopts()
        cmsdir = myargs.localpath
        dumpfilepath = myargs.dumpfilepath
        if not dumpfilepath.endswith('/'):
            dumpfilepath += '/'
        DumpFile = dumpfilepath + 'DumpFile_%s.log' % datetime.date.today()

    except KeyError: 
        print "missing some mandatory parameters, please run <check_cks.py -h >"
        sys.exit()

    try:
        for tupla in os.walk(cmsdir):
            if tupla[2]:
                for file in tupla[2]:
                    surl = tupla[0] + '/' + file
                    lfn = surl.replace(cmsdir, '')
                    try:
                        size = get_local_size(surl, lfn)
                        timestamp = get_local_timestamp(surl, lfn)
                        cksum = get_local_cksum(surl, lfn, adler_path)
                        
                        print_storage_dump(lfn, size, timestamp, cksum)
                    except OSError:
                        print "Uknown error occured"
 
    except IndexError:
        print "The file doesn't exits"
        pass
