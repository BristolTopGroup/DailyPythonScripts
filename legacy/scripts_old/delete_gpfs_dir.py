try:
    import subprocess
except:
    print "You have to use Python 2.4 or higher"
    sys.exit(0)
from optparse import OptionParser
import os


files = []
directories = []

SEbase = 'srm://lcgse02.phy.bris.ac.uk:8444/srm/managerv2?SFN=/cms/'
gpfsBase = '/gpfs_phys/storm/cms/'

def delete(file):
    output = subprocess.Popen(['srmrm', srmBase + file], stdout=subprocess.PIPE).communicate()[0]
    return output

def listDirectory(path):

    dirlist = os.listdir(path)
    
    isFile = os.path.isfile
    isDir = os.path.isdir
    
    for item in dirlist:
        newPath = path + '/' + item
        if isFile(newPath):
            files.append(newPath)
        elif isDir(newPath):
            directories.append(newPath)
            listDirectory(newPath)
            
def deleteFiles(files):
    for file in files:
        file = file.replace(gpfsBase, SEbase)
        print 'deleting file:', file
        output = subprocess.Popen(['srmrm', file], stdout=subprocess.PIPE).communicate()[0]

def deleteFolder(folder):
    print 'deleting folder:', folder
    output = subprocess.Popen(['srmrmdir', '-recursive', folder], stdout=subprocess.PIPE).communicate()[0]
    return output

def printTotalSize(path):
    output = subprocess.Popen(['du', '-sch', path], stdout=subprocess.PIPE).communicate()[0]
    print output

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-r", "--recursive",
                  action="store_true", dest="recursive", default=False,
                  help="delete gpfs folder recursively")
    
    (options, args) = parser.parse_args()
    if len(args) > 0 and vars(options)['recursive']:
        path = args[0]
        print 'getting files'
#        print os.listdir(path)
        printTotalSize(path)
        listDirectory(path)
        deleteFiles(files)
        deleteFolder(path.replace(gpfsBase, SEbase))
        print 'number of files:', len(files)
        if len(files) > 0:
            print 'first file:', files[0]
            
        print 'number of directories:', len(directories)
        if len(directories) > 0:
            print 'first dir', directories[0]
    
    else:
        print 'Delete path was not specified. Use script "./deleteGridFolder path"'
