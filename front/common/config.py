# API配置
API_BASE_URL = "http://localhost:8000"

# API endpoints
ENDPOINTS = {
    # 管理员登录
    "admin_login": "/admin/login",
    
    # 客户端
    "ac_control": "/aircon/control",
    "ac_panel": "/aircon/panel",
    
    # 前台
    "stage_query": "/stage/query",
    "stage_add": "/stage/add",
    "stage_delete": "/stage/delete",
    "stage_record": "/stage/record",
    
    # 空调管理
    "central_ac_adjust": "/central-aircon/adjust",
    "ac_status": "/aircon/status",
    
    # 酒店管理
    "admin_query_room": "/admin/query_room",
}

# UI配置
WINDOW_SIZE = {
    "login": "400x300",
    "client": "800x600",
    "front_desk": "1024x768",  
    "ac_manager": "1024x768",
    "hotel_manager": "1024x768"
}

# 空调相关常量
AC_CONFIG = {
    "temp_range": (16, 30),
    "default_temp": 24,
    "wind_speeds": ["低", "中", "高"],
    "modes": ["制冷", "制热"],
    "sweep_states": ["开", "关"],
    "power_states": ["on", "off"]
}

# 房间相关常量
ROOM_CONFIG = {
    "types": ["标准间", "大床房"],
    "states": ["空闲", "已入住", "维护中"],
    "floors": range(2, 6),  # 2-5层
    "rooms_per_floor": 10
}

# 错误消息
ERROR_MESSAGES = {
    "network": "网络连接错误",
    "auth": "认证失败",
    "invalid_input": "输入数据无效",
    "server": "服务器错误"
}