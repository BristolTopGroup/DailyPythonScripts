'''
From http://arxiv.org/abs/1305.1878
'''
import numpy as np
import ROOT as r
import math
from scipy.optimize import leastsq
mT = 172.5
mW = 80.385
mN = 0
# GeV : top quark mass
# GeV : W boson mass
# GeV : neutrino mass
def UnitCircle ():
    '''
    Unit circle in extended representation
    '''
    return np.diag ( [1 , 1, -1] )

def cofactor ( A, ( i, j ) ):
    '''Cofactor [i,j] of 3x3 matrix A '''
    a = A[not i:2 if i == 2 else None :2 if i == 1 else 1,
          not j:2 if j == 2 else None :2 if j == 1 else 1]
    return ( -1 ) ** ( i + j ) * ( a[0 , 0] * a[1 , 1] - a[1 , 0] * a[0 , 1] )

def R( axis , angle ):
    '''Rotation matrix about x(0) ,y(1) , or z(2) axis '''
    c, s = math.cos( angle ), math.sin( angle )
    R = c * np.eye ( 3 )
    for i in [-1, 0, 1]:
        R[( axis - i ) % 3 , ( axis + i ) % 3] = i * s + ( 1 - i * i )
    return R

def Derivative ():
    '''Matrix to differentiate [cos(t),sin(t) ,1] '''
    return R( 2, math.pi / 2 ).dot( np.diag ( [1 , 1, 0] ) )

def multisqrt ( y ):
    '''Valid real solutions to y=x*x '''
    return ( [] if y < 0 else 
            [0] if y == 0 else
            ( lambda r: [-r, r] )( math.sqrt( y ) ) )
    
def factor_degenerate ( G, zero = 0 ):
    '''Linear factors of degenerate quadratic polynomial '''
    if G[0 , 0] == 0 == G[1 , 1]:
        return [[G[0 , 1] , 0, G[1 , 2]] ,
                [0, G[0 , 1] , G[0 , 2] - G[1 , 2]]]
    
    swapXY = abs( G[0 , 0] ) > abs( G[1 , 1] )
    Q = G[( 1 , 0 , 2 ) , ][: , ( 1 , 0 , 2 )] if swapXY else G
    Q /= Q[1 , 1]
    q22 = cofactor ( Q, ( 2 , 2 ) )
    
    lines = []
    if -q22 <= zero:
        lines = [[Q[0, 1] , Q[1 , 1] , Q[1 , 2] + s]
                 for s in multisqrt ( -cofactor ( Q, ( 0 , 0 ) ) )]
    else:
        x0 , y0 = [ cofactor ( Q , ( i , 2 ) ) / q22 for i in [0, 1]]
        lines = [[m, Q[1 , 1] , -Q[1 , 1] * y0 - m * x0]
                 for m in [Q[0 , 1] + s
                           for s in multisqrt ( -q22 )]]
        
    return [[L[ swapXY ], L[not swapXY ], L[2]] for L in lines ]


def intersections_ellipse_line( ellipse , line , zero = 1e-12 ):
    '''Points of intersection between ellipse and line '''
    _, V = np.linalg.eig( np.cross( line , ellipse ).T )
    sols = sorted ( [( v.real / v[2]. real ,
                     np.dot( line , v.real ) ** 2 + 
                     np.dot( v.real , ellipse ).dot( v.real ) ** 2 )
                    for v in V.T],
                   key = lambda ( s, k ): k )[:2]
    return [s for s, k in sols if k < zero]

def intersections_ellipses ( A, B, returnLines = False ):
    '''Points of intersection between two ellipses '''
    LA = np.linalg
    if abs( LA.det( B ) ) > abs( LA.det( A ) ): A, B = B, A
    e = next( e.real for e in LA. eigvals ( LA.inv( A ).dot( B ) )
             if not e.imag )
    lines = factor_degenerate ( B - e * A )
    points = sum ( [ intersections_ellipse_line ( A, L )
                   for L in lines ] , [] )
    return ( points , lines ) if returnLines else points

