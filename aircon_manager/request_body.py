# front/request_body.py

from pydantic import BaseModel

class FanRates(BaseModel):
    lowSpeedRate: float
    midSpeedRate: float
    highSpeedRate: float

class CentralAirconAdjustRequest(BaseModel):
    mode: int  # 0 for cooling, 1 for heating
    resourceLimit: int  # 0 for no limit
    fanRates: FanRates
