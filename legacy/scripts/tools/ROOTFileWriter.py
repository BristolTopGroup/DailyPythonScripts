def writeHistogramDictionaryToFile(histDictionary, fileName, mode = 'w'):
    pass 


def getPath(pathWithObject):
    objectName = pathWithObject.split('/')[-1]
    path = pathWithObject.replace(objectName, '')
    return path