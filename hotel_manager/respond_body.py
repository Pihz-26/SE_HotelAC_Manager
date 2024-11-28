# hotel_manager/respond_body.py

from pydantic import BaseModel
from typing import List

class People(BaseModel):
    peopleId: int
    peopleName: str

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
