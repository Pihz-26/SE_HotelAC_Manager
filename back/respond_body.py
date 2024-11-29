from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from front.request_body import Person

class NormalRespond(BaseModel):
    code: int
    message: str
    
# 定内部的 Data 数据模型
class RoomACData(BaseModel):
    roomTemperature: int
    power: str
    temperature: int
    windSpeed: str
    mode: str
    sweep: str
    cost: float
    totalCost: float
    


      
class CheckInState(BaseModel):
    roodId: int
    roomLevel: str
    cost: int
    checkInTime: datetime
    people: Optional[Person]
 
class AcLogRecord(BaseModel):
    time: datetime
    cost: float
    power: str
    temperature: int
    windSpeed: str
    mode: str
    sweep: str
    

class RoomRecords(BaseModel):
    cost: int
    people: Optional[Person]
    records: Optional[AcLogRecord] 
  
class RoomAcStatus(BaseModel):
    roomId: int
    roomTemperature: int
    power: str
    temperature: int
    windSpeed: str
    mode: str
    sweep: str
    cost: float
    totalCost: float
    status: int
    timeSlice: int 
  
class AcControlLog(BaseModel):
    roomId: int
    time: datetime
    cost: float
    energyCost: float
    power: str
    temperature: int
    windSpeed: str
    mode:   str
    sweep: str
    status: str
    timeSlice: int
    
class AcScheduleLog(BaseModel):
    time: datetime
    waitQueue: Optional[int]
    runningQueue: Optional[int] 
    
class RoomStatus(BaseModel):
    roomId: int
    roomLevel: str
    people: Optional[Person]
    cost: int
    roomTemperature: int
    power: str
    temperature: int
    windSpeed: str
    mode: str
    sweep: str
  
class RoomACStateRespond(BaseModel):
    code: int
    message: str 
    data: Optional[RoomACData]
    
class AdminLoginRespond(BaseModel):
    code: int
    message: str
    token: str
    role: str
    
class TotalHotelCheckInStatusRespond(BaseModel):
    code: int
    message: str
    data: Optional[CheckInState]
    
class PeopleLog(BaseModel):
    time: datetime
    roomId: int
    operation: str


    
class  DetailsRespond(BaseModel):
    code: int
    checkInTime: datetime
    message: str
    data: Optional[RoomRecords]


    
class TotalAcStatusRespond(BaseModel):
    code: int
    message: str
    data: Optional[RoomAcStatus]
    

    
class WeeklyAcControlLogRespond(BaseModel):
    code: int
    message: str
    data: Optional[AcControlLog]
 
   
class WeeklyAcScheduleRespond(BaseModel):
    code: int
    message: str
    data: Optional[AcScheduleLog]
   

       
class WeeklyPeopleLogRespond(BaseModel):
    code: int
    message: str
    data: Optional[PeopleLog]
    
  
class RoomStatusRespond(BaseModel):
    code: int
    message: str
    data: Optional[RoomStatus]
    

# 登录请求数据模型
class LoginRequest(BaseModel):
    user_id: str
    password: str