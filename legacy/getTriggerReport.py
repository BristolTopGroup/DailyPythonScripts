from __future__ import division
import sys
import glob

def triggerInfo(trigger, logString):
    logString = logString.replace('\n', '')
    #remove empty entries
    entries = [token for token in logString.split(' ') if not token == '']
    info = {}
    info['name'] = entries[-1]
    info['eventsTotal'] = entries[3]
    info['eventsPassed'] = entries[4]
    info['eventsFailed'] = entries[5]
    info['efficiency'] = entries[4] / entries[3]
    return info

def readTriggerSummaryTable(filename):
    lookForLine = 'TrigReport ---------- Path   Summary ------------'
    stopLookingLine = '\n'
    
    file = open(filename)
    adding = False
    triggerLog = []
    
    for line in file.readlines():
        if lookForLine in line:
            adding = True
            
        if adding == True and stopLookingLine == line:
            break
        
        if adding:
            triggerLog.append(line.replace('\n', ''))
    file.close()
    #remove the header of the table        
    triggerLog = triggerLog[2:]
    
    return triggerLog

def trimmTriggerTable(triggerTable):
    for index in range(len(triggerTable)):
        row = triggerTable[index]
        #remove first 3 columns: TrigReport  Trig Bit#
        row = row.replace('\n', '')
        row = [token for token in row.split(' ') if not token == '']
        row = row[3:]
        
        columns = parseColumns(row)
        
        triggerTable[index] = columns
    return triggerTable
 
def parseColumns(row):
    if len(row) < 5:
        print "Unknown row, can't parse"
        return {}
    columns = {'total': int(row[0]),
               'passed': int(row[1]),
               'failed':int(row[2]),
               'errors':int(row[3]),
               'trigger':row[4]}
    return columns

def parseTriggerTable(triggerTable):
    triggers = {}
    for row in triggerTable:
        triggerName = row['trigger']
        del row['trigger']
        triggers[triggerName] = row
    return triggers
    
def mergeParsedTriggerTables(triggerTable1, triggerTable2):
    mergedTriggerTable = triggerTable1
    
    for trigger, entries in triggerTable1.iteritems():
        if not triggerTable2.has_key(trigger):
            print 'trying to merge two different triggertables!'
            return
        
        for entry, value in entries.iteritems():
            mergedTriggerTable[trigger][entry] += triggerTable2[trigger][entry]
    return mergedTriggerTable
            

def printParsedTriggerTable(triggerTable):
    keys = triggerTable.keys()
    keys.sort()
    print 'Trigger', '\t\t', 'passed', '\t', 'failed'#, '\t\t', 'total'
    for key in keys:
        entries = triggerTable[key]
        
        
        print key, '\t\t', entries['passed'], '\t', entries['failed']#, '\t\t', entries['total']
        
if __name__ == "__main__":
    files = ['/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_1.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_2.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_3.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_4.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_5.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_6.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_7.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_8.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_9.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_10.log',
             '/storage/workspaceTutorial/BristolAnalysisTools/scripts/test_run163374_11.log']
    
    if len(sys.argv) > 1: 
        files = sys.argv[1:]
        if len(files) == 1:
            if '*' in files[0]:
                files = glob.glob(files[0])
    triggerTables = []
    for file in files:
        triggerTable = readTriggerSummaryTable(file)
        triggerTable = trimmTriggerTable(triggerTable)
        parsedT = parseTriggerTable(triggerTable)
        triggerTables.append(parsedT)
        
    mergedTriggers = triggerTables[0]
    
    if len(triggerTables) > 1:
        for triggerTable in triggerTables[1:]:
            mergedTriggers = mergeParsedTriggerTables(mergedTriggers, triggerTable)
    
#    for trigger, entries in mergedTriggers.iteritems():
#        print trigger, '=', entries
        
    printParsedTriggerTable(mergedTriggers)
        
