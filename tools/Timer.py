
from time import clock

class Timer():

    def __init__(self):
        self.start_time =  clock()
    
    def elapsedTime(self):
        return clock() - self.start_time
    
    def restart(self):
        self.start_time =  clock()
