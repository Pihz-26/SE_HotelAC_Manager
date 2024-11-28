# client/respond_body.py

from pydantic import BaseModel

class NormalResponse(BaseModel):
    code: int
    message: str

class AirconPanelData(BaseModel):
    roomTemperature: int
    power: str
    temperature: int
    windSpeed: str
    mode: str
    sweep: str
    cost: float
    totalCost: float

class AirconPanelResponse(BaseModel):
    code: int
    message: str
    data: AirconPanelData
