# front_desk/request_body.py

from pydantic import BaseModel

class CheckInRequest(BaseModel):
    roomId: int
    peopleName: str

class NormalResponse(BaseModel):
    code: int
    message: str
