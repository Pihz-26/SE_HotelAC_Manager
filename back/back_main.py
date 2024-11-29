from fastapi import FastAPI
from core import *
from respond_body import *

app = FastAPI()

# 控制指定房间的空调设置
@app.get("/aircon/control")
async def room_ac_control(
    request: RoomACStatusControlRequest,  # 请求体
    session: SessionDep  # 获取数据库 sessionDep
):
    # 调用核心函数
    return await room_ac_control_core(request, session)

# 查询指定房间的空调控制面板信息
@app.get("/aircon/panel")
async def room_ac_state(roomId: int, session: SessionDep):
    # 调用核心函数获取指定房间的空调状态
    data = room_ac_state_core(roomId, session)
    return {"code": 0, "message": "操作成功", "data": data}
   

# 管理员登录，通过验证账号和密码后，发放JWT并提供管理员的身份信息供后续请求使用。
@app.get("/admin/login")
async def admin_login():
    pass

# 查询管理员有权限查看的所有房间信息
@app.get("/stage/query")   
async def room_state():
    pass

# 向指定房间添加新的顾客
@app.get("/stage/add") 
async def check_in():
    pass

# 退房
@app.get("/stage/delete")
async def check_out():
    pass

# 查询指定房间的开具详单的全部信息
@app.get("/stage/record")
async def print_record():
    pass

# 管理员调整中央空调的全局设置，包括工作模式、温度范围和风速费率。
@app.get("/central-aircon/adjust")
async def control_ac(
    adjust_request:CenterAcControlRequest,  # 请求数据
    session: SessionDep # 获取数据库 session
):
    # 调用core.py中的control_ac_core函数
    return await control_ac(adjust_request, session)

# 管理员实时获取酒店所有房间空调的运行状态和参数信息。
@app.get("/aircon/status")
async def get_ac_states(session: SessionDep):
    """
    管理员获取整个酒店空调的运行状态和参数信息。
    调用核心函数获取空调状态数据并返回。
    """
    result = get_ac_states_core(session)
    return result

# 获取空调最近一周的操作记录
@app.get("/admin/query_ac")
async def get_ac_control_log():
    pass

# 获取空调一周的调度记录
@app.get("/admin/query_ac")
async def get_ac_schedule_log():
    pass

# 获取空调一周的客流记录
@app.get("/admin/query_people")
async def get_guest_log():
    pass

# 获取所有房间信息
@app.get("/admin/query_room")
async def get_room_state():
    pass

