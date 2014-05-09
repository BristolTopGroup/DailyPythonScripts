import os
import json

def createFolderIfDoesNotExist(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
def writeStringToFile(string, filename):
    path = getPath(filename)
    createFolderIfDoesNotExist(path)
    #write file
    output_file = open(filename, 'w')
    output_file.write(string)
    output_file.close()
    
def getPath(filenameWithPath):
    absolutePath = os.path.abspath(filenameWithPath)
    filename = absolutePath.split('/')[-1]
    path = absolutePath.replace(filename, '')
    return path

def readJSONFile(filename):
    inputfile = open(filename, 'r')
    inputJSON = ''.join(inputfile.readlines())
    objects = json.loads(inputJSON)
    inputfile.close()
    return objects