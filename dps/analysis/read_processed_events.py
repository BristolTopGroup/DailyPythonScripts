'''
Created on 13 Dec 2012

@author: kreczko

Read the /storage/TopQuarkAnalysis/mc folder (or one specified)
If folder name ends with 7 or 8TeV then produce a single output
If the folder contains 7 or 8 TeV then produce two results
Otherwise exit script

Read all folders and interpret them as MC
subfolder needs to contain ntuple_<version> ...
and that should contain ROOT files

Read all ROOT files and get the number of processed events
'''
