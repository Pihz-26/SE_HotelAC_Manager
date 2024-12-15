from respond_body import NormalRespond
import jwt

# 预定义的密钥和算法
SECRET_KEY = '我爱软件工程'
ALGORITHM = 'HS256'
    

# 系统校验管理员权限（在后续接口中使用）
def check_admin(authorization: str):
    response = NormalRespond(
        code=0,
        message="认证成功"
        )
    if not authorization:
        response =  NormalRespond(
            code=1, 
            message="认证失败"
        )
    
    try:        
        # 从Authorization字段提取Bearer后的token部分
        token = authorization.split(" ")[1]
        # 解码并验证JWT
        user_role = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get('role')
        # 如果用户角色不是管理员
        if user_role not in ["酒店经理", "前台服务", "空调管理"]:
            response = NormalRespond(code=1, message="权限不足")
    # 解码失败
    except jwt.ExpiredSignatureError:  # Token过期
        response = NormalRespond(code=1, message="Token expired")
    except jwt.InvalidTokenError:  # Token无效
        response =  NormalRespond(code=1, message="Invalid token")
    except Exception as e:  # 其他错误（如Token格式不对）
        response = NormalRespond(code=1, message="认证失败")

    # 如果是管理员
    return response

    