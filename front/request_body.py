from pydantic import BaseModel
from typing import Optional
from typing import Literal


class FanRate(BaseModel):
    lowSpeedRate: float
    midSpeedRate: float
    highSpeedRate: float

# 房间空调状态设置的请求体
class RoomACStatusControlRequest(BaseModel):
    roomId: int                # 房间号，类型为整型
    power: Literal["on", "off"]               # 电源状态，例如 "on" 或 "off"
    temperature: int           # 温度，类型为整型
    windSpeed: Literal["低", "中", "高"]             # 风速，可能为 "低", "中", "高" 等
    sweep: str    
    
class AdminLoginRequest(BaseModel):
    username: str
    password: str
    
class Person(BaseModel):
    peopleId: int
    peopleName: str
    
    
class CenterAcControlRequest(BaseModel):
    mode: int
    resourceLimit: int
    fanRate: Optional[FanRate]
    


aa