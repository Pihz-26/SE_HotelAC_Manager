# back/dbcontrol.py

from typing import List, Optional
from enum import Enum
from sqlmodel import Field, Session, SQLModel, Relationship, select, create_engine
from datetime import datetime
import json

# 定义枚举类型
class RoomLevel(str, Enum):
    Standard = "标准间"
    Queen = "大床房"

class WindLevel(str, Enum):
    Low = "低"
    Medium = "中"
    High = "高"

class ACModel(str, Enum):
    Cold = "制冷"
    Warm = "制热"

# 房间数据表
class Room(SQLModel, table=True):
    room_id: int = Field(index=True, description="房间号", primary_key=True)
    room_level: RoomLevel = Field(default=RoomLevel.Standard, description="房间类型")
    state: bool = Field(default=False, description="是否已入住")
    room_temperature: int = Field(default=25, description="当前室温")
    cost: float = Field(default=0.0, description="房间空调费用")
    total_cost: float = Field(default=0.0, description="房间空调总费用")
    temperature: int = Field(default=24, description="设定温度")
    wind_speed: WindLevel = Field(default=WindLevel.Low, description="空调风速")
    sweep: str = Field(default="关", description="扫风功能开启状态")
    power: str = Field(default="off", description="空调电源状态")
    mode: ACModel = Field(default=ACModel.Cold, description="空调模式")
    status: int = Field(default=0, description="空调状态")  # 0-关闭，1-运行
    time_slice: int = Field(default=0, description="分配的时间片")

    hotel_checks: List["HotelCheck"] = Relationship(back_populates="room")

# 酒店入住情况记录表
class HotelCheck(SQLModel, table=True):
    person_id: int = Field(default=None, primary_key=True)
    guest_name: str = Field(index=True, description="入住者姓名")
    room_id: int = Field(foreign_key="room.room_id", index=True, description="房间号")
    check_in_date: datetime = Field(default_factory=datetime.now, description="入住时间")
    check_out_date: Optional[datetime] = Field(default=None, description="退房时间")
    room: Room = Relationship(back_populates="hotel_checks")

# 空调操作记录表
class AcLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(index=True, foreign_key="room.room_id", description="房间号")
    ac_model: ACModel = Field(default=ACModel.Cold)
    temperature: int = Field(default=26)
    change_time: datetime = Field(default_factory=datetime.now, description="空调状态更改时间")
    power: str = Field(default="off", description="空调电源状态")
    wind_speed: WindLevel = Field(default=WindLevel.Low, description="空调风速")
    sweep: str = Field(default="关", description="扫风功能开启状态")
    cost: float = Field(default=0.0, description="此次操作消耗的功耗")

# 中央空调控制表
class AcControl(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    record_time: datetime = Field(default_factory=datetime.now, description="中央空调设置时间")
    ac_model: ACModel = Field(default=ACModel.Cold)
    resource_limit: int = Field(default=0, description="资源限制")
    fan_rates: str = Field(default="", description="风速费率，以JSON字符串形式存储")

# 数据库初始化和会话
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # 初始化房间数据
    with Session(engine) as session:
        for floor in range(2, 6):  # 楼层 2-5
            for room_number in range(1, 41):  # 每层 40 个房间
                room_id = floor * 1000 + room_number
                room_level = RoomLevel.Standard if room_number > 10 else RoomLevel.Queen
                room = Room(room_id=room_id, room_level=room_level)
                session.add(room)
        session.commit()

def get_session():
    with Session(engine) as session:
        yield session
