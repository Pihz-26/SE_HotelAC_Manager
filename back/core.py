from fastapi import HTTPException
from sqlmodel import Session, select
from typing import Dict 
from respond_body import *
from dbcontrol import *
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta
from check_admin import *

# 预定义的密钥和算法
SECRET_KEY = '我爱软件工程'
ALGORITHM = 'HS256'

# 签发JWT token
async def create_jwt_token(user_id: str, role: str) -> str:
    # 设置JWT过期时间为30天
    expiration = datetime.now() + timedelta(days=30)  
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# 登录时获取用户角色（验证账号密码后发放JWT）
async def admin_login_core(data: AdminLoginRequest, session: SessionDep):
    # 处理请求体中的账号密码数据
    print(data)
    users = session.exec(select(User).where(User.user_id == data.username)).all()
    print(users)
    user = users[0]
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 从数据库中获取用户角色
    role = user.role
    # 创建JWT Token
    token = await create_jwt_token(user.user_id, role)
    
    # 返回响应
    return {
        "code": 0,
        "message": "登录成功",
        "token": token,
        "role": role
    }
       
# 前台获取入住情况（查询所有房间的入住信息）
# 便于演示，此处暂时只展示有人房间
async def room_state_core(session: SessionDep, authorization: str):
    # 验证管理员身份
    if check_admin(authorization):
        print("身份验证成功！")
        # 通过 SQLModel 查询数据库中所有的房间数据
        room_data_list = []
        rooms = session.exec(select(Room)).all()
        print('\n', 1, rooms)
        for room in rooms:
            if room.state == False:
                room_data = CheckInState(
                roomId=int(room.room_id),
                roomLevel=room.room_level.value,  # 通过枚举值获取房间类型
                cost=0,
                checkInTime = None,
                people=[],
                )
            else:
                # 查询当前房间的入住信息
                hotel_checks = session.exec(select(HotelCheck).
                    where(HotelCheck.room_id == room.room_id)).all()
                print('\n', 2, hotel_checks)
                if hotel_checks:
                    # 构建住户信息
                    people_info = []
                    for check in hotel_checks:
                        people = Person(
                            peopleId = 0 if check.person_id == "None" else int(check.person_id),
                            peopleName = check.guest_name,
                            )
                        people_info.append(people)
                    print('\n', 3, people_info)
                    # 创建响应数据结构
                    print(room.room_id)
                    if room.state:
                        room_data = CheckInState(
                            roomId=int(room.room_id),
                            roomLevel=room.room_level.value,  # 通过枚举值获取房间类型
                            cost=room.cost,
                            # 获取第一次入住时间
                            checkInTime = room.hotel_checks[0].check_in_date.strftime("%Y-%m-%dT%H:%M:%S"),
                            people=people_info,
                            )
            room_data_list.append(room_data)
        # 构建并返回成功响应
        response = CheckInStateRespond(
            code=0,
            message="查询成功",
            data=room_data_list
        )
        return response

# 前台办理入住（向指定房间添加新的顾客）
async def check_in_core(session: SessionDep, authorization: str, data: dict):    
    # print(authorization)
    # 验证管理员身份
    if check_admin(authorization):
        print("身份验证成功！")
        # 处理请求体中的房间号顾客名数据
        roomId = data.get("roomId")
        roomId = f"{roomId}"
        peopleName = data.get("peopleName")
        peopleID = "0"
        
        # 查询房间是否空闲
        rooms = session.exec(select(Room).
                            where(Room.room_id == roomId)).all()
        # print(rooms)
        room = rooms[0]
        # print(room)
        if not room:
            respond = NormalRespond(code=1, message="房间不存在")         
        elif room.state:          
            respond = NormalRespond(code=1, message="房间已被占用")
        else:
            # 创建顾客入住记录
            person_1 = [peopleName, peopleID]
            person_2 = ["None", "None"]
            room_data = RoomCheckIn(room_id=roomId,
                people = [person_1, person_2]
                )
            
            print(room_data)
            data_check_in(room_data, session)
            respond = NormalRespond(code=0, message="顾客添加成功")
        # 返回响应
        return respond
        

# 前台办理结账/退房（生成账单并更新房间状态）
async def check_out_core(session: SessionDep, authorization: str, roomId: int):
    # 验证管理员身份
    if check_admin(authorization):
        print("身份验证成功！")
        # 处理请求体中的房间号数据
        print(roomId)
        data_check_out(roomId, session)
        return {
            "code": 0,
            "message": "退房成功"
        }
        

