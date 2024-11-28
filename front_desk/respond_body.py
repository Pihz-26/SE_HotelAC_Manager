# front_desk/respond_body.py

from pydantic import BaseModel
from typing import List

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
