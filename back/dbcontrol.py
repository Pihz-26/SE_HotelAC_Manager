from sqlalchemy.exc import IntegrityError
from typing import Annotated, List, Optional
from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, Relationship, create_engine, select
from datetime import datetime

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

    
# 房间数据表    
class Room(SQLModel, table=True):
    room_id: str   =  Field(index=True, description="Room number", primary_key=True)
    room_level: RoomLevel = Field(default = RoomLevel.Standard, description="Room level")
    state: bool = Field(default=False, description="whether the room have been checked in")
    roomTemperature: float = Field(default=26, description="The current temperature of the room")
    environTemperature: float = Field(default=26, description="The environment temperature of the room")
    # 当前房间中空调的状态，其中包括当前花费
    cost: float = Field(default = 0, description="current AC cost in the room")
    totalCost:float =Field(default = 0, description=" totalCost in the room")
    # 风速、是否开启扫风、是否开机
    wind_level: WindLevel = Field(default=WindLevel.Low, description="AC's wind level")
    sweep: bool = Field(default=False, description="Launch sweep mode or not");
    power: bool = Field(default=False, description="Whether the AC has been launched or not")
    # 定义与 HotelCheck 的关系
    hotel_checks: List["HotelCheck"] = Relationship(back_populates="room")
    status:bool = Field(default=False, description="AC schedule status")
    
    
    
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
    cur_status: bool = Field(default=False)

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


app =FastAPI()

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables(session):
    SQLModel.metadata.create_all(engine)
    init_users(session)
    init_rooms(session)
    

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


# 增加与room类有关逻辑

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
            room.hotel_checks.append(hotel_check)  # 更新房间的入住记录
        
        final_data.append(hotel_check)
    session.add_all(final_data)
    session.commit()
    

# 数据库中编写入住数据，请在执行之前进行相应数据合法性检测
def data_room(room_data:Room, session: SessionDep):
    session.add(room_data)
    session.commit()
    
# 数据库中进行退房数据更改，请在执行前进行相应数据的合法性检测
def data_check_out(room_id: str, session: SessionDep):  
    
    rooms = session.exec(select(Room).where(Room.room_id == room_id)).all()
    room = rooms[0]
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 查找该房间是否有入住记录
    statement = select(HotelCheck).where(
        HotelCheck.room_id == room_id,
        HotelCheck.check_in_date != None,  # 确保是未退房的记录
        HotelCheck.check_out_date == None 
    )
    results = session.exec(statement).all()
    print(results)
    if not results:
        raise HTTPException(status_code=404, detail="该房间没有入住记录")
    data_list = []
    # 获取当前时间
    check_out_time = datetime.now()
    for hotel_check in results:
        print(hotel_check)
        # 获取顾客入住时间
        check_in_time = hotel_check.check_in_date
        # 退房操作：更新房间状态，清除顾客入住记录
        hotel_check.check_out_date = check_out_time
        print(check_in_time, check_out_time)
        # 计算入住天数
        stay_duration = (check_out_time - check_in_time).days
        if stay_duration == 0:
            stay_duration = 1  # 至少1天入住费用

        # 计算房费（假设房费为 100 元/天）
        room_cost = 100 * stay_duration  # 假设每晚住宿费为100元
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
        "stayDuration": stay_duration,
        "acLogs": [{"time": log.time, "cost": log.cost} for log in ac_logs]  # 可选：空调详单
        } 
        data_list.append(data)

    room.state = False  # 房间状态更新
    session.commit()

    # 返回账单信息和结算凭据给顾客
    return data_list[0]


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
    




# 创建数据库连接
engine = create_engine("sqlite:///database.db")

def init_users(session: SessionDep):
    predefined_users = [
        {"user_id": "frount_desk", "password": "frount_desk", "role": "前台服务"},
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


def init_rooms(session):
    # 生成40个房间数据
    rooms = []
    for i in range(10):
        # 标准房
        rooms.append(Room(room_id=f"200{i+1}", room_level=RoomLevel.Standard, state=False))
        rooms.append(Room(room_id=f"300{i+1}", room_level=RoomLevel.Standard, state=False))
        rooms.append(Room(room_id=f"400{i+1}", room_level=RoomLevel.Standard, state=False))
        
        # 大床房
        rooms.append(Room(room_id=f"500{i+1}", room_level=RoomLevel.Queen, state=False))

    # 将房间数据添加到数据库
    try:
        session.add_all(rooms)
        session.commit()  # 提交到数据库
        print("40个房间数据已成功初始化")
    except IntegrityError:
        session.rollback()  # 如果已存在房间数据，回滚操作
        print("房间数据已经存在")
    

    

