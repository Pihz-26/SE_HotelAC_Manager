# front/respond_body.py

from pydantic import BaseModel
from typing import List

class RoomStatus(BaseModel):
    roomId: int
    roomTemperature: float
    power: str
    temperature: float
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
    data: List[RoomStatus]

class NormalResponse(BaseModel):
    code: int
    message: str
