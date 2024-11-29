from dbcontrol import *
from respond_body import *
from datetime import datetime, timezone, timedelta
import jwt

# 预定义的密钥和算法，用于签发JWT
SECRET_KEY = ''
ALGORITHM = ''

# 生成JWT token
def create_jwt_token(user_id: str, role: str) -> str:
    # 设置JWT过期时间为1小时
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
    
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# 登录时获取用户角色（验证账号密码后发放JWT）
async def admin_login_core(settings: dict, session: Session = Depends(get_session)):
    # 处理请求体中的账号密码数据
    user_id = settings.get("user_id")
    password = settings.get("password")
    try:
        # 使用数据库验证用户身份（直接比对账号密码）
        user = verify_user_password(user_id, password, session)
        
        # 从数据库中获取用户角色
        role = user.role  
       
        # 创建JWT Token
        token = create_jwt_token(user.user_id, role)
        
        # 返回响应
        return {
            "code": 0,
            "message": "登录成功",
            "token": token,
            "role": role
        }
    
    except Exception as e:
        # 捕获其他异常，确保程序不会崩溃
        raise HTTPException(status_code=500, detail="服务器错误，请稍后重试")
    
# 前台获取入住情况（查询所有房间的入住信息）
async def room_state_core():  
    # 验证管理员身份
    # 通过 SQLModel 查询数据库中所有的房间数据
    with Session(engine) as session:
        # .where(Room.state == True)).all()  # 已入住
        rooms = session.exec(select(Room)).all()  
        
        room_data_list = []
        for room in rooms:
            # 查询当前房间的入住信息
            hotel_checks = session.exec(select(HotelCheck).
                where(HotelCheck.room_id == room.room_id)).all()
            
            # 构建住户信息
            people_info = []
            for check in hotel_checks:
                people_info.append({
                    "peopleId": check.person_id,
                    "peopleName": check.guest_name
                })
            
            # 创建响应数据结构
            room_data = {
                "roomId": room.room_id,
                "roomLevel": room.room_level.value,  # 通过枚举值获取房间类型
                "cost": room.cost,
                "checkInTime": room.hotel_checks[0].check_in_date.isoformat(),  # 获取第一次入住时间
                "people": people_info
            }    
            # room_data = RoomStatus(
            #     roomId=room.room_id,
            #     roomLevel=room.room_level.value,
            #     cost=room.cost,
            #     checkInTime = room.hotel_checks[0].check_in_date.isoformat(),
            #     people=people_info,
            # )
            
            room_data_list.append(room_data)

        # 构建并返回成功响应
        response = RoomACStateRespond(
            code=0,
            message="查询成功",
            data=room_data_list
        )
        
        return response

# 前台办理入住（向指定房间添加新的顾客）
async def chect_in_core(roomId: int, peopleName: str):    
    # 验证管理员身份
    # 查询房间是否空闲
    with Session(engine) as session:
        room = session.exec(select(Room).where(Room.room_id == roomId)).first()
        
        if not room:
            # raise HTTPException(status_code=404, detail="房间不存在")
            return NormalRespond(code=1, message="房间不存在")        
        
        elif room.state:
            # raise HTTPException(status_code=400, detail="房间已被占用")
            return NormalRespond(code=1, message="房间已被占用")
        
        else:
            # 创建顾客入住记录
            new_guest = HotelCheck(
                room_id=roomId,
                guest_name=peopleName,
                check_in_date = datetime.now(timezone.utc),  # 入住时间
                check_out_date=None  # 退房时间暂时为 None              
            )
            session.add(new_guest)
            room.state = True  # 更新房间状态为已入住
            session.commit()
            
            # 返回成功响应
            return NormalRespond(code=0, message="顾客添加成功")
        

# 前台办理结账/退房（生成账单并更新房间状态）
async def check_out_core():
    # 验证管理员身份
    # 查询顾客入住信息
    with Session(engine) as session:
        # 查找该房间是否有入住记录
        room = session.exec(select(Room).where(Room.room_id == roomId)).first()
        if not room:
            raise HTTPException(status_code=404, detail="房间不存在")
        
        guest_record = session.exec(select(HotelCheck).where(HotelCheck.room_id == roomId).where(HotelCheck.check_out_date == None)).first()
        if not guest_record:
            raise HTTPException(status_code=404, detail="该房间没有入住记录")
        
        # 获取顾客入住时间与当前时间
        check_in_time = guest_record.check_in_date
        check_out_time = datetime.utcnow()
        # 计算入住天数
        stay_duration = (check_out_time - check_in_time).days
        if stay_duration == 0:
            stay_duration = 1  # 至少1天入住费用

        # 计算房费（假设房费为 100 元/天）
        room_cost = 100 * stay_duration  # 假设每晚住宿费为100元
        
        # 查询空调消费记录
        ac_logs = session.exec(select(AcLogRecord).where(AcLogRecord.room_id == roomId).where(AcLogRecord.time >= check_in_time).where(AcLogRecord.time <= check_out_time)).all()
        ac_cost = sum(log.cost for log in ac_logs)  # 空调总费用计算
        
        # 生成账单
        total_cost = room_cost + ac_cost
        
        # 退房操作：更新房间状态，清除顾客入住记录
        guest_record.check_out_date = check_out_time
        room.state = "空闲待清理"  # 房间状态更新
        session.commit()

        # 返回账单信息和结算凭据给顾客
        return {
            "code": 0,
            "message": "退房成功",
            "data": {
                "roomCost": room_cost,
                "acCost": ac_cost,
                "totalCost": total_cost,
                "stayDuration": stay_duration,
                "acLogs": [{"time": log.time, "cost": log.cost} for log in ac_logs]  # 可选：空调详单
            }
        }

# 前台开具详单（查询指定房间的全部信息）
async def print_record_core():
    pass
