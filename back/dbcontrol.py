from typing import Annotated, List, Optional
from enum import Enum
from fastapi import Depends
from respond_body import NormalRespond
from sqlalchemy import func
from sqlmodel import Field, Session, SQLModel, Relationship, create_engine, select
from datetime import datetime
from sqlalchemy.exc import IntegrityError

'''
此处文件主要用于更新数据库中的数据，对数据库中的数据进行相应的查询操作，同时返回
整个过程中按照一定思路给出了不同应答情况的返回数据
'''


class RoomLevel(str, Enum):
    Standard= "标准间"
    Queen= "大床房"
    
class WindLevel(int, Enum):
    Low= 0
    Medium= 1
    High= 2
    
class ACModel(int, Enum):
    Cold= 0
    Warm= 1

class Status(int, Enum):
    waiting= 0
    running= 1
    noschedule= 2
    
# 房间数据表    
class Room(SQLModel, table=True):
    room_id: str   =  Field(index=True, description="Room number", primary_key=True)
    room_level: RoomLevel = Field(default = RoomLevel.Standard, description="Room level")
    state: bool = Field(default=False, description="whether the room have been checked in")
    targetTemperature: float = Field(default=25, description="The target temperature of the room")
    roomTemperature: float = Field(default=26, description="The current temperature of the room")
    environTemperature: float = Field(default=26, description="The environment temperature of the room")
    # 当前房间中空调的状态，其中包括当前花费
    cost: float = Field(default = 0, description="current AC cost in the room")
    totalCost:float =Field(default = 0, description=" totalCost in the room")
    # 风速、是否开启扫风、是否开机
    wind_level: WindLevel = Field(default=WindLevel.Medium, description="AC's wind level")
    sweep: bool = Field(default=False, description="Launch sweep mode or not");
    power: bool = Field(default=False, description="Whether the AC has been launched or not")
    # 定义与 HotelCheck 的关系
    hotel_checks: List["HotelCheck"] = Relationship(back_populates="room")
    status:Status = Field(default=Status.noschedule, description="AC schedule status")
    daily_cost: int = Field(default=0)
    
    
    
# 酒店入住情况记录表, 将
class HotelCheck(SQLModel, table=True):
    person_id: str                 = Field(index=True, default=None, primary_key=True)
    guest_name: str         = Field(index=True, description="Name of the guest")
    room_id: str        = Field(foreign_key="room.room_id",index=True, primary_key=True,description="Room number assigned to the guest")
    check_in_date: datetime = Field(default_factory=datetime.now, primary_key=True, description="Check-in date and time")
    check_out_date: Optional[datetime] = Field(default=None, description="Check-in date and time")
    # 定义与 Room 的关系
    room: Room = Relationship(back_populates="hotel_checks")
    

# 空调操作记录表
class acLog(SQLModel, table=True):
    room_id: str = Field(index=True, primary_key=True, foreign_key="room.room_id",description="Room number")
    # 空调模式和温度设置
    ac_model: ACModel = Field(default=ACModel.Cold)
    temperature: int = Field(default=26)
    change_time: datetime = Field(default_factory=datetime.now,  primary_key=True, description="the time of changing AC state") 
    power:bool = Field(default=False, description="Whether the AC has been launched or not")
    wind_level: WindLevel = Field(default=WindLevel.Low, description="AC's wind level")
    sweep: bool = Field(default=False, description="Launch sweep mode or not")
    cost: int = Field(default=0)
    cur_status: Status = Field(default=Status.running)

# 中央空调控制表，按照需求应该只用调节温度和模式
class acControl(SQLModel, table=True):
    record_time: datetime = Field(default_factory=datetime.now,  primary_key=True, description="the time of changing AC") 
    ac_model: ACModel = Field(default=ACModel.Cold)
    temperature: int = Field(default=26)

class acPamater(SQLModel, table=True):
    precept: int = Field(default=1, primary_key=True)
    low_cost_rate: float = Field(default=0.5)
    middle_cost_rate: float = Field(default=1.0)
    high_cost_rate: float = Field(default=2.0)
    
class acScheduleLog(SQLModel, table=True): 
    time: datetime = Field(default_factory=datetime.now, primary_key=True, description="the time of acSchedule state")
    waitQueue: str = Field(default="")
    runningQueue: str = Field(default="")


    
    
       
class User(SQLModel, table=True):
    user_id: str = Field(default="123", primary_key=True)
    password: str = Field(default='123')
    role: str = Field(default='admin')

class RoomCheckIn(): 
    '''
    类中应该传入两个数据，分别为房间号和入住人数据，入住人数据用(name, id)的元组来储存
    '''
    def __init__(self, room_id:str, people: List[tuple]):
        self.room_id:str = room_id
        self.people:List = people

class RoomAcData():
    '''
    类中包括房间中对空调的数据更改
    '''
    def __init__(self, wind_level:WindLevel, sweep: bool, power: bool, model:ACModel, temperature:int):
        self.wind_level = wind_level
        self.sweep = sweep
        self.power = power
        self.model = model
        self.temperature = temperature       

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables(session):
    SQLModel.metadata.create_all(engine)

    

