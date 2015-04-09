
from time import time
import datetime 

class Timer():

    def __init__(self):
        self.start_time =  time()
    
    def elapsed_time(self):
        return time() - self.start_time
    
    def restart(self):
        self.start_time =  time()

def nice_date_now():
    return datetime.datetime.now().strftime("%H.%M_%d.%m.%y")
    