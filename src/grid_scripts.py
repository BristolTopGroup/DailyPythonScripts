'''
Created on 26 Nov 2012

@author: kreczko
'''



from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--delete",
                  action="store_false", dest="delete", default=False,
                  help="delete the given argument")
    parser.add_option("-f", "--fetch",
                  action="store_false", dest="fetch", default=False,
                  help="fetch the given argument")
    (options, args) = parser.parse_args()
    

