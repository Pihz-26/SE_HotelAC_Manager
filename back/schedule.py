import threading 
from dbcontrol import *
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List
from sqlalchemy import and_

class acRunning:
    def __init__(self, start_time: datetime, wind_level: WindLevel, ac_id: str, 
                 cur_temp: float, tar_temp: float, env_temp: float, model: ACModel):
        self.start_time = start_time           # 空调启动时间
        self.wind_level = wind_level           # 空调风速
        self.ac_id = ac_id                     # 空调对应的房间ID
        self.cur_temp = cur_temp               # 当前温度
        self.tar_temp = tar_temp               # 目标温度
        self.env_temp = env_temp               # 环境温度
        self.model = model                     # 空调模式（制冷/制热

# 正在运行的列表
AC_active:List[acRunning] = []

# 正在等待的列表
AC_ready:List[acRunning] = []

# 达成目标温度后正在休息的列表
AC_over:List[acRunning] = []

lock = threading.Lock()


def update_ac_queues(session: Session):
    # 记录所有修改过的房间
    rooms_to_update = []
    # 检查正在运行的队列
    i=0
    len_a =len(AC_active)
    while(i!=len_a):
        room = session.exec(select(Room).where(Room.room_id == AC_active[i].ac_id)).first()
        if room:
            if not room.power:  # 如果空调关机
                # 更新房间的状态为 noschedule
                room.status = Status.noschedule  # 将房间状态还原为 noschedule
                rooms_to_update.append(room)  # 添加到待更新的房间列表
                AC_active.pop(i)  # 使用 pop(i) 移除空调对象
                i-=1
                len_a-=1
            else:
                AC_active[i].wind_level=room.wind_level
                AC_active[i].tar_temp=room.targetTemperature
        i+=1
                
    i=0
    len_r =len(AC_ready)
    # 检查正在等待的队列
    while(i!=len_r):
        room = session.exec(select(Room).where(Room.room_id == AC_ready[i].ac_id)).first()
        if room:
            if not room.power:  # 如果空调关机
                # 更新房间的状态为 noschedule
                room.status = Status.noschedule  # 将房间状态还原为 noschedule
                rooms_to_update.append(room)  # 添加到待更新的房间列表
                AC_ready.pop(i)  # 使用 pop(i) 移除空调对象
                i-=1
                len_r-=1
            else:
                AC_ready[i].wind_level=room.wind_level
                AC_ready[i].tar_temp=room.targetTemperature
        i+=1

    i=0
    len_o =len(AC_over)
    # 检查已休息的队列
    while(i!=len_o):
        room = session.exec(select(Room).where(Room.room_id == AC_over[i].ac_id)).first()
        if room:
            if not room.power:  # 如果空调关机
            # 更新房间的状态为 noschedule
                room.status = Status.noschedule  # 将房间状态还原为 noschedule
                rooms_to_update.append(room)  # 添加到待更新的房间列表
                AC_over.pop(i)  # 使用 pop(i) 移除空调对象
                i-=1
                len_o-=1
            else:
                AC_over[i].wind_level=room.wind_level
                AC_over[i].tar_temp=room.targetTemperature
        i+=1
    # 统一提交所有修改的房间
    if rooms_to_update:
        session.add_all(rooms_to_update)  # 将所有修改的房间对象一次性添加到会话中
        session.commit()  # 提交所有修改


timeslice = 20

