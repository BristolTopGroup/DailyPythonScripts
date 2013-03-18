#!/usr/bin/env python
# encoding: utf-8
#original from http://astronu.jinr.ru/wiki/index.php/Matplotlib


def drawGraph( g, *args, **kwargs ):
    """Plot TGraph"""
    from pylab import plot
    from numpy import frombuffer, double
    npoints = g.GetN()
    return plot( frombuffer(g.GetX(), double, npoints).copy()
               , frombuffer(g.GetY(), double, npoints).copy()
               , *args, **kwargs )
##end def 

def histGetDtype( h ):
    # 
    # Determine the array data type
    #
    import numpy
    cname = h.__class__.__name__
    dname = cname[-1]
    if   dname=='D': return numpy.double
    elif dname=='F' or dname=='K': return numpy.float 
    elif dname=='I': return numpy.int 
    elif dname=='C': return numpy.int8 #char
    elif dname=='S': return numpy.short
    elif cname=='TProfile': return numpy.double
    assert False, 'Can not determine histogram type'
##end def histGetDtype

def histGetBuffer1( h, flows=False ):
    #
    # Return histogram data buffer
    # if flows=False, exclude underflow and overflow
    #
    from numpy import frombuffer
    buf = frombuffer( h.GetArray(), histGetDtype( h ), h.GetNbinsX()+2 )
    if flows: return buf.copy()
    return buf[1:-1].copy()
##end def histGetBuffer

def histGetBuffer2( h, flows=False, mask=None ):
    #
    # Return histogram data buffer
    # if flows=False, exclude underflow and overflow
    # NOTE: buf[biny][binx] is the right access signature
    #
    from numpy import frombuffer
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    buf = frombuffer( h.GetArray(), histGetDtype( h ), (nx+2)*(ny+2) ).reshape( ( ny+2, nx+2 ) )
    buf=buf.copy()
    if mask!=None:
        from numpy import ma
        buf = ma.array( buf, mask = buf==mask )
    ##end if mask!=None
    if flows: return buf

    buf = buf[1:ny+1,1:nx+1]
    # print 'buffer', buf
    return buf
##end def histGetBuffer

def axisEdges( ax ):
    xbins = ax.GetXbins()
    n = xbins.GetSize()
    if n>0:
        from numpy import frombuffer, double
        lims = frombuffer( xbins.GetArray(), double, n )
        return lims.copy()
    else:
        from numpy import linspace
        lims = linspace( ax.GetXmin(), ax.GetXmax(), ax.GetNbins()+1 )
        # print 'axlims', lims
        return lims
    ##end if 
##end def

def importTitle( o, what='' ):
    if what=='': return
    from pylab import axes
    ax = axes()
    if 'x' in what: ax.set_xlabel( o.GetXaxis().GetTitle() )
    if 'y' in what: ax.set_ylabel( o.GetYaxis().GetTitle() )
    if 't' in what: ax.set_title( o.GetTitle() )
    if 'n' in what: ax.set_title( o.GetName() )
    if 'f' in what: ax.set_title( o.GetExpFormula() )
##end def importTitle

def drawHist1Dbar( h, *args, **kwargs ):
    """Plot 1-dimensinal histogram using pyplot.bar"""
    ax = h.GetXaxis()
    xbins = ax.GetXbins()
    n = ax.GetNbins()
    width, left=None, None
    if xbins.GetSize()>0:
        from numpy import frombuffer, double
        lims = frombuffer( ax.GetXbins().GetArray(), double, n+1 )
        left  = lims[0:-1].copy()
        width = lims[1:] - left        
        # print left
        # print width
    else:
        from numpy import linspace
        left = linspace( ax.GetXmin(), ax.GetXmax(), n+1 )[0:-1]
        width = ax.GetBinWidth( 1 )
    ##end if 
    height = histGetBuffer1( h )
    # print left
    # print height

    from pylab import bar
    return bar( left, height, width, *args, **kwargs )
##end drawHist1D

def drawHist1Dline( h, *args, **kwargs ):
    """Plot 1-dimensinal histogram using pyplot.plot"""
    ax = h.GetXaxis()
    xbins = ax.GetXbins()
    n = ax.GetNbins()
    x=None
    if xbins.GetSize()>0:
        from numpy import frombuffer, double
        x = frombuffer( ax.GetXbins().GetArray(), double, n+1 ).copy()
    else:
        from numpy import linspace
        x = linspace( ax.GetXmin(), ax.GetXmax(), n+1 )
    ##end if 
    height = histGetBuffer1( h )

    from numpy import ravel, empty, vstack
    y = empty( len(height)*2+2 )
    y[1:-1] = vstack( ( height, height ) ).ravel( order='F' ) 
    y[0]=0.0
    y[-1]=0.0
    x = vstack( ( x, x ) ).ravel( order='F' )

    from pylab import plot
    return plot( x, y, *args, **kwargs )
##end drawHist1D

