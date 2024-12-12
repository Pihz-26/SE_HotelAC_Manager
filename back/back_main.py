from fastapi import FastAPI, Header, Body, Query
from core import *
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from schedule import start_scheduler
import uvicorn
    
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时执行数据库初始化操作
    with Session(engine) as session:
        create_db_and_tables(session)
        init_users(session)
        # init_rooms(session)
    # 启动调度器
    print("Starting scheduler...")
    start_scheduler()
    print("Scheduler is running.")
    yield
    
app = FastAPI(lifespan=lifespan)

# 允许所有域名访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有头部
)

# 添加房间
@app.post("/add-room/")
async def add_room(room_data: Room, session: SessionDep):
    data_room(room_data, session)
    return {"message": f"Room {room_data.room_id} added successfully!"}

@app.delete("/delete-room/")
async def delete_room_endpoint(room_id: str, session: SessionDep):
    """
    删除房间的接口。
    参数：
        - room_id: 查询参数，用于指定要删除的房间ID
        - session: 数据库会话（依赖注入）
    返回：
        - 删除成功的消息
    """
    try:
        delete_room(room_id, session)
        return {"message": f"Room {room_id} deleted successfully!"}
    except ValueError as e:
        return {"error": str(e)}
    
@app.delete("/delete-acLog/")
async def delete_acLog_endpoint(room_id: str, session: SessionDep):
    """
    删除指定房间的所有 acLog 记录。
    参数：
        - room_id: 房间 ID（路径参数）
        - session: 数据库会话（依赖注入）
    返回：
        - 删除成功的消息
    """
    try:
        message = delete_acLog(room_id, session)
        return {"message": message}
    except ValueError as e:
        return {"error": str(e)}

# 控制指定房间的空调设置
@app.post("/aircon/control")
async def room_ac_control(
    request: RoomACStatusControlRequest,  # 请求体
    session: SessionDep  # 获取数据库 sessionDep
):
    return await room_ac_control_core(request, session)

# 查询指定房间的空调控制面板信息
@app.get("/aircon/panel")
async def room_ac_state(roomId: int, session: SessionDep):
    # 调用核心函数获取指定房间的空调状态
    return await room_ac_state_core(roomId, session)
    
# 登录时获取用户角色（验证账号密码后发放JWT）
@app.post("/admin/login")
# 从请求头获取Authorization字段
async def admin_login(session: SessionDep, data: AdminLoginRequest = Body(...)):
    return await admin_login_core(data, session)

# 前台获取入住情况（查询所有房间的入住信息）
@app.post("/stage/query")   
async def room_state(session: SessionDep, authorization: str = Header(...)):
    return await room_state_core(session, authorization)
    

# 前台办理入住（向指定房间添加新的顾客）
@app.post("/stage/add") 
async def check_in(session: SessionDep, authorization: str = Header(...), data: dict = Body(...)):
    return await check_in_core(session, authorization, data)
    

# 前台办理结账/退房（生成账单并更新房间状态）
@app.get("/stage/delete")
async def check_out(session: SessionDep, authorization: str = Header(...), roomId: int = Query(...)):
    return await check_out_core(session, authorization, roomId)
    

# 前台开具详单（查询指定房间的全部信息）
@app.get("/stage/record")
async def print_record(session: SessionDep, roomId: int = Query(...)):
    return await print_record_core(session, roomId)
    

# 管理员调整中央空调的全局设置，包括工作模式、温度范围和风速费率。
@app.post("/central-aircon/adjust")
async def control_ac(
    adjust_request:CenterAcControlRequest,  # 请求数据
    session: SessionDep # 获取数据库 session
):
    # 调用core.py中的control_ac_core函数
    return await control_ac_core(adjust_request, session)

# 管理员实时获取酒店所有房间空调的运行状态和参数信息。
@app.get("/aircon/status")
async def get_ac_states(session: SessionDep):
    """
    管理员获取整个酒店空调的运行状态和参数信息。
    调用核心函数获取空调状态数据并返回。
    """
    return await get_ac_states_core(session)

# 获取空调最近一周的操作记录
@app.get("/admin/query_ac")
async def get_ac_control_log(session: SessionDep, authorization: str = Header(...)):
    return await get_ac_control_log_core(session, authorization)

# 获取空调一周的调度记录
@app.get("/admin/query_ac")
async def get_ac_schedule_log(session: SessionDep, authorization: str = Header(...)):
    return await get_ac_schedule_log_core(session, authorization)

# 获取空调一周的客流记录
@app.get("/admin/query_people")
async def get_guest_log(session: SessionDep, authorization: str = Header(...)):
    return await get_guest_log_core(session, authorization)

# 获取所有房间信息
@app.get("/admin/query_room")
async def get_room_state(session: SessionDep, authorization: str = Header(...)):
    return await get_room_state_core(session, authorization)
