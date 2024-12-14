# frontend/common.py
import requests

API_URL = "http://10.29.149.249:8000"  # 根据实际情况修改后端地址
# 其他可能的地址：
# http://127.0.0.1:8000 本机地址
# http://10.29.132.79:8000 另一台电脑的地址

def post_json(url, data=None, headers=None):
    if headers is None:
        headers = {}
    try:
        response = requests.post(f"{API_URL}{url}", json=data, headers=headers, timeout=10)
        return response
    except requests.exceptions.RequestException as e:
        print(f"POST请求异常: {e}")
        return None

def get_json(url, headers=None, params=None):
    if headers is None:
        headers = {}
    try:
        response = requests.get(f"{API_URL}{url}", headers=headers, params=params, timeout=10)
        return response
    except requests.exceptions.RequestException as e:
        print(f"GET请求异常: {e}")
        return None
