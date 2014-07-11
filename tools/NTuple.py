'''
Created on 19 May 2014

@author: kreczko
'''
from functools import total_ordering
from os.path import getsize

class FileInfo( object ):
    def __init__( self, root_file ):
        trees = []
        for path, _, objects in root_file.walk():
            for o in objects:
                full_path = path + '/' + o
                tree = root_file.Get( full_path )
                if 'Tree' in str( type( tree ) ):
                    trees.append( TreeInfo( tree, full_path ) )
        self.trees = trees
        self.size = getsize( root_file.GetName() )
        self.tree_size = sum( tree.size for tree in self.trees )
        self.tree_zipped_bytes = sum( tree.zipped_bytes for tree in self.trees )

class TreeInfo( object ):
    def __init__( self, root_tree, full_path ):
        self.name = root_tree.GetName()
        self.url = full_path
        self.n_branches = root_tree.GetNbranches()
        self.size = root_tree.get_tot_bytes()
        self.zipped_bytes = root_tree.get_zip_bytes()
        self.n_events = root_tree.GetEntriesFast()
        branches = sorted( list( root_tree.GetListOfBranches() ) )
        self.branches = [BranchInfo( branch ) for branch in branches]
        self.grouped_branches = {}
        for branch in self.branches:
            group = branch.group
            if not self.grouped_branches.has_key( group ):
                self.grouped_branches[group] = BranchInfoGroup( group )
            self.grouped_branches[group].add( branch )

@total_ordering
class BranchInfo( object ):

    def __init__( self, root_branch ):
        self.name = root_branch.GetName()
        self.size = root_branch.GetTotalSize()
        self.zipped_bytes = root_branch.GetZipBytes()
        if '.' in self.name:
            self.group = self.name.split( '.' )[0]
        else:
            self.group = self.name
        
    def __eq__( self, other ):
        return ( ( self.name, self.size, self.zipped_bytes, self.group ) == 
                ( other.name, other.size, other.zipped_bytes, other.group ) )
        
    def __lt__( self, other ):
        return self.name < other.name
    
    def __str__( self ):
        return 'Branch %s: size = %d, zipped_bytes = %d' % ( self.name, self.size, self.zipped_bytes )
    
class BranchInfoGroup( object ):
    def __init__( self, name ):
        self.name = name
        self.branches = []
        
    def add( self, branch ):
        self.branches.append( branch )
    
    def branches( self ):
        return self.branches()
    
    def size( self ):
        return sum( [branch.size for branch in self.branches] )
    
    def zipped_bytes( self ):
        return sum( [branch.zipped_bytes for branch in self.branches] )
