'''
Created on 31 Oct 2012

@author: kreczko
'''
import unittest
from experimental.Config import Config


class Test( unittest.TestCase ):
    def test_direct_read_access( self ):
        a = Config ( f = 1 )
        self.assertEqual( a.f, 1 )
        
    def test_direct_write_access( self ):
        a = Config ( f = 1 )
        a.f = 2
        self.assertEqual( a.f, 2 )
        
    def test_indirect_read_access( self ):
        a = Config ( f = 1 )
        self.assertEqual( a.param_( 'f' ), 1 )
        
    def test_indirect_write_access( self ):
        a = Config()
        self.assertEqual( a.param_( 'sdf' ), None )
        
if __name__ == "__main__":
    unittest.main()