# 前台开具详单（查询指定房间的全部信息）
async def print_record_core(session: SessionDep, roomId: int):
        # 查找房间信息
        room = session.exec(select(Room).where(Room.room_id == roomId)).first()
        if not room:
            raise HTTPException(status_code=404, detail="房间不存在")
        
        guest_record = room.hotel_checks[-1]
        print(guest_record)
        if not guest_record:
            raise HTTPException(status_code=404, detail="该房间没有入住记录")
        
        # 获取入住时间
        check_in_time = guest_record.check_in_date
        
        # 查询该房间的空调使用记录
        ac_logs = session.exec(select(acLog).where(acLog.room_id == roomId)).all()
        print(1, ac_logs)
        # 计算空调总消费
        total_cost = sum(log.cost for log in ac_logs)
        
        # 获取住户信息
        # people_info = session.exec(select(Guest).where(Guest.room_id == roomId)).all()
        # people = [{"peopleId": guest.id, "peopleName": guest.name} for guest in people_info]
        
        # 构建空调使用记录数据
        records = []
        for log in ac_logs:
            record = {
                "time": log.change_time.isoformat(),  # ISO 8601 格式
                "cost": log.cost,
                "power": log.power,  # "on" 或 "off"
                "temperature": log.temperature,
                "windSpeed": log.wind_level,  # "低", "中", "高"
                "mode": log.ac_model,  # "制冷" 或 "制热"
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
    if adjust_request.fanRates is None or adjust_request.fanRates.lowSpeedRate is None or adjust_request.fanRates.midSpeedRate is None or adjust_request.fanRates.highSpeedRate is None:
        raise HTTPException(status_code=400, detail="必须提供风扇速度（低/中/高）!")

    # 更新空调控制表
    ac_control = acControl(ac_model=ACModel(adjust_request.mode), temperature=26)  # 默认温度为26度
    session.add(ac_control)
    session.commit()

    # 更新风速费率表
    ac_param = session.exec(select(acPamater).where(acPamater.precept == 1)).first()  # 获取当前风速费率设置
    if not ac_param:
        ac_param = acPamater()  # 如果没有记录，创建新的
    ac_param.low_cost_rate = fanRates.lowSpeedRate
    ac_param.middle_cost_rate = fanRates.midSpeedRate
    ac_param.high_cost_rate = fanRates.highSpeedRate
    session.add(ac_param)
    session.commit()
    # 返回成功响应
    return JSONResponse(content={"code": 0, "message": "中央空调设置成功"})


async def get_ac_states_core(session: SessionDep) -> Dict:
    # 查询所有房间信息
    rooms = session.exec(select(Room)).all()

    # 生成空调状态列表
    ac_states = []
    for room in rooms:
        # 获取空调控制信息
        ac_control = session.exec(select(acControl).order_by(acControl.record_time.desc())).first()
        # 如果没有空调日志或控制信息，跳过此房间
        if  not ac_control:
            continue

        # 构建每个房间的空调状态数据
        room_state = {
            "roomId": room.room_id,
            "roomTemperature": room.roomTemperature,
            "power": room.power,
            "targetTemperature": room.targetTemperature,
            "windSpeed": WindLevel(room.wind_level),  
            "mode": ACModel(ac_control.ac_model),  
            "sweep": room.sweep,  # 扫风状态
            "cost": room.cost,  # 当前房间空调费用
            "totalCost": room.totalCost,  # 累计费用
            "status": room.status,  # 状态字段，表示空调调度状态
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
    room.targetTemperature = request.temperature
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
async def room_ac_state_core(room_id: int, session: Session) -> Dict:
    # 获取房间的当前空调控制面板信息
    room = session.exec(select(Room).where(Room.room_id == str(room_id))).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    

    # 获取空调控制的全局设置（acControl）
    ac_control = session.exec(select(acControl).order_by(acControl.record_time.desc())).first()
    if not ac_control:
        raise HTTPException(status_code=404, detail="No AC control settings found")

    # 格式化返回数据
    response_data = {
        "roomTemperature": room.roomTemperature ,  # 默认室温为26度
        "power": "on" if room.power else "off",
        "temperature": room.targetTemperature,         #目标温度
        "windSpeed": WindLevel(room.wind_level),  # 风速
        "mode": ACModel(ac_control.ac_model),  # 空调模式
        "sweep": "开" if room.sweep else "关",
        "cost": room.cost,  # 当前费用
        "totalCost": room.totalCost #累计费用
    }
    
    return {
        "code": 0,
        "message": "操作成功",
        "data": response_data
    }

async def get_ac_control_log_core(session: SessionDep, authorization: str):
        # 校验身份
        one_week_ago = datetime.now() - timedelta(weeks=1)
        statement = select(acLog).filter(acLog.change_time >= one_week_ago).order_by(acLog.change_time.desc())
        
        results = session.exec(statement).all()
        if not results:
            raise HTTPException(status_code=404, detail="过去一周无任何空调操作记录")
        print(1)
        # 处理查询结果
        ac_logs = []
        wind_level_map = {
                WindLevel.Low: "低",
                WindLevel.Medium: "中",
                WindLevel.High: "高"
        }

        for record in results:
            wind_speed = wind_level_map[record.wind_level]
            ac_log = AcControlLog(
                roomId=record.room_id,
                time=record.change_time,
                cost=round(record.cost, 2),  
                energyCost=record.wind_level * record.temperature,  
                power="on" if record.power else "off",
                temperature=record.temperature,
                windSpeed=wind_speed,
                mode="制冷" if record.ac_model == ACModel.Cold else "制热",
                sweep="开" if record.sweep else "关",
                status="运行" if record.power else "关闭",
                #
                #
                #
                timeSlice=30
                #
                #
                # 
            )
            ac_logs.append(ac_log)
        
        return WeeklyAcControlLogRespond(code=0, message="查询成功", data=ac_logs)
    
async def get_ac_schedule_log_core(session: SessionDep, authorization: str):
        # 校验身份
        
        pass
    
async def get_guest_log_core(session: SessionDep, authorization: str):
        # 校验身份
        # 获取当前时间
        now = datetime.now()
        one_week_ago = now - timedelta(days=7)  # 过去一周的时间

        # 查询过去一周内的入住/离开记录
        statement = select(HotelCheck).where(HotelCheck.check_in_date >= one_week_ago)
        results = session.exec(statement).all()

        # 如果没有找到记录
        if not results:
            raise HTTPException(status_code=404, detail="没有找到过去一周的客流记录")

        # 生成客流记录
        people_logs = []
        for record in results:
            # 入住记录
            people_logs.append(PeopleLog(time=record.check_in_date, roomId=record.room_id, operation="入住"))
            # 离开记录（如果存在）
            if record.check_out_date:
                people_logs.append(PeopleLog(time=record.check_out_date, roomId=record.room_id, operation="离开"))
        
        # 返回成功响应
        return WeeklyPeopleLogRespond(
            code=0,
            message="查询成功",
            data=people_logs
        )
    
async def get_room_state_core(session: SessionDep, authorization: str):
        # 获取所有房间信息
        room_data_list = []
        rooms = session.exec(select(Room)).all()
        print('\n', 1, rooms)
        ac_control = session.exec(select(acControl).order_by(acControl.record_time.desc())).first()
        
        
        mode = "制热" if ac_control.ac_model else "制冷"
        wind_level_map = {
        WindLevel.Low: "低",
        WindLevel.Medium: "中",
        WindLevel.High: "高"
        }
        for room in rooms:
            # 查询当前房间的入住信息
            hotel_checks = session.exec(select(HotelCheck).
                where(HotelCheck.room_id == room.room_id)).all()
            print('\n', 2, hotel_checks)
            people_info = []
            if hotel_checks:
                # 构建住户信息
                
                for check in hotel_checks:
                    people = Person(
                        peopleId = 0 if check.person_id == "None" else int(check.person_id),
                        peopleName = check.guest_name,
                        )
                    print(people)
                    people_info.append(people)
            print('\n', 3, people_info)
            # 创建响应数据结构
            print(room.room_id)
            room_data = RoomStatus(
                roomId=int(room.room_id),
                roomLevel=room.room_level.value,  # 通过枚举值获取房间类型
                                    
                people=people_info,
                cost=room.cost,
                roomTemperature=room.roomTemperature,
                power="on" if room.power else "off",
                temperature=room.roomTemperature,
                windSpeed=wind_level_map[room.wind_level],
                mode=mode,
                sweep="开" if room.sweep else "关",
                )
            room_data_list.append(room_data)

        return RoomStatusRespond(
            code=0,
            message="查询成功",
            data=room_data_list
        )