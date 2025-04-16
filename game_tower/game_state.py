import json

class GameState:
    def __init__(self, scene):
        self.level = scene.level
        self.gold = scene.gold
        self.enemies_killed = scene.enemies_killed
        self.current_path = scene.current_path  # ⬅️ dodane

        self.towers = []
        self.enemies = []

        for item in scene.items():
            if hasattr(item, "tower_type"):
                self.towers.append({
                    "x": item.x(),
                    "y": item.y(),
                    "tower_type": item.tower_type
                })
            elif hasattr(item, "isEnemy") and item.isEnemy:
                self.enemies.append({
                    "type": type(item).__name__,
                    "x": item.x(),
                    "y": item.y(),
                    "hp": item.hp,
                    "alive": item.alive,
                    "path_index": item.path_index
                })

    def save(self, filename="gamestate.json"):
        with open(filename, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    @staticmethod
    def load(filename="gamestate.json"):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            print("[JSON] Błąd wczytywania stanu gry:", e)
            return None
