
#Class to represent a table and manipulate the string representation
class Table():
    #create a table with a header (first row) and a footer (last row)
    def __init__(self, header = True, footer = False):
        self.rows = []
        
    def addrow(self, row):
         self.rows.append(row)   
        
    def convertToTwikiEntry(self):
        pass
    
    def convertToLatex(self):
        pass