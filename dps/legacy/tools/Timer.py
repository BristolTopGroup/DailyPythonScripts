
from time import clock

class Timer():

    def __init__(self):
        self.current_time =  clock()
    
    def elapsedTime(self):
        return clock() - self.current_time
    
    def restart(self):
        self.current_time =  clock()
