import threading 
from dbcontrol import *
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from typing import List

class acRunning():
    start_time: datetime
    wind_level: WindLevel
    ac_id: str
    cur_temp: float
    tar_temp: float
    model: ACModel
    # 请根据你们的设计来更新相应的空调温度，调度部分不做额外实现
    def update():
        pass
    
    
# 正在运行的列表
AC_active:List[acRunning] = []

# 正在等待的列表
AC_ready:List[acRunning] = []

# 达成目标温度后正在休息的列表
AC_over:List[acRunning] = []
lock = threading.Lock()

def list_update():
    for ac_a in AC_active:
        ac_a.update()
    for ac_r in AC_ready:
        ac_r.update()
    for ac_o in AC_over:
        ac_o.update()

timeslice = 120

def callback():
    # 上锁，每次需要进行空调使用，直接将类放入ready列表中，注意上锁
    lock.acquire()
    # 更新当前的列表内部状态
    list_update()
    now = datetime.now()
    # 检查当前的over列表中是否有待执行的内容
    for i, ac_o in enumerate(AC_over):
        if (ac_o.cur_temp - ac_o.tar_temp>3 and not ac_o.model) or (ac_o.tar_temp - ac_o.tar_temp > 3 and ac_o.model):
            AC_over.pop(i)
            ac_o.start_time = now
            AC_ready.append(ac_o)
            
    # 检查当前active队列中有没有已经达到要求的数据,移动到over队列
    for i, ac_a in enumerate(AC_active):
        if (ac_a.cur_temp >= ac_a.tar_temp and ac_a.model) or (ac_a.cur_temp <= ac_a.tar_temp and not ac_a.model):
            AC_active.pop(i)
            ac_a.start_time = now
            AC_over.append(ac_a)
            
    # 首先进行等待序列的排序，按照风速等级+等待时间进行排序
    AC_ready = sorted(AC_ready, key=lambda ac: (-ac.wind_level, ac.start_time))
    AC_active = sorted(AC_active, key=lambda ac: (ac.wind_level, ac.start))
    
    # 首先将ready中优先级最高的加入到active中
    while(len(AC_active)<3):
        ac_r = AC_ready.pop(0)
        ac_r.start_time = datetime.now()
        AC_active.append(ac_r)
    # 将ready中最优先加入的和active中最优先脱出的进行比较，可以仔细想想其中的逻辑，本身应该没有问题
    ran = min(3, len(AC_active), len(AC_ready))
    for i in range(ran):
        # 等待中的风速等级更高的情况中
        if AC_ready[0].wind_level > AC_active[0].wind_level:
            ac_r = AC_ready.pop(0)
            ac_a = AC_active.pop(0)
            ac_r.start_time = datetime.now()
            ac_a.start_time = datetime.now()
            AC_ready.append(ac_a)
            AC_active.append(ac_r)
        # 风速相等的情况下，查看是否完成了时间片
        elif AC_ready[0].wind_level == AC_active[0].wind_level:
            if now - AC_active[0].start_time >= timeslice:
                ac_a = AC_active.pop[0]
                ac_r = AC_ready.pop[0]
                ac_a.start_time = now
                ac_r.start_time = now
                AC_active.append(ac_r)
                AC_ready.append(ac_a)
        
    lock.release()
    
scheduler = BlockingScheduler()
scheduler.add_job(callback, 'interval', seconds=3)  # 每5秒执行一次回调
scheduler.start()
while(True):
    pass