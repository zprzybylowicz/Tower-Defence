import xml.etree.ElementTree as ET

class GameStateXML:
    def __init__(self, scene):
        self.scene = scene

    def save(self, filename="gamestate.xml"):
        root = ET.Element("GameState")
        root.set("level", str(self.scene.level))
        root.set("gold", str(self.scene.gold))
        root.set("enemies_killed", str(self.scene.enemies_killed))

        # Zapis wież
        towers_elem = ET.SubElement(root, "Towers")
        for item in self.scene.items():
            if hasattr(item, "tower_type"):
                tower = ET.SubElement(towers_elem, "Tower")
                tower.set("x", str(int(item.x())))
                tower.set("y", str(int(item.y())))
                tower.set("type", item.tower_type)

        #  Zapis wrogów
        enemies_elem = ET.SubElement(root, "Enemies")
        for item in self.scene.items():
            if hasattr(item, "isEnemy") and item.isEnemy:
                enemy = ET.SubElement(enemies_elem, "Enemy")
                enemy.set("type", type(item).__name__)
                enemy.set("x", str(item.pos().x()))
                enemy.set("y", str(item.pos().y()))
                enemy.set("hp", str(item.hp))
                enemy.set("path_index", str(item.path_index))
                enemy.set("alive", str(item.alive))

        # Zapis ścieżki
        path_elem = ET.SubElement(root, "Path")
        for x, y in self.scene.current_path:
            step = ET.SubElement(path_elem, "Step")
            step.set("x", str(x))
            step.set("y", str(y))

        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        print("[XML] Stan gry zapisany do:", filename)

    @staticmethod
    def load(filename="gamestate.xml"):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            state = {
                "level": int(root.get("level", 1)),
                "gold": int(root.get("gold", 0)),
                "enemies_killed": int(root.get("enemies_killed", 0)),
                "towers": [],
                "enemies": [],
                "current_path": []
            }

            #  Wieże
            for tower in root.find("Towers"):
                state["towers"].append({
                    "x": float(tower.get("x", 0)),
                    "y": float(tower.get("y", 0)),
                    "tower_type": tower.get("type", "fire")
                })

            # Wrogowie
            for enemy in root.find("Enemies"):
                state["enemies"].append({
                    "type": enemy.get("type"),
                    "x": float(enemy.get("x", 0)),
                    "y": float(enemy.get("y", 0)),
                    "hp": int(enemy.get("hp", 1)),
                    "path_index": int(enemy.get("path_index", 0)),
                    "alive": enemy.get("alive", "True") == "True"
                })


            for step in root.find("Path"):
                x = int(step.get("x", 0))
                y = int(step.get("y", 0))
                state["current_path"].append((x, y))

            return state

        except Exception as e:
            print("[XML] Błąd wczytywania stanu gry:", e)
            return None
