# scenario.py
import csv
import os

SCENARIO_DIR = os.path.join(os.path.dirname(__file__), "scenarios")

def load_scenario(mode="cold"):
    filename = "scenario_cold.csv" if mode == "cold" else "scenario_hot.csv"
    path = os.path.join(SCENARIO_DIR, filename)
    actions = []
    if not os.path.exists(path):
        print(f"场景文件不存在: {path}")
        return actions
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            minute = int(row["minute"])
            roomId = row["roomId"]
            power = row["power"]
            temperature = int(row["temperature"])
            windSpeed = row["windSpeed"]
            sweep = row["sweep"]
            actions.append((minute, roomId, {
                "power": power,
                "temperature": temperature,
                "windSpeed": windSpeed,
                "sweep": sweep
            }))
    return actions

def get_actions_for_room(room_id, mode="cold"):
    all_actions = load_scenario(mode)
    # 筛选当前房间的动作，并按照minute排序
    room_actions = [act for (m, r, act) in all_actions if r == str(room_id)]
    # 根据minute排序
    room_actions = sorted(room_actions, key=lambda a: next(m for m, r, act in all_actions if r == str(room_id) and act == a))
    return room_actions
