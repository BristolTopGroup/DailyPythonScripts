
from time import time

class Timer():

    def __init__(self):
        self.start_time =  time()
    
    def elapsed_time(self):
        return time() - self.start_time
    
    def restart(self):
        self.start_time =  time()
