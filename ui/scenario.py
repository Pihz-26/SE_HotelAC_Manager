# frontend/scenario.py
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
            temperature = row["temperature"]
            windSpeed = row["windSpeed"]
            sweep = row["sweep"]
            action = {}
            if power:
                action["power"] = power
            if temperature:
                try:
                    action["temperature"] = int(temperature)
                except ValueError:
                    action["temperature"] = None
            if windSpeed:
                action["windSpeed"] = windSpeed
            if sweep:
                action["sweep"] = sweep
            actions.append({"minute": minute, "roomId": roomId, "action": action})
    # Sort actions by minute
    actions = sorted(actions, key=lambda x: x['minute'])
    return actions

def get_actions_for_room(room_id, mode="cold"):
    all_actions = load_scenario(mode)
    # 筛选动作属于指定房间的，并按照minute排序
    room_actions = [a['action'] for a in all_actions if a['roomId'] == str(room_id)]
    # 已经按分钟排序
    return room_actions
