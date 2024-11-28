# back/respond_body.py

from pydantic import BaseModel
from typing import List

class NormalResponse(BaseModel):
    code: int
    message: str

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

class AirconStatusResponse(BaseModel):
    code: int
    message: str
    data: List[RoomAcStatus]

class People(BaseModel):
    peopleId: int
    peopleName: str

class RoomData(BaseModel):
    roomId: int
    roomLevel: str
    cost: float
    checkInTime: str
    people: List[People]

class HotelStatusResponse(BaseModel):
    code: int
    message: str
    data: List[RoomData]

class Record(BaseModel):
    time: str
    cost: float
    power: str
    temperature: int
    windSpeed: str
    mode: str
    sweep: str

class RoomRecords(BaseModel):
    cost: float
    people: List[People]
    records: List[Record]

class DetailedBillResponse(BaseModel):
    code: int
    checkInTime: str
    message: str
    data: RoomRecords

class RoomInfo(BaseModel):
    roomId: int
    roomLevel: str
    people: List[People]
    cost: float
    roomTemperature: int
    power: str
    temperature: int
    windSpeed: str
    mode: str
    sweep: str

class RoomInfoResponse(BaseModel):
    code: int
    message: str
    data: List[RoomInfo]