def callback( ):
    global AC_ready  # 显式声明AC_ready为全局变量
    global AC_active  # 显式声明AC_ready为全局变量
    global AC_over  # 显式声明AC_ready为全局变量
    global lock
    session = get_session_()
    # 上锁，每次需要进行空调使用，直接将类放入ready列表中，注意上锁
    ac_control = session.exec(select(acControl).order_by(acControl.record_time.desc())).first() #查找空调模式
    # print(ac_control)
    lock.acquire()
    temperature_update()
    # 更新当前的列表内部状态
    now = datetime.now()
    if ac_control :  # 如果有对应的空调控制记录
        rooms = session.exec(select(Room).where(and_(Room.status == Status.noschedule, Room.power == True))).all()
        if rooms:
            for room in rooms:
                # 查找对应房间的空调控制数据
                    # 创建一个acRunning对象，并添加到AC_ready列表
                    ac = acRunning(
                        start_time=now,
                        wind_level=room.wind_level,  
                        ac_id=room.room_id,  # 使用room_id作为ac_id
                        cur_temp=room.roomTemperature,  # 当前房间温度
                        tar_temp=room.targetTemperature,  # 目标温度
                        env_temp=room.environTemperature,
                        model=ac_control.ac_model  # 空调的工作模式（制冷/制热）
                    )
                    AC_ready.append(ac)
                    # 更新房间的 status 为 waiting，表示它已经进入调度队列
                    room.status = Status.waiting
                    session.add(room)  # 将更新后的房间保存到数据库
            session.commit()
            print(AC_ready)
    # print(AC_ready)
    update_ac_queues(session)
    # 检查当前的over列表中是否有待执行的内容
    # over_deltas = " ".join([str(ac.tar_temp - ac.cur_temp) for ac in AC_over])
    # print(f"AC_over 中的 deltas: {over_deltas}")
    len_o =len(AC_over)
    i =0
    while(i!=len_o):
        if (AC_over[i].cur_temp - AC_over[i].tar_temp>= 0.99 and not AC_over[i].model) or (AC_over[i].tar_temp -AC_over[i].cur_temp >= 0.99 and AC_over[i].model):
            ac_o=AC_over.pop(i)
            ac_o.start_time = now
            AC_ready.append(ac_o)
            i-=1
            len_o-=1
        i+=1
      
    # 检查当前active队列中有没有已经达到要求的数据,移动到over队列
    len_a =len(AC_active)
    i=0
    while(i!=len_a):
        # active_deltas = " ".join([str(ac.tar_temp - ac.cur_temp) for ac in AC_active])
        # print(f"AC_active 中的 deltas: {active_deltas}")
        if (((AC_active[i].cur_temp - AC_active[i].tar_temp)>-0.01) and AC_active[i].model) or (((AC_active[i].cur_temp - AC_active[i].tar_temp)<0.01) and not AC_active[i].model):
            ac_a=AC_active.pop(i)
            ac_a.start_time = now
            AC_over.append(ac_a)
            i-=1
            len_a-=1
        i+=1
        
    len_r =len(AC_ready)
    i=0
    while(i!=len_r):
        # active_deltas = " ".join([str(ac.tar_temp - ac.cur_temp) for ac in AC_active])
        # print(f"AC_active 中的 deltas: {active_deltas}")
        if (((AC_ready[i].cur_temp - AC_ready[i].tar_temp)>-0.01) and AC_ready[i].model) or (((AC_ready[i].cur_temp - AC_ready[i].tar_temp)<0.01) and not AC_ready[i].model):
            ac_r=AC_ready.pop(i)
            ac_r.start_time = now
            AC_over.append(ac_r)
            i-=1
            len_r-=1
        i+=1
    # over_ids = " ".join([ac.ac_id for ac in AC_over])
    # print(f"AC_over 中的 room_id: {over_ids}")
  
            
    # 首先进行等待序列的排序，按照风速等级+等待时间进行排序
    AC_ready = sorted(AC_ready, key=lambda ac: (-ac.wind_level, ac.start_time))
    AC_active = sorted(AC_active, key=lambda ac: (ac.wind_level, ac.start_time))
 
        
    # 首先将ready中优先级最高的加入到active中
    while(len(AC_active)<3 and len(AC_ready)>0):
        ac_r = AC_ready.pop(0)
        ac_r.start_time = now
        AC_active.append(ac_r)
    # 将ready中最优先加入的和active中最优先脱出的进行比较，可以仔细想想其中的逻辑，本身应该没有问题
    ran = min(3, len(AC_active), len(AC_ready))
    for i in range(ran):
        # 等待中的风速等级更高的情况中
        if AC_ready[0].wind_level > AC_active[0].wind_level:
            ac_r = AC_ready.pop(0)
            ac_a = AC_active.pop(0)
            ac_r.start_time = now
            ac_a.start_time = now
            AC_ready.append(ac_a)
            AC_active.append(ac_r)
        # 风速相等的情况下，查看是否完成了时间片
        elif AC_ready[0].wind_level == AC_active[0].wind_level:
            if round((now - AC_ready[0].start_time).total_seconds()) >= timeslice:
                ac_a = AC_active.pop(0)
                ac_r = AC_ready.pop(0)
                ac_a.start_time = now
                ac_r.start_time = now
                AC_active.append(ac_r)
                AC_ready.append(ac_a)
    # 打印 AC_active 和 AC_ready 中的 room_id，以空格分隔
    active_ids = ' '.join([ac.ac_id for ac in AC_active])
    ready_ids  = ' '.join([ac.ac_id for ac in AC_ready])

    if(active_ids or ready_ids):
        schedule_log = acScheduleLog(time=datetime.now(),waitQueue=ready_ids,runningQueue = active_ids)
        session.add(schedule_log)
        session.commit()
    session.close()
    over_ids = ' '.join([ac.ac_id for ac in AC_over])

    print(f"AC_active 中的 room_id: {active_ids}")
    print(f"AC_ready 中的 room_id: {ready_ids}")
    print(f"AC_over 中的 room_id: {over_ids}")
    lock.release()


