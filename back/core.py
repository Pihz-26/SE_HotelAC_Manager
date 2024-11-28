# core.py
from fastapi import HTTPException
from sqlmodel import Session, select
from typing import Dict
from  respond_body import *
from dbcontrol import *
from fastapi.responses import JSONResponse


async def control_ac_core(
    adjust_request: AdjustRequest,  # 请求数据
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
