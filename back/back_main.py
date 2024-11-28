# back/back_main.py

from fastapi import FastAPI, Depends, HTTPException
from .dbcontrol import create_db_and_tables, get_session, AcControl, Room, HotelCheck, AcLog
from sqlmodel import Session, select
from pydantic import BaseModel
from .respond_body import (
    NormalResponse, AirconStatusResponse, RoomAcStatus,
    AirconPanelResponse, AirconPanelData,
    HotelStatusResponse, RoomData, People, DetailedBillResponse, RoomRecords, Record,
    RoomInfoResponse, RoomInfo
)
from typing import List
from datetime import datetime
import json

app = FastAPI()
create_db_and_tables()

# 中央空调设置请求体模型
class FanRates(BaseModel):
    lowSpeedRate: float
    midSpeedRate: float
    highSpeedRate: float

class CentralAirconAdjustRequest(BaseModel):
    mode: int  # 0 为制冷，1 为制热
    resourceLimit: int  # 资源限制（0 为无限制）
    fanRates: FanRates

# 中央空调设置接口
@app.post("/central-aircon/adjust", response_model=NormalResponse)
def control_ac(data: CentralAirconAdjustRequest, session: Session = Depends(get_session)):
    # 保存中央空调设置
    ac_control = AcControl(
        ac_model=ACModel.Cold if data.mode == 0 else ACModel.Warm,
        resource_limit=data.resourceLimit,
        fan_rates=data.fanRates.json()
    )
    session.add(ac_control)
    session.commit()
    return NormalResponse(code=0, message="中央空调设置成功")

# 获取空调状态接口
@app.get("/aircon/status", response_model=AirconStatusResponse)
def get_ac_states(session: Session = Depends(get_session)):
    # 从数据库中查询所有房间的空调状态
    statement = select(Room)
    rooms = session.exec(statement).all()

    room_status_list = []
    for room in rooms:
        status = RoomAcStatus(
            roomId=room.room_id,
            roomTemperature=room.room_temperature,
            power=room.power,
            temperature=room.temperature,
            windSpeed=room.wind_speed,
            mode=room.mode,
            sweep=room.sweep,
            cost=room.cost,
            totalCost=room.total_cost,
            status=room.status,
            timeSlice=room.time_slice
        )
        room_status_list.append(status)

    return AirconStatusResponse(code=0, message="查询成功", data=room_status_list)

# 客户端空调控制请求体
class AirconControlRequest(BaseModel):
    roomId: int
    power: str         # 'on' or 'off'
    temperature: int   # 16 - 30
    windSpeed: str     # '低', '中', '高'
    sweep: str         # '关', '开'

# 客户端空调控制
@app.post("/aircon/control", response_model=NormalResponse)
def aircon_control(data: AirconControlRequest, session: Session = Depends(get_session)):
    room = session.get(Room, data.roomId)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")

    # 更新房间状态
    room.power = data.power
    room.temperature = data.temperature
    room.wind_speed = data.windSpeed
    room.sweep = data.sweep

    # 添加空调操作记录
    ac_log = AcLog(
        room_id=room.room_id,
        ac_model=room.mode,
        temperature=room.temperature,
        power=room.power,
        wind_speed=room.wind_speed,
        sweep=room.sweep,
        cost=0.0  # 此处应计算消耗的功耗
    )
    session.add(ac_log)
    session.commit()

    return NormalResponse(code=0, message="空调设置已更新")

# 获取房间空调面板信息
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

@app.get("/aircon/panel", response_model=AirconPanelResponse)
def aircon_panel(roomId: int, session: Session = Depends(get_session)):
    room = session.get(Room, roomId)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")

    panel_data = AirconPanelData(
        roomTemperature=room.room_temperature,
        power=room.power,
        temperature=room.temperature,
        windSpeed=room.wind_speed,
        mode=room.mode,
        sweep=room.sweep,
        cost=room.cost,
        totalCost=room.total_cost
    )
    return AirconPanelResponse(code=0, message="操作成功", data=panel_data)

