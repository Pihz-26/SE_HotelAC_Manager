from dbcontrol import *
from respond_body import *
from datetime import datetime, timezone, timedelta
import jwt

# 预定义的密钥和算法
SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'

# 签发JWT token
async def create_jwt_token(user_id: str, role: str) -> str:
    # 设置JWT过期时间为1小时
    expiration = timezone.utc() + timedelta(hours=1)  
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_user(session: Session, user_id: str):
    result = session.exec(select(User).where(User.user_id == user_id))
    print(result)
    return result.scalars().first()  # 返回第一个匹配的用户对象

# 登录时获取用户角色（验证账号密码后发放JWT）
async def admin_login_core(data: dict):
    # 处理请求体中的账号密码数据
    user_id = data.get("username")
    password = data.get("password")
    print(user_id, password)
    with Session(engine) as session:
        # 执行异步查询
        user = get_user(session, user_id)
        print(f"User data: {user}")  # 调试输出，检查返回的数据类型
        if not user or user.password != password:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 从数据库中获取用户角色
        role = user.role
        # 创建JWT Token
        token = create_jwt_token(user_id, role)
        
        # 返回响应
        return {
            "code": 0,
            "message": "登录成功",
            "token": token,
            "role": role
        }
       
# 前台获取入住情况（查询所有房间的入住信息）
async def room_state_core(authorization: dict):
    # 验证管理员身份
    
    # 通过 SQLModel 查询数据库中所有的房间数据
    with Session(engine) as session:
        room_data_list = []
        rooms = session.exec(select(Room)).all()
        for room in rooms:
            # 查询当前房间的入住信息
            hotel_checks = session.exec(select(HotelCheck).
                where(HotelCheck.room_id == room.room_id)).all()
            
            # 构建住户信息
            people_info = []
            for check in hotel_checks:
                people = People(
                    peopleId = check.person_id,
                    peopleName = check.guest_name,
                    )
                people_info.append(people)
            
            # 创建响应数据结构
            room_data = RoomStatus(
                roomId=room.room_id,
                roomLevel=room.room_level.value,  # 通过枚举值获取房间类型
                cost=room.cost,
                # 获取第一次入住时间
                checkInTime = room.hotel_checks[0].check_in_date.isoformat(),
                people=people_info,
                )
            room_data_list.append(room_data)
        # 构建并返回成功响应
        response = RoomStatusRespond(
            code=0,
            message="查询成功",
            data=room_data_list
        )
        return response

# 前台办理入住（向指定房间添加新的顾客）
async def chect_in_core(authorization: dict, data: dict):    
    # 验证管理员身份
    
    # 处理请求体中的房间号顾客名数据
    roomId = data.get("roomId")
    peopleName = data.get("peopleName")
    peopleID = 1
    
    # 查询房间是否空闲
    with Session(engine) as session:
        room = session.exec(select(Room).
                            where(Room.room_id == roomId)).first()
        if not room:
            respond = NormalRespond(code=1, message="房间不存在")         
        elif room.state:          
            respond = NormalRespond(code=1, message="房间已被占用")
        else:
            # 创建顾客入住记录
            check_in_data = RoomCheckIn(
                room_id=roomId,
                people=[peopleName,peopleID],
                )
            data_check_in(check_in_data)
            room.state = True  # 更新房间状态为已入住
            session.commit()
            respond = NormalRespond(code=0, message="顾客添加成功")
        # 返回响应
        return respond
        

# 前台办理结账/退房（生成账单并更新房间状态）
async def check_out_core(authorization: dict, data: dict):
    # 验证管理员身份
    
    # 处理请求体中的房间号数据
    roomId = data.get("roomId")
    
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
async def print_record_core(authorization: dict, data: dict):
    pass
    # 验证管理员身份
    
    # 处理请求体中的房间号数据
    roomId = data.get("roomId")
    # 查询该房间的入住记录和空调使用记录
    with Session(engine) as session:
        # 查找房间信息
        room = session.exec(select(Room).where(Room.room_id == roomId)).first()
        if not room:
            raise HTTPException(status_code=404, detail="房间不存在")
        
        guest_record = session.exec(select(HotelCheck).where(HotelCheck.room_id == roomId).where(HotelCheck.check_out_date == None)).first()
        if not guest_record:
            raise HTTPException(status_code=404, detail="该房间没有入住记录")
        
        # 获取入住时间
        check_in_time = guest_record.check_in_date
        
        # 查询该房间的空调使用记录
        ac_logs = session.exec(select(AcLogRecord).where(AcLogRecord.room_id == roomId).all())
        
        # 计算空调总消费
        total_cost = sum(log.cost for log in ac_logs)
        
        # 获取住户信息
        # people_info = session.exec(select(Guest).where(Guest.room_id == roomId)).all()
        # people = [{"peopleId": guest.id, "peopleName": guest.name} for guest in people_info]
        
        # 构建空调使用记录数据
        records = []
        for log in ac_logs:
            record = {
                "time": log.time.isoformat(),  # ISO 8601 格式
                "cost": log.cost,
                "power": log.power,  # "on" 或 "off"
                "temperature": log.temperature,
                "windSpeed": log.wind_speed,  # "低", "中", "高"
                "mode": log.mode,  # "制冷" 或 "制热"
                "sweep": log.sweep  # "开" 或 "关"
            }
            records.append(record)
        
        # 返回响应数据
        return {
            "code": 0,
            "message": "查询成功",
            "checkInTime": check_in_time.isoformat(),
            "data": {
                "cost": total_cost,  # 总空调消费
                # "people": people,
                "records": records  # 空调使用记录
            }
        }
