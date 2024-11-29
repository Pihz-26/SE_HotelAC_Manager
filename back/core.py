# core.py
from fastapi import HTTPException
from sqlmodel import Session, select
from typing import Dict
from  respond_body import *
from dbcontrol import *
from fastapi.responses import JSONResponse


async def control_ac_core(
    adjust_request: CenterAcControlRequest,  # 请求数据
    session: SessionDep   # 获取数据库 session
):
    # 验证空调模式是否正确
    if adjust_request.mode not in [ACModel.Cold.value, ACModel.Warm.value]:
        raise HTTPException(status_code=400, detail="Invalid mode value. 0 for Cold, 1 for Warm.")
    
    # 验证 resourceLimit
    if adjust_request.resourceLimit not in [0, 1]:
        raise HTTPException(status_code=400, detail="resourceLimit must be 0 or 1.")
    
    # 验证风速费率
    fanRates = adjust_request.fanRates
    if "lowSpeedRate" not in fanRates or "midSpeedRate" not in fanRates or "highSpeedRate" not in fanRates:
        raise HTTPException(status_code=400, detail="Fan speed rates (low, mid, high) must be provided.")

    # 更新空调控制表
    ac_control = acControl(ac_model=ACModel(adjust_request.mode), temperature=26)  # 默认温度为26度
    session.add(ac_control)
    session.commit()

    # 更新风速费率表
    ac_param = session.exec(select(acPamater).where(acPamater.precept == 1)).first()  # 获取当前风速费率设置
    if not ac_param:
        ac_param = acPamater()  # 如果没有记录，创建新的
    ac_param.low_cost_rate = fanRates["lowSpeedRate"]
    ac_param.middle_cost_rate = fanRates["midSpeedRate"]
    ac_param.high_cost_rate = fanRates["highSpeedRate"]
    session.add(ac_param)
    session.commit()
    # 返回成功响应
    return JSONResponse(content={"code": 0, "message": "Central air conditioning settings updated successfully."})


async def get_ac_states_core(session: SessionDep) -> Dict:
    # 查询所有房间信息
    rooms = session.exec(select(Room)).all()

    # 生成空调状态列表
    ac_states = []
    for room in rooms:
        # 获取该房间的空调日志
        ac_log = session.exec(select(acLog).where(acLog.room_id == room.room_id).order_by(acLog.change_time.desc())).first()
        # 获取空调控制信息
        ac_control = session.exec(select(acControl).order_by(acControl.record_time.desc())).first()
        # 如果没有空调日志或控制信息，跳过此房间
        if not ac_log or not ac_control:
            continue

        # 构建每个房间的空调状态数据
        room_state = {
            "roomId": room.room_id,
            "roomTemperature": room.roomTemperature,
            "power": room.power,
            "temperature": ac_log.temperature,
            "windSpeed": WindLevel(room.wind_level),  
            "mode": ACModel(ac_control.ac_model),  
            "sweep": room.sweep,  # 扫风状态
            "cost": room.cost,  # 当前房间空调费用
            "totalCost": room.totalCost,  # 累计费用
            "status": room.status,  # 状态字段，表示空调调度状态
            "timeSlice": 3  # 表示分配的时间片长度
            }
        ac_states.append(room_state)
                     
    # 返回空调状态列表
    return {
        "code": 0,
        "message": "查询成功",
        "data": ac_states
    }


async def room_ac_control_core(
    request: RoomACStatusControlRequest,  # 请求体作为参数传递
    session: SessionDep  # 数据库 session
):
    # 检查房间是否存在
    room = session.get(Room, str(request.roomId))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # 转换power, windSpeed, sweep为对应值
    power_status = True if request.power == 'on' else False
    wind_speed_map = {"低": WindLevel.Low, "中": WindLevel.Medium, "高": WindLevel.High}
    sweep_status = True if request.sweep == '开' else False

    if request.windSpeed not in wind_speed_map:
        raise HTTPException(status_code=400, detail="Invalid wind speed value. Must be '低', '中', or '高'.")
    
    # 更新房间的空调状态
    room.power = power_status
    room.wind_level = wind_speed_map[request.windSpeed]
    room.sweep = sweep_status
    session.add(room)
    session.commit()

    # 记录空调操作日志
    ac_log = acLog(
        room_id=str(request.roomId),
        power=power_status,
        temperature=request.temperature,
        wind_level=wind_speed_map[request.windSpeed],
        sweep=sweep_status
    )
    session.add(ac_log)
    session.commit()

    return {"code": 0, "message": "空调设置已更新"}


#查询指定房间的空调控制面板信息
def room_ac_state_core(room_id: int, session: Session) -> Dict:
    # 获取房间的当前空调控制面板信息
    room = session.exec(select(Room).where(Room.room_id == str(room_id))).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # 获取空调的最新记录（acLog）
    ac_log = session.exec(select(acLog).where(acLog.room_id == str(room_id)).order_by(acLog.change_time.desc())).first()
    if not ac_log:
        raise HTTPException(status_code=404, detail="No AC log found for this room")

    # 获取空调控制的全局设置（acControl）
    ac_control = session.exec(select(acControl).order_by(acControl.record_time.desc())).first()
    if not ac_control:
        raise HTTPException(status_code=404, detail="No AC control settings found")

    # 格式化返回数据
    response_data = {
        "roomTemperature": room.roomTemperature ,  # 默认室温为26度
        "power": "on" if ac_log.power else "off",
        "temperature": ac_log.temperature,         #目标温度
        "windSpeed": WindLevel(room.wind_level),  # 风速
        "mode": ACModel(ac_control.ac_model),  # 空调模式
        "sweep": "开" if room.sweep else "关",
        "cost": room.cost,  # 当前费用
        "totalCost": room.totalCost #累计费用
    }
    
    return response_data