# 前台营业端接口实现
@app.post("/stage/query", response_model=HotelStatusResponse)
def get_hotel_status(session: Session = Depends(get_session)):
    statement = select(Room).where(Room.state == True)
    rooms = session.exec(statement).all()

    room_list = []
    for room in rooms:
        people_list = []
        for check in room.hotel_checks:
            if check.check_out_date is None:
                people = People(peopleId=check.person_id, peopleName=check.guest_name)
                people_list.append(people)
        room_data = RoomData(
            roomId=room.room_id,
            roomLevel=room.room_level.value,
            cost=room.cost,
            checkInTime=room.hotel_checks[0].check_in_date.isoformat() if room.hotel_checks else "",
            people=people_list
        )
        room_list.append(room_data)

    return HotelStatusResponse(code=0, message="查询成功", data=room_list)

class CheckInRequest(BaseModel):
    roomId: int
    peopleName: str

@app.post("/stage/add", response_model=NormalResponse)
def check_in(data: CheckInRequest, session: Session = Depends(get_session)):
    room = session.get(Room, data.roomId)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")

    person_id = int(datetime.now().timestamp())  # 简单生成 person_id，可根据需要修改
    hotel_check = HotelCheck(
        person_id=person_id,
        guest_name=data.peopleName,
        room_id=room.room_id
    )
    room.state = True
    session.add(hotel_check)
    session.commit()

    return NormalResponse(code=0, message="顾客添加成功")

@app.get("/stage/delete", response_model=NormalResponse)
def check_out(roomId: int, session: Session = Depends(get_session)):
    room = session.get(Room, roomId)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")

    # 更新所有未退房的入住记录
    for check in room.hotel_checks:
        if check.check_out_date is None:
            check.check_out_date = datetime.now()
    room.state = False
    session.commit()

    return NormalResponse(code=0, message="退房成功")

@app.get("/stage/record", response_model=DetailedBillResponse)
def get_detailed_bill(roomId: int, session: Session = Depends(get_session)):
    room = session.get(Room, roomId)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")

    # 获取入住信息
    people_list = []
    check_in_time = ""
    for check in room.hotel_checks:
        if check.check_out_date is None:
            people = People(peopleId=check.person_id, peopleName=check.guest_name)
            people_list.append(people)
            check_in_time = check.check_in_date.isoformat()

    # 获取空调操作记录
    statement = select(AcLog).where(AcLog.room_id == roomId)
    logs = session.exec(statement).all()
    records = []
    for log in logs:
        record = Record(
            time=log.change_time.isoformat(),
            cost=log.cost,
            power=log.power,
            temperature=log.temperature,
            windSpeed=log.wind_speed.value,
            mode=log.ac_model.value,
            sweep=log.sweep
        )
        records.append(record)

    room_records = RoomRecords(
        cost=room.total_cost,
        people=people_list,
        records=records
    )

    return DetailedBillResponse(
        code=0,
        checkInTime=check_in_time,
        message="查询成功",
        data=room_records
    )

# 酒店管理端接口实现
@app.post("/admin/query_room", response_model=RoomInfoResponse)
def get_room_info(session: Session = Depends(get_session)):
    statement = select(Room)
    rooms = session.exec(statement).all()

    room_info_list = []
    for room in rooms:
        people_list = []
        for check in room.hotel_checks:
            if check.check_out_date is None:
                people = People(peopleId=check.person_id, peopleName=check.guest_name)
                people_list.append(people)
        room_info = RoomInfo(
            roomId=room.room_id,
            roomLevel=room.room_level.value,
            people=people_list,
            cost=room.total_cost,
            roomTemperature=room.room_temperature,
            power=room.power,
            temperature=room.temperature,
            windSpeed=room.wind_speed,
            mode=room.mode,
            sweep=room.sweep
        )
        room_info_list.append(room_info)

    return RoomInfoResponse(code=0, message="查询成功", data=room_info_list)
