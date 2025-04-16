from pymongo import MongoClient
from datetime import datetime

class GameHistoryMongo:
    def __init__(self, uri="mongodb://localhost:27017", db_name="tower_defense", collection_name="histor"):
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add_record(self, mode, gold, enemies_killed, level, time_played, details=""):
        record = {
            "timestamp": datetime.now(),
            "mode": mode,
            "gold": gold,
            "enemies_killed": enemies_killed,
            "level": level,
            "time_played": time_played,
            "details": details
        }
        self.collection.insert_one(record)
        print("[MongoDB] Zapisano prostą historię.")

    def save_full_state(self, scene):
        towers = []
        enemies = []

        for item in scene.items():
            if hasattr(item, "tower_type"):
                towers.append({
                    "x": int(item.x()),
                    "y": int(item.y()),
                    "tower_type": item.tower_type
                })
            elif hasattr(item, "isEnemy") and item.isEnemy:
                enemies.append({
                    "type": type(item).__name__,
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "hp": item.hp,
                    "path_index": item.path_index,
                    "alive": item.alive
                })

        record = {
            "timestamp": datetime.now(),
            "mode": getattr(scene, "game_mode", "unknown"),
            "gold": scene.gold,
            "enemies_killed": getattr(scene, "enemies_killed", 0),
            "level": scene.level,
            "time_played": "przerwana",
            "details": "Pełny stan gry",
            "towers": towers,
            "enemies": enemies,
            "current_path": scene.current_path  # Zapisuje aktualną ścieżkę
        }

        self.collection.insert_one(record)
        print("[MongoDB] Zapisano pełny stan gry.")

    def get_history(self):
        return list(self.collection.find())

    def load_latest_state(self):
        return self.collection.find_one(
            {"current_path": {"$exists": True}},
            sort=[("timestamp", -1)]
        )
