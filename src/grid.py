'''
Created on 18 Dec 2012

@author: kreczko
'''
from optparse import OptionParser
#import grid utilities
from tools.grid_utilities import fetch_grid_file, delete_grid_folder, remote_copy_folder

def rm(filename, recursive = False):
    pass

def copyfile(source, destination):
    pass

def copy(source, destination):
    '''
    detect if remote or local
    if remote to remote: schedule in FTS? split on more than one stream?
    '''
    pass




if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--delete",
                  action="store_false", dest="delete", default=False,
                  help="delete the given argument")
    parser.add_option("-f", "--fetch",
                  action="store_false", dest="fetch", default=False,
                  help="fetch the given argument")
    (options, args) = parser.parse_args()