class nuSolutionSet ( object ):
    '''Definitions for nu analytic solution , t->b,mu ,nu '''
   
    def __init__ ( self , b, mu ,  # Lorentz Vectors
                 mW2 = mW ** 2 , mT2 = mT ** 2 , mN2 = mN ** 2 ):
        c = r.Math.VectorUtil.CosTheta ( b, mu )
        s = math.sqrt ( 1 - c ** 2 )
        
        x0p = -( mT2 - mW2 - b.M2 () ) / ( 2 * b.E() )
        x0 = -( mW2 - mu.M2 () - mN2 ) / ( 2 * mu.E() )
        
        Bb , Bm = b.Beta (), mu.Beta ()
        
        Sx = ( x0 * Bm - mu.P() * ( 1 - Bm ** 2 ) ) / Bm ** 2
        Sy = ( x0p / Bb - c * Sx ) / s
        
        w = ( Bm / Bb - c ) / s
        w_ = ( -Bm / Bb - c ) / s
        
        Om2 = w ** 2 + 1 - Bm ** 2
        eps2 = ( mW2 - mN2 ) * ( 1 - Bm ** 2 )
        x1 = Sx - ( Sx + w * Sy ) / Om2
        y1 = Sy - ( Sx + w * Sy ) * w / Om2
        Z2 = x1 ** 2 * Om2 - ( Sy - w * Sx ) ** 2 - ( mW2 - x0 ** 2 - eps2 )
        Z = math.sqrt( max ( 0, Z2 ) )
        
        for item in ['b', 'mu ', 'c', 's', 'x0 ', 'x0p ',
                     'Sx ', 'Sy ', 'w', 'w_ ', 'x1 ', 'y1 ',
                     'Z', 'Om2 ', 'eps2 ', 'mW2 ']:
            setattr ( self , item , eval( item ) )
            
    @property
    def K( self ):
        '''Extended rotation from F' to F coord . '''
        return np.array( [[ self.c, -self.s, 0, 0],
                          [self.s, self.c, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]] )
        
    @property
    def A_mu( self ):
        '''F coord. constraint on W momentum : ellipsoid '''
        B2 = self.mu.Beta () ** 2
        SxB2 = self.Sx * B2
        F = self.mW2 - self.x0 ** 2 - self.eps2
        return np.array( [[1 - B2 , 0, 0, SxB2],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [SxB2, 0, 0, F]] )

    @property
    def A_b(self ):
        '''F coord . constraint on W momentum : ellipsoid '''
        K, B = self.K, self.b.Beta ()
        mW2 , x0p = self.mW2 , self.x0p
        A_b_ = np.array ([[1 -B*B, 0, 0,B*x0p],
                           [0, 1, 0,0],
                           [0, 0, 1,0],
                           [B*x0p , 0, 0, mW2 -x0p **2]])
        return K.dot(A_b_ ).dot(K.T)

    @property
    def R_T(self ):
        '''Rotation from F coord . to laboratory coord. '''
        b_xyz = self.b.x(), self.b.y(), self.b.z()
        R_z = R(2, -self.mu.phi ())
        R_y = R(1, 0.5* math.pi - self.mu. theta ())
        R_x = next(R(0,- math.atan2 (z,y))
                   for _,y,z in (R_y.dot(R_z.dot( b_xyz )) ,))
        return R_z.T.dot(R_y.T.dot(R_x.T))

    @property
    def H_tilde (self ):
        ''' Transformation of t=[c,s ,1] to p_nu: F coord. '''
        x1 , y1 , p = self.x1 , self.y1 , self.mu.P()
        Z, w, Om = self.Z, self.w, math.sqrt(self.Om2)
        return np.array ([[ Z/Om , 0, x1 -p],
                           [w*Z/Om , 0,y1],
                           [0, Z,0]])

    @property
    def H(self ):
        ''' Transformation of t=[c,s ,1] to p_nu: lab coord. '''
        return self.R_T.dot(self.H_tilde )

    @property
    def H_perp (self ):
        ''' Transformation of t=[c,s ,1] to pT_nu : lab coord. '''
        return np.vstack([ self.H[:2] , [0, 0, 1]])

    @property
    def N(self ):
        '''Solution ellipse of pT_nu : lab coord . '''
        HpInv = np.linalg.inv(self.H_perp )
        return HpInv.T.dot(UnitCircle()).dot(HpInv)

class singleNeutrinoSolution ( object ):
    '''Most likely neutrino momentum for tt --> lepton +jets '''
    def __init__ (self, b, mu, # Lorentz Vectors
                  (metX, metY), # Momentum imbalance
                  sigma2 , # Mo. imbalance unc. matrix
                  mW2=mW **2 , mT2=mT **2):
        self.solutionSet = nuSolutionSet (b, mu , mW2 , mT2)
        S2 = np.vstack ([ np.vstack ([ np.linalg.inv( sigma2 ),
                                      [0, 0]]).T, [0, 0, 0]])
        V0 = np.outer([ metX , metY , 0], [0, 0, 1])
        deltaNu = V0 - self.solutionSet .H

        self.X = np.dot( deltaNu.T, S2 ).dot( deltaNu )
        M = next(XD + XD.T
                 for XD in (self.X.dot( Derivative ()) ,))

        solutions = intersections_ellipses (M, UnitCircle ())
        self.solutions = sorted (solutions , key=self.calcX2 )

    def calcX2 (self , t):
        return np.dot(t, self.X).dot(t)

    @property
    def chi2(self ):
        return self.calcX2 (self.solutions [0])

    @property
    def nu(self ):
        '''Solution for neutrino momentum '''
        return self.solutionSet .H.dot(self.solutions [0])

class doubleNeutrinoSolutions ( object ):
    '''Solution pairs of neutrino momenta , tt -> leptons '''
    def __init__ (self , (b, b_), (mu , mu_), # 4- vectors
              (metX , metY), # ETmiss
              mW2=mW **2 , mT2=mT **2):
        self.solutionSets = [ nuSolutionSet (B, M, mW2 , mT2)
                             for B,M in zip ((b,b_),(mu ,mu_ ))]
        
        V0 = np.outer ([ metX , metY , 0], [0, 0, 1])
        self.S = V0 - UnitCircle ()
        
        N, N_ = [ss.N for ss in self.solutionSets ]
        n_ = self.S.T.dot(N_ ).dot(self.S)
        
        v = intersections_ellipses (N, n_)
        v_ = [self.S.dot(sol) for sol in v]
        
        if not v and leastsq :
            es = [ss. H_perp for ss in self.solutionSets ]
            met = np.array ([ metX , metY , 1])

            def nus(ts ):
                return tuple (e.dot ([ math.cos(t), math.sin(t), 1])
                              for e, t in zip(es , ts ))
                
            def residuals ( params ):
                return sum(nus( params ), -met )[:2]
            
            ts ,_ = leastsq (residuals , [0, 0],
                             ftol =5e-5, epsfcn =0.01)
            v, v_ = [[i] for i in nus(ts )]
            
        for k, v in {'perp ': v, 'perp_ ': v_ , 'n_ ': n_ }. items ():
            setattr (self , k, v)

    @property
    def nunu_s (self ):
        '''Solution pairs for neutrino momenta '''
        K, K_ = [ss.H.dot(np.linalg.inv(ss. H_perp ))
                 for ss in self.solutionSets ]
        return [(K.dot(s), K_.dot(s_ ))
                for s, s_ in zip(self.perp , self.perp_ )]