def drawHist1D( h, *args, **kwargs ):
    """Plot 1-dimensinal histogram using pyplot.plot and pyplot.bar 
       baroptions are passed as baropts=dict(opt=value)
    """
    ax = h.GetXaxis()
    xbins = ax.GetXbins()
    n = ax.GetNbins()
    left, width, lims=None,None,None
    if xbins.GetSize()>0:
        from numpy import frombuffer, double
        lims = frombuffer( ax.GetXbins().GetArray(), double, n+1 ).copy()
        left  = lims[0:-1].copy()
        width = lims[1:] - left        
    else:
        from numpy import linspace
        lims = linspace( ax.GetXmin(), ax.GetXmax(), n+1 )
        left = lims[:-1]
        width = ax.GetBinWidth( 1 )
    ##end if 
    height = histGetBuffer1( h )

    from numpy import ravel, empty, vstack
    y = empty( len(height)*2+2 )
    y[1:-1] = vstack( ( height, height ) ).ravel( order='F' ) 
    y[0]=0.0
    y[-1]=0.0
    x = vstack( ( lims, lims ) ).ravel( order='F' )

    from pylab import plot, bar
    baropts = {}
    if 'baropts' in kwargs:
        baropts = kwargs['baropts']
        del kwargs['baropts']
    ##end if 'baropts' in kwargs
    if not 'linewidth' in baropts: baropts['linewidth']=0
    return plot( x, y, *args, **kwargs ), bar( left, height, width, **baropts )
##end drawHist1D

def drawHist2Dmesh( h, *args, **kwargs ):
    #
    # Plot TH2 using matplotlib
    #

    # get bin edges first
    x1 = axisEdges( h.GetXaxis() )
    y1 = axisEdges( h.GetYaxis() )

    # make a 2D mesh
    from numpy import meshgrid
    x, y = meshgrid( x1, y1 )
    # print 'mesh x', x
    # print 'mesh y', y

    # get data bufer w/o underflow/overflow bins
    mask = None
    if 'mask' in kwargs:
        mask = kwargs['mask']
        del kwargs['mask']
    ##end if
    buf = histGetBuffer2( h, mask=mask )

    # plot
    from pylab import pcolormesh
    colz = False
    if 'colz' in kwargs:
        colz = kwargs['colz']
        del kwargs['colz']
    ##end if
    res = pcolormesh( x, y, buf, *args, **kwargs )
    if colz:
        from pylab import colorbar
        colorbar()
    ##end if colz
    return res
##end def drawHist2D

def drawHist2D( h, *args, **kwargs ):
    #
    # Plot TH2 using matplotlib
    #

    # get bin edges first
    xax = h.GetXaxis()
    yax = h.GetYaxis()
    if xax.GetXbins().GetSize()>0 or yax.GetXbins().GetSize()>0:
        print 'Can not draw 2D a histogram with variable bin widths'
        print 'Use drawMesh method or draweHist2Dmesh function instead'
        return
    ##end if
    x = [ xax.GetXmin(), xax.GetXmax() ]
    y = [ yax.GetXmin(), yax.GetXmax() ]

    # get data bufer w/o underflow/overflow bins
    mask = None
    if 'mask' in kwargs:
        mask = kwargs['mask']
        del kwargs['mask']
    ##end if
    buf = histGetBuffer2( h, mask=mask )

    # plot
    from pylab import axes
    ax = axes()
    colz = False
    if 'colz' in kwargs:
        colz=kwargs['colz']
        del kwargs['colz']
    ##end if
    res = ax.pcolorfast( x, y, buf, *args, **kwargs )
    if colz:
        from pylab import gcf
        gcf().colorbar( res )
    ##end if colz

    return res
##end def drawHist2D

def drawFun( f, x, *args, **kwargs ):
    from numpy import frompyfunc
    fun = frompyfunc( f, 1, 1 )

    from pylab import plot
    return plot( x, fun(x), *args, **kwargs )
##end def drawFun

def drawTF1( f, x=None, *args, **kwargs ):
    """Draw TF1
       if x is an array-like it's used as array of x
       if x is integer it is used as N of points in function range
       if x is float it is used as step
       if x is None, the TF1->Npx is used as number of points
    
    """
    import numpy
    tp = type(x)
    if x==None:
        x = numpy.linspace( f.GetXmin(), f.GetXmax(), f.GetNpx() )
    elif tp==int:
        x = numpy.linspace( f.GetXmin(), f.GetXmax(), x )
    elif tp==float:
        x = numpy.arange( f.GetXmin(), f.GetXmax(), x )
    ##end

    return drawFun( f.Eval, x, *args, **kwargs )
##end def drawTF1

def savefig( name, *args, **kwargs ):
    """Save fig and print output filename"""
    if not name: return
    from pylab import savefig
    savefig( name, *args, **kwargs )
    print 'Save figure', name
##end def savefig

def set_title( t ):
    """Set window title"""
    from pylab import canvas
    canvas.set_window_title( t )
##end if

#
# Define draw method for:
# TH1
# TH2
# TF1
# TGraph
#
from ROOT import TH1, TH2, TGraph, TF1
setattr( TH1, 'draw', drawHist1D )
setattr( TH1, 'drawBar', drawHist1Dbar )
setattr( TH1, 'drawLine', drawHist1Dline )
setattr( TH2, 'draw', drawHist2D )
setattr( TH2, 'drawMesh', drawHist2Dmesh )
setattr( TF1, 'draw', drawTF1 )
setattr( TGraph, 'draw', drawGraph )