def get_session():
    with Session(engine) as session:
        yield session

def get_session_():
    session = Session(engine)  # 直接返回数据库会话对象
    return session  # 返回的是一个已经实例化的session对象

SessionDep = Annotated[Session, Depends(get_session)]

# 数据库中编写入住数据，请在执行之前进行相应数据合法性检测
def data_check_in(check_in_data:RoomCheckIn, session: SessionDep):
    final_data = []
    for person in check_in_data.people:
        print(1, person)
        hotel_check = HotelCheck()
        hotel_check.guest_name = person[0]
        hotel_check.person_id = person[1]
        hotel_check.room_id = check_in_data.room_id
        hotel_check.check_in_date = datetime.now()
        # 将 HotelCheck 和 Room 对象关联
        room = session.exec(select(Room).where(Room.room_id == check_in_data.room_id)).first()
        if room:
            hotel_check.room = room  # 设置房间关系
            room.state = True  # 更新房间状态为已入住
            # 计费状态初始化
            room.cost = 0
            room.totalCost = 0
            # 空调状态初始化
            room.power = False
            room.roomTemperature = room.environTemperature
            room.targetTemperature = 25
            room.wind_level = WindLevel.Medium
            room.sweep = False
            room.status = Status.noschedule
            room.hotel_checks.append(hotel_check)  # 更新房间的入住记录
        final_data.append(hotel_check)
    session.add_all(final_data)
    session.commit()
    

# 数据库中编写入住数据，请在执行之前进行相应数据合法性检测
def data_room(room_data:Room, session: SessionDep):
    session.merge(room_data)
    session.commit()
    
def delete_room(room_id: str, session: SessionDep):
    """
    从数据库中删除指定的房间。
    参数：
        - room_id: 要删除的房间ID
        - session: 数据库会话
    返回：
        - 删除成功则提交更改，否则抛出异常
    """
    room = session.exec(select(Room).where(Room.room_id == room_id)).first()
    if not room:
        raise ValueError(f"Room with ID {room_id} does not exist.")
    session.delete(room)
    session.commit()
    
# 数据库中进行退房数据更改，请在执行前进行相应数据的合法性检测
def data_check_out(room_id: str, session: SessionDep):     
    rooms = session.exec(select(Room).where(Room.room_id == room_id)).all()
    room = rooms[0]
    if not room:
        return NormalRespond (
            code=1, 
            message="房间不存在"
            )
    else:
        room.power = False
        room.state = False
    # 获取当前时间
    check_out_time = datetime.now()
    data = {}
    if not room.hotel_checks:
        return NormalRespond(
            code=1, 
            message="该房间没有入住记录"
            )
        
    hotel_check = room.hotel_checks[-1]
    # print(hotel_check)
    # 获取顾客入住时间
    check_in_time = hotel_check.check_in_date
    # 退房操作：更新房间状态，清除顾客入住记录
    hotel_check.check_out_date = check_out_time
    session.commit()

    statement = (select(acLog)).where(
        acLog.change_time >= check_in_time,
        acLog.change_time <= check_out_time,
        acLog.power == False
        )
    
    results = session.exec(statement).all()
    off_count = len(results)

    
    if off_count == 0:
        off_count = 1  # 至少1天入住费用
    # print(off_count)

    # 计算房费
    room_cost = room.daily_cost * off_count  # 假设每晚住宿费为100元
    print(room_cost)
    # 查询空调消费记录
    ac_logs = session.exec(select(acLog).where(acLog.room_id == room_id).where(acLog.change_time >= check_in_time).where(acLog.change_time <= check_out_time)).all()
    ac_cost = sum(log.cost for log in ac_logs)  # 空调总费用计算
    
    # 生成账单
    total_cost = room_cost + ac_cost
    
    data = {
    "roomCost": room_cost,
    "acCost": ac_cost,
    "totalCost": total_cost,
    "stayDuration": off_count,
    # "acLogs": [{"time": log.change_time, "cost": log.cost} for log in ac_logs]
    }
    
    return {
        "code": 0,
        "message": "退房成功",
        "bill":data
    }
        


def delete_acLog(room_id: str, session: SessionDep):
    """
    从数据库中删除指定房间的所有 acLog 记录。
    参数：
        - room_id: 要删除的房间ID
        - session: 数据库会话
    返回：
        - 删除成功的消息
    """
    # 查询所有符合条件的 acLog 记录
    logs_to_delete = session.exec(select(acLog).where(acLog.room_id == room_id)).all()

    if not logs_to_delete:
        raise ValueError(f"No acLog records found for Room ID {room_id}.")

    # 逐条删除记录
    for log in logs_to_delete:
        session.delete(log)
    # 提交更改
    session.commit()
    return f"All acLog records for Room ID {room_id} deleted successfully."


