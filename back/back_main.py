from fastapi import FastAPI, Header, Body
from dbcontrol import Room, HotelCheck, acLog, acControl, RoomCheckIn, RoomAcData
from dbcontrol import engine, SessionDep, create_db_and_tables, data_check_in, data_check_out
from sqlmodel import Field, Session, SQLModel, Relationship, ForeignKey, create_engine, select
from core import *
from respond_body import *


app = FastAPI()
create_db_and_tables()

# 控制指定房间的空调设置
@app.get("/aircon/control")
async def room_ac_control():
    pass

# 查询指定房间的空调控制面板信息
@app.get("/aircon/panel")
async def room_ac_state():
    pass

# 登录时获取用户角色（验证账号密码后发放JWT）
@app.get("/admin/login")
# 从请求头获取Authorization字段
async def admin_login(session: SessionDep, data: AdminLoginRequest = Body(...)):
    return await admin_login_core(data, session)

# 前台获取入住情况（查询所有房间的入住信息）
@app.get("/stage/query")   
async def room_state(session: SessionDep, authorization: str = Header(...)):
    return await room_state_core(session, authorization)
    

# 前台办理入住（向指定房间添加新的顾客）
@app.get("/stage/add") 
async def check_in(session: SessionDep, authorization: str = Header(...), data: dict = Body(...)):
    return await chect_in_core(session, authorization, data)
    

# 前台办理结账/退房（生成账单并更新房间状态）
@app.get("/stage/delete")
async def check_out(session: SessionDep, authorization: str = Header(...), data: dict = Body(...)):
    return await check_out_core(session, authorization, data)
    

# 前台开具详单（查询指定房间的全部信息）
@app.get("/stage/record")
async def print_record(session: SessionDep, authorization: str = Header(...), data: dict = Body(...)):
    return await print_record_core(session, authorization, data)
    

# 管理员调整中央空调的全局设置，包括工作模式、温度范围和风速费率。
@app.get("/central-aircon/adjust")
async def control_ac():
    pass

# 管理员实时获取酒店所有房间空调的运行状态和参数信息。
@app.get("/aircon/status")
async def get_ac_states():
    pass

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

