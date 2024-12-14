import threading
from back.dbcontrol import *
from datetime import datetime


def dispatch():
    print("hh")
    
threading.Timer(120, dispatch)

waiting_deque = []
active_deque = []

Max_Number = 3
class AcDispatch():
    wind_level: WindLevel
    room_id: str
 
class acDeque():
    ac_data: AcDispatch 
    time: datetime
    
def ac_add(ac: AcDispatch):
    if len(active_deque) < 3:
        ac_deque = acDeque()
        ac_deque.ac_data = ac
        ac_deque.time = datetime.now
        active_deque.append(ac_deque)
    elif  len(active_deque) > 3:
        if 
        

def ac_change():
    pass

def ac_delete():
    pass