# 空调控制记录
def updateACLog(room_id:str, room_ac_data:RoomAcData, session: SessionDep):
    ac_log = acLog()
    ac_log.room_id = room_id
    
    ac_log.wind_level = room_ac_data.wind_level
    ac_log.sweep = room_ac_data.sweep
    ac_log.power = room_ac_data.power
    
    ac_log.ac_model = room_ac_data.model
    ac_log.temperature = room_ac_data.temperature
    
    session.add(ac_log)
    session.commit()

# 更新当前房间的空调状态    
def updateRoomAcData(room_id:str, cost:int, room_ac_data:RoomAcData, session: SessionDep):
    statement = select(Room).where(Room.room_id == room_id)
    result = session.exec(statement)
    for room in result:
        room.cost = cost
        room.wind_level = room_ac_data.wind_level
        room.sweep = room_ac_data.sweep
        room.power = room_ac_data.power
       
# 更改空调状态控制表
def updateAcControl(ac_model: ACModel, temperature: int):
    ac_control =  acControl()
    ac_control.ac_model = ac_model
    ac_control.temperature = temperature

def init_users(session: SessionDep):
    predefined_users = [
        {"user_id": "front_desk", "password": "front_desk", "role": "前台服务"},
        {"user_id": "ac_manager", "password": "ac_manager", "role": "空调管理"},
        {"user_id": "manager", "password": "manager", "role": "酒店经理"}
    ]

    for user_data in predefined_users:
        user = User(
            user_id=user_data["user_id"],
            password=user_data["password"],
            role=user_data["role"]
        )

        try:
            session.add(user)
            session.commit()  # 提交到数据库
        except IntegrityError:
            session.rollback()  # 如果已存在用户，回滚操作
            print(f"User {user_data['user_id']} already exists.")


def init_acc_cold(session: SessionDep):
    # 更新空调控制表
    ac_control = acControl(ac_model=ACModel(0), temperature=26)  # 默认温度为26度
    

    ac_param = acPamater()  # 如果没有记录，创建新的
    ac_param.low_cost_rate = 0.33
    ac_param.middle_cost_rate = 0.5
    ac_param.high_cost_rate = 1
    try:
        session.add(ac_control)
        session.add(ac_param)
        session.commit()  # 提交到数据库
        print("中央空调已成功初始化为制冷")
    except IntegrityError:
        session.rollback()
        print("中央空调已为制冷")
        

def init_acc_hot(session: SessionDep):
    # 更新空调控制表
    ac_control = acControl(ac_model=ACModel(1), temperature=26)  # 默认温度为26度
    

    ac_param = acPamater()  # 如果没有记录，创建新的
    ac_param.low_cost_rate = 0.33
    ac_param.middle_cost_rate = 0.5
    ac_param.high_cost_rate = 1
    try:
        session.add(ac_control)
        session.add(ac_param)
        session.commit()  # 提交到数据库
        print("中央空调已成功初始化为制热")
    except IntegrityError:
        session.rollback()


def init_rooms_cold(session:SessionDep):
    # 初始化5个房间数据
    rooms = []
    
    rooms.append(Room(room_id=f"2001", daily_cost=100, roomTemperature=32, environTemperature=32))
    rooms.append(Room(room_id=f"2002", daily_cost=125, roomTemperature=28, environTemperature=28))
    rooms.append(Room(room_id=f"2003", daily_cost=150, roomTemperature=30, environTemperature=30))
    rooms.append(Room(room_id=f"2004", daily_cost=200, roomTemperature=29, environTemperature=29))
    rooms.append(Room(room_id=f"2005", daily_cost=100, roomTemperature=35, environTemperature=35))

    # 将房间数据添加到数据库
    try:
        session.add_all(rooms)
        session.commit()  # 提交到数据库
        print("5个房间数据已成功初始化")
    except IntegrityError:
        session.rollback()  # 如果已存在房间数据，回滚操作
        print("房间数据已经存在")


def init_rooms_hot(session:SessionDep):
    # 初始化5个房间数据
    rooms = []
    
    rooms.append(Room(room_id=f"2001", daily_cost=100, roomTemperature=10, environTemperature=10, targetTemperature=22))
    rooms.append(Room(room_id=f"2002", daily_cost=125, roomTemperature=15, environTemperature=15, targetTemperature=22))
    rooms.append(Room(room_id=f"2003", daily_cost=150, roomTemperature=18, environTemperature=18, targetTemperature=22))
    rooms.append(Room(room_id=f"2004", daily_cost=200, roomTemperature=12, environTemperature=12, targetTemperature=22))
    rooms.append(Room(room_id=f"2005", daily_cost=100, roomTemperature=14, environTemperature=14, targetTemperature=22))

    # 将房间数据添加到数据库
    try:
        session.add_all(rooms)
        session.commit()  # 提交到数据库
        print("5个房间数据已成功初始化")
    except IntegrityError:
        session.rollback()  # 如果已存在房间数据，回滚操作
        print("房间数据已经存在")
    

    

