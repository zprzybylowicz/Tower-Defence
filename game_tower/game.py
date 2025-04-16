import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem, QLabel
)
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QPixmap
from PyQt5.QtCore import QRectF, QTimer, Qt
import enemy.resources_rc
from tower import Tower, TowerDragLabel
from enemy_base import Enemy
from enemy_base import EnemyRandom, EnemyStrateg, EnemyAggressor  # z folderu enemy/enemy.py
from shop import ShopItem
from map_generator import generate_level4_path
from json_history import GameHistory
from xml_history import GameStateXML
from game_state import GameState
from mongo_history import GameHistoryMongo

TILE_SIZE = 64
GRID_WIDTH = 15
GRID_HEIGHT = 15

def generate_level1_path():
    return [(x, 7) for x in range(GRID_WIDTH)]

def generate_level2_path():
    return [
        (0, 4), (1, 4), (2, 4), (3, 4),
        (3, 5), (3, 6),
        (4, 6), (5, 6), (6, 6),
        (6, 5), (6, 4),
        (7, 4), (8, 4),
        (8, 5), (8, 6),
        (9, 6), (10, 6),
        (10, 5), (10, 4),
        (11, 4), (12, 4), (13, 4), (14, 4)
    ]

def generate_level3_path():
    return [
        (0, 2), (1, 2), (2, 2), (3, 2),
        (3, 3), (3, 4), (3, 5),
        (4, 5), (5, 5), (6, 5),
        (6, 4), (6, 3),
        (7, 3), (8, 3), (9, 3),
        (9, 4), (9, 5),
        (10, 5), (11, 5), (12, 5),
        (12, 6), (12, 7),
        (13, 7), (14, 7)
    ]

class TowerDefenseScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_dead_enemies)
        self.cleanup_timer.start(1000)  # co 1 sekundę

        self.enemies_killed = 0  #
        self.gold_display_widget = None

        self.setSceneRect(0, 0, TILE_SIZE * GRID_WIDTH, TILE_SIZE * GRID_HEIGHT)
        self.level = 1
        self.placing_tower = False
        self.enemy_skin_path = ":/enemy/enemy_1.png"
        self.enemy_type_class = EnemyRandom  # Domyślnie Random
        self.game_ended = False

        self.draw_grid()
        self.place_towers()
        QTimer.singleShot(1000, self.start_level)

        self.gold = 0
        self.gold_label = QGraphicsTextItem(f"Gold: {self.gold}")
        self.gold_label.setDefaultTextColor(QColor("gold"))
        self.gold_label.setZValue(1000)
        self.gold_label.setPos(10, 10)
        self.addItem(self.gold_label)

    def start_level(self):
        self.wave_started = True
        self.wave_start_time = QTimer().remainingTime()  # lub użyj innego sposobu, np. QDateTime.currentDateTime()
        self.spawn_enemies()
        QTimer.singleShot(5000, lambda: setattr(self, "wave_started", False))
        QTimer.singleShot(5000, self.start_wave_check)

    def set_gold_display(self, label):
        self.gold_display_widget = label
        self.gold_display_widget.setText(f"Gold: {self.gold}")

    def add_gold(self, amount):
        self.gold += amount
       # print(f"[GOLD] +{amount} (Total: {self.gold})")
        if self.gold_display_widget:
            self.gold_display_widget.setText(f"Gold: {self.gold}")

    def cleanup_dead_enemies(self):
        for item in self.items():
            if isinstance(item, Enemy) and not item.alive:
                try:
                    self.removeItem(item)
                    item.deleteLater()
                    print("[CLEANUP] Usunięto martwego wroga:", item)
                except Exception as e:
                    print("")

    def pause_game(self):
        if hasattr(self, "check_wave_timer") and self.check_wave_timer.isActive():
            self.check_wave_timer.stop()

        for item in self.items():
            if hasattr(item, "pause_game"):
                item.pause_game()

    def resume_game(self):
        if hasattr(self, "check_wave_timer") and not self.check_wave_timer.isActive():
            self.check_wave_timer.start(1000)

        for item in self.items():
            if hasattr(item, "resume_game"):
                item.resume_game()

    def draw_grid(self):
        self.clear()
        pen = QPen(QColor(200, 200, 200))

        if self.level == 1:
            self.current_path = generate_level1_path()
            grid_width = GRID_WIDTH
            grid_height = GRID_HEIGHT
        elif self.level == 2:
            self.current_path = generate_level2_path()
            grid_width = GRID_WIDTH
            grid_height = GRID_HEIGHT
        elif self.level == 3:
            self.current_path = generate_level3_path()
            grid_width = GRID_WIDTH
            grid_height = GRID_HEIGHT
        elif self.level == 4:
            self.current_path = generate_level4_path()
            # Automatycznie dopasuj rozmiar sceny do ścieżki
            grid_width = max(p[0] for p in self.current_path) + 1
            grid_height = max(p[1] for p in self.current_path) + 1
            self.setSceneRect(0, 0, grid_width * TILE_SIZE, grid_height * TILE_SIZE)

        for x in range(grid_width):
            for y in range(grid_height):
                rect = QRectF(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile = QGraphicsRectItem(rect)
                if (x, y) in self.current_path:
                    tile.setBrush(QBrush(QColor(150, 75, 0)))
                else:
                    tile.setBrush(QBrush(QColor(255, 255, 255)))
                tile.setPen(pen)
                self.addItem(tile)

    def set_drag_slot(self, layout):
        self.top_slot_layout = layout



    def replace_widget(self, new_widget):
        if hasattr(self, "top_slot_layout") and self.top_slot_layout.count() > 0:
            old = self.top_slot_layout.itemAt(0).widget()
            if old:
                self.top_slot_layout.removeWidget(old)
                old.setParent(None)
        self.top_slot_layout.addWidget(new_widget)

    def spawn_enemies(self):
        if self.level == 1:
            count = 5
        elif self.level == 2:
            QTimer.singleShot(2000, self.start_wave_check)

            count = 10
        elif self.level == 3:
            count = 10
        elif self.level == 4:
            count = 11
        else:
            count = 5

        for i in range(count):
            QTimer.singleShot(i * 2000, lambda i=i: self.add_enemy(i))

        QTimer.singleShot(10000, self.start_wave_check)
    def add_enemy(self, index):
        if self.game_ended:
            return

        enemy = self.enemy_type_class(self.current_path, skin_path=self.enemy_skin_path)
        enemy.isEnemy = True

        # Ustaw offset – dla każdego kolejnego wroga przesunięcie w poziomie
        enemy.offset_x = index * 30
        #enemy.pos_y += random.randint(30, 50)


        pix_w = enemy.pixmap().width()
        pix_h = enemy.pixmap().height()
        new_start = enemy.grid_to_pos(self.current_path[0], pix_w, pix_h)
        enemy.setPos(*new_start)
        enemy.pos_x -= index * 50
        def reward():
            self.add_gold(100)

        enemy.reward = reward

        self.addItem(enemy)
    def place_towers(self):
        if self.level == 1:
            tower_positions = [(2, 5), (5, 5), (8, 5), (11, 5), (3, 9), (7, 9), (10, 9), (13, 9)]
            for x, y in tower_positions:
                self.addItem(Tower(x, y))

    def check_wave_cleared(self):
        enemies = [item for item in self.items() if
                   hasattr(item, "isEnemy") and item.isEnemy and getattr(item, "alive", True)]
       # print("[DEBUG] Liczba żywych wrogów:", len(enemies))
        if not enemies and not self.game_ended:
            # Jeśli poziom został wybrany ręcznie, nie automatyzuj przejścia
            if getattr(self, "manual_level", False):
                return
            if self.level < 4:
                self.level += 1
                self.draw_grid()
                if self.level == 1:
                    self.place_towers()
                QTimer.singleShot(1000, self.spawn_enemies)
                QTimer.singleShot(2000, self.start_wave_check)
            else:
                self.game_over()

    def start_wave_check(self):
        self.check_wave_timer = QTimer()
        self.check_wave_timer.timeout.connect(self.check_wave_cleared)
        self.check_wave_timer.start(1000)

    def game_over(self):
        if self.game_ended:
            return
        self.game_ended = True

        # Zatrzymaj timer sprawdzający fale
        if hasattr(self, "check_wave_timer"):
            self.check_wave_timer.stop()

        # Zatrzymaj timery wrogów (iterujemy po kopii listy)
        for item in list(self.items()):
            if getattr(item, "isEnemy", False) and hasattr(item, "timer"):
                item.timer.stop()


        game_over_text = QGraphicsTextItem("GAME OVER")
        game_over_text.setFont(QFont("Arial", 48, QFont.Bold))
        game_over_text.setDefaultTextColor(QColor("red"))
        text_rect = game_over_text.boundingRect()
        center = self.sceneRect().center()
        game_over_text.setPos(center.x() - text_rect.width() / 2, center.y() - text_rect.height() / 2)
        self.addItem(game_over_text)


        mode = getattr(self, "game_mode", "single")
        gold = self.gold
        enemies_killed = getattr(self, "enemies_killed", 0)
        level = self.level
        time_played = "00:12:34"  # zastąp własnym sposobem pomiaru czasu

        # Zapis historii
        try:
            json_history = GameHistory()
            json_history.add_record(mode, gold, enemies_killed, level, time_played, "Gra zakończona")

        except Exception as e:
            print("[ERROR] Zapis JSON:", e)

        try:
            xml_history = GameStateXML()
            xml_history.add_record(mode, gold, enemies_killed, level, time_played, "Gra zakończona")

        except Exception as e:
            print("[ERROR] Zapis XML:", e)

        try:
            mongo_history = GameHistoryMongo()
            mongo_history.add_record(mode, gold, enemies_killed, level, time_played, "Gra zakończona")

        except Exception as e:
            print("[ERROR] Zapis MongoDB:", e)

    def mousePressEvent(self, event):
        if self.game_ended:
            return

        if self.level > 1 and self.placing_tower:
            pos = event.scenePos()
            gx = int(pos.x() // TILE_SIZE)
            gy = int(pos.y() // TILE_SIZE)
            if (gx, gy) not in self.current_path and not self.has_tower_at(gx, gy):
                self.add_tower(gx, gy)
        else:
            super().mousePressEvent(event)

    def has_tower_at(self, gx, gy):
        for item in self.items():
            if isinstance(item, Tower):
                if int(item.x() // TILE_SIZE) == gx and int(item.y() // TILE_SIZE) == gy:
                    return True
        return False

    def add_tower(self, gx, gy, tower_type="fire"):
        tower = Tower(gx, gy, tower_type=tower_type)
        self.addItem(tower)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "Tower":
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "Tower":
            event.acceptProposedAction()

    def dropEvent(self, event):
        if self.game_ended:
            return

        if event.mimeData().hasText():
            tower_type = event.mimeData().text()
            pos = event.scenePos()
            gx = int(pos.x() // TILE_SIZE)
            gy = int(pos.y() // TILE_SIZE)
            if (gx, gy) not in self.current_path and not self.has_tower_at(gx, gy):
                self.add_tower(gx, gy, tower_type)
                event.acceptProposedAction()




class MainWindow(QMainWindow):
    class SkinSelector(QLabel):
        def __init__(self, image_path, scene):
            super().__init__()
            self.image_path = image_path
            self.scene = scene
            self.setPixmap(QPixmap(image_path).scaled(48, 48, Qt.KeepAspectRatio))
            self.setFixedSize(50, 50)
            self.setStyleSheet("border: 1px solid gray; margin: 2px;")
            self.setCursor(Qt.PointingHandCursor)

        def mousePressEvent(self, event):
            # Ustaw nową skórkę dla przyszłych wrogów
            self.scene.enemy_skin_path = self.image_path
           # print("Wybrano skórkę:", self.image_path)
            # Zaktualizuj wygląd już istniejących wrogów
            for enemy in self.scene.items():
                if getattr(enemy, "isEnemy", False):
                    enemy.skin_path = self.image_path  # nowa skórka
                    enemy.set_skin_by_level()  # aktualizacja wyglądu
            super().mousePressEvent(event)

    def __init__(self, game_mode="single", ip_address="", parent=None):
        """
        Parametry:
         - game_mode: str = "single" / "local_coop" / "network"
         - ip_address: str = adres IP do gry sieciowej
        """
        super().__init__(parent)

        self.game_mode = game_mode
        self.ip_address = ip_address

        self.setWindowTitle("Tower Defense")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.scene = TowerDefenseScene()  # Tworzysz swoją scenę
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)


        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        layout.addWidget(side_panel)

        # Górny slot (DOMYŚLNA)
        self.default_drag_label = TowerDragLabel(QPixmap(":/enemy/6.png"), tower_type="fire")
        self.tower_drag_slot = QVBoxLayout()
        self.tower_drag_slot.addWidget(self.default_drag_label)
        side_layout.addLayout(self.tower_drag_slot)

        # Przekazujemy layout do sceny
        self.scene.set_drag_slot(self.tower_drag_slot)

        # Przycisk "Restart gry"
        restart_btn = QPushButton("Zagraj od nowa")
        restart_btn.clicked.connect(self.restart_game)
        side_layout.addWidget(restart_btn)

        # Przycisk "Pauza"
        self.pause_button = QPushButton("⏸️ Pauza")
        self.pause_button.setCheckable(True)
        self.pause_button.clicked.connect(self.toggle_pause)
        side_layout.addWidget(self.pause_button)

        # GOLD DISPLAY
        self.gold_display = QLabel("Gold: 0")
        self.gold_display.setStyleSheet("font-size: 18px; color: goldenrod; font-weight: bold;")
        side_layout.addWidget(self.gold_display)
        self.scene.set_gold_display(self.gold_display)

        # Dodaj przycisk "Historia"

        resume_btn = QPushButton("Wczytaj gre z Json")
        resume_btn.clicked.connect(self.resume_game_from_state)
        side_layout.addWidget(resume_btn)
        resume_xml_btn = QPushButton("Wczytaj grę z XML")
        resume_xml_btn.clicked.connect(self.resume_game_from_xml)
        side_layout.addWidget(resume_xml_btn)
        btn_mongo = QPushButton("Wczytaj grę z MongoDB")
        btn_mongo.clicked.connect(self.resume_game_from_mongo)
        side_layout.addWidget(btn_mongo)

        # Przycisk poziomu
        for level in [1, 2, 3, 4]:
            btn = QPushButton(f"Level {level}")
            btn.clicked.connect(lambda _, l=level: self.load_level(l))
            side_layout.addWidget(btn)

        # Typ przeciwnika
        side_layout.addWidget(QLabel("Typ przeciwnika:"))
        side_layout.addWidget(self.make_type_button("Random", EnemyRandom))
        side_layout.addWidget(self.make_type_button("Strateg", EnemyStrateg))
        side_layout.addWidget(self.make_type_button("Aggressor", EnemyAggressor))

        # Sklepik
        side_layout.addWidget(QLabel("Sklepik:"))
        side_layout.addWidget(ShopItem(QPixmap(":/enemy/6.png"), "fire", 100, self.scene))
        side_layout.addWidget(ShopItem(QPixmap(":/enemy/12.png"), "sniper", 150, self.scene))

        # Skórki przeciwnika
        side_layout.addWidget(QLabel("Skórki przeciwnika:"))
        enemy_skins = [
            ":/enemy/enemy_1.png",
            ":/enemy/enemy_2.png",
            ":/enemy/enemy_3.png",
        ]
        for skin in enemy_skins:
            side_layout.addWidget(self.SkinSelector(skin, self.scene))

        # --- Na końcu ---
        print("[DEBUG] Otrzymałem game_mode:", self.game_mode)
        print("[DEBUG] Otrzymałem ip_address:", self.ip_address)
        if self.game_mode == "local_coop":
            print("Tryb 2 graczy lokalnie - można ograniczyć połowę planszy dla każdego itp.")
        elif self.game_mode == "network":
            from network import start_image_server
            import threading
            threading.Thread(target=start_image_server, args=('0.0.0.0', 8080, self), daemon=True).start()
            print(f"Tryb sieciowy - można łączyć się z serwerem na IP: {self.ip_address}")

        else:
            print("Tryb single player")
        if self.game_mode == "resume_json":
            QTimer.singleShot(500, self.resume_game_from_state)
        elif self.game_mode == "resume_xml":
            QTimer.singleShot(500, self.resume_game_from_xml)
        elif self.game_mode == "resume_mongo":
            QTimer.singleShot(500, self.resume_game_from_mongo)


    def toggle_pause(self):
        if self.pause_button.isChecked():
            self.pause_button.setText(" Wznów")
            print("[DEBUG] Pauza kliknięta")
            self.scene.pause_game()
        else:
            self.pause_button.setText(" Pauza")
            print("[DEBUG] Wznów kliknięty")
            self.scene.resume_game()

    def make_type_button(self, name, cls):
        btn = QPushButton(name)
        btn.clicked.connect(lambda: self.set_enemy_type(cls))
        return btn

    def set_enemy_type(self, cls):
        self.scene.enemy_type_class = cls
        print("Typ przeciwnika:", cls.__name__)

    def restart_game(self):
        self.scene.level = 1
        self.scene.game_ended = False
        self.scene.clear()
        self.scene.draw_grid()
        self.scene.place_towers()
        QTimer.singleShot(1000, self.scene.spawn_enemies)

    def load_level(self, lvl):
        self.scene.manual_level = True
        self.scene.level = lvl
        self.scene.game_ended = False


        for item in list(self.scene.items()):
            # Zakładamy, że gold_label (lub gold_display_widget) to element, który chcemy zachować
            if item not in (self.scene.gold_label, self.scene.gold_display_widget):
                self.scene.removeItem(item)
        self.scene.draw_grid()
        if lvl == 1:
            self.scene.place_towers()
        QTimer.singleShot(1000, self.scene.spawn_enemies)
        QTimer.singleShot(20000, self.scene.start_wave_check)
        QTimer.singleShot(6000, lambda: setattr(self.scene, "manual_level", False))

    def closeEvent(self, event):
        try:
            if not self.scene.game_ended:
                mode = self.game_mode
                gold = self.scene.gold
                enemies_killed = getattr(self.scene, "enemies_killed", 0)
                level = self.scene.level
                time_played = "przerwana"
                details = "Gra przerwana przez zamknięcie okna"

                # Zapis stanu gry do pliku JSON
                try:
                    from game_state import GameState
                    state = GameState(self.scene)
                    state.save("gamestate.json")
                    print("[DEBUG] JSON zapisany.")
                except Exception as e:
                    print("[ERROR] Zapis stanu gry do JSON:", e)

                # Zapis stanu gry do pliku XML
                try:
                    from xml_history import GameStateXML
                    xml_state = GameStateXML(self.scene)
                    xml_state.save("gamestate.xml")
                    print("[DEBUG] XML zapisany.")
                except Exception as e:
                    print("[ERROR] Zapis stanu gry do XML:", e)

                # Zapis historii gry do MongoDB
                try:
                    if not self.scene.game_ended:
                        #print("[DEBUG] Próba zapisu do MongoDB...")
                        from mongo_history import GameHistoryMongo
                        mongo = GameHistoryMongo()
                        mongo.save_full_state(self.scene)
                        print("[DEBUG] MongoDB zapis zakończony.")
                except Exception as e:
                    print("[ERROR] Zapis do MongoDB nieudany:", e)

        except Exception as ex:
            print("[ERROR] closeEvent:", ex)
        event.accept()

    def resume_game_from_mongo(self):
        from mongo_history import GameHistoryMongo
        try:
            mongo = GameHistoryMongo()
            state = mongo.load_latest_state()
            print("[DEBUG] Wczytany stan z MongoDB:", state)
            if not state:
                print("[MongoDB] Brak zapisanego stanu gry.")
                return

            self.scene.level = state.get("level", 1)
            self.scene.gold = state.get("gold", 0)
            self.scene.enemies_killed = state.get("enemies_killed", 0)

            # Przywróć zapisaną ścieżkę, jeśli istnieje
            if "current_path" in state:
                self.scene.current_path = state["current_path"]
                print("[DEBUG] Przywrócono current_path:", self.scene.current_path)

            self.scene.clear()
            self.scene.draw_grid()

            for tower in state.get("towers", []):
                x = tower["x"]
                y = tower["y"]
                tower_type = tower.get("tower_type", "fire")
                self.scene.add_tower(x // TILE_SIZE, y // TILE_SIZE, tower_type)

            for enemy_data in state.get("enemies", []):
                enemy_type = enemy_data.get("type", "")
                x = enemy_data.get("x", 0)
                y = enemy_data.get("y", 0)
                hp = enemy_data.get("hp", 1)
                path_index = enemy_data.get("path_index", 0)
                alive = enemy_data.get("alive", True)

                if enemy_type == "EnemyRandom":
                    enemy = EnemyRandom(self.scene.current_path)
                elif enemy_type == "EnemyStrateg":
                    enemy = EnemyStrateg(self.scene.current_path)
                elif enemy_type == "EnemyAggressor":
                    enemy = EnemyAggressor(self.scene.current_path)
                else:
                    continue

                enemy.hp = hp
                enemy.path_index = path_index
                enemy.alive = alive
                enemy.pos_x = x
                enemy.pos_y = y
                enemy.setPos(x, y)

                def reward():
                    self.scene.add_gold(100)

                enemy.reward = reward
                if alive:
                    enemy.start_movement()

                self.scene.addItem(enemy)

            self.gold_display.setText(f"Gold: {self.scene.gold}")
            self.scene.start_level()
            print("Stan gry wczytany z MongoDB. Gra wznowiona.")

        except Exception as e:
            print("[MongoDB] Błąd przy wczytywaniu stanu gry:", e)

    def resume_game_from_state(self):
        state_data = GameState.load("gamestate.json")
        if state_data is None:
            print("Brak zapisanego stanu gry.")
            return
        self.scene.level = state_data.get("level", 1)
        self.scene.gold = state_data.get("gold", 0)
        self.scene.enemies_killed = state_data.get("enemies_killed", 0)


        if self.scene.level == 4 and "current_path" in state_data:
            self.scene.current_path = state_data["current_path"]

        self.scene.clear()
        self.scene.draw_grid()

        for tw_data in state_data.get("towers", []):
            x = tw_data.get("x", 0)
            y = tw_data.get("y", 0)
            tower_type = tw_data.get("tower_type", "fire")
            grid_x = int(x // TILE_SIZE)
            grid_y = int(y // TILE_SIZE)
            self.scene.add_tower(grid_x, grid_y, tower_type)
        for enemy_data in state_data.get("enemies", []):
            enemy_type = enemy_data["type"]
            x = enemy_data["x"]
            y = enemy_data["y"]
            hp = enemy_data["hp"]
            path_index = enemy_data.get("path_index", 0)
            alive = enemy_data.get("alive", True)

            if enemy_type == "EnemyRandom":
                enemy = EnemyRandom(self.scene.current_path)
            elif enemy_type == "EnemyStrateg":
                enemy = EnemyStrateg(self.scene.current_path)
            elif enemy_type == "EnemyAggressor":
                enemy = EnemyAggressor(self.scene.current_path)
            else:
                continue  # pomiń nieznany typ

            enemy.hp = hp
            enemy.path_index = path_index
            enemy.alive = alive


            enemy.pos_x = x
            enemy.pos_y = y
            enemy.setPos(x, y)

            def reward():
                self.scene.add_gold(100)

            enemy.reward = reward

            if alive:
                enemy.start_movement()

            self.scene.addItem(enemy)


        self.gold_display.setText(f"Gold: {self.scene.gold}")

        self.scene.start_level()
        print("Stan gry wczytany. Gra wznowiona.")

    def resume_game_from_xml(self):
        from xml_history import GameStateXML  # zakładam, że tak się nazywa twoja klasa

        state_data = GameStateXML.load("gamestate.xml")
        if state_data is None:
            print("Brak zapisanego stanu gry w XML.")
            return
        self.scene.level = state_data.get("level", 1)
        self.scene.gold = state_data.get("gold", 0)
        self.scene.enemies_killed = state_data.get("enemies_killed", 0)


        if self.scene.level == 4 and "current_path" in state_data:
            self.scene.current_path = state_data["current_path"]

        self.scene.clear()
        self.scene.draw_grid()

        for tw_data in state_data.get("towers", []):
            x = tw_data.get("x", 0)
            y = tw_data.get("y", 0)
            tower_type = tw_data.get("tower_type", "fire")
            grid_x = int(x // TILE_SIZE)
            grid_y = int(y // TILE_SIZE)
            self.scene.add_tower(grid_x, grid_y, tower_type)

        for enemy_data in state_data.get("enemies", []):
            enemy_type = enemy_data["type"]
            x = enemy_data["x"]
            y = enemy_data["y"]
            hp = enemy_data["hp"]
            path_index = enemy_data.get("path_index", 0)
            alive = enemy_data.get("alive", True)

            if enemy_type == "EnemyRandom":
                enemy = EnemyRandom(self.scene.current_path)
            elif enemy_type == "EnemyStrateg":
                enemy = EnemyStrateg(self.scene.current_path)
            elif enemy_type == "EnemyAggressor":
                enemy = EnemyAggressor(self.scene.current_path)
            else:
                continue

            enemy.hp = hp
            enemy.path_index = path_index
            enemy.alive = alive
            enemy.pos_x = x
            enemy.pos_y = y
            enemy.setPos(x, y)

            def reward():
                self.scene.add_gold(100)

            enemy.reward = reward

            if alive:
                enemy.start_movement()

            self.scene.addItem(enemy)

        self.gold_display.setText(f"Gold: {self.scene.gold}")
        self.scene.start_level()
        print("Stan gry z XML wczytany. Gra wznowiona.")




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())