CHECK_TIME = 10
def temperature_update():
    global AC_ready  # 显式声明AC_ready为全局变量
    global AC_active  # 显式声明AC_ready为全局变量
    global AC_over  # 显式声明AC_ready为全局变量
    global lock
    session = get_session_()
    ac_mode = session.exec(select(acControl.ac_model).order_by(acControl.record_time.desc())).first()
    delta = 0.5 if ac_mode else -0.5
    run_delta = 1 if ac_mode else -1
    now = datetime.now()
    for ac in AC_over:
        print(f"AC_over: {round((now - ac.start_time).total_seconds())}")
        if round((now-ac.start_time).total_seconds()) >= CHECK_TIME:
            if (ac_mode and ac.cur_temp <= ac.env_temp) or (not ac_mode and  ac.cur_temp >= ac.env_temp):
                continue
            if ac_mode:
                ac.cur_temp = max(ac.env_temp, ac.cur_temp-delta)
            else:
                ac.cur_temp = min(ac.env_temp, ac.cur_temp-delta)
                # 写入 Room 表
            room = session.exec(select(Room).where(Room.room_id == ac.ac_id)).first()
            if room:
                room.roomTemperature = ac.cur_temp
                session.add(room)
    for ac in AC_ready:
        if round((now-ac.start_time).total_seconds()) >= CHECK_TIME:
            if (ac_mode and ac.cur_temp <= ac.env_temp) or (not ac_mode and  ac.cur_temp >= ac.env_temp):
                continue
            if ac_mode:
                ac.cur_temp = max(ac.env_temp, ac.cur_temp-delta)
            else:
                ac.cur_temp = min(ac.env_temp, ac.cur_temp-delta)
            room = session.exec(select(Room).where(Room.room_id == ac.ac_id)).first()
            if room:
                room.roomTemperature = ac.cur_temp
                session.add(room)
    for ac in AC_active:
        pre_temp=ac.cur_temp
        if round((now-ac.start_time).total_seconds()) >= CHECK_TIME:
            if ac.wind_level == 0:
                ac.cur_temp += run_delta * 0.333
            elif ac.wind_level == 1:
                ac.cur_temp += run_delta * 0.5
            elif ac.wind_level == 2:
                ac.cur_temp += run_delta * 1.0
            room = session.exec(select(Room).where(Room.room_id == ac.ac_id)).first()
            if room:
                room.roomTemperature = ac.cur_temp
                session.add(room)
             # 更新 acLog 表的 cost 值
            ac_log = session.exec(select(acLog).where(and_(acLog.room_id == ac.ac_id, acLog.power == True)).order_by(acLog.change_time.desc())).first()
            if ac_log:
                temperature_change = abs(ac.cur_temp - pre_temp)
                ac_log.cost += temperature_change  # 将温度变化的绝对值加到cost
                session.add(ac_log)  # 更新acLog
    # 对不在 AC_active, AC_ready, AC_over 队列中的房间进行温度更新
    room_ids_in_queues = [ac.ac_id for ac in AC_active + AC_ready + AC_over]
    all_rooms = session.exec(select(Room)).all()
    for room in all_rooms:
        if room.room_id not in room_ids_in_queues:  # 如果房间不在任何一个队列中
            # 按照规则更新温度
            if ac_mode:
                room.roomTemperature = max(room.environTemperature, room.roomTemperature - delta)
            else:
                room.roomTemperature = min(room.environTemperature, room.roomTemperature - delta)
            # 将更新后的房间添加到 session 中
            session.add(room)
    session.commit()
    session.close()


def roomcost_update():
    session = get_session_()
    # 获取所有房间ID
    room_ids = session.exec(select(Room.room_id)).all()
    # 记录所有更新的房间
    rooms_to_update = []
    lock.acquire()
    for room_id in room_ids:
        # 更新 Room 表中的 cost 和 totalCost
        room = session.exec(select(Room).where(Room.room_id == room_id)).first()
        if room and room.hotel_checks:
            hotel_check = room.hotel_checks[-1]
            # 查找该房间的所有acLog记录
            logs = session.exec(
                select(acLog).where(acLog.room_id == room_id, acLog.change_time >= hotel_check.check_in_date).order_by(acLog.change_time.desc())
            ).all()

            if logs:
                # 计算所有acLog记录的cost之和
                total_cost = sum(log.cost for log in logs)
                
                # 获取最新一条acLog记录的cost
                latest_aclog = logs[0] 
                room.cost =  latest_aclog.cost  # 更新最新记录的cost
                room.totalCost = total_cost  # 更新totalCost为所有acLog记录的cost之和
                rooms_to_update.append(room)
        
            

    # 批量提交所有修改的房间
    if rooms_to_update:
        session.add_all(rooms_to_update)
        session.commit()
    session.close()
    lock.release()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(temperature_update, 'interval', seconds= CHECK_TIME)
    scheduler.add_job(callback, 'interval', seconds= CHECK_TIME)  # 每10秒执行一次回调
    scheduler.add_job(roomcost_update, 'interval', seconds= CHECK_TIME)
    scheduler.start()
    
  
