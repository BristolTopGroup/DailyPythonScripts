'''
Created on 25 Mar 2015

@author: kreczko
'''
from tabulate import tabulate
from tools.logger import log
mylog = log["tools.table"]


class PrintTable():
    '''
        Class for the creation and printing of tables
        Example usage:
            data = [
                    ['DailyPythonScripts', 'Python', 'last parts of analysis'],
                    ['NTupleProduction', 'C++/CMSSW', 'miniAOD -> ntuple'],
                    ]
            headers = ['software package', 'main language', 'comment']
            t = PrintTable(data, headers)
            # simple nice table (for console)
            print t.simple()
            # table to put into a twiki
            print t.twiki()
            # table to put into a latex document
            print t.latex()
    '''

    @mylog.trace()
    def __init__(self, data, headers):
        '''
            @param data: a list of columns
            @param headers: a list of headers (must be of column length) 
        '''
        self.data = data
        self.headers = headers

    @mylog.trace()
    def twiki(self):
        '''
            return the table as a string in twiki format
        '''
        # add bold for twiki headers
        headers = ['*' + h + '*' for h in self.headers]
        # use Emacs org-mode as baseline
        table = tabulate(self.data, headers=headers, tablefmt='orgtbl')
        table = str(table).split('\n')
        twiki_table = []
        for line in table:
            # remove header delimiter
            if not line.startswith('|--'):
                twiki_table.append(line)

        return ''.join([line + '\n' for line in twiki_table])

    @mylog.trace()
    def simple(self):
        '''
            return the table as a pretty string
        '''
        table = tabulate(self.data, headers=self.headers, tablefmt='simple')
        return str(table)

    @mylog.trace()
    def latex(self):
        '''
            return the table as a string in latex format
        '''
        table = tabulate(self.data, headers=self.headers, tablefmt='latex')
        string = str(table)
        string = string.replace('\\textbackslash{}', '\\')
        string = string.replace('\\$', '$')
        return string


if __name__ == '__main__':
    data = [['MET', 'X', ' '], ['MT', ' ', 'x']]
    headers = ['variable', 'fun', 'not fun']
    table = PrintTable(data, headers)
    print table.twiki()
