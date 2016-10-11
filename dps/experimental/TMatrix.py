from ROOT import TMatrixDSparse
from array import array
n_x, n_y = 4,4
data_array = array('d', [i+1 for i in range (n_x*n_y)])
row = array('i', [i for i in range (n_x)])
col = array('i', [i for i in range (n_y)])
print col, row
m_square = TMatrixDSparse(n_x,n_y)
m_square.SetSparseIndex(n_x)
m_square.SetRowIndexArray(row)
m_square.SetColIndexArray(col)
# m_square.SetMatrixArray(5, row, col, data_array)
    
row_index = m_square.GetRowIndexArray()
col_index =  m_square.GetColIndexArray()
pdata = m_square.GetMatrixArray()
print 'n rows=',  m_square.GetNrows()

for i in range(m_square.GetNrows()):
    sIndex = row_index[i]
    eIndex = row_index[i+1]
    print sIndex, eIndex
    for index in range(sIndex, eIndex):
        icol = col_index[index]
        data = pdata[index]
        print 'data(%d,%d) = %.4f' % (i, icol, data)
