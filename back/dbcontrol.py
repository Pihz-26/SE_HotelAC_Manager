from typing import Annotated
from typing import Union, List, Optional
from enum import Enum


from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, Relationship, ForeignKey, create_engine, select
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

class Status(int,Enum):
    waiting=0
    runing=1
    noschedule =2

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
    # 、风速、是否开启扫风、是否开机
    wind_level: WindLevel = Field(default=WindLevel.Low, description="AC's wind level")
    sweep: bool = Field(default=False, description="Launch sweep mode or not");
    power: bool = Field(default=False, description="Whether the AC has been launched or not")
    # 定义与 HotelCheck 的关系
    hotel_checks: List["HotelCheck"] = Relationship(back_populates="room")
    status:Status = Field(default=Status.noschedule, description="AC schedule status")
    
    
    
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
    password: str = Field(default="123")

  
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


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# 数据库中编写入住数据，请在执行之前进行相应数据合法性检测
def data_check_in(check_in_data:RoomCheckIn, session: SessionDep):
    final_data = []
    for person in check_in_data.people:
        hotel_check = HotelCheck()
        hotel_check.guest_name = person[0]
        hotel_check.person_id = person[1]
        hotel_check.room_id = check_in_data.room_id
        final_data.append(hotel_check)
    session.add_all(final_data)
    session.commit()

# 数据库中编写入住数据，请在执行之前进行相应数据合法性检测
def data_room(room_data:Room, session: SessionDep):
    session.add(room_data)
    session.commit()

# 数据库中进行退房数据更改，请在执行前进行相应数据的合法性检测
def data_check_out(room_id: str, session: SessionDep):  
    # 寻在出住房数据中房间号相同，入住日期存在，退房日期不存在的数据
    statement = select(HotelCheck).where(
        HotelCheck.room_id == room_id,
        HotelCheck.check_in_date != None,  # check_out_date 不为 None
        HotelCheck.check_out_date == None 
    )
    results = session.exec(statement)
    # 将其中的退房数据全部赋予当前值
    current_time = datetime.now()
    for hotel_check in results:
        hotel_check.check_out_date = current_time
       
    session.commit()

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
    

   

