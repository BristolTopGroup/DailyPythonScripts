import csv
import sys

''' Summarises the results given by the makeHLTPrescaleTable.py script in
https://twiki.cern.ch/twiki/bin/viewauth/CMS/HLTriggerTools#make_HLTPrescaleTable_py
'''

def getTriggers(csvFileName):
    file = open(csvFileName, 'rb')
    data = csv.reader(file, delimiter = ';')
    fieldNames = getFieldNames(data)
    triggers, prescaledTriggers = createTriggerDictionaries(fieldNames)
    
    reader = csv.DictReader( file, fieldnames = fieldNames ,delimiter = ';')
    triggers, prescaledTriggers = fillTriggers(reader, triggers, prescaledTriggers)
    return triggers, prescaledTriggers
    
def getFieldNames(data):
    fieldNames = []
    for row in data:
        #look for first row starting with 'run'
        if len(row) > 0 and row[0] == 'run':
            fieldNames = row#this has the format: run, '', listoftriggers
            break
    return fieldNames

def createTriggerDictionaries(fieldNames):
    triggers = {} 
    prescaledTriggers = {}     
    for name in fieldNames[2:]:
        triggers[name] = []   
        prescaledTriggers[name] = {'prescale': '', 'runs': []}
    return triggers, prescaledTriggers

def fillTriggers(data, triggers, prescaledTriggers):
    for row in data:
        for name, value in row.iteritems():
            if not name == '' or not name == 'run':#ommit emtpy and run columns
                if value == '1':#exists in the menu and has prescale = 1
                    if triggers.has_key(name):
                        triggers[name].append(row['run'])
                elif value:#exists in the menu and has prescale !=1
                    if prescaledTriggers.has_key(name):
                        prescaledTriggers[name]['prescale'] = value
                        prescaledTriggers[name]['runs'].append(row['run'])
    return triggers, prescaledTriggers
    
    
def printTriggersAsTwikiTable(triggers, prescaledTriggers):
    print '| *trigger* | *runs* |'
    for key in sorted(triggers.keys()):
        runs = sorted(triggers[key])
        if len(runs) > 0:
            print '| =%s= |' % key, runs[0], '-', runs[-1], '|'
    
    print
    print '| *trigger* | *runs* | *prescales* |'        
    for key in sorted(prescaledTriggers.keys()):
        runs =sorted(prescaledTriggers[key]['runs'])
        prescale = prescaledTriggers[key]['prescale']
        if len(runs) > 0:
            print '| =%s= |' % key, runs[0], '-', runs[-1], '|', prescale, '|'
            
    
if __name__ == "__main__":
    csvFileName = '/Users/lkreczko/Dropbox/Documents/Analysis/trigger/out2.csv'
    if len(sys.argv) > 1: 
        csvFileName = sys.argv[1]
    triggers, prescaledTriggers = getTriggers(csvFileName)
    printTriggersAsTwikiTable(triggers, prescaledTriggers)
        
        