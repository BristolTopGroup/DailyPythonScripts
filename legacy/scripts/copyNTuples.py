'''
Created on Nov 23, 2011

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''

if __name__ == "__main__":
    basePathToData = '/storage/TopQuarkGroup'
    
    #steps to do
    #1. create folder structure (Dataset/nTupleVersion)
    #2. check for corrupt files - if found, ask if wants to remove (grid certificate required)
    #3. check for duplicates - if found, ask if wants to remove (grid certificate required)
    #run options:
    #check-only
    #skim info only
    
    #print output of hadd
#    Total number of files: N
#    Total number of unique files: M
#    Process recognised: Sample
#    Input files per output file: X
#    Input directory:  /gpfs_phys/storm/cms/user/<path>
#    Using compression level Z
#    ==================================================
#    Creating output file: Sample_merged_I.root
#    Number of input files: Y
#    CRAB job number of input files: 1-2, 4,7, 10-33
#    ==================================================


#    supress output of hadd except for debug flag
#    Source file N
#    ...

#group by max size of output
#group by number of output files
#create mergeROOTFiles.log automatically (full logging), print summarised output somewhere else
#print warning when more than 500 files are going to be merged. ROOT can't handle this!!
#alternative: create temporary files so max 500 files per output file, merge the temp files and then remove them!
    