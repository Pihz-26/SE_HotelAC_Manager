# client/request_body.py

from pydantic import BaseModel

class AirconControlRequest(BaseModel):
    roomId: int
    power: str         # 'on' or 'off'
    temperature: int   # 16 - 30
    windSpeed: str     # '低', '中', '高'
    sweep: str         # '关', '开'
