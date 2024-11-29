from fastapi import HTTPException
import jwt

# 预定义的密钥和算法
SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'

# 解码JWT并提取用户角色
async def decode_jwt(token: str):
    try:
        # 解码并验证JWT
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 返回解码后的角色信息（假设角色信息在JWT的'role'字段中）
        return decoded.get('role')
    
    # 解码失败
    except jwt.ExpiredSignatureError:  # Token过期
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:  # Token无效
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:  # 其他错误（如Token格式不对）
        raise HTTPException(status_code=401, detail="认证失败")

# 系统校验管理员权限（在后续接口中使用）
async def check_admin(authorization: str):
    if not authorization:
        raise HTTPException(status_code=401, detail="认证失败")
    
    try:        
        # 从Authorization字段提取Bearer后的token部分
        token = authorization.split(" ")[1]
        
        # 解码获取角色
        user_role = decode_jwt(token)  # await

        # 如果用户角色不是管理员
        if user_role != "管理员":
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 如果是管理员
        return {"message": "身份验证成功"}
    
    except HTTPException as e:
        # 捕获并重新抛出HTTPException
        raise